$ErrorActionPreference = "Stop"

$root = Resolve-Path "."
$windsurfWorkflows = Join-Path $root ".windsurf/workflows"
$vibecodeWorkflows = Join-Path $root ".vibecode/workflows"
$githubSkills = Join-Path $root ".github/skills"
$vibecodeSkills = Join-Path $root ".vibecode/skills"

New-Item -ItemType Directory -Force -Path $vibecodeWorkflows | Out-Null
New-Item -ItemType Directory -Force -Path $vibecodeSkills | Out-Null

if (Test-Path $windsurfWorkflows) {
    Get-ChildItem -Path $windsurfWorkflows -File -Filter *.md |
        ForEach-Object {
            Copy-Item $_.FullName -Destination (Join-Path $vibecodeWorkflows $_.Name) -Force
        }
    Write-Host "Synced workflows from .windsurf/workflows -> .vibecode/workflows"
}

if (Test-Path $githubSkills) {
    Get-ChildItem -Path $githubSkills -File -Filter *.md |
        ForEach-Object {
            Copy-Item $_.FullName -Destination (Join-Path $vibecodeSkills $_.Name) -Force
        }
    Write-Host "Synced skills from .github/skills -> .vibecode/skills"
}

Write-Host "Vibecode sync done."
