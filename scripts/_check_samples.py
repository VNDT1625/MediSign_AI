import json
p = r"c:/NDT/PJ/MediSign_AI - Copy/data/training_clean/medgemma_4b/output_format_train.jsonl"
lines = open(p, encoding="utf-8").readlines()
print(f"Total samples: {len(lines)}")
for i in [0, 100, 300, 500, 800]:
    r = json.loads(lines[i])
    print(f"\n--- Sample {i} (triage={r['triage_level']}, disease={r['disease'][:40]}) ---")
    for m in r["messages"]:
        text = m["content"][:100].replace("\n", " ")
        print(f"  {m['role'].upper()}: {text}")
