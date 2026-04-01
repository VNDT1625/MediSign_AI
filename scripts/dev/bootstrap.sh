#!/usr/bin/env bash
set -euo pipefail

echo "== MediSign bootstrap (Unix) =="

if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

if [[ -f apps/mobile_flutter/pubspec.yaml ]]; then
  pushd apps/mobile_flutter >/dev/null
  flutter pub get
  popd >/dev/null
fi

if [[ -f apps/backend_fastapi/pyproject.toml ]]; then
  pushd apps/backend_fastapi >/dev/null
  python3 -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -e ".[dev]"
  popd >/dev/null
fi

echo "Bootstrap done."
