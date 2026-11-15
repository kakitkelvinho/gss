"""Build the static archive manifest and aggregate statistics from checked-in run files.

    python3 scripts/build_run_index.py

Run files are independent so two contributors can commit different runs without editing a
shared generated file. GitHub Pages builds this manifest during deployment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "gss.viewer.v1"
INDEX_SCHEMA = "gss.archive.v1"


def file_for(run_id: str) -> str:
    return hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:24] + ".json"


def save_run(run: dict, directory: Path) -> Path:
    if run.get("meta", {}).get("schema_version") != SCHEMA or not run.get("id"):
        raise ValueError("invalid viewer run")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / file_for(run["id"])
    content = json.dumps(run, separators=(",", ":"), ensure_ascii=False) + "\n"
    if path.exists() and json.loads(path.read_text()) != json.loads(content):
        raise ValueError(f"run ID collision with different content: {run['id']}")
    if not path.exists():
        path.write_text(content)
    return path


def summary(runs: list[dict]) -> dict:
    rewards = [float(r["diagnostics"]["reward"]) for r in runs]
    tags = Counter(t[0] for r in runs for t in r.get("failure_tags", []))
    usage = [r["agent_usage"] for r in runs if r.get("agent_usage")]
    return {"count": len(runs), "mean_reward": round(statistics.mean(rewards), 6) if rewards else None,
            "median_reward": round(statistics.median(rewards), 6) if rewards else None,
            "best_reward": round(max(rewards), 6) if rewards else None,
            "old_scorer_count": sum(bool(r.get("old_scorer")) for r in runs),
            "usage_covered_runs": len(usage),
            "cost_covered_runs": sum("cost_usd" in u for u in usage),
            "total_input_tokens": sum(u.get("n_input_tokens", 0) for u in usage),
            "total_output_tokens": sum(u.get("n_output_tokens", 0) for u in usage),
            "total_cost_usd": round(sum(u.get("cost_usd", 0) for u in usage), 4),
            "failure_tags": dict(sorted(tags.items()))}


def build_index(directory: Path, output: Path) -> dict:
    runs = []
    seen = set()
    for path in sorted(directory.glob("*.json")):
        run = json.loads(path.read_text())
        if run.get("meta", {}).get("schema_version") != SCHEMA:
            raise ValueError(f"unsupported run schema: {path}")
        if path.name != file_for(run["id"]):
            raise ValueError(f"run filename does not match its ID: {path}")
        if run["id"] in seen:
            raise ValueError(f"duplicate run ID: {run['id']}")
        seen.add(run["id"])
        runs.append((path, run))
    if not runs:
        raise ValueError(f"no run files found in {directory}")
    runs.sort(key=lambda item: item[1]["id"])
    entries = [{"id": r["id"], "file": "runs/" + p.name, "label": r["label"],
                "model": r["model"], "seed": r["meta"]["seed"], "level": r["meta"]["level"],
                "reward": r["diagnostics"]["reward"], "eta": r["diagnostics"].get("eta"),
                "cost_eur": r["diagnostics"].get("cost_eur"),
                "lab_time_min": r["diagnostics"].get("lab_time_min"),
                "tool_calls": r["diagnostics"].get("tool_calls"),
                "ended_by": r["diagnostics"].get("ended_by"),
                "agent_usage": r.get("agent_usage"),
                "old_scorer": bool(r.get("old_scorer")),
                "today_reward": r.get("today_reward"),
                "failure_tags": [t[0] for t in r.get("failure_tags", [])],
                "replayable": bool(r["trajectory"])} for p, r in runs]
    groups = defaultdict(list)
    for _, run in runs:
        groups[(run["model"], run["meta"]["level"])].append(run)
    index = {"schema_version": INDEX_SCHEMA, "summary": summary([r for _, r in runs]),
             "by_model_level": [{"model": model, "level": level, **summary(group)}
                                for (model, level), group in sorted(groups.items())],
             "runs": entries}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(index, separators=(",", ":"), ensure_ascii=False) + "\n")
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "viewer/runs")
    parser.add_argument("--output", type=Path, default=ROOT / "viewer/runs_index.json")
    args = parser.parse_args()
    index = build_index(args.runs, args.output)
    print(f"indexed {index['summary']['count']} runs in {args.output}")


if __name__ == "__main__":
    main()
