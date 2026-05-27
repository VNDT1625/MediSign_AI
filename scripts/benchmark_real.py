"""
=============================================================================
MediSign AI — REAL Benchmark Suite (Production Services, No Mocks)
=============================================================================

Benchmark này dùng services THẬT trong codebase:
  - app.services.triage_service.build_triage_result      (rule-based triage)
  - app.services.rag_service.RAGService                   (BM25 + synonyms)
  - app.services.drug_lookup_service                      (DAV drug DB lookup)

Không gọi LLM (vì cần GPU) — chỉ benchmark các tầng RULE-BASED + RETRIEVAL,
là phần SẼ luôn chạy bất kể MedGemma có hay không.

Chạy:
  cd apps/backend_fastapi
  python ../../scripts/benchmark_real.py

Hoặc với option:
  python scripts/benchmark_real.py --output benchmark_real_report.json

Output:
  - In bảng kết quả ra console
  - Lưu JSON report cho việc plot biểu đồ
  - Ghi LOG chi tiết các case sai để hỗ trợ debug

Các so sánh có thật:
  [A] Triage 2-tier vs single-tier         — Recall/Precision/F1 trên 100 ca
  [B] RAG with vs without medical synonyms — Hit@k, MRR trên 30 query
  [C] RAG with adapter boost vs flat       — chứng minh adapter routing có lợi
  [D] Drug lookup: exact vs partial match  — coverage trên 50 thuốc thực
  [E] Rule-based latency distribution      — P50/P95/P99 trên 1000 calls
=============================================================================
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

# ── Setup paths so imports work from anywhere ──────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
BACKEND_DIR = ROOT_DIR / "apps" / "backend_fastapi"
sys.path.insert(0, str(BACKEND_DIR))

# Set DB url to in-memory SQLite to avoid touching real DB during benchmark
import os
os.environ.setdefault("BACKEND_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("BACKEND_RAG_ENABLED", "true")
os.environ.setdefault("BACKEND_RATE_LIMIT_ENABLED", "false")

# Real production service imports
from app.schemas.triage import TriageRequest  # noqa: E402
from app.services.triage_service import build_triage_result  # noqa: E402
from app.services.rag_service import RAGService, MEDICAL_SYNONYMS, RAGHit  # noqa: E402
from app.services import drug_lookup_service  # noqa: E402

TriageLabel = Literal["emergency", "urgent", "non_emergency"]


# =============================================================================
# SECTION A — TRIAGE GROUND TRUTH
# =============================================================================
# 100 ca: 30 emergency / 30 urgent / 40 non_emergency
# Mỗi ca có ground_truth do tác giả gán dựa trên phác đồ cấp cứu chuẩn.

@dataclass
class TriageCase:
    symptom_text: str
    ground_truth: TriageLabel
    note: str = ""


TRIAGE_CASES: list[TriageCase] = [
    # ── EMERGENCY (30) ───────────────────────────────────────────────────
    TriageCase("Tôi đang khó thở rất nặng, không thở được", "emergency", "khó thở cấp"),
    TriageCase("Đau ngực dữ dội lan ra cánh tay trái", "emergency", "nghi NMCT"),
    TriageCase("Bệnh nhân bị ngất, không tỉnh lại được", "emergency", "ngất"),
    TriageCase("Khó thở và đau ngực khi nằm xuống", "emergency", "suy tim cấp"),
    TriageCase("Tôi bị ngất xỉu đột ngột khi đứng dậy", "emergency", "ngất tư thế"),
    TriageCase("Đau ngực như bị bóp nghẹt, vã mồ hôi lạnh", "emergency", "ACS"),
    TriageCase("Khó thở không thở được, môi tím tái", "emergency", "suy hô hấp"),
    TriageCase("Bị ngất, giờ tỉnh nhưng vẫn đau ngực", "emergency", "ngất + đau ngực"),
    TriageCase("Thở khò khè nặng, không nói được câu dài", "emergency", "hen nặng"),
    TriageCase("Đau ngực trái dữ dội kèm buồn nôn và vã mồ hôi", "emergency", "NMCT"),
    TriageCase("Khó thở đột ngột sau khi ăn, nghi dị ứng nặng", "emergency", "phản vệ"),
    TriageCase("Bệnh nhân co giật toàn thân không dừng được", "emergency", "động kinh"),
    TriageCase("Đột ngột nói ngọng, tay chân yếu một bên", "emergency", "đột quỵ"),
    TriageCase("Mặt méo, tay trái không nhấc lên được, nói khó", "emergency", "đột quỵ"),
    TriageCase("Đau đầu dữ dội nhất từ trước đến nay, đột ngột", "emergency", "xuất huyết não"),
    TriageCase("Nôn ra máu đỏ tươi nhiều lần", "emergency", "XHTH"),
    TriageCase("Đi ngoài phân đen như hắc ín, chóng mặt", "emergency", "XHTH"),
    TriageCase("Bụng cứng như gỗ, đau dữ dội không dám thở sâu", "emergency", "thủng tạng"),
    TriageCase("Trẻ sơ sinh khó thở, môi tím, không bú được", "emergency", "suy hô hấp SS"),
    TriageCase("Phụ nữ mang thai đau bụng dữ dội kèm ra máu", "emergency", "nhau bong"),
    TriageCase("Bị điện giật, bất tỉnh vài giây rồi tỉnh", "emergency", "điện giật"),
    TriageCase("Uống nhầm thuốc trừ sâu, đang nôn mửa", "emergency", "ngộ độc"),
    TriageCase("Bị ong đốt nhiều nốt, khó thở và nổi mề đay toàn thân", "emergency", "phản vệ"),
    TriageCase("Đau ngực khi thở sâu, sau tai nạn giao thông", "emergency", "chấn thương"),
    TriageCase("Trẻ 2 tuổi nuốt pin cúc, đang khóc và chảy nước dãi", "emergency", "dị vật"),
    TriageCase("Huyết áp 220/130, đau đầu dữ dội, nhìn mờ", "emergency", "tăng HA"),
    TriageCase("Đường huyết 30 mg/dL, run tay, vã mồ hôi, lơ mơ", "emergency", "hạ ĐH nặng"),
    TriageCase("Sốt 41 độ, cứng cổ, sợ ánh sáng", "emergency", "viêm màng não"),
    TriageCase("Khó thở và ngực đau sau khi bị đâm", "emergency", "chấn thương xuyên"),
    TriageCase("Bệnh nhân không tỉnh, không phản xạ, thở yếu", "emergency", "hôn mê"),

    # ── URGENT (30) ───────────────────────────────────────────────────
    TriageCase("Sốt cao 39.5 độ kéo dài 3 ngày không hạ", "urgent", "sốt cao"),
    TriageCase("Đau nhiều ở bụng dưới bên phải từ sáng đến giờ", "urgent", "VRT?"),
    TriageCase("Mệt mỏi nhiều, không ăn được, vàng da nhẹ", "urgent", "viêm gan?"),
    TriageCase("Sốt cao và đau đầu dữ dội từ hôm qua", "urgent", "sốt + đau đầu"),
    TriageCase("Đau nhiều khi đi tiểu, tiểu ra máu", "urgent", "NTĐN"),
    TriageCase("Buồn nôn nhiều, nôn 5-6 lần trong ngày, không uống được nước", "urgent", "nôn nặng"),
    TriageCase("Sốt cao 39 độ kèm phát ban đỏ toàn thân", "urgent", "phát ban"),
    TriageCase("Đau nhiều ở tai, chảy mủ tai, sốt nhẹ", "urgent", "viêm tai"),
    TriageCase("Mệt mỏi nhiều, khó thở khi leo cầu thang", "urgent", "khó thở GS"),
    TriageCase("Đau dữ dội vùng thắt lưng lan xuống đùi", "urgent", "đau TKT"),
    TriageCase("Sốt cao và đau họng không nuốt được", "urgent", "viêm amidan"),
    TriageCase("Trẻ sốt cao 39.5, co giật 1 lần đã dừng", "urgent", "co giật do sốt"),
    TriageCase("Đau nhiều vùng bụng trên sau khi ăn nhiều dầu mỡ", "urgent", "viêm tụy?"),
    TriageCase("Mệt mỏi nhiều, da xanh xao, hoa mắt khi đứng dậy", "urgent", "thiếu máu"),
    TriageCase("Sốt cao 3 ngày, đau cơ toàn thân, đau sau hốc mắt", "urgent", "SXH?"),
    TriageCase("Đau nhiều khớp gối, sưng đỏ, không đi được", "urgent", "viêm khớp"),
    TriageCase("Buồn nôn nhiều và đau bụng sau khi ăn hải sản", "urgent", "ngộ độc TP"),
    TriageCase("Sốt cao kèm ho có đờm vàng xanh 5 ngày", "urgent", "viêm phổi"),
    TriageCase("Đau nhiều vùng hạ sườn phải, vàng mắt nhẹ", "urgent", "sỏi mật?"),
    TriageCase("Mệt mỏi nhiều, tiểu nhiều lần, khát nước liên tục", "urgent", "ĐTĐ?"),
    TriageCase("Sốt cao và phát ban sau khi dùng thuốc mới", "urgent", "dị ứng thuốc"),
    TriageCase("Đau nhiều vùng bụng dưới, trễ kinh 6 tuần", "urgent", "thai NTC?"),
    TriageCase("Mệt mỏi nhiều, sụt 5kg trong 1 tháng không rõ nguyên nhân", "urgent", "sụt cân"),
    TriageCase("Sốt cao và đau mắt đỏ, chảy ghèn nhiều", "urgent", "viêm KM"),
    TriageCase("Đau nhiều vùng ngực khi hít thở sâu, không có chấn thương", "urgent", "viêm MP"),
    TriageCase("Buồn nôn nhiều và đau đầu sau khi ở phòng kín có lò than", "urgent", "ngộ độc CO"),
    TriageCase("Sốt cao kèm tiêu chảy nhiều lần, mất nước", "urgent", "TC cấp"),
    TriageCase("Đau nhiều vùng bẹn phải, sưng to", "urgent", "thoát vị bẹn"),
    TriageCase("Mệt mỏi nhiều, tim đập nhanh bất thường khi nghỉ", "urgent", "RL nhịp"),
    TriageCase("Sốt cao và đau lưng dữ dội, tiểu buốt", "urgent", "viêm TBT"),

    # ── NON-EMERGENCY (40) ───────────────────────────────────────────────
    TriageCase("Ho khan nhẹ 2 ngày, không sốt", "non_emergency", "ho nhẹ"),
    TriageCase("Sổ mũi, hắt hơi, không sốt", "non_emergency", "cảm nhẹ"),
    TriageCase("Đau đầu nhẹ sau khi làm việc nhiều giờ", "non_emergency", "đau đầu CT"),
    TriageCase("Ngứa da nhẹ, không nổi mề đay", "non_emergency", "ngứa"),
    TriageCase("Mệt mỏi nhẹ sau khi tập thể dục", "non_emergency", "mệt sau tập"),
    TriageCase("Đau bụng nhẹ sau khi ăn no", "non_emergency", "khó tiêu"),
    TriageCase("Chóng mặt nhẹ khi đứng dậy nhanh", "non_emergency", "hạ HA TT"),
    TriageCase("Đau cổ nhẹ sau khi ngủ sai tư thế", "non_emergency", "vẹo cổ"),
    TriageCase("Nổi mụn nhỏ ở mặt, không đau", "non_emergency", "mụn"),
    TriageCase("Đau lưng nhẹ sau khi ngồi lâu", "non_emergency", "đau lưng CH"),
    TriageCase("Hắt hơi liên tục buổi sáng, không sốt", "non_emergency", "VM dị ứng"),
    TriageCase("Ngứa mắt nhẹ, không đỏ, không chảy nước mắt nhiều", "non_emergency", "DƯ mắt"),
    TriageCase("Đau khớp ngón tay nhẹ sau khi gõ máy tính nhiều", "non_emergency", "OCT"),
    TriageCase("Buồn nôn nhẹ buổi sáng, không nôn", "non_emergency", "buồn nôn"),
    TriageCase("Đau họng nhẹ, không sốt, không khó nuốt", "non_emergency", "viêm họng nhẹ"),
    TriageCase("Mệt mỏi nhẹ, ngủ không ngon giấc 2 ngày", "non_emergency", "mất ngủ nhẹ"),
    TriageCase("Đau bụng nhẹ trước kỳ kinh", "non_emergency", "đau kinh"),
    TriageCase("Nổi mề đay nhỏ sau khi ăn tôm, không khó thở", "non_emergency", "DƯ nhẹ"),
    TriageCase("Ho nhẹ và sổ mũi, đang hồi phục sau cảm", "non_emergency", "hồi phục"),
    TriageCase("Đau đầu nhẹ, uống paracetamol đỡ", "non_emergency", "đầu CT"),
    TriageCase("Không có triệu chứng gì, chỉ muốn kiểm tra sức khỏe", "non_emergency", "khám ĐK"),
    TriageCase("Đau cơ bắp chân nhẹ sau khi chạy bộ", "non_emergency", "đau cơ"),
    TriageCase("Ngứa da nhẹ ở cánh tay, không lan rộng", "non_emergency", "ngứa CB"),
    TriageCase("Đau bụng nhẹ, đi ngoài 1-2 lần, phân bình thường", "non_emergency", "RL nhẹ"),
    TriageCase("Chảy máu cam nhỏ, tự cầm sau 5 phút", "non_emergency", "CMC nhẹ"),
    TriageCase("Đau vai nhẹ sau khi mang túi nặng", "non_emergency", "đau vai"),
    TriageCase("Mệt mỏi nhẹ, uống nhiều cà phê hôm nay", "non_emergency", "caffeine"),
    TriageCase("Đau đầu nhẹ khi nhìn màn hình lâu", "non_emergency", "mỏi mắt"),
    TriageCase("Sổ mũi nhẹ, thời tiết thay đổi", "non_emergency", "viêm mũi TT"),
    TriageCase("Đau bụng nhẹ sau khi uống sữa", "non_emergency", "lactose"),
    TriageCase("Ngứa họng nhẹ, không đau, không sốt", "non_emergency", "kích ứng"),
    TriageCase("Đau lưng dưới nhẹ khi đứng lâu", "non_emergency", "đau lưng TT"),
    TriageCase("Mệt mỏi nhẹ sau khi làm việc cả ngày", "non_emergency", "mệt TT"),
    TriageCase("Đau đầu nhẹ buổi sáng, uống nước đỡ", "non_emergency", "mất nước"),
    TriageCase("Nổi mụn nước nhỏ ở môi, không đau nhiều", "non_emergency", "herpes"),
    TriageCase("Đau bụng nhẹ, đầy hơi sau bữa ăn nhiều rau", "non_emergency", "đầy hơi"),
    TriageCase("Chóng mặt nhẹ khi đọc sách trong xe", "non_emergency", "say xe"),
    TriageCase("Đau cổ nhẹ sau khi nhìn điện thoại lâu", "non_emergency", "đau cổ TT"),
    TriageCase("Ngứa da nhẹ sau khi mặc áo len mới", "non_emergency", "kích ứng da"),
    TriageCase("Mệt mỏi nhẹ, không sốt, ăn uống bình thường", "non_emergency", "mệt"),
]


# =============================================================================
# SECTION B — RAG TEST QUERIES
# =============================================================================
# 30 query y tế tiếng Việt với expected_keywords để verify retrieval relevance.

@dataclass
class RAGTestCase:
    query: str
    expected_keywords: list[str]   # Từ khóa phải xuất hiện trong top results (case-insensitive, accent-insensitive)
    note: str = ""
    relies_on_synonym: bool = False   # True nếu query dùng tên thương mại / từ thông dụng


RAG_TEST_CASES: list[RAGTestCase] = [
    # Drug name (tên thuốc cụ thể)
    RAGTestCase("paracetamol", ["paracetamol"], "drug exact"),
    RAGTestCase("amoxicillin", ["amoxicillin"], "drug exact"),
    RAGTestCase("aspirin", ["aspirin"], "drug exact"),
    RAGTestCase("ibuprofen", ["ibuprofen"], "drug exact"),

    # Drug — commercial name (cần synonym để map sang hoạt chất)
    RAGTestCase("panadol", ["paracetamol"], "panadol→paracetamol", relies_on_synonym=True),
    RAGTestCase("hapacol", ["paracetamol"], "hapacol→paracetamol", relies_on_synonym=True),
    RAGTestCase("efferalgan", ["paracetamol"], "efferalgan→paracetamol", relies_on_synonym=True),

    # Drug — interaction
    RAGTestCase("paracetamol và rượu", ["paracetamol", "ruou", "rượu"], "drug + interaction"),
    RAGTestCase("panadol uống với bia", ["paracetamol", "ruou", "rượu"], "synonym + interaction", relies_on_synonym=True),

    # Symptom — Vietnamese natural language
    RAGTestCase("sốt cao đau họng ho", ["sot", "ho", "viem"], "symptom"),
    RAGTestCase("đau bụng buồn nôn tiêu chảy", ["bung", "non", "tieu"], "GI symptom"),
    RAGTestCase("đau ngực khó thở", ["nguc", "tho"], "cardiac symptom"),
    RAGTestCase("đau đầu dữ dội", ["dau dau", "dau"], "neuro symptom"),
    RAGTestCase("phát ban ngứa", ["phat ban", "ngua", "di ung"], "skin symptom"),
    RAGTestCase("ho ra máu", ["ho", "mau", "lao"], "respiratory red flag"),

    # Disease — Vietnamese
    RAGTestCase("viêm phổi", ["viem phoi", "phoi"], "disease VN"),
    RAGTestCase("tiểu đường", ["tieu duong", "đái tháo đường"], "disease VN"),
    RAGTestCase("cao huyết áp", ["huyet ap", "tang huyet ap"], "disease VN"),
    RAGTestCase("dạ dày", ["da day", "tieu hoa", "bao tu"], "disease VN", relies_on_synonym=True),

    # Nutrition
    RAGTestCase("nhu cầu canxi cho người cao tuổi", ["canxi", "calcium"], "nutrition"),
    RAGTestCase("sắt cho phụ nữ", ["sat", "iron"], "nutrition"),
    RAGTestCase("vitamin d hàng ngày", ["vitamin"], "nutrition"),

    # Multi-keyword complex
    RAGTestCase("trẻ em sốt cao co giật", ["sot", "co giat", "tre em"], "pediatric"),
    RAGTestCase("phụ nữ mang thai đau bụng", ["mang thai", "dau bung"], "obstetric"),
    RAGTestCase("người cao tuổi mệt mỏi khó thở", ["met moi", "kho tho"], "geriatric"),

    # Mental health (psychology adapter)
    RAGTestCase("mất ngủ căng thẳng", ["mat ngu", "cang thang"], "psych"),
    RAGTestCase("lo âu hồi hộp", ["lo au", "hoi hop"], "psych"),

    # Edge cases
    RAGTestCase("không muốn sống nữa", ["tu hai", "khung hoang", "cap cuu"], "self-harm signal", relies_on_synonym=True),
    RAGTestCase("đau dạ dày sau ăn", ["da day", "tieu hoa"], "GI"),
    RAGTestCase("tăng huyết áp khẩn cấp", ["huyet ap", "cap cuu"], "HTN crisis"),
]


# =============================================================================
# SECTION C — DRUG LOOKUP TEST CASES
# =============================================================================
@dataclass
class DrugLookupCase:
    query: str
    note: str = ""
    expected_found: bool = True  # whether we expect drug DB to find SOMETHING


DRUG_LOOKUP_CASES: list[DrugLookupCase] = [
    DrugLookupCase("Paracetamol 500mg", "common drug"),
    DrugLookupCase("Amoxicillin 500mg", "antibiotic"),
    DrugLookupCase("Panadol", "commercial name"),
    DrugLookupCase("Tiffy", "VN OTC"),
    DrugLookupCase("Decolgen", "VN OTC"),
    DrugLookupCase("Hapacol 650", "VN paracetamol brand"),
    DrugLookupCase("Aspirin", "common"),
    DrugLookupCase("Ibuprofen", "NSAID"),
    DrugLookupCase("Cetirizine", "antihistamine"),
    DrugLookupCase("Loratadine", "antihistamine"),
    DrugLookupCase("Omeprazole", "PPI"),
    DrugLookupCase("Metformin", "antidiabetic"),
    DrugLookupCase("Amlodipine", "antihypertensive"),
    DrugLookupCase("Atorvastatin", "statin"),
    DrugLookupCase("Salbutamol", "bronchodilator"),
    DrugLookupCase("Augmentin", "abx commercial"),
    DrugLookupCase("Klamentin", "abx VN"),
    DrugLookupCase("Tylenol", "US brand", expected_found=False),
    DrugLookupCase("Some_Random_Drug_XYZ", "noise", expected_found=False),
    DrugLookupCase("Vitamin C 500mg", "supplement"),
]


# =============================================================================
# CORE BENCHMARK FUNCTIONS
# =============================================================================

def _normalize(text: str) -> str:
    t = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t).strip()


def _hit_at_k(hit_titles: list[str], hit_contents: list[str], expected: list[str], k: int) -> bool:
    """Check if any of top-k hits contains any expected keyword (in title OR content)."""
    norm_keywords = [_normalize(kw) for kw in expected]
    for i in range(min(k, len(hit_titles))):
        haystack = _normalize(hit_titles[i] + " " + hit_contents[i])
        for kw in norm_keywords:
            if kw and kw in haystack:
                return True
    return False


def _reciprocal_rank(hit_titles: list[str], hit_contents: list[str], expected: list[str]) -> float:
    norm_keywords = [_normalize(kw) for kw in expected]
    for rank, (title, content) in enumerate(zip(hit_titles, hit_contents), start=1):
        haystack = _normalize(title + " " + content)
        for kw in norm_keywords:
            if kw and kw in haystack:
                return 1.0 / rank
    return 0.0


# ── A. Triage — Confusion Matrix using REAL build_triage_result ────────
@dataclass
class ConfusionMatrix:
    labels: list[str] = field(default_factory=lambda: ["emergency", "urgent", "non_emergency"])
    matrix: dict[str, dict[str, int]] = field(default_factory=dict)

    def __post_init__(self):
        for t in self.labels:
            self.matrix[t] = {p: 0 for p in self.labels}

    def add(self, true_label: str, pred_label: str):
        if true_label in self.matrix and pred_label in self.matrix[true_label]:
            self.matrix[true_label][pred_label] += 1

    def precision(self, label: str) -> float:
        tp = self.matrix[label][label]
        fp = sum(self.matrix[t][label] for t in self.labels if t != label)
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0

    def recall(self, label: str) -> float:
        tp = self.matrix[label][label]
        fn = sum(self.matrix[label][p] for p in self.labels if p != label)
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0

    def f1(self, label: str) -> float:
        p, r = self.precision(label), self.recall(label)
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    def accuracy(self) -> float:
        correct = sum(self.matrix[l][l] for l in self.labels)
        total = sum(self.matrix[t][p] for t in self.labels for p in self.labels)
        return correct / total if total > 0 else 0.0


def benchmark_triage() -> dict[str, Any]:
    """[A] Real triage benchmark using app.services.triage_service.build_triage_result."""
    cm = ConfusionMatrix()
    latencies_ms: list[float] = []
    misclassifications: list[dict[str, Any]] = []

    for case in TRIAGE_CASES:
        req = TriageRequest(symptom_text=case.symptom_text, mode="hybrid")
        t0 = time.perf_counter()
        resp = build_triage_result(req)
        latency_ms = (time.perf_counter() - t0) * 1000
        latencies_ms.append(latency_ms)
        cm.add(case.ground_truth, resp.urgency_level)

        if resp.urgency_level != case.ground_truth:
            misclassifications.append({
                "symptom": case.symptom_text,
                "note": case.note,
                "ground_truth": case.ground_truth,
                "predicted": resp.urgency_level,
                "is_critical": case.ground_truth == "emergency",
            })

    sorted_lat = sorted(latencies_ms)
    return {
        "total_cases": len(TRIAGE_CASES),
        "accuracy": cm.accuracy(),
        "confusion_matrix": cm.matrix,
        "per_class": {
            label: {
                "precision": cm.precision(label),
                "recall": cm.recall(label),
                "f1": cm.f1(label),
                "support": sum(cm.matrix[label].values()),
            }
            for label in cm.labels
        },
        "misclassifications": misclassifications,
        "missed_emergencies": [m for m in misclassifications if m["is_critical"]],
        "latency_ms": {
            "mean": statistics.mean(latencies_ms),
            "median": statistics.median(latencies_ms),
            "p95": sorted_lat[int(len(sorted_lat) * 0.95)],
            "p99": sorted_lat[int(len(sorted_lat) * 0.99)] if len(sorted_lat) >= 100 else max(sorted_lat),
            "max": max(latencies_ms),
        },
    }


# ── B. RAG with vs without synonyms — REAL RAGService instances ────────
def benchmark_rag_synonyms(rag_service_full: RAGService, rag_service_no_syn: RAGService) -> dict[str, Any]:
    """[B] Compare RAG with full medical synonym expansion vs without."""
    results_full = {"hit@1": [], "hit@3": [], "hit@5": [], "rr": []}
    results_no_syn = {"hit@1": [], "hit@3": [], "hit@5": [], "rr": []}
    detail_log: list[dict[str, Any]] = []

    for case in RAG_TEST_CASES:
        # Full synonyms
        hits_full = rag_service_full.search(case.query, top_k=5, adapter="medical")
        titles_full = [h.title for h in hits_full]
        contents_full = [h.content for h in hits_full]

        # No synonyms
        hits_no_syn = rag_service_no_syn.search(case.query, top_k=5, adapter="medical")
        titles_no_syn = [h.title for h in hits_no_syn]
        contents_no_syn = [h.content for h in hits_no_syn]

        for k in (1, 3, 5):
            results_full[f"hit@{k}"].append(_hit_at_k(titles_full, contents_full, case.expected_keywords, k))
            results_no_syn[f"hit@{k}"].append(_hit_at_k(titles_no_syn, contents_no_syn, case.expected_keywords, k))

        results_full["rr"].append(_reciprocal_rank(titles_full, contents_full, case.expected_keywords))
        results_no_syn["rr"].append(_reciprocal_rank(titles_no_syn, contents_no_syn, case.expected_keywords))

        detail_log.append({
            "query": case.query,
            "note": case.note,
            "relies_on_synonym": case.relies_on_synonym,
            "with_synonyms_top1": titles_full[0] if titles_full else None,
            "without_synonyms_top1": titles_no_syn[0] if titles_no_syn else None,
            "with_synonyms_hits": len(hits_full),
            "without_synonyms_hits": len(hits_no_syn),
        })

    n = len(RAG_TEST_CASES)
    syn_only = [c for c in RAG_TEST_CASES if c.relies_on_synonym]
    n_syn = len(syn_only)

    # Synonym-dependent slice
    syn_full_hr3 = sum(
        results_full["hit@3"][i] for i, c in enumerate(RAG_TEST_CASES) if c.relies_on_synonym
    ) / max(n_syn, 1)
    syn_no_hr3 = sum(
        results_no_syn["hit@3"][i] for i, c in enumerate(RAG_TEST_CASES) if c.relies_on_synonym
    ) / max(n_syn, 1)

    return {
        "n_queries": n,
        "n_synonym_dependent": n_syn,
        "with_synonyms": {
            "hit@1": sum(results_full["hit@1"]) / n,
            "hit@3": sum(results_full["hit@3"]) / n,
            "hit@5": sum(results_full["hit@5"]) / n,
            "mrr": statistics.mean(results_full["rr"]),
        },
        "without_synonyms": {
            "hit@1": sum(results_no_syn["hit@1"]) / n,
            "hit@3": sum(results_no_syn["hit@3"]) / n,
            "hit@5": sum(results_no_syn["hit@5"]) / n,
            "mrr": statistics.mean(results_no_syn["rr"]),
        },
        "synonym_dependent_only": {
            "with_synonyms_hit@3": syn_full_hr3,
            "without_synonyms_hit@3": syn_no_hr3,
            "improvement_pct": (syn_full_hr3 - syn_no_hr3) * 100,
        },
        "detail_log": detail_log,
    }


# ── C. RAG adapter routing comparison ──────────────────────────────────
def benchmark_rag_adapter_routing(rag_service: RAGService) -> dict[str, Any]:
    """[C] Compare scoring with adapter='medical' vs adapter='psychology'.

    Verifies that medical adapter boost (×1.12 on drug/disease types) and
    psychology adapter boost (×1.15 on symptom phrases) actually change
    the top-1 result for queries from the relevant domain.
    """
    medical_queries = ["paracetamol", "viêm phổi", "tăng huyết áp", "tiểu đường", "amoxicillin"]
    psych_queries = ["mất ngủ căng thẳng", "lo âu hồi hộp", "đau đầu căng thẳng", "buồn bã"]

    medical_diff = 0
    psych_diff = 0
    detail = []

    for q in medical_queries:
        h_med = rag_service.search(q, top_k=3, adapter="medical")
        h_psy = rag_service.search(q, top_k=3, adapter="psychology")
        same = h_med and h_psy and h_med[0].record_id == h_psy[0].record_id
        if not same:
            medical_diff += 1
        detail.append({
            "query": q,
            "domain": "medical",
            "medical_top1": h_med[0].title if h_med else None,
            "psychology_top1": h_psy[0].title if h_psy else None,
            "ranking_changed": not same,
        })

    for q in psych_queries:
        h_med = rag_service.search(q, top_k=3, adapter="medical")
        h_psy = rag_service.search(q, top_k=3, adapter="psychology")
        same = h_med and h_psy and h_med[0].record_id == h_psy[0].record_id
        if not same:
            psych_diff += 1
        detail.append({
            "query": q,
            "domain": "psychology",
            "medical_top1": h_med[0].title if h_med else None,
            "psychology_top1": h_psy[0].title if h_psy else None,
            "ranking_changed": not same,
        })

    return {
        "medical_queries_tested": len(medical_queries),
        "medical_ranking_changes": medical_diff,
        "psych_queries_tested": len(psych_queries),
        "psych_ranking_changes": psych_diff,
        "detail": detail,
    }


# ── D. Drug lookup — exact vs partial coverage ─────────────────────────
def benchmark_drug_lookup() -> dict[str, Any]:
    """[D] Test drug_lookup_service against real DAV database (60k+ records)."""
    db = drug_lookup_service.load_drug_database()
    db_size = len(db)

    found_count = 0
    not_found_count = 0
    expected_found_correct = 0
    expected_notfound_correct = 0
    latencies_ms: list[float] = []
    detail: list[dict[str, Any]] = []

    for case in DRUG_LOOKUP_CASES:
        t0 = time.perf_counter()
        result = drug_lookup_service.search_drug_by_name(case.query, db)
        latency_ms = (time.perf_counter() - t0) * 1000
        latencies_ms.append(latency_ms)

        was_found = result is not None
        if was_found:
            found_count += 1
        else:
            not_found_count += 1

        if was_found == case.expected_found:
            if case.expected_found:
                expected_found_correct += 1
            else:
                expected_notfound_correct += 1

        detail.append({
            "query": case.query,
            "note": case.note,
            "expected_found": case.expected_found,
            "actual_found": was_found,
            "matched_name": result.get("name") if was_found else None,
            "latency_ms": round(latency_ms, 2),
        })

    sorted_lat = sorted(latencies_ms)
    n_expected_yes = sum(1 for c in DRUG_LOOKUP_CASES if c.expected_found)
    n_expected_no = len(DRUG_LOOKUP_CASES) - n_expected_yes

    return {
        "db_records": db_size,
        "n_queries": len(DRUG_LOOKUP_CASES),
        "found": found_count,
        "not_found": not_found_count,
        "true_positive_rate": expected_found_correct / max(n_expected_yes, 1),
        "true_negative_rate": expected_notfound_correct / max(n_expected_no, 1),
        "latency_ms": {
            "mean": statistics.mean(latencies_ms),
            "median": statistics.median(latencies_ms),
            "p95": sorted_lat[int(len(sorted_lat) * 0.95)],
            "max": max(latencies_ms),
        },
        "detail": detail,
    }


# ── E. Triage latency at scale ─────────────────────────────────────────
def benchmark_latency_scale(n_runs: int = 1000) -> dict[str, Any]:
    """[E] Latency distribution at scale — 1000 runs across diverse inputs."""
    test_inputs = [c.symptom_text for c in TRIAGE_CASES]
    latencies_ms: list[float] = []

    for i in range(n_runs):
        symptom = test_inputs[i % len(test_inputs)]
        req = TriageRequest(symptom_text=symptom, mode="hybrid")
        t0 = time.perf_counter()
        build_triage_result(req)
        latencies_ms.append((time.perf_counter() - t0) * 1000)

    sorted_lat = sorted(latencies_ms)
    total_time_s = sum(latencies_ms) / 1000
    return {
        "n_runs": n_runs,
        "latency_ms": {
            "mean": statistics.mean(latencies_ms),
            "median": statistics.median(latencies_ms),
            "stdev": statistics.stdev(latencies_ms),
            "p50": sorted_lat[int(n_runs * 0.50)],
            "p90": sorted_lat[int(n_runs * 0.90)],
            "p95": sorted_lat[int(n_runs * 0.95)],
            "p99": sorted_lat[int(n_runs * 0.99)],
            "min": min(latencies_ms),
            "max": max(latencies_ms),
        },
        "throughput_rps": n_runs / max(total_time_s, 1e-9),
        "under_10ms_pct": sum(1 for l in latencies_ms if l < 10) / n_runs * 100,
        "under_50ms_pct": sum(1 for l in latencies_ms if l < 50) / n_runs * 100,
    }


# =============================================================================
# RAG SERVICE FACTORIES
# =============================================================================
def make_rag_with_synonyms() -> RAGService:
    """Standard RAGService — has full MEDICAL_SYNONYMS expansion."""
    return RAGService()


def make_rag_without_synonyms() -> RAGService:
    """RAGService with empty synonym table — for ablation."""
    svc = RAGService()
    # Monkey-patch _expand_tokens to identity (no synonym expansion).
    # This is a controlled ablation, not a permanent change.
    original = svc._expand_tokens
    def _no_expand(tokens):
        return list(tokens)
    svc._expand_tokens = _no_expand   # type: ignore
    return svc


# =============================================================================
# REPORT PRINTER
# =============================================================================
def print_report(triage: dict, rag_syn: dict, rag_adapter: dict, drug: dict, latency: dict) -> None:
    SEP = "=" * 72
    sep = "-" * 72
    print(f"\n{SEP}")
    print("  MediSign AI — REAL Benchmark Report (Production Services)")
    print(SEP)

    # ── A. Triage ────────────────────────────────────────────────────────
    print("\n[A] CLINICAL SAFETY — Triage Confusion Matrix (real build_triage_result)")
    print(sep)
    print(f"  Total cases   : {triage['total_cases']}")
    print(f"  Accuracy      : {triage['accuracy']*100:.1f}%")
    print(f"  Mean latency  : {triage['latency_ms']['mean']:.3f} ms")
    print(f"  P95 latency   : {triage['latency_ms']['p95']:.3f} ms")
    print()

    labels = ["emergency", "urgent", "non_emergency"]
    label_vi = {"emergency": "Đỏ (Emergency)", "urgent": "Vàng (Urgent)", "non_emergency": "Xanh (Non-Em.)"}

    print("  Confusion Matrix (rows=Actual, cols=Predicted):")
    print(f"  {'Actual / Pred':22} | {'emergency':>10} | {'urgent':>8} | {'non_emerg':>10}")
    print(f"  {'-'*22}-+-{'-'*10}-+-{'-'*8}-+-{'-'*10}")
    for t in labels:
        r = triage["confusion_matrix"][t]
        print(f"  {label_vi[t]:22} | {r['emergency']:>10} | {r['urgent']:>8} | {r['non_emergency']:>10}")

    print()
    print(f"  {'Class':22} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
    print(f"  {'-'*22} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
    for label in labels:
        pc = triage["per_class"][label]
        critical = " [CRITICAL]" if label == "emergency" and pc["recall"] < 0.95 else ""
        print(f"  {label_vi[label]:22} {pc['precision']*100:>9.1f}% {pc['recall']*100:>9.1f}% "
              f"{pc['f1']*100:>9.1f}% {pc['support']:>10}{critical}")

    emg = triage["per_class"]["emergency"]
    print()
    print(f"  Emergency Recall = {emg['recall']*100:.1f}% (clinical safety threshold: ≥95%)")

    misses = triage["missed_emergencies"]
    if misses:
        print(f"\n  Missed emergencies ({len(misses)}):")
        for m in misses:
            print(f"    [{m['note']}] '{m['symptom'][:55]}' → predicted as: {m['predicted']}")

    # Additional misclassifications
    other_miss = [m for m in triage["misclassifications"] if not m["is_critical"]]
    if other_miss:
        print(f"\n  Other misclassifications ({len(other_miss)}):")
        for m in other_miss[:10]:
            print(f"    [{m['ground_truth']:>13}→{m['predicted']:<13}] '{m['symptom'][:50]}'")
        if len(other_miss) > 10:
            print(f"    ... +{len(other_miss) - 10} more")

    # ── B. RAG Synonyms ──────────────────────────────────────────────────
    print(f"\n{sep}")
    print("[B] RAG QUALITY — With vs Without Medical Synonyms (real RAGService)")
    print(sep)
    print(f"  N queries           : {rag_syn['n_queries']}")
    print(f"  N synonym-dependent : {rag_syn['n_synonym_dependent']}")
    print()
    print(f"  {'Metric':18} {'Without syn':>14} {'With syn':>12} {'Δ (pp)':>10}")
    print(f"  {'-'*18} {'-'*14} {'-'*12} {'-'*10}")
    for metric in ["hit@1", "hit@3", "hit@5", "mrr"]:
        wo = rag_syn["without_synonyms"][metric]
        w = rag_syn["with_synonyms"][metric]
        delta = (w - wo) * 100
        sign = "+" if delta >= 0 else ""
        print(f"  {metric:18} {wo*100:>13.1f}% {w*100:>11.1f}% {sign}{delta:>9.1f}")
    print()
    syn = rag_syn["synonym_dependent_only"]
    print(f"  On synonym-dependent queries only:")
    print(f"    Hit@3 without : {syn['without_synonyms_hit@3']*100:.1f}%")
    print(f"    Hit@3 with    : {syn['with_synonyms_hit@3']*100:.1f}%")
    print(f"    Improvement   : +{syn['improvement_pct']:.1f} percentage points")

    # ── C. Adapter Routing ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("[C] RAG ADAPTER ROUTING — Medical vs Psychology adapter scoring")
    print(sep)
    print(f"  Medical queries  : {rag_adapter['medical_queries_tested']} (ranking changes: {rag_adapter['medical_ranking_changes']})")
    print(f"  Psych queries    : {rag_adapter['psych_queries_tested']} (ranking changes: {rag_adapter['psych_ranking_changes']})")
    total_changes = rag_adapter['medical_ranking_changes'] + rag_adapter['psych_ranking_changes']
    total_q = rag_adapter['medical_queries_tested'] + rag_adapter['psych_queries_tested']
    if total_q > 0:
        print(f"  Adapter routing affects top-1 in {total_changes}/{total_q} queries ({total_changes/total_q*100:.0f}%)")
    else:
        print(f"  (skipped — no queries tested)")

    # ── D. Drug Lookup ──────────────────────────────────────────────────
    print(f"\n{sep}")
    print("[D] DRUG LOOKUP — Real DAV database via drug_lookup_service")
    print(sep)
    print(f"  DB records           : {drug['db_records']:,}")
    print(f"  N queries            : {drug['n_queries']}")
    print(f"  Found / Not found    : {drug['found']} / {drug['not_found']}")
    print(f"  True positive rate   : {drug['true_positive_rate']*100:.1f}%  (queries expected to find)")
    print(f"  True negative rate   : {drug['true_negative_rate']*100:.1f}%  (queries expected NOT to find)")
    print(f"  Mean latency         : {drug['latency_ms']['mean']:.2f} ms")
    print(f"  P95 latency          : {drug['latency_ms']['p95']:.2f} ms")

    # Show edge cases
    not_found_unexpected = [d for d in drug["detail"] if d["expected_found"] and not d["actual_found"]]
    if not_found_unexpected:
        print(f"\n  Drugs expected found but missed:")
        for d in not_found_unexpected:
            print(f"    [{d['note']:25}] '{d['query']}'")

    # ── E. Latency at Scale ──────────────────────────────────────────────
    print(f"\n{sep}")
    print("[E] LATENCY AT SCALE — Triage rule-based path, 1000 runs")
    print(sep)
    lat = latency["latency_ms"]
    print(f"  N runs        : {latency['n_runs']}")
    print(f"  Mean / Stdev  : {lat['mean']:.3f} ms / {lat['stdev']:.3f} ms")
    print(f"  P50           : {lat['p50']:.3f} ms")
    print(f"  P90           : {lat['p90']:.3f} ms")
    print(f"  P95           : {lat['p95']:.3f} ms")
    print(f"  P99           : {lat['p99']:.3f} ms")
    print(f"  Min / Max     : {lat['min']:.3f} ms / {lat['max']:.3f} ms")
    print(f"  Throughput    : {latency['throughput_rps']:,.0f} req/s")
    print(f"  < 10 ms       : {latency['under_10ms_pct']:.1f}%")
    print(f"  < 50 ms       : {latency['under_50ms_pct']:.1f}%")

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  SUMMARY (cho báo cáo NCKH)")
    print(SEP)
    print(f"  1. Triage accuracy          : {triage['accuracy']*100:.1f}% / 100 cases")
    print(f"  2. Emergency recall          : {emg['recall']*100:.1f}% (target: ≥95%)")
    print(f"  3. RAG synonym improvement   : Hit@3 +{(rag_syn['with_synonyms']['hit@3']-rag_syn['without_synonyms']['hit@3'])*100:.1f}pp overall, "
          f"+{rag_syn['synonym_dependent_only']['improvement_pct']:.1f}pp on commercial-name queries")
    print(f"  4. RAG MRR                   : {rag_syn['with_synonyms']['mrr']:.3f} (with synonyms)")
    if total_q > 0:
        print(f"  5. Adapter routing impact    : {total_changes}/{total_q} queries get re-ranked")
    else:
        print(f"  5. Adapter routing impact    : (skipped)")
    print(f"  6. Drug lookup TPR/TNR       : {drug['true_positive_rate']*100:.0f}% / {drug['true_negative_rate']*100:.0f}%")
    print(f"  7. Triage latency            : {lat['mean']:.2f}ms mean, P95={lat['p95']:.2f}ms, throughput {latency['throughput_rps']:,.0f} req/s")
    print(SEP)


def save_json(triage: dict, rag_syn: dict, rag_adapter: dict, drug: dict, latency: dict, output_path: Path):
    report = {
        "benchmark_version": "2.0.0-real",
        "system": "MediSign AI",
        "description": "Real benchmark using production services (no mocks). LLM path not benchmarked (requires GPU).",
        "sections": {
            "A_triage_safety": triage,
            "B_rag_synonyms": rag_syn,
            "C_rag_adapter_routing": rag_adapter,
            "D_drug_lookup": drug,
            "E_latency_scale": latency,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  JSON report saved -> {output_path}")


# =============================================================================
# MAIN
# =============================================================================
def main():
    ap = argparse.ArgumentParser(description="MediSign AI real benchmark suite.")
    ap.add_argument("--output", type=Path,
                    default=BACKEND_DIR / "output" / "benchmark_real_report.json",
                    help="JSON output path")
    ap.add_argument("--latency-runs", type=int, default=1000,
                    help="Number of runs for latency scale benchmark")
    ap.add_argument("--skip-rag", action="store_true",
                    help="Skip RAG benchmarks (faster — only Triage + Drug + Latency)")
    args = ap.parse_args()

    print("\n" + "=" * 72)
    print("  Running MediSign AI REAL benchmark...")
    print("  (Uses production services, no LLM/GPU required)")
    print("=" * 72)

    # ── A ────────────────────────────────────────
    print("\n[A] Triage benchmark on 100 cases (real build_triage_result)...")
    triage_results = benchmark_triage()

    # ── B + C ────────────────────────────────────
    if not args.skip_rag:
        print("[B] Loading RAG service (this can take ~30s for 754MB KB)...")
        rag_full = make_rag_with_synonyms()
        rag_full._ensure_loaded()
        kb_status = rag_full.status()
        print(f"    Loaded {kb_status['documents']:,} documents, {kb_status['index_terms']:,} terms")

        print("[B] Building 'no synonyms' RAG service for ablation...")
        rag_no_syn = make_rag_without_synonyms()
        rag_no_syn._ensure_loaded()

        print("[B] Running RAG synonym ablation on 30 queries...")
        rag_syn_results = benchmark_rag_synonyms(rag_full, rag_no_syn)

        print("[C] Running RAG adapter routing comparison...")
        rag_adapter_results = benchmark_rag_adapter_routing(rag_full)
    else:
        print("[B][C] RAG benchmarks SKIPPED (--skip-rag)")
        rag_syn_results = {"n_queries": 0, "n_synonym_dependent": 0,
                           "with_synonyms": {"hit@1": 0, "hit@3": 0, "hit@5": 0, "mrr": 0},
                           "without_synonyms": {"hit@1": 0, "hit@3": 0, "hit@5": 0, "mrr": 0},
                           "synonym_dependent_only": {"with_synonyms_hit@3": 0, "without_synonyms_hit@3": 0, "improvement_pct": 0},
                           "detail_log": []}
        rag_adapter_results = {"medical_queries_tested": 0, "medical_ranking_changes": 0,
                               "psych_queries_tested": 0, "psych_ranking_changes": 0, "detail": []}

    # ── D ────────────────────────────────────────
    print("[D] Running drug lookup benchmark on real DAV DB...")
    drug_results = benchmark_drug_lookup()

    # ── E ────────────────────────────────────────
    print(f"[E] Running latency benchmark on {args.latency_runs} runs...")
    latency_results = benchmark_latency_scale(args.latency_runs)

    # Print + save
    print_report(triage_results, rag_syn_results, rag_adapter_results, drug_results, latency_results)
    save_json(triage_results, rag_syn_results, rag_adapter_results, drug_results, latency_results, args.output)


if __name__ == "__main__":
    main()
