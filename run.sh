#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv not found. Install from https://docs.astral.sh/uv/" >&2
  exit 1
fi

exec uv run --with-requirements requirements.txt uvicorn app:app --host "$HOST" --port "$PORT"
