const rawAlgorithmDetails = {
  fcfs: {
    label: "FCFS",
    accent: "#2fc5c9",
    description:
      "First Come First Serve executes each process in arrival order without preemption.",
  },
  roundRobin: {
    label: "Round Robin",
    accent: "#ff8f57",
    description:
      "Round Robin time-slices ready processes with a configurable quantum for fair CPU sharing.",
  },
  priorityRoundRobin: {
    label: "Priority Round Robin",
    accent: "#f0c54b",
    description:
      "Priority Round Robin uses priority bands first, then rotates processes within a band with time slicing.",
  },
  mlq: {
    label: "MLQ",
    accent: "#67d58a",
    description:
      "Multi-Level Queue uses fixed queue classes with strict queue priority and queue-specific quanta.",
  },
  mlfq: {
    label: "MLFQ",
    accent: "#6aa8ff",
    description:
      "Multi-Level Feedback Queue adapts queue level through demotion on CPU use and promotion through aging.",
  },
  macosAdaptive: {
    label: "macOS-Style Adaptive",
    accent: "#ff6b6b",
    description:
      "A QoS-based adaptive scheduler with feedback priority, time sharing, and pressure-aware memory management.",
  },
};

export const ALGORITHM_DETAILS = rawAlgorithmDetails;

export const QUEUE_CONFIG = {
  system: { label: "System", rank: 0, quantum: 2, accent: "#d64f4f" },
  interactive: { label: "Interactive", rank: 1, quantum: 3, accent: "#ff8f57" },
  batch: { label: "Batch", rank: 2, quantum: 5, accent: "#2fc5c9" },
  background: { label: "Background", rank: 3, quantum: Number.POSITIVE_INFINITY, accent: "#6a738a" },
};

export const QOS_CONFIG = {
  userInteractive: { label: "User Interactive", weight: 100, quantum: 2, pressureBias: 0.2 },
  userInitiated: { label: "User Initiated", weight: 84, quantum: 3, pressureBias: 0.35 },
  default: { label: "Default", weight: 68, quantum: 4, pressureBias: 0.55 },
  utility: { label: "Utility", weight: 50, quantum: 5, pressureBias: 0.8 },
  background: { label: "Background", weight: 30, quantum: 6, pressureBias: 1 },
};

export const DEFAULT_SETTINGS = {
  roundRobinQuantum: 3,
  priorityQuantum: 2,
  mlqQuantums: {
    system: 2,
    interactive: 3,
    batch: 5,
    background: Number.POSITIVE_INFINITY,
  },
  mlfqQuantums: [2, 4, 8],
  mlfqAgingThreshold: 6,
  memoryCapacity: 1200,
  memoryWarningThreshold: 0.72,
  memoryCriticalThreshold: 0.9,
};

export const DEMO_PROCESSES = [
  {
    id: "P1",
    name: "Atlas",
    arrival: 0,
    burst: 6,
    priority: 2,
    queue: "system",
    qos: "userInteractive",
    memory: 220,
  },
  {
    id: "P2",
    name: "Beacon",
    arrival: 1,
    burst: 4,
    priority: 4,
    queue: "interactive",
    qos: "userInitiated",
    memory: 180,
  },
  {
    id: "P3",
    name: "Comet",
    arrival: 2,
    burst: 9,
    priority: 6,
    queue: "batch",
    qos: "default",
    memory: 340,
  },
  {
    id: "P4",
    name: "Drift",
    arrival: 3,
    burst: 5,
    priority: 7,
    queue: "background",
    qos: "utility",
    memory: 260,
  },
  {
    id: "P5",
    name: "Echo",
    arrival: 4,
    burst: 3,
    priority: 1,
    queue: "system",
    qos: "userInteractive",
    memory: 120,
  },
  {
    id: "P6",
    name: "Flux",
    arrival: 6,
    burst: 7,
    priority: 8,
    queue: "background",
    qos: "background",
    memory: 420,
  },
];

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function mergeSettings(overrides = {}) {
  return {
    ...DEFAULT_SETTINGS,
    ...overrides,
    mlqQuantums: {
      ...DEFAULT_SETTINGS.mlqQuantums,
      ...(overrides.mlqQuantums || {}),
    },
    mlfqQuantums: Array.isArray(overrides.mlfqQuantums) && overrides.mlfqQuantums.length === 3
      ? overrides.mlfqQuantums.map((value, index) =>
          Number.isFinite(Number(value)) && Number(value) > 0 ? Number(value) : DEFAULT_SETTINGS.mlfqQuantums[index]
        )
      : [...DEFAULT_SETTINGS.mlfqQuantums],
  };
}

