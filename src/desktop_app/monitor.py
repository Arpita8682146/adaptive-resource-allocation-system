import psutil
from allocator import adjust_resources

cpu_data = []
mem_data = []

def monitor():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent

    cpu_data.append(cpu)
    mem_data.append(mem)

    if len(cpu_data) > 30:
        cpu_data.pop(0)
        mem_data.pop(0)

    adjust_resources()
    return cpu, mem