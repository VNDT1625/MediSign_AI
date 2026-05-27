# -*- coding: utf-8 -*-
"""Content - Cover, preliminaries (Vietnamese with diacritics)."""
import sys
sys.path.insert(0, r"C:\NDT\PJ\MediSign_AI - Copy\report_build")
from report_helpers import *


def build_cover(doc):
    section = doc.sections[0]
    configure_section(section, page_num_format="lowerRoman")
    for _ in range(2):
        add_para(doc, "", indent_first=False)
    add_para(doc, "BỘ GIÁO DỤC VÀ ĐÀO TẠO", bold=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "TRƯỜNG ĐẠI HỌC NGUYỄN TẤT THÀNH", bold=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.CENTER, size=14)
    add_para(doc, "KHOA CÔNG NGHỆ THÔNG TIN", bold=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.CENTER, size=12)
    for _ in range(3):
        add_para(doc, "", indent_first=False)
    add_para(doc, "BÁO CÁO TỔNG KẾT", bold=True, size=16, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "ĐỀ TÀI NGHIÊN CỨU KHOA HỌC CẤP TRƯỜNG", bold=True, size=14,
             indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "DÀNH CHO SINH VIÊN NĂM 2026", italic=True, size=12,
             indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(2):
        add_para(doc, "", indent_first=False)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("MediSign AI")
    set_run_font(run, size=22, bold=True, color=RGBColor(0x0D, 0x47, 0xA1))
    set_paragraph_format(p, indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc,
             "Xây dựng hệ thống ứng dụng đa nền tảng hỗ trợ gợi ý chăm sóc sức khỏe, "
             "đồng hành sức khỏe tinh thần và hỗ trợ người khuyết tật dựa trên trí tuệ nhân tạo",
             bold=True, size=14, indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(3):
        add_para(doc, "", indent_first=False)
    info = [
        ("Chủ nhiệm đề tài", "Nguyễn Duy Thuận"),
        ("Mã số sinh viên", "2311555799"),
        ("Lớp", "23DKTPM1A"),
        ("Khoa", "Công nghệ Thông tin"),
        ("Giảng viên hướng dẫn", "ThS. Đỗ Gia Bảo"),
        ("Năm thực hiện", "2026"),
        ("Kinh phí dự kiến", "3.000.000 VNĐ"),
    ]
    table = doc.add_table(rows=len(info), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (k, v) in enumerate(info):
        c1, c2 = table.rows[i].cells
        c1.text = ""
        p = c1.paragraphs[0]
        run = p.add_run(k)
        set_run_font(run, bold=True, size=12)
        c2.text = ""
        p = c2.paragraphs[0]
        run = p.add_run(v)
        set_run_font(run, size=12)
    for col in table.columns:
        for cell in col.cells:
            cell.width = Cm(7.0)
    for _ in range(3):
        add_para(doc, "", indent_first=False)
    add_para(doc, "TP. HỒ CHÍ MINH, THÁNG 12 NĂM 2026", bold=True, size=12,
             indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    page_break(doc)


def build_inner_cover(doc):
    add_para(doc, "BỘ GIÁO DỤC VÀ ĐÀO TẠO", bold=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "TRƯỜNG ĐẠI HỌC NGUYỄN TẤT THÀNH", bold=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.CENTER, size=14)
    add_para(doc, "KHOA CÔNG NGHỆ THÔNG TIN", bold=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.CENTER, size=12)
    for _ in range(3):
        add_para(doc, "", indent_first=False)
    add_para(doc, "BÁO CÁO TỔNG KẾT ĐỀ TÀI NGHIÊN CỨU KHOA HỌC CẤP TRƯỜNG",
             bold=True, size=14, indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(2):
        add_para(doc, "", indent_first=False)
    add_para(doc,
             "MEDISIGN AI – XÂY DỰNG HỆ THỐNG ỨNG DỤNG ĐA NỀN TẢNG HỖ TRỢ GỢI Ý "
             "CHĂM SÓC SỨC KHỎE, ĐỒNG HÀNH SỨC KHỎE TINH THẦN VÀ HỖ TRỢ NGƯỜI "
             "KHUYẾT TẬT DỰA TRÊN TRÍ TUỆ NHÂN TẠO",
             bold=True, size=14, indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(2):
        add_para(doc, "", indent_first=False)
    add_para(doc, "Lĩnh vực nghiên cứu: Công nghệ Thông tin / Trí tuệ nhân tạo ứng dụng trong Y tế",
             italic=True, indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_para(doc, "Loại hình nghiên cứu: Nghiên cứu ứng dụng",
             italic=True, indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(3):
        add_para(doc, "", indent_first=False)
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c1, c2 = table.rows[0].cells
    for cell, lines in [
        (c1, ["GIẢNG VIÊN HƯỚNG DẪN", "(Ký và ghi rõ họ tên)",
              "", "", "", "", "ThS. Đỗ Gia Bảo"]),
        (c2, ["CHỦ NHIỆM ĐỀ TÀI", "(Ký và ghi rõ họ tên)",
              "", "", "", "", "Nguyễn Duy Thuận"]),
    ]:
        cell.text = ""
        for i, line in enumerate(lines):
            p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line)
            set_run_font(run, bold=(i in (0, 6)), italic=(i == 1), size=12)
    for _ in range(3):
        add_para(doc, "", indent_first=False)
    add_para(doc, "TP. HỒ CHÍ MINH, THÁNG 12 NĂM 2026", bold=True, size=12,
             indent_first=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    page_break(doc)


def build_acknowledgement(doc):
    add_heading_1(doc, "LỜI CẢM ƠN")
    paras = [
        "Đề tài \"MediSign AI\" được hoàn thành không chỉ bằng nỗ lực cá nhân mà còn nhờ "
        "sự đồng hành tận tâm của nhiều tập thể và cá nhân. Trong khuôn khổ trang viết "
        "ngắn ngủi, tác giả xin gửi lời cảm ơn chân thành và sâu sắc nhất đến tất cả "
        "những người đã góp phần làm nên kết quả này.",

        "Trước tiên, tác giả xin trân trọng cảm ơn Ban Giám hiệu Trường Đại học Nguyễn "
        "Tất Thành, Phòng Khoa học Công nghệ và Khoa Công nghệ Thông tin đã tạo mọi điều "
        "kiện thuận lợi về mặt hành chính, tài chính và cơ sở vật chất để đề tài được "
        "triển khai trong khuôn khổ chương trình \"Đề tài Nghiên cứu Khoa học cấp Trường "
        "dành cho Sinh viên năm 2026\".",

        "Tác giả xin bày tỏ lòng biết ơn sâu sắc đến ThS. Đỗ Gia Bảo – giảng viên hướng "
        "dẫn – người đã kiên trì định hướng, góp ý phản biện và luôn kiên nhẫn lắng "
        "nghe những ý tưởng còn non nớt của sinh viên. Từ những lần thầy thẳng thắn bàn "
        "về cách \"giảm hallucination cho LLM trong y khoa\" cho đến những buổi tư vấn "
        "phương pháp định tính, sự tận tâm và nghiêm khắc của thầy là động lực lớn nhất "
        "để đề tài không đi chệch khỏi mục tiêu học thuật.",

        "Tác giả xin gửi lời cảm ơn đến quý thầy cô trong Khoa Công nghệ Thông tin đã "
        "truyền dạy kiến thức nền tảng về cấu trúc dữ liệu, học máy, kỹ thuật phần mềm "
        "và cơ sở dữ liệu – những viên gạch giúp tác giả tự tin xây dựng một hệ thống "
        "đa tầng phức tạp như MediSign AI. Các thầy cô của bộ môn Công nghệ Phần mềm đã "
        "góp nhiều ý kiến quý báu về mô hình kiến trúc và luồng xử lý dữ liệu.",

        "Lời cảm ơn đặc biệt xin được dành cho các bạn sinh viên lớp 23DKTPM1A và các "
        "bạn tình nguyện viên từ cộng đồng người khiếm thính, người cao tuổi và gia đình "
        "của họ – những người đã kiên nhẫn tham gia các buổi phỏng vấn sâu và kiểm thử "
        "ứng dụng. Chính những phản hồi chân thật, đôi lúc thẳng thắn đến \"đau lòng\", "
        "đã giúp MediSign AI không rơi vào bẫy \"công nghệ phòng thí nghiệm\" mà hướng "
        "tới nhu cầu thực sự của người yếu thế.",

        "Cuối cùng, xin được gửi lời cảm ơn chậm và sâu nhất đến gia đình – nguồn động "
        "viên lớn nhất trong suốt quá trình nghiên cứu. Ba và mẹ không phải dân kỹ thuật, "
        "nhưng sự tin tưởng và câu hỏi giản dị \"Hôm nay có khá hơn không con?\" đã là "
        "nguồn năng lượng tinh thần vững chắc để tác giả không bỏ cuộc khi gặp khó khăn "
        "về kỹ thuật hay những giai đoạn bế tắc ý tưởng.",

        "Dù đã cố gắng hết mình, đề tài không tránh khỏi những hạn chế do hạn hẹp về "
        "thời gian, nguồn lực và kinh nghiệm nghiên cứu của sinh viên. Tác giả rất mong "
        "nhận được những góp ý chân thành từ Hội đồng khoa học, quý thầy cô phản biện "
        "và độc giả để công trình được hoàn thiện hơn trong các giai đoạn phát triển "
        "tiếp theo.",
    ]
    for txt in paras:
        add_para(doc, txt)
    add_para(doc, "", indent_first=False)
    add_para(doc, "Trân trọng cảm ơn.", italic=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.RIGHT)
    add_para(doc, "TP. Hồ Chí Minh, tháng 12 năm 2026", italic=True,
             indent_first=False, align=WD_ALIGN_PARAGRAPH.RIGHT)
    add_para(doc, "Chủ nhiệm đề tài", italic=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.RIGHT)
    for _ in range(4):
        add_para(doc, "", indent_first=False, align=WD_ALIGN_PARAGRAPH.RIGHT)
    add_para(doc, "Nguyễn Duy Thuận", bold=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.RIGHT)
    page_break(doc)


def build_advisor_review(doc):
    add_heading_1(doc, "NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN")
    fields = [
        ("Họ và tên sinh viên:", "Nguyễn Duy Thuận"),
        ("Mã số sinh viên:", "2311555799"),
        ("Lớp:", "23DKTPM1A"),
        ("Khoa:", "Công nghệ Thông tin"),
        ("Tên đề tài:",
         "MediSign AI – Xây dựng hệ thống ứng dụng đa nền tảng hỗ trợ gợi ý chăm sóc "
         "sức khỏe, đồng hành sức khỏe tinh thần và hỗ trợ người khuyết tật dựa trên "
         "trí tuệ nhân tạo"),
        ("Giảng viên hướng dẫn:", "ThS. Đỗ Gia Bảo"),
    ]
    for k, v in fields:
        p = doc.add_paragraph()
        run = p.add_run(k + " ")
        set_run_font(run, bold=True, size=12)
        run = p.add_run(v)
        set_run_font(run, size=12)
        set_paragraph_format(p, indent_first=False)
    sections = [
        "1. Về tinh thần, thái độ và sự tuân thủ của sinh viên:",
        "2. Về khối lượng và độ khó của đề tài:",
        "3. Về phương pháp nghiên cứu và ý nghĩa khoa học / thực tiễn:",
        "4. Về kết quả đạt được và khả năng ứng dụng trong thực tế:",
        "5. Hạn chế, góp ý và đề xuất cho hướng phát triển tiếp theo:",
        "6. Kết luận và đề nghị (cho phép / không cho phép bảo vệ; điểm dự kiến):",
    ]
    line = "..............................................................................................................................................."
    for s in sections:
        add_para(doc, s, bold=True, indent_first=False)
        for _ in range(4):
            p = doc.add_paragraph(line)
            set_paragraph_format(p, indent_first=False)
    add_para(doc, "", indent_first=False)
    add_para(doc, "TP. Hồ Chí Minh, ngày ...... tháng ...... năm 2026",
             italic=True, indent_first=False, align=WD_ALIGN_PARAGRAPH.RIGHT)
    add_para(doc, "GIẢNG VIÊN HƯỚNG DẪN", bold=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.RIGHT)
    add_para(doc, "(Ký và ghi rõ họ tên)", italic=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.RIGHT)
    for _ in range(4):
        add_para(doc, "", indent_first=False, align=WD_ALIGN_PARAGRAPH.RIGHT)
    add_para(doc, "ThS. Đỗ Gia Bảo", bold=True, indent_first=False,
             align=WD_ALIGN_PARAGRAPH.RIGHT)
    page_break(doc)


def build_abstract(doc):
    add_heading_1(doc, "TRÍCH YẾU")
    add_para(doc,
             "Đề tài \"MediSign AI\" giải quyết hai khoảng trống điển hình trong y tế Việt "
             "Nam: thói quen tự kê đơn tại nhà của người dân và sự mất cân bằng trong hành "
             "vi tìm kiếm dịch vụ y tế – một bộ phận đi khám quá sớm khi mới có dấu hiệu "
             "nhẹ, một bộ phận khác lại chỉ đến bệnh viện khi bệnh đã chuyển nặng. Bên "
             "cạnh đó, các rối loạn tâm lý như lo âu và trầm cảm đang ngày càng phổ biến "
             "nhưng người dân ít có kênh hỗ trợ ban đầu. Câu hỏi nghiên cứu trọng tâm là: "
             "làm thế nào xây dựng một trợ lý y tế dựa trên mô hình ngôn ngữ lớn (LLM) "
             "tự triển khai, vừa gọn nhẹ về chi phí, vừa giảm thiểu rủi ro \"hallucination\" "
             "và đặc biệt thân thiện với người khuyết tật cùng người cao tuổi tại Việt Nam. "
             "Phương pháp nghiên cứu phối hợp định tính và định lượng: tổng quan tài liệu, "
             "phỏng vấn sâu nhóm yếu thế, đồng thời thiết kế và kiểm thử một hệ thống đa "
             "nền tảng gồm Flutter mobile, Next.js web và FastAPI backend. Mô hình AI lõi "
             "là MedGemma 1.5 4B được tinh chỉnh bằng kỹ thuật QLoRA với hai adapter "
             "chuyên biệt (Medical và Psychology), kết hợp kho tri thức 128.380 bản ghi "
             "và 60.472 thuốc từ Cục Quản lý Dược. Điểm mới về mặt kỹ thuật là RAG-MediSign "
             "\"phi tiêu chuẩn\": kết hợp tìm kiếm thưa (BM25), tìm kiếm đặc (sentence "
             "embeddings), hợp nhất bằng RRF và cơ chế KBLazyLoader fallback động khi điểm "
             "điều hồi thấp; bên cạnh đó là phân loại khẩn cấp ba mức Xanh – Vàng – Đỏ với "
             "tầng rule-based bypass cho các triệu chứng nguy hiểm. Kết quả cho thấy hệ "
             "thống đã triển khai 23 bảng cơ sở dữ liệu, 80 endpoint REST, 14 module "
             "Flutter và 3.248 bệnh sau khi hợp nhất bộ điều Vinmec và HelloBacsi; nền "
             "tảng đã sẵn sàng cho đánh giá thực nghiệm trong giai đoạn tiếp theo. Kết "
             "luận, MediSign AI mở ra một hướng tiếp cận khả thi cho các đề tài sinh viên "
             "khi muốn xây dựng trợ lý y tế AI gần người yếu thế và tuân thủ nguyên tắc "
             "an toàn y khoa.")
    add_para(doc, "", indent_first=False)
    p = doc.add_paragraph()
    run = p.add_run("Từ khóa: ")
    set_run_font(run, bold=True, italic=True, size=12)
    run = p.add_run("MediSign AI; Self-hosted LLM; MedGemma; QLoRA; Retrieval-Augmented "
                    "Generation (RAG); Triage y khoa; Người khuyết tật; Sức khỏe tâm thần; "
                    "Y tế số Việt Nam.")
    set_run_font(run, italic=True, size=12)
    set_paragraph_format(p, indent_first=False)
    page_break(doc)


def build_abbreviations(doc):
    add_heading_1(doc, "DANH MỤC TỪ VIẾT TẮT")
    rows = [
        ("AI", "Artificial Intelligence (Trí tuệ nhân tạo)"),
        ("API", "Application Programming Interface (Giao diện lập trình ứng dụng)"),
        ("APA", "American Psychological Association (Chuẩn trích dẫn APA)"),
        ("BM25", "Best Matching 25 – thuật toán xếp hạng văn bản thưa"),
        ("BYT", "Bộ Y tế"),
        ("CRUD", "Create-Read-Update-Delete – bốn thao tác cơ bản trên dữ liệu"),
        ("DAV", "Drug Administration of Vietnam – Cục Quản lý Dược Việt Nam"),
        ("ERD", "Entity-Relationship Diagram (Sơ đồ quan hệ thực thể)"),
        ("FAQ", "Frequently Asked Questions (Câu hỏi thường gặp)"),
        ("HSU", "Quy chuẩn trình bày báo cáo học thuật (theo tài liệu HSU Standards)"),
        ("JSON", "JavaScript Object Notation"),
        ("JWT", "JSON Web Token"),
        ("KB", "Knowledge Base (Kho tri thức)"),
        ("LLM", "Large Language Model (Mô hình ngôn ngữ lớn)"),
        ("LoRA", "Low-Rank Adaptation – kỹ thuật tinh chỉnh hiệu quả"),
        ("LOC", "Lines of Code (Số dòng mã nguồn)"),
        ("MedQuAD", "Medical Question Answering Dataset"),
        ("MVP", "Minimum Viable Product (Sản phẩm khả thi tối thiểu)"),
        ("NCKH", "Nghiên cứu Khoa học"),
        ("NIN", "Viện Dinh dưỡng Quốc gia"),
        ("NIH ODS", "U.S. National Institutes of Health – Office of Dietary Supplements"),
        ("NKT", "Người Khuyết Tật"),
        ("NTTU", "Trường Đại học Nguyễn Tất Thành"),
        ("OCR", "Optical Character Recognition (Nhận dạng ký tự quang học)"),
        ("OARS", "Open question – Affirm – Reflect – Summary, khung phỏng vấn tạo động lực"),
        ("PEFT", "Parameter-Efficient Fine-Tuning"),
        ("QLoRA", "Quantized LoRA – LoRA trên mô hình lượng tử hóa 4-bit"),
        ("RAG", "Retrieval-Augmented Generation (Sinh tăng cường dựa trên truy hồi)"),
        ("RDA", "Recommended Dietary Allowance"),
        ("REST", "Representational State Transfer"),
        ("RRF", "Reciprocal Rank Fusion – phép hợp nhất xếp hạng đảo nghịch"),
        ("SDK", "Software Development Kit"),
        ("SI", "Similarity Index – chỉ số trùng lặp Turnitin"),
        ("SQL", "Structured Query Language"),
        ("TFLite", "TensorFlow Lite – định dạng mô hình nhẹ cho thiết bị"),
        ("UI/UX", "User Interface / User Experience"),
        ("VSL", "Vietnamese Sign Language (Ngôn ngữ Ký hiệu Việt Nam)"),
    ]
    add_table(doc, ["Viết tắt", "Ý nghĩa"], rows, col_widths=[3.0, 12.0])
    page_break(doc)


def build_list_of_tables(doc):
    add_tof_field(doc, label="Bảng", title="DANH MỤC BẢNG BIỂU")
    page_break(doc)


def build_list_of_figures(doc):
    add_tof_field(doc, label="Hình", title="DANH MỤC HÌNH ẢNH")
    page_break(doc)


def build_toc(doc):
    add_toc_field(doc, levels=3, title="MỤC LỤC")
    page_break(doc)


print("part1 OK")
