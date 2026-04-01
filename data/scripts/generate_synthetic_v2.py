# -*- coding: utf-8 -*-
"""Generate MORE synthetic data - Đạt target 30K."""
import json
import random
random.seed(789)

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."
INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."

result = []

# ===== BỆNH THÔNG DỤNG (mở rộng) =====
DISEASES_VN = [
    {"name": "Cảm lạnh thông thường", "desc": "Bệnh virus phổ biến, tự khỏi sau 7-10 ngày"},
    {"name": "Cúm seasonal", "desc": "Nhiễm virus cúm, triệu chứng nặng hơn cảm"},
    {"name": "Viêm họng cấp", "desc": "Nhiễm virus hoặc vi khuẩn, đau họng"},
    {"name": "Viêm amidan", "desc": "Viêm amidan, đau khi nuốt, amidan sưng đỏ"},
    {"name": "Viêm xoang cấp", "desc": "Viêm xoang mũi, nghẹt mũi, đau mặt"},
    {"name": "Viêm phế quản cấp", "desc": "Viêm phế quản, ho có đờm"},
    {"name": "Viêm phổi", "desc": "Nhiễm khuẩn phổi, sốt cao, khó thở"},
    {"name": "Tiêu chảy cấp", "desc": "Rối loạn tiêu hóa, phân lỏng nhiều lần"},
    {"name": "Táo bón mãn tính", "desc": "Đi cầu khó, phân cứng"},
    {"name": "Hội chứng ruột kích thích", "desc": "Đau bụng, rối loạn tiêu hóa mãn tính"},
    {"name": "Viêm loét dạ dày tá tràng", "desc": "Loét niêm mạc dạ dày, đau thượng vị"},
    {"name": "Trào ngược dạ dày thực quản", "desc": "Acid trào ngược, ợ chua, đau ngực"},
    {"name": "Viêm gan B mãn tính", "desc": "Nhiễm HBV, có thể gây xơ gan"},
    {"name": "Viêm gan C", "desc": "Nhiễm HCV, có thể gây xơ gan"},
    {"name": "Xơ gan", "desc": "Gan bị xơ hóa, suy gan"},
    {"name": "Sỏi thận", "desc": "Sỏi trong thận, đau dữ dội khi di chuyển"},
    {"name": "Nhiễm trùng đường tiết niệu", "desc": "Nhiễm khuẩn bàng quang, tiểu đau rát"},
    {"name": "Viêm bàng quang", "desc": "Viêm bàng quang, tiểu nhiều lần, đau"},
    {"name": "Viêm khớp dạng thấp", "desc": "Bệnh tự miễn, sưng đau khớp"},
    {"name": "Viêm khớp gối", "desc": "Viêm khớp gối, đau, sưng, cứng"},
    {"name": "Thoái hóa khớp", "desc": "Khớp bị lão hóa, đau khi vận động"},
    {"name": "Đau thắt lưng", "desc": "Đau vùng thắt lưng, có thể chạy chân"},
    {"name": "Đau cổ", "desc": "Đau cổ, cứng cơ, có thể gây đau đầu"},
    {"name": "Đau đầu căng thẳng", "desc": "Đau đầu do stress, lo âu"},
    {"name": "Đau nửa đầu (Migraine)", "desc": "Đau đầu dữ dội một bên, buồn nôn, nhạy sáng"},
    {"name": "Chóng mặt", "desc": "Quay cuồng, mất thăng bằng"},
    {"name": "Thiếu máu", "desc": "Thiếu hồng cầu, mệt mỏi, da xanh"},
    {"name": "Cao huyết áp", "desc": "Huyết áp cao, thường không triệu chứng"},
    {"name": "Hạ huyết áp", "desc": "Huyết áp thấp, chóng mặt khi đứng"},
    {"name": "Rối loạn nhịp tim", "desc": "Tim đập không đều, hồi hộp"},
    {"name": "Suy tim", "desc": "Tim bơm máu kém, khó thở, phù"},
    {"name": "Đái tháo đường type 2", "desc": "Đường huyết cao, khát nhiều, tiểu nhiều"},
    {"name": "Đái tháo đường type 1", "desc": "Thiếu insulin, cần tiêm insulin"},
    {"name": "Tiền đái tháo đường", "desc": "Đường huyết cao nhưng chưa đạt tiểu đường"},
    {"name": "Rối loạn mỡ máu", "desc": "Cholesterol cao, triglyceride cao"},
    {"name": "Bệnh mạch vành", "desc": "Động mạch vành hẹp, đau thắt ngực"},
    {"name": "Nhồi máu cơ tim", "desc": "Động vành bị tắc, cấp cứu"},
    {"name": "Đột quỵ", "desc": "Não không được máu nuôi, cấp cứu"},
    {"name": "Hen suyễn", "desc": "Đường thở hẹp, khó thở, ho"},
    {"name": "Bệnh phổi tắc nghẽn mãn tính", "desc": "Phổi tổn thương, khó thở mãn tính"},
    {"name": "Viêm mũi dị ứng", "desc": "Dị ứng, hắt hơi, ngứa mũi"},
    {"name": "Mày đay", "desc": "Dị ứng da, phát ban đỏ ngứa"},
    {"name": "Viêm da cơ địa", "desc": "Da khô, ngứa, viêm mãn tính"},
    {"name": "Vẩy nến", "desc": "Bệnh da mãn tính, vảy trắng"},
    {"name": "Trầm cảm", "desc": "Tâm trạng thấp, mất hứng thú, mệt mỏi"},
    {"name": "Rối loạn lo âu", "desc": "Lo lắng quá mức, bồn chồn"},
    {"name": "Rối loạn giấc ngủ", "desc": "Mất ngủ, ngủ không sâu"},
    {"name": "Bệnh Alzheimer", "desc": "Sa sút trí tuệ, quên lập"},
    {"name": "Bệnh Parkinson", "desc": "Run, cứng cơ, di chuyển chậm"},
    {"name": "Ung thư phổi", "desc": "Ung thư phổi, ho kéo dài, ho ra máu"},
    {"name": "Ung thư vú", "desc": "Ung thư vú, có thể sờ thấy khối u"},
    {"name": "Ung thư dạ dày", "desc": "Ung thư dạ dày, đau bụng, sụt cân"},
    {"name": "Ung thư gan", "desc": "Ung thư gan, đau bụng, vàng da"},
    {"name": "Ung thư đại tràng", "desc": "Ung thư ruột già, thay đổi đi cầu"},
    {"name": "Bệnh gút", "desc": "Acid uric cao, khớp sưng đỏ đau"},
    {"name": "Suy thận mãn", "desc": "Thận suy, cần lọc máu"},
    {"name": "Viêm tụy", "desc": "Tụy viêm, đau bụng dữ dội"},
    {"name": "Viêm ruột", "desc": "Viêm ruột, đau bụng, tiêu chảy"},
]

