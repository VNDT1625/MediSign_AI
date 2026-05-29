# -*- coding: utf-8 -*-
"""Convert crawled drugs to JSON database format for medicine lookup."""
import json
import re

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[[a-z]\]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Load crawled data
with open(r"C:\NDT\PJ\MediSign_AI\data\training_raw\crawled_drugs_comprehensive.json", 'r', encoding='utf-8') as f:
    drugs_raw = json.load(f)

print(f"Loaded {len(drugs_raw)} drugs")

# Convert to structured database format
drug_db = []

for item in drugs_raw:
    name = item.get('name', '').strip()
    desc = clean_text(item.get('description', ''))

    if not name or len(desc) < 50:
        continue

    # Extract basic info
    drug_entry = {
        "name": name,
        "description": desc[:500],
        "source": "wikipedia"
    }

    drug_db.append(drug_entry)

print(f"Processed: {len(drug_db)} drugs")

# Save as JSON database
db_path = r"C:\NDT\PJ\MediSign_AI\data\training_clean\drug_database.json"
with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(drug_db, f, ensure_ascii=False, indent=2)

print(f"\n✓ Saved drug database to: {db_path}")
print(f"Total drugs: {len(drug_db)}")

# Show sample
print("\n=== Sample ===")
if drug_db:
    print(f"Name: {drug_db[0]['name']}")
    print(f"Desc: {drug_db[0]['description'][:200]}...")
