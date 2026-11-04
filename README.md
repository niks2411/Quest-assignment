# Agent-Based Traffic Simulation & Analytics System

An interactive traffic simulation platform that models how vehicles move through an urban road network. Built with **Python, FastAPI, React, Vite, Tailwind CSS, and HTML Canvas**, the system simulates traffic at a four-way intersection and helps analyze how road infrastructure and traffic signals affect congestion.

Each vehicle behaves independently, following realistic driving rules such as acceleration, braking, and maintaining safe distances. The simulation uses the **Intelligent Driver Model (IDM)** to reproduce vehicle movement and traffic interactions.

## Project Architecture

The project is organized into two main parts:

- **Backend:** Manages vehicle movement, traffic signals, road networks, simulation logic, and traffic analytics.
- **Frontend:** Provides an interactive dashboard to configure scenarios, control simulations, and view live traffic statistics.

```text
Traffic assignment/
├── backend/
│   ├── main.py                  # FastAPI application and WebSocket streaming
│   ├── requirements.txt         # Backend dependencies
│   ├── simulation/
│   │   ├── vehicle.py           # Vehicle types and behavior
│   │   ├── idm.py               # Vehicle movement and following model
│   │   ├── physics.py           # Movement calculations and collision checks
│   │   ├── road.py              # Road network, lanes, and capacity
│   │   ├── traffic_light.py     # Fixed and adaptive traffic signals
│   │   ├── junction.py          # Intersection and turning logic
│   │   └── metrics.py           # Traffic performance calculations
│   ├── models/
│   │   └── scenario.py          # Scenario configurations and presets
│   └── tests/                   # Automated backend tests
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── RoadCanvas.jsx       # Visual representation of traffic
    │   │   ├── MetricsCards.jsx     # Live traffic statistics
    │   │   ├── ControlsBar.jsx      # Simulation playback controls
    │   │   ├── ScenarioForm.jsx     # Scenario selection and configuration
    │   │   ├── QueueVisualizer.jsx  # Traffic queues by direction
    │   │   └── TrafficCharts.jsx    # Speed and queue charts
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── package.json
    └── vite.config.js
```

## Key Features

### 1. Vehicle Simulation Using IDM

Each vehicle is modeled as an independent agent. Its behavior depends on its current speed, acceleration, nearby vehicles, and traffic signals.

The system uses the **Intelligent Driver Model (IDM)**, introduced by Treiber et al. (2000), to calculate vehicle acceleration and maintain safe following distances.

The model considers:

- Current vehicle speed and desired speed.
- Distance from the vehicle ahead.
- Relative speed between vehicles.
- Safe following distance and braking behavior.

The simulation supports four types of vehicles:

| Vehicle | Length | Maximum Speed | Acceleration |
|---|---:|---:|---:|
| Car | 4.5 m | 60 km/h | 2.5 m/s² |
| Bus | 10.5 m | 45 km/h | 1.2 m/s² |
| Truck | 12 m | 40 km/h | 1.0 m/s² |
| Motorcycle | 2.2 m | 65 km/h | 3.2 m/s² |

Additional features include smooth braking, safe vehicle spacing, and collision prevention.

### 2. Road Network and Infrastructure

The simulation models a four-way intersection connected by four roads: North Avenue, South Boulevard, East Expressway, and West Parkway.

Users can configure different road layouts and study their impact on traffic flow.

Key capabilities include:

- Support for 1, 2, and 4 lanes per direction.
- Dynamic road capacity calculations.
- Vehicle movement through the intersection.
- An elevated North–South flyover that allows vehicles to bypass the ground-level intersection without waiting for its traffic signals.

### 3. Traffic Signal Management

Two traffic signal strategies are available:

**Fixed Signal Control**

Traffic lights follow a predefined cycle with green, yellow, and red phases.

**Adaptive Signal Control**

The system monitors traffic queues and adjusts green-light allocation based on the number of waiting vehicles in different directions.

These modes make it possible to compare conventional signal timing with traffic-responsive signal management.

### 4. Real-Time Traffic Analytics

The dashboard tracks traffic conditions as the simulation runs.

| Metric | Description |
|---|---|
| Average Speed | Average speed of active vehicles |
| Average Waiting Time | Time vehicles spend stopped or moving below 0.8 m/s |
| Directional Queues | Number of waiting vehicles on North, South, East, and West roads |
| Throughput | Number of vehicles passing through the network per minute |
| Road Utilization | Percentage of available road capacity currently occupied |

Live charts also display changes in vehicle speed and queue lengths over time.

## Simulation Scenarios

The system includes four predefined scenarios for comparing different traffic conditions and management strategies.

### Scenario A – Normal Traffic
- 50 vehicles.
- Two lanes per direction.
- Standard traffic signal cycle.
- Represents regular traffic conditions.

### Scenario B – Peak-Hour Congestion
- 180 vehicles.
- High vehicle arrival rate of 2.2 vehicles per second.
- Simulates heavy traffic and intersection congestion.

### Scenario C – Flyover Implementation
- Uses the same vehicle count and arrival rate as Scenario B.
- Activates the North–South elevated flyover.
- Demonstrates how grade-separated roads can reduce signal-related delays for bypass traffic.

### Scenario D – Adaptive Traffic Signals
- 160 vehicles.
- Enables real-time queue monitoring.
- Adjusts green-light timing according to traffic demand.

## Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Frontend | React, Vite, Tailwind CSS |
| Visualization | HTML Canvas, Recharts |
| Real-Time Communication | WebSockets |
| Simulation | Intelligent Driver Model (IDM) |
| Testing | Pytest |

## Getting Started

### Prerequisites

Install the following before running the application:

- Python 3.10 or later
- Node.js 18 or later
- npm

The project was developed and tested with Python 3.13.5 and Node.js 22.17.1.

### 1. Start the Backend

Open a terminal in the project directory:

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

The backend will be available at:

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/ws/simulation

### 2. Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser to access the simulation dashboard.

## Running Automated Tests

The backend includes automated tests for the simulation logic and API endpoints.

Run the test suite with:

```bash
cd backend
python -m pytest -v
```

The tests cover:

- IDM acceleration and braking calculations.
- Vehicle movement and collision detection.
- Simulation steps and vehicle spawning.
- Flyover routing and traffic signal behavior.
- FastAPI endpoints and integration.

**Initial test report:** 16 automated unit and API integration tests passed. Run the command above to verify the current test results.

## Project Goal

The aim of this project is to understand how vehicle behavior, road infrastructure, and traffic signal strategies influence urban traffic conditions.

By combining microscopic vehicle simulation with real-time analytics, the system provides an interactive environment for studying congestion and comparing possible traffic management improvements.