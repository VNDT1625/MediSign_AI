# -*- coding: utf-8 -*-
"""Generate more synthetic data - Focus on drugs and symptoms."""
import json
import random
random.seed(999)

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

result = []

# More drug interaction pairs
DRUG_INTERACTIONS = [
    ("Warfarin", "Aspirin", "Tăng nguy cơ xuất huyết nặng", "Tránh dùng chung trừ khi bác sĩ chỉ định"),
    ("Warfarin", "Vitamin K", "Vitamin K giảm tác dụng Warfarin", "Cần theo dõi INR thường xuyên"),
    ("Metformin", "Rượu", "Tăng nguy cơ nhiễm toan lactic", "Tránh uống rượu khi dùng Metformin"),
    ("Digoxin", "Furosemide", "Furosemide gây thiếu kali, tăng độc tính Digoxin", "Theo dõi kali máu"),
    ("Amlodipine", "Simvastatin", "Amlodipine tăng nồng độ Simvastatin", "Giảm liều Simvastatin"),
    ("Sildenafil", "Nitroglycerin", "Gây hạ huyết áp nghiêm trọng", "TUYỆT ĐỐI không dùng chung"),
    ("Clarithromycin", "Statins", "Clarithromycin tăng nồng độ Statins", "Tránh hoặc giảm liều Statins"),
    ("Isoniazid", "Phenytoin", "Tăng độc tính Phenytoin", "Theo dõi nồng độ thuốc"),
    ("Fluconazole", "Warfarin", "Fluconazole tăng tác dụng Warfarin", "Giảm liều Warfarin, theo dõi INR"),
    ("Erythromycin", "Theophylline", "Erythromycin tăng nồng độ Theophylline", "Giảm liều Theophylline"),
]

for d1, d2, effect, note in DRUG_INTERACTIONS:
    result.append({
        "question": f"{d1} và {d2} có tương tác với nhau không?",
        "answer": f"CÓ TƯƠNG TÁC. {d1} + {d2}: {effect}. {note}. {D}",
        "source": "drug_interaction"
    })
    result.append({
        "question": f"Tôi đang uống {d1} có uống {d2} được không?",
        "answer": f"KHÔNG KHUYẾN CÁO. {d1} + {d2}: {effect}. {note}. {D}",
        "source": "drug_interaction"
    })

# Drug side effects
DRUG_SIDE_EFFECTS = [
    ("Aspirin", "Xuất huyết tiêu hóa, dị ứng, hen kịch phát"),
    ("Ibuprofen", "Đau dạ dày, loét, suy thận, tăng huyết áp"),
    ("Diclofenac", "Tăng nguy cơ tim mạch, xuất huyết tiêu hóa"),
    ("Paracetamol", "Tổn thương gan nếu quá liều (>4g/ngày)"),
    ("Metformin", "Buồn nôn, tiêu chảy, nhiễm toan lactic (hiếm)"),
    ("Statins", "Đau cơ, tiêu cơ vân, tăng men gan"),
    ("Beta-blockers", "Mệt mỏi, nhịp chậm, lạnh tay chân, rối loạn cương dương"),
    ("ACE inhibitors", "Ho khan, tăng kali máu, suy thận"),
    ("ARBs", "Chóng mặt, tăng kali máu"),
    ("CCBs", "Phù chân, đỏ mặt, đau đầu, táo bón"),
    ("Sulfonylureas", "Hạ đường huyết, tăng cân"),
    ("DPP-4 inhibitors", "Nhiễm khuẩn đường hô hấp, viêm tụy (hiếm)"),
    ("Thiazolidinediones", "Tăng cân, phù, gãy xương, viêm tụy"),
    ("Benzodiazepines", "Buồn ngủ, phụ thuộc, giảm trí nhớ"),
    ("SSRIs", "Buồn nôn, mất ngủ, giảm ham muốn, serotonin syndrome"),
    ("Tricyclic antidepressants", "Khô miệng, táo bón, nhịp tim nhanh, ngộ độc"),
    ("Opioids", "Nghiện, táo bón, buồn nôn, suy hô hấp"),
    ("Corticosteroids", "Tăng cân, cao huyết áp, đái tháo đường, loãng xương"),
    ("Antihistamines", "Buồn ngủ, khô miệng, bí tiểu"),
    ("Proton pump inhibitors", "Thiếu B12, nhiễm khuẩn C. difficile, gãy xương"),
]

