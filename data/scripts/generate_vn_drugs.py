# -*- coding: utf-8 -*-
"""Generate THÊM dữ liệu thuốc - focus vào VIỆT NAM drug market.
Không trùng với dữ liệu có sẵn.
"""
import json
import random

random.seed(123)

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

result = []

# ===== THUỐC PHỔ BIẾN TẠI VIỆT NAM - chi tiết =====
DRUGS_VN = [
    # Giảm đau, hạ sốt
    {"name": "Paracetamol 500mg", "brand": "Hapacol, Efferalgan, Tylenol, Panadol", "price": "3.000-15.000 đ/viên", "uses": "Hạ sốt, giảm đau nhẹ-vừa (đau đầu, đau răng, đau cơ, đau bụng kinh)", "dose": "500-1000mg/lần, tối đa 4g/ngày", "side": "Quá liều gây tổn thương gan nguy hiểm. Dị ứng, buồn nôn.", "interact": "Rượu, Warfarin"},
    {"name": "Ibuprofen 400mg", "brand": "Advil, Motrin, Brufen, Nurofen", "price": "5.000-25.000 đ/viên", "uses": "Giảm đau, kháng viêm, hạ sốt", "dose": "400mg/lần, tối đa 1200mg/ngày", "side": "Đau dạ dày, loét, suy thận nếu dùng lâu", "interact": "Aspirin, Warfarin"},
    {"name": "Aspirin 81mg (Cardio)", "brand": "Bayer Cardio, Aspilets", "price": "5.000-10.000 đ/viên", "uses": "Phòng nhồi máu cơ tim, đột quỵ, giảm đau hạ sốt", "dose": "75-100mg/ngày (phòng), 300-900mg (giảm đau)", "side": "Xuất huyết tiêu hóa, dị ứng", "interact": "Warfarin, Clopidogrel"},
    {"name": "Diclofenac", "brand": "Cataflam, Voltaren", "price": "10.000-30.000 đ/viên", "uses": "Giảm đau khớp, viêm khớp, đau sau phẫu thuật", "dose": "25-50mg x 2-3 lần/ngày", "side": "Đau dạ dày, tăng nguy cơ tim mạch", "interact": "Aspirin, Warfarin"},

    # Kháng sinh
    {"name": "Amoxicillin 500mg", "brand": "Amoxil, Clamoxyl, Amox/KCL", "price": "5.000-15.000 đ/viên", "uses": "Nhiễm khuẩn hô hấp, tai mũi họng, tiết niệu", "dose": "500mg x 3 lần/ngày", "side": "Tiêu chảy, phát ban, dị ứng nặng", "interact": "Thuốc tránh thai"},
    {"name": "Azithromycin 250mg", "brand": "Zithromax, Sumamed, Azithro", "price": "15.000-40.000 đ/viên", "uses": "Nhiễm khuẩn hô hấp, da, tiết niệu, STDs", "dose": "Ngày 1: 500mg, Ngày 2-5: 250mg/ngày", "side": "Buồn nôn, tiêu chảy, đau bụng", "interact": "Digoxin"},
    {"name": "Ciprofloxacin 500mg", "brand": "Ciproxin, Ciplox, Ciflox", "price": "10.000-30.000 đ/viên", "uses": "Nhiễm khuẩn tiết niệu, tiêu chảy, viêm phổi", "dose": "250-500mg x 2 lần/ngày", "side": "Viêm gân, đứt gân, tiêu chảy", "interact": "Tizanidine, Theophylline"},
    {"name": "Metronidazole 250mg", "brand": "Flagyl, Metronid, Metrogyl", "price": "3.000-10.000 đ/viên", "uses": "Nhiễm khuẩn âm đạo, ruột, viêm lộ trình", "dose": "250-500mg x 3 lần/ngày", "side": "Buồn nôn, metallic taste, đầu óc quay", "interact": "Rượu, Warfarin"},
    {"name": "Doxycycline 100mg", "brand": "Doxycycline, Doxylets", "price": "5.000-15.000 đ/viên", "uses": "Viêm acnes, sốt xuất huyết, nhiễm khuẩn", "dose": "100mg x 1-2 lần/ngày", "side": "Buồn nôn, nhạy cảm ánh sáng, viêm thực quản", "interact": "Thuốc tránh thai"},
    {"name": "Clarithromycin 250mg", "brand": "Klacid, Biaxin, Clacid", "price": "30.000-60.000 đ/viên", "uses": "Nhiễm khuẩn hô hấp, H. pylori", "dose": "250mg x 2 lần/ngày", "side": "Buồn nôn, tiêu chảy, đắng miệng", "interact": "Statins, Carbamazepine"},

    # Tiêu hóa
    {"name": "Omeprazole 20mg", "brand": "Losec, Ome, Omeprazole Stada", "price": "3.000-15.000 đ/viên", "uses": "Loét dạ dày, trào ngược GERD, đau dạ dày", "dose": "20mg x 1-2 lần/ngày, trước ăn 30 phút", "side": "Đau đầu, tiêu chảy, thiếu B12 (dùng lâu)", "interact": "Clopidogrel"},
    {"name": "Pantoprazole 40mg", "brand": "Pantorc, Somac, Pantoloc", "price": "15.000-40.000 đ/viên", "uses": "Tương tự Omeprazole, ít tương tác hơn", "dose": "40mg/ngày", "side": "Đau đầu, tiêu chảy", "interact": "Ít tương tác"},
    {"name": "Domperidone 10mg", "brand": "Motilium, Domperidone", "price": "5.000-15.000 đ/viên", "uses": "Buồn nôn, nôn, đầy bụng, trào ngược", "dose": "10mg x 3 lần/ngày, tối đa 30mg", "side": "Khô miệng, đau đầu. Hiếm: rối loạn nhịp", "interact": "Amiodarone, Erythromycin"},
    {"name": "Phloroglucinol", "brand": "Spasfon, Phloroglucinol", "price": "5.000-15.000 đ/viên", "uses": "Co thắt đường tiêu hóa, đau bụng, sốc ruột", "dose": "40-80mg/lần khi đau", "side": "Buồn nôn, dị ứng da", "interact": "Ít tương tác"},
    {"name": "Menbuton", "brand": "Ursocomm, Liverpol", "price": "10.000-30.000 đ/viên", "uses": "Kích thích tiêu hóa, đầy bụng, khó tiêu", "dose": "1-2 viên x 3 lần/ngày sau ăn", "side": "Buồn nôn, tiêu chảy nhẹ", "interact": "Ít tương tác"},

    # Tim mạch
    {"name": "Amlodipine 5mg", "brand": "Norvasc, Amlor, Amlodipine", "price": "5.000-20.000 đ/viên", "uses": "Tăng huyết áp, đau thắt ngực", "dose": "5-10mg/ngày", "side": "Phù chân, đỏ mặt, đau đầu, chóng mặt", "interact": "Diltiazem, Simvastatin"},
    {"name": "Losartan 50mg", "brand": "Cozaar, Losartan Stada, Losar", "price": "10.000-30.000 đ/viên", "uses": "Tăng huyết áp, bảo vệ thận đái tháo đường", "dose": "50-100mg/ngày", "side": "Chóng mặt, tăng kali máu, suy thận", "interact": "Spironolactone, NSAIDs"},
    {"name": "Bisoprolol 5mg", "brand": "Concor, Bisoprolol", "price": "10.000-30.000 đ/viên", "uses": "Tăng huyết áp, suy tim, rối loạn nhịp", "dose": "2.5-10mg/ngày", "side": "Mệt mỏi, nhịp chậm, lạnh tay chân", "interact": "Verapamil, Digoxin"},
    {"name": "Amlodipine 5mg + Lisinopril 10mg", "brand": "Lisonel, CoAmlor, Tenbless", "price": "20.000-50.000 đ/viên", "uses": "Tăng huyết áp độ khó trị", "dose": "1 viên/ngày", "side": "Phù, ho khan, chóng mặt", "interact": "Tương tự 2 thành phần"},
    {"name": "Atorvastatin 20mg", "brand": "Lipitor, Atorvastatin, Tonva", "price": "15.000-40.000 đ/viên", "uses": "Hạ cholesterol, phòng ngừa tim mạch", "dose": "10-40mg/ngày, uống tối", "side": "Đau cơ, tăng men gan", "interact": "Erythromycin, Gemfibrozil"},
    {"name": "Rosuvastatin 10mg", "brand": "Crestor, Rosuvastatin, Rosis", "price": "20.000-60.000 đ/viên", "uses": "Hạ cholesterol mạnh, ít tương tác", "dose": "5-20mg/ngày, uống tối", "side": "Đau cơ, đau đầu", "interact": "Ít tương tác"},

    # Đái tháo đường
    {"name": "Metformin 500mg", "brand": "Glucophage, Metformin, Metfogamma", "price": "5.000-15.000 đ/viên", "uses": "Đái tháo đường type 2 - thuốc đầu tay", "dose": "500mg x 1-2 lần/ngày, tối đa 2000mg", "side": "Buồn nôn, tiêu chảy (giảm sau vài tuần)", "interact": "Rượu, Iopamidol"},
    {"name": "Gliclazide 80mg", "brand": "Diamicron, Gliclazide, Gluvik", "price": "10.000-30.000 đ/viên", "uses": "Đái tháo đường type 2 khi Metformin không đủ", "dose": "40-80mg x 2 lần/ngày", "side": "Hạ đường huyết, tăng cân", "interact": "NSAIDs, Insulin"},
    {"name": "Januvia (Sitagliptin) 50mg", "brand": "Januvia, Sitagliptin", "price": "80.000-150.000 đ/viên", "uses": "Đái tháo đường type 2, tăng insulin", "dose": "50-100mg/ngày", "side": "Nhiễm khuẩn đường hô hấp, tiêu chảy", "interact": "Ít tương tác"},

    # Thần kinh
    {"name": "Diazepam 5mg", "brand": "Valium, Seduxen, Diazem", "price": "2.000-8.000 đ/viên", "uses": "Lo âu, mất ngủ, co giật, cai rượu", "dose": "2-10mg x 2-4 lần/ngày", "side": "Buồn ngủ, lú lẫn, phụ thuộc (dùng lâu)", "interact": "Rượu, Opioids"},
    {"name": "Alprazolam 0.5mg", "brand": "Xanax, Alprox, Alprazolam", "price": "5.000-15.000 đ/viên", "uses": "Rối loạn lo âu, hoảng loạn", "dose": "0.25-0.5mg x 3 lần/ngày", "side": "Buồn ngủ, phụ thuộc, giảm trí nhớ", "interact": "Rượu, Opioids"},
    {"name": "Sertraline 50mg", "brand": "Zoloft, Sertraline, Serlift", "price": "10.000-30.000 đ/viên", "uses": "Trầm cảm, rối loạn lo âu, OCD", "dose": "25-50mg/ngày, tăng dần", "side": "Buồn nôn, mất ngủ, giảm ham muốn", "interact": "MAOIs, Tramadol"},
    {"name": "Duloxetine 30mg", "brand": "Cymbalta, Duloxetine, Dusphat", "price": "30.000-80.000 đ/viên", "uses": "Trầm cảm, đau thần kinh, xơ cơ", "dose": "30-60mg/ngày", "side": "Buồn nôn, khô miệng, tăng huyết áp", "interact": "MAOIs, NSAIDs"},
    {"name": "Pregabalin 75mg", "brand": "Lyrica, Pregabalin, Prigabin", "price": "50.000-120.000 đ/viên", "uses": "Đau thần kinh, đau xơ cơ, động kinh", "dose": "75mg x 2 lần/ngày", "side": "Chóng mặt, buồn ngủ, tăng cân", "interact": "Opioids, Benzodiazepine"},
    {"name": "Amitriptyline 25mg", "brand": "Amitriptyline, Tryptizol", "price": "3.000-10.000 đ/viên", "uses": "Trầm cảm, đau thần kinh, mất ngủ", "dose": "25-75mg/ngày", "side": "Khô miệng, buồn ngủ, táo bón, tăng cân", "interact": "MAOIs, Digoxin"},

    # Dị ứng
    {"name": "Cetirizine 10mg", "brand": "Zyrtec, Cetirizine, Cetina", "price": "3.000-15.000 đ/viên", "uses": "Dị ứng, ngứa, viêm mũi dị ứng, mày đay", "dose": "10mg/ngày (người lớn), 5mg (trẻ)", "side": "Buồn ngủ nhẹ, khô miệng", "interact": "Rượu, thuốc ngủ"},
    {"name": "Loratadine 10mg", "brand": "Claritin, Loratadine, Loratin", "price": "3.000-10.000 đ/viên", "uses": "Dị ứng, ít gây buồn ngủ", "dose": "10mg/ngày", "side": "Ít buồn ngủ, đau đầu", "interact": "Ít tương tác"},
    {"name": "Fexofenadine 180mg", "brand": "Telfast, Allegra, Fexofenadine", "price": "10.000-30.000 đ/viên", "uses": "Dị ứng, không gây buồn ngủ", "dose": "180mg/ngày", "side": "Đau đầu, buồn nôn", "interact": "Erythromycin, Antacids"},

    # Hô hấp
    {"name": "Salbutamol (Ventolin)", "brand": "Ventolin, Ai-10, Asmol", "price": "30.000-80.000 đ/bình", "uses": "Hen, COPD, giãn phế quản cấp cứu", "dose": "1-2 nhát khi khó thở, tối đa 8 nhát/ngày", "side": "Run tay, tim đập nhanh, chóng mặt", "interact": "Beta-blockers"},
    {"name": "Montelukast 10mg", "brand": "Singulair, Montelukast, Montel", "price": "40.000-100.000 đ/viên", "uses": "Phòng hen, viêm mũi dị ứng", "dose": "10mg/ngày (tối)", "side": "Đau đầu, đau bụng. Hiếm: thay đổi hành vi", "interact": "Phenobarbital"},
    {"name": "Methylprednisolone 4mg", "brand": "Medrol, Methylprednisolone", "price": "5.000-15.000 đ/viên", "uses": "Viêm, dị ứng nặng, hen, bệnh autoimmue", "dose": "4-40mg/ngày tùy bệnh", "side": "Tăng cân, cao huyết áp, loãng xương (dùng lâu)", "interact": "NSAIDs, Vaccines"},
    {"name": "Acetylcysteine (NAC)", "brand": "Mucomyst, Acetylcysteine", "price": "10.000-30.000 đ/viên", "uses": "Làm loãng đờm, giải độc paracetamol", "dose": "200mg x 3 lần/ngày (ho), uống ngay khi ngộ độc", "side": "Buồn nôn, nôn, dị ứng", "interact": "Kháng sinh"},

    # Other
    {"name": "Prednisone 5mg", "brand": "Prednisone, Prednisolone", "price": "2.000-5.000 đ/viên", "uses": "Viêm khớp, dị ứng, hen, bệnh autoimmue", "dose": "5-60mg/ngày tùy bệnh", "side": "Tăng cân, cao huyết áp, loãng xương (lâu)", "interact": "NSAIDs, Vaccines"},
    {"name": "Hydroxyzine 25mg", "brand": "Atarax, Hydroxyzine", "price": "5.000-15.000 đ/viên", "uses": "Dị ứng, ngứa, lo âu, mất ngủ", "dose": "25-50mg x 3 lần/ngày", "side": "Buồn ngủ, khô miệng, đau đầu", "interact": "Rượu, thuốc ngủ"},
    {"name": "Espravi (Salmeterol/Fluticasone)", "brand": "Seretide, Symbicort", "price": "150.000-400.000 đ/bình", "uses": "Hen, COPD kiểm soát lâu dài", "dose": "2 nhát x 2 lần/ngày", "side": "Nấm miệng, khàn giọng, đau đầu", "interact": "Beta-blockers"},
]

