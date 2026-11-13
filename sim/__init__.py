"""GSS 'Find Time Zero' physics core (pure Python, stdlib only).

The only public entry point is `Episode` in `sim.episode`. Every agent action goes through
`Episode.call(tool, args)`, which does validation, lab-time accounting, walking and logging.
The MCP layer must never bypass it.
"""

from sim.episode import Episode  # noqa: F401
