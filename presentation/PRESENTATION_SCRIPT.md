# 15–20 Minute Presentation Script & Live Demo Walkthrough
## Cloud Task Placement Optimization: Backbone Topology, Shortest Path Routing, and Knapsack Dynamic Programming

**Target Audience:** DAA Professors, Evaluation Committee, and Peer Engineers  
**Duration:** 15 to 20 Minutes (Structured Presentation + Interactive Dashboard Demo + Q&A)  
**Accompanying Slide Deck:** `presentation/cloud_task_placement_presentation.pptx`  
**Live Demo Command:** `streamlit run app.py`

---

## ⏱️ Presentation Timing Breakdown

| Timestamp | Phase | Slide / Activity | Focus & Deliverable |
| :---: | :--- | :---: | :--- |
| **00:00 – 02:00** | Introduction & Context | Slides 1 – 2 | Problem Motivation: Edge-Cloud latency vs capacity tradeoffs. |
| **02:00 – 04:30** | Mathematical Formulation | Slide 3 | Graph definition, ILP formulation, proof sketch of NP-hardness. |
| **04:30 – 07:30** | Backbone Infrastructure | Slides 4 – 5 | Prim vs Kruskal, Cut Property proof, Backbone vs Mesh tradeoff. |
| **07:30 – 10:00** | Routing Foundations | Slide 6 | Dijkstra, Bellman-Ford, Floyd-Warshall vs Johnson reweighting. |
| **10:00 – 13:00** | Placement Optimization | Slides 7 – 9 | Greedy (GNT/GLD), Knapsack DP, Branch-and-Bound Exact. |
| **13:00 – 16:30** | **Live Interactive Demo** | Live Dashboard | Streamlit demonstration: topology, routing, placement, benchmarks. |
| **16:30 – 18:30** | Empirical Results & Policy | Slides 10 – 11 | Scalability tables, latency stretch, architectural policy rules. |
| **18:30 – 20:00** | Conclusion & Q&A | Slide 12 | Summary of deliverables, open floor for questions. |

---

## Slide-by-Slide Speaker Script

### Slide 1: Title Slide (00:00 – 01:00)
> *"Good morning, respected professors and peers. Today, we are presenting our project on **Cloud Task Placement Optimization: Minimizing Communication Latency via MST Backbone, Shortest Path Routing, and Multi-Capacity Knapsack Dynamic Programming**.*
>
> *In this project, we bridge classical graph algorithms—such as Kruskal's, Prim's, Dijkstra's, and Johnson's algorithms—with multi-capacity combinatorial optimization to solve one of the most pressing engineering bottlenecks in modern distributed cloud infrastructures: where to place virtual machines and application replicas so that end-to-end request latencies are minimized while physical compute and memory limits are strictly preserved."*

---

### Slide 2: Problem Motivation & Cloud Architecture (01:00 – 02:00)
> *"Why does this matter? In modern cloud environments—such as 5G edge networks, microservices, and multi-region clouds—over **70% of end-to-end request response times** are dictated by network communication latency rather than raw CPU processing time.*
>
> *Cloud orchestrators face a fundamental tension: client traffic originates from diverse geographic endpoints. To minimize latency, we want to place application replicas as close to these traffic hotspots as possible. However, servers have strictly finite physical capacities—namely CPU cores and RAM gigabytes. Stacking tasks onto a single optimal node causes capacity oversubscription and service crashes.*
>
> *Furthermore, physical network topologies contain redundant interconnections. While useful for fault tolerance, maintaining full-mesh routing tables introduces broadcast loops and forwarding table explosion. We address this using a two-tier approach: an MST backbone for structural coordination and shortest-path routing for data forwarding."*

---

