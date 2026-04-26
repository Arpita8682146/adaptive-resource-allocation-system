import { DEMO_PROCESSES, DEFAULT_SETTINGS } from "./algorithms.js";

const PROCESS_KEY = "adaptive-resource-lab-processes";
const SETTINGS_KEY = "adaptive-resource-lab-settings";
const LAST_RUN_KEY = "adaptive-resource-lab-last-run";

function readJson(key, fallback) {
  try {
    const value = window.localStorage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch (error) {
    return fallback;
  }
}

function writeJson(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    // Ignore storage write errors so the simulator still works in private browsing or locked-down environments.
  }
}

export function loadProcesses() {
  return readJson(PROCESS_KEY, DEMO_PROCESSES);
}

export function saveProcesses(processes) {
  writeJson(PROCESS_KEY, processes);
}

export function clearProcesses() {
  writeJson(PROCESS_KEY, DEMO_PROCESSES);
}

export function loadSettings() {
  return readJson(SETTINGS_KEY, DEFAULT_SETTINGS);
}

export function saveSettings(settings) {
  writeJson(SETTINGS_KEY, settings);
}

export function loadLastRun() {
  return readJson(LAST_RUN_KEY, null);
}

export function saveLastRun(payload) {
  writeJson(LAST_RUN_KEY, payload);
}
