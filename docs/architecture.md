SYSTEM ARCHITECTURE

1. Process Module
   Represents a process with attributes:
   - Process ID
   - Burst Time
   - Memory Requirement
   - Priority

2. Resource Manager
   - Handles static CPU and memory allocation
   - Tracks available system resources
   - Calculates utilization percentages

3. Adaptive Logic
   - Monitors CPU and memory thresholds
   - Redistributes CPU based on priority
   - Suspends lowest priority process during memory overload
   - Implements priority aging to prevent starvation

4. Main Controller
   - Integrates all modules
   - Executes simulation phases
   - Logs system performance

FLOW:

Process Creation →
Static Allocation →
Monitor Utilization →
Threshold Check →
Adaptive Reallocation →
Priority Aging →
Performance Comparison →
Logging