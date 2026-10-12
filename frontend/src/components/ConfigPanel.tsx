import React from 'react';
import { Play, Sliders, Database, Layers, Sparkles, RefreshCw } from 'lucide-react';

export interface SimulationParams {
  topologyId: string;
  numTasks: number;
  trafficPattern: 'hotspot' | 'uniform';
  capacityTightness: 'loose' | 'normal' | 'tight';
  algorithm: 'exact' | 'dp' | 'gnt' | 'gld';
}

interface ConfigPanelProps {
  params: SimulationParams;
  onChange: (newParams: SimulationParams) => void;
  onRunSimulation: () => void;
  isLoading: boolean;
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({
  params,
  onChange,
  onRunSimulation,
  isLoading,
}) => {
  const topologies = [
    { id: 'campus', name: 'Campus Network Backbone', nodes: '16 Nodes • 28 Links' },
    { id: 'fattree', name: 'Datacenter Fat-Tree (k=4)', nodes: '20 Nodes • 32 Links' },
    { id: 'regional', name: 'Regional Cloud Backbone', nodes: '20 Nodes • 23 Links' },
    { id: 'waxman', name: 'Waxman Random Graph', nodes: '25 Nodes • 50+ Links' },
  ];

  const algorithms = [
    { id: 'exact', name: 'Exact Optimizer', detail: 'Branch & Bound (Globally Optimal)' },
    { id: 'dp', name: 'Dynamic Programming', detail: 'Knapsack Latency Savings State' },
    { id: 'gnt', name: 'Greedy Nearest Traffic', detail: 'Top-Traffic Hotspot Allocation' },
    { id: 'gld', name: 'Greedy Latency-Density', detail: 'Resource-Weighted Density Packing' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Sliders className="h-4 w-4 text-indigo-400" />
          <h2 className="text-sm font-semibold text-slate-100">Workload & Topology Configuration</h2>
        </div>
        <span className="text-[11px] font-mono text-slate-500 uppercase">Input Controller</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mt-4">
        {/* Topology Selection */}
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
            <Database className="h-3.5 w-3.5 text-slate-400" />
            Dataset Topology
          </label>
          <select
            value={params.topologyId}
            onChange={(e) => onChange({ ...params, topologyId: e.target.value })}
            className="w-full bg-slate-950 border border-slate-700/80 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 font-sans"
          >
            {topologies.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
          <p className="text-[11px] text-slate-500 mt-1 font-mono">
            {topologies.find((t) => t.id === params.topologyId)?.nodes}
          </p>
        </div>

        {/* Task Volume Slider */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <label className="text-xs font-medium text-slate-300">VM Replicas / Tasks</label>
            <span className="text-xs font-mono font-semibold text-indigo-400 bg-indigo-950/60 border border-indigo-800/60 px-1.5 py-0.5 rounded">
              {params.numTasks} Tasks
            </span>
          </div>
          <input
            type="range"
            min={4}
            max={30}
            step={2}
            value={params.numTasks}
            onChange={(e) => onChange({ ...params, numTasks: parseInt(e.target.value) })}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
            <span>4 Min</span>
            <span>16 Mid</span>
            <span>30 Stress</span>
          </div>
        </div>

        {/* Traffic & Tightness */}
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Traffic Flow</label>
            <select
              value={params.trafficPattern}
              onChange={(e) => onChange({ ...params, trafficPattern: e.target.value as any })}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-lg px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="hotspot">Hotspot (80/20)</option>
              <option value="uniform">Uniform</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Cap Tightness</label>
            <select
              value={params.capacityTightness}
              onChange={(e) => onChange({ ...params, capacityTightness: e.target.value as any })}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-lg px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="loose">Loose (150%)</option>
              <option value="normal">Normal (100%)</option>
              <option value="tight">Tight (60%)</option>
            </select>
          </div>
        </div>

        {/* Solver Algorithm */}
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
            <Layers className="h-3.5 w-3.5 text-slate-400" />
            Placement Algorithm
          </label>
          <select
            value={params.algorithm}
            onChange={(e) => onChange({ ...params, algorithm: e.target.value as any })}
            className="w-full bg-slate-950 border border-slate-700/80 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans"
          >
            {algorithms.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
          <p className="text-[10px] text-slate-500 mt-1 truncate">
            {algorithms.find((a) => a.id === params.algorithm)?.detail}
          </p>
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex justify-end items-center mt-5 pt-4 border-t border-slate-800">
        <button
          onClick={onRunSimulation}
          disabled={isLoading}
          className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-medium transition-all shadow-md ${
            isLoading
              ? 'bg-indigo-600/50 text-indigo-200 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/30 hover:shadow-indigo-600/50'
          }`}
        >
          {isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Computing Placement...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" />
              <span>Trigger Simulation</span>
              <kbd className="ml-1.5 px-1.5 py-0.5 text-[9px] bg-indigo-700/60 rounded text-indigo-100 font-mono">
                Run
              </kbd>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
