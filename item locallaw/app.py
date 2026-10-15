# -*- coding: utf-8 -*-
"""电动汽车充电调度可视化演示看板（DQN / FCFS / PuLP）。

运行：
    streamlit run app.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from ev_charge_engine import (
    DT_H,
    N_PILES,
    PILE_COLORS,
    START_HOUR,
    T,
    METHOD_COLORS,
    build_scenario,
    run_all,
)

# --------------------------------------------------------------------------- #
# 页面基础设置
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="电动汽车充电调度可视化看板",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        /* 整体更紧凑、投影更克制，适配比赛现场投屏 */
        .block-container {padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1400px;}
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e6e9ef;
            border-radius: 12px;
            padding: 14px 18px;
            box-shadow: 0 1px 3px rgba(20, 30, 60, 0.05);
        }
        [data-testid="stMetricValue"] {font-size: 2.0rem; font-weight: 700;}
        [data-testid="stMetricLabel"] {font-size: 0.95rem; color: #5b6472;}
        #MainMenu, footer, header {visibility: hidden;}
        section[data-testid="stSidebar"] {background: #f7f9fc;}
    </style>
    """,
    unsafe_allow_html=True,
)

METHODS = ["DQN", "FCFS", "PuLP"]
METHOD_ITEMS = {"DQN": "🧠 DQN 强化学习", "FCFS": "🚗 FCFS 先来先充", "PuLP": "📐 PuLP 线性规划"}
METHOD_TAGLINES = {
    "DQN": "深度强化学习智能体 · 三档离散功率 · 移峰填谷、安全保底",
    "FCFS": "朴素基准 · 到站即满功率充电 · 不感知变压器容量与电价",
    "PuLP": "全信息线性规划 · HiGHS 求解 · 峰值最小（理论最优基准）",
}

START_TS = pd.Timestamp("2026-10-15 08:00")
STEP_TS = pd.date_range(START_TS, periods=T, freq="15min")
STEP_TS_SOC = pd.date_range(START_TS, periods=T + 1, freq="15min")


def hex_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# --------------------------------------------------------------------------- #
# 缓存：同一场景下三种算法只跑一次，切换算法零延迟
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def compute(n_ev: int, limit: float, seed: int):
    scenario = build_scenario(n_ev=n_ev, transformer_limit_kw=limit, seed=seed)
    results = run_all(scenario)
    return scenario, results


# --------------------------------------------------------------------------- #
# 侧边栏控制区
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("## ⚙️ 调度设置")
    method = st.radio(
        "选择调度算法",
        METHODS,
        format_func=lambda m: METHOD_ITEMS[m],
        label_visibility="collapsed",
    )
    st.divider()
    n_ev = st.slider("到站车辆数（辆）", min_value=6, max_value=14, value=10, step=1)
    limit = st.slider("变压器容量（kW）", min_value=30.0, max_value=60.0, value=40.0, step=5.0)

    if "seed" not in st.session_state:
        st.session_state.seed = 42
    col_a, col_b = st.columns([1, 1])
    with col_a:
        seed = st.number_input("随机种子", min_value=0, max_value=9999,
                               value=st.session_state.seed, step=1, label_visibility="visible")
        st.session_state.seed = int(seed)
    with col_b:
        st.write("")
        if st.button("🎲 换一批", width="stretch"):
            st.session_state.seed = int(np.random.randint(0, 9999))
            st.rerun()

    st.divider()
    with st.expander("ℹ️ 场景与算法说明"):
        st.markdown(
            "- **场景**：5 个充电桩（单桩 ≤11 kW），08:00 起 24 小时、15 分钟一步；"
            "车辆 09:00–20:00 随机到站，停留 1.5–4 小时。\n"
            "- **电价**：峰 1.05 元（10–15、18–21 时）／平 0.72 元／谷 0.35 元（23–7 时）。\n"
            "- **DQN**：内置部署版策略网络推理（numpy，无需 torch），"
            "状态含电价、裕度、截止紧迫度，输出 {0, 0.5, 1} 档功率，EMS 安全底线兜底。\n"
            "- **PuLP**：MILP/LP 全信息优化，最小化峰值并以电费做同峰 tie-break。\n"
            "- **FCFS**：不做任何优化的运营基准。"
        )

scenario, results = compute(n_ev, limit, st.session_state.seed)
cur = results[method]
fcfs = results["FCFS"]

