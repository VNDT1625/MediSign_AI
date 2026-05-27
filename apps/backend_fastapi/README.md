# Backend FastAPI

Phien ban: **0.2.0** (`pyproject.toml`).
Python: 3.11+. ORM SQLAlchemy 2.0 + psycopg3. Auth PyJWT (HS256) + PBKDF2-SHA256 (120k iterations).

## AI Configuration

Backend giu FastAPI nhe va goi model runtime rieng qua endpoint OpenAI-compatible.
Mo hinh chinh la `google/medgemma-1.5-4b-it` voi **2 adapter QLoRA** (Medical + Psychology)
chia chung 1 mo hinh nen, switch theo field `model` trong request.

| Mode | Model runtime | Adapter | Status |
| --- | --- | --- | --- |
| MVP fallback | Rule-based services | None | Works without GPU |
| Medical AI | MedGemma 1.5 4B server | `medisign-medgemma-medical` | Adapter ready (`output/medisign-medgemma4b-adapter/`) |
| Psychology AI | MedGemma 1.5 4B server | `medisign-medgemma-psychology` | Adapter ready (`output/medisign_medgemma4b_psychology/adapter/`) |

Tat ca env var deu co prefix `BACKEND_` (Pydantic Settings):

```bash
BACKEND_AI_PROVIDER=openai_compatible
BACKEND_AI_BASE_URL=http://localhost:8080/v1
BACKEND_AI_API_KEY=
BACKEND_AI_MODEL=google/medgemma-1.5-4b-it
BACKEND_AI_MEDICAL_MODEL=medisign-medgemma-medical
BACKEND_AI_PSYCHOLOGY_MODEL=medisign-medgemma-psychology
BACKEND_MEDGEMMA_BASE_MODEL=google/medgemma-1.5-4b-it
BACKEND_MEDGEMMA_MEDICAL_ADAPTER_PATH=../../output/medisign-medgemma4b-adapter
BACKEND_MEDGEMMA_PSYCHOLOGY_ADAPTER_PATH=../../output/medisign_medgemma4b_psychology/adapter
```

For FPT Cloud GPU, keep backend va web on your local machine va point the
backend to the cloud model endpoint:

```powershell
scripts\dev\start-backend-rag-cloud.ps1 http://FPT_VM_IP:8080/v1
```

To start local backend va web together with the cloud AI server:

```powershell
scripts\dev\start-all-dev-cloud.ps1 http://FPT_VM_IP:8080/v1
```

The cloud script checks `http://FPT_VM_IP:8080/health` truoc khi start backend cuc bo.

Neu khong cau hinh model runtime, service van chay bang rule-based / RAG-grounded
fallback (`BACKEND_AI_PROVIDER=rule_based`).

## Install

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install --upgrade pip
pip install -e .[dev]
```

## Run

Run the real MedGemma adapter server first. This requires an NVIDIA GPU/CUDA
va Hugging Face access to `google/medgemma-1.5-4b-it`:

```powershell
huggingface-cli login
huggingface-cli download thuaannn/medisign-medgemma4b-adapter `
  --local-dir output/medisign-medgemma4b-adapter
huggingface-cli download thuaannn/medisign-medgemma4b-psychology `
  --local-dir output/medisign_medgemma4b_psychology/adapter
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
- Medical adapter: `output/medisign-medgemma4b-adapter` (preload khi start)
- Psychology adapter: `output/medisign_medgemma4b_psychology/adapter` (lazy load)
- Endpoint: `http://localhost:8080/v1/chat/completions`

Reference implementation cua server day du:
`scripts/serve_medgemma.py` va `scripts/dev/medgemma_openai_server.py`.

## Core endpoints

API prefix: `/api/v1` (cau hinh trong `BACKEND_API_PREFIX`).

Health & Auth:
- `GET /api/v1/health`
- `POST /api/v1/auth/register | /login | /refresh | /logout | /change-password`
- `POST /api/v1/auth/forgot-password | /reset-password`
- `GET  /api/v1/auth/me`

Tu van va thuoc:
- `POST /api/v1/consult/triage` (public) + `GET /history` + `DELETE /{id}`
- `POST /api/v1/medicine/scan` (text) + `POST /medicine/scan-image` (multimodal)
- `GET/POST/PATCH/DELETE /api/v1/medicine/cabinet[/{id}]`
- `POST /api/v1/medicine/cabinet/{id}/dose`
- `GET  /api/v1/medicine/cabinet/today | /upcoming | /{id}/history`

AI chat va RAG:
- `POST /api/v1/ai/chat` (JSON hoac multipart/form-data, ho tro `conversation_id` cho multi-turn)
- `GET  /api/v1/ai/status`
- `GET  /api/v1/ai/rag/status`
- `POST /api/v1/ai/rag/search | /rag/rebuild`
- `GET  /api/v1/ai/conversations[/{id}]` + `DELETE /{id}`
- `POST /api/v1/ai/conversations/{id}/feedback`
- `GET  /api/v1/ai/summary` (Quick Summary widget)

Profile va journal:
- `GET/PUT/PATCH/DELETE /api/v1/profile`
- `GET/POST /api/v1/journal` + `GET/PATCH/DELETE /journal/{id}`

Drug lookup (`/api/drug/`, khong qua `/v1`):
- `GET /api/drug/` (health) + `/list | /search/{name} | /suggestions/{kw} | /random/{count}`
- `POST /api/drug/search`

Admin (`/api/v1/admin/`, `account_type=admin`):
- Users / medicines / hospitals CRUD
- Posts moderation (community)
- Workouts / goals listing
- KB pending records (review + approve/reject + promote)
- Weight update proposals (feedback loop)
- Stats: `/admin/stats[/users|/posts|/workouts]`

## RAG after training

Run or refresh the generated knowledge base first:

```bash
python ../../scripts/build_demo_knowledge_base.py
```

The backend loads `data/knowledge_base/knowledge_base.json` (128,380 records),
builds a local BM25-style medical search index, va tu dong inject retrieved
context vao `/api/v1/ai/chat` khi `use_rag=true` (default). This works with
the trained MedGemma runtime va also returns grounded fallback answers while
the runtime is offline.

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
