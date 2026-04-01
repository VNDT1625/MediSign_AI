import json
import time
import os
import sys

try:
    from deep_translator import GoogleTranslator
    from tqdm import tqdm
except ImportError:
    print("Please install required libraries: pip install deep-translator tqdm")
    sys.exit(1)

INSTRUCTION_TEXT = "Bạn là MediSign AI, một trợ lý y tế thông minh. Nhiệm vụ của bạn là cung cấp thông tin và lời khuyên y tế dựa trên các triệu chứng hoặc câu hỏi của người dùng. Tuy nhiên, bạn phải luôn lưu ý rằng thông tin bạn cung cấp chỉ mang tính chất tham khảo và không thay thế cho chẩn đoán chuyên môn của bác sĩ. Nếu không chắc chắn, hãy khuyên người dùng đến gặp bác sĩ để được kiểm tra chính xác. \n\nLưu ý quan trọng: Dưới mỗi câu trả lời, hãy luôn thêm dòng chữ: \"Lời khuyên chỉ mang tính chất tham khảo, vui lòng đến gặp bác sĩ để được tư vấn chính xác nhất.\""

DISCLAIMER_TEXT = "\n\nLời khuyên chỉ mang tính chất tham khảo, vui lòng đến gặp bác sĩ để được tư vấn chính xác nhất."

def chunk_text(text, max_length=4500):
    """Splits text into chunks to respect translation API limits."""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def translate_text(text):
    if not text:
        return ""
    try:
        translated_chunks = []
        for chunk in chunk_text(text):
            translated = GoogleTranslator(source='zh-CN', target='vi').translate(chunk)
            if translated:
                translated_chunks.append(translated)
        return "".join(translated_chunks)
    except Exception as e:
        print(f"\nError translating: {e}")
        time.sleep(2)  # Back off
        return text

def process_chinese_medical_vi(input_file, output_file, max_items=None):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} items from {os.path.basename(input_file)}")
    
    if max_items:
        data = data[:max_items]
        print(f"Limiting to first {max_items} items")
        
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            train_data = json.load(f)
    else:
        train_data = []
        
    print(f"Loaded {len(train_data)} existing items from {os.path.basename(output_file)}")
    
    new_items = []
    
    for i, item in enumerate(tqdm(data, desc="Translating")):
        question = item.get("question", "")
        answer = item.get("answer", "")
        source = item.get("source", "chinese_medical_vi")
        
        # We also have "disease_vi", maybe prepend it to context? 
        # But `train.json` usually just has the user inputting symptoms.
        
        if not question or not answer:
            continue
            
        vi_question = translate_text(question)
        vi_answer = translate_text(answer)
        
        if "Lời khuyên chỉ mang tính chất tham khảo" not in vi_answer:
            vi_answer += DISCLAIMER_TEXT
            
        new_item = {
            "instruction": INSTRUCTION_TEXT,
            "input": vi_question,
            "output": vi_answer,
            "source": f"Medical-Dialogue-Dataset-Chinese_{source}"
        }
        new_items.append(new_item)
        
        # Sleep slightly to avoid rate limit
        time.sleep(0.3)
        
        # Save every 50 items so we don't lose progress on crash
        if (i + 1) % 50 == 0:
            temp_data = train_data + new_items
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(temp_data, f, ensure_ascii=False, indent=2)
            print(f"\nSaved progress at item {i+1}...")
            
    # Final save
    final_data = train_data + new_items
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully processed and merged {len(new_items)} translated items into {os.path.basename(output_file)}")
    print(f"Total items in train.json: {len(final_data)}")

if __name__ == '__main__':
    base_dir = r"C:\NDT\PJ\MediSign_AI"
    input_file = os.path.join(base_dir, r"data\training_raw\Medical-Dialogue-Dataset-Chinese\chinese_medical_vi.json")
    output_file = os.path.join(base_dir, r"data\training_clean\qwen_72b\train.json")
    
    print("Starting translation...")
    # First, translate all items in chinese_medical_vi.json
    process_chinese_medical_vi(input_file, output_file)
    print("Finished.")
