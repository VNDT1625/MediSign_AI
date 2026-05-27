"""
medisign_train_kaggle.py  (v5 token_type_ids fix)
=================================================
All-in-one script de train MedGemma QLoRA tren Kaggle.

Cach chay trong Kaggle Notebook:
    exec(open("scripts/medisign_train_kaggle.py").read())

Yeu cau:
  - Kaggle Secret ten: HF_TOKEN
  - GPU T4 x1 hoac T4 x2
  - Internet = On
"""

import os
import sys
import shutil
import subprocess


# ══════════════════════════════════════════════════════════
# Helper
# ══════════════════════════════════════════════════════════

def print_title(title):
    print("\n" + "═" * 60)
    print(title)
    print("═" * 60)


def run_cmd(cmd, check=False, capture=False):
    print("\n▶ CMD:")
    print(" ".join(cmd) if isinstance(cmd, list) else cmd)

    return subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        check=check,
        text=True if capture else None,
        capture_output=capture,
    )


def is_code_error(stderr_text):
    code_errors = [
        "SyntaxError",
        "IndentationError",
        "ImportError",
        "ModuleNotFoundError",
    ]
    return any(err in stderr_text for err in code_errors)


def is_oom_error(stderr_text):
    oom_errors = [
        "CUDA out of memory",
        "OutOfMemoryError",
        "torch.cuda.OutOfMemoryError",
    ]
    return any(err in stderr_text for err in oom_errors)


# ══════════════════════════════════════════════════════════
# BUOC 1 — Kiem tra GPU
# ══════════════════════════════════════════════════════════

print_title("BUOC 1: Kiem tra GPU")

run_cmd("nvidia-smi || echo 'nvidia-smi not in PATH'", check=False)

import torch

if not torch.cuda.is_available():
    print("Khong phat hien GPU - dung lai!")
    sys.exit(1)

print(f"CUDA: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")

for i in range(torch.cuda.device_count()):
    name = torch.cuda.get_device_name(i)
    mem = torch.cuda.get_device_properties(i).total_memory / 1024**3
    print(f"   GPU {i}: {name} ({mem:.1f} GB VRAM)")


# ══════════════════════════════════════════════════════════
# BUOC 2 — Clone repo sach
# ══════════════════════════════════════════════════════════

print_title("BUOC 2: Clone repo sach")

REPO_URL = "https://github.com/VNDT1625/MediSign_AI.git"
BRANCH = "codex/medgemma-kaggle-training"

WORKING_DIR = "/kaggle/working"
REPO_DIR = os.path.join(WORKING_DIR, "MediSign_AI")

os.chdir(WORKING_DIR)

if os.path.exists(REPO_DIR):
    print("Repo da ton tai - xoa de tranh patch chong patch...")
    shutil.rmtree(REPO_DIR)

run_cmd(
    ["git", "clone", "-b", BRANCH, REPO_URL],
    check=True,
)

os.chdir(REPO_DIR)

print(f"Dang o: {os.getcwd()}")
run_cmd(["ls", "-lh"], check=False)


# ══════════════════════════════════════════════════════════
# BUOC 3 — Kiem tra data
# ══════════════════════════════════════════════════════════

print_title("BUOC 3: Kiem tra data")

TRAIN_FILE = "data/training_clean/medgemma_4b/train.jsonl"
EVAL_FILE = "data/training_clean/medgemma_4b/eval.jsonl"

for file_path in [TRAIN_FILE, EVAL_FILE]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Thieu file: {file_path}")

    lines = int(subprocess.check_output(["wc", "-l", file_path]).split()[0])
    print(f"{file_path}: {lines:,} dong")


# ══════════════════════════════════════════════════════════
# BUOC 4 — Cai dependency
# ══════════════════════════════════════════════════════════

print_title("BUOC 4: Cai dependency")

REQ_FILE = "scripts/requirements_train.txt"

if not os.path.exists(REQ_FILE):
    raise FileNotFoundError(f"Khong thay file: {REQ_FILE}")

run_cmd(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-q",
        "-r",
        REQ_FILE,
    ],
    check=True,
)

print("Dependencies installed")


# ══════════════════════════════════════════════════════════
# BUOC 5 — Hugging Face login
# ══════════════════════════════════════════════════════════

print_title("BUOC 5: Hugging Face login")

from kaggle_secrets import UserSecretsClient
from huggingface_hub import login, model_info

try:
    user_secrets = UserSecretsClient()
    token = user_secrets.get_secret("HF_TOKEN")
