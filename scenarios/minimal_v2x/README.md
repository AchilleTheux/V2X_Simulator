# Minimal SUMO Scenario (Vehicle + VRU)

This folder contains a deterministic and test-friendly V2X scenario.

## Files and roles

- `network/nodes.nod.xml`: network nodes (geometry points).
- `network/edges.edg.xml`: network edges and allowed actor classes.
- `generate_network.sh`: reproducible command to generate `network/network.net.xml`.
- `network/network.net.xml`: compiled SUMO network (generated file).
- `routes.rou.xml`: one vehicle and one pedestrian definitions.
- `scenario.sumocfg`: main SUMO scenario configuration.

## Why this scenario is useful for proximity detection

- Only two actors are present, so debugging is straightforward.
- Trajectories are fixed and deterministic.
- The vehicle path and pedestrian path cross near `(50, 0)`, creating a
  predictable close-approach event around `t ~= 3.6 s`.

## Generate the network

From `scenarios/minimal_v2x/`:

```bash
bash generate_network.sh
```

Equivalent direct command:

```bash
netconvert --node-files network/nodes.nod.xml --edge-files network/edges.edg.xml --output-file network/network.net.xml
```

## Run with SUMO

```bash
sumo -c scenario.sumocfg
```

Or with GUI:

```bash
sumo-gui -c scenario.sumocfg
```
