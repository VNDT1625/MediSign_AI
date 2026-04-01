param(
    [string]$DefaultBranch = "main"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) {
    git init | Out-Null
}

cmd /c "git rev-parse --verify HEAD >NUL 2>NUL"
$hasCommit = $LASTEXITCODE -eq 0

if ($hasCommit) {
    git checkout -B $DefaultBranch | Out-Null
    git checkout -B dev | Out-Null
    git checkout $DefaultBranch | Out-Null

    Write-Host "Git strategy initialized: $DefaultBranch, dev, feature/*, hotfix/*"
} else {
    # On a brand-new repo without commits, only the current unborn branch can exist.
    git symbolic-ref HEAD "refs/heads/$DefaultBranch" | Out-Null

    Write-Host "Repository initialized with unborn branch: $DefaultBranch"
    Write-Host "Create initial commit first, then run: git branch dev"
}

Write-Host "Create branch examples:"
Write-Host "  git checkout -b feature/triage-ui dev"
Write-Host "  git checkout -b hotfix/triage-timeout main"