except Exception as e:
    print(f"Khong doc duoc Kaggle Secret HF_TOKEN: {e}")
    token = None

if not token:
    raise RuntimeError(
        "Khong thay HF_TOKEN. "
        "Vao Kaggle Notebook -> Add-ons -> Secrets -> them HF_TOKEN va bat quyen truy cap."
    )

login(
    token=token,
    add_to_git_credential=False,
)

print("Dang nhap Hugging Face thanh cong")


# ══════════════════════════════════════════════════════════
# BUOC 6 — Kiem tra quyen truy cap model
# ══════════════════════════════════════════════════════════

print_title("BUOC 6: Kiem tra quyen truy cap MedGemma")

MODEL_ID = "google/medgemma-1.5-4b-it"

try:
    info = model_info(MODEL_ID, token=token)
    print(f"Truy cap OK: {info.modelId}")
except Exception as e:
    print(f"Khong truy cap duoc {MODEL_ID}: {e}")
    print("Kiem tra token hoac request access model tren Hugging Face.")
    sys.exit(1)


# ══════════════════════════════════════════════════════════
# BUOC 7 — Patch SFTConfig
# ══════════════════════════════════════════════════════════

print_title("BUOC 7: Patch SFTConfig")

SCRIPT_PATH = "scripts/train_qlora_medgemma.py"

if not os.path.exists(SCRIPT_PATH):
    raise FileNotFoundError(f"Khong thay training script: {SCRIPT_PATH}")

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script = f.read()

patched = False

if "max_seq_length=cfg.max_seq_length" in script:
    script = script.replace(
        "max_seq_length=cfg.max_seq_length",
        "max_length=cfg.max_seq_length",
    )
    patched = True

if patched:
    with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(script)
    print("Patched: max_seq_length -> max_length")
else:
    print("Khong can patch max_seq_length hoac khong tim thay chuoi can sua")


# ══════════════════════════════════════════════════════════
# BUOC 7.5 — Patch QLoRA defaults truoc khi train
# ══════════════════════════════════════════════════════════

print_title("BUOC 7.5: Patch QLoRA defaults toi uu")

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script = f.read()

qlora_patches = {
    'LORA_TARGET_MODULES = ["q_proj", "v_proj", "k_proj", "o_proj"]': (
        'LORA_TARGET_MODULES = [\n'
        '    "q_proj",\n'
        '    "v_proj",\n'
        '    "k_proj",\n'
        '    "o_proj",\n'
        '    "gate_proj",\n'
        '    "up_proj",\n'
        '    "down_proj",\n'
        ']'
    ),
    "LORA_DROPOUT = 0.1": "LORA_DROPOUT = 0.05",
    "WARMUP_RATIO = 0.03": "WARMUP_RATIO = 0.05",
    "packing=False,": "packing=True,",
}

applied = []
skipped = []

for old, new in qlora_patches.items():
    if old in script:
        script = script.replace(old, new)
        applied.append(old[:72])
    else:
        skipped.append(old[:72])

if "weight_decay=" not in script and "neftune_noise_alpha=" not in script:
    old = "dataloader_pin_memory=False,"
    new = (
        "dataloader_pin_memory=False,\n"
        "        weight_decay=0.01,\n"
        "        neftune_noise_alpha=5,"
    )
    if old in script:
        script = script.replace(old, new)
        applied.append(old[:72])
    else:
        skipped.append(old[:72])

if applied:
    with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(script)

for item in applied:
    print(f"Patched: {item}...")
for item in skipped:
    print(f"Da co hoac khong tim thay: {item}...")


# ══════════════════════════════════════════════════════════
# BUOC 8 — Patch Gemma3 token_type_ids FIX MANH
# ══════════════════════════════════════════════════════════

print_title("BUOC 8: Patch Gemma3 token_type_ids fix manh")

