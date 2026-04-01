"""
Extract Chinese Medical Dialogues từ raw .txt files
===================================================

Parse các file .txt chứa dialogues bác sĩ - bệnh nhân từ haodf.com

Usage:
    python extract_chinese_dialogues.py
"""

import os
import json
import re
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
# SCRIPT_DIR = packages/ai_training/scripts
# Go up: scripts -> ai_training -> packages -> root
ROOT = SCRIPT_DIR.parent.parent.parent
DATA_DIR = ROOT / "data" / "training_raw" / "Medical-Dialogue-Dataset-Chinese"
OUTPUT_FILE = DATA_DIR / "extracted_dialogues.json"

print(f"DEBUG: SCRIPT_DIR = {SCRIPT_DIR}")
print(f"DEBUG: ROOT = {ROOT}")
print(f"DEBUG: DATA_DIR = {DATA_DIR}")

# Files cần parse (encoding khác nhau)
FILES_CONFIG = [
    {"year": "2010", "encoding": "utf-8"},
    {"year": "2011", "encoding": "gb2312"},
    {"year": "2012", "encoding": "utf-8"},
    {"year": "2013", "encoding": "utf-8"},
    {"year": "2014", "encoding": "gb2312"},
    {"year": "2015", "encoding": "utf-8"},
    {"year": "2016", "encoding": "utf-8"},
    {"year": "2018", "encoding": "utf-8"},
    {"year": "2019", "encoding": "utf-8"},
    {"year": "2020", "encoding": "utf-8"},
]


def parse_dialogue(text):
    """Parse một dialogue từ text"""
    result = {}

    lines = text.strip().split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith('id='):
            result['id'] = line.replace('id=', '').strip()
        elif line.startswith('http'):
            result['url'] = line.strip()
        elif line == 'Doctor faculty':
            # Next line is hospital + department
            if i + 1 < len(lines):
                result['hospital_dept'] = lines[i + 1].strip()
            i += 1
        elif line == 'Description':
            # Parse description fields
            desc = {}
            i += 1
            while i < len(lines):
                desc_line = lines[i].strip()
                if desc_line == 'Dialogue':
                    break
                if '疾病：' in desc_line:
                    desc['disease'] = desc_line.replace('疾病：', '').strip()
                elif '病情描述' in desc_line:
                    # Get content until next field
                    j = i + 1
                    content = []
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if next_line.startswith('曾经') or next_line.startswith('想得到') or next_line == 'Dialogue':
                            break
                        if next_line:
                            content.append(next_line)
                        j += 1
                    if content:
                        desc['patient_description'] = ' '.join(content)
                    i = j - 1
                elif '曾经治疗' in desc_line:
                    j = i + 1
                    content = []
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if next_line.startswith('想得到') or next_line == 'Dialogue':
                            break
                        if next_line:
                            content.append(next_line)
                        j += 1
                    if content:
                        desc['previous_treatment'] = ' '.join(content)
                    i = j - 1
                elif '想得到' in desc_line:
                    j = i + 1
                    content = []
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if next_line == 'Dialogue':
                            break
                        if next_line:
                            content.append(next_line)
                        j += 1
                    if content:
                        desc['question'] = ' '.join(content)
                    i = j - 1

                i += 1

            if desc:
                result['description'] = desc

        elif line == 'Dialogue':
            # Parse dialogue lines
            dialogues = []
            i += 1
            while i < len(lines):
                d_line = lines[i].strip()
                if d_line.startswith('id=') or d_line == '':
                    break
                if d_line.startswith('医生：') or d_line.startswith('病人：'):
                    dialogues.append(d_line)
                elif d_line.startswith('医生：') is False and d_line.startswith('病人：') is False and d_line:
                    # Continuation of previous line
                    if dialogues:
                        dialogues[-1] += ' ' + d_line
                i += 1

            if dialogues:
                result['dialogue'] = dialogues

        i += 1

    return result


def extract_all_dialogues():
    """Extract tất cả dialogues từ các file"""
    all_dialogues = []
    total_count = 0

    for config in FILES_CONFIG:
        year = config["year"]
        encoding = config["encoding"]
        file_path = DATA_DIR / f"{year}.txt"

        print(f"📂 Đang xử lý {year}.txt ({encoding})...")

        if not file_path.exists():
            print(f"   ⚠️ File không tồn tại: {file_path}")
            continue

        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()

            # Split by id=
            parts = content.split('id=')
            print(f"   Tìm thấy {len(parts) - 1} dialogues")

            for idx, part in enumerate(parts[1:], 1):
                dialogue = parse_dialogue('id=' + part)
                if dialogue and 'description' in dialogue:
                    dialogue['year'] = year
                    dialogue['source'] = 'haodf'
                    all_dialogues.append(dialogue)
                    total_count += 1

            print(f"   ✅ Đã extract: {len([d for d in all_dialogues if d.get('year') == year])} dialogues")

        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
            continue

    return all_dialogues


def main():
    print("=" * 60)
    print("EXTRACT CHINESE MEDICAL DIALOGUES")
    print("=" * 60)
    print()

    # Extract
    dialogues = extract_all_dialogues()
    print(f"\n📊 Tổng dialogues extracted: {len(dialogues)}")

    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dialogues, f, ensure_ascii=False, indent=2)

    print(f"💾 Đã lưu: {OUTPUT_FILE}")

    # Show sample
    if dialogues:
        print("\n📝 Sample:")
        print(json.dumps(dialogues[0], ensure_ascii=False, indent=2)[:500])

    print("\n" + "=" * 60)
    print("✅ HOÀN TẤT!")
    print("=" * 60)


if __name__ == '__main__':
    main()
