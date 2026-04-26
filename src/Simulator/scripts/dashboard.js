import { ALGORITHM_DETAILS, DEMO_PROCESSES, QOS_CONFIG, simulateAll } from "./algorithms.js";
import { loadLastRun, loadProcesses } from "./data-store.js";

function formatNumber(value) {
  return Number.isFinite(value) ? value.toFixed(value >= 10 ? 1 : 2) : "0";
}

function renderStats(processes, results, lastRun) {
  const statsRoot = document.getElementById("dashboardStats");
  if (!statsRoot) {
    return;
  }

  const bestLatency = [...results].sort((left, right) => left.summary.avgResponse - right.summary.avgResponse)[0];
  const bestThroughput = [...results].sort((left, right) => right.summary.throughput - left.summary.throughput)[0];
  const totalMemory = processes.reduce((total, process) => total + process.memory, 0);

  const cards = [
    {
      label: "Configured Processes",
      value: `${processes.length}`,
      helper: "Persisted locally for the simulator page",
    },
    {
      label: "Best Response Time",
      value: `${formatNumber(bestLatency.summary.avgResponse)} ticks`,
      helper: bestLatency.label,
    },
    {
      label: "Best Throughput",
      value: `${formatNumber(bestThroughput.summary.throughput)}`,
      helper: `${bestThroughput.label} processes/tick`,
    },
    {
      label: "Working Set Memory",
      value: `${totalMemory} MB`,
      helper: lastRun ? `Last run: ${lastRun.label}` : "No simulation has been run yet",
    },
  ];

  statsRoot.innerHTML = cards
    .map(
      (card) => `
        <article class="stat-card">
          <span class="eyebrow">${card.label}</span>
          <strong>${card.value}</strong>
          <p>${card.helper}</p>
        </article>
      `
    )
    .join("");
}

function renderAlgorithmCards(results) {
  const root = document.getElementById("algorithmCards");
  if (!root) {
    return;
  }

  root.innerHTML = results
    .map(
      (result) => `
        <article class="algorithm-card" style="--algorithm-accent: ${result.accent}">
          <div class="algorithm-card__header">
            <span class="pill">${result.label}</span>
            <span class="muted">${result.summary.makespan} ticks</span>
          </div>
          <h3>${result.label}</h3>
          <p>${result.description}</p>
          <dl class="metric-grid">
            <div>
              <dt>Avg wait</dt>
              <dd>${formatNumber(result.summary.avgWaiting)}</dd>
            </div>
            <div>
              <dt>Avg response</dt>
              <dd>${formatNumber(result.summary.avgResponse)}</dd>
            </div>
            <div>
              <dt>CPU use</dt>
              <dd>${formatNumber(result.summary.cpuUtilization)}%</dd>
            </div>
            <div>
              <dt>Pressure hits</dt>
              <dd>${result.summary.memoryCriticalMoments}</dd>
            </div>
          </dl>
        </article>
      `
    )
    .join("");
}

function renderComparison(results) {
  const root = document.getElementById("comparisonBody");
  if (!root) {
    return;
  }

  const lowestWait = Math.min(...results.map((result) => result.summary.avgWaiting));
  const lowestResponse = Math.min(...results.map((result) => result.summary.avgResponse));
  const highestFairness = Math.max(...results.map((result) => result.summary.fairness));

  root.innerHTML = results
    .map((result) => {
      const waitClass = result.summary.avgWaiting === lowestWait ? "is-best" : "";
      const responseClass = result.summary.avgResponse === lowestResponse ? "is-best" : "";
      const fairnessClass = result.summary.fairness === highestFairness ? "is-best" : "";

      return `
        <tr>
          <td>
            <span class="table-label" style="--algorithm-accent: ${result.accent}">${result.label}</span>
          </td>
          <td class="${waitClass}">${formatNumber(result.summary.avgWaiting)}</td>
          <td class="${responseClass}">${formatNumber(result.summary.avgResponse)}</td>
          <td>${formatNumber(result.summary.throughput)}</td>
          <td class="${fairnessClass}">${formatNumber(result.summary.fairness)}%</td>
          <td>${result.summary.memoryCriticalMoments}</td>
        </tr>
      `;
    })
    .join("");
}

function renderLastRun(lastRun) {
  const root = document.getElementById("lastRunPanel");
  if (!root) {
    return;
  }

  if (!lastRun) {
    root.innerHTML = `
      <div class="insight-card">
        <span class="eyebrow">Last Simulation</span>
        <h3>No run stored yet</h3>
        <p>Open the simulator page, choose an algorithm, and run a workload. This dashboard will refresh with the latest results automatically.</p>
      </div>
    `;
    return;
  }

  root.innerHTML = `
    <div class="insight-card">
      <span class="eyebrow">Last Simulation</span>
      <h3>${lastRun.label}</h3>
      <p>${lastRun.description}</p>
      <div class="insight-row">
        <span>Average waiting time</span>
        <strong>${formatNumber(lastRun.summary.avgWaiting)} ticks</strong>
      </div>
      <div class="insight-row">
        <span>Average response time</span>
        <strong>${formatNumber(lastRun.summary.avgResponse)} ticks</strong>
      </div>
      <div class="insight-row">
        <span>Critical memory moments</span>
        <strong>${lastRun.summary.memoryCriticalMoments}</strong>
      </div>
    </div>
  `;
}

function renderWorkloadProfile(processes) {
  const root = document.getElementById("workloadProfile");
  if (!root) {
    return;
  }

  const qosCounts = Object.keys(QOS_CONFIG).map((key) => ({
    key,
    label: QOS_CONFIG[key].label,
    count: processes.filter((process) => process.qos === key).length,
  }));

  root.innerHTML = qosCounts
    .map(
      (entry) => `
        <div class="profile-row">
          <span>${entry.label}</span>
          <div class="profile-bar">
            <span style="width: ${(entry.count / Math.max(1, processes.length)) * 100}%"></span>
          </div>
          <strong>${entry.count}</strong>
        </div>
      `
    )
    .join("");
}

function initDashboard() {
  const processes = loadProcesses() || DEMO_PROCESSES;
  const results = simulateAll(processes);
  const lastRun = loadLastRun();

  renderStats(processes, results, lastRun);
  renderAlgorithmCards(results);
  renderComparison(results);
  renderLastRun(lastRun);
  renderWorkloadProfile(processes);

  const launchButtons = document.querySelectorAll("[data-launch-simulator]");
  launchButtons.forEach((button) => {
    button.addEventListener("click", () => {
      window.location.href = "./simulator.html";
    });
  });
}

document.addEventListener("DOMContentLoaded", initDashboard);
