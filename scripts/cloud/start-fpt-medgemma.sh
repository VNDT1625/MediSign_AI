#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/MediSign_AI}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"

cd "$APP_DIR"
. .venv/bin/activate

export MEDISIGN_BASE_MODEL="${MEDISIGN_BASE_MODEL:-google/medgemma-1.5-4b-it}"
export MEDISIGN_ADAPTER_PATH="${MEDISIGN_ADAPTER_PATH:-$APP_DIR/output/medisign-medgemma4b-adapter}"
export MEDISIGN_LOAD_IN_4BIT="${MEDISIGN_LOAD_IN_4BIT:-1}"

echo "Starting MediSign MedGemma server"
echo "URL:       http://$HOST:$PORT"
echo "Base:      $MEDISIGN_BASE_MODEL"
echo "Adapter:   $MEDISIGN_ADAPTER_PATH"
echo "4-bit:     $MEDISIGN_LOAD_IN_4BIT"

python -m uvicorn scripts.dev.medgemma_openai_server:app --host "$HOST" --port "$PORT"
