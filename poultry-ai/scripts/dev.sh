#!/usr/bin/env bash
set -euo pipefail

# Start FastAPI
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 &
BACK_PID=$!

# Start Vite
cd frontend
npm run dev -- --host

# Cleanup
kill $BACK_PID || true
