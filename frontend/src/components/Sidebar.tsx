import React from 'react';
import { 
  Network, 
  Cpu, 
  GitBranch, 
  Compass, 
  BarChart3, 
  BookOpen, 
  Server, 
  Activity, 
  Layers 
} from 'lucide-react';

export type NavTab = 'topology' | 'placement' | 'mst' | 'routing' | 'benchmarks' | 'docs';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  apiStatus: 'online' | 'offline' | 'checking';
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, apiStatus }) => {
  const navItems = [
    { id: 'topology' as NavTab, label: 'Network Topologies', icon: Network, badge: '4 Presets' },
    { id: 'placement' as NavTab, label: 'Task Simulation', icon: Cpu, badge: 'Active' },
    { id: 'mst' as NavTab, label: 'MST Backbone', icon: GitBranch, badge: 'Loop-Free' },
    { id: 'routing' as NavTab, label: 'Shortest Routing', icon: Compass, badge: 'SSSP/APSP' },
    { id: 'benchmarks' as NavTab, label: 'Empirical Metrics', icon: BarChart3, badge: 'Recharts' },
    { id: 'docs' as NavTab, label: 'Technical Report', icon: BookOpen, badge: 'LaTeX' },
  ];

  return (
    <aside className="w-64 bg-slate-950 text-slate-300 flex flex-col border-r border-slate-800 select-none min-h-screen">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-600/30">
            <Server className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-semibold text-slate-100 text-sm tracking-wide">CloudPlacement</h1>
            <p className="text-[10px] text-indigo-400 font-mono font-medium uppercase tracking-wider">DAA Research Engine</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
          Optimization Suite
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`h-4 w-4 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                  isActive 
                    ? 'bg-indigo-500/30 text-indigo-200' 
                    : 'bg-slate-800 text-slate-400'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-900 bg-slate-950/60">
        <div className="bg-slate-900/90 rounded-lg p-3 border border-slate-800/80">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-medium text-slate-400">Backend API</span>
            <div className="flex items-center gap-1.5">
              <span className={`h-2 w-2 rounded-full ${
                apiStatus === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
              }`} />
              <span className="text-[11px] font-mono text-slate-300 capitalize">{apiStatus}</span>
            </div>
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-500">
            <span>Core Version</span>
            <span className="font-mono text-slate-400">v1.2.0 (Python 3.11)</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
