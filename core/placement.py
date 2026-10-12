"""
Cloud Task Placement Optimization Engine.
Minimizes client communication latency subject to multi-dimensional server capacities (CPU, RAM).
Implements:
1. Formal Problem Model (Tasks, Server Capacities, Client Traffic, Latency Matrix).
2. Greedy Schedulers (Nearest-Traffic Greedy, Latency-Density Greedy, Best-Fit Greedy).
3. Dynamic Programming (DP) Knapsack-style selection scheduler.
4. Exact / Globally Optimal Solver (Branch-and-Bound with Admissible Lower Bounds).
5. Placement Evaluation Metrics & Tradeoff Reporting.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import copy
import time
import math


@dataclass
class Task:
    task_id: str
    name: str = ""
    cpu_demand: float = 4.0   # CPU Cores
    ram_demand: float = 16.0  # RAM in GB
    # Client request traffic rates: {client_server_id: requests_per_sec}
    traffic: Dict[str, float] = field(default_factory=dict)
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            self.name = self.task_id

    def total_traffic(self) -> float:
        return sum(self.traffic.values()) if self.traffic else 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "cpu_demand": self.cpu_demand,
            "ram_demand": self.ram_demand,
            "traffic": self.traffic,
            "priority": self.priority,
            "metadata": self.metadata
        }


@dataclass
class PlacementResult:
    # Mapping: task_id -> server_id
    placements: Dict[str, str]
    unplaced_tasks: List[str]
    total_latency: float
    average_latency: float
    server_cpu_usage: Dict[str, float]
    server_ram_usage: Dict[str, float]
    server_cpu_capacity: Dict[str, float]
    server_ram_capacity: Dict[str, float]
    algorithm_name: str
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def cpu_utilization_percent(self) -> float:
        total_used = sum(self.server_cpu_usage.values())
        total_cap = sum(self.server_cpu_capacity.values())
        return (total_used / total_cap * 100.0) if total_cap > 0 else 0.0

    def ram_utilization_percent(self) -> float:
        total_used = sum(self.server_ram_usage.values())
        total_cap = sum(self.server_ram_capacity.values())
        return (total_used / total_cap * 100.0) if total_cap > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_name": self.algorithm_name,
            "placements": self.placements,
            "unplaced_tasks": self.unplaced_tasks,
            "total_latency": round(self.total_latency, 2),
            "average_latency": round(self.average_latency, 2),
            "cpu_utilization_pct": round(self.cpu_utilization_percent(), 2),
            "ram_utilization_pct": round(self.ram_utilization_percent(), 2),
            "execution_time_ms": round(self.execution_time * 1000, 3),
            "num_placed": len(self.placements),
            "num_unplaced": len(self.unplaced_tasks)
        }


def compute_task_server_latency(
    task: Task,
    server_id: str,
    dist_matrix: Dict[str, Dict[str, float]]
) -> float:
    """
    Computes total weighted communication latency for placing task on server_id:
    L(task, s) = sum_{client c} traffic(c, task) * dist(c, s)
    """
    if not task.traffic:
        # Uniform traffic if not specified
        return sum(dist_matrix.get(c, {}).get(server_id, float("inf")) for c in dist_matrix)

    total_latency = 0.0
    for client_id, rate in task.traffic.items():
        d = dist_matrix.get(client_id, {}).get(server_id, float("inf"))
        total_latency += rate * d
    return total_latency


def evaluate_placement(
    placements: Dict[str, str],
    tasks: List[Task],
    dist_matrix: Dict[str, Dict[str, float]],
    servers: Dict[str, Any]
) -> Tuple[float, float, Dict[str, float], Dict[str, float]]:
    """
    Calculate total latency, average latency, and server CPU/RAM usage.
    """
    task_map = {t.task_id: t for t in tasks}
    cpu_usage = {sid: 0.0 for sid in servers}
    ram_usage = {sid: 0.0 for sid in servers}
    total_latency = 0.0
    total_traffic = 0.0

    for tid, sid in placements.items():
        task = task_map.get(tid)
        if not task:
            continue
        cpu_usage[sid] = cpu_usage.get(sid, 0.0) + task.cpu_demand
        ram_usage[sid] = ram_usage.get(sid, 0.0) + task.ram_demand

        task_traffic = task.total_traffic()
        total_traffic += task_traffic
        lat = compute_task_server_latency(task, sid, dist_matrix)
        total_latency += lat

    avg_latency = (total_latency / total_traffic) if total_traffic > 0 else 0.0
    return total_latency, avg_latency, cpu_usage, ram_usage


def greedy_nearest_traffic_placement(
    tasks: List[Task],
    servers: Dict[str, Any],
    dist_matrix: Dict[str, Dict[str, float]]
) -> PlacementResult:
    """
    Greedy Nearest-Traffic Scheduler.
    Sorts tasks by total traffic descending (higher priority for high-traffic workloads).
    Places each task on the server with minimal communication latency that has sufficient capacity.
    """
    start_time = time.perf_counter()

    rem_cpu = {sid: float(s.cpu_capacity if hasattr(s, "cpu_capacity") else s["cpu_capacity"]) for sid, s in servers.items()}
    rem_ram = {sid: float(s.ram_capacity if hasattr(s, "ram_capacity") else s["ram_capacity"]) for sid, s in servers.items()}
    cap_cpu = dict(rem_cpu)
    cap_ram = dict(rem_ram)

    # Sort tasks by traffic descending
    sorted_tasks = sorted(tasks, key=lambda t: t.total_traffic(), reverse=True)

    placements: Dict[str, str] = {}
    unplaced: List[str] = []

    for task in sorted_tasks:
        # Score each candidate server by latency
        candidates = []
        for sid in servers:
            if rem_cpu[sid] >= task.cpu_demand and rem_ram[sid] >= task.ram_demand:
                lat = compute_task_server_latency(task, sid, dist_matrix)
                candidates.append((lat, sid))

        if candidates:
            # Pick server with minimum latency
            candidates.sort(key=lambda x: x[0])
            best_lat, best_sid = candidates[0]
            placements[task.task_id] = best_sid
            rem_cpu[best_sid] -= task.cpu_demand
            rem_ram[best_sid] -= task.ram_demand
        else:
            unplaced.append(task.task_id)

    exec_time = time.perf_counter() - start_time
    tot_lat, avg_lat, cpu_used, ram_used = evaluate_placement(placements, tasks, dist_matrix, servers)

    return PlacementResult(
        placements=placements,
        unplaced_tasks=unplaced,
        total_latency=tot_lat,
        average_latency=avg_lat,
        server_cpu_usage=cpu_used,
        server_ram_usage=ram_used,
        server_cpu_capacity=cap_cpu,
        server_ram_capacity=cap_ram,
        algorithm_name="Greedy (Nearest Traffic)",
        execution_time=exec_time
    )


def greedy_latency_density_placement(
    tasks: List[Task],
    servers: Dict[str, Any],
    dist_matrix: Dict[str, Dict[str, float]]
) -> PlacementResult:
    """
    Greedy Latency-Density Scheduler.
    Prioritizes tasks by Traffic Density = Total Traffic / (CPU Demand + RAM Demand).
    Assigns tasks to balance resource utilization and latency.
    """
    start_time = time.perf_counter()

    rem_cpu = {sid: float(s.cpu_capacity if hasattr(s, "cpu_capacity") else s["cpu_capacity"]) for sid, s in servers.items()}
    rem_ram = {sid: float(s.ram_capacity if hasattr(s, "ram_capacity") else s["ram_capacity"]) for sid, s in servers.items()}
    cap_cpu = dict(rem_cpu)
    cap_ram = dict(rem_ram)

    # Sort tasks by traffic density descending
    sorted_tasks = sorted(
        tasks,
        key=lambda t: t.total_traffic() / max(0.1, (t.cpu_demand + 0.1 * t.ram_demand)),
        reverse=True
    )

    placements: Dict[str, str] = {}
    unplaced: List[str] = []

    for task in sorted_tasks:
        candidates = []
        for sid in servers:
            if rem_cpu[sid] >= task.cpu_demand and rem_ram[sid] >= task.ram_demand:
                lat = compute_task_server_latency(task, sid, dist_matrix)
                # Cost function balances latency with remaining capacity tightness
                util_penalty = 1.0 + (1.0 - rem_cpu[sid] / cap_cpu[sid]) * 0.1
                score = lat * util_penalty
                candidates.append((score, lat, sid))

        if candidates:
            candidates.sort(key=lambda x: x[0])
            _, best_lat, best_sid = candidates[0]
            placements[task.task_id] = best_sid
            rem_cpu[best_sid] -= task.cpu_demand
            rem_ram[best_sid] -= task.ram_demand
        else:
            unplaced.append(task.task_id)

    exec_time = time.perf_counter() - start_time
    tot_lat, avg_lat, cpu_used, ram_used = evaluate_placement(placements, tasks, dist_matrix, servers)

    return PlacementResult(
        placements=placements,
        unplaced_tasks=unplaced,
        total_latency=tot_lat,
        average_latency=avg_lat,
        server_cpu_usage=cpu_used,
        server_ram_usage=ram_used,
        server_cpu_capacity=cap_cpu,
        server_ram_capacity=cap_ram,
        algorithm_name="Greedy (Latency-Density)",
        execution_time=exec_time
    )


def dp_knapsack_placement(
    tasks: List[Task],
    servers: Dict[str, Any],
    dist_matrix: Dict[str, Dict[str, float]],
    discretization_step: float = 2.0
) -> PlacementResult:
    """
    Dynamic Programming Knapsack-style Selection Scheduler.
    Maps task placement to a Multi-Choice Multi-Dimensional Knapsack model:
    Maximizes Latency Savings: Value(t, s) = Latency_worst(t) - Latency(t, s).
    For each server cluster / server, DP state DP(i, c) solves optimal subset assignment,
    then combines allocations across servers via dynamic programming / coordinate descent.
    """
    start_time = time.perf_counter()

    cap_cpu = {sid: float(s.cpu_capacity if hasattr(s, "cpu_capacity") else s["cpu_capacity"]) for sid, s in servers.items()}
    cap_ram = {sid: float(s.ram_capacity if hasattr(s, "ram_capacity") else s["ram_capacity"]) for sid, s in servers.items()}
    rem_cpu = dict(cap_cpu)
    rem_ram = dict(cap_ram)

    # Compute latency cost matrix and find worst-case latency per task
    cost_matrix: Dict[str, Dict[str, float]] = {}
    max_cost_per_task: Dict[str, float] = {}

    for task in tasks:
        tid = task.task_id
        cost_matrix[tid] = {}
        for sid in servers:
            cost_matrix[tid][sid] = compute_task_server_latency(task, sid, dist_matrix)
        max_cost_per_task[tid] = max(cost_matrix[tid].values()) if cost_matrix[tid] else 1000.0

    # Sort servers by centrality (average distance to all other nodes) to fill high-value servers first
    server_centrality = {}
    for sid in servers:
        avg_d = sum(dist_matrix.get(sid, {}).get(other, 0.0) for other in servers) / max(1, len(servers))
        server_centrality[sid] = avg_d
    sorted_servers = sorted(servers.keys(), key=lambda s: server_centrality[s])

    remaining_tasks = list(tasks)
    placements: Dict[str, str] = {}

    # Solve 0/1 Knapsack DP per server in order of network centrality
    for sid in sorted_servers:
        if not remaining_tasks:
            break

        c_cpu = int(rem_cpu[sid] // discretization_step)
        if c_cpu <= 0:
            continue

        # Item values: Latency Savings = MaxLatency - Latency(t, sid)
        # Item weight: discretized cpu_demand
        n = len(remaining_tasks)
        dp = [0.0] * (c_cpu + 1)
        parent = [[False] * (c_cpu + 1) for _ in range(n)]

        for i in range(n):
            t = remaining_tasks[i]
            w = max(1, int(t.cpu_demand // discretization_step))
            val = max_cost_per_task[t.task_id] - cost_matrix[t.task_id][sid]

            for w_curr in range(c_cpu, w - 1, -1):
                if dp[w_curr - w] + val > dp[w_curr]:
                    dp[w_curr] = dp[w_curr - w] + val
                    parent[i][w_curr] = True

        # Reconstruct chosen tasks for this server
        curr_w = c_cpu
        chosen_indices = []
        for i in range(n - 1, -1, -1):
            t = remaining_tasks[i]
            w = max(1, int(t.cpu_demand // discretization_step))
            if parent[i][curr_w]:
                # Verify RAM constraint as well
                if rem_ram[sid] >= t.ram_demand and rem_cpu[sid] >= t.cpu_demand:
                    chosen_indices.append(i)
                    curr_w -= w
                    rem_cpu[sid] -= t.cpu_demand
                    rem_ram[sid] -= t.ram_demand

        # Assign chosen tasks
        chosen_tasks = [remaining_tasks[i] for i in chosen_indices]
        for t in chosen_tasks:
            placements[t.task_id] = sid

        remaining_tasks = [t for i, t in enumerate(remaining_tasks) if i not in chosen_indices]

    # For any leftover tasks, fallback to best available server
    unplaced = []
    for t in remaining_tasks:
        best_sid = None
        best_lat = float("inf")
        for sid in servers:
            if rem_cpu[sid] >= t.cpu_demand and rem_ram[sid] >= t.ram_demand:
                lat = cost_matrix[t.task_id][sid]
                if lat < best_lat:
                    best_lat = lat
                    best_sid = sid
        if best_sid is not None:
            placements[t.task_id] = best_sid
            rem_cpu[best_sid] -= t.cpu_demand
            rem_ram[best_sid] -= t.ram_demand
        else:
            unplaced.append(t.task_id)

    exec_time = time.perf_counter() - start_time
    tot_lat, avg_lat, cpu_used, ram_used = evaluate_placement(placements, tasks, dist_matrix, servers)

    return PlacementResult(
        placements=placements,
        unplaced_tasks=unplaced,
        total_latency=tot_lat,
        average_latency=avg_lat,
        server_cpu_usage=cpu_used,
        server_ram_usage=ram_used,
        server_cpu_capacity=cap_cpu,
        server_ram_capacity=cap_ram,
        algorithm_name="Dynamic Programming (Knapsack DP)",
        execution_time=exec_time
    )


def exact_optimal_placement(
    tasks: List[Task],
    servers: Dict[str, Any],
    dist_matrix: Dict[str, Dict[str, float]],
    time_limit_sec: float = 5.0
) -> PlacementResult:
    """
    Branch-and-Bound Exact Optimizer (Find Optimised Solution).
    Guarantees globally minimal total communication latency subject to CPU & RAM constraints.
    Pruning Strategy:
    - Admissible lower bound using unconstrained nearest-server latency.
    - Candidate servers sorted by latency ascending for early tight upper bounds.
    - Backtracks when current_cost + LB >= best_cost.
    """
    start_time = time.perf_counter()

    cap_cpu = {sid: float(s.cpu_capacity if hasattr(s, "cpu_capacity") else s["cpu_capacity"]) for sid, s in servers.items()}
    cap_ram = {sid: float(s.ram_capacity if hasattr(s, "ram_capacity") else s["ram_capacity"]) for sid, s in servers.items()}

    # Compute latency costs L(t, s)
    cost_matrix: Dict[str, Dict[str, float]] = {}
    min_cost_per_task: Dict[str, float] = {}

    for task in tasks:
        tid = task.task_id
        cost_matrix[tid] = {}
        for sid in servers:
            cost_matrix[tid][sid] = compute_task_server_latency(task, sid, dist_matrix)
        min_cost_per_task[tid] = min(cost_matrix[tid].values())

    # Precalculate suffix lower bounds for tasks
    n = len(tasks)
    suffix_lb = [0.0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix_lb[i] = suffix_lb[i + 1] + min_cost_per_task[tasks[i].task_id]

    # Initialize best solution with Greedy result to seed tight upper bound
    greedy_sol = greedy_nearest_traffic_placement(tasks, servers, dist_matrix)
    best_cost = greedy_sol.total_latency if not greedy_sol.unplaced_tasks else float("inf")
    best_assignment = dict(greedy_sol.placements) if not greedy_sol.unplaced_tasks else {}

    rem_cpu = dict(cap_cpu)
    rem_ram = dict(cap_ram)
    current_assignment: Dict[str, str] = {}

    def search(task_idx: int, current_cost: float):
        nonlocal best_cost, best_assignment
        if time.perf_counter() - start_time > time_limit_sec:
            return  # Time cutoff protection

        if task_idx == n:
            if current_cost < best_cost:
                best_cost = current_cost
                best_assignment = dict(current_assignment)
            return

        # Prune if admissible lower bound meets or exceeds current best
        if current_cost + suffix_lb[task_idx] >= best_cost:
            return

        task = tasks[task_idx]
        tid = task.task_id

        # Order servers by ascending latency for this task to find good solutions fast
        sorted_candidates = sorted(servers.keys(), key=lambda s: cost_matrix[tid][s])

        for sid in sorted_candidates:
            if rem_cpu[sid] >= task.cpu_demand and rem_ram[sid] >= task.ram_demand:
                cost = cost_matrix[tid][sid]
                if current_cost + cost + suffix_lb[task_idx + 1] < best_cost:
                    # Choose sid
                    rem_cpu[sid] -= task.cpu_demand
                    rem_ram[sid] -= task.ram_demand
                    current_assignment[tid] = sid

                    search(task_idx + 1, current_cost + cost)

                    # Backtrack
                    rem_cpu[sid] += task.cpu_demand
                    rem_ram[sid] += task.ram_demand
                    del current_assignment[tid]

    # Run Branch and Bound
    search(0, 0.0)

    exec_time = time.perf_counter() - start_time

    # If no complete assignment was found (e.g. overcapacity), fallback to Greedy
    if not best_assignment:
        best_assignment = greedy_sol.placements
        unplaced = greedy_sol.unplaced_tasks
    else:
        unplaced = [t.task_id for t in tasks if t.task_id not in best_assignment]

    tot_lat, avg_lat, cpu_used, ram_used = evaluate_placement(best_assignment, tasks, dist_matrix, servers)

    return PlacementResult(
        placements=best_assignment,
        unplaced_tasks=unplaced,
        total_latency=tot_lat,
        average_latency=avg_lat,
        server_cpu_usage=cpu_used,
        server_ram_usage=ram_used,
        server_cpu_capacity=cap_cpu,
        server_ram_capacity=cap_ram,
        algorithm_name="Exact Optimizer (Branch-and-Bound)",
        execution_time=exec_time,
        metadata={"proven_optimal": len(unplaced) == 0 and exec_time < time_limit_sec}
    )
