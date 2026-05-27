# -*- coding: utf-8 -*-
"""Chapter 5 + References + Appendices."""
import sys
sys.path.insert(0, r"C:\NDT\PJ\MediSign_AI - Copy\report_build")
from report_helpers import *


def build_chapter_5(doc):
    add_heading_1(doc, "CHƯƠNG 5. KẾT LUẬN VÀ ĐỀ XUẤT")

    add_heading_2(doc, "5.1. Kết luận")
    add_para(doc,
        "Đề tài \"MediSign AI\" đã đạt được các mục tiêu cốt lõi đề ra. Về mặt "
        "kỹ thuật, hệ thống đã hoàn thiện kiến trúc ba lớp gồm Flutter mobile, "
        "Next.js web và FastAPI backend, kết nối tới một MedGemma Runtime riêng "
        "qua giao thức OpenAI-compatible. Bốn module Trợ lý Y khoa AI, Camera "
        "Quét Thuốc, Soul Garden và Hỗ trợ Người Khuyết Tật đã có khung mã "
        "nguồn đầy đủ, một số phần đã chạy được end-to-end, một số phần khác "
        "đang ở giai đoạn skeleton chờ tích hợp mô hình thực (đặc biệt là VSL "
        "và OCR thuốc).")
    add_para(doc,
        "Về mặt nghiên cứu, đề tài đề xuất biến thể RAG-MediSign kết hợp BM25, "
        "Dense embeddings, RRF và KBLazyLoader, cùng với kiến trúc Dual LoRA "
        "Adapter đặt trên cùng một mô hình MedGemma 1.5 4B. Đây là điểm khác "
        "biệt rõ rệt so với mô tả \"RAG sách vở\" trong nhiều giáo trình hiện "
        "hành và là lời giải phù hợp với đặc thù tiếng Việt cùng miền y tế của "
        "Việt Nam.")
    add_para(doc,
        "Về mặt nhân văn, hệ thống được định hướng phục vụ ba khoảng trống cùng "
        "một lúc: thói quen tự kê đơn, mất cân bằng trong hành vi tìm kiếm dịch "
        "vụ y tế và sự gia tăng các vấn đề sức khỏe tâm thần. Việc đồng thời "
        "hỗ trợ bốn phương thức giao tiếp (Voice, Sign, Tap, Text) cho thấy "
        "cam kết của đề tài đối với người yếu thế.")

    add_heading_2(doc, "5.2. Đóng góp mới của nghiên cứu")
    for it in [
        "Đóng góp 1 – Đề xuất kiến trúc RAG-MediSign \"phi tiêu chuẩn\" có "
        "tính ứng dụng trên miền y tế tiếng Việt, kết hợp BM25 nội tiến trình, "
        "Dense embeddings qua sentence-transformers/pgvector, RRF với k = 60 "
        "và KBLazyLoader fallback dựa trên MedGemma.",
        "Đóng góp 2 – Đề xuất kiến trúc Dual LoRA Adapter (Medical + "
        "Psychology) đặt cùng một mô hình nền MedGemma 1.5 4B "
        "(Medical adapter đang deploy: r=64; Psychology: r=8), "
        "cho phép tách bạch hai phong cách tư vấn mà không phải duy trì hai "
        "mô hình riêng.",
        "Đóng góp 3 – Tổng hợp kho tri thức 128.380 bản ghi và bộ điều bệnh "
        "3.248 bệnh duy nhất sau hợp nhất Vinmec và Hello Bacsi, có thể tái "
        "sử dụng cho các nghiên cứu y tế số khác.",
        "Đóng góp 4 – Mẫu thiết kế Triage hai tầng (rule-based bypass + "
        "LLM/RAG) tối ưu cho an toàn lâm sàng và độ trễ trong các tình huống "
        "khẩn cấp.",
        "Đóng góp 5 – Mẫu thiết kế giao diện đa phương thức (Voice/Sign/Tap/"
        "Text) ngay tại lớp domain model trong Flutter, sẵn sàng cho việc "
        "kiểm thử với người khuyết tật trong giai đoạn tiếp theo.",
    ]:
        add_dash_item(doc, it)

    add_heading_2(doc, "5.3. Hạn chế của nghiên cứu")
    for it in [
        "Hạn chế 1 – Module nhận diện ngôn ngữ ký hiệu mới ở giai đoạn "
        "skeleton; cần dataset VSL và mô hình TFLite thật để hoàn thiện.",
        "Hạn chế 2 – Module Camera Quét Thuốc đã có pipeline tiền xử lý và "
        "lookup nhưng chưa có classifier ảnh thuốc đã huấn luyện chính thức.",
        "Hạn chế 3 – Benchmark MedQuAD và đánh giá người dùng thực vẫn "
        "đang chờ tổ chức; các kết quả định lượng cụ thể còn để mở [cần bổ "
        "sung sau].",
        "Hạn chế 4 – Cỡ mẫu phỏng vấn dự kiến 5–10 người là đủ cho phương "
        "pháp định tính nhưng chưa đủ để tổng quát hóa thống kê; nghiên cứu "
        "tiếp theo cần mở rộng cỡ mẫu.",
        "Hạn chế 5 – Một phần dữ liệu tham khảo của miền dược (DrugBank "
        "Clinical) không truy cập được vì lý do bản quyền và thay đổi chính "
        "sách phân phối trong giai đoạn nghiên cứu.",
    ]:
        add_dash_item(doc, it)

    add_heading_2(doc, "5.4. Đề xuất hướng phát triển tiếp theo")
    for it in [
        "Hoàn thiện adapter Vision của MedGemma cho ảnh đơn thuốc và bao bì "
        "thuốc; tích hợp với hệ thống cảnh báo tương tác.",
        "Tổ chức một dataset VSL gồm khoảng 200–500 cử chỉ y khoa cơ bản và "
        "huấn luyện mô hình landmark + classifier nhẹ.",
        "Mở rộng đánh giá lâm sàng theo chuẩn an toàn (red-teaming, evaluation "
        "rubric) và mời bác sĩ tham gia hội đồng kiểm duyệt nội dung.",
        "Triển khai pgvector đầy đủ cho retrieval dày đặc và bổ sung BERTScore "
        "tự động cho từng phản hồi.",
        "Mở rộng module Soul Garden với hỗ trợ liên kết cơ sở y tế tâm thần "
        "công lập và quy trình chuyển tuyến cho các trường hợp nguy cơ tự hại.",
        "Hợp tác với Bộ Y tế và Hội Người Khuyết Tật để chuẩn hóa nội dung "
        "tư vấn và đảm bảo tính pháp lý của khuyến nghị.",
    ]:
        add_dash_item(doc, it)

    page_break(doc)


