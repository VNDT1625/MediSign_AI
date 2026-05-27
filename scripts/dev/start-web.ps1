$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$web = Join-Path $root "apps\web_next"

$env:NEXT_PUBLIC_API_BASE_URL = "http://localhost:8000/api/v1"
$env:FRONTEND_BASE_URL = "http://localhost:3000"
$env:AUTH_COOKIE_SECURE = "false"

Set-Location $web
Write-Host "Starting Next.js web on http://localhost:3000/"
npm run dev
