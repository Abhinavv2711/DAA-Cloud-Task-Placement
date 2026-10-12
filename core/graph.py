"""
Graph Model Representation using Adjacency Lists.
Models cloud servers as nodes with resource capacities and physical links as weighted edges.
Supports directed and undirected graphs, adjacency lists, export to Gephi GEXF / CSV / NetworkX.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import json
import xml.etree.ElementTree as ET


@dataclass
class Edge:
    u: str
    v: str
    weight: float  # Latency in milliseconds (ms)
    bandwidth: float = 1000.0  # Mbps
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "u": self.u,
            "v": self.v,
            "weight": self.weight,
            "bandwidth": self.bandwidth,
            "metadata": self.metadata
        }


@dataclass
class ServerNode:
    node_id: str
    name: str = ""
    cpu_capacity: float = 64.0  # CPU Cores
    ram_capacity: float = 256.0  # RAM in GB
    storage_capacity: float = 2000.0  # Storage in GB
    tier: str = "standard"  # 'core', 'aggregation', 'edge', 'datacenter'
    x: float = 0.0  # Visualization 2D coordinates
    y: float = 0.0
    region: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            self.name = self.node_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "cpu_capacity": self.cpu_capacity,
            "ram_capacity": self.ram_capacity,
            "storage_capacity": self.storage_capacity,
            "tier": self.tier,
            "x": self.x,
            "y": self.y,
            "region": self.region,
            "metadata": self.metadata
        }


class Graph:
    """
    Cloud network topology graph backed by an adjacency list representation.
    """

    def __init__(self, directed: bool = False):
        self.directed: bool = directed
        self.nodes: Dict[str, ServerNode] = {}
        # Adjacency list: u -> list of (v, weight, edge_obj)
        self.adj: Dict[str, List[Edge]] = {}

    def add_node(
        self,
        node_id: str,
        name: str = "",
        cpu_capacity: float = 64.0,
        ram_capacity: float = 256.0,
        storage_capacity: float = 2000.0,
        tier: str = "standard",
        x: float = 0.0,
        y: float = 0.0,
        region: str = "default",
        **kwargs
    ) -> ServerNode:
        """Add or update a server node in the graph."""
        node = ServerNode(
            node_id=str(node_id),
            name=name or str(node_id),
            cpu_capacity=float(cpu_capacity),
            ram_capacity=float(ram_capacity),
            storage_capacity=float(storage_capacity),
            tier=tier,
            x=float(x),
            y=float(y),
            region=region,
            metadata=kwargs
        )
        self.nodes[node.node_id] = node
        if node.node_id not in self.adj:
            self.adj[node.node_id] = []
        return node

    def add_edge(
        self,
        u: str,
        v: str,
        weight: float,
        bandwidth: float = 1000.0,
        **kwargs
    ) -> Edge:
        """
        Add a weighted edge between nodes u and v.
        Weight represents link latency in milliseconds.
        """
        u = str(u)
        v = str(v)

        if u not in self.nodes:
            self.add_node(u)
        if v not in self.nodes:
            self.add_node(v)

        # Check if edge already exists, update if found
        existing_edge = self.get_edge(u, v)
        if existing_edge:
            existing_edge.weight = float(weight)
            existing_edge.bandwidth = float(bandwidth)
            existing_edge.metadata.update(kwargs)
            if not self.directed:
                reverse = self.get_edge(v, u)
                if reverse:
                    reverse.weight = float(weight)
                    reverse.bandwidth = float(bandwidth)
                    reverse.metadata.update(kwargs)
            return existing_edge

        edge = Edge(u=u, v=v, weight=float(weight), bandwidth=float(bandwidth), metadata=kwargs)
        self.adj[u].append(edge)

        if not self.directed and u != v:
            rev_edge = Edge(u=v, v=u, weight=float(weight), bandwidth=float(bandwidth), metadata=kwargs)
            self.adj[v].append(rev_edge)

        return edge

    def get_node(self, node_id: str) -> Optional[ServerNode]:
        return self.nodes.get(str(node_id))

    def get_neighbors(self, u: str) -> List[Tuple[str, float]]:
        """Return list of (neighbor_id, latency_weight) for node u."""
        u = str(u)
        if u not in self.adj:
            return []
        return [(edge.v, edge.weight) for edge in self.adj[u]]

    def get_out_edges(self, u: str) -> List[Edge]:
        return self.adj.get(str(u), [])

    def get_edge(self, u: str, v: str) -> Optional[Edge]:
        u, v = str(u), str(v)
        for edge in self.adj.get(u, []):
            if edge.v == v:
                return edge
        return None

    def get_edge_weight(self, u: str, v: str) -> Optional[float]:
        edge = self.get_edge(u, v)
        return edge.weight if edge else None

    @property
    def num_nodes(self) -> int:
        return len(self.nodes)

    @property
    def num_edges(self) -> int:
        all_edges = self.get_all_edges()
        return len(all_edges)

    def get_all_edges(self, deduplicate_undirected: bool = True) -> List[Edge]:
        """Return all distinct edges in the graph."""
        edges: List[Edge] = []
        seen = set()
        for u in self.adj:
            for edge in self.adj[u]:
                if not self.directed and deduplicate_undirected:
                    pair = tuple(sorted([edge.u, edge.v]))
                    if pair in seen:
                        continue
                    seen.add(pair)
                edges.append(edge)
        return edges

    def density(self) -> float:
        """Graph density in range [0, 1]."""
        n = self.num_nodes
        if n <= 1:
            return 0.0
        m = self.num_edges
        max_edges = n * (n - 1) if self.directed else (n * (n - 1)) / 2.0
        return m / max_edges if max_edges > 0 else 0.0

    def degree(self, node_id: str) -> int:
        return len(self.adj.get(str(node_id), []))

    def copy(self) -> "Graph":
        """Return a deep copy of the graph."""
        g = Graph(directed=self.directed)
        for nid, node in self.nodes.items():
            g.add_node(
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
        for edge in self.get_all_edges(deduplicate_undirected=True):
            g.add_edge(edge.u, edge.v, edge.weight, edge.bandwidth, **edge.metadata)
        return g

    def to_dict(self) -> Dict[str, Any]:
        return {
            "directed": self.directed,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.get_all_edges(deduplicate_undirected=True)]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Graph":
        g = cls(directed=data.get("directed", False))
        for nd in data.get("nodes", []):
            g.add_node(
                node_id=nd["node_id"],
                name=nd.get("name", ""),
                cpu_capacity=nd.get("cpu_capacity", 64.0),
                ram_capacity=nd.get("ram_capacity", 256.0),
                storage_capacity=nd.get("storage_capacity", 2000.0),
                tier=nd.get("tier", "standard"),
                x=nd.get("x", 0.0),
                y=nd.get("y", 0.0),
                region=nd.get("region", "default"),
                **nd.get("metadata", {})
            )
        for ed in data.get("edges", []):
            g.add_edge(
                u=ed["u"],
                v=ed["v"],
                weight=ed["weight"],
                bandwidth=ed.get("bandwidth", 1000.0),
                **ed.get("metadata", {})
            )
        return g

    def export_to_json(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str) -> "Graph":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def export_to_gephi_gexf(self, filepath: str) -> None:
        """
        Export graph in GEXF format compatible with Gephi graph visualization software.
        """
        gexf = ET.Element("gexf", xmlns="http://www.gexf.net/1.2draft", version="1.2")
        meta = ET.SubElement(gexf, "meta")
        ET.SubElement(meta, "creator").text = "CloudTaskPlacementOptimizer"
        ET.SubElement(meta, "description").text = "Cloud Server Topology with Link Latencies"

        graph_type = "directed" if self.directed else "undirected"
        graph_elem = ET.SubElement(gexf, "graph", defaultedgetype=graph_type, mode="static")

        # Node attributes definition
        node_attrs = ET.SubElement(graph_elem, "attributes", {"class": "node"})
        ET.SubElement(node_attrs, "attribute", id="0", title="cpu_capacity", type="float")
        ET.SubElement(node_attrs, "attribute", id="1", title="ram_capacity", type="float")
        ET.SubElement(node_attrs, "attribute", id="2", title="tier", type="string")

        # Edge attributes definition
        edge_attrs = ET.SubElement(graph_elem, "attributes", {"class": "edge"})
        ET.SubElement(edge_attrs, "attribute", id="0", title="latency_ms", type="float")
        ET.SubElement(edge_attrs, "attribute", id="1", title="bandwidth_mbps", type="float")

        # Nodes
        nodes_elem = ET.SubElement(graph_elem, "nodes")
        for node in self.nodes.values():
            n_elem = ET.SubElement(nodes_elem, "node", id=node.node_id, label=node.name)
            attvalues = ET.SubElement(n_elem, "attvalues")
            ET.SubElement(attvalues, "attvalue", {"for": "0", "value": str(node.cpu_capacity)})
            ET.SubElement(attvalues, "attvalue", {"for": "1", "value": str(node.ram_capacity)})
            ET.SubElement(attvalues, "attvalue", {"for": "2", "value": str(node.tier)})

        # Edges
        edges_elem = ET.SubElement(graph_elem, "edges")
        for idx, edge in enumerate(self.get_all_edges(deduplicate_undirected=True)):
            e_elem = ET.SubElement(
                edges_elem,
                "edge",
                id=str(idx),
                source=edge.u,
                target=edge.v,
                weight=str(edge.weight)
            )
            attvalues = ET.SubElement(e_elem, "attvalues")
            ET.SubElement(attvalues, "attvalue", {"for": "0", "value": str(edge.weight)})
            ET.SubElement(attvalues, "attvalue", {"for": "1", "value": str(edge.bandwidth)})

        tree = ET.ElementTree(gexf)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    def export_to_csv(self, nodes_csv_path: str, edges_csv_path: str) -> None:
        """Export nodes and edges to CSV for tabular analysis and Gephi import."""
        with open(nodes_csv_path, "w", encoding="utf-8") as f:
            f.write("Id,Label,cpu_capacity,ram_capacity,storage_capacity,tier,region,x,y\n")
            for n in self.nodes.values():
                f.write(f"{n.node_id},{n.name},{n.cpu_capacity},{n.ram_capacity},{n.storage_capacity},{n.tier},{n.region},{n.x},{n.y}\n")

        with open(edges_csv_path, "w", encoding="utf-8") as f:
            f.write("Source,Target,Type,Weight,bandwidth\n")
            edge_type = "Directed" if self.directed else "Undirected"
            for e in self.get_all_edges(deduplicate_undirected=True):
                f.write(f"{e.u},{e.v},{edge_type},{e.weight},{e.bandwidth}\n")

    def to_networkx(self):
        """Convert to NetworkX graph for analysis and plotting."""
        import networkx as nx
        nx_g = nx.DiGraph() if self.directed else nx.Graph()
        for nid, n in self.nodes.items():
            nx_g.add_node(
                nid,
                name=n.name,
                cpu_capacity=n.cpu_capacity,
                ram_capacity=n.ram_capacity,
                storage_capacity=n.storage_capacity,
                tier=n.tier,
                region=n.region,
                pos=(n.x, n.y)
            )
        for e in self.get_all_edges(deduplicate_undirected=True):
            nx_g.add_edge(e.u, e.v, weight=e.weight, bandwidth=e.bandwidth)
        return nx_g
