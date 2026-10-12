"""
Single-Source and All-Pairs Shortest Path Routing Algorithms.
Implements:
1. Dijkstra's Algorithm (SSSP, O((V + E) log V)) using Min-Heap Priority Queue.
2. Bellman-Ford Algorithm (SSSP, O(V * E)) with negative weight edge support and cycle detection.
3. Floyd-Warshall Algorithm (APSP, O(V^3)) Dynamic Programming for dense topologies.
4. Johnson's Algorithm (APSP, O(V^2 log V + V * E)) with vertex reweighting for sparse topologies.
5. Adaptive APSP dynamic selector and path reconstruction utilities.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import time
from .graph import Graph, Edge
from .priority_queue import PriorityQueue


def dijkstra_sssp(
    graph: Graph,
    source: str
) -> Tuple[Dict[str, float], Dict[str, Optional[str]], float]:
    """
    Dijkstra's Single-Source Shortest Path algorithm.
    Returns:
        (distances, predecessors, execution_time_seconds)
    Time Complexity: O((V + E) log V)
    Space Complexity: O(V)
    """
    start_time = time.perf_counter()
    source = str(source)
    if source not in graph.nodes:
        raise ValueError(f"Source node '{source}' not in graph")

    distances: Dict[str, float] = {node: float("inf") for node in graph.nodes}
    predecessors: Dict[str, Optional[str]] = {node: None for node in graph.nodes}
    distances[source] = 0.0

    pq = PriorityQueue()
    for node in graph.nodes:
        pq.push(node, distances[node])

    visited: Set[str] = set()

    while not pq.is_empty():
        u, dist_u = pq.pop()
        visited.add(u)

        if dist_u == float("inf"):
            break  # Remaining nodes are unreachable

        for edge in graph.get_out_edges(u):
            v = edge.v
            if v not in visited:
                new_dist = dist_u + edge.weight
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    predecessors[v] = u
                    pq.decrease_key(v, new_dist)

    exec_time = time.perf_counter() - start_time
    return distances, predecessors, exec_time


def bellman_ford_sssp(
    graph: Graph,
    source: str
) -> Tuple[Dict[str, float], Dict[str, Optional[str]], bool, float]:
    """
    Bellman-Ford Single-Source Shortest Path algorithm.
    Supports negative edge weights (e.g. latency credits / transit savings)
    and detects negative-weight cycles.
    Returns:
        (distances, predecessors, has_negative_cycle, execution_time_seconds)
    Time Complexity: O(V * E)
    Space Complexity: O(V)
    """
    start_time = time.perf_counter()
    source = str(source)
    if source not in graph.nodes:
        raise ValueError(f"Source node '{source}' not in graph")

    distances: Dict[str, float] = {node: float("inf") for node in graph.nodes}
    predecessors: Dict[str, Optional[str]] = {node: None for node in graph.nodes}
    distances[source] = 0.0

    nodes_list = list(graph.nodes.keys())
    num_nodes = len(nodes_list)

    # In directed mode, get all directed edges; in undirected mode, edges can be traversed both ways
    all_edges: List[Edge] = []
    if graph.directed:
        for u in graph.adj:
            all_edges.extend(graph.adj[u])
    else:
        for u in graph.adj:
            all_edges.extend(graph.adj[u])

    # Relax edges up to V - 1 times
    for _ in range(num_nodes - 1):
        updated = False
        for edge in all_edges:
            u, v, w = edge.u, edge.v, edge.weight
            if distances[u] != float("inf") and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                predecessors[v] = u
                updated = True
        if not updated:
            break  # Early termination if no relaxation occurred

    # Check for negative-weight cycles
    has_negative_cycle = False
    for edge in all_edges:
        u, v, w = edge.u, edge.v, edge.weight
        if distances[u] != float("inf") and distances[u] + w < distances[v]:
            has_negative_cycle = True
            break

    exec_time = time.perf_counter() - start_time
    return distances, predecessors, has_negative_cycle, exec_time


def floyd_warshall_apsp(
    graph: Graph
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, Optional[str]]], float]:
    """
    Floyd-Warshall All-Pairs Shortest Paths dynamic programming algorithm.
    Best suited for dense topologies (E ~ V^2).
    Returns:
        (distance_matrix, next_hop_matrix, execution_time_seconds)
    Time Complexity: O(V^3)
    Space Complexity: O(V^2)
    """
    start_time = time.perf_counter()
    nodes = list(graph.nodes.keys())
    dist: Dict[str, Dict[str, float]] = {u: {v: float("inf") for v in nodes} for u in nodes}
    nxt: Dict[str, Dict[str, Optional[str]]] = {u: {v: None for v in nodes} for u in nodes}

    # Initialize self-distances and direct edges
    for u in nodes:
        dist[u][u] = 0.0
        nxt[u][u] = u

    for u in nodes:
        for edge in graph.get_out_edges(u):
            v, w = edge.v, edge.weight
            if w < dist[u][v]:
                dist[u][v] = w
                nxt[u][v] = v

    # Dynamic Programming relaxation over intermediate vertices k
    for k in nodes:
        dist_k = dist[k]
        for i in nodes:
            dist_i_k = dist[i][k]
            if dist_i_k == float("inf"):
                continue
            dist_i = dist[i]
            nxt_i = nxt[i]
            nxt_i_k = nxt_i[k]
            for j in nodes:
                cost = dist_i_k + dist_k[j]
                if cost < dist_i[j]:
                    dist_i[j] = cost
                    nxt_i[j] = nxt_i_k

    exec_time = time.perf_counter() - start_time
    return dist, nxt, exec_time


def johnson_apsp(
    graph: Graph
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, Optional[str]]], float]:
    """
    Johnson's All-Pairs Shortest Paths algorithm.
    Reweights edges using Bellman-Ford potential function h(u), then executes
    Dijkstra's algorithm from every vertex.
    Best suited for sparse topologies (E << V^2).
    Returns:
        (distance_matrix, predecessor_matrix, execution_time_seconds)
    Time Complexity: O(V^2 log V + V * E)
    Space Complexity: O(V^2)
    """
    start_time = time.perf_counter()
    nodes = list(graph.nodes.keys())

    # Step 1: Create auxiliary graph G' with dummy node q connected to all vertices with weight 0
    dummy_source = "__johnson_dummy_source__"
    aux_graph = graph.copy()
    aux_graph.add_node(dummy_source)
    for u in nodes:
        aux_graph.add_edge(dummy_source, u, weight=0.0)

    # Step 2: Run Bellman-Ford on G' from dummy node to calculate vertex potentials h(u)
    h_potentials, _, has_neg_cycle, _ = bellman_ford_sssp(aux_graph, dummy_source)
    if has_neg_cycle:
        raise ValueError("Graph contains a negative weight cycle; shortest paths are undefined")

    # Step 3: Create reweighted graph G_hat with edge weights w'(u, v) = w(u, v) + h(u) - h(v) >= 0
    reweighted_graph = Graph(directed=graph.directed)
    for nid, node in graph.nodes.items():
        reweighted_graph.add_node(
            nid,
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

    for edge in graph.get_all_edges(deduplicate_undirected=False):
        u, v, w = edge.u, edge.v, edge.weight
        reweighted_w = max(0.0, w + h_potentials[u] - h_potentials[v])
        reweighted_graph.add_edge(u, v, weight=reweighted_w, bandwidth=edge.bandwidth, **edge.metadata)

    # Step 4: Run Dijkstra from every node on reweighted graph
    dist_matrix: Dict[str, Dict[str, float]] = {u: {} for u in nodes}
    pred_matrix: Dict[str, Dict[str, Optional[str]]] = {u: {} for u in nodes}

    for u in nodes:
        dijk_dists, dijk_preds, _ = dijkstra_sssp(reweighted_graph, u)
        # Step 5: Restore original distances: d(u, v) = d'(u, v) - h(u) + h(v)
        for v in nodes:
            if dijk_dists[v] == float("inf"):
                dist_matrix[u][v] = float("inf")
            else:
                dist_matrix[u][v] = round(dijk_dists[v] - h_potentials[u] + h_potentials[v], 4)
        pred_matrix[u] = dijk_preds

    exec_time = time.perf_counter() - start_time
    return dist_matrix, pred_matrix, exec_time


def compute_apsp(
    graph: Graph,
    algorithm: str = "auto"
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Any], str, float]:
    """
    Adaptive All-Pairs Shortest Path solver.
    Dynamically picks Floyd-Warshall or Johnson based on graph density and negative weights.
    Returns:
        (distance_matrix, routing_metadata, chosen_algorithm_name, execution_time_seconds)
    """
    has_negative_weights = any(e.weight < 0 for e in graph.get_all_edges(deduplicate_undirected=True))
    v = graph.num_nodes
    e = graph.num_edges
    # Threshold: Johnson has complexity O(V^2 log V + VE), Floyd-Warshall is O(V^3).
    # Floyd-Warshall is preferred when graph is dense (E > 0.25 * V^2) or graph is small (V <= 25).
    use_johnson = (e < 0.25 * v * v and v > 20)

    if algorithm == "floyd_warshall":
        dist, nxt, t = floyd_warshall_apsp(graph)
        return dist, {"next": nxt}, "Floyd-Warshall", t
    elif algorithm == "johnson":
        dist, pred, t = johnson_apsp(graph)
        return dist, {"predecessors": pred}, "Johnson", t
    else:  # auto
        if use_johnson and not graph.directed:
            # Undirected graphs with negative edges cannot run Dijkstra without cycle risks,
            # but if non-negative, Johnson is extremely fast for sparse graphs
            if not has_negative_weights:
                dist, pred, t = johnson_apsp(graph)
                return dist, {"predecessors": pred}, "Johnson", t
            else:
                dist, nxt, t = floyd_warshall_apsp(graph)
                return dist, {"next": nxt}, "Floyd-Warshall", t
        elif use_johnson:
            dist, pred, t = johnson_apsp(graph)
            return dist, {"predecessors": pred}, "Johnson", t
        else:
            dist, nxt, t = floyd_warshall_apsp(graph)
            return dist, {"next": nxt}, "Floyd-Warshall", t


def reconstruct_path(
    source: str,
    target: str,
    predecessors_or_next: Dict[str, Any],
    is_next_matrix: bool = False
) -> Tuple[List[str], float]:
    """
    Reconstruct the explicit path list [source, ..., target] from routing metadata.
    """
    source, target = str(source), str(target)
    if source == target:
        return [source], 0.0

    path: List[str] = []

    if is_next_matrix:
        # Floyd-Warshall next-hop matrix: next_matrix[u][v] gives next hop from u to v
        nxt = predecessors_or_next
        if nxt.get(source, {}).get(target) is None:
            return [], float("inf")
        curr = source
        visited = set()
        while curr != target:
            path.append(curr)
            visited.add(curr)
            curr = nxt[curr][target]
            if curr is None or curr in visited:
                return [], float("inf")  # Loop or unreachable
        path.append(target)
        return path, 0.0
    else:
        # Predecessor mapping: preds[v] gives node before v on path from source
        preds = predecessors_or_next
        curr: Optional[str] = target
        visited = set()
        while curr is not None:
            path.append(curr)
            if curr == source:
                break
            if curr in visited:
                return [], float("inf")  # Cycle detected
            visited.add(curr)
            curr = preds.get(curr)

        if not path or path[-1] != source:
            return [], float("inf")  # Unreachable

        path.reverse()
        return path, 0.0