function normalizeProcess(process, index) {
  const queueKey = Object.hasOwn(QUEUE_CONFIG, process.queue) ? process.queue : "interactive";
  const qosKey = Object.hasOwn(QOS_CONFIG, process.qos) ? process.qos : "default";

  return {
    id: process.id || `P${index + 1}`,
    name: process.name || `Process ${index + 1}`,
    arrival: Math.max(0, Number(process.arrival) || 0),
    burst: Math.max(1, Number(process.burst) || 1),
    remaining: Math.max(1, Number(process.burst) || 1),
    priority: clamp(Math.round(Number(process.priority) || 5), 1, 10),
    queue: queueKey,
    qos: qosKey,
    memory: Math.max(64, Number(process.memory) || 128),
    start: null,
    completion: null,
    arrived: false,
    waitTicks: 0,
    recentCpu: 0,
    runStreak: 0,
    totalRun: 0,
    sliceRemaining: null,
    mlfqLevel: 0,
    lastQueuedAt: 0,
    score: 0,
  };
}

function cloneProcesses(processes) {
  return processes.map((process, index) => normalizeProcess(process, index));
}

function byArrivalThenId(processA, processB) {
  if (processA.arrival !== processB.arrival) {
    return processA.arrival - processB.arrival;
  }

  return processA.id.localeCompare(processB.id);
}

function enqueueArrivals(processes, time, onArrival) {
  processes
    .filter((process) => !process.arrived && process.arrival <= time)
    .sort(byArrivalThenId)
    .forEach((process) => {
      process.arrived = true;
      process.lastQueuedAt = time;
      onArrival(process);
    });
}

function getActiveProcesses(processes, time) {
  return processes.filter((process) => process.arrived && process.remaining > 0 && process.arrival <= time);
}

function appendEvent(events, time, message, tone = "info") {
  events.push({ time, message, tone });
}

function calculateMemorySnapshot(processes, settings) {
  const rawUsed = processes.reduce((total, process) => total + process.memory, 0);
  const capacity = Math.max(256, Number(settings.memoryCapacity) || DEFAULT_SETTINGS.memoryCapacity);
  const warningPoint = capacity * clamp(Number(settings.memoryWarningThreshold) || DEFAULT_SETTINGS.memoryWarningThreshold, 0.4, 0.95);
  const criticalPoint = capacity * clamp(Number(settings.memoryCriticalThreshold) || DEFAULT_SETTINGS.memoryCriticalThreshold, 0.5, 0.99);

  let pressure = "normal";
  if (rawUsed > criticalPoint) {
    pressure = "critical";
  } else if (rawUsed > warningPoint) {
    pressure = "warning";
  }

  let reclaimed = 0;
  let compressed = 0;

  if (pressure !== "normal") {
    const targetUsage = pressure === "critical" ? capacity * 0.82 : capacity * 0.9;
    const candidates = [...processes].sort((left, right) => {
      const qosDelta = QOS_CONFIG[right.qos].pressureBias - QOS_CONFIG[left.qos].pressureBias;
      if (qosDelta !== 0) {
        return qosDelta;
      }

      return right.memory - left.memory;
    });

    for (const candidate of candidates) {
      if (rawUsed - reclaimed <= targetUsage) {
        break;
      }

      const reclaimFactor = pressure === "critical"
        ? 0.22 + QOS_CONFIG[candidate.qos].pressureBias * 0.28
        : 0.1 + QOS_CONFIG[candidate.qos].pressureBias * 0.16;

      const saved = Math.min(candidate.memory * reclaimFactor, candidate.memory * 0.55);
      reclaimed += saved;
      compressed += saved * 0.65;
    }
  }

  const effectiveUsed = Math.max(0, rawUsed - reclaimed);

  return {
    rawUsed,
    effectiveUsed,
    reclaimed,
    compressed,
    capacity,
    ratio: capacity === 0 ? 0 : effectiveUsed / capacity,
    pressure,
    pressureScore: pressure === "critical" ? 2 : pressure === "warning" ? 1 : 0,
  };
}

