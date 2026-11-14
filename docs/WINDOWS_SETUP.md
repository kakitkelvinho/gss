# Set up GSS and Harbor on a Windows laptop

Use **Ubuntu on WSL 2** with Docker Desktop's WSL integration. Run the project's Linux commands inside Ubuntu; Windows PowerShell is only needed for the first WSL installation. Keep the clone in Ubuntu's home directory for better Docker and file performance.

## One-time Windows steps

1. In an administrator PowerShell window, run `wsl --install -d Ubuntu`, then restart if prompted. Microsoft instructions: <https://learn.microsoft.com/windows/wsl/install>.
2. Install and start Docker Desktop for Windows. In Docker Desktop, enable **Settings → Resources → WSL Integration → Ubuntu**, then apply and restart. Docker instructions: <https://docs.docker.com/desktop/features/wsl/>.
3. Open Ubuntu and clone this repository into your Linux home directory (for example `~/gss`). If the repo is private, authenticate Git using your normal GitHub access. Run `cd ~/gss`.

The repository includes an interactive setup script:

```bash
bash scripts/setup-harbor-wsl.sh
```

It checks WSL and Docker, guides uv installation, installs Harbor, runs the local tests, and runs the scripted expert through Harbor. It does not ask for or save an API key. If a prerequisite is missing, complete that step and rerun the script.

## Run a Gemini agent

Use an API key from your own hackathon project in AI Studio. The run script prompts for it each time and does not save it in the repo:

```bash
bash scripts/run-gemini.sh GEMINI_API_MODEL_ID
```

Replace `GEMINI_API_MODEL_ID` with the exact model ID shown in AI Studio. Do not type angle brackets around it. The result goes under `jobs/`; that directory is ignored by Git. In the newest job, inspect `verifier/reward.txt`, `verifier/diagnostics.json`, and `verifier/trajectory.json`. The score should be in `[0, 1]`. The scripted expert should score around `0.9`; a frontier model's score can be lower.

To summarise all runs:

```bash
python3 scripts/summarise_jobs.py jobs/
```

## If an AI assistant is helping with setup

Give it this file, `task.toml`, `environment/docker-compose.yaml`, and `docs/SUBMISSION.md` if present. Ask it to work **inside Ubuntu on WSL 2**, verify `docker info`, `uv --version`, and `harbor --help`, then run the oracle before trying a model. Do not send it an API key in chat. Enter the key locally when `run-gemini.sh` prompts. If Docker reports that its daemon is unavailable, check Docker Desktop's WSL integration first. If the oracle works but the model run fails, inspect the job's `agent/` and `trial.log` files before changing the simulator.
