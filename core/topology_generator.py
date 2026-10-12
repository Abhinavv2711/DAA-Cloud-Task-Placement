"""
Cloud Topology Generators and Synthetic Dataset Synthesizers.
Generates:
1. Realistic University/Enterprise Campus Network Topology.
2. Three-Tier Datacenter Fat-Tree Topology.
3. Trans-Regional Cloud Backbone Topology (Geant/Abilene style).
4. Waxman Random Geometric Network Topology.
5. Workload / Task Generator with realistic multi-resource demands and traffic matrices.
"""

from typing import Dict, List, Optional, Tuple
import random
import math
from .graph import Graph, ServerNode
from .placement import Task


def create_campus_topology() -> Graph:
    """
    Constructs a 16-node realistic University Campus Network Topology.
    Tiers: Core Routers, Distribution Switches, Edge/Datacenter compute nodes.
    """
    g = Graph(directed=False)

    nodes_info = [
        # (id, name, cpu, ram, tier, x, y)
        ("Core-1", "Main Data Center Core", 128, 512, "core", 5.0, 8.0),
        ("Core-2", "Backup Disaster Recovery Core", 128, 512, "core", 9.0, 8.0),
        ("Dist-North", "Distribution North (STEM)", 64, 256, "aggregation", 3.0, 6.0),
        ("Dist-South", "Distribution South (Admin/Res)", 64, 256, "aggregation", 7.0, 6.0),
        ("Dist-East", "Distribution East (Medical/Bio)", 64, 256, "aggregation", 11.0, 6.0),
        ("Dist-West", "Distribution West (Arts/Lib)", 64, 256, "aggregation", 1.0, 6.0),
        ("CS-Lab", "Computer Science Cluster", 96, 384, "edge_compute", 2.0, 3.5),
        ("Eng-HPC", "Engineering Supercomputer", 128, 512, "edge_compute", 4.0, 3.5),
        ("Science-DC", "Natural Sciences Server", 64, 256, "edge_compute", 3.0, 1.5),
        ("Admin-Server", "Central Administration VM", 48, 192, "edge_compute", 6.0, 3.5),
        ("Library-Edge", "Digital Library Repository", 32, 128, "edge_compute", 0.5, 3.5),
        ("Medical-Edge", "University Hospital Datacenter", 96, 384, "edge_compute", 11.5, 3.5),
        ("Biotech-Lab", "Genomics Sequencing Server", 64, 256, "edge_compute", 10.0, 1.5),
        ("Hostel-DC-A", "Student Residence Edge Alpha", 32, 128, "edge_compute", 7.5, 1.5),
        ("Hostel-DC-B", "Student Residence Edge Beta", 32, 128, "edge_compute", 8.5, 3.5),
        ("Media-Studio", "Creative Media & Cloud Render", 48, 192, "edge_compute", 1.5, 1.5),
    ]

    for nid, name, cpu, ram, tier, x, y in nodes_info:
        g.add_node(
            node_id=nid,
            name=name,
            cpu_capacity=cpu,
            ram_capacity=ram,
            tier=tier,
            x=x,
            y=y,
            region="Campus"
        )

    # Physical Links: (u, v, latency_ms, bandwidth_mbps)
    links = [
        # Core Backbone Link
        ("Core-1", "Core-2", 0.5, 40000),

        # Core to Distribution
        ("Core-1", "Dist-North", 1.2, 20000),
        ("Core-1", "Dist-West", 1.5, 20000),
        ("Core-1", "Dist-South", 1.8, 20000),
        ("Core-2", "Dist-South", 1.2, 20000),
        ("Core-2", "Dist-East", 1.4, 20000),
        ("Core-2", "Dist-North", 1.9, 20000),

        # Cross Distribution Links
        ("Dist-West", "Dist-North", 2.2, 10000),
        ("Dist-North", "Dist-South", 2.0, 10000),
        ("Dist-South", "Dist-East", 2.4, 10000),

        # Distribution to Compute Edges
        ("Dist-North", "CS-Lab", 1.0, 10000),
        ("Dist-North", "Eng-HPC", 0.9, 10000),
        ("CS-Lab", "Science-DC", 2.1, 5000),
        ("Eng-HPC", "Science-DC", 1.8, 5000),

        ("Dist-West", "Library-Edge", 1.5, 5000),
        ("Dist-West", "Media-Studio", 1.7, 5000),
        ("Library-Edge", "Media-Studio", 2.8, 2000),

        ("Dist-South", "Admin-Server", 1.1, 10000),
        ("Dist-South", "Hostel-DC-A", 2.5, 5000),
        ("Dist-South", "Hostel-DC-B", 2.2, 5000),
        ("Hostel-DC-A", "Hostel-DC-B", 1.6, 5000),

        ("Dist-East", "Medical-Edge", 1.0, 10000),
        ("Dist-East", "Biotech-Lab", 1.3, 10000),
        ("Medical-Edge", "Biotech-Lab", 1.5, 5000),

        # Inter-department cross links
        ("CS-Lab", "Eng-HPC", 0.8, 10000),
        ("Eng-HPC", "Admin-Server", 2.7, 5000),
        ("Admin-Server", "Hostel-DC-B", 2.0, 5000),
        ("Biotech-Lab", "Science-DC", 4.2, 2000),
    ]

    for u, v, lat, bw in links:
        g.add_edge(u, v, weight=lat, bandwidth=bw)

    return g