function updateFeedback(processes, runningProcess) {
  processes.forEach((process) => {
    if (!process.arrived || process.remaining <= 0) {
      return;
    }

    if (runningProcess && process.id === runningProcess.id) {
      process.waitTicks = 0;
      process.recentCpu = Math.min(10, process.recentCpu + 1);
      process.runStreak += 1;
      process.totalRun += 1;
      return;
    }

    process.waitTicks += 1;
    process.runStreak = 0;
    process.recentCpu = Math.max(0, process.recentCpu - 0.35);
  });
}

function makeTick({
  time,
  runningProcess,
  algorithm,
  queueLabel,
  note,
  memory,
}) {
  return {
    start: time,
    end: time + 1,
    processId: runningProcess ? runningProcess.id : "idle",
    name: runningProcess ? runningProcess.name : "Idle",
    algorithm,
    queueLabel: queueLabel || "Idle",
    priority: runningProcess ? runningProcess.priority : null,
    qos: runningProcess ? runningProcess.qos : null,
    score: runningProcess ? runningProcess.score : null,
    note: note || "",
    memory,
  };
}

function compressTimeline(ticks) {
  return ticks.reduce((segments, tick) => {
    const last = segments[segments.length - 1];

    if (
      last &&
      last.processId === tick.processId &&
      last.queueLabel === tick.queueLabel &&
      last.memory.pressure === tick.memory.pressure
    ) {
      last.end = tick.end;
      last.memory = tick.memory;
      if (tick.note) {
        last.note = last.note ? `${last.note} | ${tick.note}` : tick.note;
      }
      return segments;
    }

    segments.push({ ...tick });
    return segments;
  }, []);
}

function calculateMetrics(processes, makespan) {
  return processes
    .map((process) => {
      const turnaround = (process.completion ?? 0) - process.arrival;
      const waiting = turnaround - process.burst;
      const response = (process.start ?? process.arrival) - process.arrival;

      return {
        id: process.id,
        name: process.name,
        arrival: process.arrival,
        burst: process.burst,
        priority: process.priority,
        queue: process.queue,
        qos: process.qos,
        completion: process.completion ?? 0,
        turnaround,
        waiting,
        response,
        cpuShare: makespan === 0 ? 0 : (process.burst / makespan) * 100,
      };
    })
    .sort(byArrivalThenId);
}

function jainsFairnessIndex(values) {
  if (values.length === 0) {
    return 0;
  }

  const sum = values.reduce((total, value) => total + value, 0);
  const squaredSum = values.reduce((total, value) => total + value ** 2, 0);

  if (squaredSum === 0) {
    return 0;
  }

  return (sum ** 2) / (values.length * squaredSum);
}

function summarize(processes, ticks, metrics, events) {
  const makespan = ticks.length;
  const busyTicks = ticks.filter((tick) => tick.processId !== "idle").length;
  const waitingValues = metrics.map((metric) => metric.waiting);
  const turnaroundValues = metrics.map((metric) => metric.turnaround);
  const responseValues = metrics.map((metric) => metric.response);
  const serviceRatios = metrics.map((metric) => metric.burst / Math.max(metric.turnaround, 1));
  const memoryCriticalMoments = ticks.filter((tick) => tick.memory.pressure === "critical").length;
  const reclaimedMemory = ticks.reduce((total, tick) => total + tick.memory.reclaimed, 0);

  return {
    processCount: processes.length,
    makespan,
    cpuUtilization: makespan === 0 ? 0 : (busyTicks / makespan) * 100,
    throughput: makespan === 0 ? 0 : processes.length / makespan,
    avgWaiting: waitingValues.length === 0 ? 0 : waitingValues.reduce((total, value) => total + value, 0) / waitingValues.length,
    avgTurnaround:
      turnaroundValues.length === 0 ? 0 : turnaroundValues.reduce((total, value) => total + value, 0) / turnaroundValues.length,
    avgResponse: responseValues.length === 0 ? 0 : responseValues.reduce((total, value) => total + value, 0) / responseValues.length,
    fairness: jainsFairnessIndex(serviceRatios) * 100,
    memoryCriticalMoments,
    reclaimedMemory,
    eventCount: events.length,
  };
}

