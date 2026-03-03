SYSTEM ARCHITECTURE

1. Process Module:
   Represents processes with attributes like process ID,
   CPU requirement, memory requirement, and priority.

2. Resource Manager:
   Handles static resource allocation and tracks available CPU and memory.

3. Adaptive Logic:
   Detects overload conditions using threshold values and
   dynamically reallocates resources to prevent bottlenecks.

4. Main Controller:
   Integrates all modules and runs the simulation.

FLOW:

User Input → Process Creation → Static Allocation → 
Monitor CPU/Memory → Check Threshold → Adaptive Reallocation → Output Results