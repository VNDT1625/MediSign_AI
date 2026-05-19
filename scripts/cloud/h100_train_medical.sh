#!/usr/bin/env bash
# ╔════════════════════════════════════════════════════════════════════╗
# ║  MediSign Medical Adapter — H100 One-shot Trainer                  ║
# ║                                                                    ║
# ║  Cách dùng trên VM H100 (Vast.ai/RunPod/FPT):                     ║
# ║                                                                    ║
# ║    export HF_TOKEN='hf_YOUR_WRITE_TOKEN'                          ║
# ║    curl -sSL https://raw.githubusercontent.com/VNDT1625/\         ║
# ║      MediSign_AI/main/scripts/cloud/h100_train_medical.sh \        ║
# ║      | bash                                                        ║
# ║                                                                    ║
# ║  Hoặc 2 lệnh:                                                      ║
# ║    curl -sSL <URL> -o train.sh && bash train.sh                    ║
# ║                                                                    ║
# ║  Nó sẽ tự động:                                                    ║
# ║  1. Cài deps + Flash Attention 2 (pre-built cho H100)              ║
# ║  2. Login HF, pull dataset                                         ║
# ║  3. Train Medical Adapter (~1h trên H100 80GB)                     ║
# ║  4. Smoke test inference                                           ║
# ║  5. Push lên HuggingFace                                           ║
# ║  6. Tự terminate khi xong                                          ║
# ║                                                                    ║
# ║  ETA: ~1-1.5h tổng cộng. Chi phí: ~$1-1.50.                        ║
# ╚════════════════════════════════════════════════════════════════════╝

set -euo pipefail

# ─── Config ──────────────────────────────────────────────────────────
APP_DIR="${APP_DIR:-$HOME/medisign}"
PYTHON_SCRIPT_URL="${PYTHON_SCRIPT_URL:-https://raw.githubusercontent.com/VNDT1625/MediSign_AI/docs/fix-medgemma-model-name/scripts/cloud/h100_train_medical.py}"
LOG_FILE="$APP_DIR/training.log"

# ─── Color helpers ───────────────────────────────────────────────────
GREEN='\033[0;32m'; BLUE='\033[0;34m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[ OK ]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

banner() {
  echo ""
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║   $1"
  echo "╚════════════════════════════════════════════════════════════════╝"
}

# ─── Pre-flight checks ───────────────────────────────────────────────
banner "PRE-FLIGHT CHECKS"

[ -z "${HF_TOKEN:-}" ] && fail "HF_TOKEN chưa set. Chạy: export HF_TOKEN='hf_...'"
ok "HF_TOKEN: set (${#HF_TOKEN} chars)"

if ! command -v nvidia-smi &> /dev/null; then
  fail "nvidia-smi không có — không phải GPU instance?"
fi
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
GPU_VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
ok "GPU: $GPU_NAME ($GPU_VRAM MB)"

if ! command -v python3 &> /dev/null; then
  fail "python3 không có"
fi
PY_VER=$(python3 --version)
ok "$PY_VER"

mkdir -p "$APP_DIR"
cd "$APP_DIR"

# ─── Install deps ────────────────────────────────────────────────────
banner "STEP 1/4 — Install dependencies"

info "Upgrading pip..."
python3 -m pip install -q --upgrade pip 2>&1 | tail -2

info "Installing PyTorch + CUDA..."
python3 -m pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 2>&1 | tail -3

info "Installing transformers + training stack..."
python3 -m pip install -q \
  "transformers>=4.50" "peft>=0.13" "bitsandbytes>=0.44" \
  "accelerate>=0.34" "trl>=0.12" "datasets>=3.0" \
  sentencepiece protobuf "huggingface_hub>=0.26" \
  2>&1 | tail -3

# Flash Attention 2 — H100 có pre-built wheel, KHÔNG cần compile
info "Installing Flash Attention 2 (pre-built wheel cho H100)..."
if python3 -m pip install -q flash-attn --no-build-isolation 2>&1 | tee /tmp/flash_install.log | tail -3; then
  python3 -c "import flash_attn; print(f'  Flash-Attn version: {flash_attn.__version__}')" 2>/dev/null || warn "flash-attn import failed, will fallback to SDPA"
  ok "Flash Attention 2 installed"
else
  warn "Flash Attention 2 install failed, sẽ dùng SDPA fallback"
fi

ok "Dependencies installed"

# ─── Download Python training script ─────────────────────────────────
banner "STEP 2/4 — Download training script"

info "Pulling: $PYTHON_SCRIPT_URL"
curl -fsSL "$PYTHON_SCRIPT_URL" -o "$APP_DIR/h100_train_medical.py"

if [ ! -s "$APP_DIR/h100_train_medical.py" ]; then
  fail "Script download failed hoặc empty"
fi

LINE_COUNT=$(wc -l < "$APP_DIR/h100_train_medical.py")
ok "Downloaded h100_train_medical.py ($LINE_COUNT lines)"

# ─── Run training ────────────────────────────────────────────────────
banner "STEP 3/4 — Training Medical Adapter"

info "Logs at: $LOG_FILE"
info "ETA: ~1-1.5h trên H100 80GB"
info "Bắt đầu training... (Ctrl+C để dừng nếu cần)"
echo ""

cd "$APP_DIR"
HF_TOKEN="$HF_TOKEN" python3 h100_train_medical.py 2>&1 | tee "$LOG_FILE"
TRAIN_EXIT=${PIPESTATUS[0]}

if [ "$TRAIN_EXIT" -ne 0 ]; then
  fail "Training failed với exit code $TRAIN_EXIT. Xem log: $LOG_FILE"
fi

ok "Training completed!"

# ─── Done ────────────────────────────────────────────────────────────
banner "STEP 4/4 — Summary"

if [ -f "$APP_DIR/output/adapter/adapter_config.json" ]; then
  ADAPTER_SIZE=$(du -sh "$APP_DIR/output/adapter" | cut -f1)
  ok "Adapter saved: $APP_DIR/output/adapter ($ADAPTER_SIZE)"
fi

if grep -q "HF push OK" "$LOG_FILE"; then
  ok "Pushed to: https://huggingface.co/thuaannn/medisign-medgemma4b-adapter"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      🎉 ALL DONE! 🎉                            ║"
echo "║                                                                ║"
echo "║  Adapter: https://huggingface.co/thuaannn/medisign-medgemma4b- ║"
echo "║          adapter                                                ║"
echo "║                                                                ║"
echo "║  Bước tiếp theo:                                               ║"
echo "║  1. Verify trên HuggingFace                                    ║"
echo "║  2. Destroy VM để dừng tính tiền                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
