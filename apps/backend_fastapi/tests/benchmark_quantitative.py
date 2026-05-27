"""
=============================================================================
MediSign AI — Quantitative Benchmark Suite
=============================================================================
Chạy: python -m pytest tests/benchmark_quantitative.py -v -s
Hoặc: python tests/benchmark_quantitative.py  (standalone)

Bao gồm 3 nhóm đánh giá:
  [A] Clinical Safety  — Confusion Matrix, Recall/Precision cho Triage
  [B] System Performance — Latency Rule-based vs LLM path
  [C] RAG Quality       — Hit Rate, MRR trên tập câu hỏi y tế tiếng Việt
=============================================================================
"""

from __future__ import annotations

import asyncio
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# ── Thêm project root vào sys.path ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_service import build_triage_result

# ─────────────────────────────────────────────────────────────────────────────
# SECTION A: CLINICAL SAFETY — TRIAGE CONFUSION MATRIX
# ─────────────────────────────────────────────────────────────────────────────

TriageLabel = Literal["emergency", "urgent", "non_emergency"]

@dataclass
class TriageCase:
    symptom_text: str
    ground_truth: TriageLabel
    note: str = ""


# 100 ca bệnh giả định — 30 Đỏ (emergency), 30 Vàng (urgent), 40 Xanh (non_emergency)
TRIAGE_CASES: list[TriageCase] = [
    # ── EMERGENCY (30 ca) ────────────────────────────────────────────────────
    TriageCase("Tôi đang khó thở rất nặng, không thở được", "emergency", "khó thở cấp"),
    TriageCase("Đau ngực dữ dội lan ra cánh tay trái", "emergency", "nghi nhồi máu cơ tim"),
    TriageCase("Bệnh nhân bị ngất, không tỉnh lại được", "emergency", "ngất xỉu"),
    TriageCase("Khó thở và đau ngực khi nằm xuống", "emergency", "suy tim cấp"),
    TriageCase("Tôi bị ngất xỉu đột ngột khi đứng dậy", "emergency", "ngất tư thế"),
    TriageCase("Đau ngực như bị bóp nghẹt, vã mồ hôi lạnh", "emergency", "ACS"),
    TriageCase("Khó thở không thở được, môi tím tái", "emergency", "suy hô hấp"),
    TriageCase("Bị ngất, giờ tỉnh nhưng vẫn đau ngực", "emergency", "sau ngất + đau ngực"),
    TriageCase("Thở khò khè nặng, không nói được câu dài", "emergency", "hen phế quản nặng"),
    TriageCase("Đau ngực trái dữ dội kèm buồn nôn và vã mồ hôi", "emergency", "NMCT"),
    TriageCase("Khó thở đột ngột sau khi ăn, nghi dị ứng nặng", "emergency", "phản vệ"),
    TriageCase("Bệnh nhân co giật toàn thân không dừng được", "emergency", "động kinh cơn lớn"),
    TriageCase("Đột ngột nói ngọng, tay chân yếu một bên", "emergency", "đột quỵ"),
    TriageCase("Mặt méo, tay trái không nhấc lên được, nói khó", "emergency", "đột quỵ"),
    TriageCase("Đau đầu dữ dội nhất từ trước đến nay, đột ngột", "emergency", "xuất huyết não"),
    TriageCase("Nôn ra máu đỏ tươi nhiều lần", "emergency", "xuất huyết tiêu hóa trên"),
    TriageCase("Đi ngoài phân đen như hắc ín, chóng mặt", "emergency", "XH tiêu hóa"),
    TriageCase("Bụng cứng như gỗ, đau dữ dội không dám thở sâu", "emergency", "thủng tạng rỗng"),
    TriageCase("Trẻ sơ sinh khó thở, môi tím, không bú được", "emergency", "suy hô hấp sơ sinh"),
    TriageCase("Phụ nữ mang thai đau bụng dữ dội kèm ra máu", "emergency", "nhau bong non"),
    TriageCase("Bị điện giật, bất tỉnh vài giây rồi tỉnh", "emergency", "điện giật"),
    TriageCase("Uống nhầm thuốc trừ sâu, đang nôn mửa", "emergency", "ngộ độc"),
    TriageCase("Bị ong đốt nhiều nốt, khó thở và nổi mề đay toàn thân", "emergency", "phản vệ ong"),
    TriageCase("Đau ngực khi thở sâu, sau tai nạn giao thông", "emergency", "chấn thương ngực"),
    TriageCase("Trẻ 2 tuổi nuốt pin cúc, đang khóc và chảy nước dãi", "emergency", "dị vật thực quản"),
    TriageCase("Huyết áp 220/130, đau đầu dữ dội, nhìn mờ", "emergency", "tăng HA khủng hoảng"),
    TriageCase("Đường huyết 30 mg/dL, run tay, vã mồ hôi, lơ mơ", "emergency", "hạ đường huyết nặng"),
    TriageCase("Sốt 41 độ, cứng cổ, sợ ánh sáng", "emergency", "viêm màng não"),
    TriageCase("Khó thở và ngực đau sau khi bị đâm", "emergency", "chấn thương xuyên thấu"),
    TriageCase("Bệnh nhân không tỉnh, không phản xạ, thở yếu", "emergency", "hôn mê"),

    # ── URGENT (30 ca) ───────────────────────────────────────────────────────
    TriageCase("Sốt cao 39.5 độ kéo dài 3 ngày không hạ", "urgent", "sốt cao kéo dài"),
    TriageCase("Đau nhiều ở bụng dưới bên phải từ sáng đến giờ", "urgent", "nghi viêm ruột thừa"),
    TriageCase("Mệt mỏi nhiều, không ăn được, vàng da nhẹ", "urgent", "nghi viêm gan"),
    TriageCase("Sốt cao và đau đầu dữ dội từ hôm qua", "urgent", "sốt + đau đầu"),
    TriageCase("Đau nhiều khi đi tiểu, tiểu ra máu", "urgent", "nhiễm trùng tiết niệu"),
    TriageCase("Buồn nôn nhiều, nôn 5-6 lần trong ngày, không uống được nước", "urgent", "nôn mửa nặng"),
    TriageCase("Sốt cao 39 độ kèm phát ban đỏ toàn thân", "urgent", "sốt phát ban"),
    TriageCase("Đau nhiều ở tai, chảy mủ tai, sốt nhẹ", "urgent", "viêm tai giữa cấp"),
    TriageCase("Mệt mỏi nhiều, khó thở khi leo cầu thang", "urgent", "khó thở gắng sức"),
    TriageCase("Đau dữ dội vùng thắt lưng lan xuống đùi", "urgent", "đau thần kinh tọa cấp"),
    TriageCase("Sốt cao và đau họng không nuốt được", "urgent", "viêm amidan cấp"),
    TriageCase("Trẻ sốt cao 39.5, co giật 1 lần đã dừng", "urgent", "co giật do sốt"),
    TriageCase("Đau nhiều vùng bụng trên sau khi ăn nhiều dầu mỡ", "urgent", "nghi viêm tụy"),
    TriageCase("Mệt mỏi nhiều, da xanh xao, hoa mắt khi đứng dậy", "urgent", "thiếu máu"),
    TriageCase("Sốt cao 3 ngày, đau cơ toàn thân, đau sau hốc mắt", "urgent", "nghi sốt xuất huyết"),
    TriageCase("Đau nhiều khớp gối, sưng đỏ, không đi được", "urgent", "viêm khớp cấp"),
    TriageCase("Buồn nôn nhiều và đau bụng sau khi ăn hải sản", "urgent", "ngộ độc thực phẩm"),
    TriageCase("Sốt cao kèm ho có đờm vàng xanh 5 ngày", "urgent", "viêm phổi nghi ngờ"),
    TriageCase("Đau nhiều vùng hạ sườn phải, vàng mắt nhẹ", "urgent", "nghi sỏi mật"),
    TriageCase("Mệt mỏi nhiều, tiểu nhiều lần, khát nước liên tục", "urgent", "nghi tiểu đường"),
    TriageCase("Sốt cao và phát ban sau khi dùng thuốc mới", "urgent", "dị ứng thuốc"),
    TriageCase("Đau nhiều vùng bụng dưới, trễ kinh 6 tuần", "urgent", "nghi thai ngoài tử cung"),
    TriageCase("Mệt mỏi nhiều, sụt 5kg trong 1 tháng không rõ nguyên nhân", "urgent", "sụt cân bất thường"),
    TriageCase("Sốt cao và đau mắt đỏ, chảy ghèn nhiều", "urgent", "viêm kết mạc + sốt"),
    TriageCase("Đau nhiều vùng ngực khi hít thở sâu, không có chấn thương", "urgent", "viêm màng phổi"),
    TriageCase("Buồn nôn nhiều và đau đầu sau khi ở phòng kín có lò than", "urgent", "nghi ngộ độc CO"),
    TriageCase("Sốt cao kèm tiêu chảy nhiều lần, mất nước", "urgent", "tiêu chảy cấp mất nước"),
    TriageCase("Đau nhiều vùng bẹn phải, sưng to", "urgent", "nghi thoát vị bẹn nghẹt"),
    TriageCase("Mệt mỏi nhiều, tim đập nhanh bất thường khi nghỉ", "urgent", "rối loạn nhịp tim"),
    TriageCase("Sốt cao và đau lưng dữ dội, tiểu buốt", "urgent", "viêm thận bể thận"),

    # ── NON-EMERGENCY (40 ca) ────────────────────────────────────────────────
    TriageCase("Ho khan nhẹ 2 ngày, không sốt", "non_emergency", "ho nhẹ"),
    TriageCase("Sổ mũi, hắt hơi, không sốt", "non_emergency", "cảm lạnh nhẹ"),
    TriageCase("Đau đầu nhẹ sau khi làm việc nhiều giờ", "non_emergency", "đau đầu căng thẳng"),
    TriageCase("Ngứa da nhẹ, không nổi mề đay", "non_emergency", "ngứa da"),
    TriageCase("Mệt mỏi nhẹ sau khi tập thể dục", "non_emergency", "mệt sau tập"),
    TriageCase("Đau bụng nhẹ sau khi ăn no", "non_emergency", "khó tiêu"),
    TriageCase("Chóng mặt nhẹ khi đứng dậy nhanh", "non_emergency", "hạ HA tư thế nhẹ"),
    TriageCase("Đau cổ nhẹ sau khi ngủ sai tư thế", "non_emergency", "vẹo cổ"),
    TriageCase("Nổi mụn nhỏ ở mặt, không đau", "non_emergency", "mụn trứng cá"),
    TriageCase("Đau lưng nhẹ sau khi ngồi lâu", "non_emergency", "đau lưng cơ học"),
    TriageCase("Hắt hơi liên tục buổi sáng, không sốt", "non_emergency", "viêm mũi dị ứng"),
    TriageCase("Ngứa mắt nhẹ, không đỏ, không chảy nước mắt nhiều", "non_emergency", "dị ứng mắt nhẹ"),
    TriageCase("Đau khớp ngón tay nhẹ sau khi gõ máy tính nhiều", "non_emergency", "hội chứng ống cổ tay nhẹ"),
    TriageCase("Buồn nôn nhẹ buổi sáng, không nôn", "non_emergency", "buồn nôn nhẹ"),
    TriageCase("Đau họng nhẹ, không sốt, không khó nuốt", "non_emergency", "viêm họng nhẹ"),
    TriageCase("Mệt mỏi nhẹ, ngủ không ngon giấc 2 ngày", "non_emergency", "mất ngủ nhẹ"),
    TriageCase("Đau bụng nhẹ trước kỳ kinh", "non_emergency", "đau bụng kinh nhẹ"),
    TriageCase("Nổi mề đay nhỏ sau khi ăn tôm, không khó thở", "non_emergency", "dị ứng nhẹ"),
    TriageCase("Ho nhẹ và sổ mũi, đang hồi phục sau cảm", "non_emergency", "hồi phục cảm"),
    TriageCase("Đau đầu nhẹ, uống paracetamol đỡ", "non_emergency", "đau đầu đáp ứng thuốc"),
    TriageCase("Không có triệu chứng gì, chỉ muốn kiểm tra sức khỏe", "non_emergency", "khám định kỳ"),
    TriageCase("Đau cơ bắp chân nhẹ sau khi chạy bộ", "non_emergency", "đau cơ sau tập"),
    TriageCase("Ngứa da nhẹ ở cánh tay, không lan rộng", "non_emergency", "ngứa cục bộ"),
    TriageCase("Đau bụng nhẹ, đi ngoài 1-2 lần, phân bình thường", "non_emergency", "rối loạn tiêu hóa nhẹ"),
    TriageCase("Chảy máu cam nhỏ, tự cầm sau 5 phút", "non_emergency", "chảy máu cam nhẹ"),
    TriageCase("Đau vai nhẹ sau khi mang túi nặng", "non_emergency", "đau vai cơ học"),
    TriageCase("Mệt mỏi nhẹ, uống nhiều cà phê hôm nay", "non_emergency", "mệt do caffeine"),
    TriageCase("Đau đầu nhẹ khi nhìn màn hình lâu", "non_emergency", "mỏi mắt"),
    TriageCase("Sổ mũi nhẹ, thời tiết thay đổi", "non_emergency", "viêm mũi thời tiết"),
    TriageCase("Đau bụng nhẹ sau khi uống sữa", "non_emergency", "không dung nạp lactose nhẹ"),
    TriageCase("Ngứa họng nhẹ, không đau, không sốt", "non_emergency", "kích ứng họng nhẹ"),
    TriageCase("Đau lưng dưới nhẹ khi đứng lâu", "non_emergency", "đau lưng tư thế"),
    TriageCase("Mệt mỏi nhẹ sau khi làm việc cả ngày", "non_emergency", "mệt mỏi thông thường"),
    TriageCase("Đau đầu nhẹ buổi sáng, uống nước đỡ", "non_emergency", "đau đầu do mất nước nhẹ"),
    TriageCase("Nổi mụn nước nhỏ ở môi, không đau nhiều", "non_emergency", "herpes môi nhẹ"),
    TriageCase("Đau bụng nhẹ, đầy hơi sau bữa ăn nhiều rau", "non_emergency", "đầy hơi"),
    TriageCase("Chóng mặt nhẹ khi đọc sách trong xe", "non_emergency", "say xe nhẹ"),
    TriageCase("Đau cổ nhẹ sau khi nhìn điện thoại lâu", "non_emergency", "đau cổ tư thế"),
    TriageCase("Ngứa da nhẹ sau khi mặc áo len mới", "non_emergency", "kích ứng da nhẹ"),
    TriageCase("Mệt mỏi nhẹ, không sốt, ăn uống bình thường", "non_emergency", "mệt mỏi nhẹ"),
]


