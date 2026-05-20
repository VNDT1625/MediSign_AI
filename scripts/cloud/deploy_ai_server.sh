#!/usr/bin/env bash
# ╔════════════════════════════════════════════════════════════════════╗
# ║  MediSign AI Server — One-shot Cloud Deploy                       ║
# ║                                                                    ║
# ║  Trên VM cloud (Vast.ai/RunPod/Lambda), chạy 2 lệnh:               ║
# ║                                                                    ║
# ║    export HF_TOKEN='hf_xxx'                                        ║
# ║    curl -sSL https://raw.githubusercontent.com/VNDT1625/\         ║
# ║      MediSign_AI/docs/fix-medgemma-model-name/scripts/cloud/\     ║
# ║      deploy_ai_server.sh -o run.sh && bash run.sh                 ║
# ║                                                                    ║
# ║  Script tự:                                                        ║
# ║   1. Cài deps (torch + transformers + peft + bnb + fastapi)        ║
# ║   2. Download serve_medgemma.py                                    ║
# ║   3. Pre-load model + 2 adapters từ HuggingFace                    ║
# ║   4. Start server tại 0.0.0.0:8080 (foreground)                    ║
# ║   5. In ra URL public để backend local connect                     ║
# ║                                                                    ║
# ║  Yêu cầu GPU: ≥12GB VRAM (RTX 3060 12GB, 4090, A100, ...)         ║
# ║  Cold start: ~3-5 phút download model + 30s warmup                 ║
# ╚════════════════════════════════════════════════════════════════════╝

set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────
APP_DIR="${APP_DIR:-$HOME/medisign-server}"
PORT="${PORT:-8080}"
PYTHON_SCRIPT_URL="${PYTHON_SCRIPT_URL:-https://raw.githubusercontent.com/VNDT1625/MediSign_AI/docs/fix-medgemma-model-name/scripts/serve_medgemma.py}"

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

# ── Pre-flight ──────────────────────────────────────────────────────────
banner "PRE-FLIGHT CHECKS"

[ -z "${HF_TOKEN:-}" ] && fail "HF_TOKEN chưa set. Chạy: export HF_TOKEN='hf_...'"
ok "HF_TOKEN: set (${#HF_TOKEN} chars)"

if ! command -v nvidia-smi &> /dev/null; then
  fail "nvidia-smi không có — cần GPU instance"
fi
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
GPU_VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
ok "GPU: $GPU_NAME ($GPU_VRAM MB)"

if [ "$GPU_VRAM" -lt 10000 ]; then
  warn "VRAM thấp ($GPU_VRAM MB) — có thể OOM với model 4B + 2 adapter"
fi

if ! command -v python3 &> /dev/null; then
  fail "python3 không có"
fi
ok "$(python3 --version)"

mkdir -p "$APP_DIR"
cd "$APP_DIR"

# ── Install deps ────────────────────────────────────────────────────────
banner "STEP 1/3 — Install dependencies"

info "Upgrading pip..."
python3 -m pip install -q --upgrade pip --root-user-action=ignore 2>&1 | tail -2

info "Installing PyTorch + CUDA (lần đầu mất ~2 phút)..."
python3 -m pip install -q --root-user-action=ignore \
  torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu124 2>&1 | tail -3

info "Installing transformers + LoRA stack..."
python3 -m pip install -q --root-user-action=ignore \
  "transformers>=4.50" "peft>=0.13" "bitsandbytes>=0.44" \
  "accelerate>=0.34" "datasets>=3.0" \
  sentencepiece protobuf "huggingface_hub>=0.26" 2>&1 | tail -3

info "Installing FastAPI server stack..."
python3 -m pip install -q --root-user-action=ignore \
  fastapi "uvicorn[standard]" pydantic 2>&1 | tail -3

ok "Dependencies installed"

# ── Download serve script ───────────────────────────────────────────────
banner "STEP 2/3 — Download server script"

info "Pulling: $PYTHON_SCRIPT_URL"
curl -fsSL "$PYTHON_SCRIPT_URL" -o "$APP_DIR/serve_medgemma.py"
[ -s "$APP_DIR/serve_medgemma.py" ] || fail "Download failed"
LINE_COUNT=$(wc -l < "$APP_DIR/serve_medgemma.py")
ok "Downloaded serve_medgemma.py ($LINE_COUNT lines)"

# ── Detect public IP/URL ────────────────────────────────────────────────
banner "STEP 3/3 — Network info"

PUBLIC_IP=$(curl -s --max-time 5 https://api.ipify.org || echo "unknown")
ok "Public IP: $PUBLIC_IP"

# Vast.ai port mapping detection
VAST_TCP_PORT=""
if [ -n "${VAST_TCP_PORT_8080:-}" ]; then
  VAST_TCP_PORT="$VAST_TCP_PORT_8080"
  ok "Vast.ai detected — external port: $VAST_TCP_PORT"
fi

# ── Start server ────────────────────────────────────────────────────────
banner "STARTING MEDGEMMA SERVER"

cat <<INFO

  ┌─────────────────────────────────────────────────────────────┐
  │  Server sẽ start ở 0.0.0.0:$PORT (lần đầu tốn ~3-5 phút     │
  │  để download model ~6GB từ HuggingFace)                     │
  │                                                              │
  │  Khi thấy "Application startup complete" + "Uvicorn         │
  │  running on..." là server SẴN SÀNG.                         │
  │                                                              │
INFO

if [ -n "$VAST_TCP_PORT" ]; then
cat <<URL
  │  Trên máy LOCAL (laptop), set env backend:                  │
  │                                                              │
  │     BACKEND_AI_PROVIDER=openai_compatible                    │
  │     BACKEND_AI_BASE_URL=http://$PUBLIC_IP:$VAST_TCP_PORT/v1
  │     BACKEND_AI_API_KEY=any-string-works                      │
  │                                                              │
URL
else
cat <<URL
  │  Trên máy LOCAL (laptop), set env backend:                  │
  │                                                              │
  │     BACKEND_AI_PROVIDER=openai_compatible                    │
  │     BACKEND_AI_BASE_URL=http://$PUBLIC_IP:$PORT/v1            │
  │     BACKEND_AI_API_KEY=any-string-works                      │
  │                                                              │
  │  ⚠️  Đảm bảo port $PORT đã được expose trên Vast.ai:        │
  │     Edit instance → Open Ports → add $PORT/tcp              │
URL
fi

cat <<INFO
  │                                                              │
  │  Test từ máy local:                                          │
  │     curl http://<URL above>/health                          │
  │                                                              │
  │  Ctrl+C để stop server.                                      │
  └─────────────────────────────────────────────────────────────┘

INFO

cd "$APP_DIR"
exec python3 serve_medgemma.py --host 0.0.0.0 --port "$PORT"
