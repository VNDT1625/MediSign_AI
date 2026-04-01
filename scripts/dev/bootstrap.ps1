$ErrorActionPreference = "Stop"

Write-Host "== MediSign bootstrap (Windows) =="

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

if (Test-Path "apps/mobile_flutter/pubspec.yaml") {
    Push-Location "apps/mobile_flutter"
    flutter pub get
    Pop-Location
}

if (Test-Path "apps/backend_fastapi/pyproject.toml") {
    Push-Location "apps/backend_fastapi"
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -e ".[dev]"
    Pop-Location
}

Write-Host "Bootstrap done."
