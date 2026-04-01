"""
Script tạo thêm data training cho MediSign AI
Tạo data với format instruction-tuning: instruction, input, output
"""
import json

# System instruction chung
SYSTEM_INSTRUCTION = "Bạn là MediSign AI - trợ lý y tế thông minh. Hướng dẫn: 1. Chỉ gợi ý, KHÔNG chẩn đoán chắc chắn 2. Luôn khuyên gặp bác sĩ khi không chắc 3. Trả lời rõ ràng, dễ hiểu 4. Thêm lưu ý miễn trách."

DISCLAIMER = "\n\n⚠️ Lưu ý: Đây là gợi ý sơ bộ, không thay thế khám bác sĩ."

def create_sample(input_text, output_text):
    """Tạo một sample training"""
    return {
        "instruction": SYSTEM_INSTRUCTION,
        "input": input_text,
        "output": output_text + DISCLAIMER
    }

# ==================== EMERGENCY/CẤP CỨU ====================
emergency_data = [
    # Đau ngực
    ("Tôi bị đau ngực dữ dội lan ra tay trái, có sao không?", "Đau ngực lan ra tay trái là DẤU HIỆU NGUY HIỂM - có thể nhồi máu cơ tim.\n\n🔴 HÀNH ĐỘNG NGAY:\n1. Gọi 115 cấp cứu\n2. Nếu có thuốc nitroglycerin → đặt dưới lưỡi\n3. Ngồi nghỉ, không vận động\n4. Không tự lái xe đến bệnh viện"),
    ("Đau ngực khi hít thở sâu, có phải tim không?", "Đau ngực khi hít sâu có thể là:\n- Viêm màng ngoài tim\n- Viêm phổi\n- Thuyên tắc phổi\n- Chấn thương ngực\n\n🟡 Cần khám ngay để chẩn đoán chính xác."),
    ("Tôi bị đau ngực sau khi chơi thể thao, có nguy hiểm không?", "Đau ngực sau vận động có thể:\n- Đau cơ do tập luyện\n- Đau thắt ngực (thiếu máu cơ tim)\n\n🟡 Nếu đau kéo dài >5 phút, lan ra tay/cổ → gọi 115 ngay."),
    ("Đau ngực kèm khó thở và đổ mồ hôi, phải làm sao?", "⚠️ ĐÂY LÀ DẤU HIỆU KHẨN CẤP!\n\n🔴 CÓ THỂ: Nhồi máu cơ tim\n\n🚨 HÀNH ĐỘNG NGAY:\n1. Gọi 115\n2. Nếu có aspirin (100mg) → nhai 1 viên\n3. Ngồi nghỉ, không vận động\n4. Chờ xe cấp cứu đến"),
    ("Tôi bị đau ngực bên trái kèm buồn nôn, có phải tim không?", "Đau ngực + buồn nôn có thể:\n- Nhồi máu cơ tim (đặc biệt ở nữ)\n- Viêm dạ dày\n- Viêm túi mật\n\n🔴 Nếu đau >5 phút, đổ mồ hôi → GỌI 115 NGAY!"),

    # Khó thở
    ("Tôi bị khó thở đột ngột, có nguy hiểm không?", "⚠️ KHÓ THỞ ĐỘT NGỘT LÀ KHẨN CẤP!\n\nCó thể là:\n- Thuyên tắc phổi\n- Hen/ COPD\n- Phản ứng dị ứng\n- Đau tim\n\n🚨 Gọi 115 ngay!"),
    ("Khó thở kèm thở khò khè, có phải hen không?", "Thở khò khè + khó thở có thể:\n- Hen phế quản\n- COPD\n- Viêm phổi\n- Dị ứng\n\n🟡 Đi khám để chẩn đoán và điều trị."),
    ("Tôi bị khó thở khi leo cầu thang, có sao không?", "Khó thở khi gắng sức có thể:\n- Thiếu máu cơ tim\n- Hen\n- Bệnh phổi mãn tính\n- Béo phì\n\n🟡 Đi khám nếu tình trạng kéo dài >2 tuần."),
    ("Khó thở kèm ho ra máu, có nguy hiểm không?", "⚠️ HO RA MÁU + KHÓ THỞ LÀ RẤT NGUY HIỂM!\n\nCó thể:\n- Lao phổi\n- Ung thư phổi\n- Giãn phế quản\n\n🚨 ĐI KHÁM NGAY!"),
    ("Tôi bị khó thở về đêm, phải làm sao?", "Khó thở về đêm có thể:\n- Hen\n- Suy tim\n- Trào ngược dạ dày\n- Ngưng thở khi ngủ\n\n🟡 Đi khám để chẩn đoán."),

    # Ngất xỉu
    ("Tôi bị ngất xỉu đột ngột, có nguy hiểm không?", "⚠️ NGẤT XỈU CẦN ĐƯỢC KIỂM TRA!\n\nCó thể do:\n- Rối loạn nhịp tim\n- Hạ đường huyết\n- Hạ huyết áp\n- Bệnh tim mạch\n\n🔴 Ngất kèm đau ngực, khó thở → Gọi 115!"),
    ("Bị ngất khi đứng lâu, có sao không?", "Ngất khi đứng lâu thường do:\n- Hạ huyết áp tư thế\n- Thiếu máu\n- Mất nước\n\n🟡 Uống đủ nước, đứng từ từ. Đi khám nếu tái diễn."),
    ("Ngất xỉu kèm co giật, phải làm sao?", "⚠️ NGẤT + CO GIẬT CẦN CẤP CỨU!\n\nCó thể là:\n- Động kinh\n- Nhồi máu cơ tim\n- Rối loạn nhịp tim nặng\n\n🚨 Gọi 115 ngay!"),
    ("Tôi bị chóng mặt và ngất, có bệnh gì không?", "Chóng mặt + ngất có thể:\n- Hạ đường huyết\n- Hạ huyết áp\n- Rối loạn tiền đình\n- Bệnh tim\n\n🟡 Đi khám để tìm nguyên nhân."),
    ("Ngất xỉu khi nhìn thấy máu, có sao không?", "Ngất do phản xạ (vasovagal) - không nguy hiểm.\n\n🟡 Nằm xuống, nâng chân cao. Không cần điều trị."),

    # Chảy máu
    ("Tôi bị chảy máu mũi liên tục, có nguy hiểm không?", "Chảy máu mũi thường do:\n- Chấn thương\n- Cao huyết áp\n- Rối loạn đông máu\n- Khô niêm mạc\n\n🟡 Ngửa đầu ra sau, chườm lạnh. Khám nếu >20 phút không cầm được."),
    ("Chảy máu chân không cầm được sau khi đứt, phải làm sao?", "🔴 CẦN CẤP CỨU nếu:\n- Máu phun ra thành tia\n- Băng thấm máu sau 15 phút\n- Vết đứt sâu\n\n🚨 Gọi 115 hoặc đến cấp cứu ngay!"),
    ("Tôi bị ho ra mám, có nguy hiểm không?", "⚠️ HO RA MÁU LÀ DẤU HIỆU NGUY HIỂM!\n\nCó thể:\n- Lao phổi\n- Ung thư phổi\n- Giãn phế quản\n- Viêm phổi\n\n🚨 ĐI KHÁM NGAY!"),
    ("Chảy máu răng sau khi nhổ, có sao không?", "Chảy máu răng sau nhổ:\n- Cắn chặt gạc 30-45 phút\n- Không súc miệng trong 24h\n- Không ăn nóng\n\n🟡 Nếu chảy >2 giờ hoặc máu phun → đi khám."),
    ("Tôi bị chảy máu tai, có nguy hiểm không?", "Chảy máu tai có thể do:\n- Chấn thương\n- Nhiễm trùng\n- Ung thư\n\n🔴 Là DẤU HIỆU NGUY HIỂM - đi khám ngay!"),

    # Gãy xương/Chấn thương
    ("Tôi bị ngã và đau chân không đứng được, có gãy xương không?", "⚠️ ĐAU KHÔNG ĐƯỢC SAU CHẤN THƯƠNG CẦN KIỂM TRA!\n\nDấu hiệu gãy xương:\n- Đau dữ dội\n- Sưng to\n- Biến dạng\n- Không thể chịu lực\n\n🚨 Đi cấp cứu để chụp X-quang!"),
    ("Bị gãy tay, cần làm gì trước khi đến bệnh viện?", "🚑 SƠ CỨU GÃY XƯƠNG:\n1. Không di chuyển vùng gãy\n2. Cố định bằng nẹp (gỗ, nhựa)\n3. Chườm đá giảm sưng\n4. Không tự nắn xương\n5. Đến cấp cứu ngay!"),
    ("Tôi bị bong gân mắt cá chân, có cần đi khám không?", "Bong gân mắt cá:\n- Chườm đá 15-20 phút/cách 2h\n- Băng ép\n- Nâng chân cao\n- Nghỉ ngơi\n\n🟡 Đi khám nếu:\n- Đau không giảm sau 3 ngày\n- Sưng to\n- Không thể đi lại"),
    ("Bị chấn thương đầu, có cần đi khám không?", "⚠️ CHẤN THƯƠNG ĐẦU CẦN ĐI KHÁM nếu:\n- Mất ý thức\n- Chóng mặt, nôn ói\n- Chảy máu tai/mũi\n- Lú lẫn\n- Đau đầu dữ dội\n\n🚨 Gọi 115 nếu có các dấu hiệu trên!"),
    ("Tôi bị bầm tím to sau khi va chạm, có sao không?", "Bầm tím (chảy máu dưới da):\n- Chườm đá trong 48h đầu\n- Sau 48h chườm ấm\n- Không xoa bóp mạnh\n\n🟡 Đi khám nếu:\n- Bầm to >10cm\n- Đau tăng\n- Sưng nhiều"),

    # Phản ứng dị ứng
    ("Tôi bị phản ứng dị ứng nặng sau khi uống thuốc, phải làm sao?", "⚠️ PHẢN ỨNG DỊ ỨNG NẶNG (Anaphylaxis) LÀ KHẨN CẤP!\n\nDấu hiệu:\n- Khó thở, thở khò khè\n- Sưng môi/lưỡi\n- Phát ban, ngứa toàn thân\n- Chóng mặt\n\n🚨 Gọi 115 NGAY! Tiêm epinephrine nếu có."),
    ("Bị sốc phản vệ có triệu chứng gì?", "Sốc phản vệ (anaphylaxis):\n- Khó thở\n- Sưng mặt, môi, lưỡi\n- Phát ban đỏ, ngứa\n- Chóng mặt, ngất\n- Nôn, đau bụng\n\n🔴 GỌI 115 NGAY - CẦN TIÊM EPINEPHRINE!"),
    ("Tôi bị dị ứng thức ăn, cần mang theo gì?", "🩺 VỚI DỊ ỨNG NẶNG:\n1. Tiêm epinephrine (EpiPen)\n2. Thẻ cảnh báo dị ứng\n3. Điện thoại để gọi cấp cứu\n4. Thuốc kháng histamine\n\n⚠️ Tránh thức ăn gây dị ứng!"),
    ("Dị ứng da kèm sưng môi, có nguy hiểm không?", "⚠️ SƯNG MÔI + DỊ ỨNG DA có thể là sốc phản vệ!\n\n🚨 Gọi 115 nếi khó thở hoặc sưng lan!"),
    ("Tôi bị phát ban ngứa sau khi tiêm thuốc, có sao không?", "Phát ban sau tiêm:\n- Thuốc kháng histamine (Zyrtec, Claritin)\n- Chườm mát\n- Không gãi\n\n🟡 Đi khám nếu:\n- Phát ban lan rộng\n- Sưng môi/mặt\n- Khó thở"),

    # Đột quỵ
    (" Làm sao nhận biết đột quỵ?", "🔴 DẤU HIỆU ĐỘT QUỴ (FAST):\n- Face (Mặt): Mặt một bên méo, cười không đều\n- Arm (Tay): Tay yếu, không nâng lên được\n- Speech (Nói): Nói ngọng, khó nói\n- Time (Thời gian): Gọi 115 NGAY!\n\n⚠️ ĐỘT QUỴ LÀ CẤP CỨU - MỖI PHÚT MẤT 2 TRIỆU TẾ BÀO!"),
    ("Người bị đột quỵ cần làm gì trước khi xe cấp cứu đến?", "🚑 SƠ CỨU ĐỘT QUỴ:\n1. Gọi 115 ngay!\n2. Đặt nạn nhân nằm ngửa\n3. Đầu hơi nâng cao (15-30 độ)\n4. Không cho ăn/uống\n5. Nới lỏng quần áo\n6. Theo dõi mạch, hơi thở\n7. Sẵn sàng CPR nếu cần"),
    ("Tôi bị liệt mặt một bên kèm nói ngọng, có phải đột quỵ không?", "⚠️ ĐÂY LÀ DẤU HIỆU ĐỘT QUỴ!\n\n🔴 HÀNH ĐỘNG NGAY:\n1. Gọi 115\n2. Đến bệnh viện trong 3 giờ đầu\n3. Thuốc tan huyết khối chỉ hiệu quả trong 4.5 giờ\n\n⚠️ ĐỪNG CHỜ ĐỢI - MỖI PHÚT QUÝ GIÁ!"),
    ("Đột quỵ và nhồi máu cơ tim khác nhau thế nào?", "Khác nhau:\n- Đột quỵ: Mạch máu não bị tắc/vỡ → não tổn thương\n- Nhồi máu cơ tim: Động mạch vành bị tắc → cơ tim tổn thương\n\nCả hai đều là CẤP CỨU - gọi 115!"),
    ("Nguy cơ đột quỵ cao khi nào?", "Yếu tố nguy cơ đột quỵ:\n- Cao huyết áp\n- Đái tháo đường\n- Rượu bia, hút thuốc\n- Béo phì\n- Tim mạch\n- stress\n\n🟡 Kiểm soát các yếu tố trên để phòng ngừa!"),

    # Sốt cao/Cấp cứu khác
    ("Sốt cao trên 40 độ, có nguy hiểm không?", "⚠️ SỐT >40°C RẤT NGUY HIỂM!\n\nCó thể gây:\n- Co giật\n- Tổn thương não\n- Mất nước nặng\n\n🚨 HẠ SỐT NGAY:\n1. Paracetamol 500-1000mg\n2. Chườm mát (không冰)\n3. Uống nước nhiều\n4. Đi cấp cứu nếu không hạ sốt!"),
    ("Tôi bị co giật vì sốt cao, phải làm sao?", "🔴 CO GIẬT DO SỐT - XỬ LÝ:\n1. Đặt nạn nhân nằm nghiêng\n2. Không nhét gì vào miệng\n3. Bảo vệ đầu\n4. Đợi cơn co giật hết\n5. Hạ sốt sau đó\n6. Đi khám!"),
    ("Bị rắn cắn, cần làm gì?", "🔴 RẮN CẮN - XỬ LÝ NGAY:\n1. Gọi 115\n2. Bất động chi bị cắn\n3. Không hút độc, không cắt\n4. Chườm đá giảm sưng\n5. Ghi nhận hình dạng rắn\n6. Đến bệnh viện!"),
    ("Bị ong đốt nhiều vết, có nguy hiểm không?", "⚠️ ONG ĐỐT NHIỀU VẾT CÓ THỂ GÂY SỐC!\n\nXử lý:\n1. Lấy ngòi ra (cạo ngang, không bóp)\n2. Chườm đá\n3. Uống kháng histamine\n4. Theo dõi dấu hiệu sốc\n\n🚨 Gọi 115 nếu sưng lan, khó thở!"),
    ("Tôi bị chóng mặt dữ dội kèm nói ngọng, có phải đột quỵ không?", "⚠️ CHÓNG MẶT + NÓI NGỌNG = CÓ THỂ ĐỘT QUỴ!\n\n🔴 GỌI 115 NGAY!\n\nĐây là dấu hiệu đột quỵ tiền đình hoặc đột quỵ thực sự. Phân biệt tại nhà khó - cần CT scan."),
]

