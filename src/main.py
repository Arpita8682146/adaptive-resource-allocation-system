from process import Process
from resource_manager import ResourceManager
from adaptive_logic import apply_adaptive_logic, apply_priority_aging
import datetime


def run_simulation():
    rm = ResourceManager()

    # Create processes
    p1 = Process("P1", 10, 200, 1)
    p2 = Process("P2", 15, 300, 2)
    p3 = Process("P3", 20, 400, 3)

    processes = [p1, p2, p3]

    # Static allocation
    for p in processes:
        rm.allocate_static(p)

    static_cpu = rm.get_cpu_usage()
    static_memory = rm.get_memory_usage()

    # Adaptive logic
    apply_adaptive_logic(rm, processes)
    apply_priority_aging(processes)

    adaptive_cpu = rm.get_cpu_usage()
    adaptive_memory = rm.get_memory_usage()

    # Logging
    with open("system_log.txt", "a") as log_file:
        log_file.write("\n\n")
        log_file.write("Execution Time: " + str(datetime.datetime.now()) + "\n")
        log_file.write("Static CPU: " + str(static_cpu) + "\n")
        log_file.write("Adaptive CPU: " + str(adaptive_cpu) + "\n")
        log_file.write("Static Memory: " + str(static_memory) + "\n")
        log_file.write("Adaptive Memory: " + str(adaptive_memory) + "\n")

    return {
        "processes": processes,
        "static_cpu": static_cpu,
        "adaptive_cpu": adaptive_cpu,
        "static_memory": static_memory,
        "adaptive_memory": adaptive_memory
    }


def main():
    print("ADAPTIVE RESOURCE ALLOCATION SYSTEM")
    print("\n")

    result = run_simulation()

    print("Static CPU:", result["static_cpu"])
    print("Adaptive CPU:", result["adaptive_cpu"])
    print("Static Memory:", result["static_memory"])
    print("Adaptive Memory:", result["adaptive_memory"])


if __name__ == "__main__":
    main()