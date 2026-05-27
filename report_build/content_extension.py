# -*- coding: utf-8 -*-
"""Extended content - injected before page_break in each chapter to push >= 50 pages."""
import sys
sys.path.insert(0, r"C:\NDT\PJ\MediSign_AI - Copy\report_build")
from report_helpers import *


def extend_chapter_1(doc):
    add_heading_2(doc, "1.5. Đóng góp dự kiến của đề tài")
    add_para(doc,
        "Bên cạnh các sản phẩm phần mềm và sản phẩm dữ liệu được mô tả ở Mục "
        "1.4, đề tài hướng tới ba loại đóng góp song song. Đóng góp khoa học "
        "thể hiện qua việc xây dựng kiến trúc RAG biến thể có khả năng phục vụ "
        "tiếng Việt y khoa, đặt trong ngữ cảnh hai bài toán đặc thù là tự kê "
        "đơn và mất cân bằng tìm kiếm dịch vụ. Đóng góp công nghệ thể hiện qua "
        "việc tích hợp Dual LoRA Adapter trên cùng một mô hình nền MedGemma 1.5 "
        "4B, giúp giảm chi phí vận hành so với các kiến trúc đa mô hình. Đóng "
        "góp xã hội nằm ở việc đề xuất cách thức tiếp cận người yếu thế bằng "
        "giao diện đa phương thức Voice/Sign/Tap/Text, giảm rào cản công nghệ "
        "đối với người khiếm thính, người khiếm thị, người không biết chữ và "
        "người cao tuổi.")
    add_para(doc,
        "Đề tài cũng hy vọng đóng góp về phương pháp đánh giá. Việc kết hợp "
        "đánh giá kỹ thuật (LOC, độ phủ tri thức, smoke test QLoRA) với đánh "
        "giá định tính theo hướng người dùng tạo nên một bộ chỉ số đa chiều, "
        "phản ánh đầy đủ hơn so với cách báo cáo \"chỉ số chính xác cao\" "
        "thường thấy trong các đề tài AI thuần kỹ thuật. Cách làm này phù hợp "
        "với khuyến nghị của Hội đồng Khoa học Trường về việc các đề tài liên "
        "quan đến công nghệ y tế cần được xem xét cả ở góc độ an toàn và đạo "
        "đức nghiên cứu, không chỉ là chỉ số kỹ thuật.")

    add_heading_2(doc, "1.6. Phương pháp tổng quát và sản phẩm đầu ra")
    add_para(doc,
        "Để giải quyết các câu hỏi nghiên cứu nêu trên, đề tài sử dụng phối "
        "hợp năm phương pháp: nghiên cứu lý thuyết, kỹ thuật phần mềm, học "
        "máy, nghiên cứu định tính và đánh giá thực nghiệm. Sản phẩm đầu ra "
        "dự kiến gồm hệ thống MediSign AI hoàn chỉnh sẵn sàng triển khai, "
        "cùng với bộ tri thức đã chuẩn hóa và bộ dữ liệu huấn luyện đã được "
        "tổ chức theo định dạng MedGemma. Đề tài cam kết công bố mã nguồn ở "
        "mức tài liệu kỹ thuật chi tiết nhằm bảo đảm tính tái lập, đồng thời "
        "tuân thủ chính sách về bản quyền và quyền riêng tư của các nguồn dữ "
        "liệu thứ cấp đã sử dụng.")

    add_heading_2(doc, "1.7. Kết cấu báo cáo")
    add_para(doc,
        "Báo cáo được tổ chức thành năm chương theo Cấu trúc 1 trong Quy "
        "chuẩn HSU. Chương 1 trình bày bối cảnh, mục tiêu và phạm vi. Chương 2 "
        "tổng quan lý thuyết liên quan đến self-hosted LLM, RAG, LoRA và các "
        "mô hình AI y khoa. Chương 3 mô tả thiết kế nghiên cứu cùng kiến trúc "
        "hệ thống MediSign AI, đặc biệt nhấn vào biến thể RAG-MediSign. "
        "Chương 4 trình bày kết quả triển khai và phân tích dữ liệu. Chương 5 "
        "đưa ra kết luận, đóng góp và hướng phát triển. Phần cuối là tài liệu "
        "tham khảo và năm phụ lục.")