def build_references(doc):
    add_heading_1(doc, "TÀI LIỆU THAM KHẢO")
    add_para(doc,
        "Danh mục được sắp xếp theo thứ tự bảng chữ cái của tác giả, không đánh "
        "số, theo chuẩn APA phiên bản 6.", italic=True, indent_first=False,
        align=WD_ALIGN_PARAGRAPH.LEFT)

    refs = [
        "Ben Abacha, A., & Demner-Fushman, D. (2019). A question-entailment "
        "approach to question answering. BMC Bioinformatics, 20(1), 511. "
        "https://doi.org/10.1186/s12859-019-3119-4",

        "Bộ Y tế Việt Nam. (2023). Báo cáo tổng kết công tác y tế năm 2022 "
        "và phương hướng nhiệm vụ năm 2023. Hà Nội: Bộ Y tế.",

        "Cormack, G. V., Clarke, C. L. A., & Buettcher, S. (2009). Reciprocal "
        "rank fusion outperforms condorcet and individual rank learning methods. "
        "In Proceedings of the 32nd International ACM SIGIR Conference on "
        "Research and Development in Information Retrieval (pp. 758–759). ACM. "
        "https://doi.org/10.1145/1571941.1572114",

        "Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). "
        "QLoRA: Efficient finetuning of quantized LLMs. In Advances in Neural "
        "Information Processing Systems (Vol. 36). https://arxiv.org/abs/2305.14314",

        "Google Research. (2024). MedGemma technical report. Google. "
        "https://huggingface.co/google/medgemma-1.5-4b-it",

        "Hu, E., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, "
        "L., & Chen, W. (2021). LoRA: Low-rank adaptation of large language "
        "models. arXiv preprint arXiv:2106.09685.",

        "Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, "
        "N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & "
        "Kiela, D. (2020). Retrieval-augmented generation for knowledge-"
        "intensive NLP tasks. In Advances in Neural Information Processing "
        "Systems (Vol. 33).",

        "Miller, W. R., & Rollnick, S. (2013). Motivational interviewing: "
        "Helping people change (3rd ed.). Guilford Press.",

        "Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance "
        "framework: BM25 and beyond. Foundations and Trends in Information "
        "Retrieval, 3(4), 333–389. https://doi.org/10.1561/1500000019",

        "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence "
        "embeddings using siamese BERT-networks. In Proceedings of EMNLP "
        "(pp. 3982–3992).",

        "Tổng cục Thống kê. (2024). Niên giám thống kê Việt Nam 2024. Hà Nội: "
        "Nhà xuất bản Thống kê.",

        "Touvron, H., Martin, L., Stone, K., Albert, P., Almahairi, A., "
        "Babaei, Y., et al. (2023). Llama 2: Open foundation and fine-tuned "
        "chat models. arXiv preprint arXiv:2307.09288.",

        "Trung tâm Kiểm soát Bệnh tật TP. Hồ Chí Minh. (2023). Báo cáo tình "
        "hình kháng kháng sinh tại TP. HCM giai đoạn 2018–2022. TP. HCM: HCDC.",

        "Văn phòng Thống kê Liên Hợp Quốc về Khuyết tật. (2024). World report "
        "on disability 2024. United Nations.",

        "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., "
        "Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention is all "
        "you need. In Advances in Neural Information Processing Systems "
        "(Vol. 30).",

        "Vinmec International Hospital. (2024). Cổng thông tin sức khỏe "
        "Vinmec. https://vinmec.com/vie/cam-nang/",

        "World Health Organization. (2022). World mental health report: "
        "Transforming mental health for all. Geneva: WHO.",

        "Yunxiang, L., Zihan, L., Kai, Z., Ruilong, D., & You, Z. (2023). "
        "ChatDoctor: A medical chat model fine-tuned on a large language "
        "model Meta-AI (LLaMA) using medical domain knowledge. arXiv "
        "preprint arXiv:2303.14070.",

        "[Cần bổ sung] Báo cáo của Bộ Y tế Việt Nam về tình hình sức khỏe "
        "tâm thần (2024–2025).",

        "[Cần bổ sung] Tổ chức Người Khuyết Tật Việt Nam. (2025). Báo cáo "
        "thường niên về tiếp cận dịch vụ y tế.",
    ]
    for r in refs:
        p = doc.add_paragraph()
        run = p.add_run(r)
        set_run_font(run, size=12)
        pf = p.paragraph_format
        pf.line_spacing = 1.5
        pf.space_before = Pt(0)
        pf.space_after = Pt(6)
        pf.first_line_indent = Cm(-1.0)
        pf.left_indent = Cm(1.0)

    page_break(doc)


