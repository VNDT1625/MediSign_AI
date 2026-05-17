"""
Standalone smoke test for `scripts/train_qlora_medgemma.py` (Task 1.5).

This is a thin wrapper that re-runs the pytest suite under
`scripts/tests/test_train_qlora_config.py`. It exists so the script can
be invoked directly on a fresh Kaggle / Vast.ai instance to verify the
training environment is configured correctly **before** kicking off
the full multi-hour training run.

Usage
-----
    python scripts/train_qlora_medgemma_smoke_test.py

The same checks run via pytest on developer machines:

    pytest scripts/tests/test_train_qlora_config.py -v

Exits with status code 0 on success, non-zero on the first failure.
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    import pytest  # imported lazily so an informative error fires if missing

    test_file = Path(__file__).resolve().parent / "tests" / "test_train_qlora_config.py"
    if not test_file.exists():
        print(f"ERROR: test file not found at {test_file}", file=sys.stderr)
        return 1

    print(f"Running QLoRA config smoke tests: {test_file}")
    return pytest.main([str(test_file), "-v", "--no-header"])


if __name__ == "__main__":
    sys.exit(main())
