"""
Comprehensive Unit Test Suite for Cloud Task Placement Algorithms.
Tests PriorityQueue, Graph, MST (Prim/Kruskal), Shortest Paths (Dijkstra, Bellman-Ford, Floyd-Warshall, Johnson),
and Placement Optimization (Greedy, DP Knapsack, Exact Optimizer).
"""

import unittest
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.priority_queue import PriorityQueue
from core.graph import Graph
from core.mst import prim_mst, kruskal_mst, extract_backbone_graph
from core.shortest_path import (
    dijkstra_sssp,
    bellman_ford_sssp,
    floyd_warshall_apsp,
    johnson_apsp,
    reconstruct_path
)
from core.placement import (
    Task,
    greedy_nearest_traffic_placement,
    greedy_latency_density_placement,
    dp_knapsack_placement,
    exact_optimal_placement
)


class TestPriorityQueue(unittest.TestCase):
    def test_basic_operations(self):
        pq = PriorityQueue()
        self.assertTrue(pq.is_empty())
        pq.push("A", 10.0)
        pq.push("B", 5.0)
        pq.push("C", 20.0)

        self.assertEqual(len(pq), 3)
        self.assertEqual(pq.peek(), ("B", 5.0))

        item, p = pq.pop()
        self.assertEqual((item, p), ("B", 5.0))
        self.assertEqual(len(pq), 2)

    def test_decrease_key(self):
        pq = PriorityQueue()
        pq.push("X", 50.0)
        pq.push("Y", 30.0)
        pq.push("Z", 40.0)

        pq.decrease_key("X", 10.0)
        self.assertEqual(pq.peek(), ("X", 10.0))
        item, p = pq.pop()
        self.assertEqual(item, "X")
        self.assertEqual(p, 10.0)


class TestGraphAndMST(unittest.TestCase):
    def setUp(self):
        self.g = Graph(directed=False)
        # 5-node test graph
        # A-B (1), A-C (7), B-C (5), B-D (4), B-E (3), C-E (6), D-E (2)
        edges = [
            ("A", "B", 1.0),
            ("A", "C", 7.0),
            ("B", "C", 5.0),
            ("B", "D", 4.0),
            ("B", "E", 3.0),
            ("C", "E", 6.0),
            ("D", "E", 2.0),
        ]
        for u, v, w in edges:
            self.g.add_edge(u, v, weight=w)

    def test_kruskal_and_prim_equivalence(self):
        k_edges, k_weight, _ = kruskal_mst(self.g)
        p_edges, p_weight, _ = prim_mst(self.g, start_node="A")

        self.assertEqual(len(k_edges), 4)  # V - 1 = 5 - 1 = 4
        self.assertEqual(len(p_edges), 4)
        self.assertAlmostEqual(k_weight, 11.0)  # 1 (A-B) + 3 (B-E) + 2 (D-E) + 5 (B-C) = 11.0
        self.assertAlmostEqual(p_weight, 11.0)
        self.assertAlmostEqual(k_weight, p_weight)

    def test_backbone_extraction(self):
        k_edges, _, _ = kruskal_mst(self.g)
        bb = extract_backbone_graph(self.g, k_edges)
        self.assertEqual(bb.num_nodes, self.g.num_nodes)
        self.assertEqual(bb.num_edges, 4)


class TestShortestPath(unittest.TestCase):
    def setUp(self):
        self.g = Graph(directed=True)
        # Directed graph with known shortest paths
        self.g.add_edge("1", "2", 3.0)
        self.g.add_edge("1", "3", 8.0)
        self.g.add_edge("1", "5", -4.0)
        self.g.add_edge("2", "4", 1.0)
        self.g.add_edge("2", "5", 7.0)
        self.g.add_edge("3", "2", 4.0)
        self.g.add_edge("4", "1", 2.0)
        self.g.add_edge("4", "3", -5.0)
        self.g.add_edge("5", "4", 6.0)

    def test_bellman_ford(self):
        dists, preds, has_neg, _ = bellman_ford_sssp(self.g, "1")
        self.assertFalse(has_neg)
        self.assertEqual(dists["1"], 0.0)
        self.assertEqual(dists["2"], 1.0)  # 1->5 ( -4 ) + 5->4 ( 6 ) + 4->3 ( -5 ) + 3->2 ( 4 ) = 1
        self.assertEqual(dists["3"], -3.0) # 1->5 (-4) + 5->4 (6) + 4->3 (-5) = -3
        self.assertEqual(dists["4"], 2.0)  # 1->5 (-4) + 5->4 (6) = 2
        self.assertEqual(dists["5"], -4.0)

    def test_floyd_warshall_and_johnson_agreement(self):
        fw_dist, _, _ = floyd_warshall_apsp(self.g)
        jn_dist, _, _ = johnson_apsp(self.g)

        nodes = list(self.g.nodes.keys())
        for u in nodes:
            for v in nodes:
                self.assertAlmostEqual(fw_dist[u][v], jn_dist[u][v], places=3)

    def test_negative_cycle_detection(self):
        bad_g = Graph(directed=True)
        bad_g.add_edge("A", "B", 1.0)
        bad_g.add_edge("B", "C", -3.0)
        bad_g.add_edge("C", "A", 1.0)  # Sum = -1 cycle
        _, _, has_neg, _ = bellman_ford_sssp(bad_g, "A")
        self.assertTrue(has_neg)


class TestPlacementOptimization(unittest.TestCase):
    def setUp(self):
        # 3 servers with latencies
        self.servers = {
            "S1": {"cpu_capacity": 16.0, "ram_capacity": 64.0},
            "S2": {"cpu_capacity": 16.0, "ram_capacity": 64.0},
            "S3": {"cpu_capacity": 8.0, "ram_capacity": 32.0},
        }
        self.dist_matrix = {
            "S1": {"S1": 0.0, "S2": 10.0, "S3": 25.0},
            "S2": {"S1": 10.0, "S2": 0.0, "S3": 15.0},
            "S3": {"S1": 25.0, "S2": 15.0, "S3": 0.0},
        }
        self.tasks = [
            Task(task_id="T1", cpu_demand=4.0, ram_demand=16.0, traffic={"S1": 100.0, "S2": 10.0}),
            Task(task_id="T2", cpu_demand=8.0, ram_demand=32.0, traffic={"S2": 80.0, "S3": 20.0}),
            Task(task_id="T3", cpu_demand=4.0, ram_demand=16.0, traffic={"S3": 90.0, "S1": 10.0}),
        ]

    def test_schedulers(self):
        res_gnt = greedy_nearest_traffic_placement(self.tasks, self.servers, self.dist_matrix)
        res_dp = dp_knapsack_placement(self.tasks, self.servers, self.dist_matrix)
        res_exact = exact_optimal_placement(self.tasks, self.servers, self.dist_matrix)

        self.assertEqual(len(res_gnt.placements), 3)
        self.assertEqual(len(res_dp.placements), 3)
        self.assertEqual(len(res_exact.placements), 3)

        # Exact optimizer must achieve equal or lower total latency than heuristics
        self.assertLessEqual(res_exact.total_latency, res_gnt.total_latency + 1e-4)
        self.assertLessEqual(res_exact.total_latency, res_dp.total_latency + 1e-4)


if __name__ == "__main__":
    unittest.main()
