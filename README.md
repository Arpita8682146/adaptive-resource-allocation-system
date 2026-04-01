# 🚀 Adaptive Resource Allocation in Multiprogramming Systems

## 📌 Overview

This project implements an **Adaptive Resource Allocation System** that dynamically monitors and manages system resources (CPU & Memory) across multiple processes.

It includes both:

* 💻 Desktop-based implementation
* 🌐 Web-based dashboard (Streamlit)

The system adapts resource allocation in real-time to optimize performance.

---

## 🎯 Features

### 🔍 Real-Time Monitoring

* CPU usage tracking
* Memory usage tracking
* Live process list (PID, name, CPU%)

### ⚙️ Adaptive Resource Allocation

* Automatically adjusts process priority
* Uses `nice()` for priority control
* Dynamically optimizes CPU usage

### 🤖 AI-Based Features

* CPU prediction using Machine Learning
* Anomaly detection for unusual spikes

### 📊 Interactive Dashboard

* Built using Streamlit
* Real-time graphs (Plotly)
* Smooth UI with alerts and metrics

### 🔐 Multi-User Login System

* File-based authentication (`users.json`)
* Session handling
* Logout functionality

### 🔪 Process Management

* Kill process using PID
* Boost process priority

### 📥 Reports

* Download system data as CSV

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit** – Web dashboard
* **psutil** – System monitoring
* **pandas / numpy** – Data handling
* **plotly** – Graph visualization
* **scikit-learn** – ML prediction

---

## 📁 Project Structure

```bash
CSE-250-PROJECT/
│
├── desktop_app/              # 💻 Desktop version
│   ├── main.py
│   ├── monitor.py
│   ├── allocator.py
│   ├── dashboard.py
│
├── web_app/                 # 🌐 Web dashboard
│   ├── main.py
│   ├── monitor.py
│   ├── predictor.py
│   ├── utils.py
│   ├── stress.py
│   ├── users.json
│
├── venv/                    # Virtual environment
├── requirements.txt         # Dependencies
├── README.md                # Documentation
```

---

## ⚙️ Installation & Setup

### 1️⃣ Open Project Folder

```bash
cd CSE-250-PROJECT
```

---

### 2️⃣ Activate Virtual Environment

**Mac/Linux:**

```bash
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run Web Dashboard

```bash
python -m streamlit run web_app/main.py
```

---

## 🔐 Login Credentials

From `users.json`:

```text
Username: admin
Password: 1234
```

(Add more users in `users.json` if needed)

---

## 🧪 Demo (Testing)

1. Run dashboard
2. Run stress script:

```bash
python web_app/stress.py
```

3. Observe:

* CPU spike 📈
* Alerts ⚠️
* Graph updates

4. Find process PID
5. Kill process → CPU drops 📉

---

## 📊 How It Works

1. `monitor.py` → collects system data
2. `utils.py` → adjusts process priority
3. `predictor.py` → predicts CPU usage
4. `main.py` → integrates everything
5. Streamlit → displays dashboard

---

## 🧠 Key Concept

> Adaptive Resource Allocation dynamically distributes CPU resources based on process demand in real time.

---

## ⚠️ Limitations

* Cannot control OS kernel scheduling
* Some system processes cannot be terminated
* Requires admin privileges for certain operations

---

## 🚀 Future Enhancements

* Multi-system monitoring
* Email/notification alerts
* Role-based authentication
* Advanced ML models
* Cloud deployment

---

## 🎯 Conclusion

This project demonstrates how operating systems dynamically manage resources using adaptive techniques. It integrates monitoring, optimization, and prediction into a single system.

---
---

## ⭐ Status

✔️ Completed
✔️ Fully functional
✔️ Ready for submission
