#!/usr/bin/env bash
set -euo pipefail

# Run from scenarios/rich_v2x/ (or adjust relative paths).
netconvert \
  --node-files network/nodes.nod.xml \
  --edge-files network/edges.edg.xml \
  --output-file network/network.net.xml

printf 'Generated network/network.net.xml\n'
