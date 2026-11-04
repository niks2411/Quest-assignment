"""
FastAPI Main Application
Provides RESTful simulation control APIs and real-time WebSocket state streaming.
"""
import os
import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from simulation.engine import SimulationEngine
from models.scenario import ScenarioConfig, SCENARIO_PRESETS

app = FastAPI(
    title="Agent-Based Traffic Simulation Engine",
    description="Microscopic traffic simulation modeling roads, junctions, flyovers, and IDM car-following dynamics.",
    version="1.0.0",
)

# CORS configuration: configurable via environment variable
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Simulation Instance
engine = SimulationEngine(scenario=SCENARIO_PRESETS["normal"])
sim_speed_multiplier: float = 1.0


class ControlActionRequest(BaseModel):
    action: str  # "start", "pause", "step", "reset"
    speed_multiplier: Optional[float] = None


class ApplyPresetRequest(BaseModel):
    preset_key: str


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Traffic Simulation Backend",
        "endpoints": {
            "status": "/api/status",
            "scenarios": "/api/scenarios",
            "control": "/api/control",
            "websocket": "/ws/simulation",
        },
    }


@app.get("/api/status")
def get_status():
    """Retrieve instantaneous simulation state."""
    return engine.get_state()


@app.get("/api/scenarios")
def list_scenarios():
    """Returns available scenario presets and current active configuration."""
    presets = {k: v.model_dump() for k, v in SCENARIO_PRESETS.items()}
    return {
        "current": engine.scenario.model_dump(),
        "presets": presets,
    }


@app.post("/api/scenarios/custom")
def configure_custom_scenario(config: ScenarioConfig):
    """Applies a custom scenario configuration and resets the simulation."""
    engine.reset(scenario=config)
    return {"message": "Custom scenario applied successfully", "scenario": engine.scenario.model_dump()}


@app.post("/api/scenarios/preset")
def apply_preset(req: ApplyPresetRequest):
    """Applies a named preset scenario."""
    if req.preset_key not in SCENARIO_PRESETS:
        raise HTTPException(status_code=400, detail=f"Unknown preset '{req.preset_key}'")
    preset = SCENARIO_PRESETS[req.preset_key]
    engine.reset(scenario=preset)
    return {"message": f"Preset '{preset.name}' applied", "state": engine.get_state()}


@app.post("/api/control")
def control_simulation(req: ControlActionRequest):
    """Unified control endpoint: start, pause, step, reset, speed."""
    global sim_speed_multiplier
    action = req.action.lower()

    if action == "start":
        engine.start()
    elif action == "pause":
        engine.pause()
    elif action == "step":
        engine.step()
    elif action == "reset":
        engine.reset()
    elif action == "speed" and req.speed_multiplier is not None:
        sim_speed_multiplier = max(0.25, min(5.0, req.speed_multiplier))
    else:
        raise HTTPException(status_code=400, detail=f"Invalid action '{action}'")

    return {
        "action": action,
        "is_running": engine.is_running,
        "speed_multiplier": sim_speed_multiplier,
        "state": engine.get_state(),
    }


@app.websocket("/ws/simulation")
async def websocket_simulation_stream(websocket: WebSocket):
    """
    WebSocket endpoint streaming 20-30 FPS updates of vehicle positions and KPIs
    when the simulation is running, and listening for client commands.
    """
    await websocket.accept()
    global sim_speed_multiplier

    try:
        # Send immediate initial state
        await websocket.send_json(engine.get_state())

        while True:
            # Check for incoming client messages without blocking
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.04)
                payload = json.loads(data)
                cmd = payload.get("cmd")
                if cmd == "start":
                    engine.start()
                elif cmd == "pause":
                    engine.pause()
                elif cmd == "reset":
                    engine.reset()
                    await websocket.send_json(engine.get_state())
                elif cmd == "step":
                    state = engine.step()
                    await websocket.send_json(state)
                elif cmd == "speed":
                    sim_speed_multiplier = max(0.25, min(5.0, float(payload.get("value", 1.0))))
                elif cmd == "apply_preset":
                    p_key = payload.get("preset")
                    if p_key in SCENARIO_PRESETS:
                        engine.reset(scenario=SCENARIO_PRESETS[p_key])
                        engine.start()
                        await websocket.send_json(engine.get_state())
            except asyncio.TimeoutError:
                pass  # Normal stream tick

            # Advance simulation if running
            if engine.is_running:
                # Step with multiplier
                effective_dt = engine.dt * sim_speed_multiplier
                state = engine.step(custom_dt=effective_dt)
                await websocket.send_json(state)
            else:
                # Idle heartbeat update (light state or config changes)
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket client error: {e}")
