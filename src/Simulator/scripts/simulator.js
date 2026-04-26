import {
  ALGORITHM_DETAILS,
  DEFAULT_SETTINGS,
  DEMO_PROCESSES,
  QOS_CONFIG,
  QUEUE_CONFIG,
  simulateSchedule,
} from "./algorithms.js";
import { loadProcesses, loadSettings, saveLastRun, saveProcesses, saveSettings } from "./data-store.js";

const state = {
  processes: [],
  settings: DEFAULT_SETTINGS,
  selectedAlgorithm: "macosAdaptive",
  result: null,
};

function formatNumber(value) {
  return Number.isFinite(value) ? value.toFixed(value >= 10 ? 1 : 2) : "0";
}

function processColor(processId) {
  if (processId === "idle") {
    return "#576178";
  }

  let hash = 0;
  for (const character of processId) {
    hash = character.charCodeAt(0) + ((hash << 5) - hash);
  }

  const hue = Math.abs(hash) % 360;
  return `hsl(${hue} 70% 58%)`;
}

function syncSettingsFromInputs() {
  state.settings = {
    roundRobinQuantum: Math.max(1, Number(document.getElementById("rrQuantumInput").value) || DEFAULT_SETTINGS.roundRobinQuantum),
    priorityQuantum: Math.max(1, Number(document.getElementById("priorityQuantumInput").value) || DEFAULT_SETTINGS.priorityQuantum),
    memoryCapacity: Math.max(256, Number(document.getElementById("memoryCapacityInput").value) || DEFAULT_SETTINGS.memoryCapacity),
    memoryWarningThreshold: DEFAULT_SETTINGS.memoryWarningThreshold,
    memoryCriticalThreshold: DEFAULT_SETTINGS.memoryCriticalThreshold,
    mlqQuantums: {
      system: Math.max(1, Number(document.getElementById("mlqSystemInput").value) || DEFAULT_SETTINGS.mlqQuantums.system),
      interactive: Math.max(1, Number(document.getElementById("mlqInteractiveInput").value) || DEFAULT_SETTINGS.mlqQuantums.interactive),
      batch: Math.max(1, Number(document.getElementById("mlqBatchInput").value) || DEFAULT_SETTINGS.mlqQuantums.batch),
      background: Number.POSITIVE_INFINITY,
    },
    mlfqQuantums: [
      Math.max(1, Number(document.getElementById("mlfqQ0Input").value) || DEFAULT_SETTINGS.mlfqQuantums[0]),
      Math.max(1, Number(document.getElementById("mlfqQ1Input").value) || DEFAULT_SETTINGS.mlfqQuantums[1]),
      Math.max(1, Number(document.getElementById("mlfqQ2Input").value) || DEFAULT_SETTINGS.mlfqQuantums[2]),
    ],
    mlfqAgingThreshold: Math.max(2, Number(document.getElementById("mlfqAgingInput").value) || DEFAULT_SETTINGS.mlfqAgingThreshold),
  };

  saveSettings(state.settings);
}

function populateSettings(settings) {
  document.getElementById("rrQuantumInput").value = settings.roundRobinQuantum;
  document.getElementById("priorityQuantumInput").value = settings.priorityQuantum;
  document.getElementById("memoryCapacityInput").value = settings.memoryCapacity;
  document.getElementById("mlqSystemInput").value = settings.mlqQuantums.system;
  document.getElementById("mlqInteractiveInput").value = settings.mlqQuantums.interactive;
  document.getElementById("mlqBatchInput").value = settings.mlqQuantums.batch;
  document.getElementById("mlfqQ0Input").value = settings.mlfqQuantums[0];
  document.getElementById("mlfqQ1Input").value = settings.mlfqQuantums[1];
  document.getElementById("mlfqQ2Input").value = settings.mlfqQuantums[2];
  document.getElementById("mlfqAgingInput").value = settings.mlfqAgingThreshold;
}

function renderAlgorithmMenu() {
  const select = document.getElementById("algorithmSelect");
  select.innerHTML = Object.entries(ALGORITHM_DETAILS)
    .map(
      ([key, value]) => `
        <option value="${key}" ${state.selectedAlgorithm === key ? "selected" : ""}>${value.label}</option>
      `
    )
    .join("");
}

function renderAlgorithmDescription() {
  const detail = ALGORITHM_DETAILS[state.selectedAlgorithm];
  const description = document.getElementById("algorithmDescription");
  description.innerHTML = `
    <div class="algorithm-detail" style="--algorithm-accent: ${detail.accent}">
      <span class="pill">${detail.label}</span>
      <p>${detail.description}</p>
    </div>
  `;

  document.querySelectorAll("[data-settings-group]").forEach((section) => {
    const groups = (section.dataset.settingsGroup || "").split(",");
    const shouldShow = groups.includes("all") || groups.includes(state.selectedAlgorithm);
    section.hidden = !shouldShow;
  });
}

