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
        time.sleep(2)
        return ""

def generate_answer(item):
    """
    Attempt to extract a doctor's answer from the extracted_dialogues structure.
    Usually the answer is somewhere under description.
    Wait, `extracted_dialogues.json` structure might not have explicit doctor answer in description.
    Let's extract whatever `patient_description` is as input, and `disease` as part of input.
    If there's no answer, this data might just be synthetic prompts.
    Let's print the structure first.
    """
    pass

def process_sample(input_file, output_file, max_items=50):
    print(f"Loading data from {os.path.basename(input_file)}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} items. Processing {max_items} format samples...")
    
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            train_data = json.load(f)
    else:
        train_data = []
        
    new_items = []
    
    # We will pick the first max_items that have a valid title or description
    count = 0
    for item in tqdm(data, desc="Translating Sample", total=max_items):
        if count >= max_items:
            break
            
        title = item.get("title", "")
        desc = item.get("description", {})
        patient_desc = desc.get("patient_description", "")
        disease = desc.get("disease", "")
        
        # In extracted_dialogues, we couldn't clearly see doctor answers in the printed snippet.
        # But let's assume `question` might be in description if it's there.
        # Or maybe it's "question", "doctor_answer"
        
        input_text = f"{title}\n{patient_desc}".strip()
        
        # If no explicit answer exists in this raw file, we shouldn't merge it blindly.
        # Let's save the sample to a different file first instead of `train.json` to inspect.
        sample_output_file = output_file.replace("train.json", "sample_translated.json")
        
        vi_input = translate_text(input_text)
        
        # We don't have an explicit answer yet, so we just translate the input to see logic
        # For actual AI training data, we NEED the output. Let's just create raw translated objects.
        
        new_item = {
            "instruction": INSTRUCTION_TEXT,
            "input": vi_input,
            "output": "<EXPECTED_DOCTOR_ANSWER> " + DISCLAIMER_TEXT,
            "source": f"Medical-Dialogue-Dataset-Chinese_Sample"
        }
        new_items.append(new_item)
        count += 1
        time.sleep(0.3)
        
    # Final save to sample file
    sample_output_file = output_file.replace("train.json", "sample_translated.json")
    with open(sample_output_file, 'w', encoding='utf-8') as f:
        json.dump(new_items, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(new_items)} sampled items to {os.path.basename(sample_output_file)}")

if __name__ == '__main__':
    base_dir = r"C:\NDT\PJ\MediSign_AI"
    input_file = os.path.join(base_dir, r"data\training_raw\Medical-Dialogue-Dataset-Chinese\extracted_dialogues.json")
    output_file = os.path.join(base_dir, r"data\training_clean\qwen_72b\train.json")
    
    process_sample(input_file, output_file, max_items=10)
