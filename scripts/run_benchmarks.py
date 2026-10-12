"""
Script to execute the complete benchmark suite and export experimental data
to CSV and JSON files for the technical report, dashboard, and presentation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from core.benchmark import (
    run_mst_benchmark,
    run_shortest_path_benchmark,
    run_placement_benchmark,
    run_backbone_vs_mesh_tradeoff
)
from core.topology_generator import create_campus_topology, create_regional_cloud_backbone


def main():
    out_dir = "data/benchmark_results"
    os.makedirs(out_dir, exist_ok=True)
    print("Starting Comprehensive Benchmarking Suite...")

    # 1. MST Benchmark
    print("1/4: Running MST Benchmark (Prim vs Kruskal across sizes and densities)...")
    df_mst = run_mst_benchmark(sizes=[15, 30, 60, 120], densities=["sparse", "dense"])
    df_mst.to_csv(os.path.join(out_dir, "mst_benchmark.csv"), index=False)
    print(df_mst.to_string())

    # 2. Shortest Path Benchmark
    print("\n2/4: Running Shortest Path Benchmark (Dijkstra, Bellman-Ford, Floyd-Warshall, Johnson)...")
    df_sp = run_shortest_path_benchmark(sizes=[10, 20, 35, 50])
    df_sp.to_csv(os.path.join(out_dir, "shortest_path_benchmark.csv"), index=False)
    print(df_sp.to_string())

    # 3. Placement Optimization Benchmark
    print("\n3/4: Running Task Placement Benchmark (Greedy vs DP vs Exact Optimizer)...")
    df_placement = run_placement_benchmark(
        task_counts=[5, 10, 15, 20],
        graph_size=16,
        capacity_tightness=["loose", "normal", "tight"]
    )
    df_placement.to_csv(os.path.join(out_dir, "placement_benchmark.csv"), index=False)
    print(df_placement.to_string())

    # 4. Backbone vs Mesh Tradeoff
    print("\n4/4: Evaluating Backbone vs Mesh Tradeoff on Campus and Regional Networks...")
    campus = create_campus_topology()
    regional = create_regional_cloud_backbone()

    tradeoff_campus = run_backbone_vs_mesh_tradeoff(campus)
    tradeoff_regional = run_backbone_vs_mesh_tradeoff(regional)

    tradeoffs = {
        "campus_network": tradeoff_campus,
        "regional_cloud": tradeoff_regional
    }
    with open(os.path.join(out_dir, "backbone_tradeoffs.json"), "w", encoding="utf-8") as f:
        json.dump(tradeoffs, f, indent=2)

    print("\nCampus Backbone Tradeoff:")
    for k, v in tradeoff_campus.items():
        print(f"  {k}: {v}")

    print("\nRegional Cloud Backbone Tradeoff:")
    for k, v in tradeoff_regional.items():
        print(f"  {k}: {v}")

    print(f"\nAll benchmark results successfully exported to {out_dir}/")


if __name__ == "__main__":
    main()
