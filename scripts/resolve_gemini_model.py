"""Resolve an AI Studio display name to a generateContent model ID for this API key.

Reads GEMINI_API_KEY from the environment, never from command-line arguments. This also
validates an explicitly supplied API ID against the project's model list.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def available_models(key: str) -> list[dict]:
    models: list[dict] = []
    page_token = ""
    while True:
        query = {"pageSize": 100}
        if page_token:
            query["pageToken"] = page_token
        request = urllib.request.Request(
            f"{API_URL}?{urllib.parse.urlencode(query)}",
            headers={"x-goog-api-key": key},
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.load(response)
        except urllib.error.HTTPError as error:
            raise SystemExit(
                f"Could not list models for this API key (HTTP {error.code}). "
                "Check the hackathon project and key in AI Studio."
            ) from None
        except urllib.error.URLError as error:
            raise SystemExit(f"Could not reach the Gemini Models API: {error.reason}") from None
        models.extend(data.get("models", []))
        page_token = data.get("nextPageToken", "")
        if not page_token:
            return models


def resolve(choice: str, models: list[dict]) -> str:
    wanted = normalise(choice.removeprefix("google/").removeprefix("models/"))
    supported = [m for m in models if "generateContent" in m.get("supportedGenerationMethods", [])]
    exact_id = [m for m in supported if normalise(m.get("name", "").removeprefix("models/")) == wanted]
    exact_display = [m for m in supported if normalise(m.get("displayName", "")) == wanted]
    prefix_display = [m for m in supported if normalise(m.get("displayName", "")).startswith(wanted)]
    for matches in (exact_id, exact_display, prefix_display):
        if len(matches) == 1:
            return matches[0]["name"].removeprefix("models/")
        if len(matches) > 1:
            ids = ", ".join(m["name"].removeprefix("models/") for m in matches)
            raise SystemExit(f"Several API models match {choice!r}: {ids}. Rerun and enter one exact API ID.")
    names = ", ".join(m.get("displayName", m.get("name", "?")) for m in supported[:15])
    raise SystemExit(f"No generateContent model matches {choice!r} for this key. Available examples: {names}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: resolve_gemini_model.py <display name or API model ID>")
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set")
    print(resolve(sys.argv[1], available_models(key)))


if __name__ == "__main__":
    main()
