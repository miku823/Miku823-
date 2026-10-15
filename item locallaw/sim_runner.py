# -*- coding: utf-8 -*-
"""
EV 充电调度仿真运行器（基于真实 ev2gym + 用户 ev_config.yaml + 用户预训练 DQN）
=============================================================================

策略：
    - fcfs : 先来先充（所有在线端口满功率）
    - pulp : 每步求解线性规划（MPC），目标 = 电费 + λ·峰值功率，
             约束 = 变压器 40kW / 每桩功率上限 / 每车离场前能量需求
    - dqn  : 加载用户预训练 dqn_ev_scheduler.zip（仅支持 5 桩）

输出（logs/{strategy}_{n}p/）：
    timeseries.csv  每步：时间/总负荷/各桩SOC/步电费/累计电费/电价
    vehicles.csv    每车：到达/离开步、SOC、是否达标
    metrics.json    峰值功率/充电完成率/总电费/服务车辆数/平均满意度
logs/summary.csv    全部运行汇总
"""

import os
import sys
import json
import math
import types
import argparse
import importlib.util
from datetime import timedelta

import numpy as np
import pandas as pd
import yaml

# ---------------------------------------------------------------------------
# 兼容 shim：setuptools>=81 移除了 pkg_resources；simulate_grid=False 时
# pandapower 不会被真正调用，打 stub 即可
# ---------------------------------------------------------------------------
if importlib.util.find_spec("pkg_resources") is None:
    _m = types.ModuleType("pkg_resources")

    def _resource_filename(package, resource):
        return os.path.join(os.path.dirname(importlib.util.find_spec(package).origin),
                            resource.replace("/", os.sep))

    _m.resource_filename = _resource_filename
    sys.modules["pkg_resources"] = _m

if importlib.util.find_spec("pandapower") is None:
    _pp = types.ModuleType("pandapower")
    _pp.__path__ = []
    _top = types.ModuleType("pandapower.topology")
    _pp.topology = _top
    sys.modules["pandapower"] = _pp
    sys.modules["pandapower.topology"] = _top

import gymnasium as gym  # noqa: E402
from gymnasium import spaces  # noqa: E402
from ev2gym.models.ev2gym_env import EV2Gym  # noqa: E402

# ---------------------------------------------------------------------------
# 路径与常量
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_CFG = os.path.join(BASE_DIR, "ev_config.yaml")
TMP_CFG = os.path.join(BASE_DIR, "_cfg_runtime.yaml")
DQN_MODEL = os.path.join(BASE_DIR, "dqn_ev_scheduler.zip")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOCAL_SPECS = r"D:\Python312\Lib\site-packages\ev2gym\data\ev_specs_ev_plus_phev.json"

# DQN 奖励权重（严格照用户 ev_dqn.py）
W_LOAD, W_COST, SOC_PENALTY = 0.7, 0.3, 15.0
DQN_N_PORTS, DQN_N_LEVELS = 5, 3

# PuLP 目标中峰值功率的权重（€/kW，相对于 €/kWh 电费项）
PEAK_LAMBDA = 2.0


# ---------------------------------------------------------------------------
# 状态 / 奖励函数（逐字照抄用户 ev_dqn.py）
# ---------------------------------------------------------------------------
def ev_scheduling_state(env):
    state = [env.current_step / env.simulation_length]
    for cs in env.charging_stations:
        ev = cs.evs_connected[0]
        state.append(ev.get_soc() if ev is not None else 0.0)
    for cs in env.charging_stations:
        ev = cs.evs_connected[0]
        state.append(((ev.time_of_departure - env.current_step) / env.simulation_length)
                     if ev is not None else 0.0)
    state.append(env.current_power_usage[env.current_step - 1] if env.current_step > 0 else 0.0)
    return np.array(state, dtype=np.float64)


def ev_scheduling_reward(env, total_costs, user_satisfaction_list, invalid_action_punishment):
    total_load = env.current_power_usage[env.current_step - 1]
    env.cumulative_cost = getattr(env, "cumulative_cost", 0.0) + (-total_costs)
    reward = (-1) * W_LOAD * total_load + (-1) * W_COST * env.cumulative_cost
    for ev in env.departing_evs:
        if ev.current_capacity < ev.desired_capacity - 1e-6:
            reward -= SOC_PENALTY
    return reward


