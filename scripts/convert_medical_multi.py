#!/usr/bin/env python3
"""
Script chạy song song 20 processes để dịch nhanh hơn
"""

import os
import json
import re
import time
import requests
import sys
import subprocess
from pathlib import Path

# Cấu hình
API_KEY = "sk-VIL4n0d8qRZHTp97kDyCAQ"
INPUT_DIR = r"C:\NDT\PJ\MediSign_AI\data\training_raw\Medical-Dialogue-Dataset-Chinese"
OUTPUT_DIR = r"C:\NDT\PJ\MediSign_AI\data\training_clean"

INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."

NUM_WORKERS = 20

def read_file_with_encoding(filepath):
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Không thể đọc file {filepath}")

def parse_dialogue(content, year):
    dialogues = []
    blocks = re.split(r'\nid=\d+', content)

    for block in blocks:
        if not block.strip() or len(block.strip()) < 20:
            continue

        disease_match = re.search(r'疾病[：:]\s*(.+?)(?:\n|$)', block)
        disease = disease_match.group(1).strip() if disease_match else ""

        desc_patterns = [
            r'病情描述[：:](.+?)(?:\n曾|$)',
            r'患病时长[：:](.+?)\n病情描述[：:](.+?)(?:\n曾|$)',
        ]
        description = ""
        for pattern in desc_patterns:
            match = re.search(pattern, block, re.DOTALL)
            if match:
                description = match.group(1).strip()
                break

        help_match = re.search(r'想得到怎样的帮助[：:]\s*(.+?)(?:\n所|$)', block, re.DOTALL)
        help_request = help_match.group(1).strip() if help_match else ""

        dialogue_match = re.search(r'Dialogue\s*\n(.+)', block, re.DOTALL)
        dialogue_text = dialogue_match.group(1).strip() if dialogue_match else ""

        doctor_responses = re.findall(r'医生[：:]\s*(.+?)(?:\n病人[：:]|\n*$)', dialogue_text, re.DOTALL)

        input_text = disease
        if description:
            input_text += f". {description}"
        if help_request:
            input_text += f" {help_request}"

        output_text = " ".join(doctor_responses) if doctor_responses else ""

        if input_text and output_text:
            dialogues.append({
                "original_input": input_text,
                "original_output": output_text,
                "year": year
            })

    return dialogues

def translate_text(text, max_retries=3):
    if not text or len(text.strip()) < 2:
        return text

    url = "https://api.blackbox.ai/v1/chat/completions"
    model = "blackboxai/qwen/qwen-turbo"

    prompt = f"""Bạn là một dịch giả y khoa chuyên nghiệp. Dịch ngắn gọn: {text}"""

    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000
                },
                timeout=20
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return text

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return text

    return text

def main(worker_id, total_workers):
    print(f"Worker {worker_id} bắt đầu...")

    # Read all data
    all_dialogues = []
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2018, 2019, 2020]

    for year in years:
        filepath = os.path.join(INPUT_DIR, f"{year}.txt")
        if os.path.exists(filepath):
            content = read_file_with_encoding(filepath)
            dialogues = parse_dialogue(content, year)
            all_dialogues.extend(dialogues)

    # Split data
    total = len(all_dialogues)
    chunk_size = total // total_workers
    start_idx = worker_id * chunk_size
    end_idx = start_idx + chunk_size if worker_id < total_workers - 1 else total

    print(f"Worker {worker_id}: xử lý records {start_idx} - {end_idx}")

    my_data = all_dialogues[start_idx:end_idx]
    translated = []

    for i, item in enumerate(my_data):
        if i % 50 == 0:
            print(f"Worker {worker_id}: {i}/{len(my_data)}")

        translated_input = translate_text(item['original_input'])
        translated_output = translate_text(item['original_output'])

        translated.append({
            "instruction": INSTRUCTION,
            "input": translated_input,
            "output": translated_output,
            "source": f"medical_dialogue_{item['year']}"
        })

        time.sleep(0.02)

    # Save
    output_file = os.path.join(OUTPUT_DIR, f"medical_dialogue_part_{worker_id}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    print(f"Worker {worker_id} hoàn thành! Lưu {len(translated)} records vào {output_file}")

if __name__ == "__main__":
    worker_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    total_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    main(worker_id, total_workers)
