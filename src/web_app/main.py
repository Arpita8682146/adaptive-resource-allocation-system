import streamlit as st
import psutil
import pandas as pd
import numpy as np
import json
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

from monitor import get_data
from utils import adjust_resources
from predictor import predict_future

# -----------------------------
# LOAD USERS
# -----------------------------
def load_users():
    with open("web_app/users.json") as f:
        return json.load(f)

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
def login():
    st.title("🔐 Login")

    users = load_users()

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.rerun()
        else:
            st.error("Invalid credentials")

# Session init
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(layout="wide")
st.title("🚀 Ultimate Resource Dashboard")

# -----------------------------
# AUTO REFRESH
# -----------------------------
st_autorefresh(interval=2000)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.write(f"👤 Logged in as: {st.session_state['user']}")

if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

threshold = st.sidebar.slider("CPU Alert Threshold", 50, 100, 80)
auto_optimize = st.sidebar.toggle("Auto Optimization", value=True)

# -----------------------------
# GET DATA
# -----------------------------
cpu, mem, cpu_data, mem_data = get_data()

if auto_optimize:
    adjust_resources()

# -----------------------------
# UI CARDS
# -----------------------------
col1, col2 = st.columns(2)
col1.metric("CPU Usage", f"{cpu}%")
col2.metric("Memory Usage", f"{mem}%")

# -----------------------------
# ALERTS
# -----------------------------
if cpu > threshold:
    st.error("⚠️ High CPU Usage")
elif cpu > threshold - 20:
    st.warning("⚠️ CPU Rising")
else:
    st.success("✅ System Stable")

# -----------------------------
# ANOMALY DETECTION
# -----------------------------
st.subheader("🤖 Anomaly Detection")

if len(cpu_data) > 10:
    avg = np.mean(cpu_data)
    std = np.std(cpu_data)

    if cpu > avg + 2 * std:
        st.error("🚨 Anomaly Detected")
    else:
        st.success("No anomaly detected")

# -----------------------------
# ML PREDICTION
# -----------------------------
future_x, future_y = predict_future(cpu_data)

st.subheader("🤖 CPU Prediction")
if future_y is not None:
    st.metric("Next CPU", f"{round(future_y[0],2)}%")

# -----------------------------
# INTERACTIVE GRAPH (PLOTLY)
# -----------------------------
st.subheader("📊 Interactive Graph")

fig = go.Figure()

fig.add_trace(go.Scatter(y=cpu_data, mode='lines', name='CPU'))
fig.add_trace(go.Scatter(y=mem_data, mode='lines', name='Memory'))

if future_y is not None:
    fig.add_trace(go.Scatter(
        x=list(range(len(cpu_data), len(cpu_data)+len(future_y))),
        y=future_y,
        mode='lines',
        name='Predicted CPU',
        line=dict(dash='dash')
    ))

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# HEALTH SCORE
# -----------------------------
health = 100 - (cpu * 0.5 + mem * 0.5)
st.subheader(f"💯 Health Score: {round(health,2)}")

# -----------------------------
# PROCESS TABLE
# -----------------------------
st.subheader("📋 Processes")

processes = []
for p in psutil.process_iter(['pid','name','cpu_percent']):
    try:
        processes.append(p.info)
    except:
        pass

df = pd.DataFrame(processes)
st.dataframe(df)

# -----------------------------
# PROCESS CONTROL
# -----------------------------
st.subheader("🔘 Control")

pid = st.number_input("Enter PID", step=1)

col3, col4 = st.columns(2)

if col3.button("Kill"):
    try:
        psutil.Process(int(pid)).terminate()
        st.success("Killed")
    except:
        st.error("Failed")

if col4.button("Boost"):
    try:
        psutil.Process(int(pid)).nice(-10)
        st.success("Boosted")
    except:
        st.error("Failed")

# -----------------------------
# DOWNLOAD REPORT
# -----------------------------
st.subheader("📊 Download Report")

st.download_button(
    "Download CSV",
    df.to_csv(index=False),
    "system_report.csv"
)

# -----------------------------
# SUGGESTIONS
# -----------------------------
st.subheader("💡 Suggestions")

if cpu > threshold:
    st.write("🔴 Close heavy apps like Chrome or games")
elif cpu > threshold - 20:
    st.write("🟡 Reduce background apps")
else:
    st.write("🟢 System running efficiently")