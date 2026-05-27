# -*- coding: utf-8 -*-
"""Chapter 3 - Research Design."""
import sys
sys.path.insert(0, r"C:\NDT\PJ\MediSign_AI - Copy\report_build")
from report_helpers import *

FIG = Path(r"C:\NDT\PJ\MediSign_AI - Copy\report_build\figures")


def build_chapter_3(doc):
    add_heading_1(doc, "CHƯƠNG 3. THIẾT KẾ NGHIÊN CỨU")

    add_heading_2(doc, "3.1. Phương pháp nghiên cứu")
    add_para(doc,
        "Đề tài sử dụng phương pháp nghiên cứu hỗn hợp (mixed methods) gồm hai "
        "tuyến đồng thời: tuyến định lượng tập trung vào các đặc trưng kỹ thuật "
        "của hệ thống (số dòng mã, số endpoint, số bản ghi tri thức, kích thước "
        "tập huấn luyện); tuyến định tính tập trung vào trải nghiệm người dùng "
        "thông qua phỏng vấn sâu nhóm yếu thế. Cách tiếp cận này phù hợp với một "
        "đề tài nghiên cứu ứng dụng nơi cả tính khả thi kỹ thuật và tính nhân văn "
        "đều phải được kiểm chứng.")
    add_para(doc, "Quy trình nghiên cứu gồm sáu bước:")
    for step in [
        "Bước 1 – Tổng quan tài liệu về self-hosted LLM, RAG, LoRA và y tế số.",
        "Bước 2 – Thu thập dữ liệu: crawl Vinmec, Hello Bacsi và Cục Quản lý Dược.",
        "Bước 3 – Thiết kế kiến trúc hệ thống và biến thể RAG-MediSign.",
        "Bước 4 – Triển khai 4 module trên Flutter, Next.js và FastAPI.",
        "Bước 5 – Tinh chỉnh adapter QLoRA cho MedGemma 1.5 4B.",
        "Bước 6 – Đánh giá thực nghiệm và phỏng vấn người dùng [cần bổ sung số liệu].",
    ]:
        add_dash_item(doc, step)

    add_heading_2(doc, "3.2. Mẫu nghiên cứu")
    add_para(doc,
        "Đối với phỏng vấn sâu, đề tài dự kiến chọn mẫu có chủ đích (purposive "
        "sampling) gồm 5–10 người tham gia, đại diện cho các nhóm: người khiếm "
        "thính, người khiếm thị, người cao tuổi sống độc lập, người chăm sóc "
        "trong gia đình có người khuyết tật, và người trẻ sử dụng smartphone "
        "tích cực. Tiêu chí lựa chọn bao gồm độ tuổi từ 18 trở lên, có thiết bị "
        "di động, và đồng ý tham gia phỏng vấn ít nhất 45 phút. [Cần bổ sung "
        "thông tin chi tiết về danh sách tham gia thực tế sau khi tổ chức phỏng "
        "vấn.]")

    add_heading_2(doc, "3.3. Thiết kế bảng câu hỏi và kịch bản phỏng vấn")
    add_para(doc,
        "Bảng câu hỏi (Phụ lục C) được tổ chức theo bốn nhóm: (i) thông tin nhân "
        "khẩu học cơ bản; (ii) hành vi tự kê đơn và tìm kiếm dịch vụ y tế hiện "
        "tại; (iii) trải nghiệm sử dụng các ứng dụng y tế trước đây; (iv) đánh "
        "giá nguyên mẫu MediSign AI sau khi sử dụng thử. Kịch bản phỏng vấn sâu "
        "được thiết kế bán cấu trúc, cho phép người tham gia đào sâu vào những "
        "trải nghiệm đặc thù mà bảng hỏi đóng không thể bắt được, ví dụ rào cản "
        "ngôn ngữ với người khiếm thính hoặc lo lắng về bảo mật của người cao "
        "tuổi.")

    add_heading_2(doc, "3.4. Quá trình thu thập dữ liệu")
    add_para(doc,
        "Dữ liệu kỹ thuật được thu thập trực tiếp từ codebase đã hoàn thiện: số "
        "dòng mã được đếm bằng tập lệnh PowerShell duyệt đệ quy thư mục dự án; "
        "số endpoint được trích bằng biểu thức chính quy trên các file route "
        "FastAPI; số bảng cơ sở dữ liệu được lấy trực tiếp từ định nghĩa "
        "SQLAlchemy. Dữ liệu tri thức y khoa được crawl từ ba nguồn chính: Cục "
        "Quản lý Dược (DAV), Vinmec và Hello Bacsi.")
    add_para(doc, "Sau khi hợp nhất hai nguồn Vinmec và Hello Bacsi, "
        "thống kê thu được: 2.348 bài viết Vinmec, 1.391 bài viết Hello Bacsi, "
        "với 35 bệnh trùng tên (sau chuẩn hóa) và tổng cộng 3.248 bệnh duy nhất "
        "sau khi loại trùng. Số lượng tài liệu thuần ở cả hai nguồn cộng lại "
        "là 3.739, độ phủ trường \"triệu chứng\" đạt 100% trên cả hai bộ và "
        "trường \"nguyên nhân\" đạt 68,3% (Vinmec: 1.185/2.348; Hello Bacsi: "
        "950/1.391).")
    add_image(doc, FIG / "fig_4_3_disease_dedup.png", width_cm=14.0,
              caption="Hình 3.1. Hợp nhất bộ điều bệnh từ Vinmec và Hello Bacsi",
              source="Nguồn: Tác giả tổng hợp từ diseases_vinmec.json và diseases_hellobacsi.json")

    add_heading_2(doc, "3.5. Cách phân tích dữ liệu")
    add_para(doc,
        "Dữ liệu định lượng được mô tả bằng thống kê mô tả: tần số, tỷ lệ, trung "
        "bình. Dữ liệu định tính từ phỏng vấn được phân tích theo phương pháp "
        "phân tích chủ đề (thematic analysis) gồm sáu bước: làm quen, mã hóa, "
        "tổng hợp chủ đề sơ bộ, kiểm tra chủ đề, đặt tên chủ đề và viết báo cáo. "
        "Mã hóa được thực hiện thủ công trên bản ghi gỡ băng, với hai vòng mã "
        "hóa độc lập để giảm thiên kiến.")

    add_heading_2(doc, "3.6. Kiểm soát chất lượng (Validity và Reliability)")
    add_para(doc, "Đề tài áp dụng các biện pháp sau để bảo đảm độ tin cậy:")
    for it in [
        "Triangulation: kết hợp dữ liệu từ codebase, dữ liệu crawl và phỏng vấn "
        "để giảm thiên kiến từ một nguồn duy nhất.",
        "Member checking: gửi bản tóm tắt kết quả phỏng vấn lại cho người tham "
        "gia kiểm chứng trước khi đưa vào báo cáo.",
        "Audit trail: lưu toàn bộ pipeline xử lý dữ liệu trong thư mục scripts "
        "của repository nhằm cho phép tái lập kết quả.",
        "Smoke test cho QLoRA: 16 test case cấu hình trong "
        "`scripts/tests/test_train_qlora_config.py` và 22 test case cho ETL "
        "(`prepare_medgemma_data` 7 + `format_medgemma_dataset` 15) tham gia "
        "quality gate trước khi train.",
    ]:
        add_dash_item(doc, it)

    add_heading_2(doc, "3.7. Kiến trúc hệ thống MediSign AI")
    add_heading_3(doc, "3.7.1. Tổng quan kiến trúc")
    add_para(doc,
        "Hệ thống được tổ chức theo mô hình ba lớp: lớp Client (Flutter mobile "
        "và Next.js web), lớp API Gateway (FastAPI) và lớp dữ liệu/AI (PostgreSQL "
        "16 + MedGemma Runtime). Đặc điểm quan trọng là FastAPI không nạp mô "
        "hình MedGemma trực tiếp mà gọi qua một service GPU riêng theo chuẩn "
        "OpenAI-compatible /v1/chat/completions, giúp giải phóng tiến trình "
        "FastAPI khỏi áp lực bộ nhớ GPU.")
    add_image(doc, FIG / "fig_3_1_architecture.png", width_cm=15.5,
              caption="Hình 3.2. Kiến trúc tổng thể MediSign AI",
              source="Nguồn: Tác giả tổng hợp từ codebase apps/backend_fastapi và apps/mobile_flutter")

    add_heading_3(doc, "3.7.2. RAG-MediSign – biến thể RAG \"phi tiêu chuẩn\"")
    add_para(doc,
        "Đây là điểm khác biệt cốt lõi của đề tài so với một đường ống RAG sách "
        "vở. RAG-MediSign kết hợp đồng thời ba thành phần: (1) tìm kiếm thưa BM25 "
        "tích hợp ngay trong tiến trình FastAPI để giảm phụ thuộc vào vector store "
        "ngoài; (2) tìm kiếm dày đặc bằng sentence-transformers (pgvector) để bắt "
        "ngữ nghĩa sâu; (3) hợp nhất xếp hạng bằng Reciprocal Rank Fusion với "
        "tham số k = 60. Khi điểm hợp nhất rơi xuống dưới ngưỡng KB_MISS_THRESHOLD, "
        "cơ chế KBLazyLoader sẽ kích hoạt MedGemma để tự bổ sung kết quả tìm kiếm "
        "động, giúp hệ thống xử lý cả những truy vấn mà kho tri thức tĩnh không "
        "phủ.")
    add_image(doc, FIG / "fig_3_2_rag_pipeline.png", width_cm=15.5,
              caption="Hình 3.3. Đường ống RAG-MediSign: BM25 + Dense + RRF + LazyLoader",
              source="Nguồn: Tác giả phát triển dựa trên rag_engine.py và rag_service.py")
    add_para(doc, "Một số yếu tố đặc thù miền tiếng Việt được tích hợp:")
    for it in [
        "Bảng từ đồng nghĩa MEDICAL_SYNONYMS dạng tên thương mại ↔ hoạt chất, ví "
        "dụ panadol ↔ paracetamol, hapacol ↔ acetaminophen, efferalgan ↔ "
        "paracetamol, tylenol ↔ paracetamol; cùng với các nhóm cảnh báo cấp cứu "
        "(\"đau ngực\", \"khó thở\", \"không muốn sống\").",
        "Chuẩn hóa Unicode NFD và bỏ dấu cho cả truy vấn và tài liệu để tránh "
        "lệch token do biến thể chính tả tiếng Việt.",
        "Đa adapter trong xếp hạng: nhân hệ số 1,12 cho các loại tài liệu y khoa "
        "(drug, drug_interaction, nutrition_requirement, vietnam_common_disease) "
        "khi adapter Medical đang hoạt động, và 1,15 cho các cụm từ triệu chứng "
        "khi adapter Psychology hoạt động.",
        "Tăng điểm cho tài liệu có confidence cao và giảm điểm cho tài liệu có "
        "confidence thấp, qua đó nội suy độ tin cậy của nguồn vào kết quả xếp hạng.",
    ]:
        add_dash_item(doc, it)

    add_heading_3(doc, "3.7.3. Logic Triage 3 mức Xanh – Vàng – Đỏ")
    add_para(doc,
        "Triage được thiết kế hai tầng. Tầng 1 là rule-based detect các từ khóa "
        "khẩn cấp tiếng Việt (\"khó thở\", \"đau ngực\", \"ngất\", \"chảy máu nhiều\"), "
        "trả ngay phản hồi mức Đỏ và bypass hoàn toàn LLM nhằm bảo đảm độ trễ "
        "thấp và tránh tốn quota. Tầng 2 là MedGemma + RAG cho các trường hợp "
        "không rõ ràng, đầu ra được ràng buộc theo schema JSON với năm trường "
        "phản hồi: clarification, analysis, emergency, medicine_lookup, "
        "unsupported_image.")
    add_image(doc, FIG / "fig_3_3_triage.png", width_cm=15.5,
              caption="Hình 3.4. Logic Triage hai tầng và phân mức khẩn cấp",
              source="Nguồn: Tác giả phát triển dựa trên ai_triage_service.py")

    add_heading_3(doc, "3.7.4. Cấu trúc cơ sở dữ liệu")
    add_para(doc,
        "Hệ thống sử dụng PostgreSQL 16 với 19 bảng \"cloud\" (lưu trên server) "
        "và 4 bảng \"local\" (đồng bộ về thiết bị: DailyJournal, UserProfile, "
        "MyMedicine, DoseLog). Tổng cộng 23 bảng cover các "
        "miền chính: định danh và bảo mật người dùng, dược phẩm, lịch sử triage, "
        "cộng đồng, fitness, hội thoại AI, và các bảng meta phục vụ vòng đời tri "
        "thức (kb_pending_records, diagnosis_feedback, weight_update_proposals, "
        "disease_symptom_edges).")
    add_image(doc, FIG / "fig_3_4_erd.png", width_cm=15.5,
              caption="Hình 3.5. Sơ đồ ERD rút gọn (23 bảng)",
              source="Nguồn: Tác giả tổng hợp từ database/cloud_models.py và database/local_models.py")

    page_break(doc)


print("part3 OK")
