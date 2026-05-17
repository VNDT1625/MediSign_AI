# QLoRA Training — MedGemma 4B Medical Adapter

This guide covers running `scripts/train_qlora_medgemma.py` (Task 1.5) on
the three environments the MediSign team is targeting for the 5-day MVP:

* Kaggle (free 2× T4, 16 GB each) — recommended for the first full pass.
* Vast.ai / RunPod (RTX 4090, 24 GB) — recommended for re-runs / longer training.
* Local workstation with a single RTX 4090 (16 GB+).

Inputs and outputs are identical on every environment:

| Path | Purpose |
| ---- | ------- |
| `data/training_clean/medgemma_4b/train.jsonl` | 14 756 chat-templated training records (Task 1.4 output). |
| `data/training_clean/medgemma_4b/eval.jsonl`  | 1 640 eval records. |
| `output/medisign_medgemma4b/checkpoints/` | Step-checkpointed training state (auto-rotated, max 3). |
| `output/medisign_medgemma4b/adapter/` | Final LoRA adapter saved with `save_pretrained` (Requirement 1.8). |

## Prerequisite: accept the MedGemma terms

`google/medgemma-1.5-4b-it` is a gated model. Before the script can download
the weights you must:

1. Sign in to <https://huggingface.co/google/medgemma-1.5-4b-it> and accept
   the MedGemma Health AI Developer Foundations terms.
2. On the host machine, run:

   ```bash
   huggingface-cli login
   ```

   Paste an access token with `read` scope.

If you skip this step the script fails with `OSError: ... 401` during
model load.

---

## Run on Kaggle (free 2× T4)

Kaggle gives you 30 hours/week of free 2× T4 (16 GB × 2 = 32 GB
aggregate). One full 3-epoch pass over 14 756 records takes ~4-5 hours
on this hardware.

1. Push this repo to a private GitHub repo, then create a **Kaggle
   Dataset** that mirrors it (one-time upload). This avoids re-uploading
   on every notebook run.

2. Create a new Kaggle Notebook with **Accelerator → GPU T4 ×2** and
   **Internet → On**.

3. Paste the following cells:

   ```python
   # Cell 1 — install training deps
   !pip install -q -r /kaggle/input/medisign-ai-repo/scripts/requirements_train.txt

   # Cell 2 — authenticate to HF (use Kaggle Secrets to store HF_TOKEN)
   from kaggle_secrets import UserSecretsClient
   import os
   os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")

   # Cell 3 — copy the repo to a writable location and run training
   !cp -r /kaggle/input/medisign-ai-repo /kaggle/working/repo
   %cd /kaggle/working/repo
   !python scripts/train_qlora_medgemma.py
   ```

4. Download the adapter once training finishes:

   ```python
   # Cell 4 — zip and download
   !cd /kaggle/working/repo/output/medisign_medgemma4b && zip -r adapter.zip adapter
   from IPython.display import FileLink
   FileLink("/kaggle/working/repo/output/medisign_medgemma4b/adapter.zip")
   ```

> Tip: Kaggle sessions time out after 9 hours of inactivity. The script
> writes a checkpoint every 500 steps, so if a session is interrupted
> you can resume in a new notebook with
> `python scripts/train_qlora_medgemma.py --resume_from_checkpoint
> output/medisign_medgemma4b/checkpoints/checkpoint-XXXX`.

---

## Run on Vast.ai / RunPod (RTX 4090)

Recommended template: `pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime`
on an RTX 4090 (24 GB) instance. 3 epochs take ~3 hours on this card.

```bash
# 1. SSH into the rented instance, e.g.
ssh -p 12345 root@ssh4.vast.ai

# 2. Clone the repo and install deps
git clone https://github.com/<your-org>/MediSign_AI.git
cd MediSign_AI
pip install -r scripts/requirements_train.txt

# 3. Authenticate to HF
huggingface-cli login

# 4. Run training
python scripts/train_qlora_medgemma.py

# 5. From your local machine, scp the adapter back when done
scp -P 12345 -r root@ssh4.vast.ai:/root/MediSign_AI/output/medisign_medgemma4b/adapter ./output/medisign_medgemma4b/
```

For RunPod the workflow is identical — pick a Pod template with at
least 24 GB of VRAM and follow the same five steps inside the Pod's
terminal.

---

## Run locally (single RTX 4090, 16 GB+)

```bash
# 1. From the repo root
pip install -r scripts/requirements_train.txt

# 2. Authenticate
huggingface-cli login

# 3. Sanity-check the config without GPU work
python scripts/train_qlora_medgemma_smoke_test.py

# 4. Train
python scripts/train_qlora_medgemma.py

# 5. (Optional) cap training for a fast smoke run
python scripts/train_qlora_medgemma.py --max_steps 5
```

The final adapter ends up in `output/medisign_medgemma4b/adapter/`.
This repo now uses rank 32 LoRA across attention and MLP projections
(`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`,
`down_proj`) with `packing=True`, `weight_decay=0.01`,
`neftune_noise_alpha=5`, and `warmup_ratio=0.05`. The adapter is larger
than the old attention-only setup, so verify the zipped artifact size
before release.

---

## CLI reference

```text
python scripts/train_qlora_medgemma.py [OPTIONS]

  --model_id TEXT                   default: google/medgemma-1.5-4b-it
  --train_file PATH                 default: data/training_clean/medgemma_4b/train.jsonl
  --eval_file PATH                  default: data/training_clean/medgemma_4b/eval.jsonl
  --output_dir PATH                 default: output/medisign_medgemma4b/checkpoints
  --adapter_dir PATH                default: output/medisign_medgemma4b/adapter
  --num_epochs FLOAT                default: 3
  --max_seq_length INT              default: 2048
  --per_device_batch_size INT       default: 4
  --gradient_accumulation_steps INT default: 4
  --learning_rate FLOAT             default: 2e-4
  --max_steps INT                   default: -1 (unlimited)
  --resume_from_checkpoint PATH     default: None
```
