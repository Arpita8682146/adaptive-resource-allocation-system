from process import Process
from resource_manager import ResourceManager
from adaptive_logic import apply_adaptive_logic, apply_priority_aging
import datetime


def main():
    print("ADAPTIVE RESOURCE ALLOCATION SYSTEM")
    print("========================================\n")

    # Create log file
    log_file = open("system_log.txt", "a")
    log_file.write("\n========================================\n")
    log_file.write("Execution Time: " + str(datetime.datetime.now()) + "\n")

    # Create Resource Manager
    rm = ResourceManager()

    # Create processes
    p1 = Process("P1", 10, 200, 1)
    p2 = Process("P2", 15, 300, 2)
    p3 = Process("P3", 20, 400, 3)

    processes = [p1, p2, p3]

    # ---------------------------
    # STATIC ALLOCATION PHASE
    # ---------------------------
    print("STATIC ALLOCATION PHASE")
    print("----------------------------------------")

    for p in processes:
        rm.allocate_static(p)

    print("\nPROCESS DETAILS AFTER STATIC ALLOCATION")
    print("----------------------------------------")
    for p in processes:
        p.display_info()

    print("SYSTEM STATUS AFTER STATIC ALLOCATION")
    print("----------------------------------------")
    rm.display_system_status()

    print("UTILIZATION AFTER STATIC ALLOCATION")
    print("----------------------------------------")
    static_cpu = rm.get_cpu_usage()
    static_memory = rm.get_memory_usage()

    print("CPU Utilization:", static_cpu, "%")
    print("Memory Utilization:", static_memory, "%")

    # ---------------------------
    # ADAPTIVE LOGIC PHASE
    # ---------------------------
    print("\nAPPLYING ADAPTIVE LOGIC")
    print("========================================")

    apply_adaptive_logic(rm, processes)

    # Apply starvation prevention
    apply_priority_aging(processes)

    print("\nPROCESS DETAILS AFTER ADAPTIVE LOGIC")
    print("----------------------------------------")
    for p in processes:
        p.display_info()

    print("UPDATED SYSTEM STATUS")
    print("----------------------------------------")
    rm.display_system_status()

    print("UTILIZATION AFTER ADAPTIVE LOGIC")
    print("----------------------------------------")
    adaptive_cpu = rm.get_cpu_usage()
    adaptive_memory = rm.get_memory_usage()

    print("CPU Utilization:", adaptive_cpu, "%")
    print("Memory Utilization:", adaptive_memory, "%")

    # ---------------------------
    # PERFORMANCE COMPARISON
    # ---------------------------
    print("\nPERFORMANCE COMPARISON")
    print("========================================")
    print("Static CPU Utilization:", static_cpu, "%")
    print("Adaptive CPU Utilization:", adaptive_cpu, "%")
    print("Static Memory Utilization:", static_memory, "%")
    print("Adaptive Memory Utilization:", adaptive_memory, "%")

    # Write results to log file
    log_file.write("Static CPU: " + str(static_cpu) + "\n")
    log_file.write("Adaptive CPU: " + str(adaptive_cpu) + "\n")
    log_file.write("Static Memory: " + str(static_memory) + "\n")
    log_file.write("Adaptive Memory: " + str(adaptive_memory) + "\n")
    log_file.close()


if __name__ == "__main__":
    main()