# ===== TRIỆU CHỨNG =====
SYMPTOMS = [
    ("Sốt", "Sốt có thể do nhiễm khuẩn, virus, hoặc viêm. Sốt >38.5°C kéo dài >3 ngày cần đi khám."),
    ("Đau đầu", "Đau đầu có nhiều nguyên nhân: căng thẳng, migraine, viêm xoang, cao huyết áp."),
    ("Ho", "Ho có thể do cảm, viêm họng, viêm phế quản, dị ứng, hoặc bệnh phổi."),
    ("Khó thở", "Khó thở có thể do hen, bệnh tim, loạn thông khí phổi. Cần khám ngay."),
    ("Đau ngực", "Đau ngực có thể do tim, phổi, hoặc dạ dày. Cần cấp cứu nếu đau dữ dội."),
    ("Đau bụng", "Đau bụng có nhiều nguyên nhân. Đau dữ dội, kèm nôn ói cần khám ngay."),
    ("Tiêu chảy", "Tiêu chảy thường do virus, có thể do nhiễm khuẩn. Cần bù nước."),
    ("Buồn nôn", "Buồn nôn do nhiều nguyên nhân: dạ dày, thai nghén, đau đầu."),
    ("Chóng mặt", "Chóng mặt do nhiều nguyên nhân: tai, huyết áp, thiếu máu."),
    ("Mệt mỏi", "Mệt mỏi kéo dài có thể do thiếu máu, tuyến giáp, trầm cảm."),
    ("Sụt cân", "Sụt cân không rõ nguyên nhân cần khám để loại trừ bệnh ác tính."),
    ("Ngứa", "Ngứa do dị ứng, bệnh da, hoặc bệnh nội tiết."),
    ("Phát ban", "Phát ban da do dị ứng, nhiễm virus, hoặc bệnh autoimmue."),
    ("Vàng da", "Vàng da do viêm gan, sỏi mật, hoặc ung thư. Cần khám ngay."),
    ("Phù", "Phù do suy tim, suy thận, hoặc thiếu protein."),
]

