from utils import adjust_resources


def _metric(process, key):
    try:
        return float(process.get(key) or 0.0)
    except (AttributeError, TypeError, ValueError):
        return 0.0


def _recommendation(icon, title, description, severity):
    return {
        "icon": icon,
        "title": title,
        "description": description,
        "severity": severity,
    }


def apply_priority_aging(processes):
    aged_processes = []

    for process in processes:
        status = str(process.get("status") or "unknown").lower()
        cpu_percent = _metric(process, "cpu_percent")
        memory_percent = _metric(process, "memory_percent")

        wait_bonus = 18 if status in {"sleeping", "idle", "disk-sleep"} else 10 if status == "stopped" else 0
        adaptive_priority = round(max(0.0, 100.0 - cpu_percent - memory_percent + wait_bonus), 2)
        aged_processes.append({**process, "adaptive_priority": adaptive_priority})

    return sorted(aged_processes, key=lambda item: item["adaptive_priority"], reverse=True)


def apply_adaptive_logic(
    cpu_usage,
    memory_usage,
    processes,
    auto_optimize=False,
    cpu_threshold=80,
    memory_threshold=85,
    anomaly_detected=False,
):
    aged_processes = apply_priority_aging(processes)
    top_cpu_processes = sorted(processes, key=lambda item: _metric(item, "cpu_percent"), reverse=True)
    top_memory_processes = sorted(processes, key=lambda item: _metric(item, "memory_percent"), reverse=True)
    recommendations = []
    actions = []

    if cpu_usage > cpu_threshold:
        lead_process = top_cpu_processes[0] if top_cpu_processes else None
        if lead_process:
            recommendations.append(
                _recommendation(
                    "🔴",
                    "Critical CPU Load",
                    f"PID {lead_process['pid']} ({lead_process.get('name', 'Unknown')}) is leading CPU usage at {_metric(lead_process, 'cpu_percent'):.1f}%.",
                    "danger",
                )
            )
        else:
            recommendations.append(
                _recommendation(
                    "🔴",
                    "Critical CPU Load",
                    "CPU usage is above the configured threshold. Inspect the heaviest processes now.",
                    "danger",
                )
            )
    elif cpu_usage > cpu_threshold * 0.75:
        recommendations.append(
            _recommendation(
                "🟠",
                "Elevated CPU Usage",
                f"CPU usage is at {cpu_usage}%. Prepare to reprioritize heavy workloads.",
                "warning",
            )
        )
    else:
        recommendations.append(
            _recommendation(
                "🟢",
                "CPU Healthy",
                "CPU usage is within the expected operating range.",
                "success",
            )
        )

    if memory_usage > memory_threshold:
        lead_process = top_memory_processes[0] if top_memory_processes else None
        if lead_process:
            recommendations.append(
                _recommendation(
                    "🔴",
                    "Critical Memory Pressure",
                    f"PID {lead_process['pid']} ({lead_process.get('name', 'Unknown')}) is using {_metric(lead_process, 'memory_percent'):.2f}% memory.",
                    "danger",
                )
            )
        else:
            recommendations.append(
                _recommendation(
                    "🔴",
                    "Critical Memory Pressure",
                    "Memory usage is near capacity. Consider stopping memory-heavy workloads.",
                    "danger",
                )
            )
    elif memory_usage > memory_threshold * 0.8:
        recommendations.append(
            _recommendation(
                "🟠",
                "Moderate Memory Usage",
                f"Memory usage is at {memory_usage}%. Keep an eye on memory-heavy processes.",
                "warning",
            )
        )
    else:
        recommendations.append(
            _recommendation(
                "🟢",
                "Memory Healthy",
                "Memory usage is stable.",
                "success",
            )
        )

    if anomaly_detected:
        recommendations.append(
            _recommendation(
                "🔴",
                "Anomaly Detected",
                "The latest CPU reading is outside the recent baseline. Review process activity and recent changes.",
                "danger",
            )
        )

    if aged_processes:
        candidate = aged_processes[0]
        recommendations.append(
            _recommendation(
                "💡",
                "Priority Aging Candidate",
                f"PID {candidate['pid']} ({candidate.get('name', 'Unknown')}) has the best adaptive score ({candidate['adaptive_priority']}) for a manual boost.",
                "info",
            )
        )

    if auto_optimize and cpu_usage > cpu_threshold and top_cpu_processes:
        candidate_pool = [
            process
            for process in top_cpu_processes[:5]
            if str(process.get("status") or "").lower() not in {"stopped", "zombie"}
        ]
        actions = adjust_resources(candidate_pool)

        successful_actions = [action for action in actions if action["status"] == "updated"]
        blocked_actions = [action for action in actions if action["status"] == "blocked"]
        skipped_actions = [action for action in actions if action["status"] == "skipped"]

        if successful_actions:
            pid_list = ", ".join(str(action["pid"]) for action in successful_actions)
            recommendations.append(
                _recommendation(
                    "🤖",
                    "Auto Optimization Applied",
                    f"Adaptive tuning reduced priority for heavy CPU processes: {pid_list}.",
                    "info",
                )
            )
        

        elif blocked_actions:
            recommendations.append(
                _recommendation(
                    "🟡",
                    "Auto Optimization Limited",
                    "Automatic tuning was blocked by system permissions for one or more processes.",
                    "warning",
                )
            )

        elif skipped_actions:
            recommendations.append(
                _recommendation(
                    "🔵",
                    "Optimization Skipped",
                    "Processes already running at optimal priority.",
                    "info",
                )
            )

        # if successful_actions:
        #     pid_list = ", ".join(str(action["pid"]) for action in successful_actions)
        #     recommendations.append(
        #         _recommendation(
        #             "🤖",
        #             "Auto Optimization Applied",
        #             f"Adaptive tuning reduced priority for heavy CPU processes: {pid_list}.",
        #             "info",
        #         )
        #     )
        # elif blocked_actions:
        #     recommendations.append(
        #         _recommendation(
        #             "🟡",
        #             "Auto Optimization Limited",
        #             "Automatic tuning was blocked by system permissions for one or more processes.",
        #             "warning",
        #         )
        #     )

    return {
        "recommendations": recommendations,
        "actions": actions,
        "aged_processes": aged_processes,
        "top_cpu_processes": top_cpu_processes,
        "top_memory_processes": top_memory_processes,
    }
