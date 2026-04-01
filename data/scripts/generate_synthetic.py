# -*- coding: utf-8 -*-
"""Tạo synthetic data - các câu hỏi không trùng với nguồn có sẵn."""
import json
import random
random.seed(456)

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."
INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."

result = []

# ===== BỆNH THÔNG DỤNG TẠI VIỆT NAM =====
DISEASES = [
    {"name": "Cảm lạnh", "symptoms": "sổ mũi, hắt hơi, đau họng, ho nhẹ, mệt mỏi", "treatment": "Nghỉ ngơi, uống nước, vitamin C. Không cần kháng sinh.", "prevent": "Rửa tay thường xuyên, tránh tiếp xúc người bệnh"},
    {"name": "Cúm", "symptoms": "sốt cao, đau cơ, đau đầu, mệt mỏi, ho", "treatment": "Nghỉ ngơi, uống nước, thuốc hạ sốt. Oseltamivir nếu sớm.", "prevent": "Tiêm vaccine cúm hàng năm"},
    {"name": "Viêm họng", "symptoms": "đau họng, khó nuốt, amidan sưng đỏ, sốt", "treatment": "Kháng sinh nếu do vi khuẩn (Penicillin). Giảm đau Paracetamol.", "prevent": "Không hút thuốc, tránh thức ăn cay nóng"},
    {"name": "Viêm xoang", "symptoms": "đau mặt, nghẹt mũi, đau đầu, chảy dịch mũi", "treatment": "Xịt mũi saline, thuốc kháng histamin, kháng sinh nếu nhiễm khuẩn.", "prevent": "Tránh dị ứng, rửa mũi thường xuyên"},
    {"name": "Viêm phế quản", "symptoms": "ho kéo dài, đờm, khó thở, mệt", "treatment": "Uống nhiều nước, thuốc ho, thuốc giãn phế quản nếu cần.", "prevent": "Không hút thuốc, tránh ô nhiễm"},
    {"name": "Viêm phổi", "symptoms": "sốt cao, ho đờm, đau ngực, khó thở", "treatment": "Kháng sinh (Amoxicillin/Azithromycin). Nhập viện nặng.", "prevent": "Tiêm vaccine phế cầu, tránh hút thuốc"},
    {"name": "Tiêu chảy", "symptoms": "phân lỏng, đau bụng, nôn, sốt", "treatment": "Bù nướcORS, ăn uống nhẹ. Kháng sinh nếu nhiễm khuẩn nặng.", "prevent": "Rửa tay, ăn chín uống sôi"},
    {"name": "Táo bón", "symptoms": "đi cầu khó, phân cứng, đau bụng dưới", "treatment": "Uống nhiều nước, ăn nhiều rau xanh, tập thể dục. Thuốc nhuận tràng.", "prevent": "Chế độ ăn giàu chất xơ, uống đủ nước"},
    {"name": "Đau dạ dày", "symptoms": "đau vùng thượng vị, buồn nôn, đầy bụng, ợ chua", "treatment": "Thuốc kháng acid, ăn uống đúng giờ, tránh đồ cay nóng.", "prevent": "Không ăn quá no, tránh stress, không hút thuốc"},
    {"name": "Trào ngược dạ dày", "symptoms": "ợ chua, đau ngực, khó nuốt, ho kéo dài", "treatment": "Thuốc ức chế bơm proton (Omeprazole). Ăn ít, chia nhiều bữa.", "prevent": "Không ăn quá no, tránh nằm sau ăn, nâng đầu giường"},
    {"name": "Viêm gan B", "symptoms": "mệt mỏi, vàng da, đau bụng phải, chán ăn", "treatment": "Thuốc kháng virus (Tenofovir/Entecavir). Theo dõi định kỳ.", "prevent": "Tiêm vaccine, quan hệ an toàn, không dùng chung kim"},
    {"name": "Sỏi thận", "symptoms": "đau lưng dữ dội, đau bụng dưới, tiểu ra máu, buồn nôn", "treatment": "Uống nhiều nước, thuốc giảm đau. Tán sỏi hoặc phẫu thuật nếu to.", "prevent": "Uống đủ 2-3 lít nước/ngày, hạn chế muối"},
    {"name": "Viêm khớp gối", "symptoms": "đau khớp gối, sưng, cứng khớp buổi sáng, khó đi lại", "treatment": "Giảm đau NSAIDs, vật lý trị liệu, giảm cân nếu thừa cân.", "prevent": "Giữ cân nặng hợp lý, tập thể dục đều đặn"},
    {"name": "Đau lưng", "symptoms": "đau vùng thắt lưng, cứng cơ, khó cúi, đau chạy xuống chân", "treatment": "Nghỉ ngơi, giảm đau, vật lý trị liệu, tập thể dục.", "prevent": "Tư thế đúng khi ngồi/nâng vật, tập thể dục đều"},
    {"name": "Đau đầu migraine", "symptoms": "đau nửa đầu dữ dội, buồn nôn, nhạy sáng, kéo dài 4-72h", "treatment": "Thuốc giảm đau (Ibuprofen), thuốc đặc trị (Triptan). Phòng ngừa.", "prevent": "Ngủ đủ giấc, tránh stress, không bỏ bữa"},
    {"name": "Chóng mặt", "symptoms": "quay cuồng, mất thăng bằng, buồn nôn, ù tai", "treatment": "Tùy nguyên nhân: thuốc điều hòa tiền đình, tập vestibular.", "prevent": "Đứng lên từ từ, tránh thay đổi tư thế đột ngột"},
    {"name": "Thiếu máu", "symptoms": "mệt mỏi, da xanh, hoa mắt chóng mặt, tim đập nhanh", "treatment": "Bổ sung sắt, vitamin B12, acid folic. Điều trị nguyên nhân.", "prevent": "Ăn thịt đỏ, rau xanh, trái cây giàu vitamin C"},
    {"name": "Cao huyết áp", "symptoms": "thường không có triệu chứng, đau đầu, chóng mặt, mệt mỏi", "treatment": "Thuốc hạ áp (Amlodipine, Losartan). Giảm muối, giảm cân.", "prevent": "Giảm muối, tập thể dục, hạn chế rượu, không hút thuốc"},
    {"name": "Đái tháo đường type 2", "symptoms": "khát nước nhiều, tiểu nhiều, mệt mỏi, vết thương lâu lành", "treatment": "Metformin, thay đổi lối sống, theo dõi đường huyết.", "prevent": "Giảm cân, ăn uống lành mạnh, tập thể dục"},
    {"name": "Mỡ máu cao", "symptoms": "thường không có triệu chứng, có thể đau ngực", "treatment": "Statin (Atorvastatin). Giảm ăn mỡ, tập thể dục.", "prevent": "Ăn ít mỡ động vật, ăn nhiều rau, tập thể dục"},
]