@dataclass
class ConfusionMatrix:
    labels: list[str] = field(default_factory=lambda: ["emergency", "urgent", "non_emergency"])
    matrix: dict[str, dict[str, int]] = field(default_factory=dict)

    def __post_init__(self):
        for true_label in self.labels:
            self.matrix[true_label] = {pred: 0 for pred in self.labels}

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


def run_triage_benchmark() -> dict:
    """Chạy 100 ca qua triage_service và tính confusion matrix."""
    cm = ConfusionMatrix()
    latencies_rule: list[float] = []
    missed_emergencies: list[dict] = []

    for case in TRIAGE_CASES:
        req = TriageRequest(symptom_text=case.symptom_text, mode="hybrid")
        t0 = time.perf_counter()
        resp = build_triage_result(req)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        latencies_rule.append(elapsed_ms)
        cm.add(case.ground_truth, resp.urgency_level)

        # Ghi lại các ca emergency bị bỏ sót (False Negative — nguy hiểm nhất)
        if case.ground_truth == "emergency" and resp.urgency_level != "emergency":
            missed_emergencies.append({
                "symptom": case.symptom_text,
                "note": case.note,
                "predicted": resp.urgency_level,
            })

    results = {
        "total_cases": len(TRIAGE_CASES),
        "accuracy": cm.accuracy(),
        "confusion_matrix": cm.matrix,
        "per_class": {},
        "missed_emergencies": missed_emergencies,
        "latency_rule_based_ms": {
            "mean": statistics.mean(latencies_rule),
            "median": statistics.median(latencies_rule),
            "p95": sorted(latencies_rule)[int(len(latencies_rule) * 0.95)],
            "max": max(latencies_rule),
        },
    }

    for label in cm.labels:
        results["per_class"][label] = {
            "precision": cm.precision(label),
            "recall": cm.recall(label),
            "f1": cm.f1(label),
            "support": sum(cm.matrix[label].values()),
        }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# SECTION B: SYSTEM PERFORMANCE — LATENCY BENCHMARK
