#!/usr/bin/env python3
"""
Script dịch tuần tự với progress update và auto-save
"""

import os
import json
import re
import time
import requests
from pathlib import Path

API_KEY = "sk-VIL4n0d8qRZHTp97kDyCAQ"
INPUT_DIR = r"C:\NDT\PJ\MediSign_AI\data\training_raw\Medical-Dialogue-Dataset-Chinese"
OUTPUT_FILE = r"C:\NDT\PJ\MediSign_AI\data\training_clean\medical_dialogue_2010_2020.json"
CHECKPOINT_FILE = r"C:\NDT\PJ\MediSign_AI\data\training_clean\medical_dialogue_checkpoint.json"

INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."

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

def translate_text(text, max_retries=5):
    if not text or len(text.strip()) < 2:
        return text

    url = "https://api.blackbox.ai/v1/chat/completions"
    model = "blackboxai/qwen/qwen-turbo"

    prompt = f"""Bạn là một dịch giả y khoa chuyên nghiệp. Hãy dịch đoạn văn bản dưới đây từ tiếng Trung Quốc sang tiếng Việt (có dấu). Đảm bảo:
1. Dịch chính xác về nghĩa
2. Sử dụng thuật ngữ y khoa tiếng Việt chuẩn
3. Giữ nguyên ý nghĩa y khoa

Văn bản cần dịch:
{text}

Chỉ trả lời bằng bản dịch tiếng Việt, không giải thích thêm:"""

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
                    "max_tokens": 2000
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            elif response.status_code == 429:
                # Rate limit - wait longer
                print(f"  Rate limit, waiting...")
                time.sleep(10)
                continue
            else:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return text

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return text

    return text

def save_checkpoint(data, checkpoint_file):
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("=== Bắt đầu chuyển đổi dữ liệu Medical Dialogue ===\n")

    # Load checkpoint if exists
    start_idx = 0
    translated_data = []

    if os.path.exists(CHECKPOINT_FILE):
        print("Tìm thấy checkpoint, tiếp tục...")
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            translated_data = json.load(f)
        start_idx = len(translated_data)
        print(f"Bắt đầu từ record {start_idx}\n")

    # Read and parse all files
    all_dialogues = []
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2018, 2019, 2020]

    for year in years:
        filepath = os.path.join(INPUT_DIR, f"{year}.txt")
        if os.path.exists(filepath):
            print(f"Đọc file {year}.txt...")
            content = read_file_with_encoding(filepath)
            dialogues = parse_dialogue(content, year)
            print(f"  Tìm thấy {len(dialogues)} hội thoại")
            all_dialogues.extend(dialogues)

    print(f"\nTổng cộng: {len(all_dialogues)} hội thoại\n")
    print(f"=== Bắt đầu dịch từ record {start_idx} ===\n")

    total = len(all_dialogues)

    # Translate from start_idx
    for i in range(start_idx, total):
        if i % 100 == 0:
            print(f"  Đang dịch {i+1}/{total}...")
            # Auto-save every 100
            save_checkpoint(translated_data, CHECKPOINT_FILE)

        item = all_dialogues[i]

        translated_input = translate_text(item['original_input'])
        translated_output = translate_text(item['original_output'])

        translated_data.append({
            "instruction": INSTRUCTION,
            "input": translated_input,
            "output": translated_output,
            "source": f"medical_dialogue_{item['year']}"
        })

        # Small delay to avoid rate limit
        time.sleep(0.05)

    # Final save
    print(f"\n=== Lưu file JSON ===")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    print(f"Đã lưu {len(translated_data)} records vào {OUTPUT_FILE}")

    # Remove checkpoint
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)

if __name__ == "__main__":
    main()