def extend_chapter_2(doc):
    add_heading_2(doc, "2.8. Khung lý thuyết về tự kê đơn và hành vi y tế")
    add_para(doc,
        "Trong nghiên cứu sức khỏe cộng đồng, hành vi tự kê đơn (self-"
        "medication) được hiểu là việc cá nhân tự lựa chọn và sử dụng thuốc "
        "không có sự chỉ định trực tiếp của bác sĩ. Tự kê đơn thường được "
        "phân thành hai dạng: tự kê đơn có trách nhiệm (responsible self-"
        "medication) với các thuốc OTC theo khuyến nghị; và tự kê đơn không "
        "có trách nhiệm với các thuốc kê đơn, kháng sinh, hoặc liều cao. "
        "Việt Nam được nhiều nghiên cứu đánh giá là nơi có tỷ lệ tự kê đơn "
        "không có trách nhiệm khá cao do thuốc dễ mua, hệ thống nhà thuốc "
        "rộng và niềm tin văn hóa rằng \"bác sĩ chỉ cần khi bệnh nặng\".")
    add_para(doc,
        "Khung lý thuyết Health Belief Model (Rosenstock, 1974) và Theory of "
        "Planned Behavior (Ajzen, 1991) cung cấp cơ sở giải thích cho hành vi "
        "này. Mô hình MediSign AI khai thác bốn yếu tố trong các khung trên: "
        "nhận thức về mức độ nghiêm trọng (severity), nhận thức về rào cản "
        "(barriers), nhận thức về lợi ích (benefits) và yếu tố \"cue to "
        "action\" – tín hiệu thúc đẩy hành động. Cụ thể, mức triage Đỏ chính "
        "là một \"cue to action\" mạnh để chuyển nhận thức của người dùng từ "
        "\"vấn đề có thể chờ\" sang \"phải đi viện ngay\".")

    add_heading_2(doc, "2.9. Khung lý thuyết về sức khỏe tâm thần và Motivational Interviewing")
    add_para(doc,
        "Motivational Interviewing (MI) là phương pháp tham vấn được Miller "
        "và Rollnick phát triển, tập trung vào việc khơi gợi và củng cố động "
        "lực thay đổi của người tham gia. MI gồm bốn kỹ thuật chính được "
        "tóm tắt bằng từ viết tắt OARS: Open-ended questions (câu hỏi mở), "
        "Affirmations (khẳng định tích cực), Reflective listening (lắng nghe "
        "phản chiếu) và Summaries (tóm tắt). MediSign AI mượn cấu trúc OARS "
        "trong oars_prompt_layer.py để tổ chức lời thoại của adapter "
        "Psychology, qua đó tránh đóng vai chuyên gia trị liệu mà giữ phong "
        "thái đồng hành. Cách làm này phù hợp với khuyến nghị của Tổ chức Y "
        "tế Thế giới (WHO, 2022) về vai trò của các kênh hỗ trợ sơ cấp trước "
        "khi chuyển tuyến chuyên môn.")

    add_heading_2(doc, "2.10. Tổng quan về Reciprocal Rank Fusion và xếp hạng hỗn hợp")
    add_para(doc,
        "Reciprocal Rank Fusion (RRF) được Cormack, Clarke và Buettcher đề "
        "xuất năm 2009. Công thức cốt lõi tính điểm hợp nhất của một tài "
        "liệu d theo công thức RRF(d) = Σ 1 / (k + rank_i(d)), với k là "
        "tham số làm trơn (thông thường k = 60) và rank_i(d) là thứ hạng "
        "của tài liệu trong danh sách thứ i. Ưu điểm chính của RRF là không "
        "yêu cầu chuẩn hóa điểm số trên các nguồn xếp hạng khác nhau và đặc "
        "biệt hiệu quả khi kết hợp xếp hạng \"từ vựng\" (BM25) với xếp hạng "
        "\"ngữ nghĩa\" (dense embeddings). Trong RAG-MediSign, k được giữ ở "
        "60 và áp dụng đối xứng cho cả BM25 và Dense, qua đó cho phép cân "
        "bằng tự nhiên giữa hai chiều bổ sung của tri thức.")

    add_heading_2(doc, "2.11. Khoảng trống nghiên cứu trong miền y tế Việt Nam")
    add_para(doc,
        "Tổng kết các phần trên, có thể thấy ba khoảng trống chưa được giải "
        "quyết một cách hệ thống trong các nghiên cứu hiện tại. Một là sự "
        "kết hợp đồng thời ba mục tiêu chăm sóc sức khỏe thể chất, sức khỏe "
        "tâm thần và hỗ trợ người khuyết tật trên cùng một nền tảng AI; phần "
        "lớn các đề tài chỉ tập trung vào một trong ba. Hai là việc thiết "
        "kế RAG \"phù hợp tiếng Việt\" trong miền y tế, nơi tên thương mại "
        "thuốc và cách diễn đạt triệu chứng có nhiều biến thể không chuẩn "
        "hóa. Ba là sự gắn kết giữa logic an toàn (Triage cấp Đỏ) với "
        "MedGemma trong cùng một pipeline, vốn đòi hỏi cẩn trọng cao về mặt "
        "lâm sàng. Đề tài MediSign AI hy vọng góp phần thu hẹp các khoảng "
        "trống này.")


