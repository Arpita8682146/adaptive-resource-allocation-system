TOTAL_CPU = 100
TOTAL_MEMORY = 1000


class ResourceManager:
    def __init__(self):
        self.available_cpu = TOTAL_CPU
        self.available_memory = TOTAL_MEMORY

    def allocate_static(self, process):
        # Allocate memory if available
        if self.available_memory >= process.memory_required:
            process.allocated_memory = process.memory_required
            self.available_memory -= process.memory_required
        else:
            print("Not enough memory for", process.pid)

        # Allocate fixed CPU share (10% each)
        if self.available_cpu >= 10:
            process.allocated_cpu = 10
            self.available_cpu -= 10
        else:
            print("Not enough CPU for", process.pid)

    def display_system_status(self):
        print("Remaining CPU:", self.available_cpu)
        print("Remaining Memory:", self.available_memory)
        print("==============================")