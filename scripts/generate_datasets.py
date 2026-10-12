"""
Dataset Generation Script.
Exports sample network topologies (Campus, Fat-Tree, Regional Cloud, Waxman)
to JSON, CSV, and Gephi GEXF format into the data/ directory.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from core.topology_generator import (
    create_campus_topology,
    create_fat_tree_datacenter_topology,
    create_regional_cloud_backbone,
    create_waxman_topology
)
from core.mst import kruskal_mst, extract_backbone_graph


def main():
    os.makedirs("data", exist_ok=True)
    print("Generating Cloud Network Datasets...")

    # 1. Campus Network
    campus = create_campus_topology()
    campus.export_to_json("data/campus_network.json")
    campus.export_to_csv("data/campus_nodes.csv", "data/campus_edges.csv")
    campus.export_to_gephi_gexf("data/campus_network.gexf")
    print(f"Generated Campus Network: {campus.num_nodes} nodes, {campus.num_edges} edges")

    # Campus Backbone
    mst_edges, weight, _ = kruskal_mst(campus)
    campus_backbone = extract_backbone_graph(campus, mst_edges)
    campus_backbone.export_to_gephi_gexf("data/campus_backbone.gexf")
    campus_backbone.export_to_json("data/campus_backbone.json")
    print(f"Generated Campus MST Backbone: {campus_backbone.num_nodes} nodes, {campus_backbone.num_edges} edges (Weight: {weight:.2f} ms)")

    # 2. Datacenter Fat-Tree
    fattree = create_fat_tree_datacenter_topology(k=4)
    fattree.export_to_json("data/datacenter_fattree.json")
    fattree.export_to_csv("data/fattree_nodes.csv", "data/fattree_edges.csv")
    fattree.export_to_gephi_gexf("data/datacenter_fattree.gexf")
    print(f"Generated Fat-Tree Datacenter: {fattree.num_nodes} nodes, {fattree.num_edges} edges")

    # 3. Regional Cloud Backbone
    regional = create_regional_cloud_backbone(seed=42)
    regional.export_to_json("data/regional_cloud.json")
    regional.export_to_csv("data/regional_nodes.csv", "data/regional_edges.csv")
    regional.export_to_gephi_gexf("data/regional_cloud.gexf")
    print(f"Generated Regional Cloud: {regional.num_nodes} nodes, {regional.num_edges} edges")

    # 4. Waxman Synthetic Graph
    waxman = create_waxman_topology(num_nodes=30, alpha=0.5, beta=0.3, seed=42)
    waxman.export_to_json("data/waxman_synthetic.json")
    waxman.export_to_csv("data/waxman_nodes.csv", "data/waxman_edges.csv")
    waxman.export_to_gephi_gexf("data/waxman_synthetic.gexf")
    print(f"Generated Waxman Network: {waxman.num_nodes} nodes, {waxman.num_edges} edges")

    print("\nAll datasets generated successfully in ./data/")


if __name__ == "__main__":
    main()
