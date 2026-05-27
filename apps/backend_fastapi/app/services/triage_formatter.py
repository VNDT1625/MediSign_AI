from __future__ import annotations

from app.schemas.diagnostic import ConclusionEvidence, DiagnosticState, RankedDisease, TriageLevel


DISCLAIMER = "⚠️ Tôi không thể thay thế bác sĩ."


class TriageFormatter:
    def assign_triage_level(self, diseases_ranked: list[RankedDisease]) -> TriageLevel:
        if any(d.severity == "high" and d.probability >= 0.30 for d in diseases_ranked):
            return "red"

        top = max(diseases_ranked, key=lambda d: d.probability, default=None)
        if top is None or top.probability < 0.50:
            return "yellow"

        if any(d.severity == "medium" and d.probability >= 0.50 for d in diseases_ranked):
            return "yellow"

        if top.severity == "low" and top.probability >= 0.60:
            return "green"

        return "yellow"

    def ensure_disclaimer(self, content: str) -> str:
        if DISCLAIMER in content:
            return content
        return f"{content}\n{DISCLAIMER}"

    def render_partial(self, state: DiagnosticState) -> str:
        if not state.diseases_ranked:
            return "Mình cần thêm thông tin để phân tích triệu chứng hiện tại."

        lines = ["Các khả năng đang được cân nhắc:"]
        for disease in state.diseases_ranked:
            probability = round(disease.probability * 100)
            rationale = f" - {disease.rationale}" if disease.rationale else ""
            lines.append(f"- {disease.name}: {probability}%{rationale}")
        return "\n".join(lines)

    def render_final(self, state: DiagnosticState, evidence: ConclusionEvidence) -> str:
        triage = state.triage_level or self.assign_triage_level(state.diseases_ranked)
        top = state.diseases_ranked[0].name if state.diseases_ranked else evidence.disease_name
        lines = [
            "Kết luận:",
            f"- Khả năng phù hợp nhất: {top}",
            f"- Mức ưu tiên: {triage}",
        ]

        recommendations = evidence.recommendations or evidence.home_care
        if recommendations:
            lines.append("- Khuyến nghị:")
            lines.extend(f"  - {item}" for item in recommendations)
        if evidence.lab_tests:
            lines.append("- Xét nghiệm/khám nên cân nhắc:")
            lines.extend(f"  - {item}" for item in evidence.lab_tests)
        if evidence.red_flags:
            lines.append("- Dấu hiệu cần đi khám khẩn:")
            lines.extend(f"  - {item}" for item in evidence.red_flags)

        return self.ensure_disclaimer("\n".join(lines))

    def render_needs_test(self, state: DiagnosticState) -> str:
        summary = self.render_partial(state)
        content = (
            f"{summary}\n"
            "Các thông tin hiện tại chưa đủ để kết luận an toàn. "
            "Bạn nên đặt lịch khám hoặc làm xét nghiệm theo tư vấn của nhân viên y tế."
        )
        return self.ensure_disclaimer(content)
