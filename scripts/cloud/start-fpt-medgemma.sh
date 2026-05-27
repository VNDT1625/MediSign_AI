#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/MediSign_AI}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8080}"
if [ -z "${HF_TOKEN:-}" ] && [ -n "${HUGGING_FACE_HUB_TOKEN:-}" ]; then
  export HF_TOKEN="$HUGGING_FACE_HUB_TOKEN"
fi

cd "$APP_DIR"
. .venv/bin/activate

export MEDISIGN_BASE_MODEL="${MEDISIGN_BASE_MODEL:-google/medgemma-1.5-4b-it}"
export MEDISIGN_ADAPTER_PATH="${MEDISIGN_ADAPTER_PATH:-$APP_DIR/output/medisign-medgemma4b-adapter}"
export MEDISIGN_PSYCHOLOGY_ADAPTER_PATH="${MEDISIGN_PSYCHOLOGY_ADAPTER_PATH:-$APP_DIR/output/medisign_medgemma4b_psychology/adapter}"
export MEDISIGN_LOAD_IN_4BIT="${MEDISIGN_LOAD_IN_4BIT:-1}"
export MEDISIGN_PRELOAD_ON_START="${MEDISIGN_PRELOAD_ON_START:-1}"

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "ERROR: nvidia-smi not found. Start this on a GPU VM."
  exit 2
fi
nvidia-smi

if [ ! -f "$MEDISIGN_ADAPTER_PATH/adapter_config.json" ]; then
  echo "ERROR: adapter_config.json not found under $MEDISIGN_ADAPTER_PATH"
  exit 2
fi

echo "Starting MediSign MedGemma server"
echo "URL:       http://$HOST:$PORT"
echo "Base:      $MEDISIGN_BASE_MODEL"
echo "Adapter:   $MEDISIGN_ADAPTER_PATH"
echo "4-bit:     $MEDISIGN_LOAD_IN_4BIT"
echo "Preload:   $MEDISIGN_PRELOAD_ON_START"

python -m uvicorn scripts.dev.medgemma_openai_server:app --host "$HOST" --port "$PORT"
