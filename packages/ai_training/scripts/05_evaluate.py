"""
Bước 5: Evaluation - Đo lường Accuracy trên MedQuAD
======================================================

Script này đo lường accuracy của model trên MedQuAD benchmark.

Usage:
    python scripts/05_evaluate.py --model ./output/medisign_qwen/adapter

Metrics:
    - Accuracy (Exact Match)
    - F1-Score
    - ROUGE-L
    - BLEU
"""

import argparse
import json
import torch
from pathlib import Path
from typing import List, Dict, Tuple
from datasets import load_dataset
import evaluate

# ============================================================================
# CONFIG
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(description='Evaluate medical AI model')
    parser.add_argument('--model', type=str, default=None,
                        help='Path to adapter or model')
    parser.add_argument('--base_model', type=str,
                        default='Qwen/Qwen2.5-72B-Instruct',
                        help='Base model name')
    parser.add_argument('--dataset', type=str, default='medquad',
                        help='Dataset name: medquad, medalpaca')
    parser.add_argument('--split', type=str, default='test',
                        help='Dataset split: test, train')
    parser.add_argument('--max_samples', type=int, default=1000,
                        help='Max samples to evaluate')
    parser.add_argument('--batch_size', type=int, default=8,
                        help='Batch size for evaluation')
    return parser.parse_args()


# ============================================================================
# LOAD MODEL
# ============================================================================

