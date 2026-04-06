# 🚀 Adaptive Resource Allocation System (Operating Systems Project)

## 📌 Project Overview
This project simulates an **Adaptive Resource Allocation System** in a multiprogramming environment.  
It dynamically manages CPU and memory allocation among processes to improve system efficiency and avoid resource starvation.

The system starts with **static allocation** and then applies **adaptive logic** based on system load and process priority.

---

## 🎯 Objectives
- Maximize CPU utilization
- Prevent memory overload
- Ensure fair resource distribution
- Avoid starvation using priority aging
- Compare static vs adaptive allocation
- Simulate real-world OS behavior

---

## ⚙️ Key Features

### 🔹 1. Static Resource Allocation
- Initial CPU and memory assigned to processes
- Based on predefined requirements

### 🔹 2. Adaptive Resource Allocation
- Dynamically reallocates resources
- Adjusts based on system usage and thresholds

### 🔹 3. Priority Aging
- Prevents starvation of low-priority processes
- Gradually increases priority over time

### 🔹 4. Real-Time Monitoring
- Tracks CPU and memory usage
- Helps in decision-making

### 🔹 5. Stress Testing Module
- Simulates high system load
- Tests system stability under pressure

### 🔹 6. Prediction Module
- Predicts future resource usage
- Enhances proactive allocation

### 🔹 7. Execution Logging
- Logs system behavior
- Useful for debugging and analysis

---

## 🧠 System Architecture
Process → Resource Manager → Adaptive Logic → Allocation Update
↓
Monitoring + Prediction + Stress Testing
---

## 📂 Project Structure
adaptive-resource-allocation-system/
│
├── src/
│ ├── main.py # Main execution file
│ ├── process.py # Process class
│ ├── resource_manager.py # Resource allocation logic
│ ├── adaptive_logic.py # Adaptive + priority aging
│
│ └── web_app/
│ ├── main.py # Streamlit UI (Frontend)
│ ├── monitor.py # System monitoring
│ ├── predictor.py # Prediction logic
│ ├── stress.py # Stress testing
│ ├── utils.py # Helper functions
│ └── users.json # User data
│
├── system_log.txt # Execution logs
├── README.md # Project documentation


🖥️ Output

Process details (CPU, memory, priority)
Updated system status
Real-time dashboard visualization
Adaptive allocation results

🔬 Technologies Used

Python
Streamlit (Frontend)
OS Concepts (Scheduling, Allocation)
Git & GitHub (Collaboration)
💡 Key Concepts Used
Multiprogramming
CPU Scheduling
Resource Allocation
Priority Aging
Dynamic Optimization
