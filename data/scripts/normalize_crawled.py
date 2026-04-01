# -*- coding: utf-8 -*-
"""Chuẩn hóa dữ liệu crawled mở rộng."""
import json
import re

INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."
D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[[a-z]\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_crawled_data(input_file, output_file):
    print(f"Normalizing: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    normalized = []
    skipped = 0

    for item in data:
        question = item.get('question', '').strip()
        answer = item.get('answer', '').strip()

        if not question or not answer or len(answer) < 50:
            skipped += 1
            continue

        answer = clean_text(answer)

        if '⚠️' not in answer:
            answer = answer.rstrip() + D

        normalized.append({
            "instruction": INSTRUCTION,
            "input": question,
            "output": answer,
            "source": item.get('source', 'crawled')
        })

    print(f"  Processed: {len(data)} -> {len(normalized)} (skipped: {skipped})")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)

    return normalized

# Normalize extended crawled data
input_file = r"C:\NDT\PJ\MediSign_AI\data\training_raw\crawled_extended.json"
output_file = r"C:\NDT\PJ\MediSign_AI\data\training_raw\crawled_extended_clean.json"

crawled_clean = normalize_crawled_data(input_file, output_file)

print(f"\n✓ Normalized {len(crawled_clean)} records")
