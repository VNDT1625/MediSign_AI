$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$backend = Join-Path $root "apps\backend_fastapi"
$python = Join-Path $backend ".venv\Scripts\python.exe"
$adapter = Join-Path $root "output\medisign-medgemma4b-adapter"

if (-not (Test-Path $python)) {
  throw "Backend virtualenv not found: $python. Run apps/backend_fastapi setup first."
}

if (-not (Test-Path $adapter)) {
  throw "Adapter not found: $adapter. Clone https://huggingface.co/thuaannn/medisign-medgemma4b-adapter first."
}

$env:MEDISIGN_BASE_MODEL = if ($env:MEDISIGN_BASE_MODEL) { $env:MEDISIGN_BASE_MODEL } else { "google/medgemma-1.5-4b-it" }
$env:MEDISIGN_ADAPTER_PATH = if ($env:MEDISIGN_ADAPTER_PATH) { $env:MEDISIGN_ADAPTER_PATH } else { $adapter }
$env:MEDISIGN_LOAD_IN_4BIT = if ($env:MEDISIGN_LOAD_IN_4BIT) { $env:MEDISIGN_LOAD_IN_4BIT } else { "1" }

Set-Location $root
Write-Host "Starting MediSign MedGemma server on http://localhost:8080"
Write-Host "Base model: $env:MEDISIGN_BASE_MODEL"
Write-Host "Adapter:    $env:MEDISIGN_ADAPTER_PATH"
& $python -m uvicorn scripts.dev.medgemma_openai_server:app --host 0.0.0.0 --port 8080
