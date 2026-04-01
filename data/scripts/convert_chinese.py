# -*- coding: utf-8 -*-
"""Parse Chinese Medical Dialogue -> Vietnamese JSON Q&A (sample 500 dialogues)."""
import json, os, re

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

# Từ điển bệnh Trung-Việt phổ biến
ZH_VI = {
    "鱼鳞病": "Bệnh vẩy cá (Ichthyosis)",
    "肺炎": "Viêm phổi",
    "支气管炎": "Viêm phế quản",
    "感冒": "Cảm lạnh",
    "发烧": "Sốt",
    "咳嗽": "Ho",
    "哮喘": "Hen phế quản",
    "糖尿病": "Đái tháo đường",
    "高血压": "Tăng huyết áp",
    "心脏病": "Bệnh tim",
    "胃炎": "Viêm dạ dày",
    "皮肤": "Da liễu",
    "过敏": "Dị ứng",
    "湿疹": "Chàm (Eczema)",
    "痔疮": "Bệnh trĩ",
    "便秘": "Táo bón",
    "腹泻": "Tiêu chảy",
    "头痛": "Đau đầu",
    "失眠": "Mất ngủ",
    "抑郁": "Trầm cảm",
    "焦虑": "Lo âu",
    "甲状腺": "Tuyến giáp",
    "骨折": "Gãy xương",
    "关节炎": "Viêm khớp",
    "颈椎病": "Bệnh đốt sống cổ",
    "腰椎": "Đốt sống thắt lưng",
    "鼻炎": "Viêm mũi",
    "咽炎": "Viêm họng",
    "扁桃体": "Viêm amidan",
    "中耳炎": "Viêm tai giữa",
    "结膜炎": "Viêm kết mạc",
    "近视": "Cận thị",
    "白内障": "Đục thủy tinh thể",
    "青光眼": "Tăng nhãn áp",
    "肾结石": "Sỏi thận",
    "尿路感染": "Nhiễm trùng đường tiết niệu",
    "前列腺": "Tuyến tiền liệt",
    "月经": "Kinh nguyệt",
    "妇科": "Phụ khoa",
    "怀孕": "Mang thai",
    "不孕": "Vô sinh",
    "贫血": "Thiếu máu",
    "肝炎": "Viêm gan",
    "脂肪肝": "Gan nhiễm mỡ",
    "胆结石": "Sỏi mật",
    "痛风": "Bệnh gút",
    "银屑病": "Vẩy nến",
    "荨麻疹": "Mề đay",
    "带状疱疹": "Zona thần kinh",
    "癫痫": "Động kinh",
    "帕金森": "Parkinson",
    "脑梗": "Nhồi máu não",
    "脑出血": "Xuất huyết não",
    "冠心病": "Bệnh mạch vành",
    "心律失常": "Rối loạn nhịp tim",
    "肺结核": "Lao phổi",
    "乙肝": "Viêm gan B",
    "艾滋": "HIV/AIDS",
}

def translate_disease(zh_text):
    """Dịch tên bệnh Trung -> Việt."""
    for zh, vi in ZH_VI.items():
        if zh in zh_text:
            return vi
    return None

def parse_dialogues(filepath, max_count=100):
    """Parse file txt, trích xuất dialogues."""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        return results

    # Split by id=
    blocks = re.split(r'\nid=\d+\n', content)
    
    for block in blocks[1:max_count+1]:  # skip first empty
        lines = block.strip().split('\n')
        
        description = ""
        dialogue = ""
        department = ""
        in_desc = False
        in_dial = False
        
        for line in lines:
            line = line.strip()
            if line == "Description":
                in_desc = True
                in_dial = False
                continue
            elif line == "Dialogue":
                in_desc = False
                in_dial = True
                continue
            elif line == "Doctor faculty":
                in_desc = False
                in_dial = False
                # next line is department
                continue
            elif line.startswith("http"):
                continue
                
            if in_desc and line:
                if line.startswith("疾病："):
                    description = line[3:]
                elif line.startswith("病情描述："):
                    description = description + " - " + line[5:]
                elif line.startswith("希望提供的帮助："):
                    description = description + " | Mong muốn: " + line[8:]
            elif in_dial and line:
                if dialogue:
                    dialogue += " "
                dialogue += line

        if not description or not dialogue:
            continue

        # Dịch tên bệnh
        vi_disease = translate_disease(description)
        if vi_disease is None:
            continue  # Bỏ qua nếu không có trong từ điển

        # Tạo Q&A tiếng Việt tóm tắt
        q_text = f"Bệnh nhân hỏi về {vi_disease}: {description[:100]}..."
        a_text = f"Về bệnh {vi_disease}, bác sĩ tư vấn: {dialogue[:300]}"
        
        results.append({
            "question": q_text,
            "answer": a_text + D,
            "source": "chinese_medical_dialogue",
            "disease_vi": vi_disease,
        })

    return results

# Process all txt files
base = r"C:\NDT\PJ\MediSign_AI\data\training_raw\Medical-Dialogue-Dataset-Chinese"
txt_files = sorted([f for f in os.listdir(base) if f.endswith('.txt')])
print(f"Tim thay {len(txt_files)} file txt")

all_qa = []
for tf in txt_files:
    filepath = os.path.join(base, tf)
    qa = parse_dialogues(filepath, max_count=150)
    all_qa.extend(qa)
    print(f"  {tf}: {len(qa)} dialogues")

out = os.path.join(base, "chinese_medical_vi.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(all_qa, f, ensure_ascii=False, indent=2)
print(f"Da ghi {len(all_qa)} muc vao {out}")
