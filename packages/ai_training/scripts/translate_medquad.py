"""
Script dịch MedQuAD từ tiếng Anh sang tiếng Việt bằng Gemini AI
=============================================================

Usage:
    python translate_medquad.py --api_key "YOUR_GEMINI_API_KEY"
    python translate_medquad.py --api_key "YOUR_GEMINI_API_KEY" --limit 100  # Test với 100 câu đầu
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import time
import re

# Gemini imports
import google.generativeai as genai

# Paths
SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent.parent
MEDQUAD_DIR = ROOT / "data" / "training_raw" / "MedQuAD"
OUTPUT_DIR = ROOT / "data" / "training_clean" / "medquad_vietnamese"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_medquad_xml(file_path):
    """Parse một file XML của MedQuAD"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        qa_pairs = []

        # Lấy source và url
        source = root.get('source', 'Unknown')
        url = root.get('url', '')

        # Lấy Focus (chủ đề)
        focus = root.find('Focus')
        topic = focus.text if focus is not None else ''

        # Tìm tất cả QAPair
        qa_pairs_elem = root.find('QAPairs')
        if qa_pairs_elem is not None:
            for qa_pair in qa_pairs_elem.findall('QAPair'):
                question_elem = qa_pair.find('Question')
                answer_elem = qa_pair.find('Answer')

                if question_elem is not None and answer_elem is not None:
                    question = question_elem.text.strip() if question_elem.text else ''
                    answer = answer_elem.text.strip() if answer_elem.text else ''

                    # Lấy question type
                    qtype = question_elem.get('qtype', 'unknown')

                    if question and answer:
                        qa_pairs.append({
                            'question': question,
                            'answer': answer,
                            'qtype': qtype,
                            'topic': topic,
                            'source': source,
                            'url': url
                        })

        return qa_pairs

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []


def get_all_medquad_qa():
    """Đọc tất cả Q&A từ MedQuAD"""
    all_qa = []

    # Các folder trong MedQuAD
    folders = [
        "1_CancerGov_QA",
        "2_GARD_QA",
        "3_GHR_QA",
        "4_MPlus_Health_Topics_QA",
        "5_NIDDK_QA",
        "6_NINDS_QA",
        "7_SeniorHealth_QA",
        "8_NHLBI_QA_XML",
        "9_CDC_QA",
        "10_MPlus_ADAM_QA",
        "11_MPlusDrugs_QA",
        "12_MPlusHerbsSupplements_QA"
    ]

    for folder in folders:
        folder_path = MEDQUAD_DIR / folder
        if not folder_path.exists():
            continue

        xml_files = list(folder_path.glob("*.xml"))
        print(f"📁 {folder}: {len(xml_files)} files")

        for xml_file in xml_files:
            qa_pairs = parse_medquad_xml(xml_file)
            all_qa.extend(qa_pairs)

    return all_qa


def translate_batch(qa_batch, model, language='Vietnamese'):
    """Dịch một batch Q&A sang tiếng Việt"""
    prompt = f"""Bạn là chuyên gia dịch thuật y khoa. Dịch các câu hỏi và câu trả lời sau từ tiếng Anh sang {language}.

Quy tắc:
1. Giữ nguyên định dạng bullet points (-, •)
2. Giữ nguyên các thuật ngữ y khoa tiếng Anh nếu chưa có thuật ngữ tiếng Việt phổ biến
3. Dịch tự nhiên, dễ hiểu
4. KHÔNG thay đổi nội dung y khoa

Dưới đây là danh sách các cặp câu hỏi-trả lời (mỗi cặp cách nhau bởi ---):

{qa_batch}

Trả về JSON array với format:
[
  {{"question_vi": "câu hỏi tiếng Việt", "answer_vi": "câu trả lời tiếng Việt"}},
  ...
]

CHỈ trả về JSON, KHÔNG giải thích gì thêm:"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error translating: {e}")
        return None


def clean_json_response(text):
    """Làm sạch response JSON"""
    # Remove markdown code blocks if present
    text = re.sub(r'^```json\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text)

    # Try to find JSON array in response
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return match.group(0)

    return text


def main():
    parser = argparse.ArgumentParser(description='Dịch MedQuAD sang tiếng Việt bằng Gemini')
    parser.add_argument('--api_key', required=True, help='Gemini API Key')
    parser.add_argument('--limit', type=int, default=0, help='Số lượng Q&A tối đa (0 = tất cả)')
    parser.add_argument('--batch_size', type=int, default=10, help='Số Q&A mỗi batch')
    parser.add_argument('--resume', action='store_true', help='Tiếp tục từ file đã lưu')
    args = parser.parse_args()

    # Configure Gemini
    genai.configure(api_key=args.api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    print(f"\n{'='*60}")
    print("DỊCH MEDQUAD SANG TIẾNG VIỆT")
    print(f"{'='*60}\n")

    # Check for resume
    output_file = OUTPUT_DIR / "translated.json"
    if args.resume and output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            translated_data = json.load(f)
        print(f"✅ Resumed with {len(translated_data)} translated items")
        start_index = len(translated_data)
    else:
        translated_data = []
        start_index = 0

    # Get all Q&A if not already loaded
    if not hasattr(main, 'all_qa'):
        print("📖 Đọc dữ liệu MedQuAD...")
        main.all_qa = get_all_medquad_qa()
        print(f"📊 Tổng cộng: {len(main.all_qa)} Q&A pairs\n")

    all_qa = main.all_qa

    # Limit if specified
    if args.limit > 0:
        all_qa = all_qa[:args.limit]
        print(f"📊 Giới hạn: {len(all_qa)} Q&A pairs\n")

    # Translate in batches
    total = len(all_qa)
    success_count = len(translated_data)

    for i in range(start_index, total, args.batch_size):
        batch = all_qa[i:i + args.batch_size]

        # Prepare batch text
        batch_text = ""
        for idx, qa in enumerate(batch):
            batch_text += f"Q{idx+1}:\nQuestion: {qa['question']}\nAnswer: {qa['answer']}\n---\n"

        print(f"🔄 Dịch batch {i//args.batch_size + 1}/{(total-1)//args.batch_size + 1} ({i+1}-{min(i+args.batch_size, total)}/{total})...")

        # Translate
        response_text = translate_batch(batch_text, model)

        if response_text:
            try:
                # Clean and parse JSON
                clean_text = clean_json_response(response_text)
                batch_translated = json.loads(clean_text)

                # Add to results
                for idx, translated in enumerate(batch_translated):
                    if i + idx < len(all_qa):
                        original = all_qa[i + idx]
                        translated_data.append({
                            'question_en': original['question'],
                            'answer_en': original['answer'],
                            'question_vi': translated.get('question_vi', ''),
                            'answer_vi': translated.get('answer_vi', ''),
                            'topic': original.get('topic', ''),
                            'source': original.get('source', ''),
                            'qtype': original.get('qtype', '')
                        })

                success_count += len(batch_translated)
                print(f"   ✅ Đã dịch: {success_count}/{total}")

                # Save progress
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(translated_data, f, ensure_ascii=False, indent=2)

                # Sleep to avoid rate limit
                time.sleep(1)

            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parse error: {e}")
                time.sleep(3)
        else:
            print(f"   ❌ Translation failed")
            time.sleep(3)

    print(f"\n{'='*60}")
    print(f"✅ HOÀN TẤT!")
    print(f"📊 Đã dịch: {len(translated_data)} Q&A")
    print(f"💾 Lưu tại: {output_file}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
