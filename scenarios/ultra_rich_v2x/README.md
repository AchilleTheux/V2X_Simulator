# Ultra Rich SUMO Scenario (Grid + Multi-Actor)

This scenario is denser than `rich_v2x` and targets stress-testing of full V2X
pipelines (danger detection, strategy selection, communication simulation,
reward accumulation, and metrics export).

## Highlights

- 2x2 road-grid with 4 intersections and 8 vehicle boundary points.
- 12 deterministic vehicles (cars + buses) on diverse routes.
- 8 deterministic VRUs (pedestrians + cyclist-like persons).
- Multiple VRU corridors crossing central road areas.

## Files

- `network/nodes.nod.xml`
- `network/edges.edg.xml`
- `routes.rou.xml`
- `scenario.sumocfg`
- `generate_network.sh`

## Generate and run

```bash
cd scenarios/ultra_rich_v2x
bash generate_network.sh
sumo -c scenario.sumocfg
```

Or with GUI:

```bash
sumo-gui -c scenario.sumocfg
```
