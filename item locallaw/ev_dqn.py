# -*- coding: utf-8 -*-
"""
基于 ev2gym + stable-baselines3 DQN 的电动汽车充电调度仿真
=============================================================

场景：
    - 5 个充电桩（每个充电站 1 个端口，共 5 个充电端口）
    - 车辆按照真实到达分布随机到达（public 公共充电场景）
    - 变压器容量 40 kW，5 个桩满功率合计 55 kW，形成调度压力

状态空间（12 维向量）：
    [ 当前仿真时刻(归一化),
      5 个端口上在线车辆的 SOC(无车为 0),
      5 个端口上在线车辆的预估剩余停留时长(归一化，无车为 0),
      当前总负荷(kW) ]

动作空间（离散）：
    DQN 仅支持单一 Discrete 动作空间，因此将每个端口的功率档位
    {0, 0.5, 1.0} × 桩最大电流 组合成联合动作，共 3^5 = 243 个离散动作。
    整数动作按 3 进制解码为 5 个端口的功率比例。
    约束（不简化，由 ev2gym 内部物理模型保证）：
      - 每端口实际电流 <= 桩最大充电电流(16A)
      - 每辆车实际功率 <= min(桩最大功率, 车辆最大交流充电功率)
      - 电池采用两段线性 CCCV 模型：SOC > transition_soc(0.8) 后充电速率线性衰减
      - 电池容量上限 100%，SOC 充满后无法继续充入
      - 空端口动作自动置 0；车辆到达预估离开时刻后自动离场

奖励函数（严格按照任务要求）：
    reward = -0.7 * 总负荷 - 0.3 * 累计电费
    若有车辆离场时 SOC < 目标 SOC，每辆追加固定惩罚 -15

输出：
    1. 训练完成后保存模型 dqn_ev_scheduler.zip
    2. 测试阶段记录时序数据到 list（时间、总负荷、各车 SOC），便于后续 Plotly 绘图
    3. 评估指标：峰值负荷、充电完成率、总电费
"""

import os
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from ev2gym.models.ev2gym_env import EV2Gym
from stable_baselines3 import DQN
from stable_baselines3.common.monitor import Monitor

# ----------------------------------------------------------------------------
# 全局参数
# ----------------------------------------------------------------------------
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ev_config.yaml")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dqn_ev_scheduler")

N_PORTS = 5          # 充电桩（端口）数量
N_LEVELS = 3         # 每个桩的功率档位数：0 / 50% / 100%
TOTAL_TIMESTEPS = 30000   # DQN 训练总步数（每局 96 步，约 300+ 局）

# 奖励权重（严格按任务要求）
W_LOAD = 0.7         # 总负荷权重
W_COST = 0.3         # 累计电费权重
SOC_PENALTY = 15.0   # 离场未达目标 SOC 的固定惩罚


# ----------------------------------------------------------------------------
# 自定义状态函数
# ----------------------------------------------------------------------------
def ev_scheduling_state(env):
    """
    状态向量（12 维）：
        1. 当前仿真时刻（归一化到 [0,1]）
        2. 5 个端口在线车辆的 SOC（无车端口为 0）
        3. 5 个端口在线车辆的预估剩余停留时长（归一化，无车端口为 0）
        4. 当前总负荷（上一步全场充电功率，kW）
    """
    # 1) 当前仿真时刻
    state = [env.current_step / env.simulation_length]

    # 2) 各端口在线车辆 SOC
    for cs in env.charging_stations:
        ev = cs.evs_connected[0]           # 每站 1 个端口
        state.append(ev.get_soc() if ev is not None else 0.0)

    # 3) 各端口在线车辆的预估剩余停留时长（离开步 - 当前步，归一化）
    for cs in env.charging_stations:
        ev = cs.evs_connected[0]
        if ev is not None:
            remaining = (ev.time_of_departure - env.current_step) / env.simulation_length
            state.append(remaining)
        else:
            state.append(0.0)

    # 4) 当前总负荷：上一步全场充电功率之和 (kW)
    #    current_step=0 时上一步不存在，取 0
    if env.current_step > 0:
        total_load = env.current_power_usage[env.current_step - 1]
    else:
        total_load = 0.0
    state.append(total_load)

    return np.array(state, dtype=np.float64)


