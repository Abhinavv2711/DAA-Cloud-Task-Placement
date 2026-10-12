"""
FastAPI Backend for Cloud Task Placement React Dashboard.
Exposes REST endpoints for Topologies, MST Backbone, Shortest Path Routing,
Multi-Capacity Task Placement Schedulers, and Benchmarks.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import time
import os

from core.graph import Graph
from core.mst import prim_mst, kruskal_mst, extract_backbone_graph
from core.shortest_path import (
    dijkstra_sssp,
    bellman_ford_sssp,
    floyd_warshall_apsp,
    johnson_apsp,
    compute_apsp,
    reconstruct_path
)
from core.placement import (
    Task,
    greedy_nearest_traffic_placement,
    greedy_latency_density_placement,
    dp_knapsack_placement,
    exact_optimal_placement
)
from core.topology_generator import (
    create_campus_topology,
    create_fat_tree_datacenter_topology,
    create_regional_cloud_backbone,
    create_waxman_topology,
    generate_synthetic_tasks
)
from core.benchmark import run_backbone_vs_mesh_tradeoff

app = FastAPI(
    title="Cloud Task Placement API",
    description="High-performance backend for DAA Cloud Task Placement & Routing Dashboard",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite/Next default ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=FileResponse)
def serve_dashboard():
    """Serves the standalone interactive React & Tailwind dashboard."""
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return FileResponse("static/index.html")

@app.get("/docs/TECHNICAL_REPORT.html", response_class=FileResponse)
def serve_report():
    """Serves the publication-ready HTML technical report."""
    report_file = os.path.join(os.path.dirname(__file__), "docs", "TECHNICAL_REPORT.html")
    return FileResponse(report_file)

# In-memory cached topologies
TOPOLOGIES: Dict[str, Graph] = {
    "campus": create_campus_topology(),
    "fattree": create_fat_tree_datacenter_topology(k=4),
    "regional": create_regional_cloud_backbone(seed=42),
    "waxman": create_waxman_topology(num_nodes=25, alpha=0.5, beta=0.3, seed=42)
}


class SimulationRequest(BaseModel):
    topology_id: str = "campus"
    num_tasks: int = Field(default=10, ge=2, le=50)
    traffic_pattern: str = "hotspot"  # 'hotspot' or 'uniform'
    capacity_tightness: str = "normal"  # 'loose', 'normal', 'tight'
    algorithm: str = "exact"  # 'exact', 'dp', 'gnt', 'gld'


class MSTRequest(BaseModel):
    topology_id: str = "campus"
    algorithm: str = "kruskal"  # 'kruskal' or 'prim'
    root_node: Optional[str] = None


class RouteRequest(BaseModel):
    topology_id: str = "campus"
    source: str
    target: str
    algorithm: str = "dijkstra"  # 'dijkstra', 'bellman_ford', 'floyd_warshall', 'johnson'


@app.get("/api/topologies")
def list_topologies():
    """List available network topologies and summary statistics."""
    summary = []
    meta = {
        "campus": ("Campus Network Backbone", "16 nodes, Core/Dist/Edge university hierarchy"),
        "fattree": ("Datacenter Fat-Tree (k=4)", "20 switches, 3-tier non-blocking cloud fabric"),
        "regional": ("Regional Cloud Backbone", "20 regional datacenter metros with WAN fibers"),
        "waxman": ("Waxman Random Geometric Graph", "25 nodes with distance-probabilistic link weights")
    }
    for tid, g in TOPOLOGIES.items():
        name, desc = meta.get(tid, (tid.title(), "Network topology"))
        summary.append({
            "id": tid,
            "name": name,
            "description": desc,
            "num_nodes": g.num_nodes,
            "num_edges": g.num_edges,
            "density": round(g.density(), 4),
            "total_cpu_cores": int(sum(n.cpu_capacity for n in g.nodes.values())),
            "total_ram_gb": int(sum(n.ram_capacity for n in g.nodes.values()))
        })
    return summary


@app.get("/api/topology/{topology_id}")
def get_topology(topology_id: str):
    """Retrieve full node and edge specifications for visual graph rendering."""
    g = TOPOLOGIES.get(topology_id)
    if not g:
        raise HTTPException(status_code=404, detail="Topology not found")

    nodes = [n.to_dict() for n in g.nodes.values()]
    edges = [e.to_dict() for e in g.get_all_edges(deduplicate_undirected=True)]
    return {
        "id": topology_id,
        "nodes": nodes,
        "edges": edges,
        "num_nodes": g.num_nodes,
        "num_edges": g.num_edges
    }


@app.post("/api/mst")
def run_mst(req: MSTRequest):
    """Execute Prim or Kruskal MST and evaluate backbone latency stretch."""
    g = TOPOLOGIES.get(req.topology_id)
    if not g:
        raise HTTPException(status_code=404, detail="Topology not found")

    if req.algorithm.lower() == "prim":
        edges, weight, exec_time = prim_mst(g, start_node=req.root_node)
        algo_name = "Prim's Algorithm (Binary Min-Heap)"
    else:
        edges, weight, exec_time = kruskal_mst(g)
        algo_name = "Kruskal's Algorithm (DSU Union-by-Rank)"

    tradeoff = run_backbone_vs_mesh_tradeoff(g)

    return {
        "algorithm": algo_name,
        "total_weight_ms": round(weight, 2),
        "execution_time_ms": round(exec_time * 1000, 3),
        "mst_edges": [e.to_dict() for e in edges],
        "links_saved": tradeoff["links_saved"],
        "link_reduction_pct": tradeoff["link_reduction_pct"],
        "avg_latency_stretch": tradeoff["average_stretch_factor"]
    }


@app.post("/api/route")
def compute_route(req: RouteRequest):
    """Compute single-source or all-pairs shortest paths."""
    g = TOPOLOGIES.get(req.topology_id)
    if not g:
        raise HTTPException(status_code=404, detail="Topology not found")

    src, dst = req.source, req.target
    if src not in g.nodes or dst not in g.nodes:
        raise HTTPException(status_code=400, detail="Invalid source or target node")

    algo = req.algorithm.lower()
    has_neg_cycle = False

    if algo == "dijkstra":
        dists, preds, t = dijkstra_sssp(g, src)
        path, _ = reconstruct_path(src, dst, preds)
        cost = dists[dst]
    elif algo == "bellman_ford":
        dists, preds, has_neg, t = bellman_ford_sssp(g, src)
        path, _ = reconstruct_path(src, dst, preds)
        cost = dists[dst]
        has_neg_cycle = has_neg
    elif algo == "floyd_warshall":
        dists_mat, next_mat, t = floyd_warshall_apsp(g)
        path, _ = reconstruct_path(src, dst, next_mat, is_next_matrix=True)
        cost = dists_mat[src][dst]
    else:  # johnson
        dists_mat, preds_mat, t = johnson_apsp(g)
        path, _ = reconstruct_path(src, dst, preds_mat[src])
        cost = dists_mat[src][dst]

    return {
        "algorithm": req.algorithm,
        "source": src,
        "target": dst,
        "path": path,
        "hop_count": len(path) - 1 if path else 0,
        "latency_ms": round(cost, 2),
        "execution_time_ms": round(t * 1000, 3),
        "has_negative_cycle": has_neg_cycle
    }


@app.post("/api/simulate-placement")
def simulate_placement(req: SimulationRequest):
    """Run multi-capacity VM placement optimization."""
    g = TOPOLOGIES.get(req.topology_id)
    if not g:
        raise HTTPException(status_code=404, detail="Topology not found")

    cap_mult = 1.5 if req.capacity_tightness == "loose" else (1.0 if req.capacity_tightness == "normal" else 0.6)
    servers = {
        sid: {
            "cpu_capacity": node.cpu_capacity * cap_mult,
            "ram_capacity": node.ram_capacity * cap_mult
        }
        for sid, node in g.nodes.items()
    }

    server_ids = list(g.nodes.keys())
    tasks = generate_synthetic_tasks(
        num_tasks=req.num_tasks,
        server_ids=server_ids,
        traffic_pattern=req.traffic_pattern,
        seed=req.num_tasks * 17
    )

    dist_matrix, _, _, _ = compute_apsp(g)

    algo = req.algorithm.lower()
    if algo == "exact":
        res = exact_optimal_placement(tasks, servers, dist_matrix, time_limit_sec=4.0)
    elif algo == "dp":
        res = dp_knapsack_placement(tasks, servers, dist_matrix)
    elif algo == "gld":
        res = greedy_latency_density_placement(tasks, servers, dist_matrix)
    else:  # gnt
        res = greedy_nearest_traffic_placement(tasks, servers, dist_matrix)

    # Server load distribution details
    server_stats = []
    for sid, cap in servers.items():
        used_cpu = res.server_cpu_usage.get(sid, 0.0)
        used_ram = res.server_ram_usage.get(sid, 0.0)
        server_stats.append({
            "server_id": sid,
            "cpu_used": round(used_cpu, 1),
            "cpu_capacity": round(cap["cpu_capacity"], 1),
            "cpu_util_pct": round((used_cpu / cap["cpu_capacity"] * 100.0) if cap["cpu_capacity"] > 0 else 0, 1),
            "ram_used": round(used_ram, 1),
            "ram_capacity": round(cap["ram_capacity"], 1),
            "ram_util_pct": round((used_ram / cap["ram_capacity"] * 100.0) if cap["ram_capacity"] > 0 else 0, 1)
        })

    return {
        "algorithm": res.algorithm_name,
        "total_latency": round(res.total_latency, 2),
        "average_latency_ms": round(res.average_latency, 2),
        "execution_time_ms": round(res.execution_time * 1000, 3),
        "placed_count": len(res.placements),
        "unplaced_count": len(res.unplaced_tasks),
        "cpu_utilization_pct": round(res.cpu_utilization_percent(), 2),
        "ram_utilization_pct": round(res.ram_utilization_percent(), 2),
        "placements": res.placements,
        "servers": server_stats,
        "tasks": [t.to_dict() for t in tasks]
    }


@app.get("/api/benchmarks")
def get_benchmarks():
    """Returns precomputed empirical benchmark matrices for Recharts plotting."""
    import pandas as pd
    import os

    res = {}
    p_path = "data/benchmark_results/placement_benchmark.csv"
    m_path = "data/benchmark_results/mst_benchmark.csv"
    s_path = "data/benchmark_results/shortest_path_benchmark.csv"

    if os.path.exists(p_path):
        res["placement"] = pd.read_csv(p_path).to_dict(orient="records")
    if os.path.exists(m_path):
        res["mst"] = pd.read_csv(m_path).to_dict(orient="records")
    if os.path.exists(s_path):
        res["shortest_path"] = pd.read_csv(s_path).to_dict(orient="records")

    return res


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