# ===== THUỐC THÔNG DỤNG =====
DRUGS = [
    {"name": "Paracetamol", "uses": "Hạ sốt, giảm đau nhẹ-vừa", "dose": "500-1000mg/lần, tối đa 4g/ngày", "side": "Quá liều tổn thương gan"},
    {"name": "Ibuprofen", "uses": "Giảm đau, kháng viêm, hạ sốt", "dose": "200-400mg/lần, tối đa 1200mg/ngày", "side": "Đau dạ dày, loét"},
    {"name": "Amoxicillin", "uses": "Kháng sinh nhiễm khuẩn hô hấp, tiết niệu", "dose": "500mg x 3 lần/ngày", "side": "Tiêu chảy, dị ứng"},
    {"name": "Omeprazole", "uses": "Thuốc dạ dày, trào ngược", "dose": "20mg/ngày, trước ăn", "side": "Đau đầu, tiêu chảy"},
    {"name": "Metformin", "uses": "Điều trị đái tháo đường type 2", "dose": "500mg x 2 lần/ngày", "side": "Buồn nôn, tiêu chảy"},
    {"name": "Amlodipine", "uses": "Điều trị tăng huyết áp", "dose": "5-10mg/ngày", "side": "Phù chân, đỏ mặt"},
    {"name": "Atorvastatin", "uses": "Hạ cholesterol", "dose": "10-20mg/ngày, tối", "side": "Đau cơ, tăng men gan"},
    {"name": "Cetirizine", "uses": "Thuốc dị ứng", "dose": "10mg/ngày", "side": "Buồn ngủ nhẹ, khô miệng"},
    {"name": "Salbutamol", "uses": "Giãn phế quản, hen", "dose": "1-2 nhát khi khó thở", "side": "Run tay, tim đập nhanh"},
    {"name": "Diazepam", "uses": "An thần, chống lo âu, mất ngủ", "dose": "2-10mg/ngày", "side": "Buồn ngủ, phụ thuộc (dùng lâu)"},
    {"name": "Sertraline", "uses": "Thuốc trầm cảm, rối loạn lo âu", "dose": "25-50mg/ngày", "side": "Buồn nôn, mất ngủ, giảm ham muốn"},
    {"name": "Prednisone", "uses": "Kháng viêm, ức chế miễn dịch", "dose": "5-60mg/ngày tùy bệnh", "side": "Tăng cân, cao huyết áp, loãng xương (lâu dài)"},
    {"name": "Aspirin", "uses": "Giảm đau, hạ sốt, chống kết tập tiểu cầu", "dose": "75-100mg/ngày (phòng)", "side": "Xuất huyết tiêu hóa"},
    {"name": "Losartan", "uses": "Thuốc hạ áp, bảo vệ thận", "dose": "50-100mg/ngày", "side": "Chóng mặt, tăng kali máu"},
    {"name": "Gliclazide", "uses": "Thuốc đái tháo đường", "dose": "40-80mg/ngày", "side": "Hạ đường huyết"},
]

