# -*- coding: utf-8 -*-
"""Chapter 1 + Chapter 2."""
import sys
sys.path.insert(0, r"C:\NDT\PJ\MediSign_AI - Copy\report_build")
from report_helpers import *


def build_chapter_1(doc):
    add_heading_1(doc, "CHƯƠNG 1. PHẦN MỞ ĐẦU")

    add_heading_2(doc, "1.1. Bối cảnh nghiên cứu")
    add_para(doc,
        "Việt Nam đang đứng trước nhiều thách thức song hành trong lĩnh vực chăm sóc "
        "sức khỏe ban đầu. Theo số liệu của Tổng cục Thống kê, năm 2024 cả nước có "
        "khoảng 7,06% dân số sống chung với một dạng khuyết tật và tỷ lệ người cao "
        "tuổi đã vượt 12% [cần bổ sung số liệu cập nhật]. Cùng lúc đó, hệ thống y tế "
        "tuyến trên thường xuyên trong tình trạng quá tải còn các trạm y tế tuyến cơ "
        "sở chưa đáp ứng được nhu cầu tư vấn cá nhân hóa, đặc biệt là cho người "
        "khuyết tật, người cao tuổi và các hộ thu nhập thấp ở vùng sâu, vùng xa.")
    add_para(doc,
        "Một quan sát thực tiễn quan trọng trong xã hội Việt Nam là sự mất cân bằng "
        "trong hành vi tìm kiếm dịch vụ y tế: một bộ phận người dân quá thận trọng, "
        "tìm đến bệnh viện ngay khi mới có dấu hiệu nhẹ và làm tăng áp lực không cần "
        "thiết cho hệ thống y tế; một bộ phận khác lại có xu hướng \"chờ cho qua\", "
        "chỉ đến cơ sở y tế khi triệu chứng đã chuyển sang giai đoạn nặng hoặc xảy "
        "ra biến chứng. Song song với đó là thói quen tự kê đơn tại nhà – mua kháng "
        "sinh, giảm đau hay thuốc kê đơn mà không cần đơn bác sĩ – vốn đã được nhiều "
        "nghiên cứu và báo cáo của Bộ Y tế cảnh báo là một trong những nguyên nhân "
        "trực tiếp dẫn đến kháng kháng sinh và phản ứng có hại của thuốc.")
    add_para(doc,
        "Bên cạnh các vấn đề thuần túy về sức khỏe thể chất, các rối loạn sức khỏe "
        "tâm thần đang ngày càng phổ biến và trẻ hóa. Áp lực học hành, công việc, "
        "biến động xã hội cũng như sang chấn hậu đại dịch khiến tỷ lệ người mắc lo "
        "âu, trầm cảm, mất ngủ tăng nhanh nhưng không phải ai cũng có điều kiện hoặc "
        "đủ tin tưởng để tìm đến chuyên gia tâm lý. Khoảng cách giữa nhu cầu và "
        "nguồn lực hỗ trợ tâm thần ban đầu vì thế ngày một mở rộng.")
    add_para(doc,
        "Trong bối cảnh trên, sự phát triển nhanh của các mô hình ngôn ngữ lớn "
        "(LLM) và các kỹ thuật như Retrieval-Augmented Generation (RAG), LoRA, "
        "QLoRA đã mở ra cơ hội xây dựng các trợ lý y tế thông minh có khả năng "
        "hoạt động ngay tại Việt Nam, hỗ trợ cả ba nhóm vấn đề: tư vấn chăm sóc "
        "sức khỏe ban đầu, đồng hành sức khỏe tinh thần và hỗ trợ giao tiếp cho "
        "người khuyết tật. Tuy nhiên, các giải pháp dựa trên Cloud API thường vấp "
        "phải bài toán chi phí đắt đỏ, độ trễ cao và lo ngại về quyền riêng tư dữ "
        "liệu y tế. Đề tài \"MediSign AI\" được đề xuất nhằm trả lời câu hỏi: liệu "
        "có thể xây dựng một hệ thống self-hosted LLM, kết hợp RAG được tùy biến "
        "cho miền y tế Việt Nam, đủ khả thi để triển khai ở quy mô đề tài sinh "
        "viên cấp Trường hay không.")

    add_heading_2(doc, "1.2. Mục tiêu và câu hỏi nghiên cứu")
    add_heading_3(doc, "1.2.1. Mục tiêu tổng quát")
    add_para(doc,
        "Nghiên cứu, thiết kế và xây dựng hệ thống ứng dụng đa nền tảng \"MediSign "
        "AI\" tích hợp bốn module cốt lõi gồm Trợ lý Y khoa AI, Camera Quét Thuốc, "
        "Soul Garden cho sức khỏe tinh thần và Hỗ trợ Người Khuyết Tật, dựa trên "
        "kiến trúc self-hosted LLM kết hợp RAG được tùy biến cho miền y tế Việt "
        "Nam.")
    add_heading_3(doc, "1.2.2. Mục tiêu cụ thể")
    for item in [
        "Phân tích cơ sở lý thuyết về self-hosted LLM, RAG, LoRA fine-tuning và "
        "các mô hình AI y khoa hiện hành.",
        "Khảo sát nhu cầu thực tế của người khuyết tật và người cao tuổi thông qua "
        "phỏng vấn sâu và bảng câu hỏi.",
        "Thiết kế kiến trúc hệ thống đa nền tảng, đặc biệt là biến thể RAG-MediSign "
        "kết hợp BM25, embeddings dày đặc và RRF.",
        "Triển khai mô hình MedGemma 1.5 4B với hai adapter QLoRA chuyên biệt cho "
        "y khoa và tâm lý.",
        "Đánh giá hệ thống trên các khía cạnh kỹ thuật (LOC, hiệu năng, độ phủ tri "
        "thức) và trải nghiệm người dùng (định tính qua phỏng vấn).",
    ]:
        add_dash_item(doc, item)
    add_heading_3(doc, "1.2.3. Câu hỏi nghiên cứu")
    add_para(doc, "Đề tài tập trung trả lời ba câu hỏi sau:")
    for q in [
        "RQ1. Biến thể RAG-MediSign (BM25 + Dense + RRF + KBLazyLoader) khác RAG "
        "tiêu chuẩn ở những điểm nào về độ phủ tri thức và độ phù hợp với hỏi đáp "
        "y khoa tiếng Việt?",
        "RQ2. Kiến trúc Dual LoRA Adapter (Medical + Psychology) trên cùng một mô "
        "hình nền MedGemma 1.5 4B có hỗ trợ tách bạch hai phong cách tư vấn (y "
        "khoa và tâm lý) hay không, và có những đánh đổi gì về tài nguyên?",
        "RQ3. Mô hình triển khai self-hosted LLM cho MediSign AI có khả thi về chi "
        "phí và an toàn dữ liệu trong điều kiện một đề tài sinh viên cấp Trường so "
        "với phương án Cloud API thuần túy?",
    ]:
        add_dash_item(doc, q)

    add_heading_2(doc, "1.3. Tầm quan trọng của nghiên cứu")
    add_para(doc,
        "Đề tài có ý nghĩa khoa học và thực tiễn rõ rệt. Về mặt khoa học, nghiên "
        "cứu đóng góp một thiết kế RAG \"phi tiêu chuẩn\" thích nghi với điều kiện "
        "đặc thù của miền y tế Việt Nam: kho tri thức hỗn hợp giữa dữ liệu thuốc "
        "(Cục Quản lý Dược), bài viết bệnh học (Vinmec, Hello Bacsi), khuyến nghị "
        "dinh dưỡng và các tương tác thuốc nguy hiểm. Về mặt thực tiễn, hệ thống "
        "hướng tới các nhóm yếu thế thường bị bỏ qua khi xây dựng các sản phẩm "
        "công nghệ y tế: người khuyết tật, người cao tuổi, người ở vùng sâu vùng "
        "xa và những người không có điều kiện chi trả cho dịch vụ tư vấn riêng.")
    add_para(doc,
        "Về mặt giáo dục, đề tài cũng minh họa cách một sinh viên có thể vận dụng "
        "các kỹ thuật AI hiện đại trong khuôn khổ đề tài cấp Trường để tạo ra một "
        "sản phẩm có tính nhân văn cao thay vì chỉ dừng ở mức demo công nghệ. Đây "
        "là điểm mà đề bài \"MediSign AI\" coi như một mục tiêu mềm song hành với "
        "các mục tiêu kỹ thuật.")

    add_heading_2(doc, "1.4. Đối tượng và phạm vi nghiên cứu")
    add_heading_3(doc, "1.4.1. Đối tượng nghiên cứu")
    add_para(doc,
        "Đối tượng nghiên cứu chính là kiến trúc và quy trình triển khai một trợ "
        "lý y tế dựa trên self-hosted LLM cho người dùng phổ thông tại Việt Nam, "
        "bao gồm: mô hình ngôn ngữ y khoa MedGemma 1.5 4B, kỹ thuật QLoRA, đường "
        "ống RAG hỗn hợp BM25/Dense, kho tri thức 128.380 bản ghi, và các module "
        "ứng dụng đầu cuối trên Flutter và Next.js.")
    add_heading_3(doc, "1.4.2. Phạm vi nghiên cứu")
    add_para(doc, "Đề tài giới hạn trong các phạm vi sau:")
    for item in [
        "Phạm vi không gian: nghiên cứu thực hiện tại Trường Đại học Nguyễn Tất "
        "Thành (TP. Hồ Chí Minh); người dùng mục tiêu là người Việt Nam.",
        "Phạm vi thời gian: từ tháng 02/2026 đến tháng 12/2026.",
        "Phạm vi chuyên môn: chỉ tập trung vào tư vấn ban đầu mang tính tham khảo, "
        "không thay thế chẩn đoán y khoa; mọi khuyến nghị nguy hiểm đều phải dẫn "
        "dắt người dùng tới cơ sở y tế thật.",
        "Phạm vi kỹ thuật: chỉ huấn luyện adapter văn bản, chưa bao gồm vision "
        "fine-tuning; module nhận diện ngôn ngữ ký hiệu dừng ở giai đoạn skeleton "
        "và mock service [cần bổ sung dataset VSL chính thức].",
    ]:
        add_dash_item(doc, item)

    page_break(doc)


