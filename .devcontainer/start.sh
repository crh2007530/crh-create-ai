#!/usr/bin/env bash
set -euo pipefail

mkdir -p .devcontainer/logs

if ! pgrep -f "uvicorn app.main:app" >/dev/null 2>&1; then
  (
    cd apps/api
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ) > .devcontainer/logs/api.log 2>&1 &
fi

if ! pgrep -f "next dev" >/dev/null 2>&1; then
  (
    cd apps/web
    API_INTERNAL_URL=http://127.0.0.1:8000 NEXT_PUBLIC_API_URL=/api/backend npm run dev -- --hostname 0.0.0.0
  ) > .devcontainer/logs/web.log 2>&1 &
fi

echo "crh create AI is starting."
echo "Open the forwarded 3000 port in GitHub Codespaces."
