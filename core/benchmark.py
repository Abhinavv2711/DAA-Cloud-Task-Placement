"""
Benchmarking and Experimentation Suite for Cloud Task Placement.
Varies graph size, link density, and capacity tightness.
Measures execution runtimes, average latencies, optimality gaps, and backbone tradeoffs.
Generates structured CSV and Markdown policy tables.
"""

from typing import Any, Dict, List, Optional, Tuple
import time
import math
import pandas as pd
import numpy as np

from .graph import Graph
from .priority_queue import PriorityQueue
from .mst import prim_mst, kruskal_mst, extract_backbone_graph
from .shortest_path import (
    dijkstra_sssp,
    bellman_ford_sssp,
    floyd_warshall_apsp,
    johnson_apsp,
    compute_apsp
)
from .placement import (
    Task,
    PlacementResult,
    greedy_nearest_traffic_placement,
    greedy_latency_density_placement,
    dp_knapsack_placement,
    exact_optimal_placement
)
from .topology_generator import create_waxman_topology, generate_synthetic_tasks


def run_mst_benchmark(
    sizes: List[int] = [15, 30, 60, 120],
    densities: List[str] = ["sparse", "dense"]
) -> pd.DataFrame:
    """
    Compares Prim's vs Kruskal's algorithm runtimes across graph sizes and densities.
    """
    records = []
    for n in sizes:
        for dens in densities:
            alpha = 0.25 if dens == "sparse" else 0.85
            beta = 0.2 if dens == "sparse" else 0.5
            g = create_waxman_topology(num_nodes=n, alpha=alpha, beta=beta, seed=n * 7)

            edges_count = g.num_edges

            # Kruskal
            k_edges, k_weight, k_time = kruskal_mst(g)

            # Prim
            p_edges, p_weight, p_time = prim_mst(g)

            records.append({
                "Nodes (V)": n,
                "Edges (E)": edges_count,
                "Density Type": dens,
                "Graph Density": round(g.density(), 4),
                "Prim Runtime (ms)": round(p_time * 1000, 3),
                "Kruskal Runtime (ms)": round(k_time * 1000, 3),
                "Prim MST Weight": round(p_weight, 2),
                "Kruskal MST Weight": round(k_weight, 2),
                "Weights Match": math.isclose(p_weight, k_weight, rel_tol=1e-4)
            })

    return pd.DataFrame(records)


def run_shortest_path_benchmark(
    sizes: List[int] = [10, 20, 35, 50]
) -> pd.DataFrame:
    """
    Compares APSP (Floyd-Warshall vs Johnson) and SSSP (Dijkstra vs Bellman-Ford).
    """
    records = []
    for n in sizes:
        g = create_waxman_topology(num_nodes=n, alpha=0.4, beta=0.3, seed=n * 13)
        source = list(g.nodes.keys())[0]

        # SSSP
        _, _, dijk_time = dijkstra_sssp(g, source)
        _, _, _, bf_time = bellman_ford_sssp(g, source)

        # APSP
        _, _, fw_time = floyd_warshall_apsp(g)
        _, _, jn_time = johnson_apsp(g)

        records.append({
            "Nodes (V)": n,
            "Edges (E)": g.num_edges,
            "Dijkstra SSSP (ms)": round(dijk_time * 1000, 3),
            "Bellman-Ford SSSP (ms)": round(bf_time * 1000, 3),
            "Floyd-Warshall APSP (ms)": round(fw_time * 1000, 3),
            "Johnson APSP (ms)": round(jn_time * 1000, 3),
            "APSP Speedup (FW / Johnson)": round(fw_time / max(1e-6, jn_time), 2)
        })

    return pd.DataFrame(records)