# ==================== TRIỆU CHỨNG BỆNH ====================
symptom_data = [
    # Đau đầu
    ("Đau đầu kèm sốt, có sao không?", "Đau đầu + sốt có thể:\n- Cảm cúm\n- Viêm màng não (đau đầu dữ dội, cứng cổ)\n- Viêm xoang\n- Nhiễm trùng khác\n\n🟡 Đi khám nếu sốt >38.5°C hoặc đau đầu dữ dội!"),
    ("Tôi bị đau nửa đầu kèm buồn nôn, có phải migraine không?", "Triệu chứng migraine (đau nửa đầu):\n- Đau một bên đầu\n- Nhạy cảm ánh sáng/tiếng ồn\n- Buồn nôn/nôn\n- Nhìn thấy aura (chớp sáng)\n\n🟡 Đi khám để chẩn đoán và điều trị."),
    ("Đau đầu kéo dài 3 ngày không khỏi, có sao không?", "Đau đầu >3 ngày cần khám!\n\nCó thể:\n- Căng thẳng\n- Rối loạn mạch máu\n- Viêm xoang\n- Vấn đề thị lực\n- U não (ít gặp)\n\n🟡 Đi khám để tìm nguyên nhân."),
    ("Tôi bị đau đầu sau khi uống rượu, có sao không?", "Đau đầu sau rượu:\n- Mất nước\n- Độc tố từ rượu\n- Hạ đường huyết\n\n🟡 Uống nước, ăn đồ ngọt, nghỉ ngơi. Không uống rượu tiếp!"),
    ("Đau đầu khi thay đổi thời tiết, có sao không?", "Đau đầu theo thời tiết:\n- Thay đổi áp suất\n- Độ ẩm\n- Căng thẳng mạch máu\n\n🟡 Nghỉ ngơi, uống nước, thuốc giảm đau nếu cần."),

    # Đau bụng
    ("Tôi bị đau bụng dữ dội kèm nôn, có sao không?", "⚠️ ĐAU BỤNG DỮ DỘI + NÔN CẦN KHÁM NGAY!\n\nCó thể:\n- Viêm ruột thừa\n- Viêm tụy\n- Tắc ruột\n- Sỏi thận\n\n🚨 Đi cấp cứu nếu đau không chịu được!"),
    ("Đau bụng kèm tiêu chảy, nên làm gì?", "Đau bụng + tiêu chảy:\n- Ngộ độc thức ăn\n- Viêm dạ dày ruột\n- Hội chứng ruột kích thích\n\n🟡 Xử lý:\n- Uống oresol bù nước\n- Ăn cháo, cơm nát\n- Không uống sữa\n- Đi khám nếu >3 ngày"),
    ("Tôi bị đau bụng dưới kèm tiểu buốt, có sao không?", "Đau bụng dưới + tiểu buốt:\n- Nhiễm trùng đường tiết niệu\n- Sỏi bàng quang\n- Viêm bàng quang\n\n🟡 Uống nhiều nước, đi khám xét nghiệm nước tiểu."),
    ("Đau bụng kèm táo bón kéo dài, có nguy hiểm không?", "Táo bón + đau bụng:\n- Chế độ ăn thiếu chất xơ\n- Uống ít nước\n- Ít vận động\n- Tắc ruột (nếu nặng)\n\n🟡 Đi khám nếu không đi cầu >3 ngày hoặc đau dữ dội!"),
    ("Tôi bị đau bụng sau khi ăn, có phải dạ dày không?", "Đau bụng sau ăn có thể:\n- Viêm dạ dày\n- Loét dạ dày\n- Trào ngược dạ dày\n- Viêm tụy\n\n🟡 Đi khám nội soi dạ dày nếu kéo dài >2 tuần."),

    # Ho
    ("Tôi bị ho kéo dài 2 tuần, có sao không?", "Ho kéo dài >2 tuần cần khám!\n\nCó thể:\n- Viêm đường hô hấp mãn\n- Hen\n- Trào ngược dạ dày\n- Lao (nếu ho khan)\n- Ung thư phổi (ít gặp)\n\n🟡 Đi khám chụp X-quang phổi!"),
    ("Ho kèm đờm vàng/xanh, có nhiễm trùng không?", "Đờm vàng/xanh = CÓ NHIỄM TRÙNG!\n\nCó thể:\n- Viêm phổi\n- Viêm phế quản\n- Nhiễm trùng xoang\n\n🟡 Đi khám, có thể cần kháng sinh!"),
    ("Ho khan về đêm, có sao không?", "Ho khan về đêm:\n- Hen\n- Trào ngược dạ dày\n- Dị ứng\n- Giọt mũi sau họng\n\n🟡 Đi khám để tìm nguyên nhân."),
    ("Tôi bị ho kèm sốt nhẹ, có cần uống thuốc không?", "Ho + sốt nhẹ:\n- Cảm cúm\n- Viêm phế quản\n- Viêm phổi nhẹ\n\n🟡 Uống nước, nghỉ ngơi. Đi khám nếo sốt >38.5°C hoặc ho >1 tuần."),
    ("Ho ra máu một ít, có nguy hiểm không?", "⚠️ HO RA MÁU DÙ ÍT CŨNG NGUY HIỂM!\n\nCó thể:\n- Lao phổi\n- Giãn phế quản\n- Ung thư phổi\n- Viêm phổi\n\n🚨 ĐI KHÁM NGAY! chụp X-quang!"),

    # Mệt mỏi
    ("Tôi bị mệt mỏi kéo dài, có bệnh gì không?", "Mệt mỏi kéo dài có thể:\n- Thiếu máu\n- Trầm cảm\n- Bệnh tuyến giáp\n- Bệnh mãn tính\n- Thiếu vitamin D\n\n🟡 Đi khám xét nghiệm máu!"),
    ("Mệt kèm sụt cân không rõ nguyên nhân, có sao không?", "⚠️ MỆT + SỤT CÂN = DẤU HIỆU NGUY HIỂM!\n\nCó thể:\n- Ung thư\n- Bệnh tiểu đường\n- Cường giáp\n- Bệnh mãn tính nặng\n\n🚨 ĐI KHÁM NGAY!"),
    ("Tôi luôn cảm thấy mệt vào buổi sáng, có sao không?", "Mệt buổi sáng:\n- Ngủ không đủ giấc\n- Hội chứng ngưng thở khi ngủ\n- Trầm cảm\n- Thiếu vitamin\n\n🟡 Đi khám nếu kéo dài >2 tuần."),
    ("Mệt sau khi làm việc nhiều, có bình thường không?", "Mệt sau làm việc nhiều là BÌNH THƯỜNG!\n\n🟡 Nghỉ ngơi, ăn uống đủ chất, ngủ 7-8 tiếng/đêm."),
    ("Tôi bị mệt kèm đau cơ, có nhiễm virus không?", "Mệt + đau cơ:\n- Cảm cúm\n- COVID-19\n- Viêm cơ\n- Bệnh tự miễn\n\n🟡 Nghỉ ngơi, uống nước. Đi khám nếu sốt hoặc triệu chứng nặng."),

    # Triệu chứng khác
    ("Tôi bị chóng mặt khi đứng lên, có sao không?", "Chóng mặt khi đứng lên:\n- Hạ huyết áp tư thế\n- Thiếu máu\n- Mất nước\n\n🟡 Đứng lên từ từ, uống đủ nước. Đi khám nếu tái diễn."),
    ("Bị ù tai kéo dài, có sao không?", "Ù tai kéo dài:\n- Tiếp xúc tiếng ồn\n- Bệnh Meniere\n- Rối loạn tuần hoàn\n- Tác dụng thuốc\n\n🟡 Đi khám tai mũi họng!"),
    ("Tôi bị đau lưng dưới kéo dài, có sao không?", "Đau lưng dưới:\n- Đau cơ\n- Thoát vị đĩa đệm\n- Viêm khớp\n- Bệnh thận\n\n🟡 Đi khám nếu đau >2 tuần hoặc tê chân."),
    ("Bị phát ban đỏ ngứa toàn thân, có sao không?", "Phát ban ngứa:\n- Dị ứng\n- Chàm (eczema)\n- Viêm da\n- Nhiễm nấm\n\n🟡 Uống kháng histamine, thoa kem dịu. Đi khám nếu lan rộng."),
    ("Tôi bị sưng chân kèm đau, có sao không?", "Sưng chân:\n- Suy tim\n- Suy thận\n- Huyết khối tĩnh mạch\n- Tác dụng thuốc\n\n🟡 Đi khám để tìm nguyên nhân!"),
]

