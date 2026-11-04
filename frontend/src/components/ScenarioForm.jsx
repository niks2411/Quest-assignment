import React, { useState, useEffect } from 'react';
import { Sliders, Layers, ArrowUpRight } from 'lucide-react';

export default function ScenarioForm({ currentScenario, onApplyPreset, onApplyCustom }) {
  const [formData, setFormData] = useState({
    name: 'Custom Configuration',
    target_vehicle_count: 60,
    spawn_rate_vps: 0.8,
    lanes_per_road: 2,
    traffic_signal_green: 25.0,
    traffic_signal_yellow: 4.0,
    traffic_signal_mode: 'fixed',
    flyover_enabled: false,
    speed_limit_kmh: 60.0,
  });

  useEffect(() => {
    if (currentScenario) {
      setFormData((prev) => ({
        ...prev,
        ...currentScenario,
      }));
    }
  }, [currentScenario]);

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onApplyCustom(formData);
  };

  return (
    <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-xs space-y-5">
      {/* Benchmark Presets Section */}
      <div>
        <div className="flex items-center justify-between mb-2.5">
          <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider">
            Benchmark Scenarios
          </h3>
          <span className="text-[11px] text-slate-500">1-click presets</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <button
            onClick={() => onApplyPreset('normal')}
            className="flex flex-col text-left p-3 rounded-lg border border-slate-200 hover:border-slate-300 hover:bg-slate-50/80 transition cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold text-xs text-slate-900 group-hover:text-blue-600">
                A · Normal Traffic
              </span>
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600" />
            </div>
            <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
              50 veh, 2 lanes, standard cycle, low delay.
            </p>
          </button>

          <button
            onClick={() => onApplyPreset('peak_hour')}
            className="flex flex-col text-left p-3 rounded-lg border border-slate-200 hover:border-slate-300 hover:bg-slate-50/80 transition cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold text-xs text-slate-900 group-hover:text-rose-600">
                B · Peak-Hour Congestion
              </span>
              <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-rose-600" />
            </div>
            <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
              180 veh, 2.2 vps arrival, junction gridlock.
            </p>
          </button>

          <button
            onClick={() => onApplyPreset('flyover_bypass')}
            className="flex flex-col text-left p-3 rounded-lg border border-sky-200 bg-sky-50/30 hover:bg-sky-50/70 transition cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold text-xs text-sky-900 group-hover:text-sky-700">
                C · Flyover Added
              </span>
              <Layers className="w-3.5 h-3.5 text-sky-600" />
            </div>
            <p className="text-[11px] text-sky-700/80 mt-1 leading-relaxed">
              Elevated bypass deck active over junction.
            </p>
          </button>

          <button
            onClick={() => onApplyPreset('adaptive_signals')}
            className="flex flex-col text-left p-3 rounded-lg border border-purple-200 bg-purple-50/30 hover:bg-purple-50/70 transition cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold text-xs text-purple-900 group-hover:text-purple-700">
                D · Smart Adaptive Signals
              </span>
              <ArrowUpRight className="w-3.5 h-3.5 text-purple-600" />
            </div>
            <p className="text-[11px] text-purple-700/80 mt-1 leading-relaxed">
              Queue-length sensing real-time phase splits.
            </p>
          </button>
        </div>
      </div>

      <hr className="border-slate-100" />

      {/* Custom Parameter Adjuster */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-slate-600" />
            <h3 className="text-xs font-semibold text-slate-800 uppercase tracking-wider">
              Network Parameters
            </h3>
          </div>
          <span className="text-[11px] text-slate-500">Fine-tune model</span>
        </div>

        {/* Vehicle Volume */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-600 font-medium">Target Vehicle Volume</span>
            <span className="font-mono text-slate-900 font-bold">{formData.target_vehicle_count}</span>
          </div>
          <input
            type="range"
            min="10"
            max="250"
            step="5"
            value={formData.target_vehicle_count}
            onChange={(e) => handleChange('target_vehicle_count', parseInt(e.target.value))}
            className="w-full accent-slate-900 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
          />
        </div>

        {/* Arrival Rate */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-600 font-medium">Vehicle Arrival Rate</span>
            <span className="font-mono text-slate-900 font-bold">{formData.spawn_rate_vps} veh/sec</span>
          </div>
          <input
            type="range"
            min="0.2"
            max="3.5"
            step="0.1"
            value={formData.spawn_rate_vps}
            onChange={(e) => handleChange('spawn_rate_vps', parseFloat(e.target.value))}
            className="w-full accent-slate-900 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
          />
        </div>

        {/* Lanes & Green Light */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-slate-600 font-medium block mb-1">Road Width (Lanes)</label>
            <div className="flex gap-1.5">
              {[1, 2, 4].map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() => handleChange('lanes_per_road', l)}
                  className={`flex-1 py-1.5 text-xs font-medium rounded-md border transition cursor-pointer ${
                    formData.lanes_per_road === l
                      ? 'bg-slate-900 border-slate-900 text-white'
                      : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs text-slate-600 font-medium block mb-1">Green Signal Time</label>
            <div className="flex items-center gap-1.5">
              <input
                type="number"
                min="5"
                max="60"
                value={formData.traffic_signal_green}
                onChange={(e) => handleChange('traffic_signal_green', parseFloat(e.target.value))}
                className="w-full bg-slate-50 border border-slate-200 rounded-md px-2.5 py-1 text-xs text-slate-900 font-mono focus:bg-white focus:outline-none focus:border-slate-400"
              />
              <span className="text-xs text-slate-500 font-mono">sec</span>
            </div>
          </div>
        </div>

        {/* Infrastructure Toggles */}
        <div className="grid grid-cols-2 gap-2 pt-1">
          <label className="flex items-center gap-2 p-2.5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 cursor-pointer select-none transition">
            <input
              type="checkbox"
              checked={formData.flyover_enabled}
              onChange={(e) => handleChange('flyover_enabled', e.target.checked)}
              className="w-4 h-4 rounded text-slate-900 focus:ring-0"
            />
            <span className="text-xs font-medium text-slate-800">Elevated Flyover</span>
          </label>

          <label className="flex items-center gap-2 p-2.5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 cursor-pointer select-none transition">
            <input
              type="checkbox"
              checked={formData.traffic_signal_mode === 'adaptive'}
              onChange={(e) => handleChange('traffic_signal_mode', e.target.checked ? 'adaptive' : 'fixed')}
              className="w-4 h-4 rounded text-slate-900 focus:ring-0"
            />
            <span className="text-xs font-medium text-slate-800">Adaptive Signal</span>
          </label>
        </div>

        <button
          type="submit"
          className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded-lg transition-colors cursor-pointer shadow-xs"
        >
          Apply Custom Parameters
        </button>
      </form>
    </div>
  );
}