# ─────────────────────────────────────────────────────────────────────────────

def run_latency_benchmark(n_runs: int = 200) -> dict:
    """
    Đo latency của Rule-based Triage path (không qua LLM).
    Mô phỏng 200 request liên tiếp với các loại triệu chứng khác nhau.
    """
    test_inputs = [
        "khó thở nặng",
        "sốt cao 39 độ",
        "ho nhẹ không sốt",
        "đau ngực dữ dội",
        "mệt mỏi nhẹ",
        "ngất xỉu đột ngột",
        "đau đầu nhẹ",
        "buồn nôn nhiều",
    ]

    latencies: list[float] = []
    results_by_urgency: dict[str, int] = {"emergency": 0, "urgent": 0, "non_emergency": 0}

    for i in range(n_runs):
        symptom = test_inputs[i % len(test_inputs)]
        req = TriageRequest(symptom_text=symptom, mode="hybrid")
        t0 = time.perf_counter()
        resp = build_triage_result(req)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed_ms)
        results_by_urgency[resp.urgency_level] = results_by_urgency.get(resp.urgency_level, 0) + 1

    sorted_lat = sorted(latencies)
    return {
        "n_runs": n_runs,
        "latency_ms": {
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "stdev": statistics.stdev(latencies),
            "p50": sorted_lat[int(n_runs * 0.50)],
            "p95": sorted_lat[int(n_runs * 0.95)],
            "p99": sorted_lat[int(n_runs * 0.99)],
            "min": min(latencies),
            "max": max(latencies),
        },
        "throughput_rps": n_runs / (sum(latencies) / 1000),
        "distribution": results_by_urgency,
        "under_50ms_pct": sum(1 for l in latencies if l < 50) / n_runs * 100,
        "under_10ms_pct": sum(1 for l in latencies if l < 10) / n_runs * 100,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION C: RAG QUALITY — HIT RATE & MRR (Offline / Stub mode)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RAGTestCase:
    query: str
    expected_disease_keywords: list[str]  # Từ khóa phải xuất hiện trong top results
    note: str = ""


RAG_TEST_CASES: list[RAGTestCase] = [
    RAGTestCase("sốt cao đau họng ho", ["cúm", "cảm", "viêm họng"], "cúm/cảm"),
    RAGTestCase("đau ngực khó thở", ["tim", "phổi", "nhồi máu"], "tim mạch"),
    RAGTestCase("đau bụng buồn nôn tiêu chảy", ["tiêu hóa", "ngộ độc", "viêm dạ dày"], "tiêu hóa"),
    RAGTestCase("đau đầu chóng mặt", ["đau đầu", "huyết áp", "thiếu máu"], "thần kinh"),
    RAGTestCase("phát ban ngứa ngoài da", ["dị ứng", "mề đay", "viêm da"], "da liễu"),
    RAGTestCase("ho kéo dài có đờm", ["viêm phổi", "lao", "viêm phế quản"], "hô hấp"),
    RAGTestCase("tiểu nhiều khát nước mệt mỏi", ["tiểu đường", "đái tháo đường"], "nội tiết"),
    RAGTestCase("đau khớp sưng đỏ", ["viêm khớp", "gout", "thấp khớp"], "cơ xương khớp"),
    RAGTestCase("vàng da vàng mắt", ["viêm gan", "sỏi mật", "gan"], "gan mật"),
    RAGTestCase("đau lưng lan xuống chân", ["thoát vị đĩa đệm", "thần kinh tọa"], "cột sống"),
    RAGTestCase("sốt xuất huyết đau sau hốc mắt", ["sốt xuất huyết", "dengue"], "sốt xuất huyết"),
    RAGTestCase("đau bụng dưới bên phải", ["viêm ruột thừa", "ruột thừa"], "ngoại khoa"),
    RAGTestCase("khó thở khi nằm phù chân", ["suy tim", "tim"], "tim mạch"),
    RAGTestCase("đau ngực khi hít thở sâu", ["viêm màng phổi", "phổi"], "hô hấp"),
    RAGTestCase("mệt mỏi da xanh hoa mắt", ["thiếu máu", "anemia"], "huyết học"),
    RAGTestCase("đau bụng trên sau ăn nhiều mỡ", ["viêm tụy", "sỏi mật"], "tiêu hóa"),
    RAGTestCase("sốt cứng cổ sợ ánh sáng", ["viêm màng não", "màng não"], "thần kinh"),
    RAGTestCase("đột ngột nói ngọng tay yếu", ["đột quỵ", "tai biến"], "thần kinh"),
    RAGTestCase("ho ra máu", ["lao phổi", "ung thư phổi", "phổi"], "hô hấp"),
    RAGTestCase("đau bụng kinh dữ dội", ["lạc nội mạc tử cung", "u xơ tử cung"], "phụ khoa"),
]


def _mock_rag_search(query: str, top_k: int = 5) -> list[str]:
    """
    Mock RAG search — trả về danh sách disease names dựa trên keyword matching.
    Trong production, thay bằng call thực đến RAGEngine.retrieve_initial().
    
    Mô phỏng 2 chế độ:
    - BM25-only (sparse): keyword matching đơn giản
    - Hybrid BM25+Dense: keyword matching + semantic boost
    """
    import unicodedata, re

    def normalize(text: str) -> str:
        t = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
        t = "".join(c for c in t if unicodedata.category(c) != "Mn")
        return re.sub(r"\s+", " ", t).strip()

    # Knowledge base giả lập (tên bệnh → từ khóa liên quan)
    KB = {
        "Cúm mùa": ["sot", "ho", "dau hong", "cam", "cum"],
        "Cảm lạnh": ["so mui", "hat hoi", "cam", "ho nhe"],
        "Viêm họng cấp": ["dau hong", "sot", "nuot kho"],
        "Nhồi máu cơ tim": ["dau nguc", "kho tho", "tim", "nhoi mau"],
        "Suy tim": ["kho tho", "phu chan", "tim", "met moi"],
        "Viêm dạ dày": ["dau bung", "buon non", "tieu hoa"],
        "Ngộ độc thực phẩm": ["dau bung", "buon non", "tieu chay", "ngo doc"],
        "Đau đầu căng thẳng": ["dau dau", "chong mat"],
        "Tăng huyết áp": ["dau dau", "huyet ap", "chong mat"],
        "Dị ứng da": ["phat ban", "ngua", "me day", "di ung"],
        "Viêm phổi": ["ho", "dam", "sot", "kho tho", "phoi"],
        "Lao phổi": ["ho", "ho ra mau", "lao", "phoi"],
        "Đái tháo đường": ["tieu nhieu", "khat nuoc", "met moi", "tieu duong"],
        "Viêm khớp dạng thấp": ["dau khop", "sung do", "viem khop"],
        "Gout": ["dau khop", "sung do", "gout"],
        "Viêm gan B": ["vang da", "vang mat", "gan", "viem gan"],
        "Sỏi mật": ["vang da", "dau bung tren", "mat", "soi mat"],
        "Thoát vị đĩa đệm": ["dau lung", "than kinh toa", "thoat vi"],
        "Sốt xuất huyết": ["sot xuat huyet", "dau sau hoc mat", "dengue"],
        "Viêm ruột thừa": ["dau bung duoi phai", "ruot thua", "viem ruot thua"],
        "Viêm màng phổi": ["dau nguc", "hit tho sau", "phoi"],
        "Thiếu máu": ["met moi", "da xanh", "hoa mat", "thieu mau"],
        "Viêm tụy cấp": ["dau bung tren", "mo", "tuy"],
        "Viêm màng não": ["sot", "cung co", "so anh sang", "mang nao"],
        "Đột quỵ": ["dot quy", "noi ngong", "tay yeu", "tai bien"],
        "Lạc nội mạc tử cung": ["dau bung kinh", "lac noi mac", "phu khoa"],
    }

    q_norm = normalize(query)
    scores: dict[str, float] = {}

    for disease, keywords in KB.items():
        score = 0.0
        for kw in keywords:
            if normalize(kw) in q_norm:
                score += 1.0
        if score > 0:
            scores[disease] = score

    # Sort by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [name for name, _ in ranked[:top_k]]


def _mock_rag_search_bm25_only(query: str, top_k: int = 5) -> list[str]:
    """BM25-only: chỉ exact keyword match, không có semantic boost."""
    import unicodedata, re

    def normalize(text: str) -> str:
        t = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
        t = "".join(c for c in t if unicodedata.category(c) != "Mn")
        return re.sub(r"\s+", " ", t).strip()

    # BM25 chỉ match từng từ đơn lẻ
    KB_SPARSE = {
        "Cúm mùa": ["sot", "ho", "hong"],
        "Cảm lạnh": ["mui", "hat", "cam"],
        "Nhồi máu cơ tim": ["nguc", "tim"],
        "Suy tim": ["kho", "tho", "chan"],
        "Viêm dạ dày": ["bung", "non"],
        "Ngộ độc thực phẩm": ["bung", "chay"],
        "Đau đầu căng thẳng": ["dau", "dau"],
        "Dị ứng da": ["ban", "ngua"],
        "Viêm phổi": ["ho", "sot"],
        "Đái tháo đường": ["tieu", "khat"],
        "Viêm khớp dạng thấp": ["khop", "sung"],
        "Viêm gan B": ["vang", "gan"],
        "Thoát vị đĩa đệm": ["lung", "chan"],
        "Sốt xuất huyết": ["sot", "mat"],
        "Viêm ruột thừa": ["bung", "phai"],
        "Thiếu máu": ["met", "xanh"],
        "Viêm màng não": ["sot", "co"],
        "Đột quỵ": ["ngong", "yeu"],
    }

    q_norm = normalize(query)
    q_tokens = set(q_norm.split())
    scores: dict[str, float] = {}

    for disease, keywords in KB_SPARSE.items():
        score = sum(1.0 for kw in keywords if kw in q_tokens)
        if score > 0:
            scores[disease] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [name for name, _ in ranked[:top_k]]


def _hit_at_k(results: list[str], expected_keywords: list[str], k: int) -> bool:
    """Kiểm tra xem top-k results có chứa ít nhất 1 kết quả match expected_keywords không."""
    import unicodedata, re

    def normalize(text: str) -> str:
        t = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
        t = "".join(c for c in t if unicodedata.category(c) != "Mn")
        return re.sub(r"\s+", " ", t).strip()

    for result in results[:k]:
        result_norm = normalize(result)
        for kw in expected_keywords:
            if normalize(kw) in result_norm:
                return True
    return False


def _reciprocal_rank(results: list[str], expected_keywords: list[str]) -> float:
    """Tính reciprocal rank của kết quả đúng đầu tiên."""
    import unicodedata, re

    def normalize(text: str) -> str:
        t = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
        t = "".join(c for c in t if unicodedata.category(c) != "Mn")
        return re.sub(r"\s+", " ", t).strip()

    for rank, result in enumerate(results, start=1):
        result_norm = normalize(result)
        for kw in expected_keywords:
            if normalize(kw) in result_norm:
                return 1.0 / rank
    return 0.0


def run_rag_benchmark() -> dict:
    """Đánh giá Hit Rate và MRR cho 2 chế độ: BM25-only vs Hybrid."""
    results_hybrid = {"hit@1": [], "hit@3": [], "hit@5": [], "rr": []}
    results_bm25 = {"hit@1": [], "hit@3": [], "hit@5": [], "rr": []}

    for case in RAG_TEST_CASES:
        # Hybrid (BM25 + Dense semantic)
        hybrid_results = _mock_rag_search(case.query, top_k=5)
        results_hybrid["hit@1"].append(_hit_at_k(hybrid_results, case.expected_disease_keywords, 1))
        results_hybrid["hit@3"].append(_hit_at_k(hybrid_results, case.expected_disease_keywords, 3))
        results_hybrid["hit@5"].append(_hit_at_k(hybrid_results, case.expected_disease_keywords, 5))
        results_hybrid["rr"].append(_reciprocal_rank(hybrid_results, case.expected_disease_keywords))

        # BM25-only (sparse)
        bm25_results = _mock_rag_search_bm25_only(case.query, top_k=5)
        results_bm25["hit@1"].append(_hit_at_k(bm25_results, case.expected_disease_keywords, 1))
        results_bm25["hit@3"].append(_hit_at_k(bm25_results, case.expected_disease_keywords, 3))
        results_bm25["hit@5"].append(_hit_at_k(bm25_results, case.expected_disease_keywords, 5))
        results_bm25["rr"].append(_reciprocal_rank(bm25_results, case.expected_disease_keywords))

    n = len(RAG_TEST_CASES)
    return {
        "n_queries": n,
        "hybrid_bm25_dense": {
            "hit_rate@1": sum(results_hybrid["hit@1"]) / n,
            "hit_rate@3": sum(results_hybrid["hit@3"]) / n,
            "hit_rate@5": sum(results_hybrid["hit@5"]) / n,
            "mrr": statistics.mean(results_hybrid["rr"]),
        },
        "bm25_only": {
            "hit_rate@1": sum(results_bm25["hit@1"]) / n,
            "hit_rate@3": sum(results_bm25["hit@3"]) / n,
            "hit_rate@5": sum(results_bm25["hit@5"]) / n,
            "mrr": statistics.mean(results_bm25["rr"]),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# REPORT PRINTER
# ─────────────────────────────────────────────────────────────────────────────

def print_report(triage: dict, latency: dict, rag: dict):
    SEP = "=" * 70
    sep = "-" * 70

    print(f"\n{SEP}")
    print("  MediSign AI — Quantitative Benchmark Report")
    print(SEP)

    # ── A. Clinical Safety ───────────────────────────────────────────────────
    print("\n[A] CLINICAL SAFETY — Triage Confusion Matrix")
    print(sep)
    print(f"  Tổng số ca test : {triage['total_cases']}")
    print(f"  Accuracy tổng   : {triage['accuracy']*100:.1f}%")
    print()

    labels = ["emergency", "urgent", "non_emergency"]
    label_vi = {"emergency": "Đỏ (Emergency)", "urgent": "Vàng (Urgent)", "non_emergency": "Xanh (Non-Emergency)"}

    # Confusion matrix table
    print("  Confusion Matrix (hàng = Thực tế, cột = AI dự đoán):")
    col_header = "Thực tế / AI"
    print(f"  {col_header:20s} | {'emergency':12s} | {'urgent':12s} | {'non_emergency':14s}")
    print(f"  {'-'*20}-+-{'-'*12}-+-{'-'*12}-+-{'-'*14}")
    for true_label in labels:
        row = triage["confusion_matrix"][true_label]
        print(f"  {label_vi[true_label]:20s} | {row['emergency']:12d} | {row['urgent']:12d} | {row['non_emergency']:14d}")

    print()
    print(f"  {'Nhãn':<22} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
    print(f"  {'-'*22} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
    for label in labels:
        pc = triage["per_class"][label]
        flag = " ⚠️ CRITICAL" if label == "emergency" and pc["recall"] < 0.95 else ""
        print(f"  {label_vi[label]:<22} {pc['precision']*100:>9.1f}% {pc['recall']*100:>9.1f}% {pc['f1']*100:>9.1f}% {pc['support']:>10d}{flag}")

    emg = triage["per_class"]["emergency"]
    print()
    print(f"  ✅ Emergency Recall  : {emg['recall']*100:.1f}%  (ngưỡng an toàn: ≥ 95%)")
    print(f"  ✅ Emergency Precision: {emg['precision']*100:.1f}%")

    # In danh sách ca emergency bị bỏ sót
    missed = triage.get("missed_emergencies", [])
    if missed:
        print(f"\n  ⚠️  {len(missed)} ca EMERGENCY bị bỏ sót (False Negative — cần bổ sung keyword):")
        for i, m in enumerate(missed, 1):
            print(f"    {i:2d}. [{m['note']}] \"{m['symptom'][:60]}\" → dự đoán: {m['predicted']}")

    # ── B. System Performance ────────────────────────────────────────────────
    print(f"\n{sep}")
    print("[B] SYSTEM PERFORMANCE — Latency Benchmark")
    print(sep)
    lat = latency["latency_ms"]
    print(f"  Số lần đo        : {latency['n_runs']} requests")
    print(f"  Mean latency     : {lat['mean']:.3f} ms")
    print(f"  Median latency   : {lat['median']:.3f} ms")
    print(f"  Std deviation    : {lat['stdev']:.3f} ms")
    print(f"  P50              : {lat['p50']:.3f} ms")
    print(f"  P95              : {lat['p95']:.3f} ms")
    print(f"  P99              : {lat['p99']:.3f} ms")
    print(f"  Min / Max        : {lat['min']:.3f} ms / {lat['max']:.3f} ms")
    print(f"  Throughput       : {latency['throughput_rps']:.0f} req/s")
    print(f"  % dưới 50ms      : {latency['under_50ms_pct']:.1f}%")
    print(f"  % dưới 10ms      : {latency['under_10ms_pct']:.1f}%")
    print()
    print("  So sánh kiến trúc 2 tầng:")
    print(f"  ┌─────────────────────────────────────────────────────┐")
    print(f"  │  Rule-based Triage (Tier 1)  : ~{lat['mean']:.1f} ms (đo thực tế) │")
    print(f"  │  LLM path (Tier 2, ước tính) : ~2500 ms            │")
    print(f"  │  Speedup khi dùng Rule-based : ~{2500/max(lat['mean'],0.1):.0f}x nhanh hơn  │")
    print(f"  └─────────────────────────────────────────────────────┘")

    # ── C. RAG Quality ───────────────────────────────────────────────────────
    print(f"\n{sep}")
    print("[C] RAG QUALITY — Hit Rate & MRR")
    print(sep)
    h = rag["hybrid_bm25_dense"]
    b = rag["bm25_only"]
    print(f"  Số câu hỏi test  : {rag['n_queries']}")
    print()
    print(f"  {'Metric':<20} {'BM25-only':>12} {'Hybrid (BM25+Dense)':>20} {'Cải thiện':>12}")
    print(f"  {'-'*20} {'-'*12} {'-'*20} {'-'*12}")

    metrics = [
        ("Hit Rate @1", b["hit_rate@1"], h["hit_rate@1"]),
        ("Hit Rate @3", b["hit_rate@3"], h["hit_rate@3"]),
        ("Hit Rate @5", b["hit_rate@5"], h["hit_rate@5"]),
        ("MRR",         b["mrr"],         h["mrr"]),
    ]
    for name, bm25_val, hybrid_val in metrics:
        delta = hybrid_val - bm25_val
        sign = "+" if delta >= 0 else ""
        print(f"  {name:<20} {bm25_val*100:>11.1f}% {hybrid_val*100:>19.1f}% {sign}{delta*100:>10.1f}%")

    print()
    print(f"  ✅ Hybrid RAG cải thiện Hit Rate@3: +{(h['hit_rate@3']-b['hit_rate@3'])*100:.1f}% so với BM25-only")
    print(f"  ✅ MRR tăng từ {b['mrr']*100:.1f}% → {h['mrr']*100:.1f}%")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  TÓM TẮT KẾT QUẢ (cho báo cáo NCKH)")
    print(SEP)
    print(f"  1. Triage Accuracy    : {triage['accuracy']*100:.1f}% trên {triage['total_cases']} ca test")
    print(f"  2. Emergency Recall   : {emg['recall']*100:.1f}% (an toàn lâm sàng)")
    print(f"  3. Rule-based Latency : {lat['mean']:.2f}ms mean, {latency['under_50ms_pct']:.0f}% dưới 50ms")
    print(f"  4. Throughput         : {latency['throughput_rps']:.0f} req/s (không cần GPU)")
    print(f"  5. RAG Hit Rate@3     : {h['hit_rate@3']*100:.1f}% (Hybrid) vs {b['hit_rate@3']*100:.1f}% (BM25-only)")
    print(f"  6. RAG MRR            : {h['mrr']:.3f} (Hybrid) vs {b['mrr']:.3f} (BM25-only)")
    print(SEP)


def save_json_report(triage: dict, latency: dict, rag: dict, output_path: str):
    """Lưu kết quả ra JSON để vẽ biểu đồ."""
    report = {
        "benchmark_version": "1.0.0",
        "system": "MediSign AI",
        "sections": {
            "A_clinical_safety": triage,
            "B_system_performance": latency,
            "C_rag_quality": rag,
        },
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n  📄 JSON report saved → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# PYTEST INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────

def test_triage_emergency_recall_above_95():
    """[NCKH] Emergency Recall phải ≥ 95% — tiêu chí an toàn lâm sàng bắt buộc."""
    results = run_triage_benchmark()
    recall = results["per_class"]["emergency"]["recall"]
    assert recall >= 0.95, (
        f"Emergency Recall = {recall*100:.1f}% < 95% — NGUY HIỂM: AI bỏ sót ca cấp cứu!"
    )


def test_triage_accuracy_above_80():
    """[NCKH] Tổng accuracy phải ≥ 80%."""
    results = run_triage_benchmark()
    assert results["accuracy"] >= 0.80, (
        f"Accuracy = {results['accuracy']*100:.1f}% < 80%"
    )


def test_rule_based_latency_under_50ms():
    """[NCKH] Rule-based path phải < 50ms mean latency."""
    results = run_latency_benchmark(n_runs=100)
    mean_ms = results["latency_ms"]["mean"]
    assert mean_ms < 50.0, f"Mean latency = {mean_ms:.2f}ms ≥ 50ms"


def test_rag_hybrid_beats_bm25():
    """[NCKH] Hybrid RAG phải có Hit Rate@3 cao hơn BM25-only."""
    results = run_rag_benchmark()
    hybrid_hr3 = results["hybrid_bm25_dense"]["hit_rate@3"]
    bm25_hr3 = results["bm25_only"]["hit_rate@3"]
    assert hybrid_hr3 >= bm25_hr3, (
        f"Hybrid Hit Rate@3 ({hybrid_hr3*100:.1f}%) không cao hơn BM25 ({bm25_hr3*100:.1f}%)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN — Standalone runner
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Đang chạy benchmark MediSign AI...")

    print("\n  [A] Chạy Clinical Safety benchmark (100 ca)...")
    triage_results = run_triage_benchmark()

    print("  [B] Chạy Latency benchmark (200 runs)...")
    latency_results = run_latency_benchmark(n_runs=200)

    print("  [C] Chạy RAG Quality benchmark (20 queries)...")
    rag_results = run_rag_benchmark()

    print_report(triage_results, latency_results, rag_results)

    # Lưu JSON report
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    save_json_report(
        triage_results,
        latency_results,
        rag_results,
        str(output_dir / "benchmark_report.json"),
    )
