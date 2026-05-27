$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$backend = Join-Path $root "apps\backend_fastapi"
$python = Join-Path $backend ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
  throw "Backend virtualenv not found: $python. Run apps/backend_fastapi setup first."
}

Set-Location $root
Write-Host "Starting mock OpenAI-compatible model on http://localhost:8080"
& $python -m uvicorn scripts.dev.mock_openai_model:app --host 0.0.0.0 --port 8080
