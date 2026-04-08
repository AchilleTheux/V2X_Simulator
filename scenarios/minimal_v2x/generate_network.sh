#!/usr/bin/env bash
set -euo pipefail

# Run from scenarios/minimal_v2x/ (or adjust paths accordingly).
netconvert \
  --node-files network/nodes.nod.xml \
  --edge-files network/edges.edg.xml \
  --output-file network/network.net.xml

printf 'Generated network/network.net.xml\n'
