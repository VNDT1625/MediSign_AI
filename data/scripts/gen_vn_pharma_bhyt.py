# -*- coding: utf-8 -*-
"""Tạo Q&A về thuốc phổ biến VN, BHYT, hệ thống y tế VN, sơ cứu."""
import json, random
random.seed(43)

D = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."
result = []

# ===== THUỐC PHỔ BIẾN TẠI VIỆT NAM =====
DRUGS = [
  {"name":"Paracetamol (Hapacol, Efferalgan, Tylenol)","cong_dung":"Hạ sốt, giảm đau nhẹ đến vừa (đau đầu, đau răng, đau cơ, đau bụng kinh). Thuốc hạ sốt an toàn nhất cho trẻ em và phụ nữ mang thai.","lieu_dung":"Người lớn: 500-1000mg mỗi 4-6 giờ, tối đa 4g/ngày. Trẻ em: 10-15mg/kg/lần mỗi 4-6 giờ. Có dạng viên, siro, đạn đặt hậu môn.","tac_dung_phu":"Ít tác dụng phụ ở liều điều trị. Quá liều (>4g/ngày người lớn) gây tổn thương gan nghiêm trọng, có thể tử vong. Triệu chứng ngộ độc: buồn nôn, nôn, đau bụng, vàng da sau 24-72 giờ.","tuong_tac":"Tránh uống rượu khi dùng Paracetamol (tăng nguy cơ tổn thương gan). Cẩn trọng khi dùng chung Warfarin (tăng INR). Không kết hợp nhiều thuốc chứa Paracetamol cùng lúc.","chong_chi_dinh":"Suy gan nặng. Thiếu men G6PD (một số chế phẩm). Dị ứng Paracetamol."},
  {"name":"Amoxicillin (Amoxil, Clamoxyl)","cong_dung":"Kháng sinh nhóm Penicillin phổ rộng. Điều trị nhiễm khuẩn đường hô hấp trên (viêm họng, viêm amidan, viêm xoang), viêm tai giữa, nhiễm khuẩn tiết niệu, viêm phổi nhẹ, diệt H. pylori.","lieu_dung":"Người lớn: 500mg x 3 lần/ngày hoặc 875mg x 2 lần/ngày trong 5-10 ngày. Trẻ em: 25-50mg/kg/ngày chia 2-3 lần. Uống trước hoặc sau ăn đều được.","tac_dung_phu":"Tiêu chảy, buồn nôn, phát ban da. Phản ứng dị ứng (mày đay, phù Quincke, sốc phản vệ ở người dị ứng Penicillin). Nhiễm nấm Candida (uống lâu).","tuong_tac":"Giảm hiệu quả thuốc tránh thai. Tăng tác dụng Methotrexate. Probenecid làm tăng nồng độ Amoxicillin.","chong_chi_dinh":"Dị ứng Penicillin. Bệnh bạch cầu đơn nhân nhiễm khuẩn (gây phát ban nặng)."},
  {"name":"Omeprazole (Losec, Ome)","cong_dung":"Thuốc ức chế bơm proton (PPI). Điều trị loét dạ dày tá tràng, trào ngược dạ dày thực quản GERD, hội chứng Zollinger-Ellison. Phối hợp trong phác đồ diệt H. pylori.","lieu_dung":"Người lớn: 20mg x 1-2 lần/ngày, uống trước bữa ăn 30 phút. Loét dạ dày: 4-8 tuần. GERD: 4-8 tuần, có thể duy trì. Diệt H. pylori: 20mg x 2 lần/ngày + 2 kháng sinh.","tac_dung_phu":"Đau đầu, buồn nôn, đau bụng, tiêu chảy. Dùng lâu dài: tăng nguy cơ gãy xương (giảm hấp thu canxi), thiếu vitamin B12, thiếu magie, viêm thận kẽ.","tuong_tac":"Giảm hấp thu Clopidogrel (tránh phối hợp, thay bằng Pantoprazole). Giảm hấp thu thuốc chống nấm Ketoconazole, sắt.","chong_chi_dinh":"Dị ứng Omeprazole hoặc các PPI khác."},
  {"name":"Metformin (Glucophage)","cong_dung":"Thuốc điều trị đái tháo đường type 2 hàng đầu. Giảm đường huyết bằng cách giảm sản xuất glucose ở gan và tăng nhạy cảm insulin. Không gây hạ đường huyết khi dùng đơn trị.","lieu_dung":"Khởi đầu 500mg x 1-2 lần/ngày (uống trong hoặc sau bữa ăn để giảm tác dụng phụ tiêu hóa). Tăng dần mỗi 1-2 tuần. Liều tối đa 2000-2550mg/ngày chia 2-3 lần.","tac_dung_phu":"Rối loạn tiêu hóa (buồn nôn, tiêu chảy, đau bụng) - thường giảm sau vài tuần. Vị kim loại trong miệng. Hiếm: nhiễm toan lactic (nguy hiểm).","tuong_tac":"Ngưng trước khi chụp CT cản quang 48 giờ (nguy cơ nhiễm toan lactic). Rượu bia tăng nguy cơ nhiễm toan lactic và hạ đường huyết.","chong_chi_dinh":"Suy thận nặng (eGFR < 30). Suy gan nặng. Suy tim nặng. Nhiễm toan chuyển hóa."},
  {"name":"Amlodipine (Norvasc, Amlor)","cong_dung":"Thuốc chẹn kênh calci điều trị tăng huyết áp và đau thắt ngực ổn định. Tác dụng kéo dài 24 giờ, chỉ cần uống 1 lần/ngày.","lieu_dung":"Khởi đầu 5mg/ngày, tăng lên 10mg/ngày nếu cần. Người già/suy gan: khởi đầu 2.5mg. Uống bất kỳ lúc nào trong ngày.","tac_dung_phu":"Phù chân (mắt cá chân), nóng bừng mặt, đau đầu, chóng mặt, mệt mỏi. Phì đại nướu răng (dùng lâu).","tuong_tac":"Cẩn trọng khi phối hợp thuốc chẹn beta (tăng ức chế tim). Nước bưởi tăng nồng độ thuốc.","chong_chi_dinh":"Sốc tim. Hẹp van động mạch chủ nặng. Huyết áp thấp."},
  {"name":"Losartan (Cozaar)","cong_dung":"Thuốc chẹn thụ thể Angiotensin II (ARB) điều trị tăng huyết áp, bảo vệ thận ở bệnh nhân đái tháo đường, suy tim.","lieu_dung":"50mg/ngày, có thể tăng 100mg/ngày. Uống bất kỳ lúc nào, không phụ thuộc bữa ăn.","tac_dung_phu":"Chóng mặt, tăng kali máu, suy thận (cần theo dõi creatinine và kali). Ít gây ho khan hơn ức chế men chuyển.","tuong_tac":"Không phối hợp với ức chế men chuyển (ACEi). Cẩn trọng với thuốc lợi tiểu giữ kali (Spironolactone). NSAIDs giảm hiệu quả hạ áp.","chong_chi_dinh":"Mang thai (gây dị tật thai nhi). Hẹp động mạch thận 2 bên. Tăng kali máu."},
  {"name":"Atorvastatin (Lipitor)","cong_dung":"Thuốc hạ mỡ máu nhóm Statin. Giảm cholesterol LDL, triglyceride, tăng HDL. Phòng ngừa biến cố tim mạch.","lieu_dung":"10-80mg/ngày, uống buổi tối. Thường bắt đầu 10-20mg cho phòng ngừa, 40-80mg cho nguy cơ cao.","tac_dung_phu":"Đau cơ (myalgia) - phổ biến nhất, tiêu cơ vân (rhabdomyolysis) hiếm nhưng nguy hiểm. Tăng men gan. Đau đầu, rối loạn tiêu hóa.","tuong_tac":"Nước bưởi tăng nồng độ thuốc. Tránh phối hợp Gemfibrozil (tăng nguy cơ tiêu cơ). Cyclosporine, Erythromycin tăng nồng độ Statin.","chong_chi_dinh":"Bệnh gan hoạt động, men gan tăng > 3 lần. Mang thai, cho con bú."},
  {"name":"Berberin","cong_dung":"Thuốc kháng khuẩn đường ruột nguồn gốc thực vật, phổ biến tại Việt Nam. Điều trị tiêu chảy do nhiễm khuẩn nhẹ, kiết lỵ, viêm ruột.","lieu_dung":"Người lớn: 100mg x 2-4 lần/ngày. Trẻ em: 5-10mg/kg/ngày chia 2-3 lần. Uống trước bữa ăn.","tac_dung_phu":"Ít tác dụng phụ. Có thể gây táo bón nếu dùng lâu. Buồn nôn nhẹ.","tuong_tac":"Có thể tương tác với thuốc hạ đường huyết (tăng tác dụng hạ đường). Giảm hấp thu Cyclosporine.","chong_chi_dinh":"Phụ nữ mang thai (có thể gây co tử cung). Trẻ sơ sinh (tăng bilirubin gián tiếp gây vàng da nhân)."},
]

