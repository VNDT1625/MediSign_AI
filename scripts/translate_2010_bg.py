import os
import json
import re
import time
import requests
import concurrent.futures

API_KEY = "sk-VIL4n0d8qRZHTp97kDyCAQ"
INPUT_FILE = r"C:\NDT\PJ\MediSign_AI\data\training_raw\Medical-Dialogue-Dataset-Chinese\2010.txt"
OUTPUT_FILE = r"C:\NDT\PJ\MediSign_AI\data\training_clean\qwen_72b\2010_vi.json"
INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."
MAX_WORKERS = 10

def read_file_with_encoding(filepath):
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Không thể đọc file {filepath}")

def parse_dialogue(content):
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
        if description: input_text += f" {description}"
        if help_request: input_text += f" {help_request}"
            
        output_text = " ".join(doctor_responses) if doctor_responses else ""
        
        if input_text and output_text:
            dialogues.append({
                "original_input": input_text.strip(),
                "original_output": output_text.strip()
            })
    return dialogues

def translate_text(text, max_retries=3):
    if not text or len(text.strip()) < 2: return text
    url = "https://api.blackbox.ai/v1/chat/completions"
    model = "blackboxai/qwen/qwen-turbo"
    prompt = f"Bạn là một dịch giả y khoa chuyên nghiệp. Hãy dịch đoạn văn bản dưới đây từ tiếng Trung Quốc sang tiếng Việt (có dấu). Đảm bảo dịch chính xác về nghĩa, sử dụng thuật ngữ y khoa chuẩn. Chỉ trả lời bằng bản dịch tiếng Việt, không giải thích thêm:\n\n{text}"
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 1500}, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                time.sleep(2)
        except:
            time.sleep(2)
    return text

def translate_item(item):
    return {
        "instruction": INSTRUCTION,
        "input": translate_text(item['original_input']),
        "output": translate_text(item['original_output']),
        "source": "medical_dialogue_2010"
    }

def main():
    print("Reading file...")
    content = read_file_with_encoding(INPUT_FILE)
    all_dialogues = parse_dialogue(content)
    print(f"Found {len(all_dialogues)} records.")
    
    translated_data = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                translated_data = json.load(f)
            print(f"Resuming... Loaded {len(translated_data)} already translated.")
        except:
            pass
            
    pending = all_dialogues[len(translated_data):]
    print(f"Remaining to translate: {len(pending)}")
    
    for i in range(0, len(pending), 50):
        chunk = pending[i:i+50]
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(translate_item, chunk))
        translated_data.extend(results)
        
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        print(f"Progress: {len(translated_data)} / {len(all_dialogues)}")

if __name__ == "__main__":
    main()
