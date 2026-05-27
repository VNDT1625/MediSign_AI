# -*- coding: utf-8 -*-
"""Extension 2: more depth in chapter 2 and chapter 4."""
import sys
sys.path.insert(0, r"C:\NDT\PJ\MediSign_AI - Copy\report_build")
from report_helpers import *


def extend_chapter_2_more(doc):
    add_heading_2(doc, "2.12. So sánh các kiến trúc RAG hiện hành")
    add_para(doc,
        "Để định vị rõ vai trò của biến thể RAG-MediSign, đề tài tổng hợp một "
        "khung so sánh năm kiến trúc RAG đại diện trên các trục: nguồn xếp "
        "hạng, độ trễ, khả năng mở rộng và phù hợp với miền y tế Việt Nam.")
    add_table_caption(doc, "Bảng 2.2. So sánh năm kiến trúc RAG đại diện")
    add_table(doc, ["Kiến trúc", "Nguồn xếp hạng", "Hợp nhất", "Phù hợp y tế VN"],
              [
                  ["Naive RAG", "BM25 hoặc Dense", "—", "Hạn chế với tên thương mại VN"],
                  ["Hybrid RAG", "BM25 + Dense", "Trọng số hằng", "Trung bình, cần tinh chỉnh"],
                  ["RAG Fusion", "Dense × N truy vấn", "RRF", "Tốt cho ngữ nghĩa, yếu từ vựng"],
                  ["Self-RAG", "Dense + self-reflect", "Quyết định bởi LLM", "Cao về chi phí inference"],
                  ["RAG-MediSign", "BM25 + Dense + LazyLoader", "RRF + ngưỡng", "Tối ưu cho miền VN"],
              ],
              col_widths=[3.5, 4.5, 3.5, 4.0])
    add_table_source(doc, "Nguồn: Tác giả tổng hợp từ Lewis et al. (2020), Asai et al. (2023), tài liệu nội bộ dự án")
    add_para(doc,
        "Quan sát từ Bảng 2.2 cho thấy điểm khác biệt cốt lõi của RAG-MediSign "
        "không nằm ở việc sáng tạo một thuật toán mới mà ở việc tổ chức thông "
        "minh các thành phần đã có để phù hợp với miền y tế tiếng Việt: BM25 "
        "đóng vai trò xương sống cho từ khóa thuốc và tên bệnh, Dense bổ "
        "sung khả năng hiểu ngữ nghĩa câu nói dân dã, RRF làm trung gian, và "
        "KBLazyLoader cứu cánh cho các truy vấn nằm ngoài kho tri thức tĩnh.")