# Drug interaction pairs - focus on VIETNAM commonly used drugs
INTERACTIONS = [
    ("Warfarin", "Aspirin", "Tăng nguy cơ xuất huyết nặng. Theo dõi INR."),
    ("Warfarin", "Paracetamol", "Paracetamol liều cao tăng tác dụng Warfarin."),
    ("Metformin", "Rượu", "Tăng nguy cơ NHIỄM TOAN LACTIC - NGUY HIỂM."),
    ("Digoxin", "Amiodarone", "Amiodarone tăng nồng độ Digoxin - giảm liều 50%."),
    ("Sildenafil", "Nitroglycerin", "HẠ HUYẾT ÁP NẶNG - TUYỆT ĐỐI tránh."),
    ("Simvastatin", "Erythromycin", "Tăng nguy cơ TIÊU CƠ VÂN - tránh dùng chung."),
    ("Lithium", "Ibuprofen", "Ibuprofen tăng nồng độ Lithium - ngộ độc."),
    ("Methotrexate", "Trimethoprim", "Tăng nguy cơ GIẢM TỦY XƯƠNG."),
    ("Clopidogrel", "Omeprazole", "Omeprazole giảm tác dụng Clopidogrel."),
    ("Atorvastatin", "Nước bưởi", "Bưởi tăng nồng độ Atorvastatin - tiêu cơ."),
    ("Sertraline", "Tramadol", "Tăng nguy cơ HỘI CHỨNG SEROTONIN."),
    ("Carbamazepine", "Thuốc tránh thai", "Carbamazepine giảm hiệu quả tránh thai."),
    ("Amlodipine", "Diltiazem", "Tăng nguy cơ phù, nhịp chậm."),
    ("Diazepam", "Rượu", "Tăng buồn ngủ, suy hô hấp."),
    ("Duloxetine", "NSAIDs", "Tăng nguy cơ xuất huyết tiêu hóa."),
]