PATCH_SNIPPET = r'''
# ── MediSign v5 Gemma3 token_type_ids training patch ──
try:
    import inspect as _medisign_inspect
    import torch as _medisign_torch
    from transformers.models.gemma3 import modeling_gemma3 as _medisign_gemma3

    def _medisign_make_token_type_ids(input_ids=None, inputs_embeds=None):
        if input_ids is not None:
            return _medisign_torch.zeros_like(input_ids, dtype=_medisign_torch.long)

        if inputs_embeds is not None:
            return _medisign_torch.zeros(
                inputs_embeds.shape[:2],
                dtype=_medisign_torch.long,
                device=inputs_embeds.device,
            )

        return None

    # Patch Gemma3ForCausalLM.forward
    if hasattr(_medisign_gemma3, "Gemma3ForCausalLM"):
        _Gemma3ForCausalLM = _medisign_gemma3.Gemma3ForCausalLM

        if not hasattr(_Gemma3ForCausalLM, "_medisign_original_forward"):
            _Gemma3ForCausalLM._medisign_original_forward = _Gemma3ForCausalLM.forward

            def _medisign_causal_lm_forward(self, *args, **kwargs):
                if kwargs.get("token_type_ids") is None:
                    token_type_ids = _medisign_make_token_type_ids(
                        input_ids=kwargs.get("input_ids"),
                        inputs_embeds=kwargs.get("inputs_embeds"),
                    )
                    if token_type_ids is not None:
                        kwargs["token_type_ids"] = token_type_ids

                return _Gemma3ForCausalLM._medisign_original_forward(
                    self,
                    *args,
                    **kwargs,
                )

            _Gemma3ForCausalLM.forward = _medisign_causal_lm_forward

    # Patch Gemma3Model.forward
    if hasattr(_medisign_gemma3, "Gemma3Model"):
        _Gemma3Model = _medisign_gemma3.Gemma3Model

        if not hasattr(_Gemma3Model, "_medisign_original_forward"):
            _Gemma3Model._medisign_original_forward = _Gemma3Model.forward

            def _medisign_model_forward(self, *args, **kwargs):
                if kwargs.get("token_type_ids") is None:
                    token_type_ids = _medisign_make_token_type_ids(
                        input_ids=kwargs.get("input_ids"),
                        inputs_embeds=kwargs.get("inputs_embeds"),
                    )
                    if token_type_ids is not None:
                        kwargs["token_type_ids"] = token_type_ids

                return _Gemma3Model._medisign_original_forward(
                    self,
                    *args,
                    **kwargs,
                )

            _Gemma3Model.forward = _medisign_model_forward

    # Patch create_causal_mask_mapping, ke ca token_type_ids duoc truyen dang positional arg
    if hasattr(_medisign_gemma3, "create_causal_mask_mapping"):
        if not hasattr(_medisign_gemma3, "_medisign_original_create_causal_mask_mapping"):
            _medisign_gemma3._medisign_original_create_causal_mask_mapping = (
                _medisign_gemma3.create_causal_mask_mapping
            )

            _medisign_causal_sig = _medisign_inspect.signature(
                _medisign_gemma3._medisign_original_create_causal_mask_mapping
            )

            def _medisign_patched_create_causal_mask_mapping(*args, **kwargs):
                try:
                    bound = _medisign_causal_sig.bind_partial(*args, **kwargs)

                    token_type_ids = bound.arguments.get("token_type_ids")
                    input_ids = bound.arguments.get("input_ids")
                    inputs_embeds = bound.arguments.get("inputs_embeds")

                    if token_type_ids is None:
                        new_token_type_ids = _medisign_make_token_type_ids(
                            input_ids=input_ids,
                            inputs_embeds=inputs_embeds,
                        )

                        if new_token_type_ids is not None:
                            bound.arguments["token_type_ids"] = new_token_type_ids
                            return _medisign_gemma3._medisign_original_create_causal_mask_mapping(
                                *bound.args,
                                **bound.kwargs,
                            )

                except Exception:
                    pass

                if kwargs.get("token_type_ids") is None:
                    token_type_ids = _medisign_make_token_type_ids(
                        input_ids=kwargs.get("input_ids"),
                        inputs_embeds=kwargs.get("inputs_embeds"),
                    )
                    if token_type_ids is not None:
                        kwargs["token_type_ids"] = token_type_ids

                return _medisign_gemma3._medisign_original_create_causal_mask_mapping(
                    *args,
                    **kwargs,
                )

            _medisign_gemma3.create_causal_mask_mapping = (
                _medisign_patched_create_causal_mask_mapping
            )

    print("MediSign v5 Gemma3 token_type_ids patch active")

except Exception as _medisign_patch_error:
    print(f"MediSign Gemma3 token_type_ids patch skipped: {_medisign_patch_error}")
# ── End MediSign v5 Gemma3 token_type_ids training patch ──
'''


