$ErrorActionPreference = "Stop"

$cloudBaseUrl = $env:MEDISIGN_CLOUD_AI_BASE_URL
if (-not $cloudBaseUrl -and $args.Count -gt 0) {
  $cloudBaseUrl = $args[0]
}

if (-not $cloudBaseUrl) {
  throw "Missing cloud AI base URL. Usage: .\scripts\dev\test-cloud-ai.ps1 http://FPT_VM_IP:8080/v1"
}

$cloudBaseUrl = $cloudBaseUrl.TrimEnd("/")
if (-not $cloudBaseUrl.EndsWith("/v1")) {
  $cloudBaseUrl = "$cloudBaseUrl/v1"
}

$healthUrl = $cloudBaseUrl.Substring(0, $cloudBaseUrl.Length - 3) + "/health"
Write-Host "Checking cloud health: $healthUrl"
try {
  $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 30
} catch {
  throw "Cloud AI is not reachable at $healthUrl. Check VM is running, server is started, and inbound port 8080 is open. Detail: $($_.Exception.Message)"
}

if ($health.status -ne "ok") {
  throw "Unexpected health response: $($health | ConvertTo-Json -Compress)"
}

Write-Host "Health OK"
Write-Host "GPU: $($health.device)"
Write-Host "Adapter exists: $($health.adapter_exists)"
Write-Host "Model loaded: $($health.loaded)"

if ($health.adapter_exists -ne $true) {
  throw "Cloud server cannot see adapter files."
}

if ($health.loaded -ne $true) {
  Write-Host "Warning: model is not preloaded. The chat smoke test may take longer."
}

$body = @{
  model = "medisign-medgemma-medical"
  messages = @(
    @{
      role = "system"
      content = "Bạn là MediSign AI. Trả lời ngắn, an toàn, tiếng Việt."
    },
    @{
      role = "user"
      content = "Tôi đau họng và sốt nhẹ, nên làm gì?"
    }
  )
  temperature = 0.2
  max_tokens = 180
} | ConvertTo-Json -Depth 10

Write-Host "Running chat smoke test: $cloudBaseUrl/chat/completions"
try {
  $response = Invoke-RestMethod `
    -Uri "$cloudBaseUrl/chat/completions" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body `
    -TimeoutSec 180
} catch {
  throw "Cloud chat smoke test failed. Check FPT server terminal for model/load errors. Detail: $($_.Exception.Message)"
}

$content = $response.choices[0].message.content
if (-not $content) {
  throw "Cloud chat returned empty content."
}

Write-Host "Chat OK"
Write-Host "Response preview:"
Write-Host ($content.Substring(0, [Math]::Min(500, $content.Length)))
