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

# Lower Gemini's thinking per model turn. At OpenCode's default level, Gemini 4 Hydrogen and Carbon
# spent the whole 32k output budget reasoning in one turn; the turn ended with finish_reason
# "length" and no tool call, and OpenCode ended the session.
# Gemini 3/4 models take a thinking *level*, and OpenCode already sends one, so we override that
# value. Adding a thinkingBudget next to it is rejected with HTTP 400 ("You can only set only one
# of thinking budget and thinking level"). Older models (Gemini 2.5) use budgets instead, so they
# get no override. Set GEMINI_THINKING_LEVEL to minimal, low, medium or high, or "none" to send
# OpenCode's default.
thinking_level="${GEMINI_THINKING_LEVEL:-low}"
extra_args=()
if [[ "$thinking_level" != "none" && "$model_id" =~ ^gemini-[3-9] ]]; then
    case "$thinking_level" in
        minimal|low|medium|high) ;;
        *) printf 'GEMINI_THINKING_LEVEL must be minimal, low, medium, high or "none".\n' >&2; exit 2 ;;
    esac
    printf 'Thinking level: %s\n' "$thinking_level"
    # Harbor merges opencode_config into the opencode.json it writes for the agent.
    extra_args+=(--ak "opencode_config={\"provider\":{\"google\":{\"models\":{\"$model_id\":{\"options\":{\"thinkingConfig\":{\"thinkingLevel\":\"$thinking_level\"}}}}}}}")
fi

# Harbor recognises the 'gemini' provider and passes its key to OpenCode's 'google' provider.
exec harbor run -p . -a opencode -m "gemini/$model_id" -o ./jobs "${extra_args[@]}"
