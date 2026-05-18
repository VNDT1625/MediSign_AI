# FPT Cloud GPU deploy

This project uses this split:

```text
FPT Cloud GPU VM: MedGemma base model + MediSign LoRA adapter
Local machine: FastAPI backend + RAG + Next.js web
```

## 1. Create FPT GPU VM

Recommended VM:

- Ubuntu 22.04
- NVIDIA GPU with at least 16 GB VRAM
- 32 GB RAM or more
- 80 GB disk or more
- Public IP or public endpoint
- Inbound TCP port `8080` allowed

H100/H200 is more than enough for this adapter.

## 2. Setup on FPT VM

SSH into the VM, then run:

```bash
export HF_TOKEN='hf_your_token_with_medgemma_access'
curl -fsSL https://raw.githubusercontent.com/VNDT1625/MediSign_AI/docs/fix-medgemma-model-name/scripts/cloud/setup-fpt-medgemma.sh -o setup-fpt-medgemma.sh
bash setup-fpt-medgemma.sh
```

If the branch changes, override it:

```bash
REPO_BRANCH=main bash setup-fpt-medgemma.sh
```

## 3. Start AI server on FPT VM

```bash
cd ~/MediSign_AI
. .venv/bin/activate
bash scripts/cloud/start-fpt-medgemma.sh
```

Health check:

```bash
curl http://localhost:8080/health
```

The server preloads the model on startup. If Hugging Face access, CUDA, LoRA
loading, or GPU memory is wrong, it fails immediately in this terminal instead
of failing later from the web app.

From your local Windows machine:

```powershell
curl http://FPT_VM_IP:8080/health
```

If this does not connect, open port `8080` in the FPT firewall/security group.

Run a direct cloud AI smoke test before starting the web app:

```powershell
cd "C:\NDT\PJ\MediSign_AI - Copy"
.\scripts\dev\test-cloud-ai.ps1 http://FPT_VM_IP:8080/v1
```

## 4. Start local backend + web using cloud AI

On Windows:

```powershell
cd "C:\NDT\PJ\MediSign_AI - Copy"
.\scripts\dev\start-all-dev-cloud.ps1 http://FPT_VM_IP:8080/v1
```

Or start backend only:

```powershell
cd "C:\NDT\PJ\MediSign_AI - Copy"
.\scripts\dev\start-backend-rag-cloud.ps1 http://FPT_VM_IP:8080/v1
```

Then open:

```text
http://localhost:3000/app/chat
```

## 5. What should be running

```text
FPT VM:
  http://FPT_VM_IP:8080/health
  http://FPT_VM_IP:8080/v1/chat/completions

Local machine:
  http://localhost:8000/api/v1/ai/status
  http://localhost:3000/app/chat
```