### Slide 3: Formal Mathematical Formulation (02:00 – 04:30)
> *"Let us examine the mathematical formulation. We model the cloud network as an undirected weighted graph $G = (V, E, w, B)$, where vertices represent physical servers and edge weights represent physical link latencies in milliseconds.*
>
> *Each server $s$ possesses multi-dimensional capacities: $C_{\text{cpu}}(s)$ and $C_{\text{ram}}(s)$. We are given $K$ application tasks, each with resource demands $d_{\text{cpu}}(t)$ and $d_{\text{ram}}(t)$, and an ingress request traffic matrix $\lambda(c, t)$ from client nodes.*
>
> *Our goal is to find a binary assignment matrix $x_{t, s} \in \{0, 1\}$ that minimizes the total weighted communication latency:*
> $$\min \sum_{t \in T} \sum_{s \in V} x_{t, s} \sum_{c \in V} \lambda(c, t) \cdot D(c, s)$$
> *subject to each task being placed on exactly one server, and neither CPU nor RAM capacities being exceeded on any physical server.*
>
> *In Section 2 of our report, we prove that this problem is **strongly NP-Hard** via a reduction from the Multi-Dimensional Knapsack Problem and the Capacitated Metric Facility Location Problem. This formal hardness result proves that finding an exact polynomial-time algorithm is impossible unless $\text{P} = \text{NP}$, necessitating both efficient heuristics and pseudo-polynomial dynamic programming."*

---

### Slide 4: Backbone Synthesis: Prim vs Kruskal (04:30 – 06:00)
> *"To synthesize a loop-free, minimal-latency network backbone, we implemented both **Kruskal's Algorithm** and **Prim's Algorithm**.*
>
> *For Kruskal's algorithm, we implemented a custom Disjoint Set Union (DSU) data structure equipped with both Path Compression and Union by Rank, achieving nearly constant $O(\alpha(V))$ amortized operations and an overall time complexity of $O(E \log E)$.*
>
> *For Prim's algorithm, we implemented a custom Binary Min-Heap Priority Queue with an internal hash table that tracks heap indices, enabling true $O(\log V)$ decrease-key operations and achieving $O((V + E) \log V)$ runtime.*
>
> *We formally proved their correctness using the **Cut Property Theorem**, showing that any minimum-weight crossing edge across a cut is guaranteed to be safe in some MST. In our experiments, across all topologies, Prim's and Kruskal's algorithms produced **100% identical total backbone weights**."*

---

### Slide 5: Backbone vs Full-Mesh Tradeoff (06:00 – 07:30)
> *"A critical research question is: What price do we pay when routing exclusively over the MST backbone instead of the full physical mesh?*
>
> *We evaluated this on our 16-node University Campus Network:
> - Pruning to the MST backbone reduces active links from 28 to 15—a **46.43% link reduction**!
> - The average physical latency across all node pairs is 3.81 ms, while over the backbone it is 4.50 ms.
> - This represents an average **latency stretch of only 1.166x (or +16.6%)**.*
>
> *This provides a profound architectural insight: cloud orchestrators can disable or reserve nearly half of their switching links for control-plane and heartbeat traffic with only a modest 16% latency penalty."*

---

### Slide 6: Shortest-Path Routing Engine (07:30 – 10:00)
> *"For data plane routing, we built an adaptive routing engine:
> 1. **Dijkstra's Algorithm (SSSP):** For standard non-negative latency routing in $O((V+E)\log V)$.
> 2. **Bellman-Ford Algorithm (SSSP):** For scenarios where transit peering agreements offer negative effective latency credits, running in $O(V \cdot E)$ with early-stopping relaxation and negative-cycle detection.
> 3. **Floyd-Warshall (APSP):** Dynamic programming in $O(V^3)$, which we show is exceptionally fast on dense datacenters due to contiguous cache-friendly matrix operations.
> 4. **Johnson's Algorithm (APSP):** For sparse wide-area networks in $O(V^2 \log V + VE)$. We reweight edges using Bellman-Ford vertex potentials $h(u)$, proving that the new weights $\hat{w}(u, v) = w(u, v) + h(u) - h(v) \ge 0$ are strictly non-negative while preserving shortest paths."*

---