def find_safe_top_level_insert_index(lines):
    """
    Chi chen patch sau block import top-level dau file.
    Khong scan toan bo file de tranh chen nham vao import ben trong ham.
    """

    insert_idx = 0
    seen_import = False
    in_docstring = False
    docstring_quote = None

    for i, line in enumerate(lines[:120]):
        stripped = line.strip()

        if i == 0 and (
            stripped.startswith('"""') or stripped.startswith("'''")
        ):
            quote = stripped[:3]
            if stripped.count(quote) == 1:
                in_docstring = True
                docstring_quote = quote
            continue

        if in_docstring:
            if docstring_quote and docstring_quote in stripped:
                in_docstring = False
            continue

        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("import ") or stripped.startswith("from "):
            seen_import = True
            insert_idx = i + 1
            continue

        if seen_import:
            break

    return insert_idx


with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script = f.read()

# Xoa patch cu neu co de tranh xung dot
old_markers = [
    "# ── MediSign safe Gemma3 token_type_ids monkey-patch ──",
    "# ── Gemma3 token_type_ids monkey-patch ──",
]

for marker in old_markers:
    if marker in script:
        print(f"Phat hien patch cu: {marker}")
        print("Repo vua clone sach thuong khong co, neu co thi nen kiem tra thu cong.")

if "MediSign v5 Gemma3 token_type_ids training patch" not in script:
    lines = script.splitlines()
    insert_idx = find_safe_top_level_insert_index(lines)
    lines.insert(insert_idx, PATCH_SNIPPET)

    with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Gemma3 token_type_ids patch v5 inserted tai dong khoang: {insert_idx + 1}")
else:
    print("Gemma3 patch v5 da ton tai")


# ══════════════════════════════════════════════════════════
# BUOC 9 — Kiem tra cu phap
# ══════════════════════════════════════════════════════════

print_title("BUOC 9: Kiem tra cu phap training script")

syntax_check = run_cmd(
    [sys.executable, "-m", "py_compile", SCRIPT_PATH],
    check=False,
    capture=True,
)

if syntax_check.returncode != 0:
    print("Training script dang loi cu phap. Dung truoc khi smoke test.")
    print("\nSTDOUT:")
    print(syntax_check.stdout)
    print("\nSTDERR:")
    print(syntax_check.stderr)
    print("\nChay cell nay de xem quanh dong loi:")
    print(f"!nl -ba {SCRIPT_PATH} | sed -n '1,120p'")
    sys.exit(1)

print("Syntax OK")


# ══════════════════════════════════════════════════════════
# BUOC 10 — Unit tests
# ══════════════════════════════════════════════════════════

print_title("BUOC 10: Unit tests")

test_files = [
    "scripts/tests/test_prepare_medgemma_data.py",
    "scripts/tests/test_format_medgemma_dataset.py",
]

existing_tests = [t for t in test_files if os.path.exists(t)]

if existing_tests:
    result = run_cmd(
        [sys.executable, "-m", "pytest"] + existing_tests + ["-v"],
        check=False,
    )

    if result.returncode != 0:
        print("Unit tests FAILED - xem loi o tren")
        sys.exit(1)

    print("Unit tests PASSED")
else:
    print("Khong tim thay file test - bo qua")


# ══════════════════════════════════════════════════════════
# BUOC 11 — Smoke test thong minh
# ══════════════════════════════════════════════════════════

print_title("BUOC 11: Smoke test thong minh")

SMOKE_OUTPUT = "output/medisign_medgemma4b_smoke"
SMOKE_ADAPTER = f"{SMOKE_OUTPUT}/adapter"


def build_train_cmd(
    output_dir,
    adapter_dir,
    max_seq_length,
    per_device_batch_size="1",
    gradient_accumulation_steps="16",
    learning_rate="3e-4",
    max_steps=None,
    num_epochs=None,
):
    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--model_id", MODEL_ID,
        "--train_file", TRAIN_FILE,
        "--eval_file", EVAL_FILE,
        "--output_dir", output_dir,
        "--adapter_dir", adapter_dir,
        "--max_seq_length", str(max_seq_length),
        "--per_device_batch_size", str(per_device_batch_size),
        "--gradient_accumulation_steps", str(gradient_accumulation_steps),
        "--learning_rate", str(learning_rate),
    ]

    if max_steps is not None:
        cmd += ["--max_steps", str(max_steps)]

    if num_epochs is not None:
        cmd += ["--num_epochs", str(num_epochs)]

    return cmd


smoke_ok = False
best_seq_len = None

