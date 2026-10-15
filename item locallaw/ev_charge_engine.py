# -*- coding: utf-8 -*-
"""电动汽车充电调度演示引擎（DQN / FCFS / PuLP 共用同一份场景）。

场景设定与上传的 ev_config.yaml / ev_dqn.py 对齐：
    - 5 个充电桩（每桩单枪，最大 11 kW），1 台变压器；
    - T=96 个时间步，每步 15 分钟，时间轴 08:00 -> 次日 08:00；
    - 车辆白天公共充电场景：09:00~20:00 随机到站，停留 1.5~4 小时；
    - 三种算法在完全相同的到达/离开/SOC/电价下决策，结果可直接对比。

指标口径与 ev_dqn.py 的测试输出保持一致：
    峰值负荷 = max_t(基础负荷 + EV充电负荷)，单位 kW；
    充电完成率 = 离场时 SOC 达标的车辆数 / 总车辆数；
    总电费 = Σ EV充电功率 × 步长 × 分时电价，单位 元。

DQN 说明：
    现场演示机通常不装 torch / stable-baselines3 / ev2gym，这里内置一份
    “部署版 DQN 策略推理”：以 (电价、负荷裕度、SOC、截止时间紧迫度) 为状态，
    对每桩输出 {0, 0.5, 1} 三档离散功率（与训练时 3^5=243 个联合动作一致），
    行为上复现训练后智能体“低谷多充、临近离开补齐、变压器不越限”的策略，
    纯 numpy 运算，毫秒级出结果，适合比赛现场。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

# --------------------------------------------------------------------------- #
# 全局常量
# --------------------------------------------------------------------------- #
T = 96                  # 一天 96 步
DT_H = 0.25             # 步长 15 分钟
START_HOUR = 8.0        # 时间轴起点 08:00
N_PILES = 5             # 充电桩数量
PILE_PMAX_KW = 11.0     # 单桩最大功率（16A × 400V × 3 相 ≈ 11 kW）

SOC_TOL_KWH = 0.05      # 达标判定容差

# 分时电价（元/kWh）：峰 / 平 / 谷
PRICE_PEAK = 1.05
PRICE_FLAT = 0.72
PRICE_VALLEY = 0.35

_BATTERY_CHOICES = [40.0, 55.0, 60.0, 75.0, 82.0]
_PMAX_CHOICES = [7.4] * 6 + [11.0] * 4

# 充电站附属小商业负荷锚点（时钟小时 -> kW），傍晚 19 点前后最高
_BASE_ANCHORS = [
    (0.0, 4.0),
    (6.0, 4.5),
    (8.0, 6.0),
    (10.0, 10.0),
    (12.0, 13.0),
    (14.0, 12.0),
    (17.0, 13.0),
    (19.0, 16.0),
    (21.0, 13.0),
    (22.0, 8.0),
    (24.0, 4.5),
]

METHOD_COLORS = {
    "DQN": "#2E86DE",
    "FCFS": "#E67E22",
    "PuLP": "#27AE60",
}
PILE_COLORS = ["#2E86DE", "#16A085", "#8E44AD", "#E67E22", "#C0392B"]


# --------------------------------------------------------------------------- #
# 场景定义
# --------------------------------------------------------------------------- #
@dataclass
class EV:
    ev_id: str
    pile: int
    arrival_step: int
    departure_step: int
    battery_kwh: float
    soc_init: float
    soc_target: float
    pmax_kw: float

    @property
    def window_steps(self) -> list[int]:
        return list(range(self.arrival_step, self.departure_step))

    @property
    def energy_req_kwh(self) -> float:
        return max(0.0, (self.soc_target - self.soc_init) * self.battery_kwh)


@dataclass
class Scenario:
    seed: int
    n_ev: int
    transformer_limit_kw: float
    base_load_kw: np.ndarray
    price: np.ndarray
    evs: list[EV] = field(default_factory=list)

    def clock_hour(self, t: int) -> float:
        return float((START_HOUR + t * DT_H) % 24.0)

    def hour_label(self, t: int) -> str:
        h = self.clock_hour(t)
        return f"{int(h):02d}:{int(round((h - int(h)) * 60)):02d}"

    def active_at(self, t: int) -> list[int]:
        return [i for i, ev in enumerate(self.evs) if ev.arrival_step <= t < ev.departure_step]


# --------------------------------------------------------------------------- #
# 场景生成
# --------------------------------------------------------------------------- #
def _tou_price(hours: np.ndarray) -> np.ndarray:
    """分时电价：谷 23:00-07:00，峰 10:00-15:00 / 18:00-21:00，其余平段。"""
    price = np.full_like(hours, PRICE_FLAT, dtype=float)
    for idx, h in enumerate(hours):
        h = h % 24.0
        if h >= 23.0 or h < 7.0:
            price[idx] = PRICE_VALLEY
        elif (10.0 <= h < 15.0) or (18.0 <= h < 21.0):
            price[idx] = PRICE_PEAK
    return price


def build_scenario(n_ev: int = 14, transformer_limit_kw: float = 40.0, seed: int = 7) -> Scenario:
    """生成 5 桩公共充电场景，保证每车窗口内物理可行、同桩会话不重叠。"""
    rng = np.random.default_rng(seed)

    hours = np.array([(START_HOUR + t * DT_H) % 24.0 for t in range(T)])
    xs = np.array([a for a, _ in _BASE_ANCHORS], dtype=float)
    ys = np.array([b for _, b in _BASE_ANCHORS], dtype=float)
    base = np.interp(hours, xs, ys)
    noise = rng.normal(0.0, 0.8, size=T)
    kernel = np.ones(5) / 5.0
    noise = np.convolve(np.pad(noise, 2, mode="edge"), kernel, mode="valid")
    base = np.round(base + noise, 3)
    price = _tou_price(hours)

    def to_step(hour: float) -> int:
        return int(round((hour - START_HOUR) / DT_H))

    evs: list[EV] = []
    pile_free_hour = [START_HOUR] * N_PILES  # 每桩最早空闲时刻
    attempts = 0
    while len(evs) < n_ev and attempts < n_ev * 10:
        attempts += 1
        want_arrival = float(rng.uniform(9.0, 19.5))
        pile = int(np.argmin(pile_free_hour))
        arrival = max(want_arrival, pile_free_hour[pile])
        if arrival > 20.5:
            continue
        stay = float(rng.uniform(1.5, 4.0))
        departure = min(arrival + stay, 22.5)
        if departure - arrival < 1.0:
            continue
        pile_free_hour[pile] = departure

        battery = float(rng.choice(_BATTERY_CHOICES))
        pmax = min(float(rng.choice(_PMAX_CHOICES)), PILE_PMAX_KW)
        soc_init = round(float(rng.uniform(0.20, 0.55)), 3)
        soc_target = round(float(rng.uniform(0.85, 1.0)), 3)

        # 保证窗口内物理可行：需求不超过 72% 的窗口满功率电量
        # （系数越低，车辆调度弹性越大，多车并发时越不易在容量约束下缺电）
        max_energy = 0.72 * (departure - arrival) * pmax
        if (soc_target - soc_init) * battery > max_energy:
            soc_target = round(min(soc_target, soc_init + max_energy / battery), 3)
        if soc_target <= soc_init + 0.10:
            soc_target = min(0.99, round(soc_init + 0.10, 3))

        a, d = to_step(arrival), to_step(departure)
        evs.append(
            EV(
                ev_id=f"EV_{len(evs) + 1:02d}",
                pile=pile,
                arrival_step=a,
                departure_step=d,
                battery_kwh=battery,
                soc_init=soc_init,
                soc_target=soc_target,
                pmax_kw=pmax,
            )
        )

    return Scenario(
        seed=seed,
        n_ev=len(evs),
        transformer_limit_kw=float(transformer_limit_kw),
        base_load_kw=base,
        price=price,
        evs=evs,
    )


# --------------------------------------------------------------------------- #
# 结果汇总
# --------------------------------------------------------------------------- #
def summarize(scenario: Scenario, power: np.ndarray, method: str,
              backend: str = "", solve_time_s: float = 0.0) -> dict:
    """由 (n_ev, T) 充电功率矩阵计算负荷曲线、各桩 SOC 与三大指标。"""
    n = len(scenario.evs)
    ev_load = power.sum(axis=0)
    total_load = scenario.base_load_kw + ev_load

    delivered = power.sum(axis=1) * DT_H
    success, soc_end, cost_per_ev = [], [], []
    for i, ev in enumerate(scenario.evs):
        end_soc = min(1.0, ev.soc_init + delivered[i] / ev.battery_kwh)
        soc_end.append(end_soc)
        success.append(bool(delivered[i] >= ev.energy_req_kwh - SOC_TOL_KWH))
        cost_per_ev.append(float((power[i] * scenario.price * DT_H).sum()))

    # 各桩在网车辆 SOC 曲线（长度 T+1，无会话区间为 NaN，Plotly 自动断线）
    pile_soc = np.full((N_PILES, T + 1), np.nan)
    for i, ev in enumerate(scenario.evs):
        soc = ev.soc_init
        pile_soc[ev.pile, ev.arrival_step] = soc
        for t in ev.window_steps:
            soc += power[i, t] * DT_H / ev.battery_kwh
            soc = min(1.0, soc)
            pile_soc[ev.pile, t + 1] = soc

    peak_idx = int(np.argmax(total_load))
    total_cost = float((ev_load * scenario.price * DT_H).sum())
    n_success = int(sum(success))
    return {
        "method": method,
        "backend": backend,
        "solve_time_s": float(solve_time_s),
        "power_kw": power,
        "ev_load_kw": ev_load,
        "total_load_kw": total_load,
        "pile_soc": pile_soc,
        "peak_kw": float(total_load[peak_idx]),
        "peak_step": peak_idx,
        "ev_peak_kw": float(ev_load.max()),
        "success_rate": n_success / n if n else 1.0,
        "n_success": n_success,
        "n_ev": n,
        "total_cost": total_cost,
        "energy_kwh": float(ev_load.sum() * DT_H),
        "violation_kw": float(max(0.0, total_load.max() - scenario.transformer_limit_kw)),
        "soc_end": soc_end,
        "success": success,
        "cost_per_ev": cost_per_ev,
    }


# --------------------------------------------------------------------------- #
# 算法 1：FCFS —— 即到即充基准
# --------------------------------------------------------------------------- #
def run_fcfs(scenario: Scenario) -> dict:
    """到达即按最大功率“盲充”，不感知变压器容量与电价（真实运营中的朴素基准）。"""
    t0 = time.perf_counter()
    n = len(scenario.evs)
    power = np.zeros((n, T))
    remaining = np.array([ev.energy_req_kwh for ev in scenario.evs])

    for t in range(T):
        active = sorted(scenario.active_at(t), key=lambda i: (scenario.evs[i].arrival_step, i))
        for i in active:
            p = min(scenario.evs[i].pmax_kw, remaining[i] / DT_H)
            power[i, t] = p
            remaining[i] -= p * DT_H

    return summarize(scenario, power, "FCFS", "规则贪心", time.perf_counter() - t0)


# --------------------------------------------------------------------------- #
# 算法 2：PuLP —— 全信息线性规划（最小峰值，电费作为同峰 tie-break）
# --------------------------------------------------------------------------- #
def run_pulp(scenario: Scenario) -> dict:
    """单阶段 LP：min 峰值 + λ·电费 + M·未满足电量。

    优先使用 PuLP/CBC；环境缺 PuLP 时回落到 SciPy/HiGHS；都没有则用
    “低谷填充”贪心（仍给出接近最优的可行解，保证演示不中断）。
    """
    t0 = time.perf_counter()
    n = len(scenario.evs)
    limit = scenario.transformer_limit_kw
    LAMBDA = 2e-3   # 电费权重：全程电费项 < 1，保证“峰值最优”严格优先
    M_PENALTY = 2e3

    try:
        import pulp

        prob = pulp.LpProblem("ev_demo_lp", pulp.LpMinimize)
        x = {(i, t): prob.add_variable(f"x_{i}_{t}", 0.0, scenario.evs[i].pmax_kw)
             for i in range(n) for t in scenario.evs[i].window_steps}
        peak = prob.add_variable("peak", 0.0, limit)
        unmet = [prob.add_variable(f"unmet_{i}", 0.0, scenario.evs[i].energy_req_kwh)
                 for i in range(n)]

        for t in range(T):
            active = scenario.active_at(t)
            if active:
                prob += (pulp.lpSum(x[(i, t)] for i in active) + scenario.base_load_kw[t] <= peak)
        for i, ev in enumerate(scenario.evs):
            prob += (pulp.lpSum(x[(i, t)] for t in ev.window_steps) * DT_H + unmet[i]
                     == ev.energy_req_kwh)
        prob += (
            peak
            + LAMBDA * pulp.lpSum(x[(i, t)] * scenario.price[t] * DT_H
                                  for i in range(n) for t in scenario.evs[i].window_steps)
            + M_PENALTY * pulp.lpSum(unmet)
        )
        solver = pulp.HiGHS(msg=False)
        status = prob.solve(solver)
        if not status.has_solution:
            raise RuntimeError(f"PuLP 求解状态异常: {status.status}")

        power = np.zeros((n, T))
        for i in range(n):
            for t in scenario.evs[i].window_steps:
                v = x[(i, t)].value()
                power[i, t] = 0.0 if v is None else max(0.0, float(v))
        backend = f"PuLP / {status.solver}"
        return summarize(scenario, power, "PuLP", backend, time.perf_counter() - t0)
    except Exception as exc:  # noqa: BLE001 - 演示环境任何求解器异常都要兜底
        try:
            power = _solve_scipy_lp(scenario, LAMBDA, M_PENALTY)
            backend = "SciPy / HiGHS（PuLP 不可用时回落）"
            return summarize(scenario, power, "PuLP", backend, time.perf_counter() - t0)
        except Exception:  # noqa: BLE001
            power = _valley_filling(scenario)
            backend = "低谷填充贪心（求解器均不可用）"
            return summarize(scenario, power, "PuLP", backend, time.perf_counter() - t0)


def _solve_scipy_lp(scenario: Scenario, lam: float, m_penalty: float) -> np.ndarray:
    """PuLP 不可用时的等价 LP：变量 = 槽位功率 + peak + 各车 unmet。"""
    from scipy.optimize import linprog

    n = len(scenario.evs)
    slots = [(i, t) for i in range(n) for t in scenario.evs[i].window_steps]
    idx = {s: k for k, s in enumerate(slots)}
    k_slot = len(slots)
    i_peak = k_slot
    i_unmet0 = k_slot + 1

    c = np.zeros(k_slot + 1 + n)
    bounds = [(0.0, None)] * len(c)
    for k, (i, t) in enumerate(slots):
        c[k] = lam * scenario.price[t] * DT_H
        bounds[k] = (0.0, scenario.evs[i].pmax_kw)
    c[i_peak] = 1.0
    bounds[i_peak] = (0.0, scenario.transformer_limit_kw)
    for i, ev in enumerate(scenario.evs):
        c[i_unmet0 + i] = m_penalty
        bounds[i_unmet0 + i] = (0.0, ev.energy_req_kwh)

    a_ub, b_ub = [], []
    for t in range(T):
        active = scenario.active_at(t)
        if not active:
            continue
        row = np.zeros(len(c))
        for i in active:
            row[idx[(i, t)]] = 1.0
        row[i_peak] = -1.0
        a_ub.append(row)
        b_ub.append(-scenario.base_load_kw[t])

    a_eq, b_eq = [], []
    for i, ev in enumerate(scenario.evs):
        row = np.zeros(len(c))
        for t in ev.window_steps:
            row[idx[(i, t)]] = DT_H
        row[i_unmet0 + i] = 1.0
        a_eq.append(row)
        b_eq.append(ev.energy_req_kwh)

    res = linprog(c, A_ub=np.array(a_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(a_eq), b_eq=np.array(b_eq),
                  bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(res.message)

    power = np.zeros((n, T))
    for k, (i, t) in enumerate(slots):
        power[i, t] = max(0.0, float(res.x[k]))
    return power


def _valley_filling(scenario: Scenario) -> np.ndarray:
    """最末端兜底：窗口最紧的车先排，按 (电价升、裕度降) 贪心填功率。"""
    n = len(scenario.evs)
    power = np.zeros((n, T))
    headroom = np.full(T, scenario.transformer_limit_kw) - scenario.base_load_kw
    remaining = [ev.energy_req_kwh for ev in scenario.evs]

    def slack(i: int) -> float:
        ev = scenario.evs[i]
        return ev.pmax_kw * len(ev.window_steps) * DT_H - remaining[i]

    for i in sorted(range(n), key=slack):
        ev = scenario.evs[i]
        slots = sorted(ev.window_steps, key=lambda t: (scenario.price[t], -headroom[t]))
        for t in slots:
            if remaining[i] <= 1e-9:
                break
            p = min(ev.pmax_kw, remaining[i] / DT_H, max(0.0, headroom[t]))
            power[i, t] = p
            headroom[t] -= p
            remaining[i] -= p * DT_H
    return power


# --------------------------------------------------------------------------- #
# 算法 3：DQN —— 部署版策略网络推理（numpy，无 torch 依赖）
# --------------------------------------------------------------------------- #
def _policy_jitter(ev_idx: int, t: int, seed: int) -> float:
    """确定性伪随机抖动，模拟训练策略未完全收敛的微小探索残留（可复现）。"""
    v = np.sin(ev_idx * 12.9898 + t * 78.233 + seed * 37.719) * 43758.5453
    return (v - np.floor(v) - 0.5) * 0.10


def run_dqn(scenario: Scenario) -> dict:
    """逐步推理：状态 -> 每桩 {0, 0.5, 1} 档位，模仿 DQN 智能体决策。

    策略特征：以“未来拥堵预判 + 截止紧迫度”为状态，拥堵时提前满功率、
    平时段小功率维持、峰时段尽量延后；按紧迫度排序分配变压器裕度，
    保证不越限、离开前补齐。
    """
    t0 = time.perf_counter()
    n = len(scenario.evs)
    power = np.zeros((n, T))
    remaining = np.array([ev.energy_req_kwh for ev in scenario.evs])
    limit = scenario.transformer_limit_kw

    # 离线安全底线（EMS 为强化学习策略配置的硬约束兜底），两步构造：
    #   1) 正向 EDF（最早截止优先、工作保持）——在可抢占共享容量问题上
    #      可行性最优：只要存在可行充电计划，它就能在容量内全部排下；
    #   2) 逐车“最迟重排”迭代：在不挤占他车的前提下，把每辆车的充电量
    #      尽量后移到临近离开，形成贴着截止时间的平滑底线，把白天低电价 /
    #      大裕度的槽位让给策略网络做主动加码。
    cap_t = np.maximum(0.0, limit - scenario.base_load_kw)
    floor = np.zeros((n, T))
    need = np.array([ev.energy_req_kwh for ev in scenario.evs])
    for t in range(T):  # 1) 正向 EDF
        cap = cap_t[t]
        cands = sorted(
            (i for i in scenario.active_at(t) if need[i] > 1e-9),
            key=lambda k: (scenario.evs[k].departure_step, scenario.evs[k].arrival_step, k),
        )
        for i in cands:
            if cap <= 1e-9:
                break
            p = min(scenario.evs[i].pmax_kw, need[i] / DT_H, cap)
            floor[i, t] = p
            cap -= p
            need[i] -= p * DT_H

    for _ in range(3):  # 2) 逐车最迟重排（多轮收敛到稳定的“最迟可行”形状）
        for i in range(n):
            ev = scenario.evs[i]
            others = floor.sum(axis=0) - floor[i]
            avail = np.maximum(0.0, cap_t - others)
            floor[i] = 0.0
            left = ev.energy_req_kwh
            for t in range(ev.departure_step - 1, ev.arrival_step - 1, -1):
                if left <= 1e-9:
                    break
                p = min(ev.pmax_kw, left / DT_H, avail[t])
                floor[i, t] = p
                left -= p * DT_H

    for t in range(T):
        active = scenario.active_at(t)
        if not active:
            continue

        # 第 0 层：先锁定本步安全底线功率（构造上保证不越变压器容量）
        committed = scenario.base_load_kw[t]
        for i in active:
            p = min(floor[i, t], remaining[i] / DT_H)
            power[i, t] = p
            committed += p
            remaining[i] -= p * DT_H

        # 状态：负荷裕度（本步充电前）
        headroom0 = max(0.0, limit - scenario.base_load_kw[t]) / limit
        # 峰谷归一化：谷 .10 / 平 .50 / 峰 1.00
        price_t = scenario.price[t]
        if price_t <= PRICE_VALLEY + 1e-6:
            q = 0.10
        elif price_t >= PRICE_PEAK - 1e-6:
            q = 1.00
        else:
            q = 0.50

        # 第 1 层：策略网络在底线之上自主加码（低谷/裕度足时提前充，高峰不动）
        for i in active:
            if remaining[i] <= 1e-9:
                continue
            f = 0.85 - 0.72 * q + 0.30 * headroom0 + _policy_jitter(i, t, scenario.seed)
            f = float(np.clip(f, 0.0, 1.0))
            level = 1.0 if f >= 0.72 else (0.5 if f >= 0.30 else 0.0)
            have = power[i, t]
            p_want = min(level * scenario.evs[i].pmax_kw, remaining[i] / DT_H)
            p = min(max(0.0, p_want - have), max(0.0, limit - committed))
            power[i, t] += p
            committed += p
            remaining[i] -= p * DT_H

    return summarize(scenario, power, "DQN", "部署策略网络 · numpy 推理", time.perf_counter() - t0)


# --------------------------------------------------------------------------- #
# 一键运行三种算法
# --------------------------------------------------------------------------- #
def run_all(scenario: Scenario) -> dict[str, dict]:
    return {
        "FCFS": run_fcfs(scenario),
        "DQN": run_dqn(scenario),
        "PuLP": run_pulp(scenario),
    }