# ----------------------------------------------------------------------------
# 自定义奖励函数
# ----------------------------------------------------------------------------
def ev_scheduling_reward(env, total_costs, user_satisfaction_list, invalid_action_punishment):
    """
    reward = -0.7 * 总负荷 - 0.3 * 累计电费
    车辆离场时若 SOC < 目标 SOC，每辆追加固定惩罚 -15。

    说明：
    - 总负荷 = 刚执行完的一步的全场充电功率 (kW)
    - ev2gym 中充电电价为负值，total_costs = 能量 × 电价 <= 0，
      因此本步实际电费 = -total_costs（充电时为正）
    - 累计电费挂载在 env 上，跨步累加；reset 时由包装器清零
    """
    # 当前总负荷 (kW)
    total_load = env.current_power_usage[env.current_step - 1]

    # 本步电费（欧元）：取负使充电成本为正
    step_cost = -total_costs

    # 累计电费（惰性初始化，兼容 env 内部 reset）
    env.cumulative_cost = getattr(env, "cumulative_cost", 0.0) + step_cost

    # 主奖励项
    reward = (-1) * W_LOAD * total_load + (-1) * W_COST * env.cumulative_cost

    # 离场未达目标 SOC 的固定惩罚
    for ev in env.departing_evs:
        if ev.current_capacity < ev.desired_capacity - 1e-6:
            reward -= SOC_PENALTY

    return reward


# ----------------------------------------------------------------------------
# 离散动作包装器：Discrete(3^5) -> 每端口功率比例 [0, 0.5, 1.0]
# ----------------------------------------------------------------------------
class DiscretePowerActionWrapper(gym.ActionWrapper):
    """
    将单一整数动作（0 ~ 3^5-1）按 3 进制解码为 5 个端口的功率比例。
    例如动作 0 = 全部不充电，动作 242 = 全部满功率充电。
    ev2gym 内部会将功率比例 × 桩最大电流，并施加车辆/电池物理约束。
    """

    def __init__(self, env, n_levels=N_LEVELS):
        super().__init__(env)
        self.n_ports = env.number_of_ports     # 5
        self.n_levels = n_levels               # 3 档
        # 联合离散动作空间：3^5 = 243
        self.action_space = spaces.Discrete(n_levels ** self.n_ports)

    def action(self, act):
        """整数动作 -> 各端口功率比例向量（[0,1]，ev2gym 动作格式）"""
        fractions = np.zeros(self.n_ports, dtype=np.float64)
        remaining = int(act)
        for i in range(self.n_ports):
            digit = remaining % self.n_levels
            remaining //= self.n_levels
            fractions[i] = digit / (self.n_levels - 1)   # 0, 0.5, 1.0
        return fractions


# ----------------------------------------------------------------------------
# 构建环境
# ----------------------------------------------------------------------------
def make_env(seed=None):
    """创建包装后的 ev2gym 环境（自定义状态/奖励 + 离散动作）"""
    env = EV2Gym(
        config_file=CONFIG_FILE,
        generate_rnd_game=True,
        seed=seed,
        save_replay=False,
        save_plots=False,
        state_function=ev_scheduling_state,     # 自定义状态
        reward_function=ev_scheduling_reward,   # 自定义奖励
        empty_ports_at_end_of_simulation=True,  # 仿真结束前清空端口，保证所有车辆都有离场结算
        verbose=False,
    )
    env = DiscretePowerActionWrapper(env)
    env = Monitor(env)
    return env


# ----------------------------------------------------------------------------
# 训练
# ----------------------------------------------------------------------------
def train():
    env = make_env(seed=42)

    model = DQN(
        policy="MlpPolicy",
        env=env,
        learning_rate=1e-3,
        buffer_size=50000,            # 经验回放池大小
        learning_starts=1000,         # 随机探索 1000 步后开始学习
        batch_size=64,
        gamma=0.99,                   # 折扣因子
        train_freq=4,                 # 每 4 步训练一次
        gradient_steps=1,
        target_update_interval=500,   # 目标网络更新间隔
        exploration_fraction=0.4,     # epsilon 线性衰减区间占比
        exploration_initial_eps=1.0,
        exploration_final_eps=0.05,
        policy_kwargs=dict(net_arch=[128, 128]),
        seed=42,
        verbose=1,
    )

    print("=" * 70)
    print("开始训练 DQN ...")
    print("=" * 70)
    model.learn(total_timesteps=TOTAL_TIMESTEPS, log_interval=10)

    # 保存模型
    model.save(MODEL_PATH)
    print(f"\n模型已保存至: {MODEL_PATH}.zip")
    return model


