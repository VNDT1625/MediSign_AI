# -*- coding: utf-8 -*-
"""Chapter 4 - Results."""
import sys
sys.path.insert(0, r"C:\NDT\PJ\MediSign_AI - Copy\report_build")
from report_helpers import *

FIG = Path(r"C:\NDT\PJ\MediSign_AI - Copy\report_build\figures")


def build_chapter_4(doc):
    add_heading_1(doc, "CHƯƠNG 4. KẾT QUẢ NGHIÊN CỨU")

    add_heading_2(doc, "4.1. Kết quả triển khai bốn module")
    add_para(doc,
        "Toàn bộ hệ thống MediSign AI đã được triển khai với khối lượng mã nguồn "
        "đáng kể trên ba ngôn ngữ chính. Bảng 4.1 và Hình 4.1 dưới đây cho thấy "
        "phân bố số dòng mã (LOC) theo ngôn ngữ trong codebase tại thời điểm "
        "đóng gói báo cáo.")

    add_table_caption(doc, "Bảng 4.1. Phân bố mã nguồn theo ngôn ngữ")
    add_table(doc,
              ["Ngôn ngữ", "Số file", "Số dòng (LOC)", "Vai trò chính"],
              [
                  ["Python", "201", "≈ 44.434", "Backend FastAPI, scripts huấn luyện và crawl"],
                  ["Dart", "109", "≈ 40.360", "Mobile Flutter (14 module)"],
                  ["TypeScript / TSX", "149", "≈ 28.689", "Web Next.js 14 + shared contracts"],
                  ["Tổng cộng", "≈ 459", "≈ 113.483", "Tổng codebase chính của dự án"],
              ],
              col_widths=[3.8, 2.4, 3.5, 5.5])
    add_table_source(doc, "Nguồn: Tác giả thống kê từ codebase (loại trừ node_modules, .venv, .next, .dart_tool, build/)")
    add_image(doc, FIG / "fig_4_1_loc.png", width_cm=14.5,
              caption="Hình 4.1. Phân bố số dòng mã theo ngôn ngữ",
              source="Nguồn: Tác giả tổng hợp từ codebase")

    add_heading_3(doc, "4.1.1. AI Medical Assistant + RAG + Triage 3 mức")
    add_para(doc,
        "Module Trợ lý Y khoa AI là trục lõi của hệ thống. Backend FastAPI cung "
        "cấp tổng cộng 80 endpoint REST, trong đó các nhóm route AI và tư vấn "
        "(ai.py, consult.py, conversations.py, summary.py) đảm trách "
        "quy trình hỏi đáp y khoa. Tầng dịch vụ tương ứng gồm 24 module trong "
        "thư mục apps/backend_fastapi/app/services/, trong đó các thành phần "
        "trọng yếu là rag_engine.py, rag_service.py, ai_triage_service.py, "
        "diagnostic_orchestrator.py, kb_lazy_loader.py, oars_prompt_layer.py, "
        "personal_context_service.py, quick_summary_service.py và "
        "feedback_service.py.")
    add_table_caption(doc, "Bảng 4.2. Phân bố endpoint REST theo file route")
    add_table(doc,
              ["File route", "GET", "POST", "PUT/PATCH", "DELETE", "Tổng"],
              [
                  ["admin.py", "19", "6", "4", "4", "33"],
                  ["medicine.py", "4", "4", "1", "1", "10"],
                  ["auth.py", "1", "7", "0", "0", "8"],
                  ["drug_router.py", "5", "1", "0", "0", "6"],
                  ["ai.py", "2", "3", "0", "0", "5"],
                  ["journal.py", "2", "1", "1", "1", "5"],
                  ["conversations.py", "2", "1", "0", "1", "4"],
                  ["profile.py", "1", "0", "2", "1", "4"],
                  ["consult.py", "1", "1", "0", "1", "3"],
                  ["health.py", "1", "0", "0", "0", "1"],
                  ["summary.py", "1", "0", "0", "0", "1"],
                  ["Tổng cộng", "39", "24", "8", "9", "80"],
              ],
              col_widths=[4.0, 2.0, 2.0, 2.5, 2.0, 2.5])
    add_table_source(doc, "Nguồn: Tác giả trích xuất từ thư mục apps/backend_fastapi/app/api/routes/ và app/routers/")
    add_para(doc,
        "Logic Triage được tổ chức hai tầng như đã mô tả ở Chương 3. Trong cài "
        "đặt thực tế, module ai_triage_service.py xác định cấp Đỏ ngay khi gặp "
        "các từ khóa nguy hiểm (\"khó thở\", \"đau ngực\", \"ngất\", \"chảy máu "
        "nhiều\", \"không muốn sống\") và trả về một TriageResponse chuẩn hóa "
        "kèm danh sách hành động. Khi không phát hiện cấp cứu, lời gọi được đẩy "
        "xuống MedGemma kèm context từ RAG-MediSign, đầu ra được ràng buộc theo "
        "schema năm chế độ phản hồi.")

    add_heading_3(doc, "4.1.2. Camera Quét Thuốc")
    add_para(doc,
        "Module Camera Quét Thuốc gồm hai tầng: tiền xử lý ảnh ở "
        "image_preprocessor.py (dùng OpenCV và Pillow) và nhận diện ở "
        "medicine_vision_service.py. Sau khi nhận diện, kết quả được đối chiếu "
        "với cơ sở dữ liệu DAV (60.472 thuốc và 67.493 nhãn tương tác) qua "
        "drug_lookup_service.py và drug_router.py. Lớp truy vấn nhanh được tối "
        "ưu cho các trường name, active_ingredient và reg_number.")

    add_heading_3(doc, "4.1.3. Soul Garden – đồng hành sức khỏe tinh thần")
    add_para(doc,
        "Module Soul Garden được hiện thực dưới hai bộ phận: phía mobile có cụm "
        "lib/features/soul_garden/ với các màn hình nhật ký cảm xúc, vườn cảm "
        "xúc và lời nhắc; phía backend có route journal.py (5 endpoint), bảng "
        "daily_journals trong cơ sở dữ liệu local và oars_prompt_layer.py để "
        "tạo prompt theo phong cách Motivational Interviewing (Open question – "
        "Affirm – Reflect – Summary). Việc dùng adapter Psychology giúp giọng "
        "phản hồi của AI trở nên đồng cảm và tránh đóng vai chuyên gia trị liệu.")

    add_heading_3(doc, "4.1.4. Hỗ trợ Người Khuyết Tật")
    add_para(doc,
        "Đề tài định nghĩa bốn phương thức giao tiếp tương đương trên Flutter: "
        "Voice, Sign Language, Tap/Icon và Text, đại diện trong file "
        "lib/core/models/communication_mode.dart bằng enum CommunicationMethod. "
        "Mỗi phương thức được gán nhãn icon và mô tả phù hợp với từng nhóm "
        "người dùng (người khiếm thị – Voice; người khiếm thính – Sign; người "
        "không biết chữ – Tap; người dùng phổ thông – Text). Service nhận diện "
        "ngôn ngữ ký hiệu được khai báo trừu tượng trong "
        "sign_language_service.dart kèm MockSignLanguageService để dễ thay thế "
        "bằng RealSignLanguageService trong tương lai khi có dataset VSL [cần "
        "bổ sung sau].")

    add_heading_2(doc, "4.2. Kết quả tri thức và dữ liệu huấn luyện")
    add_para(doc,
        "Knowledge Base sau quá trình crawl, làm sạch và hợp nhất đạt 128.380 "
        "bản ghi với cấu trúc trải đều trên các nhóm trọng yếu của miền y tế. "
        "Cơ cấu cụ thể được thể hiện trong Bảng 4.3 và Hình 4.2.")
    add_table_caption(doc, "Bảng 4.3. Cơ cấu Knowledge Base sau hợp nhất")
    add_table(doc,
              ["Loại tài liệu", "Số bản ghi", "Nguồn chính"],
              [
                  ["Thuốc DAV detailed", "60.472", "Cục Quản lý Dược Việt Nam"],
                  ["Tương tác thuốc", "67.493", "openFDA, DailyMed (67.473) + curated VN (20)"],
                  ["Bệnh phổ biến VN", "10", "Tổng hợp tài liệu BYT/BV"],
                  ["Cụm từ triệu chứng VN", "11", "Tự xây bằng tay"],
                  ["Khuyến nghị dinh dưỡng", "38", "BYT/NIN (18) + NIH ODS (20)"],
                  ["Đoạn hướng dẫn lâm sàng", "356", "KCB / BYT / NIN snapshot công khai"],
                  ["Tổng cộng", "128.380", "—"],
              ],
              col_widths=[5.5, 3.0, 6.5])
    add_table_source(doc, "Nguồn: Tác giả tổng hợp từ data/knowledge_base/ và plan.md")
    add_image(doc, FIG / "fig_4_2_kb.png", width_cm=12.5,
              caption="Hình 4.2. Cơ cấu Knowledge Base (128.380 bản ghi)",
              source="Nguồn: Tác giả thống kê từ data/knowledge_base/")
    add_para(doc,
        "Riêng bộ điều bệnh cho RAG được hợp nhất từ hai nguồn Vinmec và Hello "
        "Bacsi với kết quả như Bảng 4.4. Sau khi chuẩn hóa tên (bỏ dấu, đưa về "
        "chữ thường, cắt bỏ phần phụ sau dấu hai chấm), mức độ trùng lặp giữa "
        "hai nguồn chỉ là 35 bệnh, cho thấy hai trang điều bệnh phổ biến này có "
        "phạm vi nội dung khá khác nhau và việc hợp nhất tạo độ phủ vượt trội "
        "so với từng nguồn riêng lẻ.")
    add_table_caption(doc, "Bảng 4.4. Hợp nhất bộ điều bệnh từ Vinmec và Hello Bacsi")
    add_table(doc,
              ["Chỉ tiêu", "Vinmec", "Hello Bacsi", "Tổng / Hợp nhất"],
              [
                  ["Số bài viết gốc", "2.348", "1.391", "3.739"],
                  ["Số bệnh duy nhất sau chuẩn hóa", "2.302", "981", "3.248"],
                  ["Trường \"triệu chứng\" có dữ liệu", "100,00 %", "100,00 %", "100,00 %"],
                  ["Trường \"nguyên nhân\" có dữ liệu", "50,47 %", "68,29 %", "68,30 %"],
                  ["Số bệnh trùng tên giữa hai nguồn", "—", "—", "35"],
              ],
              col_widths=[5.5, 3.0, 3.0, 3.5])
    add_table_source(doc, "Nguồn: Tác giả tổng hợp từ diseases_vinmec.json và diseases_hellobacsi.json")
    add_table_caption(doc, "Bảng 4.5. Tập huấn luyện cho MedGemma 4B (dual adapter)")
    add_table(doc,
              ["Tệp", "Số mẫu", "Mục đích"],
              [
                  ["data/training_clean/medgemma_4b/medical_train.jsonl", "15.693", "Train chính cho adapter Medical"],
                  ["data/training_clean/medgemma_4b/medical_eval.jsonl", "2.770", "Eval hold-out cho adapter Medical"],
                  ["data/training_clean/medgemma_4b/psychology_train.jsonl", "1.201", "Train cho adapter Psychology (OARS, DeepSeek-regen)"],
                  ["data/training_clean/medgemma_4b/psychology_eval.jsonl", "212", "Eval hold-out cho adapter Psychology"],
                  ["data/training_clean/medgemma_4b/train.jsonl", "17.393", "Tập legacy v1 (Medical + Psychology + OARS) — giữ làm fallback"],
                  ["data/training_clean/medgemma_4b/eval.jsonl", "3.070", "Eval legacy v1"],
                  ["data/eval_sets/demo_safety_eval.jsonl", "427", "Đánh giá an toàn (clarification / self-care / emergency / disclaimer)"],
              ],
              col_widths=[7.5, 2.0, 5.5])
    add_table_source(doc, "Nguồn: Tác giả thống kê từ thư mục data/training_clean và data/eval_sets")

    add_heading_2(doc, "4.3. So sánh hiệu năng Self-hosted vs Cloud API")
    add_para(doc,
        "Đề tài giữ định hướng self-hosted xuyên suốt và không tích hợp Cloud "
        "LLM trong phiên bản hiện tại. Bảng 4.6 trình bày so sánh định tính "
        "giữa hai phương án, làm cơ sở cho quyết định kiến trúc.")
    add_table_caption(doc, "Bảng 4.6. So sánh self-hosted vs cloud trong tình huống MediSign AI")
    add_table(doc,
              ["Tiêu chí", "Cloud API", "Self-hosted (đề tài này)"],
              [
                  ["Chi phí biên/ truy vấn", "Tăng tuyến tính theo token", "Gần bằng 0 sau đầu tư GPU"],
                  ["Bảo mật dữ liệu y tế", "Phụ thuộc bên thứ ba", "Dữ liệu không rời hạ tầng"],
                  ["Độ trễ trung bình", "Phụ thuộc đường truyền", "Có thể tối ưu cục bộ"],
                  ["Khả năng tinh chỉnh adapter", "Hạn chế", "Cao – Dual LoRA"],
                  ["Tuân thủ luật bảo vệ dữ liệu", "Phải ký kết DPA", "Không cần bên thứ ba"],
                  ["Phù hợp ngân sách 3.000.000 VND", "Khó kiểm soát", "Hợp lý nếu dùng Kaggle Free / GPU sẵn"],
              ],
              col_widths=[5.5, 4.5, 5.5])
    add_table_source(doc, "Nguồn: Tác giả tổng hợp từ tài liệu kỹ thuật và pricing công khai 2024–2026")
    add_para(doc,
        "[Cần bổ sung số liệu định lượng về độ trễ và độ chính xác sau khi tổ "
        "chức benchmark thực nghiệm trên cùng một tập câu hỏi.]")

    add_heading_2(doc, "4.4. Kết quả benchmark trên tập MedQuAD")
    add_para(doc,
        "Tập MedQuAD đã được dịch sang tiếng Việt và lưu tại "
        "data/training_raw/MedQuAD/medquad_vi.json. Đề tài hoạch định ba kịch "
        "bản đánh giá: (i) MedGemma 4B base + RAG-MediSign so với MedGemma 4B "
        "base không có RAG; (ii) MedGemma 4B + adapter Medical; (iii) ablation "
        "loại bỏ KBLazyLoader để đo đóng góp của fallback. [Cần bổ sung kết "
        "quả định lượng – độ chính xác top-k, hit-rate, BERTScore – sau khi "
        "thực thi benchmark.]")

    add_heading_2(doc, "4.5. Kết quả khảo sát và phỏng vấn người dùng")
    add_para(doc,
        "Vòng khảo sát thử dự kiến phân thành ba nhóm: nhóm người cao tuổi, "
        "nhóm người khuyết tật và nhóm người chăm sóc trong gia đình. Các chủ "
        "đề cần ghi nhận gồm hành vi tự kê đơn, niềm tin vào tư vấn AI, lo ngại "
        "về quyền riêng tư, tính dễ tiếp cận của giao diện đa phương thức và "
        "phản ứng trước các cảnh báo cấp Đỏ. [Cần bổ sung dữ liệu phỏng vấn "
        "thực sau khi tổ chức.]")

    add_heading_2(doc, "4.6. Thảo luận kết quả")
    add_para(doc,
        "Các quan sát từ thiết kế và triển khai cho thấy ba điểm đáng lưu ý. "
        "Thứ nhất, quyết định không phụ thuộc Cloud LLM giúp đề tài giữ được "
        "tính nhất quán về chính sách bảo mật dữ liệu, đặc biệt phù hợp với "
        "miền y tế. Thứ hai, biến thể RAG-MediSign cho thấy khả năng kết hợp "
        "ưu điểm của BM25 (chính xác về từ vựng, đặc biệt với tên thuốc) và "
        "embeddings dày đặc (bắt ngữ nghĩa các diễn đạt dân dã của người Việt), "
        "đồng thời KBLazyLoader đóng vai trò cứu cánh khi truy vấn rơi ngoài "
        "phạm vi tri thức tĩnh. Thứ ba, cấu trúc Dual LoRA đặt cùng MedGemma "
        "duy nhất giúp đơn giản hóa hạ tầng so với việc duy trì hai mô hình "
        "riêng biệt cho y khoa và tâm lý.")
    add_para(doc,
        "Một số rủi ro cần được kiểm soát khi mở rộng. Rủi ro thứ nhất là "
        "hallucination – mặc dù RAG đã giảm đáng kể nhưng vẫn cần lớp safety "
        "đánh giá hậu kiểm. Rủi ro thứ hai là dữ liệu thuốc thay đổi nhanh hơn "
        "khả năng cập nhật của kho tri thức tĩnh; do đó các bảng meta như "
        "kb_pending_records và weight_update_proposals đóng vai trò quan trọng "
        "trong quy trình duyệt nội dung của bác sĩ trước khi đưa vào sản xuất.")

    page_break(doc)


print("part4 OK")
