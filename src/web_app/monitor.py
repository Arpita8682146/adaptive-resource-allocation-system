import psutil

cpu_data = []
mem_data = []

def get_data():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent

    cpu_data.append(cpu)
    mem_data.append(mem)

    if len(cpu_data) > 50:
        cpu_data.pop(0)
        mem_data.pop(0)

    return cpu, mem, cpu_data, mem_data