# Generate disease Q&A
for disease in DISEASES:
    result.append({
        "question": f"Trieu chung benh {disease['name']} la gi?",
        "answer": f"Cac trieu chung cua benh {disease['name']}: {disease['symptoms']}. {D}",
        "source": "synthetic"
    })

    result.append({
        "question": f"Cach tri benh {disease['name']}?",
        "answer": f"Cach dieu tri benh {disease['name']}: {disease['treatment']}. {D}",
        "source": "synthetic"
    })

    result.append({
        "question": f"Phong ngua benh {disease['name']} nhu the nao?",
        "answer": f"Cach phong ngua benh {disease['name']}: {disease['prevent']}. {D}",
        "source": "synthetic"
    })

# Generate drug Q&A
for drug in DRUGS:
    result.append({
        "question": f"Thuoc {drug['name']} cong dung gi?",
        "answer": f"Thuoc {drug['name']} co cong dung: {drug['uses']}. {D}",
        "source": "synthetic"
    })

    result.append({
        "question": f"Lieu dung thuoc {drug['name']}?",
        "answer": f"Lieu dung {drug['name']}: {drug['dose']}. {D}",
        "source": "synthetic"
    })

    result.append({
        "question": f"Tac dung phu cua thuoc {drug['name']}?",
        "answer": f"Tac dung phu cua {drug['name']}: {drug['side']}. {D}",
        "source": "synthetic"
    })

# Generate interaction Q&A
interactions = [
    ("Warfarin", "Aspirin", "Tang nguy co xuat huyet"),
    ("Metformin", "Ruou", "Tang nguy co nhiem toan lactic"),
    ("Digoxin", "Amiodarone", "Tang nguy co ngo doc Digoxin"),
    ("Simvastatin", "Nuoc buoi", "Tang nguy co tieu co"),
    ("Diazepam", "Ruou", "Tang buon ngu, suy ho hap"),
    ("Clopidogrel", "Omeprazole", "Giam tac dung Clopidogrel"),
]

for d1, d2, effect in interactions:
    result.append({
        "question": f"{d1} va {d2} co tuong tac khong?",
        "answer": f"CO - {d1} va {d2}: {effect}. Can than trong khi su dung. {D}",
        "source": "synthetic"
    })

# Generate symptom Q&A
symptoms = [
    ("Dau dau", "Nguyen nhân pho bien: cam cum, migraine, stress, mat ngu. Can kham neu dau manh, kem soat, say chong mat."),
    ("Ho", "Co the do cam cum, viem hong, viem phoi, dị ưng. Uong nhieu nuoc, thuoc ho neu can."),
    ("Sot", "Dau hieu cua cam cum, nhiem khuan. Uong thuoc ha sot, neu sot cao hon 3 ngay can di kham."),
    ("Dau bung", "Co nhieu nguyen nhân: cam cum, ot sang, viem ruot. Neu dau manh, kem buon nao, phan co mau can di kham ngay."),
    ("Mat me", "Thieu ngu, stress, lam viec may tinh nhieu, thieu mau. Nghi ngoi duoc, cham soc mat."),
]

for symptom, answer in symptoms:
    result.append({
        "question": f"Ngay {symptom} la bi benh gi?",
        "answer": f"{symptom} co the do nhieu nguyen nhan khac nhau. {answer} {D}",
        "source": "synthetic"
    })

# Save
output_path = r"C:\NDT\PJ\MediSign_AI\data\training_raw\synthetic_data.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Generated {len(result)} synthetic Q&A records")
print(f"Saved to: {output_path}")
