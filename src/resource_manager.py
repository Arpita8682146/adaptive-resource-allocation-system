TOTAL_CPU = 100
TOTAL_MEMORY = 1000


class ResourceManager:
    def __init__(self):
        self.available_cpu = TOTAL_CPU
        self.available_memory = TOTAL_MEMORY

    def allocate_static(self, process):
        """
        Allocates CPU and Memory statically to a process.
        """

        # Allocate memory
        if self.available_memory >= process.memory_required:
            process.allocated_memory = process.memory_required
            self.available_memory -= process.memory_required
        else:
            print(f"Not enough memory for {process.pid}")
            process.allocated_memory = 0

        # Allocate CPU (simulate heavy load for adaptive testing)
        cpu_share = 40  # intentionally high to simulate overload
        if self.available_cpu >= cpu_share:
            process.allocated_cpu = cpu_share
            self.available_cpu -= cpu_share
        else:
            print(f"Not enough CPU for {process.pid}")
            process.allocated_cpu = self.available_cpu
            self.available_cpu = 0

    def display_system_status(self):
        print("Remaining CPU:", self.available_cpu)
        print("Remaining Memory:", self.available_memory)
        print("==============================")

    def get_cpu_usage(self):
        used_cpu = TOTAL_CPU - self.available_cpu
        return (used_cpu / TOTAL_CPU) * 100

    def get_memory_usage(self):
        used_memory = TOTAL_MEMORY - self.available_memory
        return (used_memory / TOTAL_MEMORY) * 100