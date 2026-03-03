class Process:
    def __init__(self, pid, burst_time, memory_required, priority):
        self.pid = pid
        self.burst_time = burst_time
        self.memory_required = memory_required
        self.priority = priority
        
        # Initially no resources allocated
        self.allocated_cpu = 0
        self.allocated_memory = 0

    def display_info(self):
        print("Process ID:", self.pid)
        print("Burst Time:", self.burst_time)
        print("Memory Required:", self.memory_required)
        print("Priority:", self.priority)
        print("Allocated CPU:", self.allocated_cpu)
        print("Allocated Memory:", self.allocated_memory)
        print("-----------------------------")