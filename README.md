# Adaptive Resource Allocation in Multiprogramming Systems (Operating Systems Project)

## 📌 Project Description
This project simulates dynamic CPU and memory allocation in a multiprogramming environment.  

The system initially performs **static allocation** and then applies **adaptive resource reallocation** when system utilization exceeds predefined thresholds.

---

## 🎯 Objectives
- Maximize CPU utilization
- Prevent memory overload
- Reduce system bottlenecks
- Ensure fairness using priority aging
- Compare static and adaptive allocation performance

---

## 🚀 Key Features
- Static CPU and memory allocation
- Real-time utilization monitoring
- Threshold-based adaptive reallocation
- Priority-based CPU redistribution
- Memory suspension during overload
- Starvation prevention using priority aging
- Performance comparison (Static vs Adaptive)
- Execution logging system

---

## 🧠 System Modules

### 1. Process Module
Represents processes with:
- Process ID
- Burst Time
- Memory Requirement
- Priority

### 2. Resource Manager
- Handles CPU and memory allocation
- Tracks available resources
- Calculates utilization

### 3. Adaptive Logic
- Detects overload using thresholds
- Redistributes CPU dynamically
- Suspends low-priority processes
- Implements priority aging

### 4. Main Controller
- Integrates all modules
- Executes simulation
- Logs system performance

---

## ⚙️ Technology Used
- Python
- Streamlit (for visualization)
- Git & GitHub

---

## ▶️ How to Run

### Run Backend:
```bash
python src/main.py
adaptive-resource-allocation-system/
│
├── README.md
├── src/
│   ├── process.py
│   ├── resource_manager.py
│   ├── adaptive_logic.py
│   ├── main.py
│   └── dashboard.py
└── docs/
    └── architecture.md
    📊 Sample Output

The system displays:

Process allocation details
CPU and memory utilization
Adaptive redistribution results
Performance comparison
Execution logs
📈 Performance Comparison

The project compares:

Static allocation vs Adaptive allocation
CPU utilization improvement
Memory optimization
    




















