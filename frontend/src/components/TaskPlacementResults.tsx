import React from 'react';
import { CheckCircle2, AlertTriangle, Clock, Zap, Cpu, HardDrive } from 'lucide-react';

export interface PlacementData {
  algorithm: string;
  total_latency: number;
  average_latency_ms: number;
  execution_time_ms: number;
  placed_count: number;
  unplaced_count: number;
  cpu_utilization_pct: number;
  ram_utilization_pct: number;
  placements: Record<string, string>;
  servers: Array<{
    server_id: string;
    cpu_used: number;
    cpu_capacity: number;
    cpu_util_pct: number;
    ram_used: number;
    ram_capacity: number;
    ram_util_pct: number;
  }>;
  tasks: Array<{
    task_id: string;
    name: string;
    cpu_demand: number;
    ram_demand: number;
    traffic: Record<string, number>;
  }>;
}

interface TaskPlacementResultsProps {
  data: PlacementData;
}

export const TaskPlacementResults: React.FC<TaskPlacementResultsProps> = ({ data }) => {
  return (
    <div className="space-y-5">
      {/* KPI Metric Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Metric 1: Average Latency */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Average Latency</span>
            <Zap className="h-3.5 w-3.5 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {data.average_latency_ms} <span className="text-xs font-normal text-slate-500">ms</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1 font-mono">
            <span>Total Cost:</span>
            <span className="text-slate-300 font-semibold">{data.total_latency.toLocaleString()}</span>
          </div>
        </div>

        {/* Metric 2: Placement Feasibility */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Placement Status</span>
            {data.unplaced_count === 0 ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
            )}
          </div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {data.placed_count} <span className="text-xs font-normal text-slate-500">/ {data.placed_count + data.unplaced_count}</span>
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 font-medium">
            {data.unplaced_count === 0 ? '100% Feasible (Zero Violations)' : `${data.unplaced_count} Unplaced Tasks`}
          </div>
        </div>

        {/* Metric 3: Cluster CPU Utilization */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Cluster CPU Util</span>
            <Cpu className="h-3.5 w-3.5 text-blue-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {data.cpu_utilization_pct}%
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className="bg-blue-500 h-full rounded-full transition-all"
              style={{ width: `${Math.min(100, data.cpu_utilization_pct)}%` }}
            />
          </div>
        </div>

        {/* Metric 4: Solver Runtime */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Solver Runtime</span>
            <Clock className="h-3.5 w-3.5 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-100">
            {data.execution_time_ms} <span className="text-xs font-normal text-slate-500">ms</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-1 font-mono truncate">
            Algorithm: <span className="text-indigo-300 font-semibold">{data.algorithm}</span>
          </div>
        </div>
      </div>

      {/* Server Capacity Allocation Profiles */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-4 flex items-center justify-between">
          <span>Server Hardware Allocation (CPU & RAM Saturation)</span>
          <span className="text-slate-500 font-mono text-[11px] normal-case">
            Strict Capacity Safeguards ($C(s) \ge \sum d(t)$)
          </span>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {data.servers.slice(0, 8).map((srv) => (
            <div key={srv.server_id} className="bg-slate-950/80 border border-slate-800 rounded-lg p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-xs text-slate-200">{srv.server_id}</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                  {srv.cpu_util_pct}% Load
                </span>
              </div>

              {/* CPU Bar */}
              <div className="mb-2">
                <div className="flex justify-between text-[10px] text-slate-400 font-mono mb-1">
                  <span>CPU Cores</span>
                  <span>{srv.cpu_used} / {srv.cpu_capacity}</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      srv.cpu_util_pct > 80 ? 'bg-rose-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${Math.min(100, srv.cpu_util_pct)}%` }}
                  />
                </div>
              </div>

              {/* RAM Bar */}
              <div>
                <div className="flex justify-between text-[10px] text-slate-400 font-mono mb-1">
                  <span>RAM GB</span>
                  <span>{srv.ram_used} / {srv.ram_capacity}</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all"
                    style={{ width: `${Math.min(100, srv.ram_util_pct)}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Placements Mapping Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="px-5 py-3.5 border-b border-slate-800 flex justify-between items-center">
          <h4 className="text-xs font-semibold text-slate-200">Replica Assignment Schedule</h4>
          <span className="text-[11px] font-mono text-slate-500">{data.tasks.length} Placed Workloads</span>
        </div>

        <div className="overflow-x-auto max-h-60">
          <table className="w-full text-left text-xs text-slate-300 font-sans">
            <thead className="bg-slate-950 text-slate-400 text-[11px] uppercase font-mono sticky top-0 border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Task ID</th>
                <th className="py-2.5 px-4">Workload Profile</th>
                <th className="py-2.5 px-4">Assigned Server</th>
                <th className="py-2.5 px-4">CPU Demand</th>
                <th className="py-2.5 px-4">RAM Demand</th>
                <th className="py-2.5 px-4">Client Request Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {data.tasks.map((t) => {
                const assignedServer = data.placements[t.task_id] || 'UNPLACED';
                const totalTraffic = Object.values(t.traffic || {}).reduce((a, b) => a + b, 0);
                return (
                  <tr key={t.task_id} className="hover:bg-slate-800/40">
                    <td className="py-2 px-4 font-semibold text-indigo-300">{t.task_id}</td>
                    <td className="py-2 px-4 text-slate-200 font-sans">{t.name}</td>
                    <td className="py-2 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-emerald-500/20 font-bold">
                        {assignedServer}
                      </span>
                    </td>
                    <td className="py-2 px-4 text-slate-300">{t.cpu_demand} Cores</td>
                    <td className="py-2 px-4 text-slate-300">{t.ram_demand} GB</td>
                    <td className="py-2 px-4 text-amber-400 font-bold">{Math.round(totalTraffic)} req/s</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