# ==================== TƯƠNG TÁC THUỐC ====================
medication_data = [
    ("Uống thuốc tránh thai có uống được kháng sinh không?", "MỘT SỐ KHÁNG SINH làm giảm hiệu quả thuốc tránh thai:\n- Rifampicin\n- Một số thuốc động kinh\n\n🟡 KHÁNG SINH THÔNG THƯỜNG (amoxicillin, azithromycin...) ảnh hưởng ÍT.\n\n⚠️ Dùng thêm biện pháp tránh thai khi uống kháng sinh!"),
    ("Uống thuốc cao huyết áp có uống được rượu không?", "⚠️ RƯỢU + THUỐC CAO HUYẾT ÁP NGUY HIỂM!\n\n- Tăng/tụt huyết áp đột ngột\n- Giảm tác dụng thuốc\n- Tổn thương gan\n\n❌ KHÔNG NÊN UỐNG RƯỢU khi dùng thuốc cao huyết áp!"),
    ("Thuốc giảm đau có tương tác với thuốc gì không?", "Thuốc giảm đau (NSAIDs) tương tác:\n- Aspirin: Tăng nguy cơ chảy máu\n- Thuốc chống đông: Nguy cơ chảy máu cao\n- Thuốc huyết áp: Giảm tác dụng\n- Lithium: Tăng độc tính\n\n⚠️ Hỏi bác sĩ trước khi dùng!"),
    ("Tôi uống thuốc tiểu đường có cần kiêng gì không?", "Thuốc tiểu đường:\n- ⚠️ KHÔNG bỏ bữa (hạ đường huyết)\n- Hạn chế rượu bia\n- Ăn đều đặn\n- Tránh đồ ngọt quá nhiều\n\n🟡 Theo dõi đường huyết thường xuyên!"),
    ("Uống thuốc sắt có uống được sữa không?", "❌ KHÔNG uống sữa cùng thuốc sắt!\n\nSữa, calcium làm giảm hấp thu sắt.\n\n🟡 Uống thuốc sắt:\n- 2h trước/sau sữa\n- Uống với nước cam (vitamin C tăng hấp thu)"),
    ("Thuốc kháng đông (warfarin) cần kiêng gì?", "⚠️ THUỐC KHÁNG ĐÔNG cần kiêng:\n- Rượu bia\n- Vitamin K cao (rau xanh, đặc biệt cải xoăn)\n- Aspirin, ibuprofen\n- Thực phẩm bổ sung garlic, ginkgo\n\n🟡 Theo dõi INR định kỳ!"),
    ("Uống thuốc giảm cân có tương tác không?", "Thuốc giảm cân có thể tương tác:\n- Thuốc trầm cảm (serotonin syndrome)\n- Thuốc huyết áp\n- Thuốc tiểu đường\n\n⚠️ Chỉ uống theo chỉ định bác sĩ!"),
    ("Tôi uống statin (thuốc giảm mỡ máu) có được ăn bưởi không?", "❌ KHÔNG ăn bưởi khi uống statin!\n\nBưởi làm tăng nồng độ statin trong máu → nguy cơ tổn thương cơ.\n\n🟡 Chọn loại statin tương thích hoặc tránh bưởi!"),
    ("Thuốc kháng histamine có gây buồn ngủ không?", "MỘT SỐ thuốc kháng histamine GÂY BUỒN NGỦ:\n- Diphenhydramine (Benadryl)\n- Chlorpheniramine\n\n🟡 Dùng thuốc thế hệ mới ít gây buồn ngủ:\n- Loratadine\n- Cetirizine\n- Fexofenadine"),
    ("Uống thuốc động kinh cần lưu ý gì?", "Thuốc động kinh:\n- Uống đều đặn, KHÔNG bỏ liều\n- Tác dụng phụ: chóng mặt, buồn ngủ\n- Cần xét nghiệm máu định kỳ\n- Không uống rượu\n\n⚠️ KHÔNG tự ngưng thuốc!"),
]

