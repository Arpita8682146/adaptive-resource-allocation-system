CPU_THRESHOLD = 80
MEMORY_THRESHOLD = 90


def apply_adaptive_logic(resource_manager, processes):
    cpu_usage = resource_manager.get_cpu_usage()
    memory_usage = resource_manager.get_memory_usage()

    print("Checking system thresholds...")
    print("CPU Usage:", cpu_usage, "%")
    print("Memory Usage:", memory_usage, "%")

    # CPU Overload Condition
    if cpu_usage > CPU_THRESHOLD:
        print("CPU overload detected! Rebalancing CPU allocation...")

        # Reset CPU availability
        resource_manager.available_cpu = 100

        for p in processes:
            if p.priority == 1:
                p.allocated_cpu = 50
            elif p.priority == 2:
                p.allocated_cpu = 30
            else:
                p.allocated_cpu = 20

            resource_manager.available_cpu -= p.allocated_cpu

    # Memory Overload Condition
    if memory_usage >= MEMORY_THRESHOLD:
        print("Memory overload detected! Suspending lowest priority process...")

        lowest_priority_process = max(processes, key=lambda x: x.priority)

        resource_manager.available_memory += lowest_priority_process.allocated_memory
        lowest_priority_process.allocated_memory = 0


def apply_priority_aging(processes):
    print("Applying Priority Aging...")

    for p in processes:
        if p.allocated_memory == 0:
            if p.priority > 1:
                p.priority -= 1
                print(f"Priority of {p.pid} improved to {p.priority}")