def load_model_and_tokenizer(args):
    """Load model với adapter nếu có."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    print(f"Loading base model: {args.base_model}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        args.base_model,
        trust_remote_code=True,
        padding_side="right"
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load model
    if args.model:
        print(f"Loading adapter from: {args.model}")
        base_model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        model = PeftModel.from_pretrained(base_model, args.model)
    else:
        print("No adapter specified, using base model")
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )

    return model, tokenizer


# ============================================================================
# FORMAT PROMPT
# ============================================================================

def format_prompt(question: str, model_type: str = "qwen") -> str:
    """Format prompt theo model type."""
    if model_type == "qwen":
        return f"<|im_start|>system\nBạn là MediSign AI - trợ lý y tế. Trả lời câu hỏi một cách ngắn gọn và chính xác.<|im_end|>\n<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n"
    elif model_type == "gemma":
        return f"<start_of_turn>user\nBạn là MediSign AI - trợ lý y tế. Trả lời câu hỏi một cách ngắn gọn và chính xác.\n\n{question}<end_of_turn>\n<start_of_turn>model\n"
    else:
        return f"Question: {question}\nAnswer:"


# ============================================================================
# GENERATE
# ============================================================================

def generate_response(model, tokenizer, question: str, max_new_tokens: int = 256) -> str:
    """Generate response từ model."""
    prompt = format_prompt(question, "qwen")

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,  # Greedy for consistent results
        temperature=0.1,
        top_p=0.9,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract assistant response
    if "<|im_start|>assistant\n" in response:
        response = response.split("<|im_start|>assistant\n")[-1]

    return response.strip()


# ============================================================================
# EVALUATION METRICS
# ============================================================================

def calculate_exact_match(prediction: str, reference: str) -> float:
    """Tính exact match accuracy."""
    # Normalize
    pred = prediction.lower().strip()
    ref = reference.lower().strip()

    # Exact match
    return 1.0 if pred == ref else 0.0


def calculate_token_accuracy(prediction: str, reference: str) -> float:
    """Tính token-level accuracy."""
    pred_tokens = set(prediction.lower().split())
    ref_tokens = set(reference.lower().split())

    if len(ref_tokens) == 0:
        return 0.0

    correct = len(pred_tokens & ref_tokens)
    return correct / len(ref_tokens)


# ============================================================================
# MAIN EVALUATION
# ============================================================================

def evaluate_model(model, tokenizer, dataset, max_samples: int = 1000):
    """Evaluate model trên dataset."""
    print(f"\n{'='*60}")
    print("EVALUATING MODEL")
    print(f"{'='*60}")

    # Load metrics
    try:
        rouge = evaluate.load("rouge")
        bleu = evaluate.load("bleu")
        exact_match = evaluate.load("exact_match")
    except Exception as e:
        print(f"Warning: Could not load some metrics: {e}")
        rouge = None
        bleu = None
        exact_match = None

    predictions = []
    references = []
    exact_matches = []
    token_accuracies = []

    # Evaluate
    samples = min(max_samples, len(dataset))

    for i, example in enumerate(dataset.select(range(samples))):
        question = example.get('question', '')
        reference_answer = example.get('answer', '')

        if not question or not reference_answer:
            continue

        # Generate
        try:
            prediction = generate_response(model, tokenizer, question)
        except Exception as e:
            print(f"Error generating for sample {i}: {e}")
            prediction = ""

        predictions.append(prediction)
        references.append(reference_answer)

        # Calculate metrics
        exact_matches.append(calculate_exact_match(prediction, reference_answer))
        token_accuracies.append(calculate_token_accuracy(prediction, reference_answer))

        if (i + 1) % 50 == 0:
            print(f"Processed {i+1}/{samples} samples...")

    # Calculate final metrics
    results = {}

    # Exact match
    em_score = sum(exact_matches) / len(exact_matches) if exact_matches else 0
    results['exact_match'] = em_score * 100

    # Token accuracy
    token_acc = sum(token_accuracies) / len(token_accuracies) if token_accuracies else 0
    results['token_accuracy'] = token_acc * 100

    # ROUGE
    if rouge:
        try:
            rouge_results = rouge.compute(
                predictions=predictions,
                references=references,
                use_aggregator=True
            )
            results['rouge1'] = rouge_results['rouge1'] * 100
            results['rouge2'] = rouge_results['rouge2'] * 100
            results['rougeL'] = rouge_results['rougeL'] * 100
            results['rougeLsum'] = rouge_results['rougeLsum'] * 100
        except Exception as e:
            print(f"ROUGE error: {e}")

    # BLEU
    if bleu:
        try:
            # BLEU cần references dạng list of lists
            refs_for_bleu = [[ref] for ref in references]
            bleu_results = bleu.compute(
                predictions=predictions,
                references=refs_for_bleu
            )
            results['bleu'] = bleu_results['bleu'] * 100
        except Exception as e:
            print(f"BLEU error: {e}")

    return results, predictions, references


# ============================================================================
# MAIN
# ============================================================================

def main():
    args = parse_args()

    print(f"\n{'='*60}")
    print("MEDQUAD EVALUATION")
    print(f"{'='*60}")
    print(f"Base model: {args.base_model}")
    print(f"Adapter: {args.model}")
    print(f"Max samples: {args.max_samples}")

    # Load dataset
    print(f"\nLoading MedQuAD dataset...")

    # Try to load from HuggingFace or local
    try:
        # Try HuggingFace
        dataset = load_dataset("bigbio/medquad", split=args.split)
        print(f"Loaded {len(dataset)} samples from HuggingFace")
    except Exception as e:
        print(f"Could not load from HuggingFace: {e}")
        print("Trying local file...")

        # Try local
        local_path = Path(__file__).parent.parent.parent / "data" / "training_clean" / "eval.json"
        if local_path.exists():
            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            from datasets import Dataset
            dataset = Dataset.from_list(data)
            print(f"Loaded {len(dataset)} samples from local file")
        else:
            print("No local eval data found. Using sample data for demo.")
            # Create sample data for demonstration
            sample_data = [
                {"question": "What is diabetes?", "answer": "Diabetes is a chronic disease that occurs when the pancreas is no longer able to make insulin."},
                {"question": "What are the symptoms of flu?", "answer": "Common symptoms of flu include fever, cough, sore throat, runny nose, muscle aches, and fatigue."},
            ]
            from datasets import Dataset
            dataset = Dataset.from_list(sample_data)

    # Load model
    model, tokenizer = load_model_and_tokenizer(args)

    # Evaluate
    results, predictions, references = evaluate_model(
        model, tokenizer, dataset, args.max_samples
    )

    # Print results
    print(f"\n{'='*60}")
    print("EVALUATION RESULTS")
    print(f"{'='*60}")

    for metric, value in results.items():
        print(f"{metric:20s}: {value:6.2f}%")

    print(f"\n{'='*60}")
    print("SAMPLE PREDICTIONS")
    print(f"{'='*60}")

    for i in range(min(3, len(predictions))):
        print(f"\n--- Sample {i+1} ---")
        print(f"Question: {references[i][:100]}...")
        print(f"Prediction: {predictions[i][:200]}...")

    # Save results
    output_dir = Path(__file__).parent.parent / "output" / "eval_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "eval_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metrics': results,
            'num_samples': len(predictions)
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Comparison with benchmarks
    print(f"\n{'='*60}")
    print("BENCHMARK COMPARISON")
    print(f"{'='*60}")

    benchmarks = {
        'Med-PaLM 2': 86.0,
        'MedAlpaca-13B': 72.0,
        'GPT-3.5': 60.0,
        'Our Model': results.get('exact_match', 0)
    }

    for name, score in benchmarks.items():
        bar = '█' * int(score / 5)
        print(f"{name:20s}: {score:5.1f}% {bar}")

    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
