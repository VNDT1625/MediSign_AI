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

$backendReady = $false
for ($i = 1; $i -le 90; $i++) {
  Start-Sleep -Seconds 2
  try {
    $status = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/rag/status" -TimeoutSec 2
    if ($status.ready -eq $true) {
      $backendReady = $true
      break
    }
  } catch {
  }
}

if (-not $backendReady) {
  throw "Backend was not ready after 180 seconds. Check the backend terminal before opening the web app."
} else {
  Write-Host "Backend and RAG are ready."
}

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$rootPath\scripts\dev\start-web.ps1`""

Write-Host "Started local dev servers using cloud AI:"
Write-Host "1. Cloud AI:   $cloudBaseUrl"
Write-Host "2. Backend:    http://localhost:8000/api/v1/ai/status"
Write-Host "3. Web:        http://localhost:3000/app/chat"