### Slide 7: Task Placement: Greedy Schedulers (10:00 – 11:30)
> *"To solve the replica placement problem, we first implemented two greedy schedulers:
> - **Greedy Nearest Traffic (GNT):** Sorts tasks by total traffic descending and greedily places each task on the feasible server with minimum aggregate client latency.
> - **Greedy Latency-Density (GLD):** Prioritizes tasks by traffic volume per unit CPU and RAM footprint.*
>
> *These greedy algorithms run in under **2.5 milliseconds** ($O(K \log K + K \cdot N)$). Remarkably, as we will demonstrate in the benchmarks, GNT achieves within **0.3% to 1.2% of the mathematically optimal placement**."*

---

### Slide 8: Dynamic Programming Knapsack Scheduler (11:30 – 12:30)
> *"To handle clustered workloads without server fragmentation, we designed a **Dynamic Programming Knapsack Scheduler**.*
>
> *We map latency minimization into a maximization problem: for each task, we compute the worst-case placement latency $L_{\text{worst}}(t)$. The latency savings from placing task $t$ on server $s$ is:
> $$\mathcal{V}(t, s) = L_{\text{worst}}(t) - L(t, s) \ge 0$$
>
> *We then solve 0/1 knapsack subproblems across servers sorted by topological closeness centrality. By discretizing CPU capacity states, the DP guarantees predictable pseudo-polynomial execution $O(N \cdot K \cdot C / \Delta)$ without exponential worst-case risk."*

---

### Slide 9: Exact Optimizer: Branch & Bound (12:30 – 13:00)
> *"To determine the true theoretical lower bound, we implemented an **Exact Optimizer** using Branch-and-Bound.
>
> *We developed an admissible lower-bounding heuristic:
> $$\text{LB} = C_{\text{current}} + \sum_{t \text{ unassigned}} \min_{s \in V} L(t, s)$$
> *Whenever current cost plus lower bound meets or exceeds the best-known incumbent, the entire subtree is pruned. We seed the initial incumbent with our GNT greedy solution, pruning more than 99% of search branches and solving realistic instances to global mathematical optimality."*

---

### Live Demo Walkthrough (13:00 – 16:30)
*(Switch screen to browser displaying Streamlit Dashboard: `streamlit run app.py`)*

> *"Now, let us walk through the live interactive demonstration of our system.*
>
> **Step 1: Network Topology Visualizer (Tab 1)**
> *Here you can see the 16-node University Campus Network rendered dynamically with Plotly. Nodes are color-coded by tier: blue for Core datacenters, green for Distribution switches, and orange for departmental compute clusters.*
>
> **Step 2: MST Backbone Extraction (Tab 2)**
> *Let's run Kruskal's algorithm. Notice how the red backbone edges connect all 16 nodes with exactly 15 edges, totaling 19.50 ms in latency weight. When we switch to Prim's algorithm, the total weight remains exactly 19.50 ms, confirming our correctness proof.*
>
> **Step 3: Shortest Path Routing (Tab 3)**
> *Let's select `Hostel-DC-A` as the source and `Medical-Edge` as the destination. The system computes the shortest route via Dijkstra, highlighting the 4-hop path and displaying the end-to-end latency of 5.8 ms in under 0.1 milliseconds.*
>
> **Step 4: Task Placement Optimization (Tab 4)**
> *Now let's deploy 12 synthetic VM replicas under a Pareto hotspot traffic pattern. First, let's run the Greedy Nearest Traffic solver: notice how average latency is 11.2 ms, with all tasks placed. Now let's run the Exact Optimizer: it achieves the global minimum latency of 11.03 ms. The server resource utilization bars confirm that neither CPU nor RAM capacities are violated.*
>
> **Step 5: Empirical Benchmarks (Tab 5)**
> *Finally, our benchmark tabs display real-time comparative charts: MST runtimes across 120 nodes, APSP speedups, and placement optimality gaps across capacity tightness regimes."*

---

### Slide 10: Experimental Benchmark Highlights (16:30 – 17:30)
*(Return to presentation slides)*

