param(
    [ValidateSet("mobile", "web", "all")]
    [string]$Target = "mobile",
    [switch]$SkipAnalyze,
    [switch]$SkipFormat,
    [switch]$SkipBuild,
    [switch]$SkipE2E
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")

function Test-MobileFrontend {
    $mobile = Join-Path $root "apps\mobile_flutter"
    Push-Location $mobile
    try {
        Write-Host "== Flutter pub get =="
        flutter pub get

        if (-not $SkipAnalyze) {
            Write-Host "== Flutter analyze =="
            flutter analyze
        }

        Write-Host "== Flutter tests =="
        flutter test

        if (-not $SkipFormat) {
            Write-Host "== Flutter format check =="
            dart format --output=none --set-exit-if-changed .
        }
    }
    finally {
        Pop-Location
    }
}

function Test-WebFrontend {
    $web = Join-Path $root "apps\web_next"
    Push-Location $web
    try {
        Write-Host "== Web npm install/check =="
        if (-not (Test-Path "node_modules")) {
            npm install
        }

        Write-Host "== Web unit tests =="
        npm run test:run

        if (-not $SkipBuild) {
            Write-Host "== Web build =="
            npm run build
        }

        if (-not $SkipE2E) {
            Write-Host "== Web e2e =="
            npm run e2e
        }
    }
    finally {
        Pop-Location
    }
}

if ($Target -eq "mobile" -or $Target -eq "all") {
    Test-MobileFrontend
}

if ($Target -eq "web" -or $Target -eq "all") {
    Test-WebFrontend
}
