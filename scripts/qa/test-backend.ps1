param(
    [switch]$SkipLint,
    [string[]]$PytestArgs = @()
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$backend = Join-Path $root "apps\backend_fastapi"
$venvPython = Join-Path $backend ".venv\Scripts\python.exe"
$effectivePytestArgs = @()

foreach ($arg in $PytestArgs) {
    $effectivePytestArgs += $arg -split "," | Where-Object { $_ -ne "" }
}

if (Test-Path $venvPython) {
    $python = $venvPython
} else {
    $python = "python"
    Write-Host "Backend .venv not found, using system python."
    Write-Host "If dependencies are missing, run:"
    Write-Host "  cd apps\backend_fastapi; python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -e .[dev]"
}

Push-Location $backend
try {
    if (-not $SkipLint) {
        Write-Host "== Backend ruff =="
        & $python -m ruff check .

        Write-Host "== Backend black check =="
        & $python -m black --check .
    }

    Write-Host "== Backend pytest =="
    if ($effectivePytestArgs.Count -gt 0) {
        & $python -m pytest @effectivePytestArgs
    } else {
        & $python -m pytest
    }
}
finally {
    Pop-Location
}