def create_fat_tree_datacenter_topology(k: int = 4) -> Graph:
    """
    Constructs a k-port Fat-Tree Datacenter Architecture.
    For k=4:
    - 4 Core switches
    - 4 Pods, each with 2 Aggregation switches and 2 Edge switches (16 total pod switches)
    - Total: 20 switches/racks
    """
    g = Graph(directed=False)

    num_cores = (k // 2) ** 2
    cores = [f"Core-{i+1}" for i in range(num_cores)]
    for i, c in enumerate(cores):
        g.add_node(c, name=f"Core Switch {i+1}", cpu_capacity=128, ram_capacity=512, tier="core", x=i * 3.0 + 2.0, y=9.0)

    aggs = []
    edges = []
    pod_size = k // 2

    for pod in range(k):
        pod_aggs = [f"Pod{pod}-Agg{j}" for j in range(pod_size)]
        pod_edges = [f"Pod{pod}-Edge{j}" for j in range(pod_size)]
        aggs.extend(pod_aggs)
        edges.extend(pod_edges)

        for j, a in enumerate(pod_aggs):
            g.add_node(a, name=f"Pod {pod} Agg {j}", cpu_capacity=64, ram_capacity=256, tier="aggregation", x=pod * 4.0 + j * 1.5, y=6.0)

        for j, e in enumerate(pod_edges):
            g.add_node(e, name=f"Pod {pod} Rack Edge {j}", cpu_capacity=64, ram_capacity=256, tier="edge", x=pod * 4.0 + j * 1.5, y=3.0)

        # Intra-pod bipartite links between Aggregation and Edge
        for a in pod_aggs:
            for e in pod_edges:
                g.add_edge(a, e, weight=0.8, bandwidth=25000)

        # Connect pod Aggregations to Core switches
        for j, a in enumerate(pod_aggs):
            for c_idx in range(pod_size):
                core_target = cores[j * pod_size + c_idx]
                g.add_edge(a, core_target, weight=1.5, bandwidth=40000)

    return g


def create_regional_cloud_backbone(seed: int = 42) -> Graph:
    """
    Constructs a 20-node Regional Cloud Backbone network mimicking major global/inter-city cloud regions.
    """
    rng = random.Random(seed)
    g = Graph(directed=False)

    regions = [
        ("US-East-1", "Virginia (Core DC)", 256, 1024, "core", 3.0, 7.0),
        ("US-East-2", "Ohio", 128, 512, "aggregation", 3.8, 6.8),
        ("US-West-1", "N. California", 128, 512, "aggregation", 1.2, 6.5),
        ("US-West-2", "Oregon", 192, 768, "core", 1.0, 8.0),
        ("US-Central", "Iowa", 96, 384, "edge", 2.5, 6.9),
        ("CA-Central", "Montreal", 96, 384, "edge", 3.6, 8.5),
        ("EU-West-1", "Ireland", 192, 768, "core", 7.0, 8.2),
        ("EU-West-2", "London", 128, 512, "aggregation", 7.5, 7.8),
        ("EU-Central-1", "Frankfurt", 256, 1024, "core", 8.5, 7.2),
        ("EU-North-1", "Stockholm", 96, 384, "edge", 8.8, 9.0),
        ("EU-South-1", "Milan", 96, 384, "edge", 8.4, 6.2),
        ("AP-South-1", "Mumbai", 128, 512, "aggregation", 12.0, 4.5),
        ("AP-Southeast-1", "Singapore", 192, 768, "core", 14.0, 3.0),
        ("AP-East-1", "Hong Kong", 96, 384, "edge", 14.5, 5.0),
        ("AP-Northeast-1", "Tokyo", 192, 768, "core", 16.0, 6.5),
        ("AP-Northeast-2", "Seoul", 96, 384, "edge", 15.2, 7.0),
        ("AP-Southeast-2", "Sydney", 128, 512, "aggregation", 16.5, 1.5),
        ("SA-East-1", "São Paulo", 96, 384, "edge", 4.5, 2.0),
        ("ME-Central-1", "Dubai", 96, 384, "edge", 10.5, 5.2),
        ("AF-South-1", "Cape Town", 64, 256, "edge", 8.5, 1.2),
    ]

    for rid, name, cpu, ram, tier, x, y in regions:
        g.add_node(rid, name=name, cpu_capacity=cpu, ram_capacity=ram, tier=tier, x=x, y=y, region=rid.split("-")[0])

    backbone_links = [
        # Transatlantic
        ("US-East-1", "EU-West-1", 68.0, 100000),
        ("US-East-2", "EU-West-2", 72.0, 80000),
        # US Domestic
        ("US-East-1", "US-East-2", 11.0, 100000),
        ("US-East-2", "US-Central", 14.0, 80000),
        ("US-Central", "US-West-2", 32.0, 80000),
        ("US-West-1", "US-West-2", 18.0, 80000),
        ("US-East-1", "CA-Central", 15.0, 50000),
        ("US-Central", "US-West-1", 29.0, 50000),
        # South America
        ("US-East-1", "SA-East-1", 105.0, 40000),
        # Europe
        ("EU-West-1", "EU-West-2", 12.0, 100000),
        ("EU-West-2", "EU-Central-1", 16.0, 100000),
        ("EU-Central-1", "EU-North-1", 22.0, 50000),
        ("EU-Central-1", "EU-South-1", 15.0, 50000),
        # Middle East & Africa
        ("EU-Central-1", "ME-Central-1", 65.0, 40000),
        ("EU-West-2", "AF-South-1", 135.0, 30000),
        ("ME-Central-1", "AP-South-1", 38.0, 40000),
        # Asia Pacific
        ("AP-South-1", "AP-Southeast-1", 42.0, 60000),
        ("AP-Southeast-1", "AP-East-1", 34.0, 60000),
        ("AP-East-1", "AP-Northeast-2", 28.0, 50000),
        ("AP-Northeast-2", "AP-Northeast-1", 24.0, 80000),
        ("AP-Southeast-1", "AP-Southeast-2", 92.0, 50000),
        # Transpacific
        ("AP-Northeast-1", "US-West-2", 95.0, 100000),
        ("AP-Southeast-2", "US-West-1", 138.0, 60000),
    ]

    for u, v, lat, bw in backbone_links:
        g.add_edge(u, v, weight=lat, bandwidth=bw)

    return g


def create_waxman_topology(
    num_nodes: int = 30,
    alpha: float = 0.5,
    beta: float = 0.3,
    seed: int = 42
) -> Graph:
    """
    Constructs a Waxman Random Geometric Network Topology.
    Link probability P(u, v) = alpha * exp(-dist(u, v) / (beta * L_max)).
    """
    rng = random.Random(seed)
    g = Graph(directed=False)

    positions = {}
    for i in range(num_nodes):
        nid = f"Node-{i+1}"
        x = rng.uniform(0.0, 100.0)
        y = rng.uniform(0.0, 100.0)
        positions[nid] = (x, y)
        cpu = rng.choice([32, 64, 96, 128])
        ram = cpu * rng.choice([4, 8])
        tier = "core" if cpu >= 96 else ("aggregation" if cpu >= 64 else "edge")
        g.add_node(nid, name=f"Server {nid}", cpu_capacity=cpu, ram_capacity=ram, tier=tier, x=x, y=y)

    nodes = list(positions.keys())
    # Compute maximum Euclidean distance
    max_dist = 0.0
    dist_map = {}
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            u, v = nodes[i], nodes[j]
            d = math.hypot(positions[u][0] - positions[v][0], positions[u][1] - positions[v][1])
            dist_map[(u, v)] = d
            if d > max_dist:
                max_dist = d

    # Add edges probabilistically
    for (u, v), d in dist_map.items():
        prob = alpha * math.exp(-d / (beta * max_dist))
        if rng.random() < prob:
            # Latency proportional to distance with slight jitter
            latency = round(d * 0.15 + rng.uniform(0.5, 2.0), 2)
            g.add_edge(u, v, weight=latency, bandwidth=rng.choice([5000, 10000, 20000]))

    # Ensure connectedness: connect any isolated node to its nearest neighbor
    for u in nodes:
        if g.degree(u) == 0:
            nearest = min((v for v in nodes if v != u), key=lambda v: dist_map.get((u, v), dist_map.get((v, u), 9999)))
            d = dist_map.get((u, nearest), dist_map.get((nearest, u), 10.0))
            g.add_edge(u, nearest, weight=round(d * 0.15 + 1.0, 2), bandwidth=10000)

    return g


def generate_synthetic_tasks(
    num_tasks: int,
    server_ids: List[str],
    traffic_pattern: str = "hotspot",
    seed: int = 101
) -> List[Task]:
    """
    Generates synthetic VM replica tasks with varying CPU/RAM profiles and client request traffic.
    Traffic patterns:
    - 'hotspot': 80% traffic concentrated in top 20% servers (Pareto principle)
    - 'uniform': evenly distributed client traffic
    - 'local': concentrated on client nodes in the same region
    """
    rng = random.Random(seed)
    task_profiles = [
        ("Web-Frontend", 4.0, 16.0),
        ("DB-Replica", 16.0, 64.0),
        ("API-Gateway", 8.0, 32.0),
        ("ML-Inference", 32.0, 128.0),
        ("Cache-Node", 4.0, 32.0),
        ("Analytics-Worker", 16.0, 48.0),
    ]

    tasks: List[Task] = []
    hotspot_servers = rng.sample(server_ids, max(1, len(server_ids) // 4))

    for i in range(num_tasks):
        tid = f"Task-{i+1}"
        profile_name, cpu, ram = rng.choice(task_profiles)
        name = f"{profile_name}-{i+1}"

        # Generate traffic map
        traffic: Dict[str, float] = {}
        if traffic_pattern == "hotspot":
            # 80% weight on hotspot servers
            for s in server_ids:
                if s in hotspot_servers:
                    traffic[s] = round(rng.uniform(50.0, 200.0), 1)
                else:
                    traffic[s] = round(rng.uniform(5.0, 25.0), 1)
        else:  # uniform
            for s in server_ids:
                traffic[s] = round(rng.uniform(10.0, 50.0), 1)

        tasks.append(
            Task(
                task_id=tid,
                name=name,
                cpu_demand=cpu,
                ram_demand=ram,
                traffic=traffic,
                priority=rng.choice([1, 2, 3]),
                metadata={"profile": profile_name}
            )
        )

    return tasks
