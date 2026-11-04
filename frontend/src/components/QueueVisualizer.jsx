import React from 'react';
import { Compass } from 'lucide-react';

export default function QueueVisualizer({ queues, signals }) {
  const q = queues || { N: 0, S: 0, E: 0, W: 0 };
  const s = signals || { N: 'RED', S: 'RED', E: 'RED', W: 'RED' };

  const arms = [
    { dir: 'N', label: 'North Arm (Avenue)', count: q.N, signal: s.N },
    { dir: 'S', label: 'South Arm (Boulevard)', count: q.S, signal: s.S },
    { dir: 'E', label: 'East Arm (Expressway)', count: q.E, signal: s.E },
    { dir: 'W', label: 'West Arm (Parkway)', count: q.W, signal: s.W },
  ];

  const maxQueue = Math.max(10, Math.max(...Object.values(q)));

  const getSignalBadge = (sig) => {
    if (sig === 'GREEN') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    if (sig === 'YELLOW') return 'bg-amber-50 text-amber-700 border-amber-200';
    return 'bg-rose-50 text-rose-700 border-rose-200';
  };

  return (
    <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-xs space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Compass className="w-3.5 h-3.5 text-slate-600" />
          <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider">
            Directional Queue Backlogs
          </h3>
        </div>
        <span className="text-[11px] text-slate-500 font-mono">Signal Status</span>
      </div>

      <div className="space-y-2.5">
        {arms.map((a) => {
          const pct = Math.min(100, Math.round((a.count / maxQueue) * 100));
          return (
            <div key={a.dir} className="p-2.5 rounded-lg border border-slate-100 bg-slate-50/70">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="text-slate-700 font-medium">{a.label}</span>
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getSignalBadge(
                      a.signal
                    )}`}
                  >
                    {a.signal}
                  </span>
                  <span className="font-mono text-slate-900 font-bold">{a.count} veh</span>
                </div>
              </div>
              <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 rounded-full ${
                    a.count > 12 ? 'bg-rose-500' : a.count > 6 ? 'bg-amber-500' : 'bg-slate-700'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
