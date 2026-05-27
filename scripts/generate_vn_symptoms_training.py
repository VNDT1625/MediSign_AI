"""
Task 1.9.2 — Generate ≥200 Vietnamese cultural-symptom Q&A training records.

Approach
--------
Hand-curated knowledge base of Vietnamese cultural symptom phrases
(`SYMPTOMS`) — each entry has the Vietnamese phrase, its rough Western
medical equivalent, common causes, self-care advice, and red flags. We
expand each entry through ~14 question templates to comfortably exceed
the ≥200 target required by Requirement 1.18.

Output
------
`data/training_raw/vn_symptoms_culture.json` — list of records:

    {
        "instruction": <SYSTEM_INSTRUCTION>,
        "input":       <Vietnamese question>,
        "output":      <Vietnamese answer ending in CANONICAL_DISCLAIMER>,
        "source":      "vn_symptoms_culture"
    }

Idempotent (`random.seed(42)`).

Usage
-----
    python scripts/generate_vn_symptoms_training.py
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from format_medgemma_dataset import CANONICAL_DISCLAIMER, ensure_disclaimer  # noqa: E402
from prepare_medgemma_data import SYSTEM_INSTRUCTION  # noqa: E402

OUTPUT_FILE = ROOT / "data" / "training_raw" / "vn_symptoms_culture.json"
SOURCE_TAG = "vn_symptoms_culture"
MIN_RECORDS = 200
SEED = 42


def _force_canonical_disclaimer(body: str) -> str:
    """Ensure the literal canonical disclaimer is present at the end.

    Task 1.9 demands the canonical phrase verbatim at the end of every
    output. `ensure_disclaimer` accepts other Vietnamese disclaimer
    variants and may leave the text without the canonical phrase, so we
    force-append it when missing.
    """
    out, _ = ensure_disclaimer(body)
    if CANONICAL_DISCLAIMER not in out:
        out = f"{out.rstrip()}\n\n{CANONICAL_DISCLAIMER}"
    return out


# ---------------------------------------------------------------------------
# Curated knowledge base — 16 Vietnamese cultural symptom descriptions
# ---------------------------------------------------------------------------
# Field reference:
#   phrase:    Vietnamese cultural phrase (input phrase)
#   western:   rough Western medical equivalent
#   causes:    list of common causes (Vietnamese)
#   eat:       list of foods/drinks to favor (Vietnamese)
#   avoid:     list of foods/drinks/behaviors to avoid
#   self_care: list of home-care advice items
#   red_flags: list of warning signs that mean to see a doctor
#   typical_duration: short Vietnamese description of how long it lasts
#   children:  short Vietnamese note about children
# ---------------------------------------------------------------------------
SYMPTOMS: list[dict] = [
    {
        "phrase": "nóng trong người",
        "western": "cảm giác nóng bức trong cơ thể, thường liên quan đến mất nước, ăn uống nhiều đồ cay nóng hoặc rối loạn chuyển hóa nhẹ",
        "causes": [
            "uống ít nước",
            "ăn nhiều đồ cay nóng, chiên rán, đồ ngọt",
            "thức khuya, căng thẳng",
            "thời tiết nóng bức",
            "tác dụng phụ một số thuốc",
        ],
        "eat": [
            "rau xanh (rau má, rau diếp cá, rau ngót)",
            "trái cây mát (dưa hấu, dưa chuột, cam, bưởi)",
            "nước lọc, nước đậu đen, nước bột sắn dây",
            "canh khổ qua, canh rau ngót",
        ],
        "avoid": [
            "đồ cay nóng (ớt, tiêu, gừng nhiều)",
            "đồ chiên rán nhiều dầu",
            "rượu bia, cà phê đặc",
            "thức khuya",
        ],
        "self_care": [
            "uống đủ 1.5–2 lít nước/ngày",
            "ăn nhiều rau xanh và trái cây mát",
            "ngủ đủ giấc trước 23h",
            "tắm nước mát, mặc quần áo thoáng",
        ],
        "red_flags": [
            "sốt cao trên 39°C kéo dài",
            "nổi mẩn đỏ lan rộng kèm ngứa nhiều",
            "tiểu ít, nước tiểu sậm màu",
            "vàng da, vàng mắt",
            "mệt mỏi kéo dài hơn 1 tuần dù đã nghỉ ngơi",
        ],
        "typical_duration": "thường vài ngày đến 1 tuần nếu điều chỉnh ăn uống và sinh hoạt",
        "children": "trẻ em bị nóng trong thường có biểu hiện táo bón, nổi rôm sảy, lưỡi đỏ; cần cho uống đủ nước và ăn rau quả mát",
    },
    {
        "phrase": "gan nóng",
        "western": "cảm giác mệt mỏi, nổi mụn, nước tiểu vàng – trong y học hiện đại có thể liên quan đến rối loạn chức năng gan nhẹ, chế độ ăn nhiều dầu mỡ, hoặc đôi khi không tìm thấy bất thường",
        "causes": [
            "ăn nhiều đồ chiên rán, đồ ngọt",
            "uống nhiều rượu bia",
            "căng thẳng, thức khuya kéo dài",
            "tác dụng phụ một số thuốc",
            "viêm gan virus (cần loại trừ bằng xét nghiệm)",
        ],
        "eat": [
            "rau xanh, trái cây tươi",
            "uống nhiều nước",
            "nước actiso, trà xanh nhạt",
            "đậu xanh, bí đao",
        ],
        "avoid": [
            "rượu bia",
            "đồ chiên rán, mỡ động vật",
            "thức khuya",
            "tự ý uống nhiều thuốc bổ gan không rõ nguồn gốc",
        ],
        "self_care": [
            "ăn uống lành mạnh, hạn chế dầu mỡ",
            "ngủ đủ giấc",
            "vận động nhẹ nhàng 30 phút/ngày",
        ],
        "red_flags": [
            "vàng da, vàng mắt",
            "nước tiểu sậm màu kéo dài",
            "đau hạ sườn phải",
            "buồn nôn, chán ăn kéo dài",
            "sụt cân không rõ nguyên nhân",
        ],
        "typical_duration": "thường cải thiện sau 1–2 tuần khi điều chỉnh chế độ ăn và sinh hoạt",
        "children": "trẻ em ít gặp khái niệm gan nóng theo dân gian; nếu trẻ chán ăn, vàng da cần đi khám bác sĩ ngay",
    },
    {
        "phrase": "phong hàn",
        "western": "thuật ngữ y học cổ truyền chỉ tình trạng nhiễm lạnh – trong y học hiện đại tương ứng với cảm lạnh, cảm cúm thể nhẹ do virus đường hô hấp",
        "causes": [
            "đi mưa, dầm nước lạnh",
            "ngủ máy lạnh nhiệt độ quá thấp",
            "thay đổi thời tiết đột ngột",
            "sức đề kháng yếu",
        ],
        "eat": [
            "cháo gừng, cháo hành tía tô",
            "trà gừng ấm, nước chanh mật ong",
            "súp gà nóng",
            "ăn đồ ấm, dễ tiêu",
        ],
        "avoid": [
            "đồ lạnh, nước đá",
            "tắm nước lạnh",
            "ngồi quạt mạnh hoặc máy lạnh thấp",
            "ra gió lạnh",
        ],
        "self_care": [
            "giữ ấm cơ thể, đặc biệt vùng cổ và lòng bàn chân",
            "uống nước ấm thường xuyên",
            "xông hơi với lá sả, gừng, chanh (người lớn)",
            "nghỉ ngơi, ngủ đủ giấc",
        ],
        "red_flags": [
            "sốt cao trên 39°C không hạ",
            "khó thở, đau ngực",
            "ho ra máu hoặc đờm vàng đặc",
            "đau đầu dữ dội kèm cứng cổ",
            "triệu chứng kéo dài hơn 7 ngày",
        ],
        "typical_duration": "thường 3–7 ngày nếu nghỉ ngơi và chăm sóc tốt",
        "children": "trẻ em bị phong hàn thường sốt nhẹ, ho, sổ mũi; cần giữ ấm, bù nước và đi khám bác sĩ nếu sốt cao hoặc bú kém",
    },
    {
        "phrase": "trúng gió",
        "western": "thuật ngữ dân gian chỉ cảm giác mệt đột ngột, chóng mặt, đau đầu, buồn nôn – trong y học hiện đại có thể là cảm lạnh, hạ huyết áp, hạ đường huyết hoặc thiếu máu não thoáng qua",
        "causes": [
            "thay đổi nhiệt độ đột ngột (từ phòng máy lạnh ra trời nắng)",
            "đi xe máy lâu dưới nắng/gió",
            "tắm khuya, gội đầu rồi ra gió",
            "mệt mỏi, đói, hạ đường huyết",
            "huyết áp thấp",
        ],
        "eat": [
            "cháo gừng, cháo hành",
            "trà gừng, nước chanh ấm",
            "ăn nhẹ khi đói",
        ],
        "avoid": [
            "ra gió lạnh ngay sau khi tắm",
            "thay đổi tư thế đột ngột",
            "nhịn ăn, để cơ thể quá đói",
        ],
        "self_care": [
            "nằm nghỉ nơi thoáng, giữ ấm cơ thể",
            "xoa dầu gió hoặc cạo gió nhẹ ở vùng cổ, lưng (người lớn)",
            "uống nước ấm, ăn nhẹ",
            "đi lại chậm rãi sau khi đỡ",
        ],
        "red_flags": [
            "yếu liệt một bên người, méo miệng, nói khó (dấu hiệu đột quỵ)",
            "mất ý thức, ngất",
            "đau ngực dữ dội",
            "đau đầu dữ dội đột ngột",
            "co giật",
        ],
        "typical_duration": "thường vài giờ đến 1 ngày nếu là trúng gió thông thường",
        "children": "trẻ nhỏ ít dùng khái niệm trúng gió; nếu trẻ đột ngột mệt, nôn, lả người cần đi khám bác sĩ ngay",
    },
    {
        "phrase": "cảm cúm",
        "western": "trong y học hiện đại tương ứng với nhiễm virus đường hô hấp trên (cảm lạnh thông thường) hoặc cúm mùa do virus influenza",
        "causes": [
            "nhiễm virus đường hô hấp",
            "thay đổi thời tiết",
            "sức đề kháng yếu",
            "tiếp xúc với người bệnh",
        ],
        "eat": [
            "cháo hành tía tô, cháo gà",
            "trà gừng mật ong",
            "trái cây giàu vitamin C (cam, chanh, ổi)",
            "uống nhiều nước ấm",
        ],
        "avoid": [
            "đồ lạnh, nước đá",
            "rượu bia",
            "ra gió lạnh",
            "tự ý dùng kháng sinh (cảm cúm do virus, kháng sinh không có tác dụng)",
        ],
        "self_care": [
            "nghỉ ngơi, ngủ đủ giấc",
            "uống nhiều nước",
            "súc miệng nước muối ấm",
            "có thể dùng paracetamol khi sốt và đau (theo liều khuyến cáo)",
        ],
        "red_flags": [
            "sốt cao trên 39°C không hạ sau 3 ngày",
            "khó thở, đau ngực, thở nhanh",
            "ho ra máu hoặc đờm vàng đặc kéo dài",
            "đau đầu dữ dội, cứng cổ",
            "lả người, không ăn uống được",
        ],
        "typical_duration": "thường 5–7 ngày; cúm mùa có thể kéo dài 7–10 ngày",
        "children": "trẻ em cần theo dõi sốt và mức độ ăn uống; sốt cao trên 38.5°C nên dùng hạ sốt đúng liều và đi khám bác sĩ nếu trẻ li bì, bú kém, khó thở",
    },
    {
        "phrase": "đau đầu phong nhiệt",
        "western": "thuật ngữ y học cổ truyền chỉ đau đầu kèm cảm giác nóng – trong y học hiện đại có thể là đau đầu do cảm cúm, viêm xoang, mất ngủ, căng thẳng hoặc tăng huyết áp",
        "causes": [
            "thời tiết nóng, mất nước",
            "thiếu ngủ, căng thẳng",
            "viêm xoang, cảm cúm",
            "tăng huyết áp (cần đo huyết áp để loại trừ)",
        ],
        "eat": [
            "uống đủ nước",
            "ăn nhẹ, đủ chất",
            "trái cây mát (dưa hấu, cam, bưởi)",
        ],
        "avoid": [
            "đồ cay nóng",
            "rượu bia, cà phê đặc",
            "thức khuya",
            "căng thẳng kéo dài",
        ],
        "self_care": [
            "nghỉ ngơi nơi yên tĩnh, mát mẻ",
            "uống nhiều nước",
            "có thể dùng paracetamol khi đau (theo liều khuyến cáo)",
            "chườm mát trán",
        ],
        "red_flags": [
            "đau đầu dữ dội đột ngột (đau như búa bổ)",
            "kèm cứng cổ, sốt cao, nôn nhiều",
            "yếu liệt tay chân, méo miệng, nói khó",
            "co giật, mất ý thức",
            "đau đầu kéo dài hơn 3 ngày không đỡ",
        ],
        "typical_duration": "thường vài giờ đến 2–3 ngày nếu là đau đầu cảm cúm thông thường",
        "children": "trẻ em đau đầu kèm sốt, nôn nhiều cần đi khám bác sĩ ngay để loại trừ viêm màng não",
    },
    {
        "phrase": "lạnh tay chân",
        "western": "cảm giác lạnh ở đầu ngón tay, ngón chân – trong y học hiện đại có thể do tuần hoàn kém, hạ huyết áp, thiếu máu, suy giáp hoặc đơn giản là thời tiết lạnh",
        "causes": [
            "thời tiết lạnh, tuần hoàn ngoại vi kém",
            "huyết áp thấp",
            "thiếu máu (đặc biệt thiếu sắt)",
            "suy giáp",
            "lo âu, căng thẳng",
        ],
        "eat": [
            "ăn đủ chất, đặc biệt thực phẩm giàu sắt (thịt đỏ, gan, rau xanh đậm)",
            "uống đủ nước ấm",
            "trà gừng, súp ấm",
        ],
        "avoid": [
            "ngồi lâu một chỗ",
            "hút thuốc lá (làm co mạch)",
            "tiếp xúc lạnh đột ngột không che chắn",
        ],
        "self_care": [
            "mặc ấm, đi tất khi trời lạnh",
            "ngâm chân nước ấm 10–15 phút trước khi ngủ",
            "tập thể dục nhẹ nhàng để cải thiện tuần hoàn",
            "xoa bóp tay chân",
        ],
        "red_flags": [
            "lạnh kèm tê, đổi màu da (trắng – tím – đỏ) như hội chứng Raynaud",
            "đau dữ dội ở chi",
            "kèm mệt mỏi, da xanh xao, rụng tóc nhiều (nghi thiếu máu/suy giáp)",
            "lạnh kèm phù chân",
        ],
        "typical_duration": "thường giảm ngay khi giữ ấm; nếu kéo dài vài tuần cần đi khám bác sĩ",
        "children": "trẻ em ít bị; nếu trẻ thường xuyên lạnh tay chân kèm chậm lớn, mệt mỏi cần đi khám bác sĩ",
    },
    {
        "phrase": "rôm sảy",
        "western": "phát ban dạng mụn nước nhỏ ở vùng nhiều mồ hôi (cổ, lưng, ngực, trán) do tắc tuyến mồ hôi – thường gặp ở trẻ em vào mùa nóng",
        "causes": [
            "thời tiết nóng ẩm",
            "ra mồ hôi nhiều, vệ sinh chưa kịp",
            "mặc quần áo chật, bí",
            "trẻ em da còn non",
        ],
        "eat": [
            "uống đủ nước",
            "trái cây mát (dưa hấu, cam)",
            "rau xanh",
            "với trẻ em: bù nước qua sữa và trái cây",
        ],
        "avoid": [
            "đồ cay nóng",
            "mặc quần áo chật, không thấm hút",
            "phòng ngột ngạt, không thoáng",
        ],
        "self_care": [
            "tắm bằng nước mát hoặc nước lá tắm (mướp đắng, lá khế, tía tô) cho trẻ",
            "lau khô da sau khi tắm",
            "mặc quần áo cotton thoáng",
            "giữ phòng mát, thoáng",
        ],
        "red_flags": [
            "rôm sảy lan rộng, mụn mủ vàng",
            "trẻ sốt cao kèm phát ban",
            "vùng phát ban sưng đỏ, đau, có dịch",
            "không đỡ sau 1 tuần chăm sóc tại nhà",
        ],
        "typical_duration": "thường 3–7 ngày nếu giữ vệ sinh và làm mát da đúng cách",
        "children": "trẻ sơ sinh và trẻ nhỏ rất dễ bị rôm sảy; cha mẹ cần lau mồ hôi thường xuyên, mặc đồ thoáng và không bôi phấn rôm dày đặc",
    },
    {
        "phrase": "nhiệt miệng",
        "western": "vết loét nhỏ, đau ở niêm mạc miệng (loét aphthous) – nguyên nhân thường lành tính, liên quan đến stress, thiếu vitamin, cắn vào niêm mạc",
        "causes": [
            "stress, thức khuya",
            "thiếu vitamin nhóm B, vitamin C, sắt, kẽm",
            "ăn nhiều đồ cay nóng",
            "vô tình cắn vào niêm mạc miệng",
            "rối loạn nội tiết (kinh nguyệt)",
        ],
        "eat": [
            "rau xanh, trái cây giàu vitamin C",
            "thực phẩm giàu vitamin nhóm B (trứng, cá, ngũ cốc nguyên hạt)",
            "sữa chua, đồ mềm dễ ăn",
            "uống nhiều nước",
        ],
        "avoid": [
            "đồ cay, nóng, chua",
            "đồ cứng, sắc gây tổn thương thêm",
            "rượu bia, cà phê",
        ],
        "self_care": [
            "súc miệng nước muối loãng 2–3 lần/ngày",
            "có thể bôi gel chuyên dùng cho nhiệt miệng (kamistad, oracortia) theo hướng dẫn dược sĩ",
            "ngủ đủ giấc, giảm stress",
            "bổ sung vitamin nhóm B nếu cần",
        ],
        "red_flags": [
            "vết loét lớn (>1cm), đau dữ dội",
            "không lành sau 2–3 tuần",
            "kèm sốt cao, hạch cổ",
            "tái phát thường xuyên (nhiều lần trong năm)",
            "loét ở vùng amidan, lưỡi gốc kèm sụt cân",
        ],
        "typical_duration": "thường tự lành sau 7–10 ngày",
        "children": "trẻ em bị nhiệt miệng thường biếng ăn, quấy khóc; cha mẹ cho ăn đồ mềm, mát, súc miệng nước muối và đi khám nếu loét nặng hoặc tái phát",
    },
    {
        "phrase": "ho có đờm",
        "western": "ho kèm tiết đờm – thường do nhiễm trùng đường hô hấp, viêm phế quản, viêm phổi nhẹ; cũng có thể do dị ứng hoặc kích ứng",
        "causes": [
            "cảm cúm, viêm họng, viêm phế quản",
            "viêm xoang chảy dịch xuống họng",
            "dị ứng, ô nhiễm không khí",
            "hút thuốc lá",
            "trào ngược dạ dày",
        ],
        "eat": [
            "uống nhiều nước ấm",
            "cháo hành tía tô, cháo gà",
            "mật ong pha nước ấm (người lớn và trẻ trên 1 tuổi)",
            "trà gừng",
        ],
        "avoid": [
            "đồ lạnh, nước đá",
            "thuốc lá, khói bụi",
            "đồ chiên rán nhiều dầu",
            "nằm ngay sau khi ăn",
        ],
        "self_care": [
            "uống nhiều nước ấm để loãng đờm",
            "súc miệng nước muối ấm",
            "xông hơi với tinh dầu khuynh diệp/sả (người lớn)",
            "có thể dùng siro long đờm theo hướng dẫn dược sĩ",
        ],
        "red_flags": [
            "ho ra máu",
            "đờm vàng đặc, xanh kéo dài",
            "khó thở, đau ngực, thở nhanh",
            "sốt cao trên 39°C",
            "ho kéo dài hơn 2 tuần",
            "sụt cân không rõ nguyên nhân",
        ],
        "typical_duration": "thường 7–10 ngày; nếu kéo dài hơn 2 tuần cần đi khám bác sĩ",
        "children": "trẻ dưới 1 tuổi không dùng mật ong; trẻ ho kèm khó thở, thở rít, bú kém cần đi khám bác sĩ ngay",
    },
    {
        "phrase": "khó tiêu đầy hơi",
        "western": "cảm giác đầy bụng, ợ hơi, khó chịu sau ăn – có thể do ăn quá nhanh, ăn nhiều dầu mỡ, hội chứng ruột kích thích, viêm dạ dày hoặc dị ứng thức ăn",
        "causes": [
            "ăn quá nhanh, ăn quá no",
            "ăn nhiều đồ chiên rán, dầu mỡ",
            "uống nước có gas",
            "stress, lo âu",
            "viêm dạ dày, trào ngược",
        ],
        "eat": [
            "ăn chậm, nhai kỹ",
            "thực phẩm dễ tiêu (cháo, súp, rau luộc)",
            "sữa chua không đường (probiotic)",
            "trà gừng, trà bạc hà",
        ],
        "avoid": [
            "đồ chiên rán, đồ ngọt nhiều",
            "nước có gas",
            "rượu bia, cà phê",
            "ăn quá no trước khi ngủ",
        ],
        "self_care": [
            "ăn chia nhỏ thành 4–5 bữa/ngày",
            "đi bộ nhẹ 10–15 phút sau ăn",
            "massage bụng theo chiều kim đồng hồ",
            "có thể dùng men tiêu hóa, simethicone (giảm hơi) theo hướng dẫn dược sĩ",
        ],
        "red_flags": [
            "đau bụng dữ dội, đau quặn không đỡ",
            "nôn ra máu hoặc đi ngoài phân đen",
            "sụt cân không rõ nguyên nhân",
            "khó nuốt, nuốt nghẹn",
            "đầy hơi kéo dài hơn 2 tuần không đỡ",
        ],
        "typical_duration": "thường vài giờ đến 1–2 ngày nếu điều chỉnh ăn uống",
        "children": "trẻ em đầy hơi thường do nuốt nhiều khí khi bú/ăn; cha mẹ vỗ ợ hơi sau khi bú và đi khám nếu trẻ nôn nhiều, bú kém",
    },
    {
        "phrase": "mất ngủ",
        "western": "khó vào giấc, ngủ chập chờn hoặc thức giấc sớm – có thể do stress, lo âu, lạm dụng cà phê, rối loạn giấc ngủ hoặc bệnh lý nội khoa",
        "causes": [
            "stress, lo âu, trầm cảm",
            "uống cà phê, trà đặc gần giờ ngủ",
            "sử dụng điện thoại, máy tính trước khi ngủ",
            "đau mạn tính, trào ngược, tiểu đêm",
            "rối loạn nội tiết (mãn kinh, cường giáp)",
        ],
        "eat": [
            "sữa ấm trước khi ngủ",
            "chuối, hạt sen, các loại hạt",
            "trà hoa cúc, trà tâm sen",
        ],
        "avoid": [
            "cà phê, trà đặc, nước có gas sau 14h",
            "ăn quá no hoặc uống nhiều nước trước ngủ",
            "dùng điện thoại trên giường",
            "rượu bia (gây ngủ nông)",
        ],
        "self_care": [
            "đi ngủ và thức dậy đúng giờ mỗi ngày",
            "phòng ngủ tối, yên tĩnh, mát mẻ",
            "thư giãn 30 phút trước ngủ (đọc sách, thiền, hít thở sâu)",
            "tập thể dục đều đặn nhưng không tập sát giờ ngủ",
        ],
        "red_flags": [
            "mất ngủ kéo dài hơn 1 tháng",
            "kèm cảm giác buồn chán, mất hứng thú, ý nghĩ tiêu cực (cần khám tâm thần)",
            "kèm khó thở khi ngủ, ngáy to và ngưng thở",
            "kèm tim đập nhanh, sụt cân (nghi cường giáp)",
        ],
        "typical_duration": "mất ngủ cấp tính thường vài ngày đến vài tuần; mạn tính cần đi khám bác sĩ",
        "children": "trẻ em mất ngủ thường do thay đổi sinh hoạt, lo lắng đi học, dùng điện thoại nhiều; cha mẹ cần lập thói quen ngủ và đi khám nếu kéo dài",
    },
    {
        "phrase": "đau bụng kinh",
        "western": "đau vùng bụng dưới trong kỳ kinh nguyệt do co thắt tử cung – đa số là đau bụng kinh nguyên phát (lành tính), một số ít liên quan đến lạc nội mạc tử cung, u xơ tử cung",
        "causes": [
            "co thắt tử cung do prostaglandin",
            "lạc nội mạc tử cung",
            "u xơ tử cung",
            "viêm vùng chậu",
        ],
        "eat": [
            "uống nước ấm",
            "trà gừng, trà hoa cúc",
            "thực phẩm giàu sắt (thịt đỏ, rau xanh đậm)",
            "chuối, socola đen",
        ],
        "avoid": [
            "đồ lạnh, nước đá",
            "cà phê, rượu bia",
            "đồ ăn quá mặn",
            "vận động mạnh khi đau",
        ],
        "self_care": [
            "chườm ấm bụng dưới",
            "nghỉ ngơi, nằm nghiêng co đầu gối",
            "có thể dùng paracetamol hoặc ibuprofen, hyoscine butylbromide (Buscopan) theo liều khuyến cáo",
            "tập yoga nhẹ, hít thở sâu",
        ],
        "red_flags": [
            "đau bụng dữ dội bất thường, không giảm với thuốc giảm đau",
            "kinh nguyệt kéo dài hơn 7 ngày hoặc lượng quá nhiều",
            "đau ngoài kỳ kinh, đau khi quan hệ",
            "sốt cao kèm đau bụng",
            "trễ kinh kèm đau dữ dội (nghi thai ngoài tử cung)",
        ],
        "typical_duration": "thường 1–3 ngày đầu kỳ kinh; nếu đau dữ dội kéo dài cần đi khám bác sĩ phụ khoa",
        "children": "bé gái mới có kinh thường đau bụng kinh; nếu đau dữ dội ảnh hưởng học tập cần đi khám bác sĩ",
    },
    {
        "phrase": "tiêu chảy",
        "western": "đi ngoài phân lỏng nhiều lần – nguyên nhân thường gặp là nhiễm virus/vi khuẩn đường ruột, ngộ độc thực phẩm, dị ứng thức ăn",
        "causes": [
            "nhiễm virus đường ruột (rotavirus, norovirus)",
            "nhiễm vi khuẩn (E. coli, Salmonella, lỵ)",
            "ngộ độc thực phẩm",
            "dị ứng/không dung nạp thức ăn (lactose)",
            "tác dụng phụ kháng sinh",
        ],
        "eat": [
            "Oresol pha đúng tỉ lệ để bù nước",
            "cháo trắng, súp, chuối, cơm",
            "sữa chua không đường (probiotic)",
            "uống nhiều nước",
        ],
        "avoid": [
            "đồ sống, gỏi, đồ tái",
            "sữa tươi, đồ ngọt nhiều",
            "đồ chiên rán",
            "rượu bia, cà phê",
        ],
        "self_care": [
            "uống Oresol sau mỗi lần đi ngoài",
            "ăn nhẹ, dễ tiêu",
            "có thể dùng diosmectite (Smecta), men vi sinh theo hướng dẫn",
            "nghỉ ngơi, theo dõi số lần đi ngoài",
        ],
        "red_flags": [
            "đi ngoài có máu, phân đen",
            "sốt cao trên 39°C",
            "mất nước nặng (mắt trũng, tiểu ít, da khô)",
            "tiêu chảy nhiều hơn 6 lần/ngày, kéo dài hơn 2 ngày",
            "trẻ nhỏ li bì, không bú được, không uống được",
        ],
        "typical_duration": "thường 1–3 ngày với tiêu chảy do virus; cần đi khám bác sĩ nếu kéo dài hoặc có dấu hiệu nặng",
        "children": "trẻ em tiêu chảy rất dễ mất nước; cha mẹ phải bù Oresol đúng cách và đi khám bác sĩ ngay khi có dấu hiệu mất nước",
    },
    {
        "phrase": "táo bón",
        "western": "đi ngoài ít hơn 3 lần/tuần, phân khô cứng, khó đi – thường do chế độ ăn ít chất xơ, uống ít nước, ít vận động; đôi khi do bệnh lý",
        "causes": [
            "ăn ít rau xanh, trái cây",
            "uống ít nước",
            "ít vận động",
            "stress, thay đổi sinh hoạt",
            "tác dụng phụ một số thuốc (giảm đau opioid, sắt, calci)",
            "bệnh lý: suy giáp, đại tràng",
        ],
        "eat": [
            "rau xanh (mồng tơi, rau lang, rau dền)",
            "trái cây giàu chất xơ (đu đủ, chuối chín, lê, mận)",
            "uống đủ 1.5–2 lít nước/ngày",
            "ngũ cốc nguyên hạt, các loại đậu",
            "sữa chua",
        ],
        "avoid": [
            "đồ ăn nhanh, ít chất xơ",
            "uống ít nước",
            "ngồi lâu một chỗ",
            "lạm dụng thuốc nhuận tràng",
        ],
        "self_care": [
            "ăn nhiều rau xanh, trái cây",
            "uống đủ nước",
            "đi bộ, vận động 30 phút/ngày",
            "tập thói quen đi vệ sinh đúng giờ",
        ],
        "red_flags": [
            "đi ngoài ra máu, phân đen",
            "đau bụng dữ dội kèm không đi được",
            "sụt cân không rõ nguyên nhân",
            "táo bón mới xuất hiện ở người trên 50 tuổi",
            "táo bón xen kẽ tiêu chảy kéo dài",
        ],
        "typical_duration": "thường cải thiện sau vài ngày khi điều chỉnh chế độ ăn và sinh hoạt",
        "children": "trẻ em táo bón thường do uống ít nước, ăn ít rau; cha mẹ tăng chất xơ, nước và đi khám nếu trẻ đau bụng nhiều, đi ngoài ra máu",
    },
    {
        "phrase": "say nắng",
        "western": "tổn thương do tiếp xúc nhiệt độ cao kéo dài – từ kiệt sức do nhiệt (heat exhaustion) đến sốc nhiệt (heat stroke) – cần xử trí cấp cứu",
        "causes": [
            "làm việc, đi lại dưới nắng nóng kéo dài",
            "uống không đủ nước khi trời nóng",
            "vận động mạnh trong môi trường nóng",
            "trẻ em và người già nhạy cảm hơn",
        ],
        "eat": [
            "uống nhiều nước, Oresol bù điện giải",
            "trái cây mát (dưa hấu, cam, dừa)",
            "đồ ăn dễ tiêu, mát",
        ],
        "avoid": [
            "ra nắng giờ cao điểm (10h–15h)",
            "rượu bia, cà phê (lợi tiểu, mất nước thêm)",
            "vận động mạnh giữa trời nắng",
        ],
        "self_care": [
            "đưa người bệnh vào nơi mát, thoáng",
            "cởi bớt quần áo, lau người bằng nước mát",
            "cho uống nước, Oresol từng ngụm nhỏ",
            "nghỉ ngơi và theo dõi",
        ],
        "red_flags": [
            "thân nhiệt trên 40°C",
            "mất ý thức, lú lẫn, co giật",
            "ngừng đổ mồ hôi dù trời nóng (dấu hiệu sốc nhiệt – cần đi khám bác sĩ ngay)",
            "nôn nhiều, không uống được",
            "đau ngực, khó thở",
        ],
        "typical_duration": "kiệt sức nhẹ thường hồi phục sau vài giờ nghỉ ngơi và bù nước; sốc nhiệt là cấp cứu cần đi khám bác sĩ ngay",
        "children": "trẻ em rất dễ say nắng; cần đội mũ, mặc đồ thoáng, uống nước thường xuyên, không cho chơi giữa trưa nắng",
    },
]


# ---------------------------------------------------------------------------
# Question templates
# ---------------------------------------------------------------------------

def _list_vn(items: list[str]) -> str:
    return "; ".join(items)


def _t_definition(s: dict):
    return (
        f"\"{s['phrase']}\" là gì?",
        f"\"{s['phrase']}\" là cách nói trong văn hóa Việt Nam, {s['western']}.",
    )


def _t_western_equivalent(s: dict):
    return (
        f"\"{s['phrase']}\" trong y học hiện đại là bệnh gì?",
        f"\"{s['phrase']}\" theo y học hiện đại {s['western']}. Để chẩn đoán chính xác cần đi khám bác sĩ.",
    )


def _t_causes(s: dict):
    if not s.get("causes"):
        return None
    return (
        f"\"{s['phrase']}\" do nguyên nhân nào gây ra?",
        f"Các nguyên nhân thường gặp gây {s['phrase']}: {_list_vn(s['causes'])}.",
    )


def _t_eat(s: dict):
    if not s.get("eat"):
        return None
    return (
        f"Bị \"{s['phrase']}\" nên ăn gì?",
        f"Khi bị {s['phrase']}, nên ăn/uống: {_list_vn(s['eat'])}. Kết hợp nghỉ ngơi và theo dõi triệu chứng.",
    )


def _t_avoid(s: dict):
    if not s.get("avoid"):
        return None
    return (
        f"Bị \"{s['phrase']}\" nên kiêng gì?",
        f"Khi bị {s['phrase']}, nên kiêng: {_list_vn(s['avoid'])}.",
    )


def _t_duration(s: dict):
    if not s.get("typical_duration"):
        return None
    return (
        f"\"{s['phrase']}\" bao lâu thì khỏi?",
        f"{s['phrase'].capitalize()} {s['typical_duration']}. Nếu kéo dài hơn dự kiến hoặc nặng lên, cần đi khám bác sĩ.",
    )


def _t_dangerous(s: dict):
    return (
        f"\"{s['phrase']}\" có nguy hiểm không?",
        f"Đa số trường hợp {s['phrase']} là tình trạng nhẹ, có thể tự khỏi với chăm sóc tại nhà. "
        "Tuy nhiên cần cảnh giác với các dấu hiệu nặng và đi khám bác sĩ nếu có dấu hiệu bất thường.",
    )


def _t_red_flags(s: dict):
    if not s.get("red_flags"):
        return None
    return (
        f"Khi nào bị \"{s['phrase']}\" cần đi khám bác sĩ?",
        f"Cần gặp bác sĩ ngay khi bị {s['phrase']} kèm các dấu hiệu sau: {_list_vn(s['red_flags'])}.",
    )


def _t_western_meds(s: dict):
    return (
        f"Bị \"{s['phrase']}\" có nên uống thuốc tây không?",
        f"Với {s['phrase']}, không nên tự ý uống nhiều loại thuốc tây. "
        "Có thể dùng các thuốc không kê đơn phù hợp với triệu chứng (ví dụ paracetamol khi sốt, đau) "
        "theo đúng liều khuyến cáo. Nếu triệu chứng nặng hoặc kéo dài, cần đi khám bác sĩ để được kê đơn phù hợp.",
    )


def _t_home_remedy(s: dict):
    if not s.get("self_care"):
        return None
    return (
        f"Mẹo chữa \"{s['phrase']}\" tại nhà?",
        f"Một số biện pháp chăm sóc tại nhà cho {s['phrase']}: {_list_vn(s['self_care'])}. "
        "Nếu sau 2–3 ngày không cải thiện, cần đi khám bác sĩ.",
    )


def _t_children(s: dict):
    if not s.get("children"):
        return None
    return (
        f"Trẻ nhỏ bị \"{s['phrase']}\" chữa thế nào?",
        f"Đối với trẻ nhỏ bị {s['phrase']}: {s['children']}.",
    )


def _t_elderly(s: dict):
    return (
        f"Người lớn tuổi bị \"{s['phrase']}\" cần lưu ý gì?",
        f"Người lớn tuổi bị {s['phrase']} thường nhạy cảm hơn và có thể có nhiều bệnh nền. "
        f"Cần theo dõi sát các dấu hiệu nặng: {_list_vn(s.get('red_flags') or ['nếu thấy mệt nhiều cần đi khám bác sĩ'])}. "
        "Nếu đang dùng nhiều thuốc, hãy hỏi bác sĩ trước khi dùng thêm thuốc khác.",
    )


def _t_pregnancy(s: dict):
    return (
        f"Phụ nữ có thai bị \"{s['phrase']}\" thì sao?",
        f"Phụ nữ có thai bị {s['phrase']} cần thận trọng hơn vì nhiều thuốc có thể ảnh hưởng đến thai nhi. "
        "Nên ưu tiên các biện pháp không dùng thuốc (nghỉ ngơi, ăn uống điều độ) và đi khám bác sĩ "
        "trước khi dùng bất kỳ thuốc nào.",
    )


def _t_prevention(s: dict):
    parts: list[str] = []
    if s.get("avoid"):
        parts.append("hạn chế: " + _list_vn(s["avoid"]))
    if s.get("self_care"):
        parts.append("duy trì thói quen tốt: " + _list_vn(s["self_care"]))
    body = (
        f"Để phòng ngừa {s['phrase']}, hãy "
        + "; ".join(parts)
        + "."
    )
    return (f"Làm thế nào để phòng tránh \"{s['phrase']}\"?", body)


TEMPLATES = [
    ("definition", _t_definition),
    ("western", _t_western_equivalent),
    ("causes", _t_causes),
    ("eat", _t_eat),
    ("avoid", _t_avoid),
    ("duration", _t_duration),
    ("dangerous", _t_dangerous),
    ("red_flags", _t_red_flags),
    ("western_meds", _t_western_meds),
    ("home_remedy", _t_home_remedy),
    ("children", _t_children),
    ("elderly", _t_elderly),
    ("pregnancy", _t_pregnancy),
    ("prevention", _t_prevention),
]


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def generate_records() -> list[dict]:
    random.seed(SEED)
    records: list[dict] = []
    seen_inputs: set[str] = set()

    for symptom in SYMPTOMS:
        for _key, builder in TEMPLATES:
            built = builder(symptom)
            if built is None:
                continue
            question, body = built
            question = question.strip()
            body = body.strip()
            if not question or not body:
                continue
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
    print(f"Generated {len(records)} VN cultural-symptom Q&A records -> {OUTPUT_FILE.relative_to(ROOT)}")
    if len(records) < MIN_RECORDS:
        raise SystemExit(
            f"Only generated {len(records)} records but Requirement 1.18 demands ≥{MIN_RECORDS}."
        )
    missing = [r for r in records if CANONICAL_DISCLAIMER not in r["output"]]
    if missing:
        raise SystemExit(f"{len(missing)} records missing the canonical disclaimer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