# ==================== ĐỘ TUỔI/GIỚI TÍNH ====================
age_gender_data = [
    # Trẻ em
    ("Trẻ 2 tuổi bị sốt 38.5 độ, cho uống thuốc gì?", "Sốt ở trẻ 2 tuổi:\n- Paracetamol liều 10-15mg/kg/lần\n- Cách 4-6 giờ nếu cần\n- Không quá 4 lần/ngày\n\n🟡 Lau mát, cho uống nhiều nước. Đi khám nếu sốt >39°C hoặc >24h!"),
    ("Trẻ sơ sinh bị sốt phải làm sao?", "⚠️ SỐT Ở TRẺ SƠ SINH (<3 tháng) RẤT NGUY HIỂM!\n\n🚨 ĐI CẤP CỨU NGAY!\n\n- Hệ miễn dịch chưa phát triển\n- Có thể nhiễm trùng nặng\n- KHÔNG tự điều trị tại nhà!"),
    ("Trẻ bị tiêu chảy có cần uống oresol không?", "Trẻ bị tiêu chảy:\n- ⚠️ oresol BẮT BUỘC bù nước\n- Pha đúng tỷ lệ\n- Cho uống từng thìa nhỏ\n- Tiếp tục cho bú/ăn bình thường\n\n🟡 Đi khám nếu tiêu chảy >2 ngày hoặc có máu!"),
    ("Trẻ bị ho có cần uống kháng sinh không?", "Trẻ ho:\n- KHÔNG tự ý dùng kháng sinh\n- Ho do virus (90%) kháng sinh vô hiệu\n- Cho uống nước, giữ ẩm đường thở\n\n🟡 Đi khám nếu sốt, khó thở hoặc ho >1 tuần."),
    ("Trẻ bị phát ban sau tiêm vaccine, có sao không?", "Phát ban sau vaccine:\n- Bình thường, là phản ứng nhẹ\n- Xuất hiện trong 24-48h\n- Tự hết sau 2-3 ngày\n\n🟡 Chườm mát, cho uống thuốc hạ sốt nếu cần."),

    # Người cao tuổi
    ("Người cao tuổi bị táo bón kéo dài, có sao không?", "Táo bón ở người cao tuổi:\n- Chất xơ, nước đầy đủ\n- Vận động nhẹ\n- Không dùng thuốc nhuận tràng thường xuyên\n\n🟡 Đi khám nếu >3 ngày không đi cầu hoặc đau bụng!"),
    ("Người cao tuổi bị chóng mặt, có nguy hiểm không?", "Chóng mặt ở người cao tuổi:\n- Nguy cơ ngã cao!\n- Rối loạn tiền đình\n- Hạ huyết áp\n- Thiếu máu não\n\n🟡 Đi khám để tìm nguyên nhân!"),
    ("Người cao tuổi bị đau khớp, nên làm gì?", "Đau khớp ở người cao tuổi:\n- Giảm cân nếu béo\n- Vận động nhẹ (đi bộ, bơi lội)\n- Chườm nóng/lạnh\n- Thuốc giảm đau theo đơn\n\n🟡 Đi khám để điều trị!"),
    ("Người cao tuổi bị mất ngủ, có sao không?", "Mất ngủ ở người cao tuổi:\n- Giữ giờ ngủ đều\n- Hạn chế caffeine\n- Không ngủ trưa quá lâu\n- Phòng ngủ thoáng mát\n\n🟡 Đi khám nếu mất ngủ kéo dài >2 tuần."),
    ("Người cao tuổi bị tiểu đêm nhiều, có bệnh không?", "Tiểu đêm ở người cao tuổi:\n- Phì đại tuyến tiền liệt (nam)\n- Bàng quang tăng hoạt\n- Tiểu đường\n- Suy thận\n\n🟡 Đi khám để chẩn đoán!"),

    # Phụ nữ mang thai
    ("Phụ nữ mang thai bị ốm nghén nặng, có sao không?", "Ốm nghén nặng (hyperemesis gravidarum):\n- Nôn >5 lần/ngày\n- Mất cân nặng\n- Mất nước\n\n🚨 CẦN ĐIỀU TRỊ tại bệnh viện!"),
    ("Phụ nữ mang thai có được uống thuốc không?", "⚠️ MANG THAI cần cẩn thận:\n- Không tự ý uống thuốc\n- Hỏi bác sĩ trước khi dùng bất kỳ thuốc nào\n- Paracetamol an toàn, NSAIDs KHÔNG\n\n🟡 Chỉ uống thuốc theo chỉ định bác sĩ!"),
    ("Phụ nữ mang thai bị sốt, có sao không?", "Sốt khi mang thai:\n- Paracetamol hạ sốt an toàn\n- Chườm mát, uống nước\n\n🚨 Đi khám ngay vì sốt cao có thể gây dị tật thai nhi!"),
    ("Phụ nữ mang thai bị đau bụng, có nguy hiểm không?", "⚠️ ĐAU BỤNG KHI MANG THAI cần khám!\n\nCó thể:\n- Thai ngoài tử cung (nếu tam cá nguyệt đầu)\n- Sảy thai\n- Bất thường tử cung\n\n🚨 Đi khám ngay để loại trừ!"),
    ("Phụ nữ mang thai bị chảy máu âm đạo, có sao không?", "⚠️ CHẢY MÁU KHI MANG THAI LÀ NGUY HIỂM!\n\n- Có thể dọa sảy\n- Nhau tiền đạo\n- Bất thường thai\n\n🚨 ĐI CẤP CỨU NGAY!"),

    # Phụ nữ
    ("Phụ nữ bị đau kinh nguyệt nặng, có sao không?", "Đau kinh nguyệt nặng có thể:\n- Lạc nội mạc tử cung\n- U xơ tử cung\n- Viêm vùng chậu\n\n🟡 Đi khám nếu đau ảnh hưởng cuộc sống!"),
    ("Phụ nữ bị rối loạn kinh nguyệt, có bệnh gì không?", "Rối loạn kinh nguyệt:\n- Căng thẳng\n- Rối loạn tuyến giáp\n- PCOS\n- Perimenopause\n\n🟡 Đi khám để tìm nguyên nhân!"),
    ("Phụ nữ tuổi tiền mãn kinh có triệu chứng gì?", "Triệu chứng tiền mãn kinh:\n- Bốc hỏa\n- Mất ngủ\n- Thay đổi tâm trạng\n- Kinh nguyệt không đều\n- Khô âm đạo\n\n🟡 Đi khám để được tư vấn!"),
    ("Phụ nữ nên khám phụ khoa định kỳ không?", "🩺 KHÁM PHỤ KHOA ĐỊNH KỲ:\n- Mỗi năm 1 lần\n- Tầm soát ung thư cổ tử cung (Pap smear)\n- Ung thư vú (tự khám + mammogram)\n- Các bệnh lây truyền qua đường tình dục\n\n⚠️ Đi khám ngay nếu có triệu chứng bất thường!"),
    ("Phụ nữ bị nấm âm đạo, có cần đi khám không?", "Nấm âm đạo:\n- Ngứa, ra khí hư đặc\n- Có thể điều trị thuốc đặt\n- Tái phát nếu không điều trị đủ\n\n🟡 Đi khám để chẩn đoán và điều trị đúng!"),

    # Nam giới
    ("Nam giới bị đau tinh hoàn, có nguy hiểm không?", "⚠️ ĐAU TINH HOÀN CẦN KHÁM NGAY!\n\nCó thể:\n- Xoắn tinh hoàn (cấp cứu)\n- Viêm tinh hoàn\n- Viêm mào tinh hoàn\n- Ung thư tinh hoàn (ít gặp)\n\n🚨 Đi khám ngay!"),
    ("Nam giới bị tiểu đêm nhiều, có bệnh gì không?", "Tiểu đêm ở nam:\n- Phì đại tuyến tiền liệt\n- Viêm tiền liệt tuyến\n- Tiểu đường\n- Bàng quang tăng hoạt\n\n🟡 Đi khám để chẩn đoán!"),
    ("Nam giới nên khám sức khỏe định kỳ không?", "🩺 KHÁM ĐỊNH KỲ CHO NAM:\n- Huyết áp, đường huyết, mỡ máu\n- Tầm soát ung thư tiền liệt (PSA)\n- Kiểm tra tinh hoàn\n- Sức khỏe tim mạch\n\n⚠️ Đặc biệt sau 40 tuổi!"),
    ("Tinh hoàn ẩn ở trẻ trai, có sao không?", "Tinh hoàn ẩn:\n- Cần phẫu thuật đưa xuống\n- Làm trước 2 tuổi\n- Nguy cơ vô sinh, ung thư\n\n🚨 Đi khám ngay để được tư vấn!"),
    ("Nam giới bị rối loạn cương cần làm gì?", "Rối loạn cương có thể do:\n- Stress, lo âu\n- Bệnh tim mạch\n- Tiểu đường\n- Thuốc\n\n🟡 Đi khám để tìm nguyên nhân và điều trị!"),
]