> *"Let us summarize the key empirical findings from our experiments:
> 1. **MST Density Crossover:** Kruskal is 35% faster on sparse graphs ($V=120, E=384: 1.18$ ms vs $1.83$ ms), whereas Prim is 31% faster on dense graphs ($V=120, E=2997: 2.39$ ms vs $3.49$ ms).
> 2. **Placement Optimality Gap:** Greedy Nearest Traffic achieved an optimality gap under **1.0%** across nearly all test cases while executing in $< 2.5$ ms.
> 3. **Computational Boundary:** When capacity is constrained ($<60\%$), the Exact Optimizer's search tree expands exponentially, reaching the 3-second safety cutoff, whereas GNT and DP execute deterministically in $\sim 2$ ms."*

---

### Slide 11: Policy Outputs & Deployment Decision Tree (17:30 – 18:30)
> *"Based on our findings, we formulate three clear engineering policies for cloud architects:
> 1. **Real-Time Admission Controller (< 5 ms SLA):** Deploy **Greedy Nearest Traffic (GNT)**. Its near-instantaneous execution and $< 1\%$ optimality gap make it the gold standard for online request dispatching.
> 2. **Batch Workload Rebalancing:** Deploy **Dynamic Programming (Knapsack DP)** during periodic rebalancing cycles to prevent server capacity fragmentation.
> 3. **Dual Network Plane Separation:** Route broadcast, synchronization, and telemetry over the **MST Backbone** (saving 46% of links), while routing latency-critical customer traffic over the full **Shortest-Path Mesh**."*

---

### Slide 12: Deliverables & Conclusion (18:30 – 20:00)
> *"To conclude, our complete project repository includes:
> - Production-grade modular Python code in `core/` (Graph, PriorityQueue, MST, Shortest Paths, Placement).
> - Datasets in JSON, CSV, and Gephi GEXF format (`data/`).
> - The interactive Streamlit Web Dashboard (`app.py`).
> - An interactive Jupyter Notebook (`cloud_task_placement.ipynb`).
> - A 10–12 page technical report with mathematical proofs (`docs/TECHNICAL_REPORT.md` and HTML).
> - This PowerPoint slide deck and speaker script.
>
> *Thank you very much for your time and attention. We would now be delighted to answer any questions."*

---

## ❓ Anticipated Questions & Model Answers

### Q1: Why does Kruskal outperform Prim on sparse graphs, but Prim wins on dense graphs?
> **Answer:**  
> *"Kruskal's runtime is dominated by edge sorting: $O(E \log E)$. On a sparse graph where $E \approx 2V$, sorting is very fast. Prim's runtime is $O((V + E) \log V)$ using a binary heap. On a dense graph where $E \approx V^2 / 2$, Kruskal must sort $V^2$ edges ($O(V^2 \log V)$), whereas Prim benefits from heap operations that process vertices and relax edges directly without global sorting. If a Fibonacci heap were used, Prim's theoretical complexity would drop to $O(E + V \log V)$."*

### Q2: Why is Johnson's Algorithm preferred over Floyd-Warshall for large transit networks?
> **Answer:**  
> *"Floyd-Warshall always runs in $O(V^3)$ time regardless of the number of edges. On a wide-area transit network with 1,000 routers and only 3,000 links ($E = 3V$), Floyd-Warshall requires $10^9$ operations. Johnson's algorithm runs in $O(V^2 \log V + VE) \approx 10^6 \times 10 + 3 \times 10^6 \approx 1.3 \times 10^7$ operations—nearly 100 times faster!"*

### Q3: How do you guarantee that Johnson's reweighting doesn't alter which path is shortest?
> **Answer:**  
> *"Because the reweighted path length telescopes! For any path $p$ from $u$ to $v$, $\hat{w}(p) = w(p) + h(u) - h(v)$. Since $h(u) - h(v)$ depends exclusively on the endpoints and is identical for every possible path between $u$ and $v$, any path that minimizes $\hat{w}(p)$ must also minimize the original weight $w(p)$."*

### Q4: Why did Greedy Nearest Traffic achieve such a small optimality gap (<1%)?
> **Answer:**  
> *"Because in metric latency spaces with hotspot client traffic, the objective function is dominated by proximity to the top traffic sources. Sorting tasks by traffic descending ensures that the tasks with the largest impact on the objective function claim the best server locations first, leaving only minor residuals for smaller tasks."*
