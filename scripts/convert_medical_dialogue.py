#!/usr/bin/env python3
"""
Script chuyển đổi dữ liệu Medical Dialogue (2010-2020) sang JSON
Sử dụng Blackbox AI API để dịch từ tiếng Trung sang tiếng Việt
"""

import os
import json
import re
import time
import requests
from pathlib import Path

# Cấu hình
API_KEY = "sk-VIL4n0d8qRZHTp97kDyCAQ"
INPUT_DIR = r"C:\NDT\PJ\MediSign_AI\data\training_raw\Medical-Dialogue-Dataset-Chinese"
OUTPUT_FILE = r"C:\NDT\PJ\MediSign_AI\data\training_clean\medical_dialogue_2010_2020.json"

# Instruction template
INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."

def read_file_with_encoding(filepath):
    """Đọc file với nhiều encoding"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Không thể đọc file {filepath}")

def parse_dialogue(content, year):
    """Parse nội dung file thành danh sách các hội thoại"""
    dialogues = []

    # Split by id=X pattern
    blocks = re.split(r'\nid=\d+', content)

    for block in blocks:
        if not block.strip() or len(block.strip()) < 20:
            continue

        # Extract URL
        url_match = re.search(r'(https?://[^\s]+)', block)
        url = url_match.group(1) if url_match else ""

        # Extract doctor info
        doctor_match = re.search(r'Doctor faculty\s*\n(.+)', block)
        doctor_info = doctor_match.group(1).strip() if doctor_match else ""

        # Extract disease
        disease_match = re.search(r'疾病[：:]\s*(.+?)(?:\n|$)', block)
        disease = disease_match.group(1).strip() if disease_match else ""

        # Extract description
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

        # Extract treatment info
        treatment_match = re.search(r'曾经治疗情况和效果[：:]\s*(.+?)(?:\n想|$)', block, re.DOTALL)
        treatment = treatment_match.group(1).strip() if treatment_match else ""

        # Extract help request
        help_match = re.search(r'想得到怎样的帮助[：:]\s*(.+?)(?:\n所|$)', block, re.DOTALL)
        help_request = help_match.group(1).strip() if help_match else ""

        # Extract dialogue
        dialogue_match = re.search(r'Dialogue\s*\n(.+)', block, re.DOTALL)
        dialogue_text = dialogue_match.group(1).strip() if dialogue_match else ""

        # Parse doctor and patient messages
        doctor_responses = re.findall(r'医生[：:]\s*(.+?)(?:\n病人[：:]|\n*$)', dialogue_text, re.DOTALL)
        patient_questions = re.findall(r'病人[：:]\s*(.+?)(?:\n医生[：:]|\n*$)', dialogue_text, re.DOTALL)

        # Create input (combination of disease + description + questions)
        input_text = disease
        if description:
            input_text += f". {description}"
        if help_request:
            input_text += f" {help_request}"

        # Create output (doctor's response)
        output_text = " ".join(doctor_responses) if doctor_responses else ""

        if input_text and output_text:
            dialogues.append({
                "original_input": input_text,
                "original_output": output_text,
                "doctor_info": doctor_info,
                "year": year
            })

    return dialogues

def translate_text(text, max_retries=3):
    """Gọi Blackbox API để dịch text từ Trung sang Việt"""
    if not text or len(text.strip()) < 2:
        return text

    url = "https://api.blackbox.ai/v1/chat/completions"

    # Use a fast and cheap model for translation
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
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2000
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"  Lỗi API: {response.status_code} - {response.text[:100]}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return text

        except Exception as e:
            print(f"  Lỗi khi dịch: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return text

    return text

def translate_batch(items, batch_size=10):
    """Dịch một batch các items"""
    results = []
    total = len(items)

    for i, item in enumerate(items):
        print(f"  Đang dịch {i+1}/{total}...")

        # Translate input
        translated_input = translate_text(item['original_input'])

        # Translate output
        translated_output = translate_text(item['original_output'])

        results.append({
            "instruction": INSTRUCTION,
            "input": translated_input,
            "output": translated_output,
            "source": f"medical_dialogue_{item['year']}"
        })

        # Rate limiting
        time.sleep(0.1)  # Reduced delay for faster processing

    return results

def main():
    print("=== Bắt đầu chuyển đổi dữ liệu Medical Dialogue ===\n")

    # Step 1: Read and parse all files
    all_dialogues = []
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]

    for year in years:
        filepath = os.path.join(INPUT_DIR, f"{year}.txt")
        if os.path.exists(filepath):
            print(f"Đọc file {year}.txt...")
            content = read_file_with_encoding(filepath)
            dialogues = parse_dialogue(content, year)
            print(f"  Tìm thấy {len(dialogues)} hội thoại")
            all_dialogues.extend(dialogues)
        else:
            print(f"File {year}.txt không tồn tại, bỏ qua")

    print(f"\nTổng cộng: {len(all_dialogues)} hội thoại\n")

    # Step 2: Translate to Vietnamese
    print("=== Bắt đầu dịch sang tiếng Việt ===\n")

    # Translate all records
    max_records = len(all_dialogues)  # No limit
    sample_dialogues = all_dialogues
    print(f"Sẽ dịch {len(sample_dialogues)} records (tất cả)")

    translated_data = translate_batch(sample_dialogues)

    # Step 3: Save to JSON
    print(f"\n=== Lưu file JSON ===")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    print(f"Đã lưu {len(translated_data)} records vào {OUTPUT_FILE}")

    # Show sample
    if translated_data:
        print("\n=== Sample (3 records đầu tiên) ===")
        for i, item in enumerate(translated_data[:3]):
            print(f"\n--- Record {i+1} ---")
            print(f"Input: {item['input'][:200]}...")
            print(f"Output: {item['output'][:200]}...")

if __name__ == "__main__":
    main()
