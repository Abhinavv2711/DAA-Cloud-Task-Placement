# ☁️ Cloud Task Placement Optimization
### Minimizing Average Latency via MST Backbone, Shortest Path Routing, and Multi-Capacity Knapsack Scheduling

**Design and Analysis of Algorithms (DAA) Capstone Project**  
**Repository:** Cloud Task Placement & Routing Optimization Engine

---

## 📌 Executive Summary
In distributed edge-cloud architectures, placing application replicas and virtual machines across physical server nodes is a fundamental optimization challenge. This repository provides an end-to-end algorithmic framework that:
1. **Models cloud servers** as nodes with multi-dimensional resource capacities (CPU, RAM) and physical links with latency weights (ms) using adjacency lists and custom priority queues.
2. **Extracts minimal-latency loop-free backbones** using **Prim's** and **Kruskal's** Minimum Spanning Tree (MST) algorithms, evaluating the trade-off between physical mesh routing and backbone tree routing.
3. **Implements adaptive shortest-path routing engines** using **Dijkstra**, **Bellman-Ford** (supporting negative edge weights and cycle detection), **Floyd-Warshall** ($O(V^3)$), and **Johnson's Algorithm** ($O(V^2 \log V + VE)$ with vertex potential reweighting).
4. **Optimizes task and replica placement** under multi-dimensional capacity constraints using:
   - **Greedy Heuristics:** Greedy Nearest Traffic (GNT) and Greedy Latency-Density (GLD).
   - **Dynamic Programming (Knapsack DP):** Multi-server 0/1 knapsack decomposition maximizing latency savings.
   - **Exact Optimizer (Branch & Bound):** Delivering provably globally optimal placements with admissible lower-bound pruning.
5. **Provides interactive deliverables:** Zero-dependency web dashboard (FastAPI backend with real-time SVG topology visualization), runnable Jupyter Notebook, and Gephi graph exports.

---

## 🗂️ Repository Structure

```text
DAA P/
├── api.py                           # FastAPI Server & REST API endpoints
├── cloud_task_placement.ipynb       # Interactive Jupyter Notebook
├── start_dashboard.bat              # One-click Windows launcher
├── requirements.txt                 # Project dependencies
├── README.md                        # Project documentation and quickstart
│
├── core/                            # Core Algorithm Package
│   ├── __init__.py                  # Package exports
│   ├── priority_queue.py            # Min-Heap Priority Queue with O(log N) decrease-key
│   ├── graph.py                     # Adjacency List Graph model & Gephi GEXF export
│   ├── mst.py                       # Prim & Kruskal MST and Backbone Extraction
│   ├── shortest_path.py             # Dijkstra, Bellman-Ford, Floyd-Warshall & Johnson
│   ├── placement.py                 # Greedy, Knapsack DP & Exact Branch-and-Bound
│   ├── topology_generator.py        # Campus, Fat-Tree, Regional Cloud & Waxman
│   └── benchmark.py                 # Automated experiment suite
│
├── data/                            # Datasets & Gephi Exports
│   ├── campus_network.json          # 16-node University Campus Network
│   ├── campus_backbone.json         # Campus MST Backbone subgraph
│   ├── campus_network.gexf          # Gephi graph export (Campus)
│   ├── campus_backbone.gexf         # Gephi graph export (Backbone)
│   ├── datacenter_fattree.json      # 20-node Fat-Tree Datacenter (k=4)
│   ├── datacenter_fattree.gexf      # Gephi graph export (Fat-Tree)
│   ├── regional_cloud.json          # 20-node Regional Cloud Backbone
│   ├── regional_cloud.gexf          # Gephi graph export (Regional Cloud)
│   ├── waxman_synthetic.json        # 30-node Waxman Random Geometric Graph
│   ├── waxman_synthetic.gexf        # Gephi graph export (Waxman)
│   └── benchmark_results/           # CSV results from empirical benchmarks
│       ├── mst_benchmark.csv
│       ├── shortest_path_benchmark.csv
│       ├── placement_benchmark.csv
│       └── backbone_tradeoffs.json
│
├── scripts/                         # Automation Scripts
│   ├── generate_datasets.py         # Generate sample datasets & Gephi files
│   ├── run_benchmarks.py            # Run complete empirical benchmark suite
│   └── generate_notebook.py         # Generate Jupyter Notebook
│
├── static/                          # Interactive Web Dashboard
│   └── index.html                   # Luxury-styled responsive SVG dashboard
│
└── tests/                           # Unit Test Suite
    └── test_all.py                  # Unit tests for all algorithms (8/8 passing)
```

