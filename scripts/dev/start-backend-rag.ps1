$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$backend = Join-Path $root "apps\backend_fastapi"
$python = Join-Path $backend ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
  throw "Backend virtualenv not found: $python. Run: cd apps/backend_fastapi; python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -e .[dev]"
}

$dbUrl = "sqlite:///$($root.Path.Replace('\','/'))/data/dev_backend.sqlite3"
$kbPath = Join-Path $root "data\knowledge_base\knowledge_base.json"
if (-not (Test-Path $kbPath)) {
  throw "RAG knowledge base not found: $kbPath"
}

$env:DATABASE_URL = $dbUrl
$env:BACKEND_DATABASE_URL = $dbUrl
$env:BACKEND_AI_PROVIDER = "openai_compatible"
$env:BACKEND_AI_BASE_URL = "http://localhost:8080/v1"
$env:BACKEND_AI_MODEL = "google/medgemma-1.5-4b-it"
$env:BACKEND_AI_MEDICAL_MODEL = "medisign-medgemma-medical"
$env:BACKEND_AI_PSYCHOLOGY_MODEL = "medisign-medgemma-psychology"
$env:BACKEND_AI_REQUEST_TIMEOUT_SECONDS = "180"
$env:BACKEND_RAG_ENABLED = "true"
$env:BACKEND_RAG_KNOWLEDGE_BASE_PATH = $kbPath
$env:BACKEND_RAG_DEFAULT_TOP_K = "5"
$env:BACKEND_RAG_MAX_CONTEXT_CHARS = "6000"
$env:BACKEND_RAG_MIN_SCORE = "0.15"

Set-Location $backend
Write-Host "Starting FastAPI backend on http://localhost:8000"
Write-Host "RAG: $env:BACKEND_RAG_KNOWLEDGE_BASE_PATH"
Write-Host "Model endpoint: $env:BACKEND_AI_BASE_URL"
& $python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