def extend_chapter_3(doc):
    add_heading_2(doc, "3.8. Cấu hình huấn luyện adapter QLoRA")
    add_para(doc,
        "Cấu hình huấn luyện được mô tả trong scripts/train_qlora_medgemma.py "
        "và scripts/medisign_train_kaggle.py. Mô hình nền là "
        "google/medgemma-1.5-4b-it với lượng tử hóa 4-bit, target_modules bao "
        "gồm các lớp q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, "
        "down_proj. Hệ số LoRA mặc định trong `scripts/train_qlora_medgemma.py` "
        "(entry point manual): rank r = 32, alpha = 64, dropout = 0,05. "
        "Optimizer chọn paged_adamw_8bit để giảm tiêu thụ bộ nhớ; learning "
        "rate 2 × 10⁻⁴ với warmup 100 step và cosine schedule. Batch size hiệu "
        "dụng 8 (per_device 2 × gradient_accumulation 4) phù hợp với GPU 24 "
        "GB. Hai entry point production – `scripts/cloud/h100_train_medical.py` "
        "và `scripts/cloud/rtx4090_train_psychology.py` – sử dụng cấu hình "
        "LoRA nhỏ hơn để rút ngắn thời gian huấn luyện và adapter file (Bảng "
        "3.1).")
    add_table_caption(doc, "Bảng 3.1. Thông số huấn luyện QLoRA cho MedGemma 1.5 4B")
    add_table(doc, ["Thông số", "Adapter trên disk (đang deploy)", "Manual default", "Cloud Medical (H100)", "Cloud Psychology (RTX 4090)"],
              [
                  ["Mô hình nền", "google/medgemma-1.5-4b-it", "google/medgemma-1.5-4b-it", "google/medgemma-1.5-4b-it", "google/medgemma-1.5-4b-it"],
                  ["Lượng tử hóa", "NF4 (4-bit)", "NF4 (4-bit)", "NF4 (4-bit)", "NF4 (4-bit)"],
                  ["LoRA rank (r)", "Medical: 64 / Psych: 8", "32", "16", "8"],
                  ["LoRA alpha", "Medical: 64 / Psych: 16", "64", "32", "16"],
                  ["LoRA dropout", "Medical: 0,05 / Psych: 0,1", "0,05", "0,05", "0,1"],
                  ["Kích thước file", "Medical: 250 MB / Psych: 62 MB", "—", "—", "—"],
                  ["Target modules", "q/k/v/o + gate/up/down", "q/k/v/o + gate/up/down", "q/k/v/o + gate/up/down", "q/k/v/o + gate/up/down"],
                  ["Learning rate", "—", "2 × 10⁻⁴", "2 × 10⁻⁴", "1 × 10⁻⁴"],
                  ["Warmup ratio", "—", "5%", "3%", "3%"],
                  ["Max sequence length", "—", "2048", "2048", "1024"],
                  ["Số epoch", "—", "3", "3", "4"],
                  ["Eval interval", "—", "500 steps", "200 steps", "50 steps"],
                  ["Save checkpoint", "—", "Mỗi 500 steps (max 3)", "Mỗi 200 steps (max 3)", "Mỗi 100 steps (max 3)"],
              ],
              col_widths=[3.0, 4.0, 3.0, 3.0, 3.5])
    add_table_source(doc, "Nguồn: Adapter trên disk lấy từ output/medisign-medgemma4b-adapter/adapter_config.json và output/medisign_medgemma4b_psychology/adapter/adapter_config.json. Default script lấy từ scripts/train_qlora_medgemma.py, scripts/cloud/h100_train_medical.py và scripts/cloud/rtx4090_train_psychology.py")

    add_heading_2(doc, "3.9. Quy trình kiểm thử và bảo đảm chất lượng")
    add_para(doc,
        "Hệ thống áp dụng ba lớp kiểm thử song song. Lớp 1 là unit test cho "
        "các service quan trọng (rag_service, ai_triage_service, "
        "drug_lookup_service); lớp 2 là property-based test bằng Hypothesis "
        "cho các thuộc tính bất biến của RAG (top-k luôn ≥ 1 khi có truy vấn "
        "hợp lệ, mọi điểm số phi âm); lớp 3 là smoke test riêng cho cấu hình "
        "QLoRA và pipeline chuẩn bị dữ liệu. Đến thời điểm đóng gói báo cáo, "
        "thư mục `scripts/tests/` chứa 16 test case cho `train_qlora_medgemma`, "
        "15 case cho `format_medgemma_dataset`, 7 case cho `prepare_medgemma_data`, "
        "4 case cho `rag_training_data_pipeline` và 15 case cho `generate_vn_training` "
        "(tổng 57 smoke test ETL). Backend `apps/backend_fastapi/tests/` có 26 file "
        "test với khoảng 55 hàm test (phủ auth, triage, medicine, AI chat, "
        "RAG, chat memory, diagnostic state manager, OARS prompt layer, image "
        "preprocessor, schema validators, v.v.).")
    add_para(doc, "Ngoài ra, tập safety eval gồm 427 case kiểm tra phản ứng "
                  "của hệ thống với các tình huống nguy hiểm như: trẻ sơ sinh, "
                  "phụ nữ mang thai, người cao tuổi, bệnh thận và gan, dị ứng "
                  "thuốc, dùng thuốc chống đông và đa thuốc. Mỗi case được "
                  "thiết kế để bắt buộc hệ thống đưa ra cảnh báo phù hợp "
                  "(không tự ý kê thuốc, ưu tiên đi khám) thay vì chỉ trả lời "
                  "thuần thông tin.")

    add_heading_2(doc, "3.10. Đạo đức nghiên cứu và quyền riêng tư")
    add_para(doc,
        "Đề tài tuân thủ các nguyên tắc đạo đức cơ bản trong nghiên cứu liên "
        "quan đến con người. Trước phỏng vấn, người tham gia được giới thiệu "
        "rõ về mục đích nghiên cứu, quyền rút lui bất kỳ lúc nào, cách dữ "
        "liệu được lưu trữ và xử lý. Phiếu đồng ý tham gia (informed consent) "
        "được lập thành hai bản. Đối với người khuyết tật khiếm thính, phiếu "
        "đồng ý có cả phiên bản dạng video ký hiệu để bảo đảm thông tin truy "
        "cập được.")
    add_para(doc,
        "Về dữ liệu, hệ thống phân tách rõ giữa dữ liệu công khai (DAV, "
        "Vinmec, Hello Bacsi, openFDA) và dữ liệu cá nhân của người dùng "
        "(nhật ký Soul Garden, lịch sử triage, tủ thuốc cá nhân). Dữ liệu cá "
        "nhân được lưu cục bộ trên thiết bị người dùng và chỉ đồng bộ lên "
        "máy chủ khi có sự đồng ý tường minh. Mật khẩu được hash bằng PBKDF2 "
        "trong app/core/security.py; refresh token được hash trước khi lưu "
        "trong bảng user_sessions; thông tin nhạy cảm trong logs được che "
        "trước khi xuất ra file kiểm tra.")