# --------------------------------------------------------------------------- #
# 标题
# --------------------------------------------------------------------------- #
st.markdown(
    f"""
    <h1 style="margin-bottom:0.2rem;">⚡ 电动汽车充电调度可视化演示看板</h1>
    <p style="color:#5b6472; margin-bottom:0.4rem;">
        当前算法：<b style="color:{METHOD_COLORS[method]};">{method}</b>
        <span style="margin-left:10px;">{METHOD_TAGLINES[method]}</span>
    </p>
    <p style="color:#8a92a0; font-size:0.85rem; margin-bottom:0.8rem;">
        场景：{scenario.n_ev} 辆车 / {N_PILES} 个充电桩 / 变压器 {scenario.transformer_limit_kw:.0f} kW /
        时间轴 {int(START_HOUR):02d}:00 起 {T} 步 × {DT_H * 60:.0f} 分钟 / 随机种子 {scenario.seed}
    </p>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# 指标卡片
# --------------------------------------------------------------------------- #
c1, c2, c3 = st.columns(3)
if method != "FCFS":
    peak_delta = f"{cur['peak_kw'] - fcfs['peak_kw']:+.1f} kW vs FCFS"
    rate_delta = f"{(cur['success_rate'] - fcfs['success_rate']) * 100:+.1f} pct vs FCFS"
    cost_delta = f"{cur['total_cost'] - fcfs['total_cost']:+.1f} 元 vs FCFS"
else:
    peak_delta = None
    rate_delta = None
    cost_delta = None

viol_note = ""
if cur["violation_kw"] > 1e-6:
    viol_note = f"<span style='color:#E74C3C; font-size:0.82rem;'>⚠ 超变压器容量 {cur['violation_kw']:.1f} kW</span>"

c1.metric("峰值负荷", f"{cur['peak_kw']:.1f} kW", peak_delta, delta_color="inverse")
c1.markdown(viol_note, unsafe_allow_html=True)
c2.metric(
    "充电完成率",
    f"{cur['success_rate'] * 100:.1f}%",
    rate_delta,
    delta_color="normal",
    help=f"离场时 SOC 达标车辆：{cur['n_success']}/{cur['n_ev']}",
)
c2.caption(f"达标车辆 {cur['n_success']} / {cur['n_ev']} 辆")
c3.metric("总电费", f"{cur['total_cost']:.1f} 元", cost_delta, delta_color="inverse")
c3.caption(f"EV 总充电量 {cur['energy_kwh']:.1f} kWh")

# --------------------------------------------------------------------------- #
# 图 1：时序负荷曲线
# --------------------------------------------------------------------------- #
st.markdown("#### 📈 系统时序负荷曲线")
color = METHOD_COLORS[method]
fig_load = go.Figure()

# 峰电价时段浅红底纹
for day in (START_TS.normalize(), START_TS.normalize() + pd.Timedelta(days=1)):
    for h0, h1 in ((10, 15), (18, 21)):
        fig_load.add_vrect(
            x0=day + pd.Timedelta(hours=h0), x1=day + pd.Timedelta(hours=h1),
            fillcolor="#E74C3C", opacity=0.05, line_width=0,
        )

fig_load.add_trace(go.Scatter(
    x=STEP_TS, y=scenario.base_load_kw, name="基础负荷（无 EV）",
    line=dict(color="#9AA3AF", width=1.8, dash="dash"), hovertemplate="%{x|%H:%M} %{y:.1f} kW<extra></extra>",
))
fig_load.add_trace(go.Scatter(
    x=STEP_TS, y=cur["ev_load_kw"], name="EV 充电负荷",
    mode="lines", line=dict(color="rgba(0,0,0,0)", width=0),
    fill="tozeroy", fillcolor=hex_rgba(color, 0.22),
    hovertemplate="%{x|%H:%M} %{y:.1f} kW<extra></extra>",
))
fig_load.add_trace(go.Scatter(
    x=STEP_TS, y=cur["total_load_kw"], name="系统总负荷",
    line=dict(color=color, width=3.0),
    hovertemplate="%{x|%H:%M} 总 %{y:.1f} kW<extra></extra>",
))
fig_load.add_hline(
    y=scenario.transformer_limit_kw,
    line=dict(color="#E74C3C", width=1.6, dash="dot"),
    annotation_text=f"变压器上限 {scenario.transformer_limit_kw:.0f} kW",
    annotation_position="top right", annotation_font_color="#E74C3C",
)
# 峰值点标注
peak_t = STEP_TS[cur["peak_step"]]
fig_load.add_trace(go.Scatter(
    x=[peak_t], y=[cur["peak_kw"]], mode="markers+text",
    marker=dict(color=color, size=11, line=dict(color="white", width=2)),
    text=[f"峰值 {cur['peak_kw']:.1f}"], textposition="top center",
    textfont=dict(size=12, color=color), name="峰值点", showlegend=False,
))
fig_load.update_layout(
    height=400, margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="white", hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    yaxis=dict(title="功率 (kW)", rangemode="tozero",
               range=[0, max(fcfs["peak_kw"], scenario.transformer_limit_kw) * 1.18],
               gridcolor="#EEF1F5", zerolinecolor="#EEF1F5"),
    xaxis=dict(tickformat="%H:%M", dtick=2 * 60 * 60 * 1000, gridcolor="#F4F6F9"),
)
st.plotly_chart(fig_load, width="stretch", config={"displayModeBar": False})

# --------------------------------------------------------------------------- #
# 图 2：各桩 SOC 变化
# --------------------------------------------------------------------------- #
st.markdown("#### 🔋 各充电桩在网车辆 SOC 变化")
fig_soc = go.Figure()
for j in range(N_PILES):
    fig_soc.add_trace(go.Scatter(
        x=STEP_TS_SOC, y=cur["pile_soc"][j], name=f"{j + 1} 号桩",
        mode="lines+markers", line=dict(color=PILE_COLORS[j], width=2.2),
        marker=dict(size=4), connectgaps=False,
        hovertemplate=f"{j + 1} 号桩 %{{x|%H:%M}} SOC %{{y:.0%}}<extra></extra>",
    ))
# 每段会话的目标 SOC（离场时刻星标）
for j in range(N_PILES):
    xs, ys = [], []
    for ev in scenario.evs:
        if ev.pile == j:
            xs.append(STEP_TS_SOC[ev.departure_step])
            ys.append(ev.soc_target)
    fig_soc.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers", marker=dict(symbol="star", size=11, color=PILE_COLORS[j],
                                                line=dict(color="white", width=1)),
        name=f"{j + 1} 号桩目标", showlegend=False, hovertemplate="目标 SOC %{y:.0%}<extra></extra>",
    ))
fig_soc.update_layout(
    height=380, margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="white", hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    yaxis=dict(title="SOC", tickformat=".0%", range=[0, 1.06],
               gridcolor="#EEF1F5", zerolinecolor="#EEF1F5"),
    xaxis=dict(tickformat="%H:%M", dtick=2 * 60 * 60 * 1000, gridcolor="#F4F6F9"),
)
st.plotly_chart(fig_soc, width="stretch", config={"displayModeBar": False})
st.caption("实线为在网车辆 SOC（换车自动断线），⭐ 为该车离场时的目标 SOC。")

# --------------------------------------------------------------------------- #
# 展开区：三算法对比 + 车辆明细
# --------------------------------------------------------------------------- #
with st.expander("📊 三算法横向对比（同一场景）"):
    rows = []
    for m in METHODS:
        r = results[m]
        rows.append({
            "算法": METHOD_ITEMS[m],
            "峰值负荷 (kW)": round(r["peak_kw"], 1),
            "EV 峰值 (kW)": round(r["ev_peak_kw"], 1),
            "充电完成率": f"{r['success_rate'] * 100:.1f}%",
            "总电费 (元)": round(r["total_cost"], 1),
            "越限 (kW)": round(r["violation_kw"], 1),
            "求解耗时 (ms)": round(r["solve_time_s"] * 1000, 1),
            "求解后端": r["backend"],
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    fig_cmp = make_subplots(rows=1, cols=2, subplot_titles=("峰值负荷 (kW)", "总电费 (元)"))
    for m in METHODS:
        r = results[m]
        fig_cmp.add_trace(go.Bar(
            x=[m], y=[r["peak_kw"]], marker_color=METHOD_COLORS[m],
            text=[f"{r['peak_kw']:.1f}"], textposition="outside", showlegend=False,
        ), row=1, col=1)
        fig_cmp.add_trace(go.Bar(
            x=[m], y=[r["total_cost"]], marker_color=METHOD_COLORS[m],
            text=[f"{r['total_cost']:.0f}"], textposition="outside", showlegend=False,
        ), row=1, col=2)
    fig_cmp.add_hline(y=scenario.transformer_limit_kw, line_dash="dot",
                      line_color="#E74C3C", row=1, col=1)
    fig_cmp.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10),
                          plot_bgcolor="white")
    fig_cmp.update_yaxes(rangemode="tozero", gridcolor="#EEF1F5")
    st.plotly_chart(fig_cmp, width="stretch", config={"displayModeBar": False})

with st.expander(f"🚙 车辆充电明细（{method}）"):
    detail = []
    for i, ev in enumerate(scenario.evs):
        detail.append({
            "车辆": ev.ev_id,
            "充电桩": f"{ev.pile + 1} 号",
            "到站": scenario.hour_label(ev.arrival_step),
            "离开": scenario.hour_label(ev.departure_step),
            "电池 (kWh)": ev.battery_kwh,
            "初始 SOC": f"{ev.soc_init:.0%}",
            "目标 SOC": f"{ev.soc_target:.0%}",
            "终止 SOC": f"{cur['soc_end'][i]:.1%}",
            "实充电量 (kWh)": round(cur["power_kw"][i].sum() * DT_H, 2),
            "电费 (元)": round(cur["cost_per_ev"][i], 2),
            "状态": "✅ 达标" if cur["success"][i] else "⚠ 未达标",
        })
    st.dataframe(pd.DataFrame(detail), hide_index=True, width="stretch")