# ===== THUỐC (mở rộng) =====
DRUGS_VN = [
    {"name": "Augmentin", "desc": "Kháng sinh Amoxicillin + Clavulanic acid"},
    {"name": "Klacid", "desc": "Kháng sinh Clarithromycin"},
    {"name": "Zinnat", "desc": "Kháng sinh Cefuroxime"},
    {"name": "Tavanic", "desc": "Kháng sinh Levofloxacin"},
    {"name": "Ciproxin", "desc": "Kháng sinh Ciprofloxacin"},
    {"name": "Telfast", "desc": "Thuốc dị ứng Fexofenadine"},
    {"name": "Singulair", "desc": "Thuốc hen Montelukast"},
    {"name": "Ventolin", "desc": "Thuốc giãn phế quản Salbutamol"},
    {"name": "Seretide", "desc": "Thuốc hít steroid + giãn phế quản"},
    {"name": "Spiriva", "desc": "Thuốc hít cho COPD Tiotropium"},
    {"name": "Lyrica", "desc": "Thuốc đau thần kinh Pregabalin"},
    {"name": "Neurontin", "desc": "Thuốc đau thần kinh Gabapentin"},
    {"name": "Zoloft", "desc": "Thuốc trầm cảm Sertraline"},
    {"name": "Cipramil", "desc": "Thuốc trầm cảm Citalopram"},
    {"name": "Effexor", "desc": "Thuốc trầm cảm Venlafaxine"},
    {"name": "Rivotril", "desc": "Thuốc an thần Clonazepam"},
    {"name": "Stesol", "desc": "Thuốc đau thần kinh Carbamazepine"},
    {"name": "Keppra", "desc": "Thuốc động kinh Levetiracetam"},
    {"name": "Valproate", "desc": "Thuốc động kinh Valproic acid"},
    {"name": "Nexium", "desc": "Thuốc dạ dày Esomeprazole"},
    {"name": "Motilium", "desc": "Thuốc chống nôn Domperidone"},
    {"name": "Normagut", "desc": "Thuốc tiêu chảy Bacillus clausii"},
    {"name": "Entero", "desc": "Thuốc tiêu chảy Racecadotril"},
    {"name": "Forlax", "desc": "Thuốc táo bón Macrogol"},
    {"name": "Duphalac", "desc": "Thuốc táo bón Lactulose"},
    {"name": "Mylanta", "desc": "Thuốc kháng acid dạ dày"},
    {"name": "Gaviscon", "desc": "Thuốc trào ngược Alginate"},
    {"name": "Cozaar", "desc": "Thuốc hạ áp Losartan"},
    {"name": "Coveram", "desc": "Thuốc hạ áp Perindopril + Amlodipine"},
    {"name": "Tenormin", "desc": "Thuốc hạ áp Atenolol"},
    {"name": "Isordil", "desc": "Thuốc đau thắt ngực Isosorbide dinitrate"},
    {"name": "Cordarone", "desc": "Thuốc nhịp tim Amiodarone"},
    {"name": "Plavix", "desc": "Thuốc chống kết tập tiểu cầu Clopidogrel"},
    {"name": "Lovenox", "desc": "Thuốc chống đông Enoxaparin"},
    {"name": "Crestor", "desc": "Thuốc hạ mỡ Rosuvastatin"},
    {"name": "Vaslip", "desc": "Thuốc hạ mỡ Simvastatin"},
    {"name": "Tricor", "desc": "Thuốc hạ triglyceride Fenofibrate"},
    {"name": "Ezetrol", "desc": "Thuốc hạ cholesterol Ezetimibe"},
    {"name": "Glucophage", "desc": "Thuốc đái tháo đường Metformin"},
    {"name": "Diamicron", "desc": "Thuốc đái tháo đường Gliclazide"},
    {"name": "Januvia", "desc": "Thuốc đái tháo đường Sitagliptin"},
    {"name": "Jardiance", "desc": "Thuốc đái tháo đường Empagliflozin"},
    {"name": "Ozempic", "desc": "Thuốc đái tháo đường Semaglutide"},
    {"name": "Victoza", "desc": "Thuốc đái tháo đường Liraglutide"},
    {"name": "Basaglar", "desc": "Thuốc tiêm insulin Basal"},
    {"name": "Novorapid", "desc": "Thuốc tiêm insulin nhanh"},
    {"name": "Lantus", "desc": "Thuốc tiêm insulin long-acting"},
    {"name": "Mediators", "desc": "Thuốc đau xơ cơ Duloxetine"},
    {"name": "Cyclobenzaprine", "desc": "Thuốc giãn cơ"},
]

# ===== GENERATE =====
# Disease Q&A
for disease in DISEASES_VN:
    result.append({
        "question": f"{disease['name']} la gi?",
        "answer": f"{disease['name']}: {disease['desc']}. {D}",
        "source": "synthetic_v2"
    })
    result.append({
        "question": f"Trieu chung benh {disease['name']}?",
        "answer": f"Cac trieu chung cua {disease['name']}: {disease['desc']}. {D}",
        "source": "synthetic_v2"
    })

# Symptoms Q&A
for symptom, desc in SYMPTOMS:
    result.append({
        "question": f"{symptom} nguyen nhan gi?",
        "answer": f"{symptom}: {desc} {D}",
        "source": "synthetic_v2"
    })
    result.append({
        "question": f"Khi nao can di kham ve trieu chung {symptom}?",
        "answer": f"{symptom}: {desc} {D}",
        "source": "synthetic_v2"
    })

# Drug Q&A
for drug in DRUGS_VN:
    result.append({
        "question": f"Thuoc {drug['name']} la gi?",
        "answer": f"{drug['name']}: {drug['desc']}. {D}",
        "source": "synthetic_v2"
    })
    result.append({
        "question": f"Cach su dung thuoc {drug['name']}?",
        "answer": f"Thuoc {drug['name']}: {drug['desc']}. {D}",
        "source": "synthetic_v2"
    })

# Save
output_path = r"C:\NDT\PJ\MediSign_AI\data\training_raw\synthetic_v2.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Generated {len(result)} synthetic V2 records")
