# 🚀 Adaptive Resource Allocation System

An intelligent system that monitors CPU and Memory usage in real-time and dynamically optimizes system performance using adaptive techniques.

---

## 📌 Overview

This project simulates how an operating system manages resources efficiently. It includes real-time monitoring, process control, prediction, and adaptive optimization.

---

## 🧠 Features

* 📊 Real-time CPU & Memory monitoring
* ⚙️ Adaptive process priority allocation
* 🤖 CPU prediction using Machine Learning (Linear Regression)
* 🚨 Anomaly detection
* 📋 Process Manager (Kill / Stop / Start / Boost)
* 🔐 User authentication system
* 📈 Interactive graphs (Plotly)
* 💻 Desktop GUI (Tkinter)
* 🌐 Web dashboard (Streamlit)

---

## 📁 Project Structure

```
ADAPTIVE-RESOURCE-ALLOCATION/
│
├── docs/
│
├── src/
│   ├── desktop_app/
│   │   ├── main.py
│   │   ├── dashboard.py
│   │   ├── monitor.py
│   │   ├── allocator.py
│
│   ├── web_app/
│   │   ├── main.py
│   │   ├── monitor.py
│   │   ├── predictor.py
│   │   ├── utils.py
│   │   ├── adaptive_logic.py
│   │   ├── stress.py
│   │   ├── users.json
│   │   ├── package.json
│   │   ├── README_NODE.md
│
├── venv/
├── requirements.txt
├── README.md
```

---

## ⚙️ How It Works

### 🔹 Monitoring

* Uses `psutil` to track CPU and Memory usage
* Stores historical data for graphs and prediction

### 🔹 Adaptive Resource Allocation

* If CPU usage is high → Increase priority (boost)
* If CPU usage is low → Decrease priority

### 🔹 Prediction

* Uses Linear Regression to predict future CPU usage
* Helps in proactive system optimization

### 🔹 Process Manager

Users can:

* 💀 Kill process (terminate)
* ⏹️ Stop process (pause/suspend)
* ▶️ Start process (resume)
* ⚡ Boost process priority

---

## 🚀 Installation

### 1️⃣ Clone Repository

```
git clone <your-repo-link>
cd ADAPTIVE-RESOURCE-ALLOCATION
```

### 2️⃣ Create Virtual Environment

```
python -m venv venv
```

Activate:

**Windows**

```
venv\Scripts\activate
```

**Mac/Linux**

```
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

## ▶️ Run the Project

### 🌐 Run Web Dashboard

```
streamlit run src/web_app/main.py
```

### 💻 Run Desktop Application

```
python src/desktop_app/main.py
```

---

## 🔐 Login Credentials

Default users:

```
admin : 1234
user1 : pass1
user2 : pass2
```

---

## 📊 Health Score

```
Health Score = 100 - (0.5 × CPU + 0.5 × Memory)
```

* Higher → Better system performance
* Lower → System under stress

---

## 🧪 Stress Testing

To simulate high CPU usage:

```
python src/web_app/stress.py
```

---

## 🔧 Technologies Used

* Python
* Streamlit
* Tkinter
* psutil
* NumPy
* Pandas
* Plotly
* Scikit-learn
* matplotlib

---

## ⚠️ Notes

* Some processes cannot be killed due to OS restrictions
* Admin privileges may be required
* CPU % may show 0 initially due to measurement delay

---

## 🚀 Future Enhancements

* Docker deployment
* Cloud monitoring
* AI-based anomaly detection
* Multi-user system
* Kubernetes integration

---

## 👨‍💻 Authors

* Shivam Bharti
* Arpita Singh
* Vishal Gaurav

---

## 💡 Conclusion

This project demonstrates how adaptive systems dynamically manage resources, similar to modern operating systems.

---