function renderProcessTable() {
  const tbody = document.getElementById("processTableBody");
  const count = document.getElementById("processCount");

  count.textContent = `${state.processes.length} process${state.processes.length === 1 ? "" : "es"}`;

  if (state.processes.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="table-empty">No processes configured yet. Add one manually or load the demo workload.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = state.processes
    .map(
      (process) => `
        <tr>
          <td><span class="process-chip" style="--chip-color: ${processColor(process.id)}">${process.id}</span></td>
          <td>${process.name}</td>
          <td>${process.arrival}</td>
          <td>${process.burst}</td>
          <td>${process.priority}</td>
          <td>${QUEUE_CONFIG[process.queue].label}</td>
          <td>${QOS_CONFIG[process.qos].label}</td>
          <td>${process.memory} MB</td>
          <td><button class="ghost-button" data-remove-process="${process.id}">Remove</button></td>
        </tr>
      `
    )
    .join("");
}

function renderSummary(result) {
  const summaryRoot = document.getElementById("summaryCards");
  if (!result) {
    summaryRoot.innerHTML = `
      <article class="stat-card">
        <span class="eyebrow">Simulation Status</span>
        <strong>Waiting to run</strong>
        <p>Choose an algorithm and execute the configured workload to populate the analysis panels.</p>
      </article>
    `;
    return;
  }

  summaryRoot.innerHTML = `
    <article class="stat-card">
      <span class="eyebrow">Algorithm</span>
      <strong>${result.label}</strong>
      <p>${result.description}</p>
    </article>
    <article class="stat-card">
      <span class="eyebrow">Average Waiting</span>
      <strong>${formatNumber(result.summary.avgWaiting)} ticks</strong>
      <p>Average time processes spent queued.</p>
    </article>
    <article class="stat-card">
      <span class="eyebrow">Average Response</span>
      <strong>${formatNumber(result.summary.avgResponse)} ticks</strong>
      <p>How quickly the scheduler first touched each process.</p>
    </article>
    <article class="stat-card">
      <span class="eyebrow">Critical Pressure Moments</span>
      <strong>${result.summary.memoryCriticalMoments}</strong>
      <p>${Math.round(result.summary.reclaimedMemory)} MB reclaimed across the run.</p>
    </article>
  `;
}

function renderTimeline(result) {
  const root = document.getElementById("ganttTimeline");
  if (!result) {
    root.innerHTML = `<div class="empty-panel">Run a workload to generate the Gantt timeline.</div>`;
    return;
  }

  const scale = document.getElementById("timelineScale");
  const total = Math.max(1, result.summary.makespan);
  scale.innerHTML = Array.from({ length: total + 1 }, (_, index) => `<span>${index}</span>`).join("");

  root.innerHTML = result.timeline
    .map((segment) => {
      const duration = segment.end - segment.start;
      return `
        <article
          class="timeline-segment ${segment.processId === "idle" ? "is-idle" : ""} pressure-${segment.memory.pressure}"
          style="--segment-width: ${Math.max(76, duration * 42)}px; --segment-color: ${processColor(segment.processId)}"
          title="${segment.name} | ${segment.start}-${segment.end} | ${segment.note}"
        >
          <span class="segment-name">${segment.name}</span>
          <strong>${segment.start} - ${segment.end}</strong>
          <small>${segment.queueLabel}</small>
        </article>
      `;
    })
    .join("");
}

function renderMetrics(result) {
  const tbody = document.getElementById("metricsTableBody");
  if (!result) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="table-empty">Per-process metrics will appear here after the first simulation run.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = result.metrics
    .map(
      (metric) => `
        <tr>
          <td>${metric.id}</td>
          <td>${metric.name}</td>
          <td>${metric.waiting}</td>
          <td>${metric.response}</td>
          <td>${metric.turnaround}</td>
          <td>${metric.completion}</td>
          <td>${QUEUE_CONFIG[metric.queue].label}</td>
          <td>${QOS_CONFIG[metric.qos].label}</td>
        </tr>
      `
    )
    .join("");
}

function renderMemoryChart(result) {
  const root = document.getElementById("memoryChart");
  if (!result) {
    root.innerHTML = `<div class="empty-panel">Memory pressure bars will appear after a simulation run.</div>`;
    return;
  }

  root.innerHTML = result.memoryTimeline
    .map((point) => {
      const height = point.capacity === 0 ? 0 : (point.effectiveUsed / point.capacity) * 100;
      return `
        <div class="memory-bar pressure-${point.pressure}" title="t=${point.time}, used=${Math.round(point.effectiveUsed)} MB, reclaimed=${Math.round(point.reclaimed)} MB">
          <span style="height: ${Math.min(100, Math.max(8, height))}%"></span>
          <small>${point.time}</small>
        </div>
      `;
    })
    .join("");
}

function renderEvents(result) {
  const root = document.getElementById("eventLog");
  if (!result) {
    root.innerHTML = `<div class="empty-panel">Queue changes, promotions, and pressure events will appear here.</div>`;
    return;
  }

  root.innerHTML = result.events
    .slice(-18)
    .reverse()
    .map(
      (event) => `
        <article class="event-row event-${event.tone}">
          <span>T+${event.time}</span>
          <p>${event.message}</p>
        </article>
      `
    )
    .join("");
}

function renderResult(result) {
  renderSummary(result);
  renderTimeline(result);
  renderMetrics(result);
  renderMemoryChart(result);
  renderEvents(result);
}

function persistProcesses() {
  saveProcesses(state.processes);
}

function nextProcessId() {
  const nextIndex = state.processes.length + 1;
  let candidate = `P${nextIndex}`;

  while (state.processes.some((process) => process.id === candidate)) {
    candidate = `P${Math.floor(Math.random() * 900) + 100}`;
  }

  return candidate;
}

function addProcessFromForm(event) {
  event.preventDefault();

  const nameInput = document.getElementById("nameInput");
  const arrivalInput = document.getElementById("arrivalInput");
  const burstInput = document.getElementById("burstInput");
  const priorityInput = document.getElementById("priorityInput");
  const queueInput = document.getElementById("queueInput");
  const qosInput = document.getElementById("qosInput");
  const memoryInput = document.getElementById("memoryInput");

  const process = {
    id: nextProcessId(),
    name: nameInput.value.trim() || `Process ${state.processes.length + 1}`,
    arrival: Math.max(0, Number(arrivalInput.value) || 0),
    burst: Math.max(1, Number(burstInput.value) || 1),
    priority: Math.min(10, Math.max(1, Number(priorityInput.value) || 5)),
    queue: queueInput.value,
    qos: qosInput.value,
    memory: Math.max(64, Number(memoryInput.value) || 128),
  };

  state.processes = [...state.processes, process].sort((left, right) => left.arrival - right.arrival || left.id.localeCompare(right.id));
  persistProcesses();
  renderProcessTable();
  event.target.reset();
  arrivalInput.value = 0;
  burstInput.value = 4;
  priorityInput.value = 5;
  queueInput.value = "interactive";
  qosInput.value = "default";
  memoryInput.value = 256;
}

function removeProcess(processId) {
  state.processes = state.processes.filter((process) => process.id !== processId);
  persistProcesses();
  renderProcessTable();
}

function runSimulation() {
  syncSettingsFromInputs();
  state.result = simulateSchedule(state.selectedAlgorithm, state.processes, state.settings);
  renderResult(state.result);
  saveLastRun({
    label: state.result.label,
    description: state.result.description,
    summary: state.result.summary,
  });
}

function attachEvents() {
  document.getElementById("processForm").addEventListener("submit", addProcessFromForm);

  document.getElementById("algorithmSelect").addEventListener("change", (event) => {
    state.selectedAlgorithm = event.target.value;
    renderAlgorithmDescription();
  });

  document.getElementById("runButton").addEventListener("click", runSimulation);

  document.getElementById("loadDemoButton").addEventListener("click", () => {
    state.processes = [...DEMO_PROCESSES];
    persistProcesses();
    renderProcessTable();
  });

  document.getElementById("clearProcessesButton").addEventListener("click", () => {
    state.processes = [];
    persistProcesses();
    renderProcessTable();
    renderResult(null);
  });

  document.getElementById("processTableBody").addEventListener("click", (event) => {
    const target = event.target.closest("[data-remove-process]");
    if (!target) {
      return;
    }

    removeProcess(target.dataset.removeProcess);
  });

  document.querySelectorAll(".settings-panel input").forEach((input) => {
    input.addEventListener("change", syncSettingsFromInputs);
  });
}

function initSimulator() {
  state.processes = loadProcesses();
  state.settings = loadSettings();
  renderAlgorithmMenu();
  populateSettings(state.settings);
  renderAlgorithmDescription();
  renderProcessTable();
  renderResult(null);
  attachEvents();
}

document.addEventListener("DOMContentLoaded", initSimulator);
