def apply_adaptive_logic(rm, processes):
    cpu_threshold = 80
    memory_threshold = 800

    if rm.get_cpu_usage() > cpu_threshold:
        # Reallocate CPU based on priority
        rm.reallocate_cpu(processes)

    if rm.get_memory_usage() > memory_threshold:
        # Suspend lowest priority process
        lowest_priority_process = min(processes, key=lambda p: p.priority)
        rm.suspend_process(lowest_priority_process)

def apply_priority_aging(processes):
    for p in processes:
        if p.status == "ready":
            p.priority += 1  # Increase priority to prevent starvation