# ==================== DINH DƯỠNG/SỨC KHỎE ====================
nutrition_data = [
    ("Người bị tiểu đường nên ăn gì?", "🍽️ ĂN UỐNG CHO NGƯỜI TIỂU ĐƯỜNG:\n\n✅ NÊN ĂN:\n- Rau xanh, hoa quả ít đường\n- Ngũ cốc nguyên hạt\n- Thịt nạc, cá\n- Chất xơ cao\n\n❌ HẠN CHẾ:\n- Đường, tinh bột tinh chế\n- Đồ ngọt, nước ngọt\n- Gạo trắng, bánh mì trắng\n\n🟡 Ăn đều đặn, không bỏ bữa!"),
    ("Người cao huyết áp nên ăn gì?", "🍽️ ĂN CHO CAO HUYẾT ÁP:\n\n✅ NÊN ĂN:\n- Rau xanh, hoa quả\n- Cá, gà không da\n- Đậu hũ\n- Ngũ cốc nguyên hạt\n\n❌ HẠN CHẾ:\n- Muối (<5g/ngày)\n- Đồ ăn nhiều mỡ\n- Rượu bia\n\n🟡 DASH diet hiệu quả cho cao huyết áp!"),
    ("Người bị mỡ máu cao nên kiêng gì?", "🩸 MỠ MÁU CAO:\n\n❌ NÊN TRÁNH:\n- Nội tạng động vật\n- Thịt đỏ nhiều mỡ\n- Trứng (lòng đỏ)\n- Sữa nguyên kem\n- Đồ chiên rán\n\n✅ NÊN ĂN:\n- Cá (đặc biệt cá hồi)\n- Dầu olive\n- Rau xanh\n- Yến mạch"),
    ("Người bị đau dạ dày nên ăn gì?", "🍽️ ĂN KHI ĐAU DẠ DÀY:\n\n✅ NÊN ĂN:\n- Cháo, súp loãng\n- Rau luộc, hoa quả chín\n- Thịt nạc, cá hấp\n- Sữa chua\n\n❌ TRÁNH:\n- Đồ cay, chiên rán\n- Cà phê, nước có gas\n- Rượu bia, thuốc lá\n- Ăn quá no hoặc để đói\n\n🟡 Ăn ít, chia nhiều bữa!"),
    ("Người béo phì nên giảm cân thế nào?", "💪 GIẢM CÂN LÀNH MẠNH:\n\n- Giảm từ từ (0.5-1kg/tuần)\n- Giảm 500 calo/ngày\n- Tập thể dục 150 phút/tuần\n- Ngủ đủ giấc (7-8h)\n- Không nhịn ăn\n\n⚠️ Không dùng thuốc giảm cân không rõ nguồn gốc!"),
    ("Người bị thiếu máu nên ăn gì?", "🩸 ĂN ĐỂ BỔ SUNG SẮT:\n\n✅ NÊN ĂN:\n- Thịt đỏ, gan\n- Hải sản\n- Đậu, đậu lăng\n- Rau xanh đậm\n- Ngũ cốc fortified\n\n🟡 Kết hợp vitamin C để tăng hấp thu sắt!"),
    ("Người bị gout (gút) nên kiêng gì?", "⚠️ GOUT - NÊN TRÁNH:\n- Nội tạng động vật\n- Hải sản (tôm, cua, cá mòi)\n- Bia, rượu\n- Thịt đỏ\n- Nấm\n\n✅ NÊN ĂN:\n- Nước (2-3 lít/ngày)\n- Rau xanh\n- Hoa quả\n- Sữa ít béo"),
    ("Người bị suy thận nên ăn gì?", "🩺 ĂN KHI SUY THẬN:\n\n✅ NÊN ĂN:\n- Chất đạm vừa đủ\n- Rau củ (trừ khoai tây, chuối)\n- Hoa quả ít kali\n\n❌ HẠN CHẾ:\n- Muối\n- Chất đạm nhiều\n- Nước (tùy giai đoạn)\n- Kali cao\n\n🟡 Theo dõi bác sĩ dinh dưỡng!"),
    ("Người bị xương khớp nên bổ sung gì?", "🦴 XƯƠNG KHỚP:\n\n✅ BỔ SUNG:\n- Calcium (1000-1200mg/ngày)\n- Vitamin D\n- Vitamin K2\n- Glucosamine (nếu cần)\n\n✅ ĂN:\n- Sữa, phô mai\n- Cá béo\n- Rau xanh\n\n🟡 Tập thể dục nhẹ!"),
    ("Người muốn tăng cơ nên ăn gì?", "💪 TĂNG CƠ:\n\n✅ ĂN NHIỀU:\n- Đạm (thịt, cá, trứng, đậu)\n- Carb phức hợp (gạo lứt, yến mạch)\n- Chất béo tốt (bơ, dầu olive)\n\n⏰ Ăn đều 5-6 bữa/ngày\n💪 Tập luyện sức mạnh\n\n🟡 Không quá lạm dụng!"),
]