class DiscretePowerActionWrapper(gym.ActionWrapper):
    """Discrete(3^5) -> 每端口功率比例 {0, 0.5, 1.0}（照抄用户 ev_dqn.py）"""

    def __init__(self, env, n_levels=DQN_N_LEVELS):
        super().__init__(env)
        self.n_ports = env.number_of_ports
        self.n_levels = n_levels
        self.action_space = spaces.Discrete(n_levels ** self.n_ports)

    def action(self, act):
        fractions = np.zeros(self.n_ports, dtype=np.float64)
        remaining = int(act)
        for i in range(self.n_ports):
            digit = remaining % self.n_levels
            remaining //= self.n_levels
            fractions[i] = digit / (self.n_levels - 1)
        return fractions


# ---------------------------------------------------------------------------
# 环境构建
# ---------------------------------------------------------------------------
def load_patched_config(n_piles):
    """读取用户 ev_config.yaml，修正本机车型库路径并按需改桩数"""
    with open(SRC_CFG, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    cfg["ev_specs_file"] = LOCAL_SPECS  # 原配置指向 E:/ 不存在路径
    cfg["number_of_charging_stations"] = int(n_piles)
    with open(TMP_CFG, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True)
    return cfg


def make_env(n_piles, seed):
    cfg = load_patched_config(n_piles)
    env = EV2Gym(
        config_file=TMP_CFG,
        generate_rnd_game=True,
        seed=seed,
        save_replay=False,
        save_plots=False,
        state_function=ev_scheduling_state,
        reward_function=ev_scheduling_reward,
        empty_ports_at_end_of_simulation=True,
        verbose=False,
    )
    return env, cfg


def pile_max_kw(cfg):
    """单桩最大功率 kW = 16A × 400V × √3（三相）"""
    cs = cfg["charging_station"]
    return cs["max_charge_current"] * cs["voltage"] * math.sqrt(cs["phases"]) / 1000.0


# ---------------------------------------------------------------------------
# 策略
# ---------------------------------------------------------------------------
def extract_price_curve(env):
    """ev2gym charge_prices 形状为 (n_cs, sim_length)，提取全天价格曲线"""
    cp = np.asarray(env.charge_prices, dtype=float)
    if cp.ndim == 2:
        return cp[0, :] if cp.shape[1] >= cp.shape[0] else cp[:, 0]
    return cp


def fcfs_action(env, obs):
    """先来先充：所有端口满功率"""
    return np.ones(env.number_of_ports, dtype=np.float64)


def make_pulp_policy(cfg):
    """MPC：每步对当前在线车辆求解 LP，只执行第一步功率"""
    import pulp

    p_max = pile_max_kw(cfg)
    tr_max = float(cfg["transformer"]["max_power"])

    def policy(env, obs):
        n = env.number_of_ports
        now = env.current_step
        dt_h = env.timescale / 60.0

        connected = []
        for i, cs in enumerate(env.charging_stations):
            ev = cs.evs_connected[0] if cs.evs_connected else None
            if ev is not None:
                connected.append((i, ev))
        if not connected:
            return np.zeros(n, dtype=np.float64)

        prices = extract_price_curve(env)

        def price_at(step):
            return -float(prices[min(step, len(prices) - 1)])  # 电价为负，取负得正 €/kWh 成本

        prob = pulp.LpProblem("ev_sched", pulp.LpMinimize)
        # 决策变量 p[(port, t)]：该端口在 (now+t) 步的充电功率 kW
        index = [(i, t) for (i, ev) in connected
                 for t in range(max(1, ev.time_of_departure - now))]
        p = prob.add_variable_dict("p_%d_%d", index, cat=pulp.LpContinuous, lowBound=0)
        cap = {i: min(p_max, float(ev.max_ac_charge_power)) for (i, ev) in connected}
        for (i, t) in index:
            p[(i, t)].upBound = cap[i]

        peak = prob.add_variable("peak", lowBound=0)

        horizon = max(t for (_, t) in index) + 1
        obj_terms = []
        for t in range(horizon):
            step_load = pulp.lpSum(p[(i, t)] for (i, ev) in connected
                                   if (i, t) in p)
            prob += (step_load <= tr_max, f"tr_{t}")
            prob += (peak >= step_load, f"peak_{t}")
            obj_terms.append(price_at(now + t) * dt_h * step_load)

        for (i, ev) in connected:
            r = max(1, ev.time_of_departure - now)
            need = max(0.0, float(ev.desired_capacity) - float(ev.current_capacity))
            # CCCV 长尾：SOC>0.8 后指数衰减，充满需额外时间。
            # 把能量需求的完成时限收紧 tail 步，为衰减尾段预留时间。
            tail = int(math.ceil(0.2 * float(ev.battery_capacity)
                                 / (cap[i] * dt_h) * 3)) + 1
            r_eff = max(1, r - tail)
            prob += (pulp.lpSum(p[(i, t)] for t in range(r_eff)) * dt_h
                     >= min(need, cap[i] * dt_h * r_eff),
                     f"need_{i}")
            # 平均速率下限：当前步功率 >= 剩余需求/有效剩余时间，
            # 防止 MPC 在滚动重解中无限推迟充电导致离场未充满
            min_rate = min(cap[i], need / (dt_h * r_eff))
            if min_rate > 0:
                prob += (p[(i, 0)] >= min_rate, f"minrate_{i}")

        prob += pulp.lpSum(obj_terms) + PEAK_LAMBDA * peak
        prob.solve(pulp.HiGHS(msg=False, timeLimit=10))

        action = np.zeros(n, dtype=np.float64)
        for (i, ev) in connected:
            v = p[(i, 0)].value()
            if v:
                action[i] = np.clip(v / p_max, 0.0, 1.0)
        return action

    return policy


def make_dqn_policy(env_raw, seed):
    """加载用户预训练 DQN（仅 5 桩）；返回 (wrapped_env, predict_fn)"""
    from stable_baselines3 import DQN
    from stable_baselines3.common.monitor import Monitor

    assert env_raw.number_of_ports == DQN_N_PORTS, "DQN 预训练模型仅支持 5 桩"
    env = DiscretePowerActionWrapper(env_raw)
    env = Monitor(env)
    model = DQN.load(DQN_MODEL, env=env)

    def predict(obs):
        a, _ = model.predict(obs, deterministic=True)
        return int(a)

    return env, predict


# ---------------------------------------------------------------------------
# 仿真主循环与日志
# ---------------------------------------------------------------------------
def rollout(base_env, policy, seed, wrapped_env=None):
    """
    wrapped_env 为 None 时直接 step(base_env)（动作=功率比例向量）；
    否则 step(wrapped_env)（DQN：动作=整数，policy 用包装后 obs 推理）。
    日志一律从 base_env（未包装 EV2Gym）读取。
    """
    step_env = wrapped_env if wrapped_env is not None else base_env
    obs, _ = step_env.reset(seed=seed)
    base_env.cumulative_cost = 0.0

    n_ports = base_env.number_of_ports
    rows = []
    prev_cum = 0.0
    done = False
    while not done:
        if wrapped_env is not None:
            action = policy(obs)
        else:
            action = policy(base_env, obs)
        obs, _r, term, trunc, _info = step_env.step(action)
        done = term or trunc

        t = base_env.current_step - 1
        step_time = base_env.sim_date - timedelta(minutes=base_env.timescale)
        cum = float(getattr(base_env, "cumulative_cost", 0.0))
        prices = extract_price_curve(base_env)
        price = -float(prices[min(t, len(prices) - 1)])

        row = {
            "step": t,
            "time": step_time.strftime("%Y-%m-%d %H:%M"),
            "total_load_kw": float(base_env.current_power_usage[t]),
            "step_cost": cum - prev_cum,
            "cumulative_cost": cum,
            "price_eur_kwh": price,
        }
        for i, cs in enumerate(base_env.charging_stations):
            ev = cs.evs_connected[0] if cs.evs_connected else None
            row[f"port_{i}_soc"] = float(ev.get_soc()) if ev is not None else np.nan
        rows.append(row)
        prev_cum = cum

    return pd.DataFrame(rows)


def collect_vehicles(base_env):
    recs = []
    for ev in base_env.EVs:
        completed = bool(ev.current_capacity >= ev.desired_capacity - 1e-6)
        recs.append({
            "arrival_step": int(ev.time_of_arrival),
            "departure_step": int(ev.time_of_departure),
            "battery_capacity_kwh": float(ev.battery_capacity),
            "final_capacity_kwh": float(ev.current_capacity),
            "desired_capacity_kwh": float(ev.desired_capacity),
            "final_soc": float(ev.get_soc()),
            "completed": completed,
        })
    return pd.DataFrame(recs)


def compute_metrics(base_env, ts_df, veh_df, strategy, n_piles, seed):
    stats = base_env.stats
    served = int(stats["total_ev_served"])
    completed = int(veh_df["completed"].sum()) if len(veh_df) else 0
    return {
        "strategy": strategy,
        "n_piles": n_piles,
        "seed": seed,
        "peak_kw": float(ts_df["total_load_kw"].max()),
        "completion_rate": (completed / served) if served else 0.0,
        "total_cost_eur": float(-stats["total_profits"]),
        "total_ev_served": served,
        "avg_user_satisfaction": float(stats["average_user_satisfaction"]),
    }


def run_strategy(strategy, n_piles, seed):
    env, cfg = make_env(n_piles, seed)
    wrapped = None
    if strategy == "fcfs":
        policy = fcfs_action
    elif strategy == "pulp":
        policy = make_pulp_policy(cfg)
    elif strategy == "dqn":
        wrapped, predict = make_dqn_policy(env, seed)
        policy = predict
    else:
        raise ValueError(strategy)

    ts_df = rollout(env, policy, seed, wrapped_env=wrapped)
    veh_df = collect_vehicles(env)
    metrics = compute_metrics(env, ts_df, veh_df, strategy, n_piles, seed)

    out_dir = os.path.join(LOG_DIR, f"{strategy}_{n_piles}p")
    os.makedirs(out_dir, exist_ok=True)
    ts_df.to_csv(os.path.join(out_dir, "timeseries.csv"),
                 index=False, encoding="utf-8-sig")
    veh_df.to_csv(os.path.join(out_dir, "vehicles.csv"),
                  index=False, encoding="utf-8-sig")
    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piles", type=int, default=5)
    ap.add_argument("--seed", type=int, default=2024)
    ap.add_argument("--strategies", type=str, default="fcfs,pulp,dqn")
    args = ap.parse_args()

    strategies = [s.strip() for s in args.strategies.split(",") if s.strip()]
    if args.piles != DQN_N_PORTS and "dqn" in strategies:
        print(f"[提示] 桩数={args.piles}≠{DQN_N_PORTS}，DQN 使用 5 桩预训练模型，跳过重跑")
        strategies.remove("dqn")

    all_metrics = []
    for s in strategies:
        print(f"=== 运行 {s} | 桩数={args.piles} | 种子={args.seed} ===")
        m = run_strategy(s, args.piles, args.seed)
        all_metrics.append(m)
        print(json.dumps(m, ensure_ascii=False))

    # 汇总表：整合同桩数全部策略的 metrics.json
    rows = []
    if os.path.isdir(LOG_DIR):
        for d in sorted(os.listdir(LOG_DIR)):
            mj = os.path.join(LOG_DIR, d, "metrics.json")
            if os.path.isfile(mj):
                with open(mj, encoding="utf-8") as f:
                    rows.append(json.load(f))
    if rows:
        pd.DataFrame(rows).to_csv(os.path.join(LOG_DIR, "summary.csv"),
                                  index=False, encoding="utf-8-sig")
    print("完成。日志目录:", LOG_DIR)


if __name__ == "__main__":
    main()
