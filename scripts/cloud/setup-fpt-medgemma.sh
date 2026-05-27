#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/VNDT1625/MediSign_AI.git}"
REPO_BRANCH="${REPO_BRANCH:-docs/fix-medgemma-model-name}"
APP_DIR="${APP_DIR:-$HOME/MediSign_AI}"
ADAPTER_REPO="${ADAPTER_REPO:-thuaannn/medisign-medgemma4b-adapter}"
PSYCHOLOGY_ADAPTER_REPO="${PSYCHOLOGY_ADAPTER_REPO:-thuaannn/medisign-medgemma4b-psychology}"
if [ -z "${HF_TOKEN:-}" ] && [ -n "${HUGGING_FACE_HUB_TOKEN:-}" ]; then
  export HF_TOKEN="$HUGGING_FACE_HUB_TOKEN"
fi
SUDO=""
if command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
fi

echo "== MediSign FPT Cloud MedGemma setup =="
echo "Repo:    $REPO_URL"
echo "Branch:  $REPO_BRANCH"
echo "App dir: $APP_DIR"

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "ERROR: nvidia-smi not found. This VM does not look like a GPU VM."
  exit 2
fi
nvidia-smi

if [ -z "${HF_TOKEN:-}" ] && [ ! -f "$HOME/.cache/huggingface/token" ]; then
  echo "ERROR: HF_TOKEN is missing and no Hugging Face cached token was found."
  echo "Run this first, then rerun setup:"
  echo "  export HF_TOKEN='hf_your_token_with_medgemma_access'"
  exit 2
fi

$SUDO apt-get update
$SUDO apt-get install -y git git-lfs python3 python3-venv python3-pip

git lfs install

if [ ! -d "$APP_DIR/.git" ]; then
  git clone -b "$REPO_BRANCH" "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" fetch origin "$REPO_BRANCH"
  git -C "$APP_DIR" checkout "$REPO_BRANCH"
  git -C "$APP_DIR" pull --ff-only origin "$REPO_BRANCH"
fi

cd "$APP_DIR"

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip uninstall -y torch torchvision torchaudio >/dev/null 2>&1 || true
python -m pip install --index-url https://download.pytorch.org/whl/cu124 torch
python -m pip install -r scripts/requirements_medgemma_server.txt

python - <<'PY'
import os
import sys

import torch
from huggingface_hub import login, model_info

try:
    from huggingface_hub import get_token
except ImportError:
    from huggingface_hub import HfFolder
    get_token = HfFolder.get_token

token = os.environ.get("HF_TOKEN") or get_token()
if not token:
    sys.exit("HF token not found after dependency install.")

login(token=token, add_to_git_credential=False)
print("CUDA available:", torch.cuda.is_available())
print("GPU count:", torch.cuda.device_count())
if not torch.cuda.is_available():
    sys.exit("CUDA is not available inside Python.")

info = model_info("google/medgemma-1.5-4b-it", token=token)
print("Hugging Face model access OK:", info.modelId)
PY

mkdir -p output

# Pull medical adapter
echo "Pulling medical adapter ..."
huggingface-cli download "$ADAPTER_REPO" \
  --local-dir output/medisign-medgemma4b-adapter

# Pull psychology adapter (optional — bỏ qua nếu repo chưa tồn tại)
echo "Pulling psychology adapter ..."
huggingface-cli download "$PSYCHOLOGY_ADAPTER_REPO" \
  --local-dir output/medisign_medgemma4b_psychology/adapter \
  || echo "  WARN: psychology adapter repo not accessible, skipping"

python -m py_compile scripts/dev/medgemma_openai_server.py
test -f output/medisign-medgemma4b-adapter/adapter_config.json
test -f output/medisign-medgemma4b-adapter/adapter_model.safetensors

echo
echo "Setup done."
echo "Start server:"
echo "  cd $APP_DIR"
echo "  . .venv/bin/activate"
echo "  bash scripts/cloud/start-fpt-medgemma.sh"