# ==================== MULTI-TURN CONVERSATIONS ====================
multiturn_data = [
    ("Tôi bị đau đầu", "Đau đầu có nhiều nguyên nhân. Bạn có triệu chứng gì kèm theo không?\n- Sốt?\n- Buồn nôn?\n- Chóng mặt?\n- Đau mắt?"),
    ("Tôi bị ho kéo dài 2 tuần", "Ho kéo dài >2 tuần cần được kiểm tra. Bạn có triệu chứng nào khác không?\n- Đờm?\n- Sốt?\n- Khó thở?\n- Đau ngực?"),
    ("Tôi mệt mỏi và khó ngủ", "Mệt mỏi + khó ngủ có thể do nhiều nguyên nhân. Bạn có đang stress hoặc lo âu không? Có bệnh mãn tính nào không?"),
    ("Con tôi bị sốt", "Trẻ bao nhiêu tuổi? Sốt bao nhiêu độ? Có triệu chứng gì khác không (ho, nôn, phát ban...)?"),
    ("Tôi muốn giảm cân", "Để giảm cân hiệu quả, tôi cần biết:\n- Cân nặng, chiều cao hiện tại\n- Bạn có bệnh nền (tiểu đường, tim mạch...)?\n- Mức độ vận động hiện tại?"),
    ("Tôi bị đau bụng", "Đau bụng ở vị trí nào? Khi nào đau nhiều nhất? Có kèm nôn, tiêu chảy, sốt không?"),
    ("Tôi uống thuốc huyết áp", "Bạn đang uống thuốc gì? Có tác dụng phụ không? Huyết áp đo được bao nhiêu? Có thay đổi chế độ ăn uống không?"),
    ("Tôi bị cao huyết áp", "Bạn đã được chẩn đoán cao huyết áp bao lâu rồi? Đang uống thuốc gì? Có triệu chứng gì (đau đầu, chóng mặt...) không?"),
    ("Tôi muốn kiểm tra sức khỏe", "Kiểm tra sức khỏe tổng quát nên bao gồm:\n- Xét nghiệm máu (đường, mỡ, gan, thận)\n- Huyết áp\n- Điện tâm đồ\n- Chụp X-quang phổi\n- Khám mắt, tai mũi họng\n\nBạn có triệu chứng cụ thể nào cần khám không?"),
    ("Tôi bị tiểu đường type 2", "Bạn đang điều trị thế nào (uống thuốc/insulin)? Đường huyết đo được bao nhiêu? Có biến chứng nào chưa (mắt, thận, chân)?"),
]

