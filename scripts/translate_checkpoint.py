#!/usr/bin/env python3
import os
import json

API_KEY = "sk-VIL4n0d8qRZHTp97kDyCAQ"
import requests
import time
import sys

def translate(text):
    if not text: return text
    url = "https://api.blackbox.ai/v1/chat/completions"
    for _ in range(3):
        try:
            r = requests.post(url, headers={"Authorization": f"Bearer {API_KEY}"}, json={
                "model": "blackboxai/qwen/qwen-turbo",
                "messages": [{"role": "user", "content": f"Dịch: {text}"}],
                "max_tokens": 500
            }, timeout=15)
            if r.status_code == 200:
                return r.json()['choices'][0]['message']['content']
        except: pass
    return text

# Read existing data
INPUT = r"C:\NDT\PJ\MediSign_AI\data\training_clean\medical_dialogue_checkpoint.json"
OUT = r"C:\NDT\PJ\MediSign_AI\data\training_clean\medical_dialogue_full.json"

print("Loading checkpoint...")
with open(INPUT, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} records")

INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh."

for i, item in enumerate(data):
    if i % 50 == 0:
        print(f"Translating {i}/{len(data)}...")

    # Translate input
    item['instruction'] = INSTRUCTION
    item['input'] = translate(item['input'])
    item['output'] = translate(item['output'])

    time.sleep(0.03)

print("Saving...")
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Done! Saved to {OUT}")
