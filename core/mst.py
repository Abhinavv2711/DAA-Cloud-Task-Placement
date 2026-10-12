"""
Minimum Spanning Tree (MST) Algorithms and Backbone Network Extraction.
Implements:
1. Prim's Algorithm using Binary Min-Heap Priority Queue (O((V + E) log V)).
2. Kruskal's Algorithm using Disjoint Set Union (DSU) with Path Compression and Union by Rank (O(E log E)).
3. Backbone Subgraph Extraction and Structural Analytics.
"""

from typing import Dict, List, Optional, Set, Tuple
import time
from .graph import Graph, Edge
from .priority_queue import PriorityQueue


class DisjointSetUnion:
    """
    Disjoint Set Union (Union-Find) with path compression and union by rank.
    Nearly O(1) amortized operations via inverse Ackermann complexity O(alpha(V)).
    """

    def __init__(self, elements: List[str]):
        self.parent: Dict[str, str] = {x: x for x in elements}
        self.rank: Dict[str, int] = {x: 0 for x in elements}

    def find(self, x: str) -> str:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x: str, y: str) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # Already in the same connected component

        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        return True


def kruskal_mst(graph: Graph) -> Tuple[List[Edge], float, float]:
    """
    Kruskal's Algorithm for Minimum Spanning Tree.
    Returns:
        (mst_edges, total_latency_weight, execution_time_seconds)
    Time Complexity: O(E log E)
    Space Complexity: O(V + E)
    """
    start_time = time.perf_counter()

    all_edges = graph.get_all_edges(deduplicate_undirected=True)
    # Sort all edges in non-decreasing order of latency weight
    sorted_edges = sorted(all_edges, key=lambda e: e.weight)

    node_ids = list(graph.nodes.keys())
    dsu = DisjointSetUnion(node_ids)

    mst_edges: List[Edge] = []
    total_weight = 0.0
    target_edges_count = len(node_ids) - 1

    for edge in sorted_edges:
        if dsu.union(edge.u, edge.v):
            mst_edges.append(edge)
            total_weight += edge.weight
            if len(mst_edges) == target_edges_count:
                break

    exec_time = time.perf_counter() - start_time
    return mst_edges, total_weight, exec_time


def prim_mst(graph: Graph, start_node: Optional[str] = None) -> Tuple[List[Edge], float, float]:
    """
    Prim's Algorithm for Minimum Spanning Tree using a custom Binary Min-Heap Priority Queue.
    Returns:
        (mst_edges, total_latency_weight, execution_time_seconds)
    Time Complexity: O((V + E) log V)
    Space Complexity: O(V)
    """
    start_time = time.perf_counter()
    node_ids = list(graph.nodes.keys())
    if not node_ids:
        return [], 0.0, 0.0

    if start_node is None or start_node not in graph.nodes:
        start_node = node_ids[0]

    pq = PriorityQueue()
    # Track the minimal edge connecting each node to the growing MST
    parent: Dict[str, Optional[str]] = {node: None for node in node_ids}
    edge_obj_map: Dict[str, Optional[Edge]] = {node: None for node in node_ids}
    visited: Set[str] = set()

    for node in node_ids:
        initial_p = 0.0 if node == start_node else float("inf")
        pq.push(node, initial_p)

    mst_edges: List[Edge] = []
    total_weight = 0.0

    while not pq.is_empty():
        u, weight = pq.pop()
        visited.add(u)

        if parent[u] is not None:
            best_edge = edge_obj_map[u]
            if best_edge:
                mst_edges.append(best_edge)
                total_weight += weight

        for edge in graph.get_out_edges(u):
            v = edge.v
            if v not in visited:
                current_p = pq.get_priority(v)
                if current_p is not None and edge.weight < current_p:
                    parent[v] = u
                    edge_obj_map[v] = edge
                    pq.decrease_key(v, edge.weight)

    exec_time = time.perf_counter() - start_time
    return mst_edges, total_weight, exec_time


def extract_backbone_graph(original_graph: Graph, mst_edges: List[Edge]) -> Graph:
    """
    Constructs a dedicated backbone network Graph containing all original server nodes
    and only the edges selected by the Minimum Spanning Tree.
    """
    backbone = Graph(directed=original_graph.directed)

    # Copy all nodes to preserve capacity attributes
    for nid, node in original_graph.nodes.items():
        backbone.add_node(
            node_id=nid,
            name=node.name,
            cpu_capacity=node.cpu_capacity,
            ram_capacity=node.ram_capacity,
            storage_capacity=node.storage_capacity,
            tier=node.tier,
            x=node.x,
            y=node.y,
            region=node.region,
            **node.metadata
        )

    # Insert only the backbone edges
    for edge in mst_edges:
        backbone.add_edge(
            u=edge.u,
            v=edge.v,
            weight=edge.weight,
            bandwidth=edge.bandwidth,
            **edge.metadata
        )

    return backbone