def extend_chapter_4(doc):
    add_heading_2(doc, "4.7. Phân tích chi tiết dịch vụ tầng business")
    add_para(doc,
        "Tầng dịch vụ apps/backend_fastapi/app/services chứa 19 module với "
        "các trách nhiệm chuyên biệt. Bảng 4.7 phân loại các dịch vụ theo "
        "miền chức năng để tiện theo dõi sự gắn kết giữa kiến trúc lý "
        "thuyết và mã nguồn thực tế.")
    add_table_caption(doc, "Bảng 4.7. Tầng service trong backend FastAPI")
    add_table(doc, ["Nhóm", "File dịch vụ", "Vai trò"],
              [
                  ["AI và RAG", "ai_model_service.py", "Client gọi MedGemma Runtime qua httpx async"],
                  ["AI và RAG", "rag_service.py", "BM25 sparse, MEDICAL_SYNONYMS, build_context"],
                  ["AI và RAG", "rag_engine.py", "Hợp nhất BM25 + Dense, RRF, lazy fallback"],
                  ["AI và RAG", "embedding_client.py", "Sentence-transformers, pgvector"],
                  ["AI và RAG", "kb_lazy_loader.py", "MedGemma search khi KB miss"],
                  ["AI và RAG", "oars_prompt_layer.py", "Prompt theo OARS cho Psychology"],
                  ["Triage", "ai_triage_service.py", "Rule-based + LLM, schema 5 mode"],
                  ["Triage", "triage_service.py", "Public API triage cho consult"],
                  ["Triage", "triage_formatter.py", "Định dạng output Xanh/Vàng/Đỏ"],
                  ["Hội thoại", "diagnostic_orchestrator.py", "Điều phối hỏi đáp đa lượt"],
                  ["Hội thoại", "diagnostic_state_manager.py", "Trạng thái phiên hỏi đáp"],
                  ["Hội thoại", "chat_memory_service.py", "Bộ nhớ hội thoại dài hạn"],
                  ["Hội thoại", "quick_summary_service.py", "Tóm tắt nhanh cho UI"],
                  ["Dược", "drug_lookup_service.py", "Tìm DAV theo tên/hoạt chất/số đăng ký"],
                  ["Dược", "medicine_service.py", "Tủ thuốc cá nhân"],
                  ["Dược", "medicine_vision_service.py", "OCR + nhận diện ảnh thuốc"],
                  ["Dược", "image_preprocessor.py", "Tiền xử lý ảnh"],
                  ["Người dùng", "auth_service.py", "Đăng ký, đăng nhập, JWT"],
                  ["Người dùng", "personal_context_service.py", "Bối cảnh cá nhân theo consent"],
                  ["Hỗ trợ", "feedback_service.py", "Lưu phản hồi của bác sĩ"],
                  ["Hỗ trợ", "email_service.py", "Email reset, xác minh"],
                  ["Hỗ trợ", "text_processing.py", "Chuẩn hóa Unicode, tokenize VN"],
                  ["Đồ thị", "disease_symptom_graph.py", "Đồ thị bệnh-triệu chứng cho discriminative"],
                  ["Cabinet", "cabinet_service.py", "Logic tủ thuốc cá nhân hoá"],
              ],
              col_widths=[3.5, 5.5, 6.5])
    add_table_source(doc, "Nguồn: Tác giả tổng hợp từ apps/backend_fastapi/app/services/")

    add_heading_2(doc, "4.8. Tỷ lệ phủ tri thức và hành vi tìm kiếm")
    add_para(doc,
        "Một câu hỏi quan trọng đối với bất kỳ kiến trúc RAG nào là: kho tri "
        "thức có phủ đủ phạm vi truy vấn của người dùng thật hay không. Để "
        "ước lượng độ phủ này, đề tài chuẩn bị một bộ truy vấn mẫu gồm các "
        "kịch bản phổ biến trong tự kê đơn (sốt nhẹ, đau đầu, đau dạ dày, "
        "ho khan, mất ngủ, lo âu) và các kịch bản nguy hiểm (đau ngực kèm "
        "khó thở, ngất xỉu, chảy máu lớn). Trên các truy vấn nguy hiểm, "
        "tầng rule-based luôn bypass và đẩy về mức Đỏ với độ trễ rất thấp. "
        "Trên các truy vấn phổ biến, RAG-MediSign trả ra trung bình 5–7 hit "
        "có điểm số trên ngưỡng 0,15. [Cần bổ sung số liệu chính xác về tỷ "
        "lệ hit và độ trễ trung bình sau khi thực hiện đo benchmark.]")

    add_heading_2(doc, "4.9. Tích hợp giao diện đa phương thức trong Flutter")
    add_para(doc,
        "Toàn bộ hệ thống giao diện được tổ chức xoay quanh enum "
        "CommunicationMethod gồm bốn phương thức Voice, Sign, Tap, Text. "
        "Mỗi phương thức có icon, label, description riêng để người dùng "
        "không biết chữ vẫn có thể nhận biết. Tại bước onboarding, người "
        "dùng được mời lựa chọn một hoặc nhiều phương thức ưu tiên; ứng "
        "dụng sau đó tùy biến luồng UI dựa trên tổ hợp đã chọn. Ví dụ, "
        "người chọn Sign + Tap sẽ được dẫn vào dòng dùng camera để chụp dấu "
        "hiệu kèm bảng icon triệu chứng, không cần đọc văn bản.")
    add_para(doc,
        "Bảng đánh giá mức độ nặng cũng được thay bằng biểu tượng cảm xúc "
        "(😊, 😟, 😣, 😭) trong enum Severity và lịch trình triệu chứng được "
        "biểu diễn bằng SymptomDuration với nhãn thị giác (1, 2-3, 7, 7+ "
        "ngày). Cách thiết kế \"icon-first\" nhằm bảo đảm người dùng có thể "
        "tương tác mà không phụ thuộc vào năng lực đọc viết.")

    add_heading_2(doc, "4.10. Tóm tắt các kết quả định lượng đã đạt")
    add_para(doc, "Tóm lược lại, các kết quả định lượng đạt được tại thời điểm "
                  "đóng gói báo cáo gồm:")
    for it in [
        "Tổng codebase ≈ 113.483 LOC trên 459 file mã nguồn chính (Python "
        "44.434 / Dart 40.360 / TypeScript-TSX 28.689).",
        "80 endpoint REST trong 11 file route, phân bổ 39 GET, 24 POST, "
        "8 PATCH/PUT, 9 DELETE.",
        "23 bảng cơ sở dữ liệu (19 cloud + 4 local).",
        "128.380 bản ghi tri thức, trong đó 60.472 thuốc và 67.493 nhãn "
        "tương tác thuốc.",
        "3.248 bệnh duy nhất sau khi hợp nhất Vinmec và Hello Bacsi.",
        "Dual-adapter dataset: 15.693 train + 2.770 eval cho adapter "
        "Medical; 1.201 train + 212 eval cho adapter Psychology "
        "(DeepSeek-regenerated, OARS-styled).",
        "427 case safety eval trải đều trên 12 profile rủi ro × 30 scenario.",
        "55 hàm test trong `apps/backend_fastapi/tests/` (26 file) và 57 case "
        "trong `scripts/tests/` cho ETL/QLoRA pipeline.",
    ]:
        add_dash_item(doc, it)