function finalizeResult(algorithmKey, processes, ticks, events) {
  const timeline = compressTimeline(ticks);
  const metrics = calculateMetrics(processes, ticks.length);
  const summary = summarize(processes, ticks, metrics, events);
  const memoryTimeline = ticks.map((tick) => ({
    time: tick.start,
    usedMemory: tick.memory.rawUsed,
    effectiveUsed: tick.memory.effectiveUsed,
    reclaimed: tick.memory.reclaimed,
    compressed: tick.memory.compressed,
    pressure: tick.memory.pressure,
    capacity: tick.memory.capacity,
  }));

  return {
    algorithm: algorithmKey,
    label: ALGORITHM_DETAILS[algorithmKey].label,
    description: ALGORITHM_DETAILS[algorithmKey].description,
    accent: ALGORITHM_DETAILS[algorithmKey].accent,
    timeline,
    ticks,
    metrics,
    summary,
    events,
    memoryTimeline,
  };
}

function runFcfs(inputProcesses, settings) {
  const processes = cloneProcesses(inputProcesses);
  const readyQueue = [];
  const ticks = [];
  const events = [];
  let current = null;
  let time = 0;
  let completed = 0;
  let lastPressure = "normal";

  while (completed < processes.length && time < 10000) {
    enqueueArrivals(processes, time, (process) => {
      readyQueue.push(process);
      appendEvent(events, time, `${process.name} entered the FCFS ready queue.`);
    });

    if (!current && readyQueue.length > 0) {
      current = readyQueue.shift();
    }

    const memory = calculateMemorySnapshot(getActiveProcesses(processes, time), settings);
    if (memory.pressure !== lastPressure) {
      appendEvent(events, time, `Memory pressure changed to ${memory.pressure}.`, memory.pressure === "critical" ? "warning" : "info");
      lastPressure = memory.pressure;
    }

    if (!current) {
      ticks.push(makeTick({ time, runningProcess: null, algorithm: "fcfs", queueLabel: "Idle", note: "CPU idle", memory }));
      time += 1;
      continue;
    }

    if (current.start === null) {
      current.start = time;
    }

    current.remaining -= 1;
    updateFeedback(processes, current);
    ticks.push(
      makeTick({
        time,
        runningProcess: current,
        algorithm: "fcfs",
        queueLabel: "FCFS Queue",
        note: "Non-preemptive dispatch",
        memory,
      })
    );

    if (current.remaining === 0) {
      current.completion = time + 1;
      completed += 1;
      appendEvent(events, time + 1, `${current.name} completed execution.`);
      current = null;
    }

    time += 1;
  }

  return finalizeResult("fcfs", processes, ticks, events);
}

function highestPriorityReady(readyMap) {
  return [...readyMap.keys()].sort((left, right) => Number(left) - Number(right)).find((priority) => readyMap.get(priority).length > 0);
}

