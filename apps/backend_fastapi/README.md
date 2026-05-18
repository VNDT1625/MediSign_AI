# Backend FastAPI

## AI Configuration

Backend hien tai giu FastAPI nhe va goi model runtime rieng qua endpoint OpenAI-compatible. Model train chinh cua du an la `google/medgemma-1.5-4b-it` voi QLoRA medical adapter.

| Mode | Model runtime | Adapter | Status |
| --- | --- | --- | --- |
| MVP fallback | Rule-based services | None | Works without GPU |
| Medical AI | MedGemma 1.5 4B server | Medical LoRA | Adapter downloaded and wired |
| Psychology AI | MedGemma-compatible server | Psychology/Personal LoRA | Planned |

Set these in `.env`:

```bash
AI_PROVIDER=openai_compatible
AI_BASE_URL=http://localhost:8080/v1
AI_API_KEY=
AI_MODEL=google/medgemma-1.5-4b-it
AI_MEDICAL_MODEL=medisign-medgemma-medical
AI_PSYCHOLOGY_MODEL=medisign-medgemma4b-psychology
```

Neu khong cau hinh model runtime, service van chay bang rule-based/mock fallback.

## Install

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install --upgrade pip
pip install -e .[dev]
```

## Run

Run the real MedGemma adapter server first. This requires an NVIDIA GPU/CUDA
and Hugging Face access to `google/medgemma-1.5-4b-it`:

```powershell
git lfs install
git clone https://huggingface.co/thuaannn/medisign-medgemma4b-adapter output\medisign-medgemma4b-adapter
```

```powershell
scripts\dev\start-medgemma-server.ps1
```

Then run the backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

For local web + backend + real model together:

```powershell
scripts\dev\start-all-dev.ps1
```

The model server uses:

- Base model: `google/medgemma-1.5-4b-it`
- Adapter: `output/medisign-medgemma4b-adapter`
- Endpoint: `http://localhost:8080/v1/chat/completions`

## Core endpoints

- `GET /api/v1/health`
- `POST /api/v1/consult/triage`
- `POST /api/v1/medicine/scan`
- `POST /api/v1/ai/chat`
- `GET /api/v1/ai/status`
- `GET /api/v1/ai/rag/status`
- `POST /api/v1/ai/rag/search`
- `POST /api/v1/ai/rag/rebuild`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

## RAG after training

Run or refresh the generated knowledge base first:

```bash
python ../../scripts/build_demo_knowledge_base.py
```

The backend loads `data/knowledge_base/knowledge_base.json`, builds a local
BM25-style medical search index, and automatically injects retrieved context
into `/api/v1/ai/chat` when `use_rag=true` (default). This works with the
trained MedGemma runtime and also returns grounded fallback answers while the
runtime is offline.

## Demo auth account

- Email: `demo@medisign.ai`
- Password: `ChangeMe123`

## Test / Lint / Contract

```bash
python -m pytest
ruff check .
black --check .
python -c "from pathlib import Path; import yaml; from openapi_spec_validator import validate_spec; spec=yaml.safe_load(Path('../../packages/shared_contracts/openapi/medisign-api.openapi.yaml').read_text()); validate_spec(spec)"
```
