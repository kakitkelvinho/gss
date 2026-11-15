#!/usr/bin/env bash
# Select a Claude model and run a scored OpenCode episode: the same harness, instruction and
# simulator tools as the Gemini runs (scripts/run-gemini.sh), so only the model changes.
set -euo pipefail

cd "$(dirname "$0")/.."

if (( $# > 1 )); then
    printf 'Usage: bash scripts/run-claude.sh [Claude API model ID]\n' >&2
    exit 2
fi

if (( $# == 1 )); then
    model_id="$1"
else
    ids=(claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5 claude-fable-5-2)
    names=('Claude Opus 5.5' 'Claude Sonnet 5.5' 'Claude Haiku 5.5' 'Claude Fable 5.2')
    printf 'Choose a Claude model (this list is not a quality ranking):\n'
    for i in "${!ids[@]}"; do
        printf '  %d. %s (%s)\n' "$((i + 1))" "${names[$i]}" "${ids[$i]}"
    done
    printf '  %d. Enter an API model ID manually\n' "$((${#ids[@]} + 1))"
    IFS= read -r -p 'Number: ' choice </dev/tty
    if [[ "$choice" =~ ^[1-9][0-9]*$ ]] && (( choice <= ${#ids[@]} )); then
        model_id="${ids[$((choice - 1))]}"
    elif [[ "$choice" == "$((${#ids[@]} + 1))" ]]; then
        IFS= read -r -p 'API model ID: ' model_id </dev/tty
    else
        printf 'Choose a number from 1 to %d.\n' "$((${#ids[@]} + 1))" >&2
        exit 2
    fi
fi

model_id="${model_id#anthropic/}"
if [[ -z "$model_id" ]]; then
    printf 'A model ID is required.\n' >&2
    exit 2
fi

IFS= read -r -s -p "Anthropic API key: " ANTHROPIC_API_KEY </dev/tty
printf '\n' >&2
if [[ -z "$ANTHROPIC_API_KEY" ]]; then
    printf 'An Anthropic API key is required.\n' >&2
    exit 1
fi
export ANTHROPIC_API_KEY

# Check the key and model before starting the containers. The key goes in a header, never the URL.
status="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 \
    -H "x-api-key: $ANTHROPIC_API_KEY" -H 'anthropic-version: 2023-06-01' \
    "https://api.anthropic.com/v1/models/$model_id" || true)"
case "$status" in
    200) ;;
    401) printf 'The API key was rejected (HTTP 401).\n' >&2; exit 1 ;;
    403) printf 'This key cannot use %s (HTTP 403).\n' "$model_id" >&2; exit 1 ;;
    404) printf 'Model %s was not found for this key (HTTP 404).\n' "$model_id" >&2; exit 1 ;;
    *) printf 'Could not check the model (HTTP %s); continuing anyway.\n' "${status:-none}" >&2 ;;
esac

printf 'Using %s\n' "$model_id"
# Harbor passes ANTHROPIC_API_KEY to OpenCode's 'anthropic' provider. Current Claude models choose
# their own thinking depth, so no thinking budget is set here (unlike run-gemini.sh).
exec harbor run -p . -a opencode -m "anthropic/$model_id" -o ./jobs