def main():
    """Tạo data và lưu vào file"""
    all_new_data = []

    # Thêm tất cả data
    for q, a in emergency_data:
        all_new_data.append(create_sample(q, a))

    for q, a in symptom_data:
        all_new_data.append(create_sample(q, a))

    for q, a in medication_data:
        all_new_data.append(create_sample(q, a))

    for q, a in age_gender_data:
        all_new_data.append(create_sample(q, a))

    for q, a in nutrition_data:
        all_new_data.append(create_sample(q, a))

    # Multi-turn (input chính là câu hỏi đầu, output là câu hỏi lại để lấy context)
    for q, a in multiturn_data:
        all_new_data.append(create_sample(q, a))

    print(f"Tổng số samples mới: {len(all_new_data)}")
    print(f"  - Emergency: {len(emergency_data)}")
    print(f"  - Triệu chứng: {len(symptom_data)}")
    print(f"  - Thuốc: {len(medication_data)}")
    print(f"  - Độ tuổi/Giới tính: {len(age_gender_data)}")
    print(f"  - Dinh dưỡng: {len(nutrition_data)}")
    print(f"  - Multi-turn: {len(multiturn_data)}")

    # Lưu file
    output_file = "c:/NDT/PJ/MediSign_AI/data/training_clean/qwen_72b/train_new.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_new_data, f, ensure_ascii=False, indent=2)

    print(f"\nĐã lưu vào: {output_file}")

if __name__ == "__main__":
    main()
