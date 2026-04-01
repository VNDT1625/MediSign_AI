# Branching Strategy

- `main`: production-ready
- `dev`: integration branch
- `feature/*`: feature development from `dev`
- `hotfix/*`: urgent fixes from `main`

## Initialize branches

```powershell
./scripts/git/init-branch-strategy.ps1
```

## Basic flow

1. Tao `feature/*` tu `dev`
2. Mo PR vao `dev` sau khi quality gate pass
3. Merge `dev` -> `main` theo release cadence
