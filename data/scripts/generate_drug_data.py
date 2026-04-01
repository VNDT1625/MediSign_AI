# -*- coding: utf-8 -*-
"""Generate thêm dữ liệu về thuốc và tương tác thuốc.
Mở rộng từ nguồn có sẵn + synthetic data từ knowledge base.
"""
import json
import random

random.seed(42)

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

# Mở rộng database thuốc - thêm nhiều loại thuốc phổ biến tại VN
DRUGS = [
    # Giảm đau, hạ sốt, kháng viêm
    {"name": "Paracetamol", "brand": "Hapacol, Efferalgan, Tylenol", "type": "Giảm đau, hạ sốt", "uses": "Hạ sốt, giảm đau nhẹ đến vừa (đau đầu, đau răng, đau cơ, đau bụng kinh)", "dose_adult": "500-1000mg mỗi 4-6 giờ, tối đa 4g/ngày", "dose_child": "10-15mg/kg/lần mỗi 4-6 giờ", "side_effects": "Quá liều (>4g/ngày) gây tổn thương gan nghiêm trọng. Buồn nôn, nôn, đau bụng, vàng da.", "interactions": "Tránh rượu (tăng tổn thương gan). Cẩn trọng Warfarin (tăng INR).", "contra": "Suy gan nặng, thiếu G6PD, dị ứng."},
    {"name": "Ibuprofen", "brand": "Advil, Motrin, Brufen", "type": "Kháng viêm không steroid (NSAID)", "uses": "Giảm đau, kháng viêm, hạ sốt. Đau răng, đau đầu, đau khớp, viêm khớp dạng thấp.", "dose_adult": "200-400mg mỗi 4-6 giờ, tối đa 1200mg/ngày không kê đơn", "dose_child": "5-10mg/kg/lần mỗi 6-8 giờ", "side_effects": "Đau dạ dày, buồn nôn, tiêu chảy. Dùng lâu: tăng nguy cơ loét dạ dày, xuất huyết tiêu hóa, suy thận.", "interactions": "Tránh aspirin (giảm tác dụng). Tăng nguy cơ xuất huyết với warfarin, heparin. Giảm tác dụng thuốc hạ áp.", "contra": "Loét dạ dày, suy thận nặng, mang thai 3 tháng cuối, dị ứng NSAID."},
    {"name": "Aspirin", "brand": "Bayer, Cardio", "type": "NSAID, chống kết tập tiểu cầu", "uses": "Giảm đau, hạ sốt, chống kết tập tiểu cầu (phòng nhồi máu cơ tim, đột quỵ).", "dose_adult": "Giảm đau: 300-900mg mỗi 4-6 giờ. Phòng ngừa: 75-100mg/ngày", "dose_child": "Không dùng cho trẻ < 16 tuổi (hội chứng Reye)", "side_effects": "Kích thích dạ dày, buồn nôn. Xuất huyết tiêu hóa. Dị ứng.", "interactions": "Tăng nguy cơ xuất huyết với warfarin, heparin, clopidogrel. Giảm tác dụng thuốc hạ áp.", "contra": "Dị ứng, loét dạ dày, rối loạn đông máu, mang thai 3 tháng cuối."},

    # Kháng sinh
    {"name": "Amoxicillin", "brand": "Amoxil, Clamoxyl, Augmentin", "type": "Kháng sinh Penicillin", "uses": "Nhiễm khuẩn đường hô hấp, viêm họng, viêm amidan, viêm xoang, nhiễm khuẩn tiết niệu, viêm phổi, diệt H. pylori.", "dose_adult": "500mg x 3 lần/ngày hoặc 875mg x 2 lần/ngày", "dose_child": "25-50mg/kg/ngày chia 2-3 lần", "side_effects": "Tiêu chảy, buồn nôn, phát ban da. Dị ứng nặng (phù Quincke, sốc phản vệ). Nhiễm nấm Candida.", "interactions": "Giảm hiệu quả thuốc tránh thai. Tăng tác dụng Methotrexate. Probenecid tăng nồng độ Amoxicillin.", "contra": "Dị ứng Penicillin. Bạch cầu đơn nhân nhiễm khuẩn."},
    {"name": "Azithromycin", "brand": "Zithromax, Sumamed", "type": "Kháng sinh Macrolide", "uses": "Nhiễm khuẩn đường hô hấp (viêm phổi, viêm phế quản), nhiễm khuẩn da, nhiễm khuẩn tiết niệu, bệnh lây qua đường tình dục.", "dose_adult": "500mg ngày 1, sau đó 250mg/ngày các ngày 2-5", "dose_child": "10mg/kg ngày 1, sau đó 5mg/kg các ngày 2-5", "side_effects": "Buồn nôn, nôn, tiêu chảy, đau bụng. Đau đầu, rối loạn vị giác. Kéo dài QT.", "interactions": "Tránh dùng với thuốc kéo dài QT (quinidine, amiodarone). Tăng nồng độ Digoxin.", "contra": "Dị ứng Azithromycin. Bệnh gan nặng. Kéo dài QT bẩm sinh."},
    {"name": "Ciprofloxacin", "brand": "Ciproxin, Ciplox", "type": "Kháng sinh Quinolone", "uses": "Nhiễm khuẩn tiết niệu, viêm phổi, nhiễm khuẩn da, tiêu chảy nhiễm khuẩn, bệnh lây qua đường tình dục.", "dose_adult": "250-500mg x 2 lần/ngày", "dose_child": "Không khuyến cáo cho trẻ < 18 tuổi (ảnh hưởng sụn)", "side_effects": "Buồn nôn, tiêu chảy, đau bụng. Đau đầu, chóng mặt. Viêm gân, đứt gân (đặc biệt gân Achilles).", "interactions": "Tránh sữa, calcium, iron (giảm hấp thu). Tăng nguy cơ đứt gân với corticosteroids.", "contra": "Dị ứng Quinolone. Trẻ em, mang thai, cho con bú. Bệnh gân."},
    {"name": "Metronidazole", "brand": "Flagyl, Metronid", "type": "Kháng khuẩn, kháng protozoa", "uses": "Nhiễm khuẩn âm đạo, viêm lộ trình, nhiễm khuẩn ruột (C. difficile), bệnh giardia, amip, viêm phổi, nhiễm khuẩn hỗn hợp.", "dose_adult": "250-500mg x 3-4 lần/ngày", "dose_child": "7.5mg/kg x 3 lần/ngày", "side_effects": "Buồn nôn, nôn, đau bụng, tiêu chảy. Metallic taste. Đầu óc quay cuồng, dị ứng da.", "interactions": "Tránh rượu (phản ứng disulfiram - nôn, đỏ mặt, tim đập nhanh). Tăng tác dụng warfarin.", "contra": "Dị ứng. Mang thai 3 tháng đầu. Rối loạn thần kinh trung ương."},

    # Tiêu hóa
    {"name": "Omeprazole", "brand": "Losec, Ome, PPIs", "type": "Ức chế bơm proton (PPI)", "uses": "Loét dạ dày tá tràng, trào ngược dạ dày thực quản (GERD), hội chứng Zollinger-Ellison, phối hợp diệt H. pylori.", "dose_adult": "20mg x 1-2 lần/ngày, uống trước ăn 30 phút", "dose_child": "0.5-1mg/kg/ngày", "side_effects": "Đau đầu, buồn nôn, đau bụng, tiêu chảy. Dùng lâu: tăng gãy xương, thiếu B12, thiếu Mg, viêm thận.", "interactions": "Giảm hấp thu Clopidogrel (tránh phối hợp). Giảm hấp thu Ketoconazole, sắt.", "contra": "Dị ứng PPI."},
    {"name": "Pantoprazole", "brand": "Pantorc, Somac", "type": "PPI", "uses": "Tương tự Omeprazole, ít tương tác hơn.", "dose_adult": "40mg x 1-2 lần/ngày", "dose_child": "0.5-1mg/kg/ngày", "side_effects": "Tương tự Omeprazole nhưng ít hơn.", "interactions": "Ít tương tác hơn Omeprazole. Vẫn giảm hấp thu thuốc cần acid.", "contra": "Dị ứng."},
    {"name": "Domperidone", "brand": "Motilium", "type": "Chống nôn, tăng nhu động ruột", "uses": "Buồn nôn, nôn, đầy bụng, trào ngược, kém ăn do tiêu hóa chậm.", "dose_adult": "10mg x 3 lần/ngày, tối đa 30mg/ngày", "dose_child": "0.25-0.5mg/kg x 3-4 lần/ngày", "side_effects": "Khô miệng, đau đầu, tiêu chảy. Hiếm: rối loạn nhịp tim, đột tử.", "interactions": "Tránh: amiodarone, sotalol, quinidine, disopyramide, erythromycin, ketoconazole.", "contra": "U xơ gan, ruột bị tắc nghẽn, xuất huyết tiêu hóa. Không dùng kéo dài."},

    # Tim mạch
    {"name": "Amlodipine", "brand": "Norvasc, Amlor", "type": "Chẹn kênh Calci", "uses": "Tăng huyết áp, đau thắt ngực ổn định.", "dose_adult": "5-10mg/ngày", "dose_child": "0.1-0.2mg/kg/ngày", "side_effects": "Phù chân, nóng bừng mặt, đau đầu, chóng mặt, mệt mỏi.", "interactions": "Nước bưởi tăng nồng độ. Cẩn trọng thuốc chẹn beta.", "contra": "Sốc tim, hẹp van động mạch chủ nặng, huyết áp thấp."},
    {"name": "Losartan", "brand": "Cozaar, Losartan Stada", "type": "Chẹn thụ thể Angiotensin II (ARB)", "uses": "Tăng huyết áp, bảo vệ thận ở đái tháo đường, suy tim.", "dose_adult": "50-100mg/ngày", "dose_child": "0.7-1.4mg/kg/ngày", "side_effects": "Chóng mặt, tăng kali máu, suy thận. Ít ho khan hơn ACEI.", "interactions": "Tránh ACEI (tăng K). Cẩn trọng Spironolactone. NSAIDs giảm hiệu quả.", "contra": "Mang thai, hẹp động mạch thận 2 bên, tăng kali máu."},
    {"name": "Atenolol", "brand": "Tenormin, Atenol", "type": "Chẹn beta", "uses": "Tăng huyết áp, đau thắt ngực, rối loạn nhịp tim, sau nhồi máu cơ tim.", "dose_adult": "25-100mg/ngày", "dose_child": "0.5-2mg/kg/ngày", "side_effects": "Mệt mỏi, chóng mặt, chân tay lạnh, giảm nhịp tim, rối loạn cương dương.", "interactions": "Tăng tác dụng với amiodarone, digoxin. Tránh dùng với verapamil.", "contra": "Suy tim nặng, nhịp chậm, khí phế thũng, hen."},
    {"name": "Amlodipine + Lisinopril", "brand": "Lisonel, Amstadine", "type": "Phối hợp (PPI + ACEI)", "uses": "Tăng huyết áp khi cần điều trị kết hợp.", "dose_adult": "1 viên/ngày (5mg + 10mg)", "dose_child": "Không khuyến cáo", "side_effects": "Phù, ho khan, chóng mặt, đau đầu.", "interactions": "Tương tự Amlodipine và Lisinopril riêng lẻ.", "contra": "Tương tự hai thành phần."},
    {"name": "Atorvastatin", "brand": "Lipitor, Atorvastatin", "type": "Statin - hạ mỡ máu", "uses": "Hạ cholesterol LDL, triglyceride, phòng ngừa biến cố tim mạch.", "dose_adult": "10-80mg/ngày, uống buổi tối", "dose_child": "10-20mg/ngày (≥10 tuổi)", "side_effects": "Đau cơ (myalgia), tiêu cơ vân hiếm nhưng nguy hiểm. Tăng men gan. Đau đầu, rối loạn tiêu hóa.", "interactions": "Nước bưởi tăng nồng độ. Tránh Gemfibrozil (tiêu cơ). Erythromycin, Cyclosporine tăng nồng độ Statin.", "contra": "Bệnh gan hoạt động, tăng men gan > 3 lần. Mang thai, cho con bú."},
    {"name": "Rosuvastatin", "brand": "Crestor, Rosuvastatin", "type": "Statin", "uses": "Tương tự Atorvastatin, mạnh hơn, ít tương tác hơn.", "dose_adult": "5-20mg/ngày, uống buổi tối", "dose_child": "5-10mg/ngày (≥10 tuổi)", "side_effects": "Đau cơ, đau đầu, tiêu chảy.", "interactions": "Ít tương tác hơn Atorvastatin.", "contra": "Bệnh gan, tăng men gan."},

    # Đái tháo đường
    {"name": "Metformin", "brand": "Glucophage, Metformin", "type": "Thuốc đái tháo đường type 2", "uses": "Điều trị đái tháo đường type 2. Giảm đường huyết, tăng nhạy cảm insulin.", "dose_adult": "500mg x 1-2 lần/ngày, tối đa 2000-2550mg/ngày", "dose_child": "500mg x 1-2 lần/ngày (≥10 tuổi)", "side_effects": "Rối loạn tiêu hóa (buồn nôn, tiêu chảy, đau bụng) - giảm sau vài tuần. Vị kim loại. Hiếm: nhiễm toan lactic.", "interactions": "Ngưng 48h trước chụp CT cản quang. Tránh rượu (nhiễm toan lactic).", "contra": "Suy thận nặng (eGFR < 30), suy gan nặng, suy tim nặng, nhiễm toan chuyển hóa."},
    {"name": "Gliclazide", "brand": "Diamicron, Gliclazide", "type": "Kích thích tiết insulin (Sulfonylurea)", "uses": "Đái tháo đường type 2 khi Metformin không đủ.", "dose_adult": "40-80mg/ngày, có thể tăng đến 320mg/ngày", "dose_child": "Không khuyến cáo", "side_effects": "Hạ đường huyết (đặc biệt người già, bỏ ăn). Tăng cân. Buồn nôn, tiêu chảy.", "interactions": "Tăng hạ đường huyết với sulfonylurea khác, insulin, NSAIDs. Tránh rượu.", "contra": "Đái tháo đường type 1, suy gan, suy thận nặng, mang thai."},

    # Thần kinh
    {"name": "Diazepam", "brand": "Valium, Seduxen", "type": "Benzodiazepine - an thần", "uses": "Lo âu, căng thẳng, mất ngủ, co giật, cơ thắt, cai rượu.", "dose_adult": "2-10mg x 2-4 lần/ngày (tùy chỉ định)", "dose_child": "0.1-0.3mg/kg/lần", "side_effects": "Buồn ngủ, chóng mặt, lú lẫn, giảm trí nhớ. Dùng lâu: phụ thuộc, quen thuốc, hội chứng cai.", "interactions": "Tăng tác dụng với rượu, thuốc ngủ, thuốc giảm đau opioid. Giảm tác dụng thuốc động kinh.", "contra": "Suy hô hấp nặng, bệnh gan nặng, glocom góc hẹp, mang thai."},
    {"name": "Alprazolam", "brand": "Xanax, Alprox", "type": "Benzodiazepine - an thần", "uses": "Rối loạn lo âu, hoảng loạn, mất ngủ liên quan lo âu.", "dose_adult": "0.25-0.5mg x 3 lần/ngày, tối đa 4mg/ngày", "dose_child": "Không khuyến cáo", "side_effects": "Tương tự Diazepam nhưng mạnh hơn, nguy cơ phụ thuộc cao hơn.", "interactions": "Tương tự Diazepam.", "contra": "Tương tự Diazepam."},
    {"name": "Duloxetine", "brand": "Cymbalta, Duloxetine", "type": "Chống trầm cảm SNRI", "uses": "Trầm cảm, rối loạn lo ân tổng hợp, đau thần kinh ngoại vi, đau xơ cơ.", "dose_adult": "30-60mg/ngày", "dose_child": "Không khuyến cáo < 18 tuổi", "side_effects": "Buồn nôn, khô miệng, táo bón, mệt mỏi, tăng huyết áp, giảm ham muốn.", "interactions": "Tránh MAOIs (nguy cơ hội chứng serotonin). Tăng nguy cơ chảy máu với aspirin, NSAIDs, warfarin.", "contra": "Glocom góc hẹp, mang thai, cho con bú."},
    {"name": "Sertraline", "brand": "Zoloft, Sertraline", "type": "Chống trầm cảm SSRI", "uses": "Trầm cảm, rối loạn lo ân, rối loạn hoảng loạn, OCD, PTSD.", "dose_adult": "25-50mg/ngày, tăng dần đến 200mg/ngày", "dose_child": "25-50mg/ngày (≥12 tuổi)", "side_effects": "Buồn nôn, tiêu chảy, khô miệng, mất ngủ, giảm ham muốn, rối loạn cương dương.", "interactions": "Tránh MAOIs. Tăng tác dụng thuốc chống đông, NSAIDs.", "contra": "Dị ứng. Không dùng với MAOIs hoặc pimozide."},

    # Dị ứng
    {"name": "Cetirizine", "brand": "Zyrtec, Cetirizine", "type": "Kháng histamin H1 thế hệ mới", "uses": "Dị ứng, ngứa, viêm mũi dị ứng, mày đay.", "dose_adult": "10mg/ngày (1 viên)", "dose_child": "5mg/ngày (trẻ 6-12 tuổi: 5mg x 2 hoặc 10mg/ngày)", "side_effects": "Buồn ngủ nhẹ (ít hơn thế hệ cũ), khô miệng, đau đầu.", "interactions": "Tăng buồn ngủ với rượu, thuốc ngủ. Ít tương tác.", "contra": "Dị ứng Cetirizine. Suy thận nặng."},
    {"name": "Loratadine", "brand": "Claritin, Loratadine", "type": "Kháng histamin H1", "uses": "Dị ứng, ngứa, viêm mũi dị ứng, mày đay.", "dose_adult": "10mg/ngày", "dose_child": "5mg/ngày (2-12 tuổi)", "side_effects": "Ít buồn ngủ hơn Cetirizine. Đau đầu, khô miệng, mệt mỏi.", "interactions": "Tương tự Cetirizine.", "contra": "Dị ứng."},

    # hô hấp
    {"name": "Salbutamol", "brand": "Ventolin, Ai-10", "type": "Giãn phế quản beta-2", "uses": "Hen, COPD, co thắt phế quản. Giãn phế quản cấp cứu.", "dose_adult": "1-2 nhát x 3-4 lần/ngày (hít), 2-4mg x 3-4 lần/ngày (uống)", "dose_child": "1-2 nhát x 3-4 lần/ngày (hít), 0.1-0.15mg/kg x 3-4 lần/ngày (uống)", "side_effects": "Run tay, tim đập nhanh, chóng mặt, đau đầu, hypokalemia.", "interactions": "Tăng tác dụng với beta-agonist khác, xanthines. Tránh non-selective beta-blockers.", "contra": "Dị ứng. Cần thận trọng bệnh tim, cường giáp."},
    {"name": "Montelukast", "brand": "Singulair, Montelukast", "type": "Chất đối vận leukotriene", "uses": "Phòng ngừa và điều trị hen, viêm mũi dị ứng. Thay thế cho corticosteroid nhẹ.", "dose_adult": "10mg/ngày (tối)", "dose_child": "4-5mg/ngày (2-6 tuổi), 5mg/ngày (6-14 tuổi)", "side_effects": "Đau đầu, đau bụng, tiêu chảy. Hiếm: thay đổi hành vi, trầm cảm, ý tưởng tự tử.", "interactions": "Ít tương tác. Phenobarbital giảm nồng độ Montelukast.", "contra": "Dị ứng."},

    # Other
    {"name": "Prednisone", "brand": "Prednisone, Prednisolone", "type": "Corticosteroid", "uses": "Viêm khớp, viêm da, dị ứng nặng, hen, bệnh autoimmue, một số ung thư.", "dose_adult": "5-60mg/ngày tùy bệnh", "dose_child": "0.5-2mg/kg/ngày", "side_effects": "Dùng lâu: tăng cân, cao huyết áp, đái tháo đường, loãng xương, teo da, suy thượng thận.", "interactions": "Tăng nguy cơ xuất huyết với NSAIDs. Giảm tác dụng thuốc hạ áp. Vaccin không hiệu quả.", "contra": "Nhiễm khuẩn nặng chưa điều trị, nấm hệ thống, loét dạ dày."},
    {"name": "Levofloxacin", "brand": "Tavanic, Levo", "type": "Kháng sinh Quinolone", "uses": "Nhiễm khuẩn tiết niệu, viêm phổi, nhiễm khuẩn da, viêm xoang.", "dose_adult": "250-500mg/ngày", "dose_child": "Không khuyến cáo < 18 tuổi", "side_effects": "Buồn nôn, tiêu chảy. Viêm gân, đứt gân. Nhức đầu, chóng mặt.", "interactions": "Tương tự Ciprofloxacin.", "contra": "Dị ứng Quinolone. Trẻ em, mang thai, cho con bú."},
]

