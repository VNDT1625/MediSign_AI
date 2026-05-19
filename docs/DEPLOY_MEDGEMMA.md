# Deploy MedGemma 4B Inference Server

Hướng dẫn deploy MedGemma 4B + 2 LoRA adapters (medical + psychology) cho backend MediSign FastAPI.

## Tổng quan

```
┌──────────────────┐     OpenAI-compatible      ┌──────────────────┐
│  FastAPI Backend │ ───────────────────────►  │ MedGemma Server  │
│  (CPU, port 8000)│   /v1/chat/completions    │ (GPU, port 8080) │
└──────────────────┘                            └──────────────────┘
                                                  base: medgemma-1.5-4b
                                                  + LoRA medical
                                                  + LoRA psychology
```

Backend là client mỏng — không cần GPU. MedGemma server chạy riêng (cùng máy GPU local hoặc cloud), backend gọi qua HTTP.

## Adapters đã train

- `thuaannn/medisign-medgemma4b-adapter` — Medical (15.7K records, 3 epochs)
- `thuaannn/medisign-medgemma4b-psychology` — Psychology OARS (1.2K records, 4 epochs, merged on top of medical)

## Cài đặt

### 1. Cài deps trên GPU machine

```bash
pip install fastapi uvicorn transformers peft bitsandbytes accelerate \
            pydantic torch huggingface_hub sentencepiece protobuf
```

### 2. Set HuggingFace token

```bash
export HF_TOKEN='hf_xxxxx'
```

### 3. Chạy server

```bash
python scripts/serve_medgemma.py --port 8080 --host 0.0.0.0
```

Lần đầu chạy mất 1-3 phút để download model + adapters (~9GB total). Lần sau cache local.

## Yêu cầu GPU

| GPU | VRAM | Mode | OK? |
|---|---|---|---|
| RTX 3060 12GB | 12GB | 4-bit | ✅ vừa đủ |
| RTX 3090/4090 | 24GB | 4-bit | ✅ thoải mái |
| RTX 4060 8GB | 8GB | 4-bit | ❌ không đủ |
| A100 40GB | 40GB | bf16 (LOAD_4BIT=0) | ✅ tốc độ tối đa |
| H100 80GB | 80GB | bf16 | ✅ overkill |

4-bit (default) chiếm ~4GB VRAM cho base + ~30MB cho 2 adapter. Có dư room cho KV cache khi serve nhiều request.

## Test server

### Health check
```bash
curl http://localhost:8080/health
```

### List models
```bash
curl http://localhost:8080/v1/models
```

### Chat — Medical
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "medisign-medgemma-medical",
    "messages": [
      {"role": "user", "content": "Triệu chứng tiểu đường type 2 là gì?"}
    ],
    "max_tokens": 256
  }'
```

### Chat — Psychology (OARS)
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "medisign-medgemma-psychology",
    "messages": [
      {"role": "user", "content": "Em bị áp lực thi cử, mất ngủ mấy hôm nay."}
    ],
    "max_tokens": 256
  }'
```

## Cấu hình Backend FastAPI

Trong `apps/backend_fastapi/.env`:

```env
BACKEND_AI_PROVIDER=openai_compatible
BACKEND_AI_BASE_URL=http://localhost:8080/v1
BACKEND_AI_API_KEY=any-string-works
BACKEND_AI_MODEL=google/medgemma-1.5-4b-it
BACKEND_AI_MEDICAL_MODEL=medisign-medgemma-medical
BACKEND_AI_PSYCHOLOGY_MODEL=medisign-medgemma-psychology
BACKEND_AI_REQUEST_TIMEOUT_SECONDS=60
```

Restart backend, gọi `/api/ai/status` để verify:
```bash
curl http://localhost:8000/api/ai/status
```

Phải thấy `"ready": true` và `"provider": "openai_compatible"`.

## Triển khai production

### Option A — Cùng máy GPU local
```bash
# Window 1: MedGemma server
HF_TOKEN=hf_xxx python scripts/serve_medgemma.py

# Window 2: Backend
cd apps/backend_fastapi && uvicorn app.main:app --port 8000
```

### Option B — Cloud GPU (Vast.ai/RunPod) + backend trên CPU server
1. Rent GPU instance (RTX 3090 ~$0.20/hr là đủ)
2. Expose port 8080 với SSH tunnel hoặc public IP
3. Trên backend server, set `BACKEND_AI_BASE_URL` trỏ tới GPU instance

```bash
# Trên GPU instance
HF_TOKEN=hf_xxx python scripts/serve_medgemma.py --host 0.0.0.0 --port 8080

# Trên backend server (laptop hoặc VPS)
export BACKEND_AI_BASE_URL=http://<gpu-instance-ip>:8080/v1
uvicorn app.main:app
```

### Option C — Docker
Tạo `Dockerfile.medgemma`:
```dockerfile
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install fastapi uvicorn transformers peft bitsandbytes accelerate \
                pydantic torch huggingface_hub sentencepiece protobuf
COPY scripts/serve_medgemma.py /app/serve_medgemma.py
WORKDIR /app
EXPOSE 8080
CMD ["python3", "serve_medgemma.py", "--host", "0.0.0.0", "--port", "8080"]
```

## Performance

- **Cold start** (first request after server boots): 5-8s (warmup CUDA kernels)
- **Subsequent requests** (4-bit mode, RTX 4090):
  - 256 tokens: ~3-5s
  - 512 tokens: ~6-10s
- **Concurrent requests**: handled sequentially (single GPU + global lock). Để serve nhiều user song song, deploy nhiều instance + load balancer.

## Switch adapter

Backend tự switch adapter dựa vào field `model` trong request:
- `model: "medisign-medgemma-medical"` → activate medical LoRA
- `model: "medisign-medgemma-psychology"` → activate psychology LoRA

Switch chỉ đổi pointer, không reload weights → ~50ms overhead.

## Troubleshooting

### "Model not loaded yet" (HTTP 503)
Server đang trong quá trình load model. Đợi 1-3 phút rồi retry.

### CUDA OOM
Giảm số concurrent request hoặc thêm `LOAD_4BIT=1` (default).

### "401 Unauthorized" khi pull model
Token `HF_TOKEN` chưa có quyền read repos `thuaannn/*`. Verify:
```bash
python -c "from huggingface_hub import whoami; print(whoami(token='$HF_TOKEN'))"
```
Hoặc đảm bảo repos `thuaannn/medisign-medgemma4b-*` là public.

### Tốc độ chậm
- Tắt 4-bit (`LOAD_4BIT=0`) nếu có VRAM dư → tăng tốc 1.5-2×
- Giảm `max_tokens` trong request
- Dùng GPU mạnh hơn (4090 → A100 → H100)
