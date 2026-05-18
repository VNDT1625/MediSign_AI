#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/VNDT1625/MediSign_AI.git}"
REPO_BRANCH="${REPO_BRANCH:-docs/fix-medgemma-model-name}"
APP_DIR="${APP_DIR:-$HOME/MediSign_AI}"
ADAPTER_REPO="${ADAPTER_REPO:-https://huggingface.co/thuaannn/medisign-medgemma4b-adapter}"

echo "== MediSign FPT Cloud MedGemma setup =="
echo "Repo:    $REPO_URL"
echo "Branch:  $REPO_BRANCH"
echo "App dir: $APP_DIR"

sudo apt-get update
sudo apt-get install -y git git-lfs python3 python3-venv python3-pip

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
python -m pip install -r scripts/requirements_train.txt
python -m pip install -e apps/backend_fastapi

mkdir -p output
if [ ! -d output/medisign-medgemma4b-adapter/.git ]; then
  git clone "$ADAPTER_REPO" output/medisign-medgemma4b-adapter
else
  git -C output/medisign-medgemma4b-adapter pull --ff-only
fi

python -m py_compile scripts/dev/medgemma_openai_server.py

echo
echo "Setup done."
echo "Start server:"
echo "  cd $APP_DIR"
echo "  . .venv/bin/activate"
echo "  bash scripts/cloud/start-fpt-medgemma.sh"
