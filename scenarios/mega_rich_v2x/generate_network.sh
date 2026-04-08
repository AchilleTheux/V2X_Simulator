#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

netconvert \
  --node-files network/nodes.nod.xml \
  --edge-files network/edges.edg.xml \
  --output-file network/network.net.xml

echo "Generated: $SCRIPT_DIR/network/network.net.xml"
