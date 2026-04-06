import psutil
from collections import deque
import time

# 📊 Store last 50 values
cpu_data = deque(maxlen=50)
mem_data = deque(maxlen=50)

# 🔥 IMPORTANT: Warm-up CPU measurement (prevents 0.0 issue)
psutil.cpu_percent(interval=None)
time.sleep(0.1)

def get_data():
    try:
        # ⚡ Get CPU (NON-blocking + accurate after warm-up)
        cpu = psutil.cpu_percent(interval=None)

        # 💾 Memory
        mem = psutil.virtual_memory().percent

        # 🧠 Safety fallback
        if cpu is None or cpu == 0.0:
            cpu = psutil.cpu_percent(interval=0.5)  # fallback for accuracy

        # 📈 Store history
        cpu_data.append(cpu)
        mem_data.append(mem)

        return cpu, mem, list(cpu_data), list(mem_data)

    except Exception as e:
        print("Error in get_data:", e)
        return 0.0, 0.0, list(cpu_data), list(mem_data)