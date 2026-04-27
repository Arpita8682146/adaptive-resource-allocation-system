import math

import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from adaptive_logic import apply_adaptive_logic
from monitor import get_data
from predictor import detect_anomaly, predict_future
from utils import (
    boost_process,
    build_process_dataframe,
    compute_health,
    ensure_session_state,
    is_pid_active,
    kill_process,
    load_users,
    resume_process,
    start_stress_test,
    stop_stress_test,
    suspend_process,
)

# -----------------------------
# CONFIG & STYLES
# -----------------------------
st.set_page_config(page_title="🚀 Resource Dashboard Pro", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0a0e1a 100%); }
.metric-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 28px; backdrop-filter: blur(24px);
    position: relative; overflow: hidden; transition: transform 0.3s, box-shadow 0.3s;
}
.metric-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.3); }
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}
.metric-value { font-size: 2.4rem; font-weight: 800; margin: 8px 0 4px; letter-spacing: -0.02em; }
.metric-label { font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.metric-icon { font-size: 1.6rem; opacity: 0.9; }
.glass-card {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px; padding: 28px; backdrop-filter: blur(24px); margin-bottom: 16px;
    position: relative;
}
.glass-card::before {
    content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 60%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
}
.alert-bar {
    padding: 16px 22px; border-radius: 14px; font-size: 0.9rem; font-weight: 500;
    border-left: 4px solid; margin-bottom: 10px; backdrop-filter: blur(12px);
}
.alert-danger { background: rgba(239,68,68,0.08); border-color: #ef4444; color: #fca5a5; }
.alert-warning { background: rgba(245,158,11,0.08); border-color: #f59e0b; color: #fcd34d; }
.alert-success { background: rgba(34,197,94,0.08); border-color: #22c55e; color: #86efac; }
.alert-info { background: rgba(56,189,248,0.08); border-color: #38bdf8; color: #7dd3fc; }
.live-dot {
    width: 8px; height: 8px; background: #22c55e; border-radius: 50%;
    display: inline-block; animation: pulse 2s infinite; margin-right: 6px;
    box-shadow: 0 0 12px rgba(34,197,94,0.6);
}
@keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.85); } }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.login-icon { animation: float 3s ease-in-out infinite; font-size: 3rem; }
.header-title { font-size: 1.6rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.01em; }
.header-live {
    display: inline-flex; align-items: center; gap: 6px; font-size: 0.78rem;
    color: #22c55e; font-weight: 600; background: rgba(34,197,94,0.1);
    padding: 4px 14px; border-radius: 100px;
}
.section-title { font-size: 0.8rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 16px; }
.rec-card {
    border-radius: 12px; padding: 14px 18px; margin-bottom: 10px; border-left: 4px solid;
}
.rec-danger { background: rgba(239,68,68,0.08); border-color: #ef4444; }
.rec-warning { background: rgba(245,158,11,0.08); border-color: #f59e0b; }
.rec-success { background: rgba(34,197,94,0.08); border-color: #22c55e; }
.rec-info { background: rgba(56,189,248,0.08); border-color: #38bdf8; }
.rec-title { font-size: 0.9rem; font-weight: 700; color: #f1f5f9; margin-bottom: 4px; }
.rec-desc { font-size: 0.78rem; color: #94a3b8; line-height: 1.5; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
header[data-testid="stHeader"] { background: transparent; }

section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(24px);
}
section[data-testid="stSidebar"] .stMarkdown { color: #e2e8f0; }

.stButton > button {
    border-radius: 14px !important; font-weight: 600 !important;
    transition: all 0.3s !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(0,0,0,0.3) !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
}

.stTextInput > div > div > input, .stNumberInput > div > div > input {
    border-radius: 14px !important; background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important; color: #e2e8f0 !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

.stDataFrame { border-radius: 16px; overflow: hidden; }
</style>
""",
    unsafe_allow_html=True,
)


def render_metric(col, icon, label, value, color):
    glow = f"radial-gradient(circle at top right, {color}15, transparent 70%)"
    col.markdown(
        f"""
        <div class="metric-card" style="background: {glow}, rgba(255,255,255,0.03);">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color: {color};">{value}</div>
            <div class="metric-icon">{icon}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def notify(result):
    success, message = result
    if success:
        st.success(f"✅ {message}")
    else:
        st.error(f"❌ {message}")


@st.cache_data(ttl=2, show_spinner=False)
def get_process_snapshot():
    return build_process_dataframe()


def run_process_action(action, pid):
    pid = int(pid or 0)
    if pid <= 0:
        st.warning("⚠️ Enter a valid PID")
        return

    if action == "stop":
        result = suspend_process(pid)
        if result[0]:
            st.session_state["stopped_pids"].add(pid)
    elif action == "start":
        result = resume_process(pid)
        if result[0]:
            st.session_state["stopped_pids"].discard(pid)
    elif action == "boost":
        result = boost_process(pid)
        if result[0]:
            st.session_state["boosted_pids"].add(pid)
    elif action == "kill":
        result = kill_process(pid)
        if result[0]:
            st.session_state["killed_pids"].add(pid)
            st.session_state["stopped_pids"].discard(pid)
            st.session_state["boosted_pids"].discard(pid)
    else:
        result = (False, "Unsupported action")

    if result[0]:
        get_process_snapshot.clear()
    notify(result)


ensure_session_state(st.session_state)

if st.session_state["stress_pid"] and not is_pid_active(st.session_state["stress_pid"]):
    st.session_state["stress_pid"] = None

# -----------------------------
# AUTHENTICATION
# -----------------------------
if not st.session_state["logged_in"]:
    _, center_col, _ = st.columns([1.2, 1, 1.2])
    with center_col:
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
                border-radius: 20px; padding: 40px; backdrop-filter: blur(24px); text-align: center;">
                <div class="login-icon">⚡</div>
                <h2 style="color: #f1f5f9; margin: 10px 0 4px;">System Login</h2>
                <p style="color: #64748b; font-size: 0.85rem;">Resource Dashboard Pro</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login"):
            username = st.text_input("👤 Username").strip()
            password = st.text_input("🔒 Password", type="password").strip()
            submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
            if submitted:
                users = load_users()
                if username in users and str(users[username]) == str(password):
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = username
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")
        st.markdown(
            "<p style='text-align:center;color:#64748b;font-size:0.8rem;'>Default: admin / 1234</p>",
            unsafe_allow_html=True,
        )
    st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
            <span style="font-size: 1.8rem;">⚡</span>
            <div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #f1f5f9;">Dashboard Pro</div>
                <div style="font-size: 0.75rem; color: #64748b;">System Monitor v2.0</div>
            </div>
        </div>
        <hr style="border-color: rgba(255,255,255,0.06); margin: 16px 0;">
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### ⚙️ Settings")
    threshold = st.slider("CPU Alert Threshold", 50, 100, 80)
    auto_optimize = st.toggle("🔄 Auto Optimization", value=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["user"] = ""
        st.rerun()

# -----------------------------
# DATA COLLECTION
# -----------------------------
st_autorefresh(interval=3000, key="ref")
cpu, mem, cpu_history, mem_history = get_data(
    st.session_state["cpu_history"], st.session_state["mem_history"], history_size=60
)
st.session_state["cpu_history"] = cpu_history
st.session_state["mem_history"] = mem_history

raw_process_df = get_process_snapshot()
if not raw_process_df.empty and st.session_state["killed_pids"]:
    raw_process_df = raw_process_df[~raw_process_df["pid"].isin(st.session_state["killed_pids"])].reset_index(drop=True)

process_records = raw_process_df.to_dict("records") if not raw_process_df.empty else []
_, future_y = predict_future(cpu_history)
is_anomaly, _, _ = detect_anomaly(cpu_history)
health = compute_health(cpu, mem)
num_tasks = len(process_records)

adaptive_state = apply_adaptive_logic(
    cpu_usage=cpu,
    memory_usage=mem,
    processes=process_records,
    auto_optimize=auto_optimize,
    cpu_threshold=threshold,
    memory_threshold=85,
    anomaly_detected=is_anomaly,
)

auto_actions = adaptive_state["actions"]
priority_map = {process["pid"]: process["adaptive_priority"] for process in adaptive_state["aged_processes"]}

df_procs = raw_process_df.copy()
if df_procs.empty:
    df_procs["adaptive_priority"] = []
else:
    df_procs["adaptive_priority"] = df_procs["pid"].map(priority_map).fillna(0.0)
    df_procs["name"] = df_procs["name"].astype(str)
    boosted_mask = df_procs["pid"].isin(st.session_state["boosted_pids"])
    stopped_mask = df_procs["pid"].isin(st.session_state["stopped_pids"])
    df_procs.loc[boosted_mask, "name"] = df_procs.loc[boosted_mask, "name"] + " ⚡"
    df_procs.loc[stopped_mask, "status"] = "stopped"
    df_procs.loc[stopped_mask, "cpu_percent"] = 0.0

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    f"""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 12px;">
        <span class="header-title">🚀 Resource Dashboard</span>
        <span class="header-live"><span class="live-dot"></span> Live</span>
    </div>
    <span style="color: #64748b; font-size: 0.85rem;">📡 User: {st.session_state['user']}</span>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# METRIC CARDS
# -----------------------------
colors = {"cpu": "#2dd4bf", "mem": "#a78bfa", "health": "#22c55e", "tasks": "#38bdf8"}
m1, m2, m3, m4 = st.columns(4)

render_metric(m1, "⚡", "CPU Usage", f"{cpu}%", colors["cpu"])
render_metric(m2, "🧠", "Memory", f"{mem}%", colors["mem"])
render_metric(m3, "💚", "Health", f"{health}%", colors["health"])
render_metric(m4, "📋", "Tasks", str(num_tasks), colors["tasks"])

st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)

# -----------------------------
# ALERTS
# -----------------------------
a1, a2, a3 = st.columns(3)
with a1:
    if cpu > threshold:
        status_class, status_message = "alert-danger", "⚠️ High CPU Load Detected"
    elif cpu > threshold * 0.75:
        status_class, status_message = "alert-warning", "🔶 Moderate CPU Load"
    else:
        status_class, status_message = "alert-success", "✅ System Stable"
    st.markdown(
        f'<div class="alert-bar {status_class}"><strong>Status:</strong> {status_message}</div>',
        unsafe_allow_html=True,
    )
with a2:
    engine_class, engine_message = ("alert-danger", "🚨 Anomaly Detected") if is_anomaly else ("alert-info", "🔍 Normal Pattern")
    st.markdown(
        f'<div class="alert-bar {engine_class}"><strong>Smart Engine:</strong> {engine_message}</div>',
        unsafe_allow_html=True,
    )
with a3:
    prediction_message = f"📊 Next: {future_y[0]}%" if future_y else "⏳ Analyzing..."
    st.markdown(
        f'<div class="alert-bar alert-info"><strong>Prediction:</strong> {prediction_message}</div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)

if auto_actions:
    updated_actions = [action for action in auto_actions if action["status"] == "updated"]
    blocked_actions = [action for action in auto_actions if action["status"] == "blocked"]
    if updated_actions:
        pid_summary = ", ".join(str(action["pid"]) for action in updated_actions)
        st.markdown(
            f'<div class="alert-bar alert-info"><strong>Adaptive Actions:</strong> Reprioritized PIDs {pid_summary}</div>',
            unsafe_allow_html=True,
        )
    elif blocked_actions:
        st.markdown(
            '<div class="alert-bar alert-warning"><strong>Adaptive Actions:</strong> Auto optimization was limited by system permissions</div>',
            unsafe_allow_html=True,
        )

# -----------------------------
# CHARTS & HEALTH GAUGE
# -----------------------------
chart_col, gauge_col = st.columns([3, 1])

with chart_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Real-Time Performance</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=cpu_history,
            name="CPU %",
            line=dict(color="#2dd4bf", width=2.5, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(45,212,191,0.08)",
        )
    )
    fig.add_trace(
        go.Scatter(
            y=mem_history,
            name="MEM %",
            line=dict(color="#a78bfa", width=2.5, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(167,139,250,0.08)",
        )
    )
    fig.update_layout(
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#64748b", size=11),
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.12,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color="#94a3b8"),
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False, range=[0, 100]),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with gauge_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💚 System Health</div>', unsafe_allow_html=True)
    angle = (health / 100) * 180
    health_color = "#22c55e" if health >= 70 else "#f59e0b" if health >= 40 else "#ef4444"
    radius = math.radians(180 - angle)
    x_pos = 60 + 45 * math.cos(radius)
    y_pos = 60 - 45 * math.sin(radius)
    large_arc = 1 if angle > 180 else 0
    st.markdown(
        f"""
        <div style="text-align: center;">
            <svg viewBox="0 0 120 70" style="width: 180px; margin: 0 auto;">
                <path d="M 15 60 A 45 45 0 0 1 105 60" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8" stroke-linecap="round"/>
                <path d="M 15 60 A 45 45 0 {large_arc} 1 {x_pos:.1f} {y_pos:.1f}" fill="none" stroke="{health_color}" stroke-width="8" stroke-linecap="round" style="filter: drop-shadow(0 0 6px {health_color}80);"/>
            </svg>
            <div style="font-size: 2.5rem; font-weight: 800; color: {health_color}; margin-top: 8px;">{health}%</div>
            <div style="color: #64748b; font-size: 0.85rem;">Overall Score</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# RECOMMENDATIONS
# -----------------------------
st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">💡 Recommendations</div>', unsafe_allow_html=True)

recommendations = list(adaptive_state["recommendations"])
if health < 40:
    recommendations.append(
        {"icon": "🔴", "title": "System Health Critical", "description": "Overall health is poor. Immediate intervention recommended.", "severity": "danger"}
    )
elif health < 70:
    recommendations.append(
        {"icon": "🟠", "title": "Health Needs Attention", "description": "System health is below optimal. Review resource allocation.", "severity": "warning"}
    )

risk_levels = {rec["severity"] for rec in recommendations}
if not risk_levels.intersection({"danger", "warning"}):
    recommendations.append(
        {"icon": "💡", "title": "System Responsive", "description": "Adaptive controls and telemetry are running normally.", "severity": "info"}
    )

for rec in recommendations:
    st.markdown(
        f"""
        <div class="rec-card rec-{rec['severity']}">
            <div class="rec-title">{rec['icon']} {rec['title']}</div>
            <div class="rec-desc">{rec['description']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# STRESS TEST
# -----------------------------
st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔥 Stress Test Control</div>', unsafe_allow_html=True)

stress_running = is_pid_active(st.session_state["stress_pid"])
stress_cols = st.columns([1, 1, 2])

with stress_cols[0]:
    if st.button("🔥 Start Stress", use_container_width=True):
        if stress_running:
            st.warning(f"⚠️ Stress test already running on PID {st.session_state['stress_pid']}")
        else:
            try:
                st.session_state["stress_pid"] = start_stress_test()
                get_process_snapshot.clear()
                st.success(f"✅ Stress test started on PID {st.session_state['stress_pid']}")
            except Exception as exc:
                st.error(f"❌ Unable to start stress test: {exc}")

with stress_cols[1]:
    if st.button("🧹 Stop Stress", use_container_width=True):
        if not stress_running:
            st.warning("⚠️ No active stress test is running")
        else:
            result = stop_stress_test(st.session_state["stress_pid"])
            if result[0]:
                st.session_state["stress_pid"] = None
                get_process_snapshot.clear()
            notify(result)

stress_running = is_pid_active(st.session_state["stress_pid"])
with stress_cols[2]:
    status_class = "alert-danger" if stress_running else "alert-success"
    status_message = (
        f"Stress script active on PID {st.session_state['stress_pid']}" if stress_running else "Stress script is idle"
    )
    st.markdown(
        f'<div class="alert-bar {status_class}"><strong>Status:</strong> {status_message}</div>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# PROCESS MANAGER
# -----------------------------
st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 Process Manager</div>', unsafe_allow_html=True)

top_cols = st.columns([2, 1, 1, 1, 1])
with top_cols[0]:
    pid_input = st.number_input("Enter PID", min_value=0, step=1, key="pid_top", label_visibility="collapsed")
with top_cols[1]:
    if st.button("⏹️ Stop", use_container_width=True, key="stop_top"):
        run_process_action("stop", pid_input)
with top_cols[2]:
    if st.button("▶️ Start", use_container_width=True, key="start_top"):
        run_process_action("start", pid_input)
with top_cols[3]:
    if st.button("⚡ Boost", use_container_width=True, key="boost_top"):
        run_process_action("boost", pid_input)
with top_cols[4]:
    if st.button("💀 Kill", use_container_width=True, type="primary", key="kill_top"):
        run_process_action("kill", pid_input)

search = st.text_input("🔍 Filter processes...", placeholder="Type process name...", key="proc_search")
if search:
    df_procs = df_procs[df_procs["name"].str.contains(search, case=False, na=False)]

st.dataframe(
    df_procs.head(15),
    use_container_width=True,
    hide_index=True,
    column_config={
        "pid": st.column_config.NumberColumn("PID", width="small"),
        "name": st.column_config.TextColumn("Process Name", width="medium"),
        "cpu_percent": st.column_config.ProgressColumn("CPU %", min_value=0, max_value=100, format="%.1f%%"),
        "memory_percent": st.column_config.ProgressColumn("Memory %", min_value=0, max_value=100, format="%.2f%%"),
        "adaptive_priority": st.column_config.NumberColumn("Adaptive Score", format="%.1f"),
        "status": st.column_config.TextColumn("Status", width="small"),
    },
)

ctrl1, ctrl2 = st.columns(2)
with ctrl1:
    pid_kill = st.number_input("PID to Kill", min_value=0, step=1, key="k")
    if st.button("💀 Kill Process", type="primary", use_container_width=True):
        run_process_action("kill", pid_kill)
with ctrl2:
    pid_boost = st.number_input("PID to Boost", min_value=0, step=1, key="b")
    if st.button("⚡ Boost Priority", use_container_width=True):
        run_process_action("boost", pid_boost)

ctrl3, ctrl4 = st.columns(2)
with ctrl3:
    pid_stop = st.number_input("PID to Stop", min_value=0, step=1, key="s")
    if st.button("⏹️ Stop Process", use_container_width=True):
        run_process_action("stop", pid_stop)
with ctrl4:
    pid_start = st.number_input("PID to Start", min_value=0, step=1, key="st_pid")
    if st.button("▶️ Start Process", use_container_width=True):
        run_process_action("start", pid_start)

st.markdown("</div>", unsafe_allow_html=True)
