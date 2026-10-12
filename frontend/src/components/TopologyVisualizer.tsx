import React, { useState } from 'react';
import { Eye, EyeOff, GitBranch, Layers, ZoomIn } from 'lucide-react';

export interface NodeData {
  node_id: string;
  name: string;
  tier: string;
  cpu_capacity: number;
  ram_capacity: number;
  x: number;
  y: number;
}

export interface EdgeData {
  u: string;
  v: string;
  weight: number;
  bandwidth?: number;
}

interface TopologyVisualizerProps {
  nodes: NodeData[];
  edges: EdgeData[];
  mstEdges?: EdgeData[];
  highlightPath?: string[];
  placements?: Record<string, string>; // task_id -> server_id
  title?: string;
}

export const TopologyVisualizer: React.FC<TopologyVisualizerProps> = ({
  nodes,
  edges,
  mstEdges = [],
  highlightPath = [],
  placements = {},
  title = 'Cloud Network Topology',
}) => {
  const [showMst, setShowMst] = useState(true);
  const [showWeights, setShowWeights] = useState(true);
  const [hoveredNode, setHoveredNode] = useState<NodeData | null>(null);

  // Compute bounding box to normalize coordinates into 800x450 viewBox
  const minX = Math.min(...nodes.map((n) => n.x), 0);
  const maxX = Math.max(...nodes.map((n) => n.x), 10);
  const minY = Math.min(...nodes.map((n) => n.y), 0);
  const maxY = Math.max(...nodes.map((n) => n.y), 10);

  const scaleX = (x: number) => 60 + ((x - minX) / (maxX - minX || 1)) * 680;
  const scaleY = (y: number) => 390 - ((y - minY) / (maxY - minY || 1)) * 320; // Invert Y for cartesian view

  const nodeMap = new Map(nodes.map((n) => [n.node_id, n]));

  // Check if an edge is part of MST
  const mstSet = new Set(
    mstEdges.map((e) => [e.u, e.v].sort().join('--'))
  );

  // Check if an edge is part of active shortest path
  const pathEdgeSet = new Set();
  for (let i = 0; i < highlightPath.length - 1; i++) {
    pathEdgeSet.add([highlightPath[i], highlightPath[i + 1]].sort().join('--'));
  }

  // Count placed tasks per node
  const taskCounts: Record<string, number> = {};
  Object.values(placements).forEach((sid) => {
    taskCounts[sid] = (taskCounts[sid] || 0) + 1;
  });

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col">
      {/* Visualizer Top Bar */}
      <div className="px-5 py-3.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <Layers className="h-4 w-4 text-indigo-400" />
          <h3 className="text-xs font-semibold text-slate-100">{title}</h3>
          <span className="text-[11px] font-mono text-slate-500">
            {nodes.length} Servers • {edges.length} Links
          </span>
        </div>

        {/* View Controls */}
        <div className="flex items-center gap-2">
          {mstEdges.length > 0 && (
            <button
              onClick={() => setShowMst(!showMst)}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] font-medium transition-all ${
                showMst
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <GitBranch className="h-3 w-3" />
              <span>Backbone MST</span>
            </button>
          )}

          <button
            onClick={() => setShowWeights(!showWeights)}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-[11px] font-medium bg-slate-800 text-slate-400 hover:text-slate-200"
          >
            {showWeights ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
            <span>Weights</span>
          </button>
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div className="relative h-[480px] bg-slate-950/80 w-full flex items-center justify-center p-2">
        <svg
          viewBox="0 0 800 450"
          className="w-full h-full select-none"
          style={{ maxHeight: '100%' }}
        >
          {/* Subtle Grid Lines */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1E293B" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="800" height="450" fill="url(#grid)" />

          {/* Regular Physical Links */}
          {edges.map((edge, idx) => {
            const u = nodeMap.get(edge.u);
            const v = nodeMap.get(edge.v);
            if (!u || !v) return null;

            const edgeKey = [edge.u, edge.v].sort().join('--');
            const isMst = showMst && mstSet.has(edgeKey);
            const isPath = pathEdgeSet.has(edgeKey);

            if (isMst || isPath) return null; // Rendered in highlighted layer

            const x1 = scaleX(u.x);
            const y1 = scaleY(u.y);
            const x2 = scaleX(v.x);
            const y2 = scaleY(v.y);

            return (
              <g key={`base-${idx}`}>
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="#334155"
                  strokeWidth="1.2"
                  strokeOpacity="0.7"
                />
                {showWeights && (
                  <text
                    x={(x1 + x2) / 2}
                    y={(y1 + y2) / 2 - 3}
                    fill="#64748B"
                    fontSize="9"
                    fontFamily="monospace"
                    textAnchor="middle"
                  >
                    {edge.weight}ms
                  </text>
                )}
              </g>
            );
          })}

          {/* Highlighted MST Backbone Links */}
          {showMst &&
            mstEdges.map((edge, idx) => {
              const u = nodeMap.get(edge.u);
              const v = nodeMap.get(edge.v);
              if (!u || !v) return null;

              const x1 = scaleX(u.x);
              const y1 = scaleY(u.y);
              const x2 = scaleX(v.x);
              const y2 = scaleY(v.y);

              return (
                <g key={`mst-${idx}`}>
                  <line
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke="#F43F5E"
                    strokeWidth="3.2"
                    strokeLinecap="round"
                    strokeOpacity="0.9"
                  />
                  {showWeights && (
                    <text
                      x={(x1 + x2) / 2}
                      y={(y1 + y2) / 2 - 4}
                      fill="#FDA4AF"
                      fontSize="9"
                      fontWeight="bold"
                      fontFamily="monospace"
                      textAnchor="middle"
                    >
                      {edge.weight}ms
                    </text>
                  )}
                </g>
              );
            })}

          {/* Active Shortest Path Route Links */}
          {highlightPath.map((nodeId, idx) => {
            if (idx === highlightPath.length - 1) return null;
            const u = nodeMap.get(nodeId);
            const v = nodeMap.get(highlightPath[idx + 1]);
            if (!u || !v) return null;

            return (
              <line
                key={`route-${idx}`}
                x1={scaleX(u.x)}
                y1={scaleY(u.y)}
                x2={scaleX(v.x)}
                y2={scaleY(v.y)}
                stroke="#38BDF8"
                strokeWidth="4"
                strokeLinecap="round"
                className="animate-pulse"
              />
            );
          })}

          {/* Server Nodes */}
          {nodes.map((node) => {
            const cx = scaleX(node.x);
            const cy = scaleY(node.y);
            const isPathNode = highlightPath.includes(node.node_id);
            const assignedCount = taskCounts[node.node_id] || 0;

            let fillColor = '#3B82F6'; // Core: Blue
            if (node.tier === 'aggregation') fillColor = '#10B981'; // Agg: Emerald
            if (node.tier.includes('edge')) fillColor = '#F59E0B'; // Edge: Amber

            if (isPathNode) fillColor = '#38BDF8';

            return (
              <g
                key={node.node_id}
                className="cursor-pointer transition-transform hover:scale-110"
                onMouseEnter={() => setHoveredNode(node)}
                onMouseLeave={() => setHoveredNode(null)}
              >
                {/* Node Outer Halo for placed tasks */}
                {assignedCount > 0 && (
                  <circle
                    cx={cx}
                    cy={cy}
                    r="15"
                    fill="none"
                    stroke="#A855F7"
                    strokeWidth="2"
                    strokeDasharray="3 3"
                    className="animate-spin"
                    style={{ transformOrigin: `${cx}px ${cy}px`, animationDuration: '6s' }}
                  />
                )}

                {/* Main Node Circle */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={isPathNode ? 11 : 9}
                  fill={fillColor}
                  stroke="#0F172A"
                  strokeWidth="2"
                />

                {/* Node Label */}
                <text
                  x={cx}
                  y={cy + 17}
                  fill="#F1F5F9"
                  fontSize="10"
                  fontWeight="600"
                  fontFamily="sans-serif"
                  textAnchor="middle"
                >
                  {node.node_id}
                </text>

                {/* Placed Task Badge */}
                {assignedCount > 0 && (
                  <g>
                    <circle cx={cx + 8} cy={cy - 8} r="6" fill="#9333EA" />
                    <text
                      x={cx + 8}
                      y={cy - 6}
                      fill="#FFFFFF"
                      fontSize="8"
                      fontWeight="bold"
                      textAnchor="middle"
                    >
                      {assignedCount}
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {/* Hovered Node Details Popover */}
        {hoveredNode && (
          <div className="absolute top-4 left-4 bg-slate-900/95 border border-slate-700/80 rounded-lg p-3 text-xs shadow-2xl backdrop-blur-md pointer-events-none min-w-[200px]">
            <div className="font-semibold text-slate-100 flex items-center justify-between">
              <span>{hoveredNode.name}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 uppercase">
                {hoveredNode.tier}
              </span>
            </div>
            <div className="mt-2 space-y-1 font-mono text-[11px] text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-500">Node ID:</span>
                <span>{hoveredNode.node_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">CPU Cores:</span>
                <span className="text-emerald-400">{hoveredNode.cpu_capacity} Cores</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">RAM:</span>
                <span className="text-indigo-400">{hoveredNode.ram_capacity} GB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Active Tasks:</span>
                <span className="text-purple-400 font-bold">
                  {taskCounts[hoveredNode.node_id] || 0} Replicas
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div className="px-5 py-2.5 bg-slate-900/90 border-t border-slate-800 flex flex-wrap items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-blue-500"></span>
            <span>Core Router</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
            <span>Aggregation</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500"></span>
            <span>Edge Compute</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-1 w-4 bg-rose-500"></span>
            <span>MST Backbone</span>
          </div>
        </div>
        <span className="font-mono text-[10px] text-slate-500">Coordinates Normalized 2D</span>
      </div>
    </div>
  );
};
