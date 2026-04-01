param(
    [switch]$SkipFlutter,
    [switch]$SkipBackend,
    [switch]$SkipContract,
    [int]$FlakyRepeat = 5
)

$ErrorActionPreference = "Stop"

Write-Host "== MediSign Quality Gate =="

if (-not $SkipFlutter) {
    if (Test-Path "apps/mobile_flutter/pubspec.yaml") {
        Push-Location "apps/mobile_flutter"
        Write-Host "[1/6] Flutter analyze"
        flutter analyze

        Write-Host "[2/6] Flutter tests"
        flutter test

        Write-Host "[3/6] Flutter format check"
        dart format --output=none --set-exit-if-changed .

        Write-Host "[4/6] Flutter flaky guard ($FlakyRepeat lan)"
        for ($i = 1; $i -le $FlakyRepeat; $i++) {
            Write-Host "  - Lan $i/$FlakyRepeat"
            flutter test
        }
        Pop-Location
    } else {
        Write-Host "  - Bo qua flutter check (chua co pubspec.yaml)."
    }
}

if (-not $SkipBackend) {
    Write-Host "[5/6] Backend lint + tests"
    Push-Location "apps/backend_fastapi"
    if (-not (Test-Path "pyproject.toml")) {
        throw "Khong tim thay apps/backend_fastapi/pyproject.toml"
    }
    python -m ruff check .
    python -m black --check .
    python -m pytest
    Pop-Location
}

if (-not $SkipContract) {
    Write-Host "[6/6] OpenAPI contract validation"
    python -c "from pathlib import Path; import yaml; from openapi_spec_validator import validate_spec; spec_path=Path('packages/shared_contracts/openapi/medisign-api.openapi.yaml'); spec=yaml.safe_load(spec_path.read_text(encoding='utf-8')); validate_spec(spec)"
}

Write-Host "== Quality Gate PASS =="
