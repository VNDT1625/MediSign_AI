# -*- coding: utf-8 -*-
"""Chuẩn hóa dữ liệu crawled từ Wikipedia."""
import json
import re

# Config
INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."
D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

def clean_text(text):
    """Làm sạch text."""
    if not text:
        return ""
    # Remove references like [1], [2]
    text = re.sub(r'\[\d+\]', '', text)
    # Remove [a], [b] references
    text = re.sub(r'\[[a-z]\]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_drug_data(input_file, output_file):
    """Chuẩn hóa dữ liệu thuốc."""
    print(f"Normalizing: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    normalized = []
    skipped = 0

    for item in data:
        # Extract drug name from question
        question = item.get('question', '').strip()
        answer = item.get('answer', '').strip()

        if not question or not answer:
            skipped += 1
            continue

        # Clean answer
        answer = clean_text(answer)

        # Add disclaimer if missing
        if '⚠️' not in answer:
            answer = answer.rstrip() + D

        # Create normalized record
        normalized.append({
            "instruction": INSTRUCTION,
            "input": question,
            "output": answer,
            "source": item.get('source', 'wikipedia')
        })

    print(f"  Processed: {len(data)} -> {len(normalized)} (skipped: {skipped})")

    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)

    return normalized

# Normalize Wikipedia drugs
input_file = r"C:\NDT\PJ\MediSign_AI\data\training_raw\wikipedia_drugs.json"
output_file = r"C:\NDT\PJ\MediSign_AI\data\training_raw\wikipedia_drugs_clean.json"

wiki_clean = normalize_drug_data(input_file, output_file)

# Show sample
print("\n=== Sample normalized data ===")
if wiki_clean:
    print(f"Instruction: {wiki_clean[0]['instruction'][:80]}...")
    print(f"Input: {wiki_clean[0]['input']}")
    print(f"Output: {wiki_clean[0]['output'][:150]}...")
    print(f"Source: {wiki_clean[0]['source']}")
