import streamlit as st
import psutil
import pandas as pd
import numpy as np
import json
import os
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

# -----------------------------
# CONFIG & STYLES
# -----------------------------
st.set_page_config(page_title="🚀 Resource Dashboard Pro", layout="wide")

st.markdown("""
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
""", unsafe_allow_html=True)

# -----------------------------
# AUTHENTICATION
# -----------------------------
def load_users():
    creds = {"admin": "1234", "user1": "pass1", "user2": "pass2"}
    try:
        curr_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(curr_path, "users.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    creds[str(k).strip()] = str(v).strip()
    except:
        pass
    return creds

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "cpu_history" not in st.session_state:
    st.session_state["cpu_history"] = []
if "mem_history" not in st.session_state:
    st.session_state["mem_history"] = []
if "boosted_pids" not in st.session_state:
    st.session_state["boosted_pids"] = set()
if "stopped_pids" not in st.session_state:
    st.session_state["stopped_pids"] = set()
if "killed_pids" not in st.session_state:
    st.session_state["killed_pids"] = set()

if not st.session_state["logged_in"]:
    st.markdown("", unsafe_allow_html=True)
    _, col_c, _ = st.columns([1.2, 1, 1.2])
    with col_c:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
            border-radius: 20px; padding: 40px; backdrop-filter: blur(24px); text-align: center;">
            <div class="login-icon">⚡</div>
            <h2 style="color: #f1f5f9; margin: 10px 0 4px;">System Login</h2>
            <p style="color: #64748b; font-size: 0.85rem;">Resource Dashboard Pro</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("👤 Username").strip()
            p = st.text_input("🔒 Password", type="password").strip()
            submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
            if submitted:
                db = load_users()
                if u in db and str(db[u]) == str(p):
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = u
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")
        st.markdown("<p style='text-align:center;color:#64748b;font-size:0.8rem;'>Default: admin / 1234</p>", unsafe_allow_html=True)
    st.stop()

# -----------------------------
# DATA COLLECTION
# -----------------------------
st_autorefresh(interval=3000, key="ref")
cpu = psutil.cpu_percent(interval=0.1)
mem = psutil.virtual_memory().percent

st.session_state["cpu_history"].append(cpu)
st.session_state["mem_history"].append(mem)
st.session_state["cpu_history"] = st.session_state["cpu_history"][-60:]
st.session_state["mem_history"] = st.session_state["mem_history"][-60:]

# -----------------------------
# PREDICTION & ANOMALY DETECTION
# -----------------------------
def predict_cpu(data):
    if len(data) < 5:
        return None, None
    trend = (data[-1] - data[0]) / len(data)
    future = [round(max(0, min(100, data[-1] + trend * i)), 2) for i in range(1, 11)]
    return list(range(len(data), len(data) + 10)), future

is_anomaly = False
avg_cpu = 0
if len(st.session_state["cpu_history"]) > 10:
    avg_cpu = np.mean(st.session_state["cpu_history"])
    std_cpu = np.std(st.session_state["cpu_history"])
    is_anomaly = cpu > (avg_cpu + 2 * std_cpu)

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
        <span style="font-size: 1.8rem;">⚡</span>
        <div>
            <div style="font-size: 1.1rem; font-weight: 800; color: #f1f5f9;">Dashboard Pro</div>
            <div style="font-size: 0.75rem; color: #64748b;">System Monitor v2.0</div>
        </div>
    </div>
    <hr style="border-color: rgba(255,255,255,0.06); margin: 16px 0;">
    """, unsafe_allow_html=True)
    st.markdown("#### ⚙️ Settings")
    threshold = st.slider("CPU Alert Threshold", 50, 100, 80)
    auto_optimize = st.toggle("🔄 Auto Optimization", value=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

# -----------------------------
# HEADER
# -----------------------------
st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 12px;">
        <span class="header-title">🚀 Resource Dashboard</span>
        <span class="header-live"><span class="live-dot"></span> Live</span>
    </div>
    <span style="color: #64748b; font-size: 0.85rem;">📡 User: {st.session_state['user']}</span>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# METRIC CARDS
# -----------------------------
health = round(100 - (cpu * 0.5 + mem * 0.5), 2)
num_tasks = len(psutil.pids())

colors = {"cpu": "#2dd4bf", "mem": "#a78bfa", "health": "#22c55e", "tasks": "#38bdf8"}
m1, m2, m3, m4 = st.columns(4)

def render_metric(col, icon, label, value, color):
    glow = f"radial-gradient(circle at top right, {color}15, transparent 70%)"
    col.markdown(f"""
    <div class="metric-card" style="background: {glow}, rgba(255,255,255,0.03);">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-icon">{icon}</div>
    </div>
    """, unsafe_allow_html=True)

render_metric(m1, "⚡", "CPU Usage", f"{cpu}%", colors["cpu"])
render_metric(m2, "🧠", "Memory", f"{mem}%", colors["mem"])
render_metric(m3, "💚", "Health", f"{health}%", colors["health"])
render_metric(m4, "📋", "Tasks", str(num_tasks), colors["tasks"])

st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)

# -----------------------------
# ALERTS (with danger/warning colors)
# -----------------------------
a1, a2, a3 = st.columns(3)
with a1:
    if cpu > threshold:
        cls, msg = "alert-danger", "⚠️ High CPU Load Detected"
    elif cpu > threshold * 0.75:
        cls, msg = "alert-warning", "🔶 Moderate CPU Load"
    else:
        cls, msg = "alert-success", "✅ System Stable"
    st.markdown(f'<div class="alert-bar {cls}"><strong>Status:</strong> {msg}</div>', unsafe_allow_html=True)
with a2:
    cls, msg = ("alert-danger", "🚨 Anomaly Detected") if is_anomaly else ("alert-info", "🔍 Normal Pattern")
    st.markdown(f'<div class="alert-bar {cls}"><strong>Smart Engine:</strong> {msg}</div>', unsafe_allow_html=True)
with a3:
    f_x, f_y = predict_cpu(st.session_state["cpu_history"])
    pred_msg = f"📊 Next: {f_y[0]}%" if f_y else "⏳ Analyzing..."
    st.markdown(f'<div class="alert-bar alert-info"><strong>Prediction:</strong> {pred_msg}</div>', unsafe_allow_html=True)

st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)

# -----------------------------
# CHARTS & HEALTH GAUGE
# -----------------------------
chart_col, gauge_col = st.columns([3, 1])

with chart_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Real-Time Performance</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=st.session_state["cpu_history"], name="CPU %",
        line=dict(color='#2dd4bf', width=2.5, shape='spline'),
        fill='tozeroy', fillcolor='rgba(45,212,191,0.08)',
    ))
    fig.add_trace(go.Scatter(
        y=st.session_state["mem_history"], name="MEM %",
        line=dict(color='#a78bfa', width=2.5, shape='spline'),
        fill='tozeroy', fillcolor='rgba(167,139,250,0.08)',
    ))
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#64748b", size=11),
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="center", x=0.5,
                    font=dict(size=12, color="#94a3b8")),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', zeroline=False,
                   range=[0, 100], showticklabels=True),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with gauge_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💚 System Health</div>', unsafe_allow_html=True)
    angle = (health / 100) * 180
    health_color = "#22c55e" if health >= 70 else "#f59e0b" if health >= 40 else "#ef4444"
    import math
    rad = math.radians(180 - angle)
    x = 60 + 45 * math.cos(rad)
    y = 60 - 45 * math.sin(rad)
    large_arc = 1 if angle > 180 else 0
    st.markdown(f"""
    <div style="text-align: center;">
        <svg viewBox="0 0 120 70" style="width: 180px; margin: 0 auto;">
            <path d="M 15 60 A 45 45 0 0 1 105 60" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8" stroke-linecap="round"/>
            <path d="M 15 60 A 45 45 0 {large_arc} 1 {x:.1f} {y:.1f}" fill="none" stroke="{health_color}" stroke-width="8" stroke-linecap="round" style="filter: drop-shadow(0 0 6px {health_color}80);"/>
        </svg>
        <div style="font-size: 2.5rem; font-weight: 800; color: {health_color}; margin-top: 8px;">{health}%</div>
        <div style="color: #64748b; font-size: 0.85rem;">Overall Score</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# RECOMMENDATIONS
# -----------------------------
st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">💡 Recommendations</div>', unsafe_allow_html=True)

recs = []
if cpu > 80:
    recs.append(("🔴", "Critical CPU Load", "CPU usage is dangerously high. Consider terminating heavy processes or scaling resources.", "danger"))
elif cpu > 60:
    recs.append(("🟠", "Elevated CPU Usage", "CPU is moderately high. Monitor closely and prepare to optimize.", "warning"))
else:
    recs.append(("🟢", "CPU Healthy", "CPU usage is within normal range. No action needed.", "success"))

if mem > 85:
    recs.append(("🔴", "Critical Memory Pressure", "Memory is nearly full. Close unused applications or increase RAM.", "danger"))
elif mem > 65:
    recs.append(("🟠", "Moderate Memory Usage", "Memory usage is climbing. Keep an eye on memory-hungry processes.", "warning"))
else:
    recs.append(("🟢", "Memory Healthy", "Memory usage is normal.", "success"))

if is_anomaly:
    recs.append(("🔴", "Anomaly Detected", "Unusual CPU spike detected. Investigate recent process activity.", "danger"))

if health < 40:
    recs.append(("🔴", "System Health Critical", "Overall health is poor. Immediate intervention recommended.", "danger"))
elif health < 70:
    recs.append(("🟠", "Health Needs Attention", "System health is below optimal. Review resource allocation.", "warning"))

if all(r[3] == "success" for r in recs):
    recs.append(("💡", "All Systems Optimal", "Everything is running smoothly. Great job!", "info"))

for icon, title, desc, severity in recs:
    st.markdown(f"""
    <div class="rec-card rec-{severity}">
        <div class="rec-title">{icon} {title}</div>
        <div class="rec-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# PROCESS MANAGER
# -----------------------------
st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 Process Manager</div>', unsafe_allow_html=True)

# Top controls - PID input with all 4 actions
top_cols = st.columns([2, 1, 1, 1, 1])
with top_cols[0]:
    pid_input = st.number_input("Enter PID", min_value=0, step=1, key="pid_top", label_visibility="collapsed")
with top_cols[1]:
    if st.button("⏹️ Stop", use_container_width=True, key="stop_top"):
        if pid_input > 0:
            try:
                proc = psutil.Process(int(pid_input))
                if int(pid_input) not in st.session_state["stopped_pids"]:
                    proc.suspend()
                    st.session_state["stopped_pids"].add(int(pid_input))
                    st.success(f"✅ Stopped PID {pid_input}")
                else:
                    st.warning(f"⚠️ PID {pid_input} already stopped")
            except Exception as e:
                st.error(f"❌ Error: {e}")
with top_cols[2]:
    if st.button("▶️ Start", use_container_width=True, key="start_top"):
        if pid_input > 0:
            try:
                proc = psutil.Process(int(pid_input))
                if int(pid_input) in st.session_state["stopped_pids"]:
                    proc.resume()
                    st.session_state["stopped_pids"].discard(int(pid_input))
                    st.success(f"✅ Started PID {pid_input}")
                else:
                    st.warning(f"⚠️ PID {pid_input} already running")
            except Exception as e:
                st.error(f"❌ Error: {e}")
with top_cols[3]:
    if st.button("⚡ Boost", use_container_width=True, key="boost_top"):
        if pid_input > 0:
            try:
                p = psutil.Process(int(pid_input))
                if os.name == 'nt':
                    p.nice(psutil.HIGH_PRIORITY_CLASS)
                else:
                    p.nice(-10)
                st.session_state["boosted_pids"].add(int(pid_input))
                st.success(f"✅ Boosted PID {pid_input}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
with top_cols[4]:
    if st.button("💀 Kill", use_container_width=True, type="primary", key="kill_top"):
        if pid_input > 0:
            try:
                psutil.Process(int(pid_input)).terminate()
                st.session_state["killed_pids"].add(int(pid_input))
                st.success(f"✅ Killed PID {pid_input}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# Process filter
search = st.text_input("🔍 Filter processes...", placeholder="Type process name...", key="proc_search")

@st.cache_data(ttl=2)
def get_procs():
    p_list = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            info = p.info
            info['cpu_percent'] = info['cpu_percent'] or 0.0
            info['memory_percent'] = round(info['memory_percent'] or 0.0, 2)
            info['status'] = info.get('status', 'unknown')
            p_list.append(info)
        except:
            continue
    return pd.DataFrame(p_list).sort_values('cpu_percent', ascending=False)

df_procs = get_procs()

# Filter out killed PIDs
if st.session_state["killed_pids"]:
    df_procs = df_procs[~df_procs['pid'].isin(st.session_state["killed_pids"])]

# Mark stopped/boosted
if not df_procs.empty:
    df_procs['boosted'] = df_procs['pid'].apply(lambda x: "⚡" if x in st.session_state["boosted_pids"] else "")
    df_procs['name'] = df_procs['name'] + df_procs['boosted']
    df_procs.loc[df_procs['pid'].isin(st.session_state["stopped_pids"]), 'status'] = 'stopped'
    df_procs.loc[df_procs['pid'].isin(st.session_state["stopped_pids"]), 'cpu_percent'] = 0.0
    df_procs = df_procs.drop(columns=['boosted'])

if search:
    df_procs = df_procs[df_procs['name'].str.contains(search, case=False, na=False)]

st.dataframe(
    df_procs.head(15),
    use_container_width=True,
    hide_index=True,
    column_config={
        "pid": st.column_config.NumberColumn("PID", width="small"),
        "name": st.column_config.TextColumn("Process Name", width="medium"),
        "cpu_percent": st.column_config.ProgressColumn("CPU %", min_value=0, max_value=100, format="%.1f%%"),
        "memory_percent": st.column_config.ProgressColumn("Memory %", min_value=0, max_value=100, format="%.2f%%"),
        "status": st.column_config.TextColumn("Status", width="small"),
    }
)

# Bottom controls
ctrl1, ctrl2 = st.columns(2)
with ctrl1:
    pid_kill = st.number_input("PID to Kill", min_value=0, step=1, key="k")
    if st.button("💀 Kill Process", type="primary", use_container_width=True):
        try:
            psutil.Process(int(pid_kill)).terminate()
            st.session_state["killed_pids"].add(int(pid_kill))
            st.success(f"✅ Killed PID {pid_kill}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
with ctrl2:
    pid_boost = st.number_input("PID to Boost", min_value=0, step=1, key="b")
    if st.button("⚡ Boost Priority", use_container_width=True):
        try:
            p = psutil.Process(int(pid_boost))
            if os.name == 'nt':
                p.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                p.nice(-10)
            st.session_state["boosted_pids"].add(int(pid_boost))
            st.success(f"✅ Boosted PID {pid_boost}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

ctrl3, ctrl4 = st.columns(2)
with ctrl3:
    pid_stop = st.number_input("PID to Stop", min_value=0, step=1, key="s")
    if st.button("⏹️ Stop Process", use_container_width=True):
        try:
            proc = psutil.Process(int(pid_stop))
            proc.suspend()
            st.session_state["stopped_pids"].add(int(pid_stop))
            st.success(f"✅ Stopped PID {pid_stop}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
with ctrl4:
    pid_start = st.number_input("PID to Start", min_value=0, step=1, key="st_pid")
    if st.button("▶️ Start Process", use_container_width=True):
        try:
            proc = psutil.Process(int(pid_start))
            proc.resume()
            st.session_state["stopped_pids"].discard(int(pid_start))
            st.success(f"✅ Started PID {pid_start}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)