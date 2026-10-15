"""电动汽车有序充电——静态规划（全信息，PuLP MILP）。

问题：已知所有车辆的到达时刻、离开时刻、初始/目标 SOC，统一求解每辆车每个时间步的
充电功率，使系统总负荷峰值最小。

决策变量
    p[i, t]   车辆 i 在时间步 t 的充电功率（kW），仅在其可充电窗口内有定义
    peak      系统总负荷峰值（kW），即 max_t (base[t] + Σ_i p[i,t])
    unmet[i]  车辆 i 未能充入的电量（kWh），仅用于物理不可行时的软约束

目标（两阶段）
    阶段 1：min  peak + M * Σ_i unmet[i]
            主目标是峰值最小；M 取足够大（默认 1e3），保证"满足充电需求"优先于"压低峰值"，
            同时避免"窗口内充不满"导致的模型不可行。
    阶段 2（可关掉）：在 peak <= peak* + tol、unmet[i] <= unmet*[i] 的前提下，
            min Σ_i Σ_t p[i,t] * base[t]
            峰值最优解通常不唯一，不加第二阶段会出现"临离开前集中大功率充电"的退化解；
            该线性权重把充电推到基础负荷低谷，得到与 DQN（谷时充电）、FCFS（即到即充）可比的自然解，
            且不改变峰值最优性。

约束
    (1) 变压器容量：base[t] + Σ_i p[i,t] <= peak <= transformer_limit，对任意 t 成立
    (2) 离开前充到目标 SOC：Σ_t p[i,t] * dt_h + unmet[i] = E_req[i]
    (3) 单辆车功率：0 <= p[i,t] <= Pmax_i，且窗口外恒为 0（用变量上界实现）

输出（默认 results/<method>/）
    charging_power.npy    (T, N) 充电功率矩阵，kW
    charging_power.csv    含 time 列的功率矩阵（便于和 DQN/FCFS 直接对齐绘图）
    ev_records.csv        每辆车需求电量、实充电量、终止 SOC、是否成功
    load_profile.csv      逐时间步基础负荷 / EV 负荷 / 总负荷，供峰值与曲线对比
    summary.json          峰值、充电成功率、约束校验等汇总指标
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pulp

from ev_scenario import Scenario, load_or_create_scenario

ROOT = Path(__file__).resolve().parent

# 求解器返回的数值容差：HiGHS 的可行性容差为 1e-7 量级，电量判定必须留出余量，
# 否则会把"已充满但差 1e-5 kWh"的车误判为失败。
SOC_TOL_KWH = 1e-3
POWER_TOL_KW = 1e-6


# --------------------------------------------------------------------------- #
# 求解器选择
# --------------------------------------------------------------------------- #
def build_solver(name: str = "auto") -> pulp.LpSolver:
    """返回可用的 PuLP 求解器；auto 时依次尝试 HiGHS、Gurobi，最后回落到 PuLP 默认求解器。"""
    candidates: dict[str, list] = {
        "highs": [pulp.HiGHS],
        "gurobi": [pulp.GUROBI],
        "auto": [pulp.HiGHS, pulp.GUROBI],
    }
    if name not in candidates:
        raise ValueError(f"未知求解器 {name!r}，可选：{sorted(candidates)}")
    for cls in candidates[name]:
        try:
            solver = cls(msg=False)
        except Exception:
            continue
        if solver.available():
            return solver
    if name == "auto" and pulp.LpSolverDefault is not None:
        return pulp.LpSolverDefault
    raise RuntimeError(f"求解器 {name!r} 不可用，请安装对应后端（如 pip install highspy）")


# --------------------------------------------------------------------------- #
# 建模与求解
# --------------------------------------------------------------------------- #
def solve_static(
    scenario: Scenario,
    solver: pulp.LpSolver | None = None,
    tie_break: bool = True,
    m_penalty: float = 1e3,
    tol: float = 1e-3,
) -> dict:
    """求解静态最优有序充电，返回 (充电功率矩阵, 峰值, 未满足电量, 求解信息)。"""
    T = scenario.T
    dt = scenario.dt_h
    evs = scenario.evs
    base = list(scenario.base_load_kw)
    limit = scenario.transformer_limit_kw

    prob = pulp.LpProblem("EV_charging_peak_shaving", pulp.LpMinimize)

    peak = prob.add_variable("peak_kw", 0.0, limit)
    p: dict[str, dict[int, pulp.LpVariable]] = {}
    unmet: dict[str, pulp.LpVariable] = {}
    for ev in evs:
        p[ev.id] = prob.add_variable_dict(f"p_{ev.id}", ev.window_steps, 0.0, ev.pmax_kw)
        unmet[ev.id] = prob.add_variable(f"unmet_{ev.id}", 0.0, ev.energy_req_kwh)

    # 约束 (1)：每个时间步的变压器容量 / 峰值定义
    for t in range(T):
        active = scenario.evs_active_at(t)
        if not active:
            continue
        expr = pulp.lpSum(p[ev.id][t] for ev in active) + base[t]
        prob += (expr <= peak, f"load_at_{t}")

    # 约束 (2)：离开前充到目标 SOC（缺电 slack 保证模型不因个别车不可行而整体失败）
    for ev in evs:
        delivered = pulp.lpSum(p[ev.id][t] for t in ev.window_steps) * dt
        prob += (delivered + unmet[ev.id] == ev.energy_req_kwh, f"soc_{ev.id}")

    # 阶段 1：最小化峰值（惩罚项只在需求无法满足时才起作用）
    prob += peak + m_penalty * pulp.lpSum(list(unmet.values())), "min_peak"
    solver = solver or build_solver("auto")
    stats1 = prob.solve(solver)
    if not stats1.has_solution:
        raise RuntimeError(f"阶段 1 求解失败：{stats1.status}")

    peak_star = float(peak.value())
    unmet_star = {ev.id: max(0.0, float(unmet[ev.id].value())) for ev in evs}

    stats2 = None
    if tie_break:
        # 阶段 2：锁定峰值最优解，把充电尽量移到基础负荷低谷（去退化，不影响峰值最优性）
        prob += (peak <= peak_star + tol, "peak_upper_bound")
        for ev in evs:
            prob += (unmet[ev.id] <= unmet_star[ev.id] + 1e-6, f"unmet_upper_bound_{ev.id}")
        prob.setObjective(
            pulp.lpSum(p[ev.id][t] * base[t] for ev in evs for t in ev.window_steps)
        )
        stats2 = prob.solve(solver)
        if not stats2.has_solution:
            raise RuntimeError(f"阶段 2 求解失败：{stats2.status}")

    # 提取结果
    P = np.zeros((len(evs), T), dtype=float)
    for i, ev in enumerate(evs):
        for t in ev.window_steps:
            v = p[ev.id][t].value()
            P[i, t] = 0.0 if v is None else float(v)
    P[np.abs(P) < 1e-9] = 0.0

    return {
        "power_kw": P,
        "peak_kw": float(peak.value()),
        "unmet_kwh": {ev.id: max(0.0, float(unmet[ev.id].value())) for ev in evs},
        "stage1": stats1,
        "stage2": stats2,
        "solver_name": stats1.solver,
        "tie_break": tie_break,
    }


# --------------------------------------------------------------------------- #
# 指标与约束校验
# --------------------------------------------------------------------------- #
def evaluate(scenario: Scenario, power_kw: np.ndarray, unmet_kwh: dict[str, float]) -> dict:
    """计算峰值、充电成功率并逐条校验三类约束。"""
    dt = scenario.dt_h
    base = np.asarray(scenario.base_load_kw, dtype=float)
    ev_load = power_kw.sum(axis=0)
    total = base + ev_load

    records = []
    for i, ev in enumerate(scenario.evs):
        delivered = float(power_kw[i].sum() * dt)
        req = ev.energy_req_kwh
        soc_end = min(1.0, ev.soc_init + delivered / ev.battery_kwh)
        ok = delivered >= req - SOC_TOL_KWH
        records.append(
            {
                "ev_id": ev.id,
                "arrival_step": ev.arrival_step,
                "departure_step": ev.departure_step,
                "arrival_hour": round(scenario.clock_hour(ev.arrival_step), 2),
                "departure_hour": round(scenario.clock_hour(ev.departure_step), 2),
                "available_steps": ev.n_steps_available,
                "pmax_kw": ev.pmax_kw,
                "battery_kwh": ev.battery_kwh,
                "soc_init": ev.soc_init,
                "soc_target": ev.soc_target,
                "energy_req_kwh": round(req, 6),
                "energy_delivered_kwh": round(delivered, 6),
                "unmet_kwh": round(float(unmet_kwh.get(ev.id, 0.0)), 6),
                "soc_end": round(soc_end, 6),
                "success": bool(ok),
            }
        )

    n_ev = len(scenario.evs)
    n_success = sum(r["success"] for r in records)
    energy_req_total = sum(r["energy_req_kwh"] for r in records)
    energy_del_total = sum(r["energy_delivered_kwh"] for r in records)

    # 约束校验（含数值容差）
    outside_violation = 0.0
    for i, ev in enumerate(scenario.evs):
        window = set(ev.window_steps)
        outside = [t for t in range(scenario.T) if t not in window]
        if outside and power_kw[i, outside].size:
            outside_violation = max(outside_violation, float(power_kw[i, outside].max()))
    pmax_violation = max(
        (float(power_kw[i].max() - ev.pmax_kw) for i, ev in enumerate(scenario.evs)),
        default=0.0,
    )
    checks = {
        "transformer_max_total_kw": round(float(total.max()), 6),
        "transformer_limit_kw": float(scenario.transformer_limit_kw),
        "transformer_violation_kw": round(max(0.0, float(total.max() - scenario.transformer_limit_kw)), 6),
        "pmax_violation_kw": round(max(0.0, pmax_violation), 6),
        "outside_window_violation_kw": round(outside_violation, 6),
        "soc_shortfall_kwh": round(float(sum(max(0.0, r["energy_req_kwh"] - r["energy_delivered_kwh"]) for r in records)), 6),
    }

    peak_idx = int(np.argmax(total))
    base_peak_idx = int(np.argmax(base))
    return {
        "records": records,
        "ev_load_kw": ev_load,
        "total_load_kw": total,
        "metrics": {
            "base_peak_kw": round(float(base.max()), 6),
            "base_peak_time": scenario.hour_label(base_peak_idx),
            "ev_peak_kw": round(float(ev_load.max()), 6),
            "total_peak_kw": round(float(total.max()), 6),
            "peak_step": peak_idx,
            "peak_time": scenario.hour_label(peak_idx),
            "transformer_limit_kw": float(scenario.transformer_limit_kw),
            "peak_headroom_kw": round(float(scenario.transformer_limit_kw - total.max()), 6),
            "success_rate": round(n_success / n_ev, 6) if n_ev else 1.0,
            "n_ev": n_ev,
            "n_ev_success": int(n_success),
            "n_ev_failed": int(n_ev - n_success),
            "energy_success_rate": round(energy_del_total / energy_req_total, 6) if energy_req_total else 1.0,
            "energy_req_kwh": round(energy_req_total, 6),
            "energy_delivered_kwh": round(energy_del_total, 6),
            "energy_unmet_kwh": round(max(0.0, energy_req_total - energy_del_total), 6),
        },
        "checks": checks,
    }


# --------------------------------------------------------------------------- #
# 结果落盘
# --------------------------------------------------------------------------- #
def save_results(
    scenario: Scenario,
    power_kw: np.ndarray,
    unmet_kwh: dict[str, float],
    solve_info: dict,
    out_dir: Path,
    method: str,
    scenario_path: Path,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    ev = evaluate(scenario, power_kw, unmet_kwh)

    times = np.array([scenario.clock_hour(t) for t in range(scenario.T)])
    header = "t,time_h," + ",".join(scenario.ev_ids)
    rows = np.column_stack([np.arange(scenario.T), times, power_kw.T])
    np.savetxt(out_dir / "charging_power.csv", rows, delimiter=",", header=header, comments="", fmt="%.6f")
    np.save(out_dir / "charging_power.npy", power_kw)

    with (out_dir / "load_profile.csv").open("w", encoding="utf-8") as f:
        f.write("t,time_h,base_load_kw,ev_load_kw,total_load_kw,transformer_limit_kw\n")
        for t in range(scenario.T):
            f.write(
                f"{t},{scenario.clock_hour(t):.4f},{scenario.base_load_kw[t]:.6f},"
                f"{ev['ev_load_kw'][t]:.6f},{ev['total_load_kw'][t]:.6f},"
                f"{scenario.transformer_limit_kw:.6f}\n"
            )

    rec_fields = list(ev["records"][0].keys()) if ev["records"] else ["ev_id"]
    with (out_dir / "ev_records.csv").open("w", encoding="utf-8") as f:
        f.write(",".join(rec_fields) + "\n")
        for r in ev["records"]:
            f.write(",".join(str(r[k]) for k in rec_fields) + "\n")

    scenario_sha1 = hashlib.sha1(scenario_path.read_bytes()).hexdigest() if scenario_path.exists() else None
    stage1, stage2 = solve_info["stage1"], solve_info["stage2"]
    summary = {
        "method": method,
        "problem": "静态最优有序充电（全信息，最小化负荷峰值）",
        "solver": solve_info["solver_name"],
        "stage1_status": str(stage1.status).split(".")[-1],
        "stage2_status": None if stage2 is None else str(stage2.status).split(".")[-1],
        "tie_break_valley_filling": bool(solve_info["tie_break"]),
        "solve_time_s": round(float(stage1.time + (stage2.time if stage2 else 0.0)), 4),
        "num_variables": int(stage1.num_variables),
        "num_constraints": int(stage1.num_constraints),
        "scenario": {
            "name": scenario.name,
            "seed": scenario.seed,
            "file": str(scenario_path),
            "sha1": scenario_sha1,
            "T": scenario.T,
            "dt_h": scenario.dt_h,
            "start_hour": scenario.start_hour,
            "n_ev": scenario.n_ev,
        },
        **ev["metrics"],
        "constraint_checks": ev["checks"],
        "all_constraints_satisfied": bool(
            ev["checks"]["transformer_violation_kw"] <= POWER_TOL_KW
            and ev["checks"]["pmax_violation_kw"] <= POWER_TOL_KW
            and ev["checks"]["outside_window_violation_kw"] <= POWER_TOL_KW
            and ev["checks"]["soc_shortfall_kwh"] <= SOC_TOL_KWH
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def print_report(scenario: Scenario, summary: dict) -> None:
    m, c = summary, summary["constraint_checks"]
    print(f"\n=== 静态规划结果（{summary['method']}，求解器 {summary['solver']}） ===")
    print(f"场景：{scenario.name}  T={scenario.T} 步 × {scenario.dt_h} h，车辆 {m['n_ev']} 辆")
    print(f"变压器上限            : {m['transformer_limit_kw']:.1f} kW")
    print(f"基础负荷峰值          : {m['base_peak_kw']:.2f} kW  (出现在 {m['base_peak_time']})")
    print(f"EV 负荷峰值           : {m['ev_peak_kw']:.2f} kW")
    print(f"总负荷峰值（目标值）  : {m['total_peak_kw']:.2f} kW  (出现在 {m['peak_time']})")
    print(f"峰值余量              : {m['peak_headroom_kw']:.2f} kW")
    print(f"充电成功率            : {m['success_rate'] * 100:.1f}%  ({m['n_ev_success']}/{m['n_ev']} 辆充到目标 SOC)")
    print(f"电量完成度            : {m['energy_delivered_kwh']:.1f} / {m['energy_req_kwh']:.1f} kWh")
    print("约束校验：")
    print(f"  [{'OK' if c['transformer_violation_kw'] <= POWER_TOL_KW else 'NG'}] 变压器：最大总负荷 {c['transformer_max_total_kw']:.3f} kW "
          f"vs 上限 {c['transformer_limit_kw']:.1f} kW（越限 {c['transformer_violation_kw']:.3f} kW）")
    print(f"  [{'OK' if c['soc_shortfall_kwh'] <= SOC_TOL_KWH else 'NG'}] 目标 SOC：短缺 {c['soc_shortfall_kwh']:.6f} kWh（容差 {SOC_TOL_KWH}）")
    print(f"  [{'OK' if c['pmax_violation_kw'] <= POWER_TOL_KW else 'NG'}] 单车 Pmax：越限 {c['pmax_violation_kw']:.6f} kW")
    print(f"  [{'OK' if c['outside_window_violation_kw'] <= POWER_TOL_KW else 'NG'}] 场站外充电：{c['outside_window_violation_kw']:.6f} kW")
    print(f"求解耗时              : {m['solve_time_s']:.2f} s，变量 {m['num_variables']}，约束 {m['num_constraints']}")


# --------------------------------------------------------------------------- #
# 命令行入口
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description="电动汽车有序充电静态规划（PuLP MILP，最小化负荷峰值）")
    ap.add_argument("--scenario", default=str(ROOT / "scenario.json"), help="共享场景文件（不存在则按下面参数生成）")
    ap.add_argument("--regenerate", action="store_true", help="忽略已有场景文件，重新生成")
    ap.add_argument("--seed", type=int, default=0, help="场景随机种子")
    ap.add_argument("--n-ev", type=int, default=40, help="车辆数")
    ap.add_argument("--limit", type=float, default=380.0, help="变压器容量上限 kW")
    ap.add_argument("--out-root", default=str(ROOT / "results"), help="结果根目录")
    ap.add_argument("--method", default="static", help="结果子目录名（对比时作为方法名）")
    ap.add_argument("--solver", default="auto", choices=["auto", "highs", "gurobi"], help="求解器")
    ap.add_argument("--no-tie-break", action="store_true", help="关闭第二阶段低谷填充（只保留最小峰值目标）")
    ap.add_argument("--m-penalty", type=float, default=1e3, help="未满足电量的惩罚系数")
    args = ap.parse_args()

    scenario_path = Path(args.scenario)
    scenario = load_or_create_scenario(
        scenario_path,
        regenerate=args.regenerate,
        seed=args.seed,
        n_ev=args.n_ev,
        transformer_limit_kw=args.limit,
    )
    problems = scenario.validate()
    if problems:
        raise SystemExit("场景校验未通过：\n  " + "\n  ".join(problems))

    solver = build_solver(args.solver)
    t0 = time.perf_counter()
    solve_info = solve_static(
        scenario, solver=solver, tie_break=not args.no_tie_break, m_penalty=args.m_penalty
    )
    wall = time.perf_counter() - t0

    out_dir = Path(args.out_root) / args.method
    summary = save_results(
        scenario,
        solve_info["power_kw"],
        solve_info["unmet_kwh"],
        solve_info,
        out_dir,
        args.method,
        scenario_path,
    )
    summary["wall_time_s"] = round(wall, 4)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print_report(scenario, summary)
    print(f"结果已保存到：{out_dir}")


if __name__ == "__main__":
    main()
