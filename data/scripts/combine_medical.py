# -*- coding: utf-8 -*-
import json, os

with open(r"C:\NDT\PJ\MediSign_AI\data\scripts\_p1.json", "r", encoding="utf-8") as f:
    p1 = json.load(f)
with open(r"C:\NDT\PJ\MediSign_AI\data\scripts\_p2.json", "r", encoding="utf-8") as f:
    p2 = json.load(f)

combined = p1 + p2
out = r"C:\NDT\PJ\MediSign_AI\data\training_raw\full_medical_vi.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)
print(f"Da ghi {len(combined)} muc vao {out}")

# Xoa file en cu
old = r"C:\NDT\PJ\MediSign_AI\data\training_raw\full_medical_en.json"
if os.path.exists(old):
    os.remove(old)
    print(f"Da xoa {old}")