function runRoundRobin(inputProcesses, settings) {
  const processes = cloneProcesses(inputProcesses);
  const quantum = Math.max(1, Number(settings.roundRobinQuantum) || DEFAULT_SETTINGS.roundRobinQuantum);
  const readyQueue = [];
  const ticks = [];
  const events = [];
  let current = null;
  let time = 0;
  let completed = 0;

  while (completed < processes.length && time < 10000) {
    enqueueArrivals(processes, time, (process) => {
      readyQueue.push(process);
      appendEvent(events, time, `${process.name} joined the Round Robin queue.`);
    });

    if (!current && readyQueue.length > 0) {
      current = readyQueue.shift();
      current.sliceRemaining = quantum;
    }

    const memory = calculateMemorySnapshot(getActiveProcesses(processes, time), settings);

    if (!current) {
      ticks.push(makeTick({ time, runningProcess: null, algorithm: "roundRobin", queueLabel: "Idle", note: "CPU idle", memory }));
      time += 1;
      continue;
    }

    if (current.start === null) {
      current.start = time;
    }

    current.remaining -= 1;
    current.sliceRemaining -= 1;
    updateFeedback(processes, current);
    ticks.push(
      makeTick({
        time,
        runningProcess: current,
        algorithm: "roundRobin",
        queueLabel: `RR q=${quantum}`,
        note: `Time slice remaining: ${current.sliceRemaining}`,
        memory,
      })
    );

    if (current.remaining === 0) {
      current.completion = time + 1;
      completed += 1;
      appendEvent(events, time + 1, `${current.name} finished during its time slice.`);
      current = null;
    } else if (current.sliceRemaining === 0) {
      appendEvent(events, time + 1, `${current.name} rotated to the back of the RR queue.`);
      readyQueue.push(current);
      current = null;
    }

    time += 1;
  }

  return finalizeResult("roundRobin", processes, ticks, events);
}

function runPriorityRoundRobin(inputProcesses, settings) {
  const processes = cloneProcesses(inputProcesses);
  const quantum = Math.max(1, Number(settings.priorityQuantum) || DEFAULT_SETTINGS.priorityQuantum);
  const readyByPriority = new Map(Array.from({ length: 10 }, (_, index) => [index + 1, []]));
  const ticks = [];
  const events = [];
  let current = null;
  let time = 0;
  let completed = 0;

  while (completed < processes.length && time < 10000) {
    enqueueArrivals(processes, time, (process) => {
      readyByPriority.get(process.priority).push(process);
      appendEvent(events, time, `${process.name} entered priority band ${process.priority}.`);
    });

    const topPriority = highestPriorityReady(readyByPriority);
    if (current && topPriority && Number(topPriority) < current.priority) {
      readyByPriority.get(current.priority).push(current);
      appendEvent(events, time, `${current.name} was preempted by a higher-priority process.`, "warning");
      current = null;
    }

    if (!current && topPriority) {
      current = readyByPriority.get(topPriority).shift();
      current.sliceRemaining = quantum;
    }

    const memory = calculateMemorySnapshot(getActiveProcesses(processes, time), settings);

    if (!current) {
      ticks.push(
        makeTick({
          time,
          runningProcess: null,
          algorithm: "priorityRoundRobin",
          queueLabel: "Idle",
          note: "No ready process",
          memory,
        })
      );
      time += 1;
      continue;
    }

    if (current.start === null) {
      current.start = time;
    }

    current.remaining -= 1;
    current.sliceRemaining -= 1;
    updateFeedback(processes, current);
    ticks.push(
      makeTick({
        time,
        runningProcess: current,
        algorithm: "priorityRoundRobin",
        queueLabel: `Priority ${current.priority}`,
        note: `Band RR slice left: ${current.sliceRemaining}`,
        memory,
      })
    );

    if (current.remaining === 0) {
      current.completion = time + 1;
      completed += 1;
      appendEvent(events, time + 1, `${current.name} completed from priority ${current.priority}.`);
      current = null;
    } else if (current.sliceRemaining === 0) {
      readyByPriority.get(current.priority).push(current);
      appendEvent(events, time + 1, `${current.name} yielded after exhausting its priority band quantum.`);
      current = null;
    }

    time += 1;
  }

  return finalizeResult("priorityRoundRobin", processes, ticks, events);
}

function highestQueueReady(queues) {
  return Object.keys(QUEUE_CONFIG).find((queueKey) => queues[queueKey].length > 0);
}

