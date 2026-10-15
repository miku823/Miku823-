"""把各方法（static / dqn / fcfs ...）的结果放到同一张图上对比。

约定：每个方法的结果目录为 results/<method>/，其中至少包含
    summary.json      峰值、充电成功率等汇总指标
    load_profile.csv  t,time_h,base_load_kw,ev_load_kw,total_load_kw,transformer_limit_kw
（static_plan.py 已按此格式输出；DQN / FCFS 只需按同样列名落盘即可自动纳入对比。）

用法：
    python plot_compare.py                      # 自动扫描 results/ 下所有方法
    python plot_compare.py --methods static fcfs dqn
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parent
METHOD_LABELS = {
    "static": "静态最优（全信息 MILP）",
    "dqn": "DQN",
    "fcfs": "FCFS（即到即充）",
}


def discover_methods(results_root: Path) -> list[str]:
    if not results_root.exists():
        return []
    return sorted(p.name for p in results_root.iterdir() if (p / "load_profile.csv").exists())


def load_method(results_root: Path, method: str) -> dict | None:
    d = results_root / method
    profile_path, summary_path = d / "load_profile.csv", d / "summary.json"
    if not profile_path.exists():
        print(f"[跳过] {method}：缺少 {profile_path}")
        return None
    df = pd.read_csv(profile_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    total = df["total_load_kw"].to_numpy()
    return {
        "method": method,
        "label": summary.get("method_label") or METHOD_LABELS.get(method, method.upper()),
        "t": df["t"].to_numpy(),
        "time_h": df["time_h"].to_numpy(),
        "base": df["base_load_kw"].to_numpy(),
        "ev": df["ev_load_kw"].to_numpy(),
        "total": total,
        "limit": float(df["transformer_limit_kw"].iloc[0]),
        "peak_kw": float(summary.get("total_peak_kw", np.nan)),
        "ev_peak_kw": float(summary.get("ev_peak_kw", np.nan)),
        "success_rate": float(summary.get("success_rate", np.nan)),
        "violation_kw": float(summary.get("constraint_checks", {}).get("transformer_violation_kw", 0.0)),
        "all_constraints_satisfied": bool(summary.get("all_constraints_satisfied", True)),
        "solve_time_s": summary.get("solve_time_s", np.nan),
    }


def print_table(rows: list[dict]) -> pd.DataFrame:
    table = pd.DataFrame(
        [
            {
                "method": r["method"],
                "峰值(kW)": round(r["peak_kw"], 3),
                "EV峰值(kW)": round(r["ev_peak_kw"], 3),
                "基础峰值(kW)": round(float(r["base"].max()), 3),
                "充电成功率": f"{r['success_rate'] * 100:.1f}%",
                "变压器越限(kW)": round(r["violation_kw"], 3),
                "约束满足": r["all_constraints_satisfied"],
                "求解耗时(s)": r["solve_time_s"],
            }
            for r in rows
        ]
    )
    print("\n=== 各方法指标对比 ===")
    print(table.to_string(index=False))
    return table


def plot(rows: list[dict], out_path: Path, dpi: int = 150) -> None:
    ref = rows[0]
    dt_h = float(ref["time_h"][1] - ref["time_h"][0]) if len(ref["time_h"]) > 1 else 0.25
    hours = ref["t"] * dt_h  # 相对场景起点的小时数

    def hour_labels() -> tuple[list[float], list[str]]:
        ticks = list(np.arange(0, hours[-1] + 1e-9, 4.0))
        labels = [f"{int(h) % 24:02d}:00" for h in (ref["time_h"][0] + np.array(ticks)) % 24]
        return ticks, labels

    fig, axes = plt.subplots(3, 1, figsize=(12, 11), gridspec_kw={"height_ratios": [2.2, 1.6, 1.2]})

    # (1) 总负荷曲线
    ax = axes[0]
    ax.plot(hours, ref["base"], color="#9e9e9e", ls="--", lw=1.6, label="基础负荷（无 EV）")
    for r in rows:
        ax.plot(hours, r["total"], lw=2.0, marker="o", ms=2.5, label=f"{r['label']}（峰值 {r['peak_kw']:.1f} kW）")
    ax.axhline(ref["limit"], color="#d62728", lw=1.4, ls=":", label=f"变压器上限 {ref['limit']:.0f} kW")
    ax.set_title("系统总负荷曲线对比")
    ax.set_ylabel("功率 (kW)")
    ax.legend(loc="upper left", fontsize=9, ncol=2)
    ax.grid(alpha=0.3)

    # (2) EV 聚合充电负荷
    ax = axes[1]
    for r in rows:
        ax.plot(hours, r["ev"], lw=1.8, marker="o", ms=2.5, label=r["label"])
    ax.set_title("EV 聚合充电负荷对比")
    ax.set_ylabel("功率 (kW)")
    ax.legend(loc="upper left", fontsize=9, ncol=2)
    ax.grid(alpha=0.3)

    # (3) 峰值与成功率
    ax = axes[2]
    labels = [r["label"] for r in rows]
    x = np.arange(len(rows))
    ax.bar(x - 0.2, [r["peak_kw"] for r in rows], 0.4, color="#1f77b4", label="总负荷峰值 (kW)")
    ax2 = ax.twinx()
    ax2.bar(x + 0.2, [r["success_rate"] * 100 for r in rows], 0.4, color="#2ca02c", label="充电成功率 (%)")
    ax.axhline(ref["limit"], color="#d62728", lw=1.4, ls=":")
    ax.set_xticks(x, labels, fontsize=9)
    ax.set_ylabel("峰值 (kW)")
    ax2.set_ylabel("充电成功率 (%)")
    ax2.set_ylim(0, 115)
    for xi, r in zip(x, rows):
        ax.text(xi - 0.2, r["peak_kw"], f"{r['peak_kw']:.1f}", ha="center", va="bottom", fontsize=8)
        ax2.text(xi + 0.2, r["success_rate"] * 100, f"{r['success_rate'] * 100:.0f}%", ha="center", va="bottom", fontsize=8)
    ax.set_title("峰值与充电成功率对比")
    ax.grid(alpha=0.3, axis="y")

    ticks, tick_labels = hour_labels()
    for ax_ in axes[:2]:
        ax_.set_xticks(ticks, tick_labels)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    print(f"\n对比图已保存：{out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="各充电方法（static/DQN/FCFS）结果对比绘图")
    ap.add_argument("--results-root", default=str(ROOT / "results"))
    ap.add_argument("--methods", nargs="*", default=None, help="指定方法子目录，默认自动扫描")
    ap.add_argument("--out", default=None, help="输出图片路径，默认 <results-root>/comparison.png")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    results_root = Path(args.results_root)
    methods = args.methods or discover_methods(results_root)
    if not methods:
        raise SystemExit(f"{results_root} 下没有找到任何方法的结果（需含 load_profile.csv）")

    # static 作为基准排在最前，其余按名称排序
    methods = sorted(methods, key=lambda m: (m != "static", m))
    rows = [r for r in (load_method(results_root, m) for m in methods) if r is not None]
    if not rows:
        raise SystemExit("没有可用的结果数据")

    table = print_table(rows)
    out_path = Path(args.out) if args.out else results_root / "comparison.png"
    csv_path = out_path.with_name(out_path.stem + "_metrics.csv")
    table.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"指标表已保存：{csv_path}")
    plot(rows, out_path, dpi=args.dpi)


if __name__ == "__main__":
    main()
