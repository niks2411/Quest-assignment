import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Maximize2, Minimize2 } from 'lucide-react';

/**
 * Clean & Professional Civil Engineering 2D Simulation Viewport
 * High-resolution 900x900 canvas viewport with dynamic scaling,
 * high-contrast lane striping, pedestrian crosswalks, grade-separated flyover,
 * and micro-agent kinematics.
 *
 * Supports browser Fullscreen API for immersive viewing.
 */
export default function RoadCanvas({ simulationState, lanes = 2, flyoverEnabled = false }) {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Listen for fullscreen changes (user pressing Esc, browser toolbar, etc.)
  useEffect(() => {
    const onFsChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', onFsChange);
    return () => document.removeEventListener('fullscreenchange', onFsChange);
  }, []);

  const toggleFullscreen = useCallback(async () => {
    try {
      if (!document.fullscreenElement) {
        await containerRef.current?.requestFullscreen();
      } else {
        await document.exitFullscreen();
      }
    } catch (err) {
      console.warn('Fullscreen toggle failed:', err);
    }
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = 900;
    const height = 900;
    const centerX = width / 2;
    const centerY = height / 2;

    const laneWidthPx = 18;
    const totalRoadWidth = lanes * laneWidthPx * 2; // bidirectional
    const junctionHalf = Math.max(52, totalRoadWidth / 2 + 12);

    ctx.clearRect(0, 0, width, height);

    // 1. Urban Cadastral / Plot Background
    ctx.fillStyle = '#f8fafc';
    ctx.fillRect(0, 0, width, height);

    // Subtle city block parcels
    ctx.fillStyle = '#f1f5f9';
    // Top-left parcel
    ctx.fillRect(20, 20, centerX - totalRoadWidth / 2 - 32, centerY - totalRoadWidth / 2 - 32);
    // Top-right parcel
    ctx.fillRect(centerX + totalRoadWidth / 2 + 16, 20, centerX - totalRoadWidth / 2 - 32, centerY - totalRoadWidth / 2 - 32);
    // Bottom-left parcel
    ctx.fillRect(20, centerY + totalRoadWidth / 2 + 16, centerX - totalRoadWidth / 2 - 32, centerY - totalRoadWidth / 2 - 32);
    // Bottom-right parcel
    ctx.fillRect(centerX + totalRoadWidth / 2 + 16, centerY + totalRoadWidth / 2 + 16, centerX - totalRoadWidth / 2 - 32, centerY - totalRoadWidth / 2 - 32);

    // Grid lines for architectural scale
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    for (let p = 0; p <= width; p += 90) {
      ctx.beginPath();
      ctx.moveTo(p, 0);
      ctx.lineTo(p, height);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, p);
      ctx.lineTo(width, p);
      ctx.stroke();
    }

    // 2. Concrete Road Bed & Asphalt Surface
    // Pavement curb base (slightly wider than asphalt)
    ctx.fillStyle = '#cbd5e1';
    ctx.fillRect(centerX - totalRoadWidth / 2 - 5, 0, totalRoadWidth + 10, height);
    ctx.fillRect(0, centerY - totalRoadWidth / 2 - 5, width, totalRoadWidth + 10);

    // Asphalt surface
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(centerX - totalRoadWidth / 2, 0, totalRoadWidth, height);
    ctx.fillRect(0, centerY - totalRoadWidth / 2, width, totalRoadWidth);

    // Pedestrian Zebra Crosswalks (at intersection perimeter)
    const drawCrosswalk = (startX, startY, isHorizontal, length) => {
      ctx.fillStyle = '#ffffff';
      const barWidth = 4;
      const barSpacing = 8;
      const numBars = Math.floor(length / barSpacing);

      for (let i = 0; i < numBars; i++) {
        if (isHorizontal) {
          ctx.fillRect(startX + i * barSpacing, startY, barWidth, 12);
        } else {
          ctx.fillRect(startX, startY + i * barSpacing, 12, barWidth);
        }
      }
    };

    // North crosswalk
    drawCrosswalk(centerX - totalRoadWidth / 2, centerY - junctionHalf - 16, true, totalRoadWidth);
    // South crosswalk
    drawCrosswalk(centerX - totalRoadWidth / 2, centerY + junctionHalf + 4, true, totalRoadWidth);
    // West crosswalk
    drawCrosswalk(centerX - junctionHalf - 16, centerY - totalRoadWidth / 2, false, totalRoadWidth);
    // East crosswalk
    drawCrosswalk(centerX + junctionHalf + 4, centerY - totalRoadWidth / 2, false, totalRoadWidth);

    // 3. Road Markings & Striping
    // Solid Yellow Center Divider Lines
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 2.5;

    // North arm
    ctx.beginPath();
    ctx.moveTo(centerX - 1.5, 0);
    ctx.lineTo(centerX - 1.5, centerY - junctionHalf);
    ctx.moveTo(centerX + 1.5, 0);
    ctx.lineTo(centerX + 1.5, centerY - junctionHalf);
    // South arm
    ctx.moveTo(centerX - 1.5, centerY + junctionHalf);
    ctx.lineTo(centerX - 1.5, height);
    ctx.moveTo(centerX + 1.5, centerY + junctionHalf);
    ctx.lineTo(centerX + 1.5, height);
    // West arm
    ctx.moveTo(0, centerY - 1.5);
    ctx.lineTo(centerX - junctionHalf, centerY - 1.5);
    ctx.moveTo(0, centerY + 1.5);
    ctx.lineTo(centerX - junctionHalf, centerY + 1.5);
    // East arm
    ctx.moveTo(centerX + junctionHalf, centerY - 1.5);
    ctx.lineTo(width, centerY - 1.5);
    ctx.moveTo(centerX + junctionHalf, centerY + 1.5);
    ctx.lineTo(width, centerY + 1.5);
    ctx.stroke();

    // White dashed lane boundaries for multi-lane roads
    if (lanes > 1) {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([10, 14]);

      for (let l = 1; l < lanes; l++) {
        const offset = l * laneWidthPx;

        // North lanes
        ctx.beginPath();
        ctx.moveTo(centerX - offset, 0);
        ctx.lineTo(centerX - offset, centerY - junctionHalf);
        ctx.moveTo(centerX + offset, 0);
        ctx.lineTo(centerX + offset, centerY - junctionHalf);
        // South lanes
        ctx.moveTo(centerX - offset, centerY + junctionHalf);
        ctx.lineTo(centerX - offset, height);
        ctx.moveTo(centerX + offset, centerY + junctionHalf);
        ctx.lineTo(centerX + offset, height);
        // West lanes
        ctx.moveTo(0, centerY - offset);
        ctx.lineTo(centerX - junctionHalf, centerY - offset);
        ctx.moveTo(0, centerY + offset);
        ctx.lineTo(centerX - junctionHalf, centerY + offset);
        // East lanes
        ctx.moveTo(centerX + junctionHalf, centerY - offset);
        ctx.lineTo(width, centerY - offset);
        ctx.moveTo(centerX + junctionHalf, centerY + offset);
        ctx.lineTo(width, centerY + offset);
        ctx.stroke();
      }
      ctx.setLineDash([]);
    }

    // Stop Lines (Thick white bar before intersection entrance)
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 4;
    // North inbound
    ctx.beginPath();
    ctx.moveTo(centerX - totalRoadWidth / 2, centerY - junctionHalf);
    ctx.lineTo(centerX, centerY - junctionHalf);
    // South inbound
    ctx.moveTo(centerX, centerY + junctionHalf);
    ctx.lineTo(centerX + totalRoadWidth / 2, centerY + junctionHalf);
    // West inbound
    ctx.moveTo(centerX - junctionHalf, centerY);
    ctx.lineTo(centerX - junctionHalf, centerY + totalRoadWidth / 2);
    // East inbound
    ctx.moveTo(centerX + junctionHalf, centerY - totalRoadWidth / 2);
    ctx.lineTo(centerX + junctionHalf, centerY);
    ctx.stroke();

    // 4. Compact Professional Traffic Signals
    const signals = simulationState?.traffic_light?.signals || {
      N: 'RED',
      S: 'RED',
      E: 'RED',
      W: 'RED',
    };

    const drawSignalHead = (x, y, state, armLabel) => {
      // Matte dark housing
      ctx.fillStyle = '#0f172a';
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.roundRect(x - 12, y - 12, 24, 24, 5);
      ctx.fill();
      ctx.stroke();

      const colorMap = {
        RED: '#ef4444',
        YELLOW: '#f59e0b',
        GREEN: '#10b981',
      };
      const lampColor = colorMap[state] || '#64748b';

      // Lamp with crisp indicator
      ctx.fillStyle = lampColor;
      ctx.beginPath();
      ctx.arc(x, y, 6.5, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Direction label
      ctx.fillStyle = '#334155';
      ctx.font = 'bold 10px monospace';
      ctx.fillText(armLabel, x - 3.5, y + 21);
    };

    drawSignalHead(centerX - totalRoadWidth / 2 - 16, centerY - junctionHalf - 6, signals.N, 'N');
    drawSignalHead(centerX + totalRoadWidth / 2 + 16, centerY + junctionHalf + 6, signals.S, 'S');
    drawSignalHead(centerX + junctionHalf + 6, centerY - totalRoadWidth / 2 - 16, signals.E, 'E');
    drawSignalHead(centerX - junctionHalf - 6, centerY + totalRoadWidth / 2 + 16, signals.W, 'W');

    // 5. Vehicles on Ground Layer
    const vehicles = simulationState?.vehicles || [];
    const groundVehicles = vehicles.filter((v) => !v.on_flyover);
    const flyoverVehicles = vehicles.filter((v) => v.on_flyover);

    const renderVehicle = (v) => {
      ctx.save();
      ctx.translate(v.x, v.y);
      ctx.rotate(v.angle);

      const vLength = Math.max(16, v.length * 3.2);
      const vWidth = Math.max(9, v.width * 3.2);

      // Soft contact shadow
      ctx.fillStyle = 'rgba(15, 23, 42, 0.35)';
      ctx.beginPath();
      ctx.roundRect(-vLength / 2 + 1.5, -vWidth / 2 + 1.5, vLength, vWidth, 2);
      ctx.fill();

      // Chassis Body
      ctx.fillStyle = v.color || '#2563eb';
      ctx.beginPath();
      ctx.roundRect(-vLength / 2, -vWidth / 2, vLength, vWidth, 3);
      ctx.fill();

      // Cabin / Roof
      ctx.fillStyle = 'rgba(15, 23, 42, 0.4)';
      ctx.fillRect(-vLength / 6, -vWidth / 2 + 1.5, vLength / 3, vWidth - 3);

      // Windshield
      ctx.fillStyle = '#e2e8f0';
      ctx.fillRect(vLength / 6, -vWidth / 2 + 1.5, 2, vWidth - 3);

      // Headlights
      ctx.fillStyle = '#fef08a';
      ctx.fillRect(vLength / 2 - 1.5, -vWidth / 2 + 1, 1.5, 2.5);
      ctx.fillRect(vLength / 2 - 1.5, vWidth / 2 - 3.5, 1.5, 2.5);

      // Tail / Brake Lights
      const isBraking = v.status === 'braking' || v.status === 'stopped';
      ctx.fillStyle = isBraking ? '#ef4444' : '#7f1d1d';
      ctx.fillRect(-vLength / 2, -vWidth / 2 + 1, 1.5, 2.5);
      ctx.fillRect(-vLength / 2, vWidth / 2 - 3.5, 1.5, 2.5);

      ctx.restore();
    };

    groundVehicles.forEach(renderVehicle);

    // 6. Grade-Separated Flyover Viaduct
    if (flyoverEnabled) {
      const viaductWidth = 38;
      const rampStart = 45;
      const rampEnd = height - 45;

      // Realistic structural drop shadow
      ctx.fillStyle = 'rgba(15, 23, 42, 0.18)';
      ctx.beginPath();
      ctx.roundRect(centerX - viaductWidth / 2 + 10, rampStart, viaductWidth, rampEnd - rampStart, 4);
      ctx.fill();

      // Concrete Viaduct Structure
      ctx.fillStyle = '#e2e8f0';
      ctx.fillRect(centerX - viaductWidth / 2 - 3, rampStart, viaductWidth + 6, rampEnd - rampStart);

      // Flyover Asphalt Surface
      ctx.fillStyle = '#334155';
      ctx.fillRect(centerX - viaductWidth / 2 + 2, rampStart + 8, viaductWidth - 4, rampEnd - rampStart - 16);

      // Viaduct Parapets / Barriers
      ctx.strokeStyle = '#94a3b8';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(centerX - viaductWidth / 2, rampStart);
      ctx.lineTo(centerX - viaductWidth / 2, rampEnd);
      ctx.moveTo(centerX + viaductWidth / 2, rampStart);
      ctx.lineTo(centerX + viaductWidth / 2, rampEnd);
      ctx.stroke();

      // Center divider on viaduct
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(centerX, rampStart + 10);
      ctx.lineTo(centerX, rampEnd - 10);
      ctx.stroke();

      // Render vehicles on viaduct
      flyoverVehicles.forEach(renderVehicle);

      // Badge
      ctx.fillStyle = '#0369a1';
      ctx.font = '600 12px system-ui, sans-serif';
      ctx.fillText('ELEVATED FLYOVER VIADUCT (FREE-FLOW BYPASS)', centerX - 145, 34);
    }
  }, [simulationState, lanes, flyoverEnabled]);

  return (
    <div
      ref={containerRef}
      className={`relative flex flex-col items-center justify-center bg-white border border-slate-200/90 rounded-2xl p-4 shadow-sm overflow-hidden w-full ${
        isFullscreen ? 'rounded-none border-none p-0' : ''
      }`}
    >
      {/* Top Left Status Badge */}
      <div className="absolute top-5 left-5 z-10 flex items-center gap-2 bg-white/95 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-slate-200 shadow-xs text-xs">
        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
        <span className="text-slate-800 font-semibold">Kinematic Viewport</span>
        <span className="text-slate-400 text-[11px]">· 900×900 High-Res</span>
      </div>

      {/* Top Right Fleet Legend + Fullscreen Toggle */}
      <div className="absolute top-5 right-5 z-10 flex items-center gap-3 bg-white/95 backdrop-blur-sm px-3.5 py-1.5 rounded-lg border border-slate-200 shadow-xs text-xs">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-xs bg-blue-600"></span>
          <span className="text-slate-700 font-medium">Car</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-xs bg-amber-500"></span>
          <span className="text-slate-700 font-medium">Bus</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-xs bg-red-600"></span>
          <span className="text-slate-700 font-medium">Truck</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-xs bg-emerald-600"></span>
          <span className="text-slate-700 font-medium">Bike</span>
        </div>

        {/* Divider */}
        <div className="w-px h-4 bg-slate-200"></div>

        {/* Fullscreen Button */}
        <button
          onClick={toggleFullscreen}
          title={isFullscreen ? 'Exit Fullscreen (Esc)' : 'View Fullscreen'}
          className="p-1 rounded-md hover:bg-slate-100 transition-colors text-slate-600 hover:text-slate-900 cursor-pointer"
        >
          {isFullscreen ? (
            <Minimize2 className="w-4 h-4" />
          ) : (
            <Maximize2 className="w-4 h-4" />
          )}
        </button>
      </div>

      <canvas
        ref={canvasRef}
        width={900}
        height={900}
        className={`rounded-xl border border-slate-200 bg-slate-50 shadow-inner ${
          isFullscreen
            ? 'w-full h-full max-w-none max-h-full object-contain rounded-none border-none'
            : 'w-full max-w-[850px] aspect-square'
        }`}
        style={isFullscreen ? { maxHeight: '100vh', aspectRatio: '1 / 1' } : undefined}
      />
    </div>
  );
}
