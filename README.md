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

## Notes

- No advanced logic is implemented yet.
- SUMO/TraCI integration points are marked with TODO comments.
- Modules are intentionally small and typed for easy extension.
