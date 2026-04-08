# Mega Rich SUMO Scenario (Dense Multi-Actor V2X)

This scenario is richer than `ultra_rich_v2x` and designed for repeated
strategy comparisons with many dangerous proximity opportunities.

## What is richer here

- 3x3 road grid (9 intersections) with 12 boundary entry/exit points.
- 20 deterministic vehicles (cars + buses) with straight and turning routes.
- 16 deterministic VRUs (pedestrians + cyclist-like persons).
- 4 pedestrian corridors (horizontal, vertical, 2 diagonals) crossing near the
  central area to produce frequent vehicle/VRU proximity events.

## Design choices

- Deterministic by construction (`sigma=0`, `speedDev=0`, fixed seed, sorted departures).
- Simple but dense geometry for robust tests and reproducible metrics.
- VRU corridors pass through/near central roads so danger detection is stressed
  without requiring radio-level complexity.

## Files

- `network/nodes.nod.xml`
- `network/edges.edg.xml`
- `routes.rou.xml`
- `scenario.sumocfg`
- `generate_network.sh`

## Generate and run

```bash
cd scenarios/mega_rich_v2x
bash generate_network.sh
sumo -c scenario.sumocfg
```

Or with GUI:

```bash
sumo-gui -c scenario.sumocfg
```