# Drug interactions - mở rộng
DRUG_INTERACTIONS = [
    {"drug1": "Warfarin", "drug2": "Aspirin", "effect": "Tăng nguy cơ xuất huyết nặng. Aspirin ức chế kết tập tiểu cầu + Warfarin chống đông = nguy cơ chảy máu nguy hiểm.", "recommendation": "Tránh phối hợp trừ khi có chỉ định bác sĩ. Nếu cần, theo dõi sát INR và dấu hiệu chảy máu."},
    {"drug1": "Warfarin", "drug2": "Paracetamol", "effect": "Paracetamol liều cao (>2g/ngày) kéo dài tăng tác dụng Warfarin, tăng nguy cơ xuất huyết.", "recommendation": "Dùng Paracetamol liều thấp an toàn. Nếu dùng >2g/ngày >1 tuần, theo dõi INR thường xuyên."},
    {"drug1": "Metformin", "drug2": "Rượu", "effect": "Rượu tăng nguy cơ NHIỄM TOAN LACTIC nguy hiểm tính mạng (đặc biệt khi đói, uống nhiều).", "recommendation": "Tránh uống rượu khi dùng Metformin. Đặc biệt không uống rượu khi đói."},
    {"drug1": "Digoxin", "drug2": "Amiodarone", "effect": "Amiodarone tăng nồng độ Digoxin lên 70-100%, dễ gây ngộ độc Digoxin (buồn nôn, rối loạn nhịp, nhìn màu vàng).", "recommendation": "Giảm liều Digoxin 50% khi dùng chung Amiodarone. Theo dõi nồng độ Digoxin."},
    {"drug1": "Sildenafil", "drug2": "Nitroglycerin", "effect": "Cả hai giãn mạch, kết hợp gây HẠ HUYẾT ÁP NGHIÊM TRỌNG, chóng mặt, ngất, thậm chí tử vong.", "recommendation": "TUYỆT ĐỐI không dùng chung. Cách ít nhất 24-48 giờ."},
    {"drug1": "Simvastatin", "drug2": "Erythromycin", "effect": "Erythromycin ức chế CYP3A4, tăng nồng độ Simvastatin, nguy cơ TIÊU CƠ VÂN (đau cơ nặng, suy thận).", "recommendation": "Tránh dùng chung. Nếu cần, dùng Atorvastatin hoặc Rosuvastatin thay thế (ít tương tác hơn)."},
    {"drug1": "L Lithium", "drug2": "Ibuprofen", "effect": "Ibuprofen giảm thải Lithium, tăng nồng độ Lithium trong máu, gây NGỘ ĐỘC Lithium (lú lẫn, run, co giật).", "recommendation": "Tránh NSAIDs khi dùng Lithium. Dùng Paracetamol thay thế nếu cần."},
    {"drug1": "Methotrexate", "drug2": "Trimethoprim/Sulfamethoxazole", "effect": "Cả hai ức chế folate. Kết hợp tăng nguy cơ: GIẢM TỦY XƯƠNG nặng, loét miệng, tiêu chảy.", "recommendation": "Tránh dùng chung, đặc biệt liều cao Methotrexate. Nếu cần, theo dõi máu chặt chẽ."},
    {"drug1": "Clopidogrel", "drug2": "Omeprazole", "effect": "Omeprazole giảm hoạt hóa Clopidogrel, giảm tác dụng chống kết tập tiểu cầu, tăng nguy cơ ĐỘT QUỴ.", "recommendation": "Tránh Omeprazole khi dùng Clopidogrel. Dùng Pantoprazole hoặc Ranitidine thay thế."},
    {"drug1": "Atorvastatin", "drug2": "Nước bưởi", "effect": "Nước bưởi ức chế CYP3A4, tăng nồng độ Atorvastatin, nguy cơ tiêu cơ vân.", "recommendation": "Tránh nước bưởi khi dùng Atorvastatin. Ăn bưởi an toàn (ít tương tác)."},
    {"drug1": "Amlodipine", "drug2": "Diltiazem", "effect": "Cả hai chẹn kênh calcium, kết hợp tăng nguy cơ PHÙ, nhịp tim chậm, hạ huyết áp.", "recommendation": "Dùng chung được nếu theo dõi. Giảm liều Amlodipine nếu cần."},
    {"drug1": "Sertraline", "drug2": "Tramadol", "effect": "Tăng nguy cơ HỘI CHỨNG SEROTONIN (sốt, cứng cơ, lú lẫn, co giật) - nguy hiểm.", "recommendation": "Dùng chung cần thận trọng. Liều thấp, theo dõi dấu hiệu serotonin syndrome."},
    {"drug1": "Phenytoin", "drug2": "Warfarin", "effect": "Phenytoin vừa tăng vừa giảm tác dụng Warfarin (phức tạp), khó dự đoán.", "recommendation": "Theo dõi INR thường xuyên khi thay đổi liều Phenytoin."},
    {"drug1": "Carbamazepine", "drug2": "Thuốc tránh thai", "effect": "Carbamazepine tăng chuyển hóa estrogen, giảm hiệu quả THUỐC TRÁNH THAI.", "recommendation": "Dùng biện pháp tránh thai bổ sung (condom). Thay bằng thuốc không ảnh hưởng nếu có thể."},
]

