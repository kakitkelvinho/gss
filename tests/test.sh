#!/bin/bash
# Verifier: scores from /gss/out/result.json, the simulator's true final state, which the collect
# hook read from the sim container after the agent's container was stopped. Writes
# /logs/verifier/reward.txt (one float in [0, 1]) and reward.json (numeric diagnostics).
mkdir -p /logs/verifier
python3 /tests/score.py || echo 0 > /logs/verifier/reward.txt
exit 0
