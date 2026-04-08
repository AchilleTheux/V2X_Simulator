# Rich SUMO Scenario (Multi-actor V2X)

This scenario extends `minimal_v2x` with more actors and interaction patterns
while staying deterministic and easy to debug.

## What is richer here

- 4-way vehicle intersection around `(0, 0)`.
- 4 vehicles with different trajectories (including one turning vehicle).
- 3 VRUs (`ped_0`, `ped_1`, `cyc_0`) on two pedestrian corridors.
- Deterministic departures and speeds (`sigma=0`, `speedDev=0`, fixed seed).

## Why this is useful

- Produces several close approaches over the same run.
- Better for stress-testing context building, danger detection, and reward logic.
- Still small enough for step-by-step tracing in TraCI.

## Files

- `network/nodes.nod.xml`
- `network/edges.edg.xml`
- `routes.rou.xml`
- `scenario.sumocfg`
- `generate_network.sh`

## Generate network

```bash
cd scenarios/rich_v2x
bash generate_network.sh
```

Equivalent command:

```bash
netconvert --node-files network/nodes.nod.xml --edge-files network/edges.edg.xml --output-file network/network.net.xml
```

## Run

```bash
sumo -c scenario.sumocfg
```

or

```bash
sumo-gui -c scenario.sumocfg
```