for drug, side in DRUG_SIDE_EFFECTS:
    result.append({
        "question": f"Tác dụng phụ của thuốc {drug} là gì?",
        "answer": f"Tác dụng phụ của {drug}: {side}. {D}",
        "source": "drug_side_effects"
    })
    result.append({
        "question": f"Thuốc {drug} có gây hại gì không?",
        "answer": f"Tác dụng không mong muốn của {drug}: {side}. {D}",
        "source": "drug_side_effects"
    })

# Drug contraindications
DRUG_CONTRA = [
    ("Aspirin", "Dị ứng, loét dạ dày, rối loạn đông máu, mang thai 3 tháng cuối"),
    ("Ibuprofen", "Dị ứng NSAID, loét dạ dày, suy thận nặng, mang thai 3 tháng cuối"),
    ("Metformin", "Suy thận nặng, suy gan nặng, nhiễm toan lactic"),
    ("Statins", "Bệnh gan hoạt động, mang thai, cho con bú"),
    ("Beta-blockers", "Suy tim nặng, nhịp chậm, khí phế thũng, hen"),
    ("ACE inhibitors", "Phù Quincke, mang thai, hẹp động mạch thận"),
    ("Sildenafil", "Dùng Nitroglycerin, bệnh tim nặng, hạ huyết áp"),
    ("Warfarin", "Thai kỳ, xuất huyết nội tạng, viêm màng ngoài tim"),
    ("Amiodarone", "Bệnh tuyến giáp, bệnh phổi, khoảng QT dài"),
    ("Clopidogrel", "Xuất huyết đang hoạt động, loét dạ dày"),
]

for drug, contra in DRUG_CONTRA:
    result.append({
        "question": f"Ai không nên dùng thuốc {drug}?",
        "answer": f"Chống chỉ định của {drug}: {contra}. {D}",
        "source": "drug_contra"
    })
    result.append({
        "question": f"Trường hợp nào không được dùng {drug}?",
        "answer": f"Không dùng {drug} khi: {contra}. {D}",
        "source": "drug_contra"
    })

# Drug dosage
DRUG_DOSAGE = [
    ("Paracetamol", "Người lớn: 500-1000mg/lần, tối đa 4g/ngày. Trẻ: 10-15mg/kg/lần"),
    ("Amoxicillin", "Người lớn: 500mg x 3 lần/ngày hoặc 875mg x 2 lần/ngày"),
    ("Azithromycin", "Ngày 1: 500mg, các ngày 2-5: 250mg/ngày (uống 1 lần/ngày)"),
    ("Omeprazole", "20mg x 1-2 lần/ngày, uống trước ăn 30 phút"),
    ("Metformin", "500mg x 1-2 lần/ngày, có thể tăng đến 2000mg/ngày"),
    ("Amlodipine", "5-10mg/ngày (uống 1 lần)"),
    ("Atorvastatin", "10-80mg/ngày, uống vào buổi tối"),
    ("Losartan", "50-100mg/ngày (uống 1 lần)"),
    ("Diazepam", "2-10mg x 2-4 lần/ngày tùy chỉ định (không quá 30mg/ngày)"),
    ("Sertraline", "50mg/ngày, có thể tăng đến 200mg/ngày"),
]

for drug, dose in DRUG_DOSAGE:
    result.append({
        "question": f"Liều dùng thuốc {drug} như thế nào?",
        "answer": f"Liều dùng {drug}: {dose}. {D}",
        "source": "drug_dosage"
    })
    result.append({
        "question": f"Cách uống thuốc {drug}?",
        "answer": f"Cách sử dụng {drug}: {dose}. {D}",
        "source": "drug_dosage"
    })

# Save
output_path = r"C:\NDT\PJ\MediSign_AI\data\training_raw\synthetic_drugs.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Generated {len(result)} drug-focused records")
