"""电动汽车充电调度场景：生成、读写与校验。

所有方法（静态最优 MILP / DQN / FCFS）共用同一份 scenario.json，
保证到达时间、离开时间、目标 SOC 等全信息一致，结果才能放在一起画图对比。

时间离散约定
    时间轴被均分为 T 个时间步，每步 dt_h 小时。第 t 步覆盖区间 [t*dt_h, (t+1)*dt_h)。
    第 0 步对应的时钟时刻为 start_hour（24 小时制），因此 scene.clock_hour(t) 可把
    步索引映射回时钟时间。
    第 i 辆车在第 t 步可充电当且仅当 arrival_step <= t < departure_step，
    即"离开前充完"等价于在 departure_step 之前（含该步结束时刻）完成充电，不发生时间穿越。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

# 住宅负荷日模板（锚点：小时 -> kW），傍晚 19:00 附近出现晚高峰
_BASE_ANCHORS = [
    (0.0, 110.0),
    (4.0, 95.0),
    (6.0, 120.0),
    (8.0, 165.0),
    (11.0, 175.0),
    (14.0, 185.0),
    (17.0, 235.0),
    (19.0, 300.0),
    (20.0, 285.0),
    (21.0, 250.0),
    (22.0, 190.0),
    (23.0, 140.0),
    (24.0, 110.0),
]

# 电池容量 / 充电功率的可选集合
_BATTERY_CHOICES = [40.0, 55.0, 60.0, 75.0, 82.0]
_PMAX_CHOICES = [7.4] * 7 + [11.0] * 2 + [22.0]

# 车辆到家与次日离开的时间范围（小时，24 小时制）
_HOME_HOUR_RANGE = (17.0, 22.0)
_LEAVE_HOUR_RANGE = (7.0, 9.0)


@dataclass
class EVSpec:
    """单辆电动汽车的静态信息（全信息规划的前提：已知到达、离开与目标 SOC）。"""

    id: str
    arrival_step: int
    departure_step: int
    battery_kwh: float
    soc_init: float
    soc_target: float
    pmax_kw: float

    @property
    def window_steps(self) -> list[int]:
        """可充电的时间步：半开区间 [arrival_step, departure_step)。"""
        return list(range(self.arrival_step, self.departure_step))

    @property
    def n_steps_available(self) -> int:
        """可充电的时间步数量（乘以 dt_h 即得到可用小时数）。"""
        return int(self.departure_step - self.arrival_step)

    @property
    def energy_req_kwh(self) -> float:
        """离开前必须补入的电量（kWh）。"""
        return max(0.0, (self.soc_target - self.soc_init) * self.battery_kwh)


@dataclass
class Scenario:
    """一套完整的充电场景，可序列化为 JSON 供各方法共享。"""

    name: str
    seed: int
    dt_h: float
    T: int
    start_hour: float
    transformer_limit_kw: float
    base_load_kw: list[float]
    evs: list[EVSpec] = field(default_factory=list)

    # ---------- 基本属性 ----------
    @property
    def n_ev(self) -> int:
        return len(self.evs)

    @property
    def ev_ids(self) -> list[str]:
        return [ev.id for ev in self.evs]

    def clock_hour(self, t: int) -> float:
        """第 t 步开始的时钟时刻（0~24）。"""
        return float((self.start_hour + t * self.dt_h) % 24.0)

    def hour_label(self, t: int) -> str:
        h = self.clock_hour(t)
        return f"{int(h):02d}:{int(round((h - int(h)) * 60)):02d}"

    def evs_active_at(self, t: int) -> list[EVSpec]:
        return [ev for ev in self.evs if ev.arrival_step <= t < ev.departure_step]

    # ---------- 序列化 ----------
    def to_dict(self) -> dict:
        d = asdict(self)
        d["base_load_kw"] = [float(v) for v in self.base_load_kw]
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Scenario":
        evs = [EVSpec(**ev) for ev in data["evs"]]
        return cls(
            name=str(data.get("name", "scenario")),
            seed=int(data.get("seed", 0)),
            dt_h=float(data["dt_h"]),
            T=int(data["T"]),
            start_hour=float(data.get("start_hour", 0.0)),
            transformer_limit_kw=float(data["transformer_limit_kw"]),
            base_load_kw=[float(v) for v in data["base_load_kw"]],
            evs=evs,
        )

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> "Scenario":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def validate(self) -> list[str]:
        """返回问题列表（为空表示场景自洽）。"""
        problems: list[str] = []
        if len(self.base_load_kw) != self.T:
            problems.append(f"base_load_kw 长度 {len(self.base_load_kw)} != T={self.T}")
        if self.dt_h <= 0 or self.T <= 0:
            problems.append("dt_h / T 必须为正")
        for ev in self.evs:
            if not (0 <= ev.arrival_step < ev.departure_step <= self.T):
                problems.append(f"{ev.id}: 到达/离开步越界 ({ev.arrival_step}, {ev.departure_step})")
            if ev.pmax_kw <= 0 or ev.battery_kwh <= 0:
                problems.append(f"{ev.id}: Pmax 或电池容量非正")
            if not (0.0 <= ev.soc_init < ev.soc_target <= 1.0):
                problems.append(f"{ev.id}: SOC 区间非法 ({ev.soc_init} -> {ev.soc_target})")
            capacity = ev.n_steps_available * self.dt_h * ev.pmax_kw
            if ev.energy_req_kwh > capacity + 1e-9:
                problems.append(
                    f"{ev.id}: 窗口内物理不可行（需求 {ev.energy_req_kwh:.2f} kWh > 容量 {capacity:.2f} kWh）"
                )
        return problems


def daily_base_load(T: int, dt_h: float, start_hour: float, seed: int = 0) -> np.ndarray:
    """按日模板生成不含 EV 的基础负荷曲线（kW）。"""
    hours = np.array([(start_hour + t * dt_h) % 24.0 for t in range(T)], dtype=float)
    xs = np.array([a for a, _ in _BASE_ANCHORS], dtype=float)
    ys = np.array([b for _, b in _BASE_ANCHORS], dtype=float)
    profile = np.interp(hours, xs, ys)

    rng = np.random.default_rng(seed + 991)
    noise = rng.normal(0.0, 1.0, size=T)
    kernel = np.ones(7) / 7.0
    noise = np.convolve(np.concatenate([noise[-3:], noise, noise[:3]]), kernel, mode="same")[3:-3]
    profile = profile * (1.0 + 0.03 * noise)
    return np.round(profile, 3)


def generate_scenario(
    seed: int = 0,
    n_ev: int = 40,
    transformer_limit_kw: float = 380.0,
    T: int = 96,
    dt_h: float = 0.25,
    start_hour: float = 12.0,
    name: str | None = None,
) -> Scenario:
    """生成一套住宅小区有序充电场景。

    时间轴从 12:00 开始（避免跨零点带来的时间回绕），车辆 17:00~22:00 到家、
    次日 7:00~9:00 离开，正好落在傍晚基础负荷高峰与凌晨低谷之间。
    """
    rng = np.random.default_rng(seed)
    base = daily_base_load(T, dt_h, start_hour, seed=seed)

    def to_step(hour: float) -> int:
        return int(round(((hour - start_hour) % 24.0) / dt_h)) % T

    evs: list[EVSpec] = []
    for i in range(n_ev):
        arrival_h = float(rng.uniform(*_HOME_HOUR_RANGE))
        departure_h = float(rng.uniform(*_LEAVE_HOUR_RANGE))
        a = to_step(arrival_h)
        d = to_step(departure_h)
        if d <= a:  # 兜底：离开步必须晚于到达步
            d = a + max(1, int(round(8.0 / dt_h)))

        battery = float(rng.choice(_BATTERY_CHOICES))
        pmax = float(rng.choice(_PMAX_CHOICES))
        soc_init = round(float(rng.uniform(0.25, 0.55)), 3)
        soc_target = round(float(rng.uniform(0.85, 1.0)), 3)

        # 保证窗口内物理可行：需求不超过 85% 的窗口充电能力
        window_h = (d - a) * dt_h
        max_energy = 0.85 * window_h * pmax
        if (soc_target - soc_init) * battery > max_energy:
            soc_target = round(min(soc_target, soc_init + max_energy / battery), 4)
            soc_target = max(soc_target, min(1.0, soc_init + 0.05))

        evs.append(
            EVSpec(
                id=f"EV_{i:03d}",
                arrival_step=a,
                departure_step=d,
                battery_kwh=battery,
                soc_init=soc_init,
                soc_target=round(soc_target, 4),
                pmax_kw=pmax,
            )
        )

    scenario = Scenario(
        name=name or f"residential_{n_ev}ev_seed{seed}",
        seed=seed,
        dt_h=dt_h,
        T=T,
        start_hour=start_hour,
        transformer_limit_kw=transformer_limit_kw,
        base_load_kw=[float(v) for v in base],
        evs=evs,
    )
    return scenario


def load_or_create_scenario(
    path: str | Path = "scenario.json",
    regenerate: bool = False,
    **kwargs,
) -> Scenario:
    """读取共享场景；不存在（或要求重建）时按 kwargs 生成并落盘。"""
    path = Path(path)
    if path.exists() and not regenerate:
        return Scenario.load(path)
    scenario = generate_scenario(**kwargs)
    scenario.save(path)
    return scenario