function runMlq(inputProcesses, settings) {
  const processes = cloneProcesses(inputProcesses);
  const quantums = {
    system: Math.max(1, Number(settings.mlqQuantums.system) || DEFAULT_SETTINGS.mlqQuantums.system),
    interactive: Math.max(1, Number(settings.mlqQuantums.interactive) || DEFAULT_SETTINGS.mlqQuantums.interactive),
    batch: Math.max(1, Number(settings.mlqQuantums.batch) || DEFAULT_SETTINGS.mlqQuantums.batch),
    background: Number.POSITIVE_INFINITY,
  };
  const queues = {
    system: [],
    interactive: [],
    batch: [],
    background: [],
  };
  const ticks = [];
  const events = [];
  let current = null;
  let time = 0;
  let completed = 0;

  while (completed < processes.length && time < 10000) {
    enqueueArrivals(processes, time, (process) => {
      queues[process.queue].push(process);
      appendEvent(events, time, `${process.name} entered the ${QUEUE_CONFIG[process.queue].label} queue.`);
    });

    const topQueue = highestQueueReady(queues);
    if (current && topQueue && QUEUE_CONFIG[topQueue].rank < QUEUE_CONFIG[current.queue].rank) {
      queues[current.queue].push(current);
      appendEvent(events, time, `${current.name} was preempted by the ${QUEUE_CONFIG[topQueue].label} queue.`, "warning");
      current = null;
    }

    if (!current && topQueue) {
      current = queues[topQueue].shift();
      current.sliceRemaining = quantums[current.queue];
    }

    const memory = calculateMemorySnapshot(getActiveProcesses(processes, time), settings);

    if (!current) {
      ticks.push(makeTick({ time, runningProcess: null, algorithm: "mlq", queueLabel: "Idle", note: "No ready queue", memory }));
      time += 1;
      continue;
    }

    if (current.start === null) {
      current.start = time;
    }

    current.remaining -= 1;
    if (Number.isFinite(current.sliceRemaining)) {
      current.sliceRemaining -= 1;
    }
    updateFeedback(processes, current);
    ticks.push(
      makeTick({
        time,
        runningProcess: current,
        algorithm: "mlq",
        queueLabel: `${QUEUE_CONFIG[current.queue].label} Queue`,
        note: Number.isFinite(current.sliceRemaining) ? `Queue slice left: ${current.sliceRemaining}` : "Queue runs FCFS",
        memory,
      })
    );

    if (current.remaining === 0) {
      current.completion = time + 1;
      completed += 1;
      appendEvent(events, time + 1, `${current.name} completed inside the ${QUEUE_CONFIG[current.queue].label} queue.`);
      current = null;
    } else if (Number.isFinite(current.sliceRemaining) && current.sliceRemaining === 0) {
      queues[current.queue].push(current);
      appendEvent(events, time + 1, `${current.name} rotated inside the ${QUEUE_CONFIG[current.queue].label} queue.`);
      current = null;
    }

    time += 1;
  }

  return finalizeResult("mlq", processes, ticks, events);
}

function highestMlfqReady(queues) {
  return queues.findIndex((queue) => queue.length > 0);
}

function promoteAgedMlfqProcesses(queues, time, agingThreshold, events) {
  for (let level = 1; level < queues.length; level += 1) {
    for (let index = 0; index < queues[level].length; ) {
      const process = queues[level][index];
      if (time - process.lastQueuedAt >= agingThreshold) {
        queues[level].splice(index, 1);
        process.mlfqLevel -= 1;
        process.sliceRemaining = null;
        process.lastQueuedAt = time;
        queues[level - 1].push(process);
        appendEvent(events, time, `${process.name} was promoted to Q${process.mlfqLevel} through aging.`);
        continue;
      }
      index += 1;
    }
  }
}

