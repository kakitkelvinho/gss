#!/usr/bin/env bash
# Rebuild the deck: base-v2.html -> out/pitch-deck-v4.html -> v5 -> v6, then copy v6 to ../pitch-deck.html.
# Needs Node 18+. Regenerate scans.json first with: (cd .. && uv run python deck/grab-scans.py)
set -e; cd "$(dirname "$0")"; mkdir -p out
node 1-build-v4.js && node 2-posters-1-2.js && node 3-posters-rest.js
cp out/pitch-deck-v6.html ../pitch-deck.html
echo "Done: pitch-deck.html"
