import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Layers, Activity, FileText, Cpu } from 'lucide-react';

import RoadCanvas from './components/RoadCanvas';
import MetricsCards from './components/MetricsCards';
import ControlsBar from './components/ControlsBar';
import ScenarioForm from './components/ScenarioForm';
import QueueVisualizer from './components/QueueVisualizer';
import TrafficCharts from './components/TrafficCharts';

const RAW_BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const BACKEND_URL = RAW_BACKEND_URL.replace(/\/+$/, '');
const WS_URL =
  import.meta.env.VITE_WS_URL ||
  (BACKEND_URL.startsWith('https://')
    ? BACKEND_URL.replace('https://', 'wss://') + '/ws/simulation'
    : BACKEND_URL.replace('http://', 'ws://') + '/ws/simulation');

export default function App() {
  const [simState, setSimState] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [speedMultiplier, setSpeedMultiplier] = useState(1.0);
  const [history, setHistory] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    let ws;
    let reconnectTimer;

    const connect = () => {
      ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setSimState(data);

          if (data.metrics) {
            setHistory((prev) => {
              const newEntry = {
                time: `${Math.round(data.sim_time)}s`,
                speed: data.metrics.avg_speed_kmh,
                queue: data.metrics.total_queue,
              };
              const updated = [...prev, newEntry];
              return updated.length > 30 ? updated.slice(updated.length - 30) : updated;
            });
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message', e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimer = setTimeout(connect, 1500);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

  const sendWsCmd = (cmd, payload = {}) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ cmd, ...payload }));
    } else {
      if (cmd === 'start' || cmd === 'pause' || cmd === 'step' || cmd === 'reset') {
        axios.post(`${BACKEND_URL}/api/control`, { action: cmd });
      }
    }
  };

  const handleStart = () => sendWsCmd('start');
  const handlePause = () => sendWsCmd('pause');
  const handleStep = () => sendWsCmd('step');
  const handleReset = () => {
    sendWsCmd('reset');
    setHistory([]);
  };

  const handleSpeedChange = (mult) => {
    setSpeedMultiplier(mult);
    sendWsCmd('speed', { value: mult });
  };

  const handleApplyPreset = (presetKey) => {
    sendWsCmd('apply_preset', { preset: presetKey });
    setHistory([]);
  };

  const handleApplyCustom = async (customConfig) => {
    try {
      await axios.post(`${BACKEND_URL}/api/scenarios/custom`, customConfig);
      setHistory([]);
      const res = await axios.get(`${BACKEND_URL}/api/status`);
      setSimState(res.data);
    } catch (err) {
      console.error('Failed to apply custom scenario', err);
    }
  };

  const lanes = simState?.scenario?.lanes_per_road || 2;
  const flyoverEnabled = Boolean(simState?.scenario?.flyover_enabled);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Professional Clean Header */}
      <header className="border-b border-slate-200/90 bg-white sticky top-0 z-50 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center text-white font-bold text-sm tracking-tight">
              TS
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-bold text-sm sm:text-base text-slate-900 tracking-tight">
                  TrafficSim
                </h1>
                <span className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
                  Microscopic IDM Engine
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Agent-based intersection simulation with variable capacity & grade-separated flyover
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-xs text-slate-600 font-mono">
              <Cpu className="w-3.5 h-3.5 text-slate-600" />
              <span>FastAPI Backend · Canvas UI</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-[1480px] mx-auto px-4 py-5 flex-1 w-full space-y-5">
        {/* Playback Controls Bar */}
        <ControlsBar
          isRunning={Boolean(simState?.is_running)}
          simTime={simState?.sim_time || 0}
          speedMultiplier={speedMultiplier}
          isConnected={isConnected}
          onStart={handleStart}
          onPause={handlePause}
          onReset={handleReset}
          onStep={handleStep}
          onSpeedChange={handleSpeedChange}
        />

        {/* Primary KPIs Cards */}
        <MetricsCards metrics={simState?.metrics} />

        {/* Layout: Viewport (Left) & Controls/Analytics (Right) */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
          {/* Simulation Canvas Viewport (7 cols on xl) */}
          <div className="xl:col-span-7 flex flex-col space-y-4">
            <RoadCanvas
              simulationState={simState}
              lanes={lanes}
              flyoverEnabled={flyoverEnabled}
            />

            {/* Methodology Note */}
            <div className="p-4 bg-white border border-slate-200/90 rounded-xl shadow-xs text-xs space-y-1.5 text-slate-600">
              <div className="flex items-center gap-1.5 font-semibold text-slate-900">
                <FileText className="w-3.5 h-3.5 text-slate-700" />
                <span>Simulation Dynamics & Methodology</span>
              </div>
              <p className="leading-relaxed">
                Vehicles operate as individual agent entities executing the{' '}
                <strong className="text-slate-900">Intelligent Driver Model (IDM)</strong>. Speed updates calculate continuous headway spacing ($s$) and relative closing rate ($\Delta v$), ensuring physical acceleration and safe deceleration without hard-coded stop jumps.
              </p>
              {flyoverEnabled && (
                <p className="text-sky-800 bg-sky-50 p-2 rounded-md border border-sky-100">
                  <strong className="text-sky-900">Infrastructure Analysis:</strong> The active North-South flyover eliminates intersection conflicts for through-traffic, preserving continuous corridor capacity even under peak arrival volumes.
                </p>
              )}
            </div>
          </div>

          {/* Scenario Config & Queue Breakdown (5 cols on xl) */}
          <div className="xl:col-span-5 space-y-5">
            <ScenarioForm
              currentScenario={simState?.scenario}
              onApplyPreset={handleApplyPreset}
              onApplyCustom={handleApplyCustom}
            />

            <QueueVisualizer
              queues={simState?.metrics?.queues}
              signals={simState?.traffic_light?.signals}
            />

            <TrafficCharts history={history} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200/80 bg-white py-3.5 text-center text-xs text-slate-500">
        TrafficSim · Civil Engineering Microscopic Simulation · Intelligent Driver Model (Treiber et al.)
      </footer>
    </div>
  );
}