# Generate Q&A
result = []

# 1. Drug information Q&A
for drug in DRUGS:
    # Công dụng
    result.append({
        "question": f"{drug['name']} ({drug['brand']}) dùng để làm gì?",
        "answer": f"{drug['name']} ({drug['type']}) có công dụng: {drug['uses']}. {D}",
        "source": "drug_db"
    })

    # Liều dùng người lớn
    result.append({
        "question": f"Liều dùng {drug['name']} cho người lớn như thế nào?",
        "answer": f"Liều dùng {drug['name']} cho người lớn: {drug['dose_adult']}. {D}",
        "source": "drug_db"
    })

    # Tác dụng phụ
    result.append({
        "question": f"Tác dụng phụ của {drug['name']} là gì?",
        "answer": f"Tác dụng phụ của {drug['name']}: {drug['side_effects']}. {D}",
        "source": "drug_db"
    })

    # Tương tác
    result.append({
        "question": f"{drug['name']} tương tác với thuốc nào?",
        "answer": f"Tương tác của {drug['name']}: {drug['interactions']}. {D}",
        "source": "drug_db"
    })

    # Chống chỉ định
    result.append({
        "question": f"Ai không nên dùng {drug['name']}?",
        "answer": f"Chống chỉ định của {drug['name']}: {drug['contra']}. {D}",
        "source": "drug_db"
    })

    # Liều dùng trẻ em
    if drug['dose_child'] and 'Không' not in drug['dose_child']:
        result.append({
            "question": f"Liều dùng {drug['name']} cho trẻ em?",
            "answer": f"Liều dùng {drug['name']} cho trẻ em: {drug['dose_child']}. {D}",
            "source": "drug_db"
        })

# 2. Drug interactions Q&A
for inter in DRUG_INTERACTIONS:
    result.append({
        "question": f"{inter['drug1']} và {inter['drug2']} có tương tác không?",
        "answer": f"CÓ. Tương tác giữa {inter['drug1']} và {inter['drug2']}: {inter['effect']}. Khuyến cáo: {inter['recommendation']}. {D}",
        "source": "drug_interaction"
    })

    result.append({
        "question": f"Uống {inter['drug1']} với {inter['drug2']} có an toàn không?",
        "answer": f"KHÔNG AN TOÀN. {inter['effect']}. {inter['recommendation']}. {D}",
        "source": "drug_interaction"
    })

# Save
output_path = r"C:\NDT\PJ\MediSign_AI\data\training_raw\drug_medicine_qa.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✓ Generated {len(result)} drug Q&A records")
print(f"  - Drug info: {len(DRUGS) * 5 + (len(DRUGS) // 2)} Q&A")
print(f"  - Drug interactions: {len(DRUG_INTERACTIONS) * 2} Q&A")
print(f"  Saved to: {output_path}")
