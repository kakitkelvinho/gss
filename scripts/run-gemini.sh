#!/usr/bin/env bash
# Run a scored OpenCode episode with a Gemini API key entered for this run only.
set -euo pipefail

model_id="${1:?Usage: bash scripts/run-gemini.sh <Gemini API model ID>}"
cd "$(dirname "$0")/.."

IFS= read -r -s -p "Gemini API key: " GEMINI_API_KEY </dev/tty
printf '\n' >&2
if [[ -z "$GEMINI_API_KEY" ]]; then
    printf 'A Gemini API key is required.\n' >&2
    exit 1
fi
export GEMINI_API_KEY

exec harbor run -p . -a opencode -m "google/$model_id" -o ./jobs