function runMlfq(inputProcesses, settings) {
  const processes = cloneProcesses(inputProcesses);
  const quantums = settings.mlfqQuantums;
  const agingThreshold = Math.max(2, Number(settings.mlfqAgingThreshold) || DEFAULT_SETTINGS.mlfqAgingThreshold);
  const queues = [[], [], []];
  const ticks = [];
  const events = [];
  let current = null;
  let time = 0;
  let completed = 0;

  while (completed < processes.length && time < 10000) {
    enqueueArrivals(processes, time, (process) => {
      process.mlfqLevel = 0;
      process.sliceRemaining = null;
      queues[0].push(process);
      appendEvent(events, time, `${process.name} entered Q0.`);
    });

    promoteAgedMlfqProcesses(queues, time, agingThreshold, events);

    const highestReadyLevel = highestMlfqReady(queues);
    if (current && highestReadyLevel !== -1 && highestReadyLevel < current.mlfqLevel) {
      current.lastQueuedAt = time;
      queues[current.mlfqLevel].push(current);
      appendEvent(events, time, `${current.name} was preempted by a higher MLFQ queue.`, "warning");
      current = null;
    }

    if (!current && highestReadyLevel !== -1) {
      current = queues[highestReadyLevel].shift();
      if (!Number.isFinite(current.sliceRemaining) || current.sliceRemaining === null || current.sliceRemaining <= 0) {
        current.sliceRemaining = quantums[current.mlfqLevel];
      }
    }

    const memory = calculateMemorySnapshot(getActiveProcesses(processes, time), settings);

    if (!current) {
      ticks.push(makeTick({ time, runningProcess: null, algorithm: "mlfq", queueLabel: "Idle", note: "No ready process", memory }));
      time += 1;
      continue;
    }

    if (current.start === null) {
      current.start = time;
    }

    current.remaining -= 1;
    current.sliceRemaining -= 1;
    updateFeedback(processes, current);
    ticks.push(
      makeTick({
        time,
        runningProcess: current,
        algorithm: "mlfq",
        queueLabel: `Q${current.mlfqLevel}`,
        note: `Feedback slice left: ${current.sliceRemaining}`,
        memory,
      })
    );

    if (current.remaining === 0) {
      current.completion = time + 1;
      completed += 1;
      appendEvent(events, time + 1, `${current.name} completed from Q${current.mlfqLevel}.`);
      current.sliceRemaining = null;
      current = null;
    } else if (current.sliceRemaining === 0) {
      const previousLevel = current.mlfqLevel;
      current.mlfqLevel = Math.min(queues.length - 1, current.mlfqLevel + 1);
      current.lastQueuedAt = time + 1;
      current.sliceRemaining = null;
      queues[current.mlfqLevel].push(current);
      if (current.mlfqLevel !== previousLevel) {
        appendEvent(events, time + 1, `${current.name} used its slice and was demoted to Q${current.mlfqLevel}.`);
      } else {
        appendEvent(events, time + 1, `${current.name} stayed in the lowest queue after using its slice.`);
      }
      current = null;
    }

    time += 1;
  }

  return finalizeResult("mlfq", processes, ticks, events);
}

function adaptiveScore(process, memory) {
  const qosProfile = QOS_CONFIG[process.qos];
  const baseScore = qosProfile.weight + (11 - process.priority) * 4;
  const waitBoost = Math.min(36, process.waitTicks * 3);
  const cpuPenalty = process.recentCpu * 7 + process.runStreak * 2.5;
  const memoryPenalty = memory.pressureScore === 0
    ? 0
    : (memory.pressure === "critical" ? 12 : 5) * qosProfile.pressureBias + (process.memory / 64) * qosProfile.pressureBias * memory.pressureScore;
  const pressureBonus = memory.pressure !== "critical"
    ? 0
    : process.qos === "userInteractive" || process.qos === "userInitiated"
      ? 12
      : 0;

  return baseScore + waitBoost + pressureBonus - cpuPenalty - memoryPenalty;
}

function chooseAdaptiveProcess(processes, memory) {
  const eligible = processes.filter((process) => process.arrived && process.remaining > 0);
  if (eligible.length === 0) {
    return null;
  }

  eligible.forEach((process) => {
    process.score = adaptiveScore(process, memory);
  });

  return eligible.sort((left, right) => {
    if (right.score !== left.score) {
      return right.score - left.score;
    }
    if (left.arrival !== right.arrival) {
      return left.arrival - right.arrival;
    }
    return left.id.localeCompare(right.id);
  })[0];
}

