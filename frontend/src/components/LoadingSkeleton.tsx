import React from 'react';
import { Loader2 } from 'lucide-react';

export const CardSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 animate-pulse">
      <div className="h-3 w-24 bg-slate-800 rounded mb-3"></div>
      <div className="h-7 w-32 bg-slate-700/80 rounded mb-2"></div>
      <div className="h-2.5 w-16 bg-slate-800/60 rounded"></div>
    </div>
  );
};

export const ChartSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 animate-pulse h-80 flex flex-col justify-between">
      <div className="flex justify-between items-center">
        <div className="h-4 w-40 bg-slate-800 rounded"></div>
        <div className="h-3 w-20 bg-slate-800/60 rounded"></div>
      </div>
      <div className="flex items-end justify-between h-48 px-4 gap-3">
        {[40, 65, 30, 85, 50, 95, 70, 45].map((h, i) => (
          <div
            key={i}
            className="w-full bg-slate-800/80 rounded-t"
            style={{ height: `${h}%` }}
          ></div>
        ))}
      </div>
      <div className="h-3 w-full bg-slate-800/40 rounded"></div>
    </div>
  );
};

export const TopologySkeleton: React.FC = () => {
  return (
    <div className="relative bg-slate-950 border border-slate-800 rounded-xl h-[460px] flex items-center justify-center overflow-hidden">
      {/* Background Pulse Grid */}
      <div className="absolute inset-0 grid grid-cols-6 grid-rows-4 gap-4 p-8 opacity-20">
        {Array.from({ length: 24 }).map((_, i) => (
          <div key={i} className="border border-slate-800 rounded-lg"></div>
        ))}
      </div>

      {/* Center Spinner Banner */}
      <div className="relative z-10 flex flex-col items-center gap-3 p-6 bg-slate-900/90 border border-slate-800 rounded-xl shadow-2xl backdrop-blur-md">
        <Loader2 className="h-8 w-8 text-indigo-400 animate-spin" />
        <div className="text-center">
          <p className="text-xs font-semibold text-slate-100 tracking-wide">
            Computing Graph Routing & Task Placement
          </p>
          <p className="text-[11px] text-slate-400 font-mono mt-0.5">
            Invoking Python Backend (Shortest-Paths & Knapsack DP)...
          </p>
        </div>
      </div>
    </div>
  );
};

export const TableSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 animate-pulse">
      <div className="h-4 w-36 bg-slate-800 rounded mb-4"></div>
      <div className="space-y-2.5">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex justify-between items-center py-2 border-b border-slate-800/60">
            <div className="h-3.5 w-28 bg-slate-800 rounded"></div>
            <div className="h-3.5 w-20 bg-slate-800/80 rounded"></div>
            <div className="h-3.5 w-16 bg-slate-800/60 rounded"></div>
          </div>
        ))}
      </div>
    </div>
  );
};
