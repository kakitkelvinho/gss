# Harbor run logs

Unedited Harbor job folders (`harbor run -p . -a <agent> ...`), kept so the reported scores can be
checked. Each trial folder has `verifier/reward.txt` (the score), `verifier/diagnostics.json` (final
physics), `verifier/trajectory.json` (every tool call with lab time) and, for OpenCode runs,
`agent/opencode.txt` (the agent's own log). OpenCode's internal database and file snapshots are left
out; nothing else is removed. Every run can also be replayed step by step at
<https://kakitkelvinho.github.io/gss/>.

| job | agent / model | seed | level | reward |
|---|---|---|---|---|
| `2026-11-14__15-54-53` | oracle (scripted expert) | 1 | 1 | 0.908 |
| `2026-11-14__15-56-19` | oracle (scripted expert) | 1 | 2 | 0.907 |
| `2026-11-15__01-00-16` | OpenCode + gemini-3.1-pro-preview | 1 | 1 | 0.000 |
| `2026-11-15__01-12-43` | OpenCode + gemini-3.1-pro-preview | 1 | 1 | 0.000 |
| `2026-11-15__01-34-04` | OpenCode + gemini-3.1-pro-preview | 2 | 1 | 0.000 |
| `2026-11-15__01-42-54` | OpenCode + gemini-3.1-pro-preview | 3 | 1 | 0.000 |

The oracle runs were graded by the scorer before `78cd401`; today's grader gives 0.909 and 0.908.
The Gemini runs were graded by the current scorer. Why they failed: [docs/gemini-pro-results.md](../../docs/gemini-pro-results.md).
