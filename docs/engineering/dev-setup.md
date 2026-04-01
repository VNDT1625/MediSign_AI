# Dev Setup

## Prerequisites

- Flutter stable
- Python 3.11+
- PowerShell 7+ hoac bash

## Setup nhanh

Windows:

```powershell
./scripts/dev/bootstrap.ps1
```

Unix:

```bash
bash ./scripts/dev/bootstrap.sh
```

## Chay backend

```bash
cd apps/backend_fastapi
uvicorn app.main:app --reload
```

## Chay mobile

```bash
cd apps/mobile_flutter
flutter run
```

## Quality gate

```powershell
./scripts/qa/run-quality-gate.ps1
```