# ===== Generate Questions =====
for drug in DRUGS_VN:
    # Price
    result.append({
        "question": f"Giá {drug['name']} bao nhiêu? Mua ở đâu?",
        "answer": f"Giá {drug['name']} (thương hiệu {drug['brand']}): khoảng {drug['price']}. Có bán tại nhà thuốc trên toàn quốc. {D}",
        "source": "vn_drugs"
    })

    # Uses
    result.append({
        "question": f"{drug['name']} dùng để làm gì? Chữa bệnh gì?",
        "answer": f"{drug['name']} có công dụng: {drug['uses']}. {D}",
        "source": "vn_drugs"
    })

    # Dose
    result.append({
        "question": f"Cách dùng {drug['name']}? Liều lượng như thế nào?",
        "answer": f"Liều dùng {drug['name']}: {drug['dose']}. {D}",
        "source": "vn_drugs"
    })

    # Side effects
    result.append({
        "question": f"Tác dụng phụ của {drug['name']} là gì?",
        "answer": f"Tác dụng phụ của {drug['name']}: {drug['side']}. {D}",
        "source": "vn_drugs"
    })

    # Interactions
    result.append({
        "question": f"{drug['name']} có tương tác với thuốc nào?",
        "answer": f"Các thuốc cần cẩn trọng khi dùng chung với {drug['name']}: {drug['interact']}. {D}",
        "source": "vn_drugs"
    })

# Drug interactions
for d1, d2, effect in INTERACTIONS:
    result.append({
        "question": f"{d1} và {d2} có tương tác với nhau không?",
        "answer": f"Có tương tác: {effect} {D}",
        "source": "vn_drug_interactions"
    })

    result.append({
        "question": f"Tôi đang uống {d1} có uống {d2} được không?",
        "answer": f"Thận trọng: {effect} {D}",
        "source": "vn_drug_interactions"
    })

# Save
output_path = r"C:\NDT\PJ\MediSign_AI\data\training_raw\vn_drugs_extended.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✓ Generated {len(result)} Vietnam drug Q&A records")
print(f"  - Drug info: {len(DRUGS_VN) * 5} Q&A")
print(f"  - Drug interactions: {len(INTERACTIONS) * 2} Q&A")
print(f"  Saved to: {output_path}")
