import json
import os
import subprocess
import sys
from copy import deepcopy

import pandas as pd
import psutil

DEFAULT_USERS = {"admin": "1234", "user1": "pass1", "user2": "pass2"}
DEFAULT_SESSION_STATE = {
    "logged_in": False,
    "user": "",
    "cpu_history": [],
    "mem_history": [],
    "boosted_pids": set(),
    "stopped_pids": set(),
    "killed_pids": set(),
    "stress_pid": None,
}
PROCESS_COLUMNS = ["pid", "name", "cpu_percent", "memory_percent", "status"]


def load_users(file_path=None):
    creds = DEFAULT_USERS.copy()
    path = file_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")

    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            for username, password in data.items():
                creds[str(username).strip()] = str(password).strip()
    except (OSError, TypeError, ValueError):
        pass

    return creds


def ensure_session_state(session_state):
    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in session_state:
            session_state[key] = deepcopy(value)


def compute_health(cpu, mem):
    return round(max(0.0, 100 - (cpu * 0.5 + mem * 0.5)), 2)


def build_process_dataframe():
    process_rows = []

    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            info = proc.info
            process_rows.append(
                {
                    "pid": int(info["pid"]),
                    "name": info.get("name") or "Unknown",
                    "cpu_percent": round(float(info.get("cpu_percent") or 0.0), 2),
                    "memory_percent": round(float(info.get("memory_percent") or 0.0), 2),
                    "status": info.get("status") or "unknown",
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if not process_rows:
        return pd.DataFrame(columns=PROCESS_COLUMNS)

    return pd.DataFrame(process_rows).sort_values(
        ["cpu_percent", "memory_percent"], ascending=[False, False]
    ).reset_index(drop=True)


def _coerce_pid(pid):
    return int(pid or 0)


def suspend_process(pid):
    try:
        pid = _coerce_pid(pid)
        psutil.Process(pid).suspend()
        return True, f"Stopped PID {pid}"
    except (ValueError, TypeError):
        return False, "Enter a valid PID"
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return False, f"PID {pid} does not exist"
    except psutil.AccessDenied:
        return False, f"Permission denied while stopping PID {pid}"
    except Exception as exc:
        return False, f"Unable to stop PID {pid}: {exc}"


def resume_process(pid):
    try:
        pid = _coerce_pid(pid)
        psutil.Process(pid).resume()
        return True, f"Started PID {pid}"
    except (ValueError, TypeError):
        return False, "Enter a valid PID"
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return False, f"PID {pid} does not exist"
    except psutil.AccessDenied:
        return False, f"Permission denied while starting PID {pid}"
    except Exception as exc:
        return False, f"Unable to start PID {pid}: {exc}"


def kill_process(pid):
    try:
        pid = _coerce_pid(pid)
        psutil.Process(pid).terminate()
        return True, f"Terminated PID {pid}"
    except (ValueError, TypeError):
        return False, "Enter a valid PID"
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return False, f"PID {pid} does not exist"
    except psutil.AccessDenied:
        return False, f"Permission denied while terminating PID {pid}"
    except Exception as exc:
        return False, f"Unable to terminate PID {pid}: {exc}"


def boost_process(pid):
    try:
        pid = _coerce_pid(pid)
        proc = psutil.Process(pid)
        if os.name == "nt":
            proc.nice(psutil.HIGH_PRIORITY_CLASS)
        else:
            proc.nice(max(-10, proc.nice() - 5))
        return True, f"Boosted PID {pid}"
    except (ValueError, TypeError):
        return False, "Enter a valid PID"
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return False, f"PID {pid} does not exist"
    except psutil.AccessDenied:
        return False, f"Permission denied while boosting PID {pid}"
    except Exception as exc:
        return False, f"Unable to boost PID {pid}: {exc}"


def adjust_resources(processes, cpu_threshold=5.0, unix_nice_level=10):
    adjustments = []

    for process in processes:
        pid = _coerce_pid(process.get("pid"))
        if pid <= 0:
            continue

        try:
            proc = psutil.Process(pid)
            name = process.get("name") or proc.name()
            cpu_percent = round(float(process.get("cpu_percent") or 0.0), 2)

            if cpu_percent < cpu_threshold:
                adjustments.append(
                    {
                        "pid": pid,
                        "name": name,
                        "status": "skipped",
                        "action": "monitor",
                        "detail": "CPU below optimization threshold",
                    }
                )
                continue

            if os.name == "nt":
                target_nice = psutil.BELOW_NORMAL_PRIORITY_CLASS
            else:
                target_nice = max(proc.nice(), unix_nice_level)

            if proc.nice() == target_nice:
                adjustments.append(
                    {
                        "pid": pid,
                        "name": name,
                        "status": "skipped",
                        "action": "throttle",
                        "detail": "Process already running with reduced priority",
                    }
                )
                continue

            proc.nice(target_nice)
            adjustments.append(
                {
                    "pid": pid,
                    "name": name,
                    "status": "updated",
                    "action": "throttle",
                    "detail": f"Reduced priority to relieve CPU pressure ({cpu_percent}% CPU)",
                }
            )
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            adjustments.append(
                {
                    "pid": pid,
                    "name": process.get("name") or "Unknown",
                    "status": "skipped",
                    "action": "monitor",
                    "detail": "Process exited before optimization ran",
                }
            )
        except psutil.AccessDenied:
            adjustments.append(
                {
                    "pid": pid,
                    "name": process.get("name") or "Unknown",
                    "status": "blocked",
                    "action": "throttle",
                    "detail": "Permission denied while changing priority",
                }
            )

    return adjustments


def get_stress_script_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "stress.py")


def is_pid_active(pid):
    try:
        pid = _coerce_pid(pid)
        return pid > 0 and psutil.pid_exists(pid) and psutil.Process(pid).is_running()
    except (psutil.NoSuchProcess, psutil.ZombieProcess, ValueError, TypeError):
        return False


def start_stress_test():
    script_path = get_stress_script_path()
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return process.pid


def stop_stress_test(pid):
    return kill_process(pid)