for seq_len in [1024, 768, 512]:
    print(f"\nThu smoke test voi max_seq_length={seq_len}")

    cmd = build_train_cmd(
        output_dir=SMOKE_OUTPUT,
        adapter_dir=SMOKE_ADAPTER,
        max_seq_length=seq_len,
        max_steps=20,
    )

    result = run_cmd(cmd, check=False, capture=True)

    if result.returncode == 0:
        smoke_ok = True
        best_seq_len = seq_len
        print(f"Smoke test PASSED voi max_seq_length={seq_len}")
        break

    stderr_text = result.stderr or ""
    stdout_text = result.stdout or ""
    combined_text = stdout_text + "\n" + stderr_text

    print("Smoke test FAILED")
    print("\nSTDOUT tail:")
    print(stdout_text[-3000:])
    print("\nSTDERR tail:")
    print(stderr_text[-5000:])

    if is_code_error(combined_text):
        print("Day la loi code Python, khong phai OOM. Dung ngay.")
        sys.exit(1)

    if "token_type_ids is required" in combined_text:
        print("Van loi token_type_ids. Patch chua an vao model.")
        print("Hay gui 120 dong dau cua scripts/train_qlora_medgemma.py:")
        print(f"!nl -ba {SCRIPT_PATH} | sed -n '1,140p'")
        sys.exit(1)

    if is_oom_error(combined_text):
        print("CUDA OOM - thu max_seq_length nho hon...")
        continue

    print("Loi khong xac dinh, khong retry mu.")
    sys.exit(1)

if not smoke_ok:
    print("Smoke test FAILED o moi max_seq_length.")
    sys.exit(1)


# ══════════════════════════════════════════════════════════
# BUOC 12 — Train that
# ══════════════════════════════════════════════════════════

print_title("BUOC 12: Train that")

FULL_OUTPUT = "output/medisign_medgemma4b"
FULL_ADAPTER = f"{FULL_OUTPUT}/adapter"

train_seq_len = best_seq_len or 512
per_device_batch = 1
grad_accum = 16 if torch.cuda.device_count() >= 2 else 32

print(f"Train that dung max_seq_length={train_seq_len}")
print(
    "Full train config: "
    f"per_device_batch_size={per_device_batch}, "
    f"gradient_accumulation_steps={grad_accum}, "
    "num_epochs=3, learning_rate=3e-4"
)

cmd = build_train_cmd(
    output_dir=FULL_OUTPUT,
    adapter_dir=FULL_ADAPTER,
    max_seq_length=train_seq_len,
    per_device_batch_size=per_device_batch,
    gradient_accumulation_steps=grad_accum,
    learning_rate="3e-4",
    num_epochs=3,
)

result = run_cmd(cmd, check=False, capture=False)

if result.returncode != 0:
    print("Train that FAILED")
    sys.exit(1)

print("Train that hoan thanh!")


# ══════════════════════════════════════════════════════════
# BUOC 13 — Kiem tra adapter output
# ══════════════════════════════════════════════════════════

print_title("BUOC 13: Kiem tra adapter output")

if not os.path.exists(FULL_ADAPTER):
    print(f"Khong thay thu muc adapter: {FULL_ADAPTER}")
    sys.exit(1)

run_cmd(["ls", "-lh", FULL_ADAPTER], check=False)

required_files = [
    "adapter_config.json",
]

for fname in required_files:
    fpath = os.path.join(FULL_ADAPTER, fname)

    if os.path.exists(fpath):
        print(f"{fname} ton tai")
    else:
        print(f"Khong thay {fname} - kiem tra lai output")


# ══════════════════════════════════════════════════════════
# BUOC 14 — Zip adapter
# ══════════════════════════════════════════════════════════

print_title("BUOC 14: Zip adapter")

ZIP_PATH = "/kaggle/working/medisign_medgemma4b_adapter.zip"

if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)

run_cmd(
    ["zip", "-r", ZIP_PATH, FULL_ADAPTER],
    check=True,
)

size_mb = os.path.getsize(ZIP_PATH) / 1024**2

print(f"Adapter da zip: {ZIP_PATH} ({size_mb:.1f} MB)")


# ══════════════════════════════════════════════════════════
# BUOC 15 — Tom tat
# ══════════════════════════════════════════════════════════

print_title("HOAN THANH - Tom tat")

print(f"  Model         : {MODEL_ID}")
print(f"  GPU           : {torch.cuda.get_device_name(0)}")
print(f"  GPU count     : {torch.cuda.device_count()}")
print(f"  Smoke test    : PASSED")
print(f"  Train that    : 3 epochs")
print(f"  Max seq length: {train_seq_len}")
print(f"  Adapter output: {FULL_ADAPTER}")
print(f"  Adapter zip   : {ZIP_PATH} ({size_mb:.1f} MB)")
print("  -> Tai file zip tu Kaggle Output panel de dung offline")
print("═" * 60)