DRUG_QA_TYPES = [
    ("cong_dung", ["{name} dùng để làm gì?", "Công dụng của {name}?", "Khi nào nên uống {name}?", "{name} chữa bệnh gì?"]),
    ("lieu_dung", ["Liều dùng {name} như thế nào?", "Uống {name} bao nhiêu mg?", "Cách dùng {name} đúng cách?", "{name} uống ngày mấy lần?"]),
    ("tac_dung_phu", ["Tác dụng phụ của {name}?", "{name} có tác dụng phụ gì?", "Uống {name} có hại gì không?", "Phản ứng bất lợi khi dùng {name}?"]),
    ("tuong_tac", ["{name} tương tác với thuốc nào?", "Khi uống {name} cần tránh gì?", "{name} không được kết hợp với thuốc nào?"]),
    ("chong_chi_dinh", ["Ai không được uống {name}?", "Chống chỉ định của {name}?", "Trường hợp nào không nên dùng {name}?"]),
]

for drug in DRUGS:
    for field, templates in DRUG_QA_TYPES:
        if field in drug:
            q = random.choice(templates).format(name=drug["name"])
            result.append({"question": q, "answer": drug[field] + D, "source": "vn_pharma"})

# ===== HỆ THỐNG Y TẾ VIỆT NAM / BHYT =====
BHYT_QA = [
  {"q":"Bảo hiểm y tế (BHYT) tại Việt Nam hoạt động thế nào?","a":"BHYT Việt Nam là bảo hiểm xã hội bắt buộc. Mức đóng 4.5% lương (người lao động 1.5%, doanh nghiệp 3%). Đối tượng được hỗ trợ: người nghèo, trẻ em dưới 6 tuổi, người cao tuổi. BHYT chi trả 80-100% chi phí khám chữa bệnh tùy đối tượng và tuyến điều trị."},
  {"q":"Thẻ BHYT khám ở đâu được chi trả?","a":"Khám đúng tuyến (cơ sở đăng ký ban đầu): chi trả 80-100%. Khám trái tuyến tại bệnh viện tuyến huyện: chi trả 100%. Khám trái tuyến tuyến tỉnh: chi trả 60% nội trú. Khám trái tuyến tuyến trung ương: chi trả 40% nội trú. Cấp cứu: chi trả như đúng tuyến tại mọi cơ sở y tế."},
  {"q":"Trẻ em dưới 6 tuổi có được BHYT miễn phí không?","a":"Có. Trẻ em dưới 6 tuổi được cấp thẻ BHYT miễn phí, được chi trả 100% chi phí khám chữa bệnh tại mọi cơ sở y tế công lập. Cha mẹ cần đăng ký khai sinh và làm thẻ BHYT cho trẻ tại UBND xã/phường."},
  {"q":"Hệ thống bệnh viện Việt Nam phân tuyến thế nào?","a":"Phân 4 tuyến: (1) Tuyến xã: trạm y tế xã - khám bệnh thông thường, tiêm chủng, chăm sóc sức khỏe ban đầu. (2) Tuyến huyện: bệnh viện quận/huyện - cấp cứu, điều trị nội trú, phẫu thuật đơn giản. (3) Tuyến tỉnh: bệnh viện tỉnh/thành phố - chuyên khoa sâu hơn. (4) Tuyến trung ương: Bạch Mai, Chợ Rẫy, Trung ương Huế - kỹ thuật cao nhất."},
  {"q":"Quy trình khám bệnh BHYT tại bệnh viện?","a":"Bước 1: Nộp thẻ BHYT và CMND/CCCD tại quầy tiếp nhận. Bước 2: Lấy số thứ tự, chờ khám. Bước 3: Bác sĩ khám, kê đơn thuốc hoặc chỉ định xét nghiệm. Bước 4: Làm xét nghiệm nếu có. Bước 5: Tái khám lấy kết quả. Bước 6: Nhận thuốc BHYT tại quầy thuốc bệnh viện. Đồng chi trả tùy đối tượng (thường 20%)."},
  {"q":"Chương trình Tiêm chủng mở rộng Việt Nam gồm những vaccine nào?","a":"Chương trình Tiêm chủng mở rộng (TCMR) miễn phí cho trẻ em gồm: BCG (lao) - sơ sinh, Viêm gan B - sơ sinh + 3 mũi, DPT-VGB-Hib (bạch hầu, ho gà, uốn ván, viêm gan B, Hib) - 2, 3, 4 tháng, OPV/IPV (bại liệt) - 2, 3, 4 tháng, Sởi - 9 tháng, Sởi-Rubella - 18 tháng, Viêm não Nhật Bản - 1-5 tuổi. Thai phụ: uốn ván."},
  {"q":"Số điện thoại cấp cứu y tế tại Việt Nam?","a":"Số cấp cứu y tế: 115. Ngoài ra: 113 (công an), 114 (cứu hỏa). Tổng đài tư vấn y tế: 1900 9095 (Bộ Y tế). Khi gọi 115: nêu rõ địa chỉ, tình trạng bệnh nhân, số điện thoại liên lạc. Xe cấp cứu sẽ đến trong thời gian nhanh nhất."},
  {"q":"Khám sức khỏe định kỳ nên làm những xét nghiệm gì?","a":"Khám sức khỏe định kỳ cơ bản nên gồm: Công thức máu, đường huyết lúc đói, mỡ máu (cholesterol, triglyceride), chức năng gan (ALT, AST), chức năng thận (creatinine, ure), tổng phân tích nước tiểu, X-quang phổi, siêu âm bụng tổng quát, điện tâm đồ (> 40 tuổi). Phụ nữ: Pap smear, siêu âm vú. Nam > 50: PSA (ung thư tiền liệt tuyến). Tần suất: 1 lần/năm."},
  {"q":"Thủ tục chuyển viện BHYT như thế nào?","a":"Bước 1: Bác sĩ điều trị đánh giá cần chuyển tuyến trên. Bước 2: Bệnh viện làm giấy chuyển viện (có dấu, chữ ký). Bước 3: Bệnh nhân mang giấy chuyển viện + thẻ BHYT + CCCD đến bệnh viện tuyến trên. Giấy chuyển viện có hiệu lực cho cả đợt điều trị. Trường hợp cấp cứu không cần giấy chuyển viện."},
  {"q":"Chi phí khám bệnh BHYT đồng chi trả bao nhiêu?","a":"Tùy đối tượng: Hộ nghèo, trẻ dưới 6 tuổi, người có công: đồng chi trả 0% (được chi trả 100%). Hộ cận nghèo: đồng chi trả 5%. Đối tượng khác: đồng chi trả 20%. Khám trái tuyến: đồng chi trả cao hơn. Lưu ý: trần thanh toán BHYT cho 1 lần khám không quá 40 tháng lương cơ sở."},
]