---

## ⚡ Quickstart & How to Run

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run the Interactive Web Dashboard
```powershell
start_dashboard.bat
# or:
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```
*Opens the interactive web interface at http://localhost:8000 displaying topology visualization, MST backbone toggles, Dijkstra/Bellman-Ford route tracing, task placement solvers, and benchmark charts.*

### 3. Run the Unit Test Suite
```powershell
python -m unittest tests/test_all.py
```
*Executes all 8 test suites verifying Min-Heap Priority Queue, Prim/Kruskal equivalence, SSSP, APSP, negative-cycle detection, and placement solvers.*

### 4. Run the Empirical Benchmarking Suite
```powershell
python scripts/run_benchmarks.py
```
*Benchmarks Prim vs Kruskal up to $V=120$, Floyd-Warshall vs Johnson, and Greedy vs DP vs Exact placement under loose, normal, and tight capacities.*

### 5. Launch the Jupyter Notebook
```powershell
jupyter notebook cloud_task_placement.ipynb
```

---

## 🔬 Algorithmic Summary & Complexities

| Category | Algorithm | Time Complexity | Space Complexity | Key Feature / Theoretical Invariant |
| :--- | :--- | :---: | :---: | :--- |
| **Priority Queue** | Binary Min-Heap | $O(\log N)$ | $O(N)$ | $O(\log N)$ `decrease_key` via item-to-index tracking |
| **Backbone (MST)** | Kruskal | $O(E \log E)$ | $O(V + E)$ | DSU with Path Compression & Union by Rank ($O(\alpha(V))$) |
| **Backbone (MST)** | Prim | $O((V+E)\log V)$ | $O(V)$ | Priority Queue with Cut Property verification |
| **Routing (SSSP)** | Dijkstra | $O((V+E)\log V)$ | $O(V)$ | Optimal shortest paths for non-negative link latencies |
| **Routing (SSSP)** | Bellman-Ford | $O(V \cdot E)$ | $O(V)$ | Supports negative edge weights; detects negative cycles |
| **Routing (APSP)** | Floyd-Warshall | $O(V^3)$ | $O(V^2)$ | Dynamic programming; optimal for dense datacenters |
| **Routing (APSP)** | Johnson | $O(V^2 \log V + VE)$ | $O(V^2)$ | Reweights via vertex potentials $\hat{w}(u,v) \ge 0$; optimal for sparse graphs |
| **Placement** | Greedy Nearest (GNT) | $O(K \log K + K \cdot N)$ | $O(K + N)$ | Fast online heuristic; achieves $< 1.0\%$ optimality gap |
| **Placement** | Greedy Density (GLD) | $O(K \log K + K \cdot N)$ | $O(K + N)$ | Prioritizes tasks by traffic-to-resource footprint ratio |
| **Placement** | Knapsack DP | $O(N \cdot K \cdot \frac{C}{\Delta})$ | $O(K \cdot C)$ | Decomposes placement into multi-server knapsack states |
| **Placement** | Exact Optimizer | $O(N^K)$ worst-case | $O(K)$ | Branch & Bound with admissible lower bounds ($\text{LB}$) and pruning |

---

## 📊 Key Experimental Findings

1. **MST Density Crossover:**
   - On sparse topologies ($V=120, E=384$), Kruskal is **35.7% faster** ($1.178$ ms vs $1.834$ ms).
   - On dense topologies ($V=120, E=2997$), Prim is **31.6% faster** ($2.388$ ms vs $3.490$ ms).
   - Prim and Kruskal produced **100% identical total MST weights** across all runs.
2. **Backbone Pruning Efficiency:**
   - In the Campus Network, the MST backbone eliminates **46.43% of active links** (from 28 down to 15).
   - The average communication latency increases from 3.81 ms to 4.50 ms, representing a latency stretch of only **1.166x (+16.6%)**.
3. **Placement Solution Quality:**
   - **Greedy Nearest Traffic (GNT)** consistently achieves within **0.3% to 1.2%** of the mathematical global optimum while executing in $< 2.5$ ms.
   - Under tight capacity ($<60\%$), the **Exact Optimizer** experiences combinatorial explosion ($> 3000$ ms timeout), while **Knapsack DP** and **GNT** scale predictably.

---

## 👥 Authors & Academic Attribution
Developed for the **Design and Analysis of Algorithms (DAA)** curriculum.  
All algorithms implemented from first principles in standard Python with complete correctness proofs and reproducible benchmarks.