function runMacosAdaptive(inputProcesses, settings) {
  const processes = cloneProcesses(inputProcesses);
  const ticks = [];
  const events = [];
  let current = null;
  let time = 0;
  let completed = 0;
  let lastPressure = "normal";

  while (completed < processes.length && time < 10000) {
    enqueueArrivals(processes, time, (process) => {
      appendEvent(events, time, `${process.name} arrived with ${QOS_CONFIG[process.qos].label} QoS.`);
    });

    const active = getActiveProcesses(processes, time);
    const memory = calculateMemorySnapshot(active, settings);

    if (memory.pressure !== lastPressure) {
      if (memory.pressure === "warning") {
        appendEvent(events, time, "Memory pressure entered warning mode; compression is increasing.", "warning");
      } else if (memory.pressure === "critical") {
        appendEvent(events, time, "Memory pressure entered critical mode; background workloads are being reclaimed.", "warning");
      } else {
        appendEvent(events, time, "Memory pressure returned to normal.");
      }
      lastPressure = memory.pressure;
    }

    const bestProcess = chooseAdaptiveProcess(processes, memory);

    if (current && current.remaining > 0) {
      current.score = adaptiveScore(current, memory);
      const shouldPreemptForSlice = current.sliceRemaining !== null && current.sliceRemaining <= 0;
      const shouldPreemptForPriority = bestProcess && bestProcess.id !== current.id && bestProcess.score > current.score + 5;

      if (shouldPreemptForSlice || shouldPreemptForPriority) {
        appendEvent(
          events,
          time,
          shouldPreemptForSlice
            ? `${current.name} yielded after finishing its QoS time slice.`
            : `${current.name} was preempted by ${bestProcess.name} because adaptive priority shifted.`,
          "warning"
        );
        current.sliceRemaining = null;
        current = null;
      }
    }

    if (!current && bestProcess) {
      current = bestProcess;
      if (current.sliceRemaining === null) {
        current.sliceRemaining = QOS_CONFIG[current.qos].quantum;
      }
    }

    if (!current) {
      ticks.push(
        makeTick({
          time,
          runningProcess: null,
          algorithm: "macosAdaptive",
          queueLabel: "Idle",
          note: "Scheduler waiting for work",
          memory,
        })
      );
      time += 1;
      continue;
    }

    if (current.start === null) {
      current.start = time;
    }

    current.score = adaptiveScore(current, memory);
    current.remaining -= 1;
    current.sliceRemaining -= 1;
    updateFeedback(processes, current);

    const noteParts = [
      `${QOS_CONFIG[current.qos].label} QoS`,
      `Adaptive score ${current.score.toFixed(1)}`,
    ];

    if (memory.pressure === "warning") {
      noteParts.push("memory compression active");
    }
    if (memory.pressure === "critical") {
      noteParts.push("background reclaim active");
    }

    ticks.push(
      makeTick({
        time,
        runningProcess: current,
        algorithm: "macosAdaptive",
        queueLabel: `${QOS_CONFIG[current.qos].label} lane`,
        note: noteParts.join(" | "),
        memory,
      })
    );

    if (current.remaining === 0) {
      current.completion = time + 1;
      completed += 1;
      appendEvent(events, time + 1, `${current.name} completed under the adaptive scheduler.`);
      current.sliceRemaining = null;
      current = null;
    }

    time += 1;
  }

  return finalizeResult("macosAdaptive", processes, ticks, events);
}

export function simulateSchedule(algorithmKey, processes, settings = {}) {
  const mergedSettings = mergeSettings(settings);
  const safeProcesses = Array.isArray(processes) && processes.length > 0 ? processes : DEMO_PROCESSES;

  switch (algorithmKey) {
    case "fcfs":
      return runFcfs(safeProcesses, mergedSettings);
    case "roundRobin":
      return runRoundRobin(safeProcesses, mergedSettings);
    case "priorityRoundRobin":
      return runPriorityRoundRobin(safeProcesses, mergedSettings);
    case "mlq":
      return runMlq(safeProcesses, mergedSettings);
    case "mlfq":
      return runMlfq(safeProcesses, mergedSettings);
    case "macosAdaptive":
      return runMacosAdaptive(safeProcesses, mergedSettings);
    default:
      return runMacosAdaptive(safeProcesses, mergedSettings);
  }
}

export function simulateAll(processes, settings = {}) {
  return Object.keys(ALGORITHM_DETAILS).map((algorithmKey) => simulateSchedule(algorithmKey, processes, settings));
}