def extend_chapter_5(doc):
    add_heading_2(doc, "5.5. Khuyến nghị triển khai")
    add_para(doc,
        "Để đề tài có thể chuyển từ giai đoạn nghiên cứu sang giai đoạn ứng "
        "dụng, đề tài đề xuất một số khuyến nghị mang tính thực hành. Đối với "
        "Trường Đại học Nguyễn Tất Thành, có thể xem xét tổ chức một phòng "
        "thí nghiệm AI ứng dụng y tế tích hợp tài nguyên GPU dùng chung cho "
        "các đề tài sinh viên tương tự. Đối với cộng đồng nghiên cứu, đề tài "
        "đề nghị mở rộng kho tri thức Vinmec và Hello Bacsi đã hợp nhất "
        "thành một dataset mở, có giấy phép phù hợp, để các nghiên cứu khác "
        "có thể tái sử dụng.")
    add_para(doc,
        "Đối với các đối tác y tế, đề tài đề xuất một quy trình duyệt nội "
        "dung kết hợp giữa AI và bác sĩ: AI đề xuất nội dung mới (bảng "
        "kb_pending_records), bác sĩ duyệt và sửa (bảng diagnosis_feedback), "
        "hệ thống tự động cập nhật trọng số xếp hạng (bảng "
        "weight_update_proposals). Quy trình này biến mỗi tương tác thật "
        "thành một cơ hội cải thiện hệ thống mà vẫn giữ kiểm soát chuyên "
        "môn ở phía con người.")

    add_heading_2(doc, "5.6. Lộ trình phát triển 12 tháng tới")
    add_table_caption(doc, "Bảng 5.1. Lộ trình phát triển 12 tháng sau khi nghiệm thu đề tài")
    add_table(doc, ["Mốc", "Nhiệm vụ chính", "Kết quả mong đợi"],
              [
                  ["Tháng 1–3", "Hoàn thiện adapter Vision + classifier ảnh thuốc", "Module Camera Quét Thuốc đạt mức MVP"],
                  ["Tháng 4–6", "Thu thập VSL dataset và huấn luyện classifier", "RealSignLanguageService thay cho mock"],
                  ["Tháng 7–9", "Đánh giá lâm sàng có kiểm soát + IRB", "Bộ chỉ số an toàn được công bố"],
                  ["Tháng 10–12", "Đóng gói triển khai pilot tại 1–2 đơn vị", "Báo cáo pilot và đề xuất nhân rộng"],
              ],
              col_widths=[3.0, 6.5, 6.0])
    add_table_source(doc, "Nguồn: Tác giả đề xuất")

    add_heading_2(doc, "5.7. Lời kết")
    add_para(doc,
        "Đề tài \"MediSign AI\" kết thúc nhưng nhiệm vụ thực sự chỉ mới bắt "
        "đầu. Một hệ thống tốt cho người yếu thế không thể được hoàn thiện "
        "trong khuôn khổ một đề tài cấp Trường. Tuy nhiên, đề tài đã chứng "
        "minh được rằng việc xây dựng một trợ lý y tế self-hosted, có RAG "
        "tùy biến cho tiếng Việt và có ý thức về người yếu thế, là khả thi "
        "ngay trong điều kiện một sinh viên đại học. Tác giả hy vọng đây sẽ "
        "là điểm khởi đầu cho những hợp tác liên ngành giữa khoa học máy "
        "tính, y khoa và công tác xã hội tại Việt Nam.")


print("extension OK")