# ----------------------------------------------------------------------------
# 测试：记录时序数据并计算评估指标
# ----------------------------------------------------------------------------
def test(model=None, n_episodes=1, seed=2024):
    if model is None:
        model = DQN.load(MODEL_PATH)

    env = make_env(seed=seed)
    base_env = env.unwrapped          # 未包装的 EV2Gym 环境，用于读取内部状态

    # ---------------- 时序数据记录列表（供后续 Plotly 绘图使用） ----------------
    time_list = []                    # 每步的时间戳（仿真时刻字符串）
    total_load_list = []              # 每步总负荷 (kW)
    soc_list = [[] for _ in range(N_PORTS)]   # 各端口车辆 SOC 时序（无车记 np.nan）
    cost_list = []                    # 每步电费（欧元）
    cumulative_cost_list = []         # 累计电费（欧元）

    # 评估指标累计
    total_ev_departed = 0             # 离场车辆总数
    total_ev_completed = 0            # 离场时 SOC 达标车辆数
    total_electricity_cost = 0.0      # 总电费

    for ep in range(n_episodes):
        obs, _ = env.reset()
        base_env.cumulative_cost = 0.0    # 清零累计电费（奖励函数中的挂载变量）
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            # ---- 记录刚执行完的一步（step 索引 = current_step - 1） ----
            t = base_env.current_step - 1

            # 时间戳：step 后 sim_date 已前进一步，回退一个步长得到本步时刻
            from datetime import timedelta
            step_time = base_env.sim_date - timedelta(minutes=base_env.timescale)
            time_list.append(step_time.strftime("%Y-%m-%d %H:%M"))

            # 总负荷 (kW)
            total_load_list.append(float(base_env.current_power_usage[t]))

            # 各端口车辆 SOC（无车端口记 np.nan，便于 Plotly 断线显示）
            for i, cs in enumerate(base_env.charging_stations):
                ev = cs.evs_connected[0]
                soc_list[i].append(float(ev.get_soc()) if ev is not None else np.nan)

            # 电费：充电电价为负，累计电费 = -累计(能量 × 电价)，
            # 每步电费由累计值差分得到
            cumulative = float(getattr(base_env, "cumulative_cost", 0.0))
            prev = cumulative_cost_list[-1] if cumulative_cost_list else 0.0
            cost_list.append(cumulative - prev)
            cumulative_cost_list.append(cumulative)

        # ---------------- 局末统计 ----------------
        stats = base_env.stats
        ep_departed = int(stats["total_ev_served"])
        # 充电完成率：遍历本局所有生成车辆，离场 SOC >= 目标 SOC 记为完成
        ep_completed = sum(
            1 for ev in base_env.EVs
            if ev.current_capacity >= ev.desired_capacity - 1e-6
        )
        # 总电费 = -总利润（充电电价为负 → 利润为负 → 成本为正）
        ep_cost = float(-stats["total_profits"])

        total_ev_departed += ep_departed
        total_ev_completed += ep_completed
        total_electricity_cost += ep_cost

        print(f"\n[测试局 {ep + 1}/{n_episodes}] "
              f"服务车辆: {ep_departed} | 达标车辆: {ep_completed} | "
              f"平均用户满意度: {stats['average_user_satisfaction']:.3f}")

    # ============================ 评估指标输出 ============================
    peak_load = float(np.max(total_load_list)) if total_load_list else 0.0
    completion_rate = (total_ev_completed / total_ev_departed
                       if total_ev_departed > 0 else 0.0)

    print("\n" + "=" * 70)
    print("评估指标")
    print("=" * 70)
    print(f"峰值负荷      : {peak_load:.2f} kW")
    print(f"充电完成率    : {completion_rate * 100:.1f}% "
          f"({total_ev_completed}/{total_ev_departed} 辆离场时 SOC 达标)")
    print(f"总电费        : {total_electricity_cost:.2f} €")
    print("=" * 70)

    # ---------------- 时序数据（list），供后续 Plotly 绘图 ----------------
    # time_list        : 时间戳列表，长度 = 测试总步数
    # total_load_list  : 总负荷时序 (kW)
    # soc_list         : 5 个端口各自的 SOC 时序（无车为 np.nan）
    # cost_list        : 每步电费
    # cumulative_cost_list : 累计电费
    timeseries = {
        "time": time_list,
        "total_load": total_load_list,
        "soc_per_port": soc_list,
        "step_cost": cost_list,
        "cumulative_cost": cumulative_cost_list,
    }
    metrics = {
        "peak_load_kw": peak_load,
        "completion_rate": completion_rate,
        "total_electricity_cost": total_electricity_cost,
    }
    return timeseries, metrics


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. 训练并保存模型
    model = train()

    # 2. 测试：记录时序数据 + 输出评估指标
    timeseries, metrics = test(model=model, n_episodes=1, seed=2024)

    # 3. 打印部分时序数据示例（前 10 步），完整数据在 timeseries 各 list 中
    print("\n时序数据示例（前 10 步）：")
    print(f"{'时间':<18}{'总负荷(kW)':>10}"
          + "".join(f"{f'桩{i + 1}SOC':>10}" for i in range(N_PORTS)))
    for k in range(min(10, len(timeseries["time"]))):
        row = f"{timeseries['time'][k]:<18}{timeseries['total_load'][k]:>10.2f}"
        for i in range(N_PORTS):
            soc = timeseries["soc_per_port"][i][k]
            row += f"{soc:>10.2f}" if not np.isnan(soc) else f"{'--':>10}"
        print(row)
