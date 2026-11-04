"""
Integration Tests for FastAPI Endpoints
Tests REST APIs for status, scenario switching, simulation control, and metrics.
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "traffic_light" in data
    assert "vehicles" in data


def test_scenarios_listing():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "presets" in data
    assert "normal" in data["presets"]
    assert "peak_hour" in data["presets"]
    assert "flyover_bypass" in data["presets"]


def test_simulation_control_flow():
    # 1. Start
    res_start = client.post("/api/control", json={"action": "start"})
    assert res_start.status_code == 200
    assert res_start.json()["is_running"] is True

    # 2. Step
    res_step = client.post("/api/control", json={"action": "step"})
    assert res_step.status_code == 200
    assert res_step.json()["state"]["sim_time"] > 0

    # 3. Pause
    res_pause = client.post("/api/control", json={"action": "pause"})
    assert res_pause.status_code == 200
    assert res_pause.json()["is_running"] is False

    # 4. Reset
    res_reset = client.post("/api/control", json={"action": "reset"})
    assert res_reset.status_code == 200
    assert res_reset.json()["state"]["sim_time"] == 0.0


def test_apply_preset():
    response = client.post("/api/scenarios/preset", json={"preset_key": "flyover_bypass"})
    assert response.status_code == 200
    data = response.json()
    assert data["state"]["scenario"]["flyover_enabled"] is True
