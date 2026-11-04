import React from 'react';
import { Gauge, Clock, Car, BarChart3, TrendingUp, AlertCircle } from 'lucide-react';

export default function MetricsCards({ metrics }) {
  const m = metrics || {
    active_vehicles: 0,
    completed_vehicles: 0,
    avg_speed_kmh: 0,
    avg_waiting_time_sec: 0,
    throughput_vpm: 0,
    road_utilization_pct: 0,
    total_queue: 0,
  };

  const cards = [
    {
      title: 'Active Fleet',
      value: m.active_vehicles,
      sub: `${m.completed_vehicles} trips completed`,
      icon: Car,
      accent: 'border-l-blue-600',
      iconColor: 'text-blue-600',
    },
    {
      title: 'Average Speed',
      value: `${m.avg_speed_kmh}`,
      unit: 'km/h',
      sub: m.avg_speed_kmh < 15 ? 'Congested corridor' : 'Free-flow conditions',
      icon: Gauge,
      accent: m.avg_speed_kmh < 15 ? 'border-l-amber-500' : 'border-l-emerald-600',
      iconColor: m.avg_speed_kmh < 15 ? 'text-amber-600' : 'text-emerald-600',
    },
    {
      title: 'Mean Wait Time',
      value: `${m.avg_waiting_time_sec}`,
      unit: 's',
      sub: 'Intersection delay',
      icon: Clock,
      accent: m.avg_waiting_time_sec > 25 ? 'border-l-rose-500' : 'border-l-sky-600',
      iconColor: m.avg_waiting_time_sec > 25 ? 'text-rose-600' : 'text-sky-600',
    },
    {
      title: 'Road Utilization',
      value: `${m.road_utilization_pct}`,
      unit: '%',
      sub: 'Of physical capacity',
      icon: BarChart3,
      accent: 'border-l-indigo-600',
      iconColor: 'text-indigo-600',
    },
    {
      title: 'Throughput',
      value: `${m.throughput_vpm}`,
      unit: 'veh/min',
      sub: 'Discharge rate',
      icon: TrendingUp,
      accent: 'border-l-teal-600',
      iconColor: 'text-teal-600',
    },
    {
      title: 'Stopped Queue',
      value: m.total_queue,
      sub: 'Vehicles at signals',
      icon: AlertCircle,
      accent: m.total_queue > 15 ? 'border-l-rose-500' : 'border-l-slate-400',
      iconColor: m.total_queue > 15 ? 'text-rose-600' : 'text-slate-500',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <div
            key={i}
            className={`p-3.5 bg-white border border-slate-200/90 border-l-4 ${c.accent} rounded-lg shadow-xs hover:shadow-sm transition-shadow`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-[11px] font-semibold text-slate-500 tracking-wider uppercase">
                {c.title}
              </span>
              <Icon className={`w-3.5 h-3.5 ${c.iconColor}`} />
            </div>
            <div className="flex items-baseline gap-1 mt-1">
              <span className="text-2xl font-bold tracking-tight text-slate-900 font-mono">
                {c.value}
              </span>
              {c.unit && <span className="text-xs font-medium text-slate-500">{c.unit}</span>}
            </div>
            <div className="text-[11px] text-slate-500 mt-1 truncate">{c.sub}</div>
          </div>
        );
      })}
    </div>
  );
}