def build_chapter_2(doc):
    add_heading_1(doc, "CHƯƠNG 2. TỔNG QUAN LÝ THUYẾT")

    add_heading_2(doc, "2.1. Self-hosted LLM và so sánh với Cloud API")
    add_para(doc,
        "Mô hình ngôn ngữ lớn (Large Language Model – LLM) là họ mô hình học sâu "
        "được huấn luyện trên kho dữ liệu văn bản khổng lồ và có khả năng sinh "
        "ngôn ngữ tự nhiên. Trong các ứng dụng y tế, hai phương án triển khai phổ "
        "biến là sử dụng dịch vụ Cloud API (ví dụ OpenAI, Google Gemini) và tự "
        "trien khai self-hosted (ví dụ MedGemma, Llama, Gemma). Mỗi phương án có "
        "những đánh đổi rõ rệt về chi phí, độ trễ, quyền riêng tư và khả năng "
        "kiểm soát.")
    add_table_caption(doc, "Bảng 2.1. So sánh Cloud API và Self-hosted LLM ở quy mô đề tài sinh viên")
    add_table(doc,
              ["Tiêu chí", "Cloud API", "Self-hosted (MedGemma 4B)"],
              [
                  ["Chi phí định kỳ", "Trả theo token, biến động", "Đầu tư GPU một lần, vận hành ổn định"],
                  ["Độ trễ", "Phụ thuộc đường truyền", "Chủ động, có thể tối ưu cục bộ"],
                  ["Quyền riêng tư", "Dữ liệu rời khỏi tổ chức", "Dữ liệu nằm trong hạ tầng kiểm soát"],
                  ["Khả năng tùy biến", "Hạn chế (prompt engineering)", "Cao – có thể fine-tune adapter"],
                  ["Yêu cầu hạ tầng", "Không", "Cần GPU 24 GB hoặc 2× T4 free"],
                  ["Phù hợp đề tài SV", "Phù hợp prototyping", "Phù hợp khi cần kiểm soát dữ liệu y khoa"],
              ],
              col_widths=[4.5, 5.0, 6.0])
    add_table_source(doc, "Nguồn: Tác giả tổng hợp từ Touvron et al. (2023), Hu et al. (2021), tài liệu MedGemma (Google, 2024)")
    add_para(doc,
        "Đề tài MediSign AI lựa chọn cách tiếp cận self-hosted vì ba lý do: dữ "
        "liệu y khoa là loại dữ liệu nhạy cảm cần được bảo vệ; khả năng tinh chỉnh "
        "adapter là điều kiện then chốt để mô hình hiểu cách diễn đạt triệu chứng "
        "của người Việt; và chi phí biên cho từng câu hỏi gần như bằng không khi "
        "đã có hạ tầng. Trong các phiên bản trước của thiết kế, một số mô hình "
        "Cloud từng được cân nhắc làm fallback nhưng đã được loại bỏ trong giai "
        "đoạn hiện tại để giữ tính nhất quán \"on-premise\" cho hệ thống.")

    add_heading_2(doc, "2.2. Kỹ thuật Retrieval-Augmented Generation (RAG)")
    add_para(doc,
        "RAG là kỹ thuật được Lewis và cộng sự đề xuất năm 2020 nhằm bổ sung tri "
        "thức bên ngoài cho LLM thay vì cố nhồi mọi thông tin vào trọng số mô "
        "hình. Một đường ống RAG tiêu chuẩn gồm ba khối chính: (1) bộ điều hồi "
        "(retriever) trả về các đoạn văn liên quan từ kho tri thức; (2) bộ tổng "
        "hợp (generator) – chính là LLM – tạo câu trả lời dựa trên cả truy vấn và "
        "ngữ cảnh điều hồi; (3) hệ thống chỉ mục dữ liệu (vector store hoặc "
        "inverted index).")
    add_para(doc,
        "Trong miền y khoa, RAG đặc biệt quan trọng vì hai lý do. Thứ nhất, tri "
        "thức y khoa thay đổi nhanh – thuốc mới, phác đồ mới, cảnh báo tương tác "
        "mới được công bố thường xuyên – nên việc nhồi vào trọng số mô hình là "
        "không khả thi. Thứ hai, RAG cho phép trích nguồn (citation), một yêu cầu "
        "thiết yếu của bất kỳ hệ thống tư vấn y khoa nào. Trong đề tài, RAG được "
        "tùy biến đặc biệt để bù đắp cho các đặc thù của tiếng Việt và miền y tế "
        "Việt Nam, sẽ được mô tả chi tiết trong Chương 3.")

    add_heading_2(doc, "2.3. LoRA và kiến trúc Dual Adapter")
    add_para(doc,
        "Low-Rank Adaptation (LoRA) là kỹ thuật được Hu và cộng sự đề xuất năm "
        "2021, cho phép tinh chỉnh các mô hình ngôn ngữ lớn bằng cách chỉ huấn "
        "luyện một lượng nhỏ tham số bổ sung dạng ma trận hạng thấp, thay vì "
        "huấn luyện lại toàn bộ tham số gốc. QLoRA (Dettmers và cộng sự, 2023) "
        "mở rộng LoRA bằng cách lượng tử hóa mô hình nền xuống 4-bit và áp dụng "
        "LoRA trên đó, giúp giảm mạnh nhu cầu bộ nhớ GPU.")
    add_para(doc,
        "Trong MediSign AI, kiến trúc \"Dual LoRA Adapter\" được áp dụng cho mô "
        "hình MedGemma 1.5 4B: một adapter Medical phụ trách tư vấn y khoa thông "
        "thường (đang deploy: r=64, alpha=64, ~250 MB), một adapter Psychology phụ "
        "trách các tình huống đồng hành sức khỏe tinh thần (r=8, alpha=16, ~62 MB). "
        "Cả hai adapter có thể nạp/tháo theo ngữ cảnh truy vấn để hệ thống chuyển "
        "phong cách linh hoạt giữa hai miền chuyên môn mà vẫn giữ chung mô hình nền. "
        "Lưu ý: cấu hình deploy của adapter Medical (r=64) cao hơn default của các "
        "script huấn luyện trong repo (r=16 production / r=32 manual); việc re-train "
        "sẽ tạo ra adapter có kích thước nhỏ hơn.")

    add_heading_2(doc, "2.4. Mô hình AI y khoa: MedGemma, ChatDoctor và các đối thủ")
    add_para(doc,
        "MedGemma (Google, 2024) là họ mô hình mở rộng của Gemma được tinh chỉnh "
        "trên dữ liệu y khoa và sinh học. Phiên bản MedGemma 1.5 4B Instruct được "
        "đề tài lựa chọn vì cân bằng tốt giữa chất lượng đầu ra và yêu cầu phần "
        "cứng (có thể chạy trên một RTX 4090 hoặc hai T4 trên Kaggle Free). Bên "
        "cạnh đó, đề tài cũng tham khảo các tập dữ liệu lớn như ChatDoctor (Yunxiang "
        "et al., 2023), MedQuAD (Ben Abacha & Demner-Fushman, 2019) và bộ Medical "
        "Dialogue 2010–2020 cho khâu chuẩn bị dữ liệu huấn luyện.")
    add_para(doc,
        "Trong các phương án thay thế, một số mô hình Cloud từng được cân nhắc "
        "nhưng đã được loại bỏ khỏi pipeline để giữ tính nhất quán self-hosted; "
        "MedGemma 4B được sử dụng làm mô hình lõi duy nhất cho cả truy vấn y khoa "
        "và truy vấn tâm lý thông qua hai adapter chuyên biệt.")

    add_heading_2(doc, "2.5. OCR và nhận diện thông tin thuốc")
    add_para(doc,
        "Module Camera Quét Thuốc dựa trên hai khối: tiền xử lý ảnh (resize, khử "
        "nhiễu, chuyển ảnh xám) và nhận diện ký tự quang học (OCR). Các thư viện "
        "phổ biến trong miền tiếng Việt gồm Tesseract, PaddleOCR và VietOCR. Sau "
        "OCR, văn bản trích xuất được đối chiếu với cơ sở dữ liệu thuốc DAV (60.472 "
        "thuốc, 67.493 nhãn tương tác) để xác định hoạt chất, hàm lượng, dạng bào "
        "chế, cảnh báo và chống chỉ định.")

    add_heading_2(doc, "2.6. Sign Language Recognition và 3D Avatar")
    add_para(doc,
        "Nhận diện ngôn ngữ ký hiệu (Sign Language Recognition – SLR) là bài toán "
        "phân lớp chuỗi cử chỉ tay từ chuỗi khung hình video. Hai cách tiếp cận "
        "phổ biến là dùng landmark tay (MediaPipe) kết hợp mạng phân lớp cử chỉ, "
        "hoặc dùng mô hình end-to-end trên video. Đối với tiếng Việt, dữ liệu "
        "công khai về Vietnamese Sign Language (VSL) còn rất hạn chế, là một "
        "khoảng trống đáng kể. Trong giai đoạn này, MediSign AI giữ giao diện "
        "trừu tượng SignLanguageService và một MockSignLanguageService để chuẩn "
        "bị sẵn cho việc tích hợp mô hình thật khi có dataset VSL [cần bổ sung "
        "thêm sau].")

    add_heading_2(doc, "2.7. Các nghiên cứu liên quan và khoảng trống nghiên cứu")
    add_para(doc,
        "Trên thế giới, nhiều nghiên cứu đã ứng dụng RAG cho tư vấn y khoa trên "
        "tiếng Anh (Ben Abacha et al., 2019; Yunxiang et al., 2023). Tuy vậy, các "
        "công trình tập trung vào miền y tế Việt Nam, đặc biệt là kết hợp đồng "
        "thời tư vấn y khoa, đồng hành tâm lý và hỗ trợ người khuyết tật trên "
        "cùng một hệ thống self-hosted còn hiếm. Khoảng trống nghiên cứu mà đề "
        "tài hướng tới gồm:")
    for it in [
        "Khoảng trống về dữ liệu: thiếu các kho tri thức tổng hợp, đa nguồn, có "
        "tổ chức cho miền y tế Việt Nam.",
        "Khoảng trống về kiến trúc: thiếu mô tả chi tiết về RAG hỗn hợp BM25 + "
        "Dense + RRF + KBLazyLoader trong miền y tế tiếng Việt.",
        "Khoảng trống về thiết kế trải nghiệm: ít nghiên cứu kết hợp đồng thời "
        "ba kênh hỗ trợ (sức khỏe thể chất, tâm thần, người khuyết tật) trong "
        "một sản phẩm.",
    ]:
        add_dash_item(doc, it)

    page_break(doc)


print("part2 OK")
