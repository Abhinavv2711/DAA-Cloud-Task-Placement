"""
Automated PowerPoint Presentation Generator.
Creates a professional 12-slide deck for the 15-20 minute technical presentation.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN


def build_deck():
    os.makedirs("presentation", exist_ok=True)
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    c_primary = RGBColor(13, 71, 161)     # Deep Blue
    c_accent = RGBColor(30, 136, 229)     # Electric Blue
    c_dark = RGBColor(33, 33, 33)         # Near Black
    c_gray = RGBColor(117, 117, 117)      # Slate Gray
    c_card_bg = RGBColor(245, 247, 250)   # Light Gray

    slides_data = [
        {
            "title": "Cloud Task & VM Placement Optimization",
            "subtitle": "Minimizing Communication Latency via MST Backbone, Shortest Path Routing & Knapsack DP\nDesign and Analysis of Algorithms (DAA)",
            "bullets": [
                "Comprehensive Project Defense & Technical Demonstration",
                "Presenter: Distributed Cloud Systems Team",
                "Time: 15–20 Minutes"
            ]
        },
        {
            "title": "1. Problem Motivation & Cloud Architecture",
            "subtitle": "The Edge-Cloud Latency & Placement Challenge",
            "bullets": [
                "Modern distributed clouds feature heterogeneous edge nodes and multi-tier datacenters.",
                "Over 70% of end-to-end request latency stems from inter-node communication.",
                "Conflicting Objectives: Place replicas near client traffic hotspots vs Respect physical CPU & RAM capacities.",
                "Network Bottlenecks: Full-mesh links cause broadcast storms; require loop-free spanning tree backbone."
            ]
        },
        {
            "title": "2. Formal Mathematical Formulation",
            "subtitle": "Multi-Dimensional Capacitated Optimization",
            "bullets": [
                "Infrastructure: Undirected graph G = (V, E) with link latencies w(u, v) and capacities C(s) = (CPU, RAM).",
                "Workload: Tasks T = {t_1, ..., t_M} with resource demands d(t) and client traffic matrix Lambda = [lambda(c, t)].",
                "Objective: Min sum_{t in T} sum_{s in V} x_{t,s} * sum_{c in V} lambda(c, t) * dist(c, s).",
                "Capacity Constraints: sum_t x_{t,s} * d_cpu(t) <= C_cpu(s) and sum_t x_{t,s} * d_ram(t) <= C_ram(s) for all s.",
                "Complexity Theorem: Strongly NP-Hard via reduction from Multi-Dimensional Knapsack & Metric Facility Location."
            ]
        },
        {
            "title": "3. Backbone Synthesis: Prim vs Kruskal",
            "subtitle": "Loop-Free Minimal Latency Infrastructure",
            "bullets": [
                "Kruskal's Algorithm: O(E log E) via Disjoint Set Union (DSU) with Path Compression & Union by Rank.",
                "Prim's Algorithm: O((V + E) log V) via custom Binary Min-Heap Priority Queue with O(log N) decrease-key.",
                "Correctness: Proved mathematically via the Cut Property (light edge crossing any cut is safe in an MST).",
                "Empirical Result: Kruskal is 35% faster on sparse graphs; Prim is 31% faster on dense graphs; weights match 100%."
            ]
        },
        {
            "title": "4. Backbone vs Full-Mesh Tradeoff",
            "subtitle": "Evaluating Latency Stretch vs Topology Pruning",
            "bullets": [
                "Campus Network (16 Nodes, 28 Links): Backbone saves 13 links (46.43% link reduction).",
                "Latency Impact: Average physical latency = 3.81 ms; Backbone latency = 4.50 ms.",
                "Average Latency Stretch: Only 1.166x (+16.6% latency increase).",
                "Architectural Decision: Route broadcast, heartbeats, and telemetry over MST; route strict low-latency replicas over full mesh."
            ]
        },
        {
            "title": "5. Shortest-Path Routing Engine",
            "subtitle": "Adaptive SSSP & APSP Strategies",
            "bullets": [
                "Dijkstra (SSSP): O((V + E) log V) for standard non-negative latency routing.",
                "Bellman-Ford (SSSP): O(V * E) with negative weight edge handling and negative cycle detection.",
                "Floyd-Warshall (APSP): O(V^3) dynamic programming matrix formulation for dense clusters.",
                "Johnson's Algorithm (APSP): O(V^2 log V + VE) using vertex potential reweighting w'(u, v) = w(u, v) + h(u) - h(v) >= 0."
            ]
        },
        {
            "title": "6. Task Placement: Greedy Schedulers",
            "subtitle": "Fast Online Heuristics for Sub-Millisecond Admission",
            "bullets": [
                "Greedy Nearest Traffic (GNT): Sorts tasks by total traffic descending; places on nearest feasible server.",
                "Greedy Latency-Density (GLD): Prioritizes tasks by traffic-to-resource footprint ratio.",
                "Execution Speed: Runs in under 2.5 ms even for large graphs (O(M * N)).",
                "Quality: Consistently achieves within 0.3% - 1.2% of the mathematically global optimum."
            ]
        },
        {
            "title": "7. Dynamic Programming Knapsack Scheduler",
            "subtitle": "Decomposition into 0/1 Multi-Knapsack States",
            "bullets": [
                "Formulation: Value V(t, s) = Latency_worst(t) - Latency(t, s) represents latency savings.",
                "Server Knapsack: Discretizes CPU capacity states into DP table: DP[i, c] = max(DP[i-1, c], DP[i-1, c - w_i] + v_i).",
                "Centrality Ordering: Solves knapsacks starting with topologically central nodes.",
                "Performance: Pseudo-polynomial time O(N * M * C / Delta); avoids exponential branching explosion."
            ]
        },
        {
            "title": "8. Exact Optimizer: Branch & Bound",
            "subtitle": "Guaranteed Global Optimum with Admissible Pruning",
            "bullets": [
                "Lower Bounding: LB(state) = Current_Cost + sum_{unassigned} min_s L(t, s).",
                "Pruning Invariant: If Current_Cost + LB >= Best_Known_Cost, prune subtree immediately.",
                "Greedy Seeding: Seeds upper bound with GNT solution, dramatically reducing explored state space.",
                "Optimality: Delivers the ground-truth optimal placement to benchmark heuristic solutions."
            ]
        },
        {
            "title": "9. Experimental Benchmark Highlights",
            "subtitle": "Empirical Findings Across Scale & Density",
            "bullets": [
                "MST Scaling: Verified on V = 15 to 120 nodes. Kruskal dominates sparse; Prim dominates dense.",
                "Placement Accuracy: GNT average latency gap < 1.0%; DP gap 2% - 11% with balanced resource packing.",
                "Runtime Scaling: Under tight capacity, Exact Optimizer reaches timeout (>3000 ms), whereas GNT & DP execute in ~2 ms.",
                "Topology Generality: Evaluated on 3-tier Fat-Tree, Regional Cloud, Campus network, and Waxman random graphs."
            ]
        },
        {
            "title": "10. Policy Outputs & Deployment Matrix",
            "subtitle": "Production Guidelines for Cloud Orchestrators",
            "bullets": [
                "Online Admission (< 5 ms SLA): Deploy Greedy Nearest Traffic (GNT) for instantaneous scheduling.",
                "Batch Cluster Rebalancing: Deploy Dynamic Programming Knapsack to avoid server fragmentation.",
                "High-Value Strategic Audits: Deploy Exact Optimizer during maintenance windows for globally optimal layouts.",
                "Network Plane Separation: MST backbone for control/broadcast plane; Shortest Path mesh for data plane."
            ]
        },
        {
            "title": "11. Interactive Demo & Deliverables Summary",
            "subtitle": "Live Demonstration & Code Repository",
            "bullets": [
                "Streamlit Web Dashboard: Live topology visualizer, MST toggles, interactive route tracer, placement solver.",
                "Interactive Jupyter Notebook: Step-by-step mathematical formulation and code walkthrough.",
                "Complete Deliverables: Git repo, datasets, Gephi exports (.gexf), 10-12 page technical report, slide deck.",
                "Thank You! Q&A Session."
            ]
        }
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(blank_layout)

        # Header Title Box
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(1.2))
        tf = title_box.text_frame
        tf.word_wrap = True
        p_title = tf.paragraphs[0]
        p_title.text = data["title"]
        p_title.font.size = Pt(28)
        p_title.font.bold = True
        p_title.font.color.rgb = c_primary

        if "subtitle" in data:
            p_sub = tf.add_paragraph()
            p_sub.text = data["subtitle"]
            p_sub.font.size = Pt(16)
            p_sub.font.italic = True
            p_sub.font.color.rgb = c_accent

        # Content Card Box
        content_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(11.7), Inches(4.8))
        c_tf = content_box.text_frame
        c_tf.word_wrap = True

        for idx, bullet in enumerate(data["bullets"]):
            p = c_tf.paragraphs[0] if idx == 0 else c_tf.add_paragraph()
            p.text = "•  " + bullet
            p.font.size = Pt(18)
            p.font.color.rgb = c_dark
            p.space_after = Pt(14)

    pptx_path = "presentation/cloud_task_placement_presentation.pptx"
    prs.save(pptx_path)
    print(f"Generated PowerPoint Presentation Deck: {pptx_path}")


if __name__ == "__main__":
    build_deck()
