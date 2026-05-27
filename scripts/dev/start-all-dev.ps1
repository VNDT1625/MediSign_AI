$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$rootPath = $root.Path

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$rootPath\scripts\dev\start-medgemma-server.ps1`""
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$rootPath\scripts\dev\start-backend-rag.ps1`""
Start-Sleep -Seconds 4
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$rootPath\scripts\dev\start-web.ps1`""

Write-Host "Started 3 dev servers:"
Write-Host "1. MedGemma:   http://localhost:8080/health"
Write-Host "2. Backend:    http://localhost:8000/api/v1/ai/status"
Write-Host "3. Web:        http://localhost:3000/"
