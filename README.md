# MediSign AI - Du an y te thong minh

MediSign AI la ung dung y te thong minh ho tro:

- Goi y trieu chung va muc do can chu y
- Tra cuu thong tin thuoc
- Quan ly tu thuoc ca nhan
- Tu van suc khoe bang tieng Viet

> Luu y: AI chi dua ra goi y so bo, khong thay the chan doan hoac chi dinh cua bac si.

## Model AI

### MedGemma 4B

Model train hien tai: `google/medgemma-4b-it`

Du an khong train lai full model. Pipeline hien tai train **QLoRA medical adapter** cho MediSign AI.

| Thanh phan | Gia tri |
| --- | --- |
| Base model | `google/medgemma-4b-it` |
| Phuong phap | QLoRA |
| Train file | `data/training_clean/medgemma_4b/train.jsonl` |
| Eval file | `data/training_clean/medgemma_4b/eval.jsonl` |
| Adapter output | `output/medisign_medgemma4b/adapter/` |

Tai lieu train chi tiet: `docs/training/QLORA_TRAINING.md`.

## Luong xu ly thuoc

```
1. User nhap text hoac gui anh thuoc
2. OCR / vision runtime trich xuat ten thuoc
3. Backend tim trong drug database
4. Tra thong tin thuoc va canh bao phu hop
```

Module hien tai uu tien lookup database. Neu can nhan dien thuoc truc tiep tu anh bang vision classifier, can bo sung dataset anh thuoc that.

## Drug Database

Backend uu tien cac file database lon neu ton tai, fallback ve file nho cu.

Duong dan uu tien trong `apps/backend_fastapi/app/services/drug_lookup_service.py`:

1. `data/training_clean/drug_database_dav_detailed_10k.json`
2. `data/training_clean/drug_database_10k_full.json`
3. `data/training_clean/drug_database_10k.json`
4. `data/training_clean/drug_database_expanded.json`
5. `data/training_clean/drug_database.json`

File tot nhat hien co:

- `drug_database_dav_detailed_10k.json`
- 22,585 records
- 15,884 ten thuoc unique
- 22,237 records co so dang ky
- 10,574 records co hoat chat

## Training Data

### MedGemma 4B

```
data/training_clean/medgemma_4b/
├── merged_dataset.json  (17,196 records sau dedup)
├── train.jsonl          (15,476 records)
├── eval.jsonl           (1,720 records)
├── merge_stats.json
└── format_stats.json
```

Format JSONL:

```json
{
  "text": "<start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\n...<end_of_turn>",
  "instruction": "Bạn là MediSign AI...",
  "input": "Câu hỏi của người dùng",
  "output": "Câu trả lời y tế có disclaimer",
  "source": "all_medical"
}
```

Nguon du lieu chinh trong corpus MedGemma:

- `all_medical`: 12,391
- `medquad`: 1,362
- `drug_db`: 968
- `medical_dialogue_2010`: 800
- `vn_drugs_commercial`: 576
- Cac nguon synthetic / VN symptoms / drug medicine khac

## API Endpoints

### Drug Lookup

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/drug/` | Health check |
| GET | `/api/drug/list` | List all drugs |
| POST | `/api/drug/search` | Search drug by name |
| GET | `/api/drug/search/{name}` | Search drug |
| GET | `/api/drug/suggestions/{keyword}` | Get suggestions |
| GET | `/api/drug/random/{count}` | Random drugs |

### Core Backend

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/consult/triage` | Rule-based/AI triage |
| POST | `/api/v1/medicine/scan` | Medicine scan |
| POST | `/api/v1/ai/chat` | OpenAI-compatible model runtime client |

## Quick Start

### Backend

```bash
cd apps/backend_fastapi
uvicorn app.main:app --reload
```

### Train MedGemma Adapter

```bash
pip install -r scripts/requirements_train.txt
huggingface-cli login
python scripts/train_qlora_medgemma_smoke_test.py
python scripts/train_qlora_medgemma.py
```

## Structure

- `apps/mobile_flutter`: Flutter client
- `apps/web_next`: Next.js web client
- `apps/backend_fastapi`: FastAPI backend
- `packages/shared_contracts`: OpenAPI + JSON Schema contracts
- `data/training_clean`: Cleaned training data and drug database
- `docs/training`: Training documentation

## Disclaimer

- AI chi dua ra goi y, khong thay the chan doan cua bac si.
- Luon tham khao bac si/duoc si truoc khi dung thuoc.
- Neu co dau hieu nang, can lien he co so y te hoac cap cuu.
