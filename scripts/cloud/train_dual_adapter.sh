#!/usr/bin/env bash
# Train Dual Adapter trên FPT Cloud VM (H100)
#
# Usage:
#   export HF_TOKEN='hf_YOUR_WRITE_TOKEN'
#   bash scripts/cloud/train_dual_adapter.sh medical
#   bash scripts/cloud/train_dual_adapter.sh psychology
#   bash scripts/cloud/train_dual_adapter.sh both
#
# Yêu cầu: GPU VM, đã chạy setup-fpt-medgemma.sh trước đó

set -euo pipefail

ADAPTER_TYPE="${1:-both}"
APP_DIR="${APP_DIR:-$HOME/MediSign_AI}"
DATA_REPO_ID="${DATA_REPO_ID:-thuaannn/medisign-training-data}"

if [ -z "${HF_TOKEN:-}" ] && [ -n "${HUGGING_FACE_HUB_TOKEN:-}" ]; then
  export HF_TOKEN="$HUGGING_FACE_HUB_TOKEN"
fi
if [ -z "${HF_TOKEN:-}" ]; then
  echo "ERROR: HF_TOKEN chưa được set. Chạy:"
  echo "  export HF_TOKEN='hf_your_write_token'"
  exit 1
fi

cd "$APP_DIR"
. .venv/bin/activate

# ─── Cài training dependencies ─────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════"
echo "  Installing training dependencies ..."
echo "═══════════════════════════════════════════════════════════"
pip install -q --upgrade pip
pip install -q "transformers>=4.50" "peft>=0.13" "bitsandbytes>=0.44" "accelerate>=0.34" "trl>=0.12" "datasets>=3.0"
pip install -q sentencepiece protobuf huggingface_hub tensorboard

# Flash-Attention 2 nếu GPU hỗ trợ
python -c "
import torch
if torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 8:
    print('GPU hỗ trợ Flash-Attention 2')
    exit(0)
else:
    print('GPU không hỗ trợ Flash-Attention 2')
    exit(1)
" && pip install -q flash-attn --no-build-isolation || echo "  Skip flash-attn"

# Login HF
huggingface-cli login --token "$HF_TOKEN" --add-to-git-credential

# ─── Pull dataset từ HF ────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Pulling dataset from $DATA_REPO_ID ..."
echo "═══════════════════════════════════════════════════════════"
mkdir -p data/training_clean/medgemma_4b
huggingface-cli download "$DATA_REPO_ID" \
  --repo-type dataset \
  --local-dir data/training_clean/medgemma_4b \
  --include "medical_*.jsonl" "psychology_*.jsonl"

# ─── Train function ────────────────────────────────────────────────────
train_adapter() {
  local kind=$1   # medical | psychology
  local repo_id=$2

  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo "  Training $kind adapter"
  echo "═══════════════════════════════════════════════════════════"

  python scripts/train_qlora_medgemma.py \
    --model_id google/medgemma-1.5-4b-it \
    --train_file "data/training_clean/medgemma_4b/${kind}_train.jsonl" \
    --eval_file  "data/training_clean/medgemma_4b/${kind}_eval.jsonl" \
    --num_epochs 3 \
    --output_dir "output/medisign_medgemma4b_${kind}/checkpoints" \
    --adapter_dir "output/medisign_medgemma4b_${kind}/adapter"

  echo ""
  echo "  Pushing adapter to https://huggingface.co/$repo_id ..."

  python -c "
from huggingface_hub import HfApi, upload_folder
api = HfApi(token='$HF_TOKEN')
try:
    api.create_repo(repo_id='$repo_id', exist_ok=True, private=False)
except Exception as e:
    print(f'Note: {e}')
upload_folder(
    folder_path='output/medisign_medgemma4b_${kind}/adapter',
    repo_id='$repo_id',
    commit_message='${kind} adapter trained on VM',
    token='$HF_TOKEN',
)
print('✅ Pushed successfully')
"
}

# ─── Run training ──────────────────────────────────────────────────────
case "$ADAPTER_TYPE" in
  medical)
    train_adapter medical thuaannn/medisign-medgemma4b-adapter
    ;;
  psychology)
    train_adapter psychology thuaannn/medisign-medgemma4b-psychology
    ;;
  both)
    train_adapter medical thuaannn/medisign-medgemma4b-adapter
    train_adapter psychology thuaannn/medisign-medgemma4b-psychology
    ;;
  *)
    echo "Usage: $0 {medical|psychology|both}"
    exit 1
    ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ DONE"
echo "═══════════════════════════════════════════════════════════"
echo "Adapter đã push lên HuggingFace."
echo "Bước tiếp: start runtime server với cả 2 adapter:"
echo "  bash scripts/cloud/start-fpt-medgemma.sh"
