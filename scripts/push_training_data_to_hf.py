"""Push training data lên HuggingFace Dataset Hub.

Usage:
    python scripts/push_training_data_to_hf.py
    python scripts/push_training_data_to_hf.py --repo thuaannn/medisign-training-data
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "training_clean" / "medgemma_4b"
TRAIN_FILE = DATA_DIR / "train.jsonl"
EVAL_FILE = DATA_DIR / "eval.jsonl"

DEFAULT_REPO = "thuaannn/medisign-training-data"


def push(repo: str, token: str | None = None, files: list[str] | None = None) -> None:
    try:
        from huggingface_hub import HfApi, login
        from huggingface_hub.utils import HfHubHTTPError
    except ImportError:
        print("[ERROR] huggingface_hub not installed. Run: pip install huggingface_hub")
        sys.exit(1)

    if token:
        login(token=token, add_to_git_credential=False)
        print("Logged in with provided token.")

    # Determine which files to upload
    if files:
        upload_files = [(DATA_DIR / f, f) for f in files]
    else:
        upload_files = [(TRAIN_FILE, "train.jsonl"), (EVAL_FILE, "eval.jsonl")]

    # Check files exist
    for file_path, _ in upload_files:
        if not file_path.exists():
            print(f"[ERROR] Missing: {file_path}")
            sys.exit(1)

    total = sum(p.stat().st_size for p, _ in upload_files)
    print(f"Files to upload: {len(upload_files)} ({total/1024/1024:.1f} MB total)")
    print(f"Target: {repo}")
    print()

    api = HfApi(token=token)

    # Create repo if not exists
    try:
        api.repo_info(repo_id=repo, repo_type="dataset")
        print(f"Repo exists: https://huggingface.co/datasets/{repo}")
    except HfHubHTTPError:
        print(f"Creating new dataset repo: {repo}")
        api.create_repo(repo_id=repo, repo_type="dataset", private=False)

    # Upload files
    for file_path, hf_path in upload_files:
        n = sum(1 for _ in file_path.open(encoding="utf-8"))
        print(f"Uploading {file_path.name} ({file_path.stat().st_size / 1024 / 1024:.1f} MB, {n:,} records)...")
        api.upload_file(
            path_or_fileobj=str(file_path),
            path_in_repo=hf_path,
            repo_id=repo,
            repo_type="dataset",
            commit_message=f"Update {hf_path}: {n:,} records",
        )
        print(f"  ✓ {hf_path} uploaded")

    print(f"\n✅ Done! Dataset at: https://huggingface.co/datasets/{repo}")
    print("\nTrên FPT Cloud VM, pull về bằng:")
    print(f"  huggingface-cli download {repo} \\")
    print(f"    --repo-type dataset \\")
    print(f"    --local-dir data/training_clean/medgemma_4b/")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO, help="HuggingFace dataset repo ID")
    parser.add_argument("--token", default=None, help="HuggingFace write token")
    parser.add_argument("--files", nargs="+", default=None, help="Specific filenames to upload from data dir")
    args = parser.parse_args()
    push(args.repo, token=args.token, files=args.files)


if __name__ == "__main__":
    main()
