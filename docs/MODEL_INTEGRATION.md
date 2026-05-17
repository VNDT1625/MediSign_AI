# MediSign AI Model Integration

## Runtime shape

FastAPI does not load MedGemma 4B directly. The model runs in a separate GPU
process and exposes an OpenAI-compatible endpoint:

```text
Flutter app -> FastAPI -> MedGemma runtime server -> base model + LoRA adapter
```

This keeps the API process lightweight and lets the model server restart,
scale, or move to another GPU machine without changing app code.

## Adapter outputs expected by the backend

Medical adapter:

```text
output/medisign_medgemma4b/adapter/
```

Psychology/SoulGarden adapter:

```text
output/medisign_medgemma4b_psychology/adapter/
```

The backend only stores these paths for readiness checks. The model server is
responsible for loading the base model and adapter.

The backend chooses the OpenAI-compatible `model` field from the request
adapter:

| Request adapter | Runtime model name |
|---|---|
| `medical` | `BACKEND_AI_MEDICAL_MODEL` |
| `psychology` | `BACKEND_AI_PSYCHOLOGY_MODEL` |
| other | `BACKEND_AI_MODEL` |

## Backend env

```env
BACKEND_AI_PROVIDER=openai_compatible
BACKEND_AI_MODEL=google/medgemma-4b-it
BACKEND_AI_MEDICAL_MODEL=medisign-medgemma-medical
BACKEND_AI_PSYCHOLOGY_MODEL=medisign-medgemma-psychology
BACKEND_AI_BASE_URL=http://localhost:8080/v1
BACKEND_AI_API_KEY=
BACKEND_RAG_ENABLED=true
BACKEND_RAG_KNOWLEDGE_BASE_PATH=data/knowledge_base/knowledge_base.json
BACKEND_RAG_DEFAULT_TOP_K=5
BACKEND_RAG_MAX_CONTEXT_CHARS=6000
BACKEND_RAG_MIN_SCORE=0.15
BACKEND_MEDGEMMA_MEDICAL_ADAPTER_PATH=../../output/medisign_medgemma4b/adapter
BACKEND_MEDGEMMA_PSYCHOLOGY_ADAPTER_PATH=../../output/medisign_medgemma4b_psychology/adapter
```

If `BACKEND_AI_PROVIDER=rule_based`, backend returns safe mock/fallback
responses so frontend and API development can continue before training is done.

## Backend endpoints

```http
GET /api/v1/ai/status
POST /api/v1/ai/chat
GET /api/v1/ai/rag/status
POST /api/v1/ai/rag/search
POST /api/v1/ai/rag/rebuild
```

Example:

```json
{
  "message": "Tôi bị sốt và đau họng 2 ngày",
  "adapter": "medical",
  "use_rag": true,
  "rag_top_k": 5
}
```

For Soul Garden:

```json
{
  "message": "Hôm nay tôi rất căng thẳng và khó ngủ",
  "adapter": "psychology"
}
```

## What happens after training

1. Train adapter and place/export it under the expected output folder.
2. Build or refresh the RAG knowledge base:
   ```bash
   python scripts/build_demo_knowledge_base.py
   ```
3. Start a MedGemma runtime server that loads:
   - base model: `google/medgemma-4b-it`
   - selected LoRA adapter: medical or psychology
4. Set backend env to `BACKEND_AI_PROVIDER=openai_compatible` and keep `BACKEND_RAG_ENABLED=true`.
5. Call `/api/v1/ai/rag/status` to confirm the knowledge index is ready.
6. Call `/api/v1/ai/status` to confirm backend can see model and RAG config.
7. Call `/api/v1/ai/chat` from Flutter or Postman.

## RAG behavior

The backend loads `data/knowledge_base/knowledge_base.json` and builds a local
BM25-style medical retrieval index with Vietnamese normalization and common
drug/symptom synonyms. `/api/v1/ai/chat` retrieves context by default, injects
that context into the model system prompt, and returns the used `sources` in
the API response. If the model runtime is offline, the same RAG hits are used
to produce a grounded fallback answer instead of an empty mock.

Use `/api/v1/ai/rag/rebuild` after replacing the knowledge base file without
restarting the API process.
