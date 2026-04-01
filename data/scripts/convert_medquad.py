# -*- coding: utf-8 -*-
"""Parse MedQuAD XML -> Vietnamese JSON Q&A."""
import xml.etree.ElementTree as ET
import json, os, glob

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

# Từ điển y khoa Anh-Việt cho các bệnh phổ biến
DISEASE_VI = {
    "acanthamoeba": "Nhiễm Acanthamoeba",
    "acromegaly": "Bệnh to cực (Acromegaly)",
    "adrenal insufficiency": "Suy tuyến thượng thận",
    "amyloidosis": "Bệnh amyloidosis (thoái hóa tinh bột)",
    "anemia": "Thiếu máu",
    "appendicitis": "Viêm ruột thừa",
    "arthritis": "Viêm khớp",
    "asthma": "Hen phế quản",
    "celiac disease": "Bệnh celiac",
    "chickenpox": "Thủy đậu",
    "chlamydia": "Nhiễm Chlamydia",
    "cholera": "Bệnh tả",
    "cirrhosis": "Xơ gan",
    "crohn": "Bệnh Crohn",
    "cushing": "Hội chứng Cushing",
    "cystic fibrosis": "Xơ nang",
    "dengue": "Sốt xuất huyết Dengue",
    "diabetes": "Đái tháo đường",
    "diphtheria": "Bệnh bạch hầu",
    "ebola": "Bệnh Ebola",
    "eczema": "Chàm (Eczema)",
    "epilepsy": "Động kinh",
    "fibromyalgia": "Đau cơ xơ hóa",
    "flu": "Cúm",
    "gallstones": "Sỏi mật",
    "gastritis": "Viêm dạ dày",
    "glaucoma": "Tăng nhãn áp (Glaucoma)",
    "gonorrhea": "Bệnh lậu",
    "gout": "Bệnh gout (gút)",
    "heart disease": "Bệnh tim",
    "heart failure": "Suy tim",
    "hemophilia": "Bệnh máu khó đông",
    "hepatitis": "Viêm gan",
    "herpes": "Herpes",
    "hiv": "HIV/AIDS",
    "hypertension": "Tăng huyết áp",
    "hypothyroidism": "Suy giáp",
    "hyperthyroidism": "Cường giáp",
    "irritable bowel": "Hội chứng ruột kích thích",
    "kidney disease": "Bệnh thận",
    "kidney stones": "Sỏi thận",
    "leukemia": "Bệnh bạch cầu (Leukemia)",
    "liver disease": "Bệnh gan",
    "lupus": "Lupus ban đỏ",
    "lyme disease": "Bệnh Lyme",
    "malaria": "Sốt rét",
    "measles": "Sởi",
    "meningitis": "Viêm màng não",
    "multiple sclerosis": "Đa xơ cứng",
    "mumps": "Quai bị",
    "norovirus": "Norovirus",
    "obesity": "Béo phì",
    "osteoporosis": "Loãng xương",
    "pancreatitis": "Viêm tụy",
    "parkinson": "Bệnh Parkinson",
    "pneumonia": "Viêm phổi",
    "prostate": "Tuyến tiền liệt",
    "psoriasis": "Vẩy nến",
    "rabies": "Bệnh dại",
    "salmonella": "Nhiễm Salmonella",
    "schizophrenia": "Tâm thần phân liệt",
    "sickle cell": "Bệnh hồng cầu hình liềm",
    "stroke": "Đột quỵ",
    "syphilis": "Giang mai",
    "tetanus": "Uốn ván",
    "tuberculosis": "Lao phổi",
    "typhoid": "Thương hàn",
    "ulcer": "Loét dạ dày",
    "urinary tract infection": "Nhiễm trùng đường tiết niệu",
    "whooping cough": "Ho gà",
    "zika": "Virus Zika",
}

QTYPE_VI = {
    "information": "là gì",
    "symptoms": "có triệu chứng gì",
    "causes": "nguyên nhân là gì",
    "exams and tests": "chẩn đoán bằng cách nào",
    "treatment": "điều trị như thế nào",
    "prevention": "phòng ngừa như thế nào",
    "susceptibility": "ai có nguy cơ mắc",
    "complications": "có biến chứng gì",
    "outlook": "tiên lượng như thế nào",
    "inheritance": "có di truyền không",
    "frequency": "phổ biến như thế nào",
    "research": "nghiên cứu mới nhất là gì",
}

def get_vi_name(focus):
    fl = focus.lower()
    for key, vi in DISEASE_VI.items():
        if key in fl:
            return vi
    return focus

def shorten_answer(answer, max_chars=500):
    """Rút gọn câu trả lời dài, giữ nội dung quan trọng."""
    if not answer:
        return ""
    answer = answer.strip()
    if len(answer) <= max_chars:
        return answer
    # Cắt tại câu gần nhất
    cut = answer[:max_chars]
    last_period = cut.rfind('.')
    if last_period > max_chars // 2:
        return cut[:last_period + 1]
    return cut + "..."

def parse_xml(filepath):
    """Parse một file XML MedQuAD, trả về list Q&A."""
    results = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        focus = root.find("Focus")
        focus_text = focus.text.strip() if focus is not None and focus.text else "Không rõ"
        vi_name = get_vi_name(focus_text)

        qapairs = root.find("QAPairs")
        if qapairs is None:
            return results

        for qapair in qapairs.findall("QAPair"):
            q_elem = qapair.find("Question")
            a_elem = qapair.find("Answer")
            if q_elem is None or a_elem is None:
                continue

            qtype = q_elem.get("qtype", "information")
            answer_text = a_elem.text.strip() if a_elem.text else ""
            if not answer_text:
                continue

            # Tạo câu hỏi tiếng Việt
            vi_qtype = QTYPE_VI.get(qtype, "là gì")
            vi_question = f"{vi_name} {vi_qtype}?"

            # Rút gọn câu trả lời
            short_answer = shorten_answer(answer_text)

            results.append({
                "question": vi_question,
                "answer": short_answer + D,
                "source": "medquad",
                "original_disease": focus_text,
                "original_qtype": qtype,
            })
    except Exception as e:
        print(f"  Loi parse {filepath}: {e}")
    return results

# Scan all XML files
base = r"C:\NDT\PJ\MediSign_AI\data\training_raw\MedQuAD"
xml_files = glob.glob(os.path.join(base, "**", "*.xml"), recursive=True)
print(f"Tim thay {len(xml_files)} file XML")

all_qa = []
for xf in sorted(xml_files):
    qa = parse_xml(xf)
    all_qa.extend(qa)

out = os.path.join(base, "medquad_vi.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(all_qa, f, ensure_ascii=False, indent=2)
print(f"Da ghi {len(all_qa)} cau hoi-tra loi vao {out}")
