# V2X Communication Simulator Skeleton

This repository contains a clean Python skeleton for an academic V2X project
based on SUMO + Python.

## Goals

- Simulate interactions between VRU (pedestrian/cyclist) and vehicles.
- Detect dangerous proximity situations.
- Choose a communication mode:
  - direct VRU <-> vehicle
  - via infrastructure (RSU)
- Prepare later integration of MAB strategies (for example Thompson sampling).

## Project layout

- `v2x_sim/sumo_runner.py`: SUMO lifecycle wrapper (start/step/stop).
- `v2x_sim/context_builder.py`: builds typed scene context objects.
- `v2x_sim/danger_detector.py`: danger event interface and detector skeleton.
- `v2x_sim/communication_model.py`: communication decision abstractions.
- `v2x_sim/baseline.py`: simple threshold-based baseline policy.
- `v2x_sim/thompson.py`: placeholder for Thompson sampling MAB policy.
- `v2x_sim/metrics.py`: lightweight experiment metrics collector.
- `v2x_sim/logger.py`: shared logger configuration utility.
- `v2x_sim/main.py`: minimal orchestration entry point.
- `tests/`: pytest test skeletons.

## Quick start

Run the skeleton simulation loop:

```bash
python -m v2x_sim.main --steps 20
```

Run tests:

```bash
pytest -q
```

## Ubuntu Setup (Required Tools)

Install base Python tools:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-pytest
```

Install SUMO tools:

```bash
sudo apt install -y sumo sumo-tools sumo-doc
```

Check installation:

```bash
python3 --version
pytest --version
sumo --version
netconvert --version
```

## Validation Tests

Run unit tests:

```bash
pytest -q
```

Generate and run the minimal SUMO scenario test:

```bash
cd scenarios/minimal_v2x
bash generate_network.sh
sumo -c scenario.sumocfg --duration-log.statistics
```

## Notes

- No advanced logic is implemented yet.
- SUMO/TraCI integration points are marked with TODO comments.
- Modules are intentionally small and typed for easy extension.

## Minimal SUMO Scenario

- Scenario folder: `scenarios/minimal_v2x/`
- Main config: `scenarios/minimal_v2x/scenario.sumocfg`
- Scenario documentation: `scenarios/minimal_v2x/README.md`
