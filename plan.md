# MediSign AI Plan

## 0. Execution status

Data completion phase has been executed for public/free-source scope.

Current generated outputs:

- `data/knowledge_base/knowledge_base.json`
- `data/knowledge_base/drugs.json`
- `data/knowledge_base/drug_interactions.json`
- `data/knowledge_base/nutrition_requirements_by_age.json`
- `data/knowledge_base/vietnamese_symptom_phrases.json`
- `data/knowledge_base/vietnam_common_diseases.json`
- `data/knowledge_base/public/openfda_drug_interaction_labels.json`
- `data/knowledge_base/public/nutrition_public_reference.json`
- `data/knowledge_base/public/public_guideline_chunks.json`
- `data/knowledge_base/public/harvest_report.json`
- `data/training_raw/structured_response_training.json`
- `data/eval_sets/demo_safety_eval.jsonl`

Current counts after full DAV crawl and rebuild:

- DAV API raw items: 53,814 / 53,814
- DAV detailed records: 53,698
- DAV detailed drug database: 64,045 records
- Knowledge base total: 128,380 records
- Knowledge base drugs: 60,472 records
- Drug interaction records: 67,493 records
  - curated high-risk interaction pairs: 20 records
  - public openFDA/DailyMed drug-label interaction sections: 67,473 records
- Nutrition by age/context: 38 records
  - Vietnam BYT/NIN seed rows: 18 records
  - NIH ODS public reference rows: 20 records
- Vietnamese symptom/culture phrases: 11 records
- Vietnam common diseases: 10 records
- Public guideline/document chunks: 356 records
- Structured output training samples: 67 records
- Demo eval samples: 67 records
- MedGemma merged dataset: 17,263 records
- MedGemma train/eval: 15,536 / 1,727 records

Public harvest notes:

- DrugBank Clinical was not fetched because it is paid/licensed and needs credentials.
- DrugBank full database download was attempted with the provided account on 2026-05-17, but the server returned `403 Forbidden`; the current DrugBank release page says academic dataset downloads are temporarily paused while they update distribution.
- `data/knowledge_base/public/raw/drugbank/drugbank.xsd` has been copied into the project. This is the XML schema, not the database content.
- openFDA/DailyMed interaction data is broad public label text, not clean severity/mechanism interaction pairs.
- KCB/BYT/NIN guideline data is a public snapshot from reachable official pages, linked PDFs, and the Vietnam RDA PDF available during harvest.
- This is now enough for RAG/RAG-lite indexing, but still needs medical review before production use.

Verification completed:

- QLoRA config smoke test: 13 passed, 1 skipped
- MedGemma prepare/format tests: 26 passed

## 1. RAG status

RAG chua duoc implement trong backend.

Hien tai backend da co:

- AI model client: `apps/backend_fastapi/app/services/ai_model_service.py`
- Rule-based triage: `apps/backend_fastapi/app/services/ai_triage_service.py`
- Drug lookup service: `apps/backend_fastapi/app/services/drug_lookup_service.py`
- Drug database tu DAV/Cuc Duoc va cac nguon thuoc khac

Hien tai backend chua co:

- `rag_service.py`
- Embedding model/service
- Vector database/index nhu FAISS, Chroma, Qdrant, pgvector
- Retrieval top-k context
- Context injection truoc khi goi MedGemma
- Citation/source tracking cho cau tra loi

MVP nen lam theo thu tu:

1. RAG-lite cho thuoc: search truc tiep drug database theo ten thuoc, hoat chat, so dang ky.
2. Dua ket qua search vao prompt/context cho MedGemma.
3. Sau do moi bo sung vector RAG cho tai lieu y khoa, guideline, FAQ, bai viet da kiem duyet.

## 2. Model flow

### Text input

```text
User text
-> MedGemma 4B + MediSign adapter
-> Structured output cho UI
```

### JPG input

```text
User JPG
-> MedGemma 4B vision doc/nhan dien anh
-> Tao image_context dang text/cau truc
-> MedGemma 4B + MediSign adapter xu ly image_context
-> Structured output cho UI
```

Khong train vision trong phase hien tai. Chi train text adapter de model hieu tieng Viet, thuoc Viet Nam, safety, va format dau ra cua MediSign.

## 3. Required output modes

Model/backend can tra ve structured output, khong chi plain text.

Cac mode can co:

- `clarification`: thieu thong tin, hoi them nhu chat text.
- `analysis`: du thong tin hoac co anh, tra card danh gia so bo va goi y xu tri.
- `emergency`: co dau hieu nguy hiem, uu tien cap cuu/kham gap.
- `medicine_lookup`: lien quan den thuoc, can dua ket qua lookup/RAG-lite vao cau tra loi.
- `unsupported_image`: anh khong ro, khong thuoc mien y khoa, hoac khong du chat luong.

## 4. Required response schema draft

```json
{
  "response_type": "clarification | analysis | emergency | medicine_lookup | unsupported_image",
  "chat_message": {
    "kind": "text | analysis",
    "text": "Cau tra loi ngan cho nguoi dung",
    "bullets": ["Cau hoi them 1", "Cau hoi them 2"],
    "intro": "Mo dau cho analysis card",
    "assessment": [
      { "label": "Nhiet do", "value": "37.8°C (sot nhe)" }
    ],
    "handling": [
      "Nghi ngoi, uong nhieu nuoc am."
    ],
    "note": "Day khong phai chan doan cuoi cung..."
  },
  "quick_summary": {
    "symptoms": "Tom tat trieu chung",
    "preliminary_assessment": "Danh gia so bo",
    "recommendation": "Khuyen nghi ngan gon"
  },
  "image_context": {
    "image_type": "medicine_package | prescription | xray | skin | lab_result | unknown",
    "extracted_text": "Text doc duoc tu anh neu co",
    "observations": ["Quan sat tu anh"],
    "confidence": "low | medium | high",
    "limitations": "Gioi han cua viec doc anh"
  },
  "next_suggestions": [
    { "label": "Khi nao can di kham?", "intent": "red_flags" }
  ],
  "safety": {
    "urgency": "self_care | clinic | urgent | emergency",
    "red_flags": [],
    "disclaimer": "MediSign AI chi dua ra goi y so bo, khong thay the chan doan cua bac si."
  },
  "sources": [
    {
      "type": "drug_database | guideline | model_vision",
      "title": "Ten nguon",
      "record_id": "optional",
      "url": "optional"
    }
  ]
}
```

## 5. Training target

Train adapter de model:

- Tra loi bang tieng Viet tu nhien, de hieu.
- Hieu cach dien dat cua nguoi Viet trong trieu chung hang ngay.
- Hieu thuoc Viet Nam, ten thuong mai, hoat chat, dang bao che, so dang ky.
- Biet khi nao hoi them thong tin.
- Biet khi nao tao analysis card.
- Biet khi nao can canh bao kham gap/cap cuu.
- Luon tra output theo schema.
- Luon co disclaimer y te.

Kien thuc thay doi nhanh, dac biet thuoc va guideline, nen uu tien dua qua RAG/RAG-lite thay vi chi nhoi vao fine-tune.