for item in BHYT_QA:
    result.append({"question": item["q"], "answer": item["a"] + D, "source": "vn_bhyt"})

# ===== SƠ CỨU THƯỜNG GẶP =====
FIRST_AID = [
  {"q":"Cách sơ cứu khi bị bỏng?","a":"Bỏng nhẹ (độ 1-2, diện tích nhỏ): Ngâm vùng bỏng vào nước mát (không lạnh) 15-20 phút. Không bôi kem đánh răng, nước mắm, mỡ. Che vết bỏng bằng gạc sạch. Uống thuốc giảm đau nếu cần. Bỏng nặng (diện rộng, bỏng điện, bỏng hóa chất, bỏng đường thở): gọi 115 ngay, che phủ vết bỏng bằng vải sạch, giữ ấm bệnh nhân."},
  {"q":"Cách xử lý khi bị rắn cắn?","a":"Giữ bình tĩnh, hạn chế vận động (để nọc không lan nhanh). Cởi bỏ đồ trang sức vùng bị cắn. Rửa vết cắn bằng nước sạch. Băng ép bất động (rắn hổ mang, cạp nong/nia) hoặc không băng ép (rắn lục). KHÔNG rạch da, hút nọc, đắp lá. Ghi nhớ đặc điểm rắn. Đưa đến cơ sở y tế có huyết thanh kháng nọc rắn ngay."},
  {"q":"Cách sơ cứu người bị đuối nước?","a":"Gọi 115 ngay. Vớt nạn nhân lên nếu an toàn (dùng dây, phao, gậy). Đặt nạn nhân nằm ngửa trên mặt phẳng. Kiểm tra ý thức, hơi thở. Nếu không thở: thực hiện hô hấp nhân tạo (CPR) - 30 ép ngực + 2 thổi ngạt, lặp lại. KHÔNG dốc ngược nạn nhân. Tiếp tục CPR cho đến khi xe cứu thương đến."},
  {"q":"Cách xử lý khi bị ngộ độc thực phẩm?","a":"Triệu chứng: buồn nôn, nôn mửa, tiêu chảy, đau bụng, sốt. Xử lý: Ngưng ăn thực phẩm nghi ngờ. Bù nước bằng oresol hoặc nước muối đường (1 muỗng cà phê muối + 8 muỗng đường/1 lít nước). Không tự ý uống thuốc cầm tiêu chảy (Loperamide) nếu nghi nhiễm khuẩn. Đến bệnh viện nếu: nôn nhiều không uống được nước, tiêu chảy > 6 lần/ngày, sốt cao, phân có máu, trẻ em, người già."},
  {"q":"Cách CPR (hồi sinh tim phổi) cơ bản?","a":"Dành cho người lớn: (1) Kiểm tra ý thức: gọi to, vỗ vai. (2) Gọi 115. (3) Kiểm tra mạch cảnh (không quá 10 giây). (4) Ép ngực: đặt gót bàn tay giữa ngực, ép sâu 5-6cm, tần số 100-120 lần/phút. (5) Thổi ngạt: ngửa đầu nâng cằm, bịt mũi, thổi 2 lần. (6) Tỷ lệ 30:2 (30 ép ngực, 2 thổi ngạt). Tiếp tục cho đến khi có nhịp tim hoặc xe cứu thương đến. Dùng AED (máy sốc điện tự động) nếu có."},
  {"q":"Cách sơ cứu gãy xương?","a":"Không di chuyển nạn nhân trừ khi nguy hiểm (cháy, sập). Cố định chi gãy bằng nẹp (thanh gỗ, bìa cứng) buộc trên và dưới vị trí gãy. Không cố nắn xương. Chườm lạnh giảm sưng. Băng ép nếu có vết thương hở (gãy xương hở). Gọi 115 hoặc đưa đến bệnh viện. Gãy xương cột sống: tuyệt đối không di chuyển, chờ cứu hộ chuyên nghiệp."},
  {"q":"Cách xử lý khi bị say nắng, say nóng?","a":"Đưa nạn nhân vào chỗ mát, thoáng gió. Cởi bớt quần áo. Lau mát bằng khăn ướt ở nách, bẹn, cổ, trán. Cho uống nước mát (không uống nước đá lạnh). Nếu hôn mê, co giật, sốt > 40°C: gọi 115 ngay - đây là cấp cứu y tế. Phòng tránh: tránh nắng 10h-15h, đội mũ, uống đủ nước, mặc quần áo thoáng."},
  {"q":"Cách xử lý vết thương chảy máu?","a":"Đeo găng tay nếu có. Rửa vết thương bằng nước sạch. Ép chặt vết thương bằng gạc/vải sạch trong 10-15 phút (không mở ra kiểm tra). Nếu máu thấm qua: đặt thêm gạc lên trên, không bỏ lớp cũ. Nâng cao chi bị thương. Băng ép. Đến bệnh viện nếu: chảy máu không cầm sau 15 phút, vết thương sâu/rộng, cần khâu, nghi tổn thương gân/thần kinh. Tiêm phòng uốn ván nếu vết thương bẩn."},
]

