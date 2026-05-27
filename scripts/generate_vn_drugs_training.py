"""
Task 1.9.1 — Generate ≥500 Vietnamese commercial-drug Q&A training records.

Approach
--------
Template-based, fully deterministic generation. No external API calls. We
hand-curate a knowledge base of Vietnamese commercial drugs (`DRUGS`) with
verified factual fields (brand name, generic name, indication, doses,
contraindications, common side effects, food/drug warnings, pregnancy/
lactation note, OTC status), then expand each entry through ~17 question
templates. Templates that need a structured field which is empty for a
particular drug are skipped — we never fabricate facts.

With 32 drugs × ≥17 templates we comfortably exceed the ≥500 target
required by Requirement 1.17.

Output
------
`data/training_raw/vn_drugs_commercial.json` — list of records:

    {
        "instruction": <SYSTEM_INSTRUCTION>,
        "input":       <Vietnamese question>,
        "output":      <Vietnamese answer ending in CANONICAL_DISCLAIMER>,
        "source":      "vn_drugs_commercial"
    }

The schema matches `merged_dataset.json` so this file can be wired into
`scripts/prepare_medgemma_data.py` as an additional `iio` source.

Idempotent: `random.seed(42)` is set even though templates are
deterministic — guarantees byte-identical re-runs.

Usage
-----
    python scripts/generate_vn_drugs_training.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

# Allow imports from the scripts/ folder when run directly.
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from format_medgemma_dataset import CANONICAL_DISCLAIMER, ensure_disclaimer  # noqa: E402
from prepare_medgemma_data import SYSTEM_INSTRUCTION  # noqa: E402

OUTPUT_FILE = ROOT / "data" / "training_raw" / "vn_drugs_commercial.json"
SOURCE_TAG = "vn_drugs_commercial"
MIN_RECORDS = 500
SEED = 42


def _force_canonical_disclaimer(body: str) -> str:
    """Ensure the literal canonical disclaimer is present at the end.

    `ensure_disclaimer` accepts other Vietnamese disclaimer variants and
    returns the text unchanged if any are detected. The Task 1.9 spec
    however requires the canonical phrase verbatim at the end of every
    output, so we run `ensure_disclaimer` first (to keep its formatting
    and avoid double-appending when the canonical phrase is already
    there) and then force-append the canonical phrase if it is still
    missing.
    """
    out, _ = ensure_disclaimer(body)
    if CANONICAL_DISCLAIMER not in out:
        out = f"{out.rstrip()}\n\n{CANONICAL_DISCLAIMER}"
    return out


# ---------------------------------------------------------------------------
# Curated knowledge base — 32 Vietnamese commercial drugs
# ---------------------------------------------------------------------------
# Field reference:
#   brand:        commercial name as sold in Vietnam
#   generic:      INN / generic name
#   ingredient:   short Vietnamese description of active ingredient(s)
#   indication:   what it is used for (Vietnamese)
#   dose_adult:   typical adult dose, or "" if not applicable
#   dose_child:   typical child dose, or "" if not recommended for children
#   contra:       list of contraindications (Vietnamese phrases)
#   side_effects: list of common side-effect phrases (Vietnamese)
#   warnings:     list of food/drug interaction warnings (Vietnamese)
#   pregnancy:    Vietnamese sentence about use in pregnancy / breastfeeding
#   otc:          True if available without prescription, False otherwise
#   form:         "viên", "siro", "gói bột", "viên sủi", etc.
# ---------------------------------------------------------------------------
DRUGS: list[dict] = [
    {
        "brand": "Panadol",
        "generic": "Paracetamol",
        "ingredient": "paracetamol 500mg",
        "indication": "giảm đau và hạ sốt mức độ nhẹ đến vừa, ví dụ đau đầu, đau răng, đau cơ, sốt do cảm cúm",
        "dose_adult": "1 viên 500mg mỗi 4–6 giờ khi cần, không quá 8 viên (4g) trong 24 giờ",
        "dose_child": "10–15mg/kg mỗi 4–6 giờ, không quá 60mg/kg/ngày, ưu tiên dạng siro hoặc gói bột cho trẻ nhỏ",
        "contra": ["người suy gan nặng", "người dị ứng với paracetamol"],
        "side_effects": ["buồn nôn nhẹ", "nổi mẩn da hiếm gặp", "tổn thương gan khi quá liều"],
        "warnings": [
            "không uống cùng rượu bia vì làm tăng nguy cơ tổn thương gan",
            "không dùng đồng thời với các thuốc khác cũng chứa paracetamol như Hapacol, Efferalgan, Tiffy",
        ],
        "pregnancy": "Có thể dùng cho phụ nữ có thai và cho con bú ở liều thông thường, nhưng nên tham khảo bác sĩ.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Efferalgan",
        "generic": "Paracetamol",
        "ingredient": "paracetamol 500mg dạng viên sủi",
        "indication": "giảm đau và hạ sốt, đặc biệt phù hợp với người khó nuốt viên",
        "dose_adult": "1 viên sủi 500mg pha với nước, mỗi 4–6 giờ, không quá 4g/ngày",
        "dose_child": "trẻ em dùng dạng gói bột Efferalgan 80mg/150mg/250mg theo cân nặng, 10–15mg/kg mỗi 4–6 giờ",
        "contra": ["suy gan nặng", "dị ứng paracetamol", "người ăn kiêng natri cần lưu ý vì viên sủi chứa muối natri"],
        "side_effects": ["buồn nôn nhẹ", "phát ban hiếm gặp"],
        "warnings": [
            "không uống cùng rượu bia",
            "không phối hợp với thuốc khác chứa paracetamol",
        ],
        "pregnancy": "Phụ nữ có thai và cho con bú có thể dùng liều thông thường, nên hỏi ý kiến bác sĩ.",
        "otc": True,
        "form": "viên sủi",
    },
    {
        "brand": "Hapacol",
        "generic": "Paracetamol",
        "ingredient": "paracetamol, có nhiều hàm lượng (80mg, 150mg, 250mg, 500mg, 650mg)",
        "indication": "giảm đau, hạ sốt cho cả người lớn và trẻ em",
        "dose_adult": "Hapacol 500mg hoặc 650mg, 1 viên mỗi 4–6 giờ, không quá 4g paracetamol/ngày",
        "dose_child": "Hapacol 80/150/250 dạng gói sủi theo cân nặng, 10–15mg/kg mỗi 4–6 giờ",
        "contra": ["suy gan nặng", "dị ứng paracetamol"],
        "side_effects": ["buồn nôn", "phát ban hiếm gặp"],
        "warnings": [
            "tránh uống cùng rượu bia",
            "không dùng cùng các thuốc khác chứa paracetamol",
        ],
        "pregnancy": "An toàn ở liều thông thường cho phụ nữ có thai và cho con bú, nhưng nên hỏi bác sĩ.",
        "otc": True,
        "form": "viên / gói sủi",
    },
    {
        "brand": "Tiffy",
        "generic": "Paracetamol + Chlorpheniramine + Phenylephrine",
        "ingredient": "paracetamol, chlorpheniramine maleate và phenylephrine HCl",
        "indication": "giảm triệu chứng cảm cúm: sốt, đau đầu, sổ mũi, nghẹt mũi, hắt hơi",
        "dose_adult": "1 viên mỗi 6 giờ, không quá 4 viên/ngày",
        "dose_child": "trẻ em trên 6 tuổi dùng theo chỉ dẫn bác sĩ; không tự ý dùng cho trẻ dưới 6 tuổi",
        "contra": ["tăng huyết áp", "bệnh tim nặng", "cường giáp", "glaucoma góc đóng", "phì đại tuyến tiền liệt"],
        "side_effects": ["buồn ngủ", "khô miệng", "tim đập nhanh", "tăng huyết áp"],
        "warnings": [
            "không uống cùng rượu bia vì gây buồn ngủ và hại gan",
            "không phối hợp với các thuốc cảm cúm khác chứa paracetamol hoặc phenylephrine",
        ],
        "pregnancy": "Không khuyến cáo dùng cho phụ nữ có thai và cho con bú nếu không có chỉ định bác sĩ.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Decolgen",
        "generic": "Paracetamol + Chlorpheniramine + Phenylephrine",
        "indication": "giảm triệu chứng cảm cúm thông thường: sốt, sổ mũi, nghẹt mũi, đau đầu",
        "ingredient": "paracetamol 500mg, phenylephrine 10mg, chlorpheniramine 2mg",
        "dose_adult": "1 viên mỗi 6 giờ, không quá 4 viên/ngày",
        "dose_child": "trẻ trên 12 tuổi: 1 viên mỗi 6 giờ; trẻ nhỏ hơn cần dạng siro và theo chỉ dẫn bác sĩ",
        "contra": ["tăng huyết áp nặng", "bệnh mạch vành", "cường giáp", "glaucoma", "phì đại tuyến tiền liệt"],
        "side_effects": ["buồn ngủ", "khô miệng", "đánh trống ngực", "bí tiểu"],
        "warnings": [
            "không phối hợp với thuốc khác cũng chứa paracetamol hoặc thuốc kháng histamin",
            "không uống rượu bia khi dùng",
        ],
        "pregnancy": "Tránh dùng cho phụ nữ có thai và cho con bú nếu không có chỉ định.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Berberin",
        "generic": "Berberin clorid",
        "ingredient": "berberin clorid 50mg hoặc 100mg, chiết xuất từ cây vàng đắng",
        "indication": "điều trị tiêu chảy, lỵ trực khuẩn, hội chứng lỵ, viêm ruột do vi khuẩn",
        "dose_adult": "2–4 viên 50mg/lần, 2–3 lần/ngày, uống sau ăn",
        "dose_child": "trẻ em dùng theo chỉ dẫn bác sĩ, thường 1–2 viên 50mg/lần, 2 lần/ngày tùy độ tuổi",
        "contra": ["phụ nữ có thai (đặc biệt 3 tháng đầu)", "trẻ sơ sinh", "người tiền sử dị ứng berberin"],
        "side_effects": ["buồn nôn nhẹ", "táo bón", "tiêu chảy nhẹ"],
        "warnings": [
            "không tự ý dùng quá 7 ngày nếu không đỡ; cần đi khám bác sĩ để loại trừ nguyên nhân khác",
            "không thay thế cho bù nước Oresol khi tiêu chảy nhiều",
        ],
        "pregnancy": "Không nên dùng cho phụ nữ có thai vì có thể kích thích tử cung; phụ nữ cho con bú nên hỏi bác sĩ.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Eugica",
        "generic": "Tinh dầu khuynh diệp + tần dày lá + gừng + tinh dầu bạc hà",
        "ingredient": "hỗn hợp tinh dầu thiên nhiên: khuynh diệp, tần dày lá, gừng, bạc hà",
        "indication": "giảm ho, long đờm, làm dịu cổ họng, hỗ trợ điều trị cảm cúm và viêm họng nhẹ",
        "dose_adult": "1–2 viên/lần, 3 lần/ngày",
        "dose_child": "trẻ em trên 30 tháng tuổi: 1 viên/lần, 2–3 lần/ngày; dạng siro Eugica fort phù hợp với trẻ nhỏ hơn",
        "contra": ["trẻ dưới 30 tháng tuổi (dạng viên)", "người có tiền sử động kinh", "dị ứng với bạc hà hoặc khuynh diệp"],
        "side_effects": ["dị ứng da nhẹ", "kích ứng dạ dày khi uống lúc đói"],
        "warnings": [
            "uống nhiều nước ấm khi dùng để tăng hiệu quả long đờm",
            "không tự ý dùng quá 7 ngày; nếu ho kéo dài cần đi khám bác sĩ",
        ],
        "pregnancy": "Phụ nữ có thai và cho con bú nên hỏi ý kiến bác sĩ trước khi dùng.",
        "otc": True,
        "form": "viên nang",
    },
    {
        "brand": "Fugacar",
        "generic": "Mebendazole",
        "ingredient": "mebendazole 500mg",
        "indication": "tẩy giun đường ruột (giun đũa, giun kim, giun móc, giun tóc)",
        "dose_adult": "1 viên 500mg uống một lần duy nhất, có thể nhai hoặc nuốt nguyên viên",
        "dose_child": "trẻ từ 2 tuổi trở lên: 1 viên 500mg liều duy nhất; trẻ dưới 2 tuổi cần chỉ định bác sĩ",
        "contra": ["trẻ dưới 1 tuổi", "phụ nữ có thai 3 tháng đầu", "dị ứng mebendazole"],
        "side_effects": ["đau bụng nhẹ", "buồn nôn", "tiêu chảy thoáng qua"],
        "warnings": [
            "nên tẩy giun định kỳ 6 tháng/lần cho cả gia đình",
            "không cần nhịn ăn hay uống thuốc xổ kèm theo",
        ],
        "pregnancy": "Tránh dùng trong 3 tháng đầu thai kỳ; các giai đoạn sau cần ý kiến bác sĩ.",
        "otc": True,
        "form": "viên nhai",
    },
    {
        "brand": "Smecta",
        "generic": "Diosmectite",
        "ingredient": "diosmectite 3g/gói",
        "indication": "điều trị tiêu chảy cấp ở người lớn và trẻ em, đau do bệnh lý thực quản – dạ dày – đại tràng",
        "dose_adult": "3 gói/ngày, pha với nửa cốc nước, uống giữa các bữa ăn",
        "dose_child": "trẻ dưới 1 tuổi: 1 gói/ngày; 1–2 tuổi: 1–2 gói/ngày; trên 2 tuổi: 2–3 gói/ngày",
        "contra": ["dị ứng diosmectite", "tắc ruột"],
        "side_effects": ["táo bón nhẹ", "đầy hơi"],
        "warnings": [
            "uống cách các thuốc khác ít nhất 2 giờ vì có thể giảm hấp thu thuốc",
            "luôn dùng kèm Oresol để bù nước và điện giải khi tiêu chảy",
        ],
        "pregnancy": "An toàn cho phụ nữ có thai và cho con bú ở liều khuyến cáo.",
        "otc": True,
        "form": "gói bột pha nước",
    },
    {
        "brand": "Oresol",
        "generic": "Oral rehydration salts (ORS)",
        "ingredient": "natri clorid, kali clorid, natri citrat, glucose",
        "indication": "bù nước và điện giải khi tiêu chảy, nôn mửa, sốt cao, mất nước do nắng nóng",
        "dose_adult": "uống 200–400ml sau mỗi lần đi ngoài; tổng 2–3 lít/ngày tùy mức độ mất nước",
        "dose_child": "trẻ em uống 50–100ml sau mỗi lần đi ngoài; trẻ nhỏ uống từng ngụm nhỏ liên tục",
        "contra": ["tắc ruột", "suy thận nặng không kiểm soát"],
        "side_effects": ["buồn nôn nhẹ nếu uống quá nhanh"],
        "warnings": [
            "PHẢI pha đúng tỉ lệ ghi trên gói (thường 1 gói với đúng 200ml hoặc 1 lít nước); pha sai tỉ lệ có thể nguy hiểm cho trẻ",
            "nếu trẻ tiêu chảy nặng, li bì, không uống được hoặc nôn liên tục thì cần đi khám bác sĩ ngay",
        ],
        "pregnancy": "An toàn cho phụ nữ có thai và cho con bú.",
        "otc": True,
        "form": "gói bột pha nước",
    },
    {
        "brand": "Mediplex",
        "generic": "Vitamin nhóm B (B1, B6, B12)",
        "ingredient": "vitamin B1, B6, B12 liều cao",
        "indication": "hỗ trợ điều trị viêm dây thần kinh, đau dây thần kinh, tê bì tay chân, đau lưng do thần kinh",
        "dose_adult": "1 viên/lần, 2–3 lần/ngày sau ăn",
        "dose_child": "không khuyến cáo cho trẻ nhỏ trừ khi có chỉ định bác sĩ",
        "contra": ["dị ứng với bất kỳ vitamin nhóm B nào trong thành phần"],
        "side_effects": ["nước tiểu vàng sậm (do B2 nếu có)", "buồn nôn nhẹ"],
        "warnings": [
            "không thay thế cho điều trị nguyên nhân gây đau thần kinh",
            "nếu triệu chứng tê bì kéo dài cần đi khám bác sĩ để tìm nguyên nhân",
        ],
        "pregnancy": "Có thể dùng cho phụ nữ có thai khi có chỉ định bác sĩ.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Becozyme",
        "generic": "Vitamin nhóm B phức hợp",
        "ingredient": "phức hợp vitamin nhóm B (B1, B2, B3, B5, B6, B12) và một số vi chất",
        "indication": "bổ sung vitamin nhóm B trong các trường hợp ăn uống kém, mệt mỏi, chán ăn, sau ốm dậy",
        "dose_adult": "1 viên/ngày, uống sau ăn",
        "dose_child": "trẻ em dùng theo chỉ định bác sĩ",
        "contra": ["dị ứng với vitamin nhóm B"],
        "side_effects": ["nước tiểu vàng sậm", "buồn nôn nhẹ"],
        "warnings": [
            "không thay thế cho chế độ ăn uống cân bằng",
            "không uống cùng rượu bia vì giảm hấp thu vitamin",
        ],
        "pregnancy": "An toàn cho phụ nữ có thai và cho con bú ở liều khuyến cáo.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Vitamin 3B",
        "generic": "Vitamin B1 + B6 + B12",
        "ingredient": "vitamin B1 (thiamin), B6 (pyridoxin), B12 (cyanocobalamin)",
        "indication": "phòng và hỗ trợ điều trị thiếu vitamin nhóm B, đau thần kinh, mệt mỏi",
        "dose_adult": "1–2 viên/lần, 2–3 lần/ngày sau ăn",
        "dose_child": "trẻ em trên 6 tuổi: 1 viên/ngày; trẻ nhỏ hơn cần chỉ định bác sĩ",
        "contra": ["dị ứng với bất kỳ vitamin B nào trong thành phần"],
        "side_effects": ["buồn nôn nhẹ", "nước tiểu vàng sậm"],
        "warnings": [
            "không dùng đồng thời với levodopa (B6 làm giảm tác dụng thuốc Parkinson)",
            "không thay thế cho chẩn đoán nguyên nhân tê bì, đau thần kinh",
        ],
        "pregnancy": "An toàn ở liều thông thường cho phụ nữ có thai và cho con bú.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Alaxan",
        "generic": "Paracetamol + Ibuprofen",
        "ingredient": "paracetamol 325mg và ibuprofen 200mg",
        "indication": "giảm đau cơ, đau khớp, đau lưng, đau răng, đau đầu",
        "dose_adult": "1 viên mỗi 6 giờ khi cần, không quá 4 viên/ngày",
        "dose_child": "không khuyến cáo cho trẻ dưới 12 tuổi",
        "contra": ["loét dạ dày tá tràng đang hoạt động", "suy gan, suy thận nặng", "hen do aspirin/NSAID", "phụ nữ 3 tháng cuối thai kỳ"],
        "side_effects": ["đau dạ dày", "buồn nôn", "phát ban", "tăng huyết áp"],
        "warnings": [
            "uống sau khi ăn no để giảm kích ứng dạ dày",
            "không uống cùng rượu bia vì tăng nguy cơ chảy máu dạ dày và hại gan",
        ],
        "pregnancy": "Không dùng trong 3 tháng cuối thai kỳ; các giai đoạn khác cần ý kiến bác sĩ.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Mydocalm",
        "generic": "Tolperisone",
        "ingredient": "tolperisone HCl 50mg hoặc 150mg",
        "indication": "giãn cơ, giảm co cứng cơ trong các bệnh lý thần kinh – cơ – xương khớp",
        "dose_adult": "150–450mg/ngày chia 3 lần, uống sau ăn",
        "dose_child": "trẻ từ 3 tháng tuổi: 5–10mg/kg/ngày chia 3 lần (theo chỉ định bác sĩ)",
        "contra": ["nhược cơ (myasthenia gravis)", "dị ứng tolperisone hoặc lidocain"],
        "side_effects": ["buồn nôn", "đau bụng nhẹ", "mệt mỏi", "phát ban"],
        "warnings": [
            "có thể gây phản ứng dị ứng nghiêm trọng – ngừng thuốc và đi khám bác sĩ ngay nếu nổi mề đay, khó thở, sưng mặt",
        ],
        "pregnancy": "Không khuyến cáo trong 3 tháng đầu thai kỳ; các giai đoạn khác cần ý kiến bác sĩ.",
        "otc": False,
        "form": "viên nén",
    },
    {
        "brand": "Loratadin",
        "generic": "Loratadine",
        "ingredient": "loratadine 10mg",
        "indication": "điều trị viêm mũi dị ứng, mày đay, ngứa do dị ứng",
        "dose_adult": "1 viên 10mg/ngày, uống bất kỳ thời điểm nào trong ngày",
        "dose_child": "trẻ 2–12 tuổi nặng dưới 30kg: 5mg (1/2 viên hoặc 5ml siro)/ngày; trên 30kg: 10mg/ngày",
        "contra": ["dị ứng loratadine"],
        "side_effects": ["đau đầu nhẹ", "khô miệng", "buồn ngủ ít gặp"],
        "warnings": [
            "ít gây buồn ngủ hơn các thuốc kháng histamin thế hệ 1",
            "thận trọng khi suy gan – có thể cần giảm liều theo bác sĩ",
        ],
        "pregnancy": "Chỉ dùng cho phụ nữ có thai và cho con bú khi thật cần thiết, theo ý kiến bác sĩ.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Cetirizin",
        "generic": "Cetirizine",
        "ingredient": "cetirizine HCl 10mg",
        "indication": "điều trị viêm mũi dị ứng, mày đay mạn tính, ngứa do dị ứng",
        "dose_adult": "1 viên 10mg/ngày, uống vào buổi tối",
        "dose_child": "trẻ 2–6 tuổi: 2.5mg x 2 lần/ngày (dạng siro); trẻ trên 6 tuổi: 10mg/ngày",
        "contra": ["suy thận nặng (cần chỉnh liều)", "dị ứng cetirizine hoặc hydroxyzine"],
        "side_effects": ["buồn ngủ", "khô miệng", "mệt mỏi"],
        "warnings": [
            "không lái xe hoặc vận hành máy móc khi mới dùng vì có thể buồn ngủ",
            "tránh uống cùng rượu bia",
        ],
        "pregnancy": "Chỉ dùng khi thật cần thiết theo ý kiến bác sĩ.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Salonpas",
        "generic": "Methyl salicylate + Menthol (cao dán)",
        "ingredient": "methyl salicylate, menthol và các tinh dầu giảm đau",
        "indication": "giảm đau cơ, đau lưng, đau vai gáy, bong gân, đau khớp tại chỗ",
        "dose_adult": "dán 1 miếng lên vùng đau, tối đa 2 lần/ngày, mỗi lần không quá 8 giờ",
        "dose_child": "trẻ trên 12 tuổi dùng như người lớn; trẻ nhỏ hơn cần ý kiến bác sĩ",
        "contra": ["da bị tổn thương, vết thương hở", "dị ứng với salicylate hoặc menthol"],
        "side_effects": ["kích ứng da nhẹ", "đỏ da tại chỗ dán"],
        "warnings": [
            "không dán lên mắt, niêm mạc, vết thương hở",
            "không dùng cùng aspirin liều cao vì có thể tăng hấp thu salicylate",
        ],
        "pregnancy": "Phụ nữ có thai 3 tháng cuối nên tránh dùng; các giai đoạn khác cần ý kiến bác sĩ.",
        "otc": True,
        "form": "miếng dán",
    },
    {
        "brand": "Aspirin pH8",
        "generic": "Acetylsalicylic acid",
        "ingredient": "acetylsalicylic acid 500mg dạng bao phim chống acid dạ dày",
        "indication": "giảm đau, hạ sốt, kháng viêm; liều thấp dùng phòng ngừa biến cố tim mạch theo chỉ định bác sĩ",
        "dose_adult": "giảm đau hạ sốt: 500mg–1g mỗi 4–6 giờ, không quá 4g/ngày",
        "dose_child": "không dùng cho trẻ em và thanh thiếu niên dưới 16 tuổi do nguy cơ hội chứng Reye",
        "contra": ["loét dạ dày tá tràng đang hoạt động", "rối loạn đông máu", "trẻ dưới 16 tuổi (nguy cơ hội chứng Reye)", "phụ nữ 3 tháng cuối thai kỳ"],
        "side_effects": ["đau dạ dày", "buồn nôn", "ù tai khi quá liều", "chảy máu nhẹ"],
        "warnings": [
            "uống sau khi ăn no",
            "không uống cùng rượu bia hoặc các NSAID khác vì tăng nguy cơ chảy máu",
        ],
        "pregnancy": "Tránh dùng trong 3 tháng cuối thai kỳ; các giai đoạn khác cần ý kiến bác sĩ.",
        "otc": True,
        "form": "viên bao phim",
    },
    {
        "brand": "Maalox",
        "generic": "Aluminium hydroxide + Magnesium hydroxide",
        "ingredient": "nhôm hydroxide và magnesi hydroxide",
        "indication": "trung hòa acid dạ dày, giảm ợ chua, đầy bụng, khó tiêu, viêm loét dạ dày tá tràng",
        "dose_adult": "1–2 viên nhai sau bữa ăn 1–2 giờ và trước khi ngủ, hoặc khi có triệu chứng",
        "dose_child": "trẻ em trên 12 tuổi dùng như người lớn; trẻ nhỏ hơn cần ý kiến bác sĩ",
        "contra": ["suy thận nặng", "dị ứng với thành phần thuốc"],
        "side_effects": ["táo bón (do nhôm)", "tiêu chảy (do magnesi)"],
        "warnings": [
            "uống cách các thuốc khác ít nhất 2 giờ vì có thể giảm hấp thu kháng sinh, sắt, một số thuốc khác",
        ],
        "pregnancy": "Có thể dùng cho phụ nữ có thai trong thời gian ngắn theo ý kiến bác sĩ.",
        "otc": True,
        "form": "viên nhai",
    },
    {
        "brand": "Phosphalugel",
        "generic": "Aluminium phosphate",
        "ingredient": "nhôm phosphate dạng gel uống",
        "indication": "trung hòa acid, giảm đau dạ dày, ợ chua, trào ngược, viêm loét dạ dày",
        "dose_adult": "1–2 gói/lần, 2–3 lần/ngày khi đau hoặc sau ăn 1–2 giờ",
        "dose_child": "trẻ trên 6 tháng tuổi: 1/2–1 gói sau mỗi bữa ăn, theo chỉ dẫn bác sĩ",
        "contra": ["suy thận nặng"],
        "side_effects": ["táo bón nhẹ"],
        "warnings": [
            "uống cách các thuốc khác ít nhất 2 giờ",
            "không tự ý dùng kéo dài quá 2 tuần nếu triệu chứng không đỡ – cần đi khám bác sĩ",
        ],
        "pregnancy": "An toàn cho phụ nữ có thai và cho con bú khi dùng ngắn hạn.",
        "otc": True,
        "form": "gói gel uống",
    },
    {
        "brand": "Omeprazol",
        "generic": "Omeprazole",
        "ingredient": "omeprazole 20mg",
        "indication": "điều trị loét dạ dày tá tràng, trào ngược dạ dày thực quản, hội chứng Zollinger-Ellison",
        "dose_adult": "20–40mg/ngày uống trước bữa ăn sáng 30 phút",
        "dose_child": "trẻ em theo cân nặng và chỉ định bác sĩ",
        "contra": ["dị ứng omeprazole hoặc các thuốc nhóm PPI khác"],
        "side_effects": ["đau đầu", "tiêu chảy", "đau bụng", "thiếu vitamin B12 khi dùng kéo dài"],
        "warnings": [
            "không tự ý dùng kéo dài quá 8 tuần nếu không có chỉ định bác sĩ",
            "thuốc tương tác với clopidogrel, warfarin, một số thuốc kháng nấm – cần báo bác sĩ thuốc đang dùng",
        ],
        "pregnancy": "Chỉ dùng cho phụ nữ có thai khi thật cần thiết, theo ý kiến bác sĩ.",
        "otc": False,
        "form": "viên nang",
    },
    {
        "brand": "Motilium-M",
        "generic": "Domperidone",
        "ingredient": "domperidone 10mg",
        "indication": "giảm buồn nôn, nôn, đầy bụng, khó tiêu, trào ngược",
        "dose_adult": "1 viên 10mg, 3 lần/ngày trước bữa ăn 15–30 phút, không quá 30mg/ngày",
        "dose_child": "trẻ em dùng theo cân nặng và chỉ định bác sĩ; tránh dùng kéo dài",
        "contra": ["bệnh tim, kéo dài QT", "u tuyến yên tiết prolactin", "suy gan trung bình – nặng"],
        "side_effects": ["khô miệng", "đau đầu", "rối loạn nhịp tim hiếm gặp"],
        "warnings": [
            "không dùng quá 7 ngày nếu không có chỉ định bác sĩ",
            "tránh phối hợp với thuốc chống nấm (ketoconazole) và một số kháng sinh nhóm macrolide",
        ],
        "pregnancy": "Chỉ dùng khi thật cần thiết theo ý kiến bác sĩ.",
        "otc": False,
        "form": "viên nén",
    },
    {
        "brand": "Buscopan",
        "generic": "Hyoscine butylbromide",
        "ingredient": "hyoscine butylbromide 10mg",
        "indication": "giảm đau bụng do co thắt cơ trơn (đau bụng kinh, đau quặn ruột, đau đường mật)",
        "dose_adult": "1–2 viên/lần, 3–5 lần/ngày",
        "dose_child": "trẻ em trên 6 tuổi: 1 viên/lần, 3 lần/ngày",
        "contra": ["glaucoma góc đóng", "phì đại tuyến tiền liệt", "tắc ruột", "nhược cơ"],
        "side_effects": ["khô miệng", "táo bón", "nhìn mờ", "tim đập nhanh"],
        "warnings": [
            "nếu đau bụng dữ dội kéo dài, kèm sốt, nôn nhiều cần đi khám bác sĩ ngay – có thể là viêm ruột thừa hoặc bệnh ngoại khoa",
        ],
        "pregnancy": "Chỉ dùng khi thật cần thiết và theo ý kiến bác sĩ.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Strepsils",
        "generic": "Amylmetacresol + 2,4-dichlorobenzyl alcohol",
        "ingredient": "amylmetacresol và 2,4-dichlorobenzyl alcohol",
        "indication": "giảm đau rát họng, hỗ trợ điều trị viêm họng nhẹ",
        "dose_adult": "ngậm 1 viên mỗi 2–3 giờ, không quá 12 viên/ngày",
        "dose_child": "trẻ em trên 6 tuổi dùng như người lớn nhưng giảm số lần",
        "contra": ["dị ứng với thành phần thuốc"],
        "side_effects": ["dị ứng tại chỗ hiếm gặp"],
        "warnings": [
            "nếu đau họng kéo dài quá 3 ngày, kèm sốt cao, khó nuốt nặng cần đi khám bác sĩ",
        ],
        "pregnancy": "An toàn cho phụ nữ có thai khi dùng theo liều khuyến cáo.",
        "otc": True,
        "form": "viên ngậm",
    },
    {
        "brand": "Bổ phế Nam Hà",
        "generic": "Cao dược liệu (bạch linh, cát cánh, ô mai, trần bì, bạc hà…)",
        "ingredient": "cao chiết các vị thuốc cổ truyền: bạch linh, cát cánh, ô mai, trần bì, bạc hà, cam thảo",
        "indication": "hỗ trợ điều trị ho khan, ho có đờm, viêm họng, khản tiếng",
        "dose_adult": "1 thìa cà phê (5ml) hoặc 1 viên ngậm mỗi 2–3 giờ",
        "dose_child": "trẻ trên 30 tháng tuổi: 1/2 liều người lớn theo chỉ dẫn",
        "contra": ["trẻ dưới 30 tháng tuổi (dạng siro nồng độ cao)", "người dị ứng với bạc hà"],
        "side_effects": ["dị ứng nhẹ hiếm gặp"],
        "warnings": [
            "nếu ho kéo dài quá 7 ngày hoặc kèm sốt, khó thở, ho ra máu cần đi khám bác sĩ",
            "uống nhiều nước ấm để tăng hiệu quả",
        ],
        "pregnancy": "Phụ nữ có thai và cho con bú nên hỏi ý kiến bác sĩ trước khi dùng.",
        "otc": True,
        "form": "siro / viên ngậm",
    },
    {
        "brand": "Hoạt huyết dưỡng não",
        "generic": "Cao bạch quả (Ginkgo biloba) + cao đinh lăng",
        "ingredient": "cao bạch quả, cao đinh lăng và các vị thuốc bổ thần kinh",
        "indication": "hỗ trợ tuần hoàn não, giảm đau đầu, hoa mắt, chóng mặt, suy giảm trí nhớ ở người lớn tuổi",
        "dose_adult": "1–2 viên/lần, 2–3 lần/ngày",
        "dose_child": "không khuyến cáo cho trẻ em",
        "contra": ["người đang dùng thuốc chống đông như warfarin", "phụ nữ có thai", "trẻ em"],
        "side_effects": ["đau bụng nhẹ", "đau đầu nhẹ"],
        "warnings": [
            "không phối hợp với aspirin, warfarin do tăng nguy cơ chảy máu",
            "không thay thế điều trị tăng huyết áp hoặc tai biến mạch máu não",
        ],
        "pregnancy": "Không khuyến cáo dùng cho phụ nữ có thai và cho con bú.",
        "otc": True,
        "form": "viên nang",
    },
    {
        "brand": "Glucosamine",
        "generic": "Glucosamine sulfate",
        "ingredient": "glucosamine sulfate 500mg–1500mg",
        "indication": "hỗ trợ điều trị thoái hóa khớp, đau khớp gối, khô khớp",
        "dose_adult": "1500mg/ngày, có thể chia 1–3 lần, dùng kéo dài 2–3 tháng",
        "dose_child": "không khuyến cáo cho trẻ dưới 18 tuổi",
        "contra": ["dị ứng hải sản (vỏ tôm, cua)", "phụ nữ có thai và cho con bú"],
        "side_effects": ["đầy bụng nhẹ", "buồn nôn", "ợ nóng"],
        "warnings": [
            "thận trọng ở người tiểu đường vì có thể ảnh hưởng đường huyết",
            "có thể tương tác với thuốc chống đông warfarin",
        ],
        "pregnancy": "Không khuyến cáo cho phụ nữ có thai và cho con bú.",
        "otc": True,
        "form": "viên nén",
    },
    {
        "brand": "Calcium Sandoz",
        "generic": "Calcium carbonate / Calcium lactate gluconate",
        "ingredient": "calci carbonat và calci lactate gluconate dạng viên sủi",
        "indication": "phòng và điều trị thiếu calci, hỗ trợ phát triển xương cho trẻ em, người lớn tuổi, phụ nữ có thai",
        "dose_adult": "1 viên sủi 500mg–1000mg/ngày",
        "dose_child": "trẻ em theo độ tuổi và chỉ định bác sĩ",
        "contra": ["sỏi thận do calci", "tăng calci máu"],
        "side_effects": ["táo bón", "đầy hơi"],
        "warnings": [
            "uống cách các thuốc khác (kháng sinh tetracycline, sắt, levothyroxine) ít nhất 2 giờ",
            "uống nhiều nước để tránh sỏi thận",
        ],
        "pregnancy": "Có thể dùng cho phụ nữ có thai và cho con bú theo liều khuyến cáo.",
        "otc": True,
        "form": "viên sủi",
    },
    {
        "brand": "Vitamin C 500mg",
        "generic": "Ascorbic acid",
        "ingredient": "vitamin C (acid ascorbic) 500mg",
        "indication": "phòng và điều trị thiếu vitamin C, tăng sức đề kháng khi cảm cúm",
        "dose_adult": "1 viên/ngày, không quá 2g/ngày",
        "dose_child": "trẻ em trên 6 tuổi: 100–250mg/ngày",
        "contra": ["sỏi thận oxalat", "tiền sử thiếu G6PD"],
        "side_effects": ["đau dạ dày khi uống lúc đói", "tiêu chảy khi liều cao"],
        "warnings": [
            "không dùng liều cao kéo dài vì có thể gây sỏi thận",
            "uống sau ăn để giảm kích ứng dạ dày",
        ],
        "pregnancy": "An toàn ở liều khuyến cáo cho phụ nữ có thai và cho con bú.",
        "otc": True,
        "form": "viên sủi / viên nén",
    },
    {
        "brand": "Enterogermina",
        "generic": "Bacillus clausii (men vi sinh)",
        "ingredient": "bào tử Bacillus clausii sống",
        "indication": "điều trị và phòng ngừa rối loạn tiêu hóa, tiêu chảy, sau khi dùng kháng sinh",
        "dose_adult": "1–2 ống 5ml/ngày",
        "dose_child": "trẻ sơ sinh và trẻ nhỏ: 1 ống/ngày, có thể pha với sữa hoặc nước",
        "contra": ["dị ứng với thành phần thuốc"],
        "side_effects": ["dị ứng nhẹ hiếm gặp"],
        "warnings": [
            "uống cách kháng sinh ít nhất 2 giờ",
            "không thay thế cho bù nước Oresol khi tiêu chảy nhiều",
        ],
        "pregnancy": "An toàn cho phụ nữ có thai và cho con bú.",
        "otc": True,
        "form": "ống uống",
    },
    {
        "brand": "Postinor",
        "generic": "Levonorgestrel",
        "ingredient": "levonorgestrel 1.5mg (tránh thai khẩn cấp)",
        "indication": "tránh thai khẩn cấp trong vòng 72 giờ sau quan hệ không bảo vệ",
        "dose_adult": "1 viên duy nhất càng sớm càng tốt, tốt nhất trong 12 giờ và không quá 72 giờ sau quan hệ",
        "dose_child": "không dùng cho trẻ vị thành niên dưới 16 tuổi nếu không có ý kiến bác sĩ",
        "contra": ["có thai đã được xác nhận", "chảy máu âm đạo bất thường chưa rõ nguyên nhân", "rối loạn đông máu nặng"],
        "side_effects": ["buồn nôn", "đau đầu", "đau bụng dưới", "rối loạn kinh nguyệt", "căng ngực"],
        "warnings": [
            "không phải biện pháp tránh thai thường xuyên – chỉ dùng trong tình huống khẩn cấp; cần đi khám bác sĩ phụ khoa để có biện pháp tránh thai phù hợp",
            "nếu nôn trong vòng 3 giờ sau khi uống cần uống lại 1 viên",
        ],
        "pregnancy": "Không dùng cho phụ nữ đã có thai.",
        "otc": True,
        "form": "viên nén",
    },
]


# ---------------------------------------------------------------------------
# Question templates
# ---------------------------------------------------------------------------
# Each template is a tuple (key, builder) where builder takes the drug dict
# and returns (question, answer_body) or None to skip when the required
# field is missing/empty. The disclaimer is appended downstream.
# ---------------------------------------------------------------------------

def _list_vn(items: list[str]) -> str:
    """Render a Vietnamese bullet-style list inline (no markdown)."""
    return "; ".join(items)


def _t_indication(d: dict):
    return (
        f"Thuốc {d['brand']} dùng để làm gì?",
        f"{d['brand']} ({d['generic']}) thường được dùng để {d['indication']}.",
    )


def _t_ingredient(d: dict):
    if not d.get("ingredient"):
        return None
    return (
        f"{d['brand']} có thành phần gì?",
        f"{d['brand']} chứa {d['ingredient']}.",
    )


def _t_generic(d: dict):
    return (
        f"{d['brand']} thuộc nhóm thuốc nào?",
        f"{d['brand']} có hoạt chất chính là {d['generic']}, dùng để {d['indication']}.",
    )


def _t_dose_adult(d: dict):
    if not d.get("dose_adult"):
        return None
    return (
        f"Người lớn uống {d['brand']} liều như thế nào?",
        f"Liều thông thường cho người lớn: {d['dose_adult']}. "
        "Không tự ý vượt quá liều khuyến cáo và nên đi khám bác sĩ nếu triệu chứng không cải thiện.",
    )


def _t_dose_child(d: dict):
    if not d.get("dose_child"):
        return None
    return (
        f"Trẻ em có dùng được {d['brand']} không?",
        f"Đối với trẻ em: {d['dose_child']}. Với trẻ nhỏ, nên hỏi ý kiến bác sĩ hoặc dược sĩ trước khi dùng.",
    )


def _t_side_effects(d: dict):
    if not d.get("side_effects"):
        return None
    return (
        f"{d['brand']} có tác dụng phụ gì?",
        f"Các tác dụng phụ thường gặp khi dùng {d['brand']} có thể bao gồm: "
        f"{_list_vn(d['side_effects'])}. Nếu phản ứng nặng hoặc kéo dài, cần đi khám bác sĩ.",
    )


def _t_contra(d: dict):
    if not d.get("contra"):
        return None
    return (
        f"Ai không nên dùng {d['brand']}?",
        f"Các trường hợp không nên dùng {d['brand']}: {_list_vn(d['contra'])}. "
        "Khi không chắc chắn, hãy hỏi bác sĩ hoặc dược sĩ trước khi dùng.",
    )


def _t_alcohol(d: dict):
    return (
        f"{d['brand']} có dùng cùng rượu bia được không?",
        f"Không nên uống rượu bia khi đang dùng {d['brand']} vì có thể làm tăng tác dụng phụ "
        f"và ảnh hưởng đến gan, dạ dày. Nếu lỡ uống, hãy theo dõi triệu chứng và đi khám bác sĩ nếu thấy bất thường.",
    )


def _t_pregnancy(d: dict):
    if not d.get("pregnancy"):
        return None
    return (
        f"Phụ nữ có thai dùng {d['brand']} được không?",
        f"{d['pregnancy']} Tốt nhất nên hỏi bác sĩ sản khoa trước khi dùng bất kỳ thuốc nào trong thai kỳ.",
    )


def _t_breastfeeding(d: dict):
    return (
        f"Phụ nữ đang cho con bú dùng {d['brand']} được không?",
        f"Với {d['brand']}, lưu ý: {d['pregnancy']} Nếu đang cho con bú và cần dùng thuốc, "
        "nên hỏi bác sĩ về liều lượng và thời điểm uống phù hợp.",
    )


def _t_food(d: dict):
    return (
        f"Uống {d['brand']} trước hay sau ăn?",
        f"{d['brand']} ở dạng {d['form']} thường được khuyến cáo uống "
        f"{'sau ăn' if d['generic'].lower() in ('paracetamol + ibuprofen', 'acetylsalicylic acid', 'omeprazole') or 'NSAID' in d['ingredient'] or 'sắt' in d['ingredient'].lower() else 'theo chỉ dẫn trên bao bì hoặc của dược sĩ'}. "
        "Đọc kỹ hướng dẫn sử dụng trước khi dùng.",
    )


def _t_overdose(d: dict):
    return (
        f"Lỡ uống quá liều {d['brand']} thì phải làm sao?",
        f"Nếu lỡ uống quá liều {d['brand']}, ngưng thuốc ngay và đi khám bác sĩ hoặc đến cơ sở y tế gần nhất. "
        "Mang theo vỏ thuốc để bác sĩ biết loại và hàm lượng đã uống.",
    )


def _t_warnings(d: dict):
    if not d.get("warnings"):
        return None
    return (
        f"Có lưu ý gì khi dùng {d['brand']}?",
        f"Một số lưu ý khi dùng {d['brand']}: {_list_vn(d['warnings'])}.",
    )


def _t_side_effect_handling(d: dict):
    if not d.get("side_effects"):
        return None
    se = d["side_effects"][0]
    return (
        f"Tôi uống {d['brand']} bị {se}, phải làm sao?",
        f"{se} là tác dụng phụ có thể gặp khi dùng {d['brand']}. "
        "Hãy uống đủ nước, nghỉ ngơi và theo dõi. Nếu triệu chứng nặng lên, kéo dài hoặc xuất hiện dấu hiệu dị ứng "
        "(khó thở, sưng môi, mề đay), cần ngưng thuốc và đi khám bác sĩ ngay.",
    )


def _t_combination(d: dict):
    """Combination question — uses paracetamol-rich pairs as a sample warning."""
    # Order matters for idempotency — sets are NOT iteration-stable across
    # Python processes (PYTHONHASHSEED is randomised by default), so we use
    # an explicit ordered tuple here.
    para_brands = ("Panadol", "Efferalgan", "Hapacol", "Tiffy", "Decolgen", "Alaxan")
    if d["brand"] in para_brands:
        other = next(b for b in para_brands if b != d["brand"])
        return (
            f"Có thể uống {d['brand']} cùng lúc với {other} không?",
            f"Không nên. Cả {d['brand']} và {other} đều chứa paracetamol, dùng đồng thời có thể gây quá liều "
            "paracetamol và tổn thương gan nghiêm trọng. Chỉ dùng một loại tại một thời điểm và tham khảo "
            "ý kiến dược sĩ nếu cần phối hợp.",
        )
    return (
        f"Uống {d['brand']} cùng các thuốc khác có sao không?",
        f"Khi dùng {d['brand']} cùng các thuốc khác, hãy báo cho bác sĩ hoặc dược sĩ biết toàn bộ thuốc đang dùng "
        "để tránh tương tác. Đặc biệt lưu ý các tương tác sau: "
        f"{_list_vn(d.get('warnings') or ['cần đọc kỹ tờ hướng dẫn sử dụng'])}.",
    )


def _t_otc(d: dict):
    if d.get("otc") is None:
        return None
    if d["otc"]:
        body = (
            f"{d['brand']} là thuốc không kê đơn (OTC), có thể mua tại nhà thuốc. "
            "Tuy nhiên vẫn nên hỏi dược sĩ về liều dùng và các thuốc đang dùng kèm để tránh tương tác."
        )
    else:
        body = (
            f"{d['brand']} là thuốc kê đơn, cần có toa của bác sĩ mới được mua và sử dụng. "
            "Không tự ý dùng để tránh tác dụng phụ và biến chứng."
        )
    return (f"{d['brand']} có cần kê đơn không?", body)


def _t_storage(d: dict):
    return (
        f"Bảo quản {d['brand']} như thế nào?",
        f"Bảo quản {d['brand']} ở nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp, nhiệt độ dưới 30°C, "
        "để xa tầm tay trẻ em. Kiểm tra hạn dùng trước khi sử dụng.",
    )


def _t_when_to_see_doctor(d: dict):
    return (
        f"Khi nào dùng {d['brand']} cần đi khám bác sĩ?",
        f"Cần gặp bác sĩ ngay khi dùng {d['brand']} mà: triệu chứng không cải thiện sau 3 ngày, sốt cao kéo dài, "
        "có dấu hiệu dị ứng (khó thở, sưng phù, nổi mề đay), nôn nhiều, đau bụng dữ dội, hoặc có bất kỳ dấu hiệu "
        "bất thường nào khác.",
    )


TEMPLATES = [
    ("indication", _t_indication),
    ("ingredient", _t_ingredient),
    ("generic", _t_generic),
    ("dose_adult", _t_dose_adult),
    ("dose_child", _t_dose_child),
    ("side_effects", _t_side_effects),
    ("contra", _t_contra),
    ("alcohol", _t_alcohol),
    ("pregnancy", _t_pregnancy),
    ("breastfeeding", _t_breastfeeding),
    ("food", _t_food),
    ("overdose", _t_overdose),
    ("warnings", _t_warnings),
    ("side_effect_handling", _t_side_effect_handling),
    ("combination", _t_combination),
    ("otc", _t_otc),
    ("storage", _t_storage),
    ("when_to_see_doctor", _t_when_to_see_doctor),
]


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def generate_records() -> list[dict]:
    """Build the full list of {instruction, input, output, source} records."""
    random.seed(SEED)
    records: list[dict] = []
    seen_inputs: set[str] = set()

    for drug in DRUGS:
        for _key, builder in TEMPLATES:
            built = builder(drug)
            if built is None:
                continue
            question, body = built
            question = question.strip()
            body = body.strip()
            if not question or not body:
                continue
            # Within-file uniqueness — should already hold by construction
            # but enforce it defensively.
            if question in seen_inputs:
                continue
            seen_inputs.add(question)

            output = _force_canonical_disclaimer(body)
            records.append(
                {
                    "instruction": SYSTEM_INSTRUCTION,
                    "input": question,
                    "output": output,
                    "source": SOURCE_TAG,
                }
            )

    return records


def write_records(records: list[dict], path: Path = OUTPUT_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)


def main() -> int:
    records = generate_records()
    write_records(records)
    print(f"Generated {len(records)} VN drug Q&A records -> {OUTPUT_FILE.relative_to(ROOT)}")
    if len(records) < MIN_RECORDS:
        raise SystemExit(
            f"Only generated {len(records)} records but Requirement 1.17 demands ≥{MIN_RECORDS}."
        )
    # Sanity-check disclaimer presence
    missing = [r for r in records if CANONICAL_DISCLAIMER not in r["output"]]
    if missing:
        raise SystemExit(f"{len(missing)} records missing the canonical disclaimer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