def run_placement_benchmark(
    task_counts: List[int] = [5, 10, 15, 25],
    graph_size: int = 16,
    capacity_tightness: List[str] = ["loose", "normal", "tight"]
) -> pd.DataFrame:
    """
    Compares Greedy, Dynamic Programming, and Exact Optimizer on task placement.
    Evaluates runtime, average latency, and optimality gaps.
    """
    g = create_waxman_topology(num_nodes=graph_size, alpha=0.5, beta=0.3, seed=42)
    dist_matrix, _, _, _ = compute_apsp(g)
    server_ids = list(g.nodes.keys())

    records = []

    for num_t in task_counts:
        for tightness in capacity_tightness:
            # Scale server capacities according to tightness
            cap_mult = 1.5 if tightness == "loose" else (1.0 if tightness == "normal" else 0.6)
            servers = {}
            for sid, node in g.nodes.items():
                servers[sid] = {
                    "cpu_capacity": node.cpu_capacity * cap_mult,
                    "ram_capacity": node.ram_capacity * cap_mult
                }

            tasks = generate_synthetic_tasks(num_t, server_ids, traffic_pattern="hotspot", seed=num_t * 11)

            # 1. Greedy Nearest
            res_gnt = greedy_nearest_traffic_placement(tasks, servers, dist_matrix)

            # 2. Greedy Latency-Density
            res_gld = greedy_latency_density_placement(tasks, servers, dist_matrix)

            # 3. Dynamic Programming
            res_dp = dp_knapsack_placement(tasks, servers, dist_matrix)

            # 4. Exact Optimizer (run if task count <= 25 for quick execution)
            if num_t <= 20:
                res_exact = exact_optimal_placement(tasks, servers, dist_matrix, time_limit_sec=3.0)
                exact_lat = res_exact.average_latency
                exact_time = res_exact.execution_time * 1000
            else:
                res_exact = None
                exact_lat = None
                exact_time = None

            # Calculate optimality gap for DP and Greedy if exact solution available
            dp_gap = round(((res_dp.average_latency - exact_lat) / exact_lat * 100.0), 2) if exact_lat else None
            gnt_gap = round(((res_gnt.average_latency - exact_lat) / exact_lat * 100.0), 2) if exact_lat else None

            records.append({
                "Tasks": num_t,
                "Tightness": tightness,
                "GNT Avg Latency (ms)": round(res_gnt.average_latency, 2),
                "DP Avg Latency (ms)": round(res_dp.average_latency, 2),
                "Exact Avg Latency (ms)": round(exact_lat, 2) if exact_lat is not None else "N/A",
                "GNT Gap (%)": gnt_gap if gnt_gap is not None else "N/A",
                "DP Gap (%)": dp_gap if dp_gap is not None else "N/A",
                "GNT Runtime (ms)": round(res_gnt.execution_time * 1000, 3),
                "DP Runtime (ms)": round(res_dp.execution_time * 1000, 3),
                "Exact Runtime (ms)": round(exact_time, 3) if exact_time is not None else "N/A",
                "DP CPU Util (%)": round(res_dp.cpu_utilization_percent(), 1)
            })

    return pd.DataFrame(records)


def run_backbone_vs_mesh_tradeoff(graph: Graph) -> Dict[str, Any]:
    """
    Evaluates the tradeoff between routing on the full physical network vs the MST backbone.
    Quantifies latency stretch, hop-count changes, and link reduction efficiency.
    """
    mst_edges, total_mst_weight, _ = kruskal_mst(graph)
    backbone_g = extract_backbone_graph(graph, mst_edges)

    dist_full, _, _, _ = compute_apsp(graph)
    dist_backbone, _, _, _ = compute_apsp(backbone_g)

    nodes = list(graph.nodes.keys())
    pairs = 0
    full_lat_sum = 0.0
    backbone_lat_sum = 0.0
    stretches = []

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            u, v = nodes[i], nodes[j]
            d_full = dist_full[u][v]
            d_bb = dist_backbone[u][v]
            if d_full < float("inf") and d_bb < float("inf") and d_full > 0:
                pairs += 1
                full_lat_sum += d_full
                backbone_lat_sum += d_bb
                stretches.append(d_bb / d_full)

    avg_full_lat = full_lat_sum / max(1, pairs)
    avg_bb_lat = backbone_lat_sum / max(1, pairs)
    avg_stretch = np.mean(stretches) if stretches else 1.0
    max_stretch = np.max(stretches) if stretches else 1.0

    links_saved = graph.num_edges - backbone_g.num_edges
    link_reduction_pct = (links_saved / max(1, graph.num_edges)) * 100.0

    return {
        "num_nodes": graph.num_nodes,
        "physical_edges": graph.num_edges,
        "backbone_edges": backbone_g.num_edges,
        "links_saved": links_saved,
        "link_reduction_pct": round(link_reduction_pct, 2),
        "avg_physical_latency_ms": round(avg_full_lat, 2),
        "avg_backbone_latency_ms": round(avg_bb_lat, 2),
        "average_stretch_factor": round(float(avg_stretch), 3),
        "maximum_stretch_factor": round(float(max_stretch), 3),
        "total_mst_weight": round(total_mst_weight, 2)
    }