for item in FIRST_AID:
    result.append({"question": item["q"], "answer": item["a"] + D, "source": "vn_first_aid"})

# ===== DINH DƯỠNG VÀ LỐI SỐNG =====
NUTRITION = [
  {"q":"Chế độ ăn cho người tiểu đường type 2?","a":"Nguyên tắc: chia nhỏ bữa ăn (3 bữa chính + 2-3 bữa phụ), hạn chế tinh bột trắng (cơm trắng, bánh mì trắng, bún phở), thay bằng gạo lứt, yến mạch, khoai lang. Ăn nhiều rau xanh, protein (cá, đậu phụ, ức gà). Hạn chế đường, nước ngọt, trái cây ngọt nhiều. Trái cây ít đường tốt: ổi, bưởi, thanh long. Tránh: cơm nếp, xôi, chè, bánh kẹo, nước ngọt."},
  {"q":"Phụ nữ mang thai cần bổ sung gì?","a":"Acid folic 400mcg/ngày (trước và 3 tháng đầu thai kỳ - phòng dị tật ống thần kinh). Sắt 30-60mg/ngày từ tuần 16. Canxi 1000-1200mg/ngày. DHA 200mg/ngày (phát triển não thai nhi). Vitamin D. Iod (muối iod). Ăn đa dạng: thịt, cá, trứng, sữa, rau xanh, trái cây. Tránh: rượu bia, thuốc lá, cá chứa thủy ngân cao (cá kiếm, cá thu lớn), thức ăn sống."},
  {"q":"Trẻ em cần ăn dặm từ khi nào?","a":"Bắt đầu ăn dặm từ đủ 6 tháng tuổi (WHO khuyến cáo). Dấu hiệu sẵn sàng: trẻ ngồi vững, biết với đồ ăn, mất phản xạ đẩy lưỡi. Bắt đầu với bột loãng gồm: bột gạo + thịt/cá + rau + dầu ăn (4 nhóm thực phẩm). Tăng dần độ đặc và đa dạng. 6-8 tháng: 2 bữa/ngày. 9-11 tháng: 3 bữa. 12-24 tháng: 3 bữa chính + 2 phụ. Tiếp tục bú mẹ đến 2 tuổi."},
  {"q":"Người cao tuổi cần lưu ý gì về sức khỏe?","a":"Khám sức khỏe định kỳ 6 tháng/lần. Đo huyết áp thường xuyên. Tầm soát đái tháo đường, mỡ máu, ung thư (đại trực tràng, vú, cổ tử cung). Tiêm vaccine cúm hàng năm, phế cầu. Tập thể dục nhẹ 30 phút/ngày (đi bộ, tai chi). Phòng ngã: đi giày có đế chống trượt, thanh vịn trong nhà tắm. Bổ sung canxi + vitamin D phòng loãng xương. Uống đủ nước. Duy trì giao tiếp xã hội phòng trầm cảm."},
  {"q":"Tập thể dục bao nhiêu là đủ cho người trưởng thành?","a":"Theo WHO: 150-300 phút/tuần hoạt động cường độ vừa (đi bộ nhanh, đạp xe, bơi) hoặc 75-150 phút cường độ mạnh (chạy bộ, aerobic). Kết hợp tập sức mạnh cơ 2 lần/tuần. Giảm thời gian ngồi. Bắt đầu từ từ nếu ít vận động. Tập thể dục đều đặn giảm nguy cơ: bệnh tim mạch 30%, đái tháo đường 40%, trầm cảm 30%, ung thư 20%."},
]

for item in NUTRITION:
    result.append({"question": item["q"], "answer": item["a"] + D, "source": "vn_nutrition"})

OUT = r"C:\NDT\PJ\MediSign_AI\data\training_raw\vn_pharma_bhyt.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"Generated {len(result)} entries -> {OUT}")
