# Backend FastAPI

## AI Triage Configuration

**IMPORTANT**: Xem `packages/ai_training/README.md` để hiểu đầy đủ về 3 deployment modes.

### Tóm tắt:

| Mode | Model | Adapter | Cần train? |
|------|-------|---------|------------|
| Cloud | Qwen 2.5 72B | Medical LoRA | ✅ Yes |
| Local | Gemma 2B | Medical + Personal LoRA | ✅ Yes |
| Hybrid | Qwen + Gemma | Cả hai | ✅ Yes |

### Current MVP Implementation:

Set these in `.env`:
```bash
AI_PROVIDER=gemini          # "gemini", "qwen", hoặc "local"
AI_API_KEY=                 # Để trống nếu chỉ dùng rule-based
AI_MODEL=gemini-2.0-flash
```

Service vẫn work hoàn toàn chỉ với rule-based (không cần AI).

## Install

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install --upgrade pip
pip install -e .[dev]
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Core endpoints

- `GET /api/v1/health`
- `POST /api/v1/consult/triage`
- `POST /api/v1/medicine/scan`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

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
