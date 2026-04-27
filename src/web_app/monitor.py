import time
from collections import deque

import psutil

cpu_data = deque(maxlen=60)
mem_data = deque(maxlen=60)

psutil.cpu_percent(interval=None)
time.sleep(0.1)


def _append_history(history, value, history_size):
    history.append(round(float(value), 2))
    if not hasattr(history, "maxlen") and len(history) > history_size:
        del history[:-history_size]


def get_data(cpu_history=None, mem_history=None, history_size=60):
    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent

        if cpu is None:
            cpu = 0.0
        if cpu == 0.0 and not cpu_data:
            cpu = psutil.cpu_percent(interval=0.2)

        target_cpu_history = cpu_history if cpu_history is not None else cpu_data
        target_mem_history = mem_history if mem_history is not None else mem_data
        _append_history(target_cpu_history, cpu, history_size)
        _append_history(target_mem_history, mem, history_size)

        return round(cpu, 2), round(mem, 2), list(target_cpu_history), list(target_mem_history)
    except Exception as exc:
        print("Error in get_data:", exc)
        return 0.0, 0.0, list(cpu_history or cpu_data), list(mem_history or mem_data)