def extend_chapter_4_cases(doc):
    add_heading_2(doc, "4.11. Bốn tình huống tham chiếu (case studies)")
    add_para(doc,
        "Để minh họa cách hệ thống vận hành trong các tình huống thường gặp, "
        "đề tài chuẩn bị bốn tình huống tham chiếu lần lượt thuộc bốn nhóm: "
        "tự kê đơn an toàn, tự kê đơn rủi ro, dấu hiệu tâm lý không khẩn "
        "cấp, và dấu hiệu khẩn cấp thực sự.")

    add_heading_3(doc, "4.11.1. Tình huống 1 – Tự kê đơn an toàn")
    add_para(doc,
        "Một người dùng nữ, 32 tuổi, mô tả: \"Em bị sốt nhẹ 37,8 độ kèm đau "
        "đầu, không có triệu chứng gì khác.\" Hệ thống nhận diện cụm từ "
        "\"sốt nhẹ\" và \"đau đầu\", nâng các tài liệu liên quan đến sốt "
        "do virus thường gặp lên đầu danh sách. Triage trả về mức Xanh, "
        "khuyến nghị nghỉ ngơi, uống đủ nước và dùng paracetamol theo "
        "khuyến cáo, đồng thời đặt mốc 24–48 giờ để theo dõi. Adapter "
        "Medical thêm cảnh báo về tương tác paracetamol và rượu, đặc biệt "
        "đối với người dùng đang uống thuốc khác.")

    add_heading_3(doc, "4.11.2. Tình huống 2 – Tự kê đơn rủi ro")
    add_para(doc,
        "Một người dùng nam, 45 tuổi, mô tả: \"Tôi định mua kháng sinh "
        "amoxicillin để uống thử cho khỏi đau họng, có sao không?\" Hệ "
        "thống phát hiện ý định tự dùng kháng sinh và kích hoạt nhánh "
        "medicine_lookup, kết nối kết quả từ cơ sở dữ liệu DAV và bảng "
        "tương tác thuốc. Phản hồi của hệ thống không cản trở thẳng nhưng "
        "trình bày rõ rủi ro kháng kháng sinh, các trường hợp cần dùng "
        "kháng sinh, dấu hiệu cần đi khám và khuyến nghị không tự dùng "
        "amoxicillin nếu không có chỉ định của bác sĩ.")

    add_heading_3(doc, "4.11.3. Tình huống 3 – Dấu hiệu tâm lý không khẩn cấp")
    add_para(doc,
        "Một sinh viên, 22 tuổi, viết trong Soul Garden: \"Mấy hôm nay em "
        "thấy mất ngủ, ăn không ngon, không muốn gặp ai.\" Hệ thống chuyển "
        "lời gọi sang adapter Psychology với prompt theo OARS. Phản hồi "
        "khởi đầu bằng câu hỏi mở (\"Em có thể chia sẻ thêm tình trạng này "
        "đã kéo dài bao lâu không?\"), khẳng định cảm xúc của người dùng "
        "(\"Cảm giác mất ngủ và mệt mỏi như em mô tả là điều rất nhiều "
        "người trải qua\"), phản chiếu (\"Có vẻ em đang muốn ở một mình "
        "nhiều hơn so với trước đây\") và tóm tắt. Khi không có dấu hiệu "
        "tự hại, hệ thống chỉ gợi ý các kỹ thuật vệ sinh giấc ngủ và đề "
        "xuất tham vấn chuyên gia khi triệu chứng kéo dài quá hai tuần.")

    add_heading_3(doc, "4.11.4. Tình huống 4 – Khẩn cấp thực sự")
    add_para(doc,
        "Một người dùng nam, 55 tuổi, mô tả: \"Tôi đột nhiên đau ngực "
        "trái, lan ra cánh tay và khó thở.\" Tầng rule-based phát hiện cụm "
        "\"đau ngực\" và \"khó thở\" – những từ khóa nằm trong danh sách "
        "EMERGENCY_KEYWORDS – và bypass hoàn toàn LLM, trả về phản hồi mức "
        "Đỏ với hướng dẫn gọi 115, không tự ý dùng thuốc, thông báo cho "
        "người thân. Toàn bộ thời gian phản hồi chỉ là chi phí thực thi "
        "rule-based, đảm bảo độ trễ thấp nhất có thể trong tình huống "
        "nguy cấp. Sau khi gửi cảnh báo, hệ thống mới chạy MedGemma để "
        "sinh gợi ý hành động chi tiết hơn, chạy bất đồng bộ để không làm "
        "trễ thông điệp khẩn cấp ban đầu.")

    add_para(doc,
        "Bốn tình huống trên cho thấy thiết kế hai tầng của Triage và sự "
        "phối hợp giữa hai adapter Medical, Psychology là phù hợp với "
        "thực tế đa dạng của người dùng Việt Nam. Việc đặt một tầng rule-"
        "based phía trước MedGemma là quyết định an toàn quan trọng: ngay "
        "cả khi mô hình bị lỗi tải hoặc sai lệch, các trường hợp nguy "
        "hiểm vẫn được chặn lại bởi luật cứng.")

    add_heading_2(doc, "4.12. Phân tích an toàn ở mức kiến trúc")
    add_para(doc,
        "An toàn của một hệ thống tư vấn y tế AI cần được kiểm tra ở ít "
        "nhất ba lớp: lớp dữ liệu (đầu vào), lớp suy luận (xử lý), lớp "
        "đầu ra. Ở lớp dữ liệu, MediSign AI phân tách rõ giữa dữ liệu "
        "công khai và dữ liệu cá nhân, áp dụng PBKDF2 cho mật khẩu và "
        "JWT-rotation cho phiên. Ở lớp suy luận, Triage hai tầng và "
        "MEDICAL_SYNONYMS giúp giảm rủi ro hiểu sai do biến thể chính "
        "tả. Ở lớp đầu ra, schema năm chế độ phản hồi yêu cầu mỗi câu "
        "trả lời phải có trường safety với danh sách red_flags và "
        "disclaimer; điều này được thực thi ngay trong post-process của "
        "MedGemma client thay vì để mô hình tự quyết định.")

    add_para(doc,
        "Một bài toán an toàn quan trọng khác là an toàn nội dung tâm lý. "
        "Hệ thống áp dụng một danh sách từ khóa nguy cơ tự hại; khi phát "
        "hiện, adapter Psychology không trả lời theo OARS thông thường "
        "mà chuyển sang nhánh khẩn cấp với hướng dẫn liên hệ đường dây "
        "nóng (115, 1900-…) và mô tả các bước an toàn ngay tức thì. Cách "
        "tiếp cận này nhất quán với khuyến nghị của WHO (2022) về vai "
        "trò chuyển tuyến của các kênh hỗ trợ ban đầu.")


print("ext2 OK")