def build_appendices(doc):
    add_heading_1(doc, "PHỤ LỤC A. MÃ NGUỒN CÁC MODULE QUAN TRỌNG")
    add_para(doc, "Phụ lục này trích lược các đoạn mã đại diện cho ba khối cốt lõi: "
                  "RAG-MediSign, Triage hai tầng và mô hình dữ liệu cơ sở.", indent_first=False)
    add_heading_2(doc, "A.1. Trích đoạn rag_engine.py – hợp nhất BM25 và Dense bằng RRF")
    code = (
        "fused = self._rrf_merge(bm25_hits, dense_hits, k=60)\n"
        "candidates = self._to_disease_candidates(fused)\n\n"
        "if self.lazy_loader is not None and db is not None:\n"
        "    max_score = max((c.probability for c in candidates), default=0.0)\n"
        "    if not candidates or max_score < KB_MISS_THRESHOLD:\n"
        "        lazy_candidates = await self.lazy_loader.search_and_enrich(query, db)\n"
        "        if lazy_candidates:\n"
        "            candidates = lazy_candidates"
    )
    p = doc.add_paragraph()
    run = p.add_run(code)
    set_run_font(run, size=10)
    run.font.name = "Consolas"
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("ascii", "hAnsi", "cs"):
        rFonts.set(qn(f"w:{attr}"), "Consolas")
    set_paragraph_format(p, indent_first=False, align=WD_ALIGN_PARAGRAPH.LEFT,
                         line=1.15)

    add_heading_2(doc, "A.2. Trích đoạn ai_triage_service.py – rule-based bypass")
    code2 = (
        "EMERGENCY_KEYWORDS = (\n"
        "    \"khó thở\", \"đau ngực\", \"ngất\", \"co giật\", \"chảy máu nhiều\",\n"
        "    \"không muốn sống\", \"hôn mê\", \"tê liệt nửa người\",\n"
        ")\n\n"
        "def _classify_urgency_rule_based(text: str) -> str:\n"
        "    if any(k in text.lower() for k in EMERGENCY_KEYWORDS):\n"
        "        return \"emergency\"\n"
        "    if any(k in text.lower() for k in URGENT_KEYWORDS):\n"
        "        return \"urgent\"\n"
        "    return \"non_emergency\""
    )
    p = doc.add_paragraph()
    run = p.add_run(code2)
    set_run_font(run, size=10)
    run.font.name = "Consolas"
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("ascii", "hAnsi", "cs"):
        rFonts.set(qn(f"w:{attr}"), "Consolas")
    set_paragraph_format(p, indent_first=False, align=WD_ALIGN_PARAGRAPH.LEFT,
                         line=1.15)
    add_para(doc, "[Phần đầy đủ xem tại apps/backend_fastapi/app/services/ai_triage_service.py.]",
             italic=True, indent_first=False)
    page_break(doc)

    add_heading_1(doc, "PHỤ LỤC B. SƠ ĐỒ ERD CHI TIẾT")
    add_para(doc, "Tham khảo Hình 3.5 trong Chương 3 và file "
                  "apps/backend_fastapi/app/database/cloud_models.py + local_models.py "
                  "để xem định nghĩa đầy đủ.", indent_first=False)
    add_heading_2(doc, "B.1. Nhóm bảng cốt lõi (Cloud) — 19 bảng")
    add_table(doc, ["Bảng", "Vai trò"],
              [
                  ["users", "Tài khoản người dùng (UUID, email, hash mật khẩu PBKDF2)"],
                  ["user_sessions", "Phiên đăng nhập + refresh token đã hash"],
                  ["password_resets", "Token đặt lại mật khẩu"],
                  ["email_verifications", "Token xác minh email"],
                  ["medicine_registry", "60.472 thuốc DAV: hoạt chất, hàm lượng, cảnh báo"],
                  ["hospitals", "Danh sách bệnh viện và phòng khám"],
                  ["family_connections", "Liên kết hỗ trợ trong gia đình"],
                  ["triage_history", "Lịch sử triage để học từ phản hồi bác sĩ"],
                  ["community_posts", "Bài viết cộng đồng ẩn danh, có kiểm duyệt"],
                  ["post_comments", "Bình luận trong cộng đồng"],
                  ["post_likes", "Lượt thích bài cộng đồng"],
                  ["workout_sessions", "Phiên tập thể dục"],
                  ["fitness_goals", "Mục tiêu thể dục cá nhân"],
                  ["chat_conversations", "Hội thoại multi-turn diagnostic"],
                  ["chat_messages", "Tin nhắn chi tiết kèm metadata DiagnosticState"],
                  ["kb_pending_records", "Hàng đợi nội dung KB chờ bác sĩ duyệt"],
                  ["diagnosis_feedback", "Feedback bác sĩ sửa kết quả AI"],
                  ["weight_update_proposals", "Đề xuất cập nhật trọng số xếp hạng"],
                  ["disease_symptom_edges", "Đồ thị bệnh – triệu chứng cho discriminative question"],
              ],
              col_widths=[5.5, 9.5])
    add_heading_2(doc, "B.2. Nhóm bảng local — 4 bảng")
    add_table(doc, ["Bảng", "Vai trò"],
              [
                  ["daily_journals", "Nhật ký cảm xúc trong Soul Garden"],
                  ["user_profiles", "Hồ sơ y tế cá nhân, lưu trên thiết bị"],
                  ["my_medicines", "Tủ thuốc cá nhân hóa người dùng"],
                  ["dose_logs", "Lịch sử uống thuốc (append-only) phục vụ adherence"],
              ],
              col_widths=[5.5, 9.5])
    page_break(doc)

    add_heading_1(doc, "PHỤ LỤC C. BẢNG CÂU HỎI KHẢO SÁT")
    add_para(doc, "Bảng câu hỏi gồm bốn nhóm chính. Người tham gia trả lời theo "
                  "thang Likert 5 mức từ 1 (Hoàn toàn không đồng ý) đến 5 (Hoàn "
                  "toàn đồng ý), trừ các câu thông tin nhân khẩu.", indent_first=False)
    add_heading_2(doc, "C.1. Thông tin nhân khẩu học")
    for q in [
        "C1.1 Giới tính, độ tuổi, tình trạng khuyết tật (nếu có).",
        "C1.2 Trình độ học vấn cao nhất.",
        "C1.3 Khu vực sinh sống (đô thị / nông thôn / vùng sâu).",
        "C1.4 Mức thu nhập hàng tháng (lựa chọn theo nhóm).",
    ]:
        add_dash_item(doc, q)
    add_heading_2(doc, "C.2. Hành vi tự kê đơn và tìm kiếm dịch vụ y tế")
    for q in [
        "C2.1 Khi có dấu hiệu sốt nhẹ, bạn thường tự mua thuốc hay đi khám?",
        "C2.2 Bạn đã từng dùng kháng sinh khi không có đơn bác sĩ chưa?",
        "C2.3 Khi bệnh nặng, bao lâu thì bạn quyết định đi viện?",
        "C2.4 Lý do chính khiến bạn trì hoãn đi khám là gì?",
    ]:
        add_dash_item(doc, q)
    add_heading_2(doc, "C.3. Trải nghiệm các ứng dụng y tế trước đây")
    for q in [
        "C3.1 Bạn đã sử dụng ứng dụng tư vấn y tế nào?",
        "C3.2 Khó khăn lớn nhất khi dùng các ứng dụng đó là gì?",
        "C3.3 Bạn có lo ngại về quyền riêng tư khi gửi triệu chứng cho ứng dụng AI không?",
    ]:
        add_dash_item(doc, q)
    add_heading_2(doc, "C.4. Đánh giá nguyên mẫu MediSign AI")
    for q in [
        "C4.1 Mức độ dễ hiểu của giao diện đa phương thức.",
        "C4.2 Mức độ phù hợp của lời tư vấn cho hoàn cảnh thực tế.",
        "C4.3 Mức độ tin tưởng đối với cảnh báo cấp Đỏ.",
        "C4.4 Mức độ thoải mái khi chia sẻ cảm xúc trong Soul Garden.",
        "C4.5 Đề xuất cải thiện cụ thể.",
    ]:
        add_dash_item(doc, q)
    page_break(doc)

    add_heading_1(doc, "PHỤ LỤC D. KẾT QUẢ PHỎNG VẤN SÂU")
    add_para(doc, "[Cần bổ sung] Phụ lục này sẽ ghi nhận biên bản gỡ băng và bảng "
                  "mã chủ đề sau khi tổ chức phỏng vấn 5–10 người tham gia. Mã hóa "
                  "được thực hiện hai vòng độc lập theo phương pháp phân tích chủ đề.",
             indent_first=False)
    page_break(doc)

    add_heading_1(doc, "PHỤ LỤC E. HƯỚNG DẪN CÀI ĐẶT VÀ SỬ DỤNG")
    add_heading_2(doc, "E.1. Yêu cầu môi trường")
    for it in [
        "Python 3.11 trở lên",
        "Node.js 20 trở lên",
        "Flutter SDK ≥ 3.4",
        "PostgreSQL 16",
        "GPU 24 GB (khuyến nghị) hoặc 2× T4 trên Kaggle",
    ]:
        add_dash_item(doc, it)
    add_heading_2(doc, "E.2. Các bước triển khai")
    steps = [
        "Bước 1 – Sao chép repository và cấu hình biến môi trường: cp .env.example .env",
        "Bước 2 – Khởi tạo backend FastAPI: cd apps/backend_fastapi && python -m venv .venv && .venv\\Scripts\\activate && pip install -e .[dev]",
        "Bước 3 – Khởi động cơ sở dữ liệu PostgreSQL qua docker-compose up -d postgres",
        "Bước 4 – Chạy migration Alembic: alembic upgrade head",
        "Bước 5 – Khởi động backend: uvicorn app.main:app --reload --port 8000",
        "Bước 6 – Khởi chạy MedGemma Runtime trên GPU server qua endpoint OpenAI-compatible",
        "Bước 7 – Khởi động web: cd apps/web_next && npm install && npm run dev",
        "Bước 8 – Khởi động mobile: cd apps/mobile_flutter && flutter run",
    ]
    for s in steps:
        add_dash_item(doc, s)
    add_heading_2(doc, "E.3. Các lệnh huấn luyện adapter QLoRA")
    for it in [
        "scripts/prepare_medgemma_data.py – chuẩn bị tập dữ liệu hợp nhất",
        "scripts/format_medgemma_dataset.py – chuyển sang định dạng phù hợp với MedGemma",
        "scripts/train_qlora_medgemma.py – chạy huấn luyện chính trên GPU",
        "scripts/train_qlora_medgemma_smoke_test.py – kiểm tra cấu hình trước khi chạy thật",
        "scripts/medisign_train_kaggle.py – kịch bản huấn luyện trên Kaggle Free",
    ]:
        add_dash_item(doc, it)


print("part5 OK")
