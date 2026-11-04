import React from 'react';
import { Play, Pause, RotateCcw, StepForward, Activity } from 'lucide-react';

export default function ControlsBar({
  isRunning,
  simTime,
  speedMultiplier,
  isConnected,
  onStart,
  onPause,
  onReset,
  onStep,
  onSpeedChange,
}) {
  const speeds = [0.5, 1.0, 2.0, 4.0];

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    const ms = Math.floor((secs % 1) * 10);
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${ms}`;
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 bg-white border border-slate-200/90 rounded-xl shadow-xs">
      {/* Primary Action Buttons */}
      <div className="flex items-center gap-2">
        {!isRunning ? (
          <button
            onClick={onStart}
            className="flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded-lg transition-colors shadow-xs cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Run Simulation</span>
          </button>
        ) : (
          <button
            onClick={onPause}
            className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-xs rounded-lg transition-colors shadow-xs cursor-pointer"
          >
            <Pause className="w-3.5 h-3.5 fill-current" />
            <span>Pause</span>
          </button>
        )}

        <button
          onClick={onStep}
          disabled={isRunning}
          className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 disabled:opacity-40 disabled:cursor-not-allowed text-slate-700 text-xs font-medium rounded-lg border border-slate-200 transition-colors cursor-pointer"
        >
          <StepForward className="w-3.5 h-3.5 text-slate-600" />
          <span>Step (50ms)</span>
        </button>

        <button
          onClick={onReset}
          className="flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-rose-50 text-rose-600 text-xs font-medium rounded-lg border border-slate-200 hover:border-rose-300 transition-colors cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
      </div>

      {/* Speed Multiplier Segmented Control */}
      <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
        <span className="text-[11px] font-medium text-slate-500 px-2">Speed:</span>
        {speeds.map((s) => (
          <button
            key={s}
            onClick={() => onSpeedChange(s)}
            className={`px-2.5 py-1 text-xs font-mono rounded-md transition-all cursor-pointer ${
              speedMultiplier === s
                ? 'bg-white text-slate-900 font-semibold shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            {s}x
          </button>
        ))}
      </div>

      {/* Simulation Clock & Connection Status */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100/90 rounded-lg border border-slate-200 font-mono text-xs">
          <span className="text-slate-500 font-medium">SIM TIME</span>
          <span className="font-semibold text-slate-900">{formatTime(simTime)}</span>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-slate-600 font-medium pl-1">
          <span
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-emerald-500' : 'bg-rose-500 animate-pulse'
            }`}
          ></span>
          <span>{isConnected ? 'Engine Ready' : 'Connecting...'}</span>
        </div>
      </div>
    </div>
  );
}
