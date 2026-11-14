"""Score the episode from the simulator's true final state. Stdlib only."""

import json
import os
import shutil

SRC = os.environ.get("GSS_RESULT_DIR", "/gss/out")
OUT = os.environ.get("GSS_VERIFIER_DIR", "/logs/verifier")


def main():
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(SRC, "result.json")
    if not os.path.exists(path):
        print(f"no result at {path}: the simulator state was not collected; reward 0")
        with open(os.path.join(OUT, "reward.txt"), "w") as f:
            f.write("0\n")
        return
    with open(path) as f:
        res = json.load(f)
    reward = float(res.get("reward", 0.0))
    if not (0.0 <= reward <= 1.0):  # also rejects NaN
        reward = 0.0
    with open(os.path.join(OUT, "reward.txt"), "w") as f:
        f.write(f"{reward!r}\n")
    with open(os.path.join(OUT, "reward.json"), "w") as f:
        json.dump({"reward": reward}, f)  # Harbor reports every key here as a reward: score only
    # Diagnostics (O, |dt|, cost, lab time, ...) are not part of the reward.
    with open(os.path.join(OUT, "diagnostics.json"), "w") as f:
        json.dump(res, f, indent=1)
    traj = os.path.join(SRC, "trajectory.json")
    if os.path.exists(traj):
        shutil.copy(traj, os.path.join(OUT, "trajectory.json"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
