#!/usr/bin/env bash
# Select a Gemini model, resolve its API ID, and run a scored OpenCode episode.
set -euo pipefail

cd "$(dirname "$0")/.."

if (( $# > 1 )); then
    printf 'Usage: bash scripts/run-gemini.sh [Gemini API model ID]\n' >&2
    exit 2
fi

if (( $# == 1 )); then
    model_choice="$1"
else
    choices=(
        'Gemini 3.1 Pro'
        'Gemini 4 Argon'
        'Gemini 4 Carbon'
        'Gemini 4 Hydrogen'
        'Gemini 3.8 Flash'
        'Gemini 2.5 Pro'
    )
    printf 'Choose a Gemini model (this list is not a quality ranking):\n'
    for i in "${!choices[@]}"; do
        printf '  %d. %s\n' "$((i + 1))" "${choices[$i]}"
    done
    printf '  %d. Enter an API model ID manually\n' "$((${#choices[@]} + 1))"
    IFS= read -r -p 'Number: ' choice </dev/tty
    if [[ "$choice" =~ ^[1-9][0-9]*$ ]] && (( choice <= ${#choices[@]} )); then
        model_choice="${choices[$((choice - 1))]}"
    elif [[ "$choice" == "$((${#choices[@]} + 1))" ]]; then
        IFS= read -r -p 'API model ID: ' model_choice </dev/tty
    else
        printf 'Choose a number from 1 to %d.\n' "$((${#choices[@]} + 1))" >&2
        exit 2
    fi
fi

if [[ -z "$model_choice" ]]; then
    printf 'A model name or API ID is required.\n' >&2
    exit 2
fi

IFS= read -r -s -p "Gemini API key: " GOOGLE_GENERATIVE_AI_API_KEY </dev/tty
printf '\n' >&2
if [[ -z "$GOOGLE_GENERATIVE_AI_API_KEY" ]]; then
    printf 'A Gemini API key is required.\n' >&2
    exit 1
fi
export GOOGLE_GENERATIVE_AI_API_KEY

model_id="$(python3 scripts/resolve_gemini_model.py "$model_choice")"
printf 'Using %s (API ID: %s)\n' "$model_choice" "$model_id"
# Harbor recognises the 'gemini' provider and passes its key to OpenCode's 'google' provider.
exec harbor run -p . -a opencode -m "gemini/$model_id" -o ./jobs
