# -*- coding: utf-8 -*-
"""Parse PubMedQA -> Vietnamese JSON Q&A."""
import json, os

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

# Từ điển thuật ngữ y khoa Anh-Việt
TERMS = {
    "mortality": "tử vong",
    "survival": "sống sót",
    "efficacy": "hiệu quả",
    "treatment": "điều trị",
    "therapy": "liệu pháp",
    "diagnosis": "chẩn đoán",
    "prognosis": "tiên lượng",
    "prevention": "phòng ngừa",
    "cancer": "ung thư",
    "tumor": "khối u",
    "infection": "nhiễm trùng",
    "inflammation": "viêm",
    "surgery": "phẫu thuật",
    "drug": "thuốc",
    "vaccine": "vắc-xin",
    "blood pressure": "huyết áp",
    "diabetes": "đái tháo đường",
    "cardiovascular": "tim mạch",
    "respiratory": "hô hấp",
    "neurological": "thần kinh",
    "psychiatric": "tâm thần",
    "pediatric": "nhi khoa",
    "geriatric": "lão khoa",
    "obstetric": "sản khoa",
    "gynecologic": "phụ khoa",
    "renal": "thận",
    "hepatic": "gan",
    "pulmonary": "phổi",
    "cardiac": "tim",
    "cerebral": "não",
    "gastric": "dạ dày",
    "intestinal": "ruột",
    "skeletal": "xương",
    "muscular": "cơ",
    "dermatologic": "da liễu",
    "ophthalmic": "mắt",
    "otologic": "tai",
    "oral": "miệng",
}

DECISION_VI = {"yes": "Có", "no": "Không", "maybe": "Có thể"}

def parse_pubmedqa(filepath):
    """Parse PubMedQA JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for pmid, entry in data.items():
        question = entry.get("QUESTION", "")
        contexts = entry.get("CONTEXTS", [])
        long_answer = entry.get("LONG_ANSWER", "")
        decision = entry.get("final_decision", "")

        if not question or not long_answer:
            continue

        # Giữ câu hỏi gốc + thêm context Việt
        vi_decision = DECISION_VI.get(decision, decision)

        # Tóm tắt context
        context_summary = ""
        if contexts:
            context_summary = contexts[0][:200] + "..." if len(contexts[0]) > 200 else contexts[0]

        answer_text = long_answer[:400]
        if len(long_answer) > 400:
            last_dot = answer_text.rfind('.')
            if last_dot > 200:
                answer_text = answer_text[:last_dot+1]

        results.append({
            "question": question,
            "answer": f"Kết luận: {vi_decision}. {answer_text}" + D,
            "source": "pubmedqa",
            "pmid": pmid,
        })

    return results

# Process
base = r"C:\NDT\PJ\MediSign_AI\data\training_raw\pubmedqa\data"
pqa_file = os.path.join(base, "ori_pqal.json")

if os.path.exists(pqa_file):
    qa = parse_pubmedqa(pqa_file)
    out = os.path.join(os.path.dirname(base), "pubmedqa_vi.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(qa, f, ensure_ascii=False, indent=2)
    print(f"Da ghi {len(qa)} muc vao {out}")
else:
    print(f"Khong tim thay {pqa_file}")
