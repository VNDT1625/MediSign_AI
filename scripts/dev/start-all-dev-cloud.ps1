$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$rootPath = $root.Path

$cloudBaseUrl = $env:MEDISIGN_CLOUD_AI_BASE_URL
if (-not $cloudBaseUrl -and $args.Count -gt 0) {
  $cloudBaseUrl = $args[0]
}

if (-not $cloudBaseUrl) {
  throw "Missing cloud AI base URL. Usage: .\scripts\dev\start-all-dev-cloud.ps1 http://FPT_VM_IP:8080/v1"
}

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$rootPath\scripts\dev\start-backend-rag-cloud.ps1`"", "`"$cloudBaseUrl`""
Start-Sleep -Seconds 4
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$rootPath\scripts\dev\start-web.ps1`""

Write-Host "Started local dev servers using cloud AI:"
Write-Host "1. Cloud AI:   $cloudBaseUrl"
Write-Host "2. Backend:    http://localhost:8000/api/v1/ai/status"
Write-Host "3. Web:        http://localhost:3000/app/chat"
