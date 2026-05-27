import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

FIG_DIR = Path(r"C:\NDT\PJ\MediSign_AI - Copy\report_build\figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False


def box(ax, xy, w, h, text, color="#E3F2FD", edge="#1565C0", fontsize=9, weight="normal"):
    x, y = xy
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                       linewidth=1.2, edgecolor=edge, facecolor=color)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, weight=weight, wrap=True)


def arrow(ax, src, dst, color="#37474F", style="-|>", lw=1.2):
    a = FancyArrowPatch(src, dst, arrowstyle=style, mutation_scale=12,
                         linewidth=lw, color=color)
    ax.add_patch(a)


# === Figure 3.1 — Architecture overview ===========================
fig, ax = plt.subplots(figsize=(11, 7.5))
ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis("off")
ax.set_title("Hinh 3.1 — Kien truc tong the MediSign AI",
             fontsize=12, weight="bold", pad=14)

# Client tier
box(ax, (0.4, 6.4), 3.4, 1.1, "Flutter Mobile App\n(14 modules, 40.4k LOC)",
    color="#FFF3E0", edge="#E65100", weight="bold")
box(ax, (4.3, 6.4), 3.4, 1.1, "Next.js 14 Web App\n(143 files, 28.4k LOC)",
    color="#FFF3E0", edge="#E65100", weight="bold")
box(ax, (8.2, 6.4), 3.4, 1.1, "3D Avatar / Sign UI\n(VSL + Voice + Tap + Text)",
    color="#FFF3E0", edge="#E65100", weight="bold")

# API gateway
box(ax, (3.5, 4.7), 5.0, 1.0,
    "FastAPI Backend (Python 3.11)\n80 endpoints • JWT • PBKDF2 • CORS",
    color="#E8F5E9", edge="#1B5E20", weight="bold")

# Service layer
box(ax, (0.3, 2.9), 2.6, 1.2,
    "Triage Service\n3 muc Xanh/Vang/Do\nRule-based + LLM",
    color="#E1F5FE", edge="#0277BD")
box(ax, (3.05, 2.9), 2.6, 1.2,
    "RAG Engine\nBM25 + Dense\nRRF + LazyLoader",
    color="#E1F5FE", edge="#0277BD")
box(ax, (5.8, 2.9), 2.6, 1.2,
    "Drug Lookup\nDAV 60.472 thuoc\n67.493 tuong tac",
    color="#E1F5FE", edge="#0277BD")
box(ax, (8.55, 2.9), 3.1, 1.2,
    "Medicine Vision\nOCR + Image\nClassifier",
    color="#E1F5FE", edge="#0277BD")

# AI runtime
box(ax, (1.0, 1.0), 4.5, 1.2,
    "MedGemma 1.5 4B Runtime (GPU rieng)\n+ LoRA Medical adapter\n+ LoRA Psychology adapter",
    color="#F3E5F5", edge="#4A148C", weight="bold")

# Data
box(ax, (6.5, 1.0), 5.1, 1.2,
    "PostgreSQL 16 (23 bang)\nKnowledge Base 128.380 records\nDual-adapter dataset 19.876 mau",
    color="#FCE4EC", edge="#880E4F", weight="bold")

# Arrows
for sx in [2.1, 6.0, 9.9]:
    arrow(ax, (sx, 6.4), (sx, 5.7))
arrow(ax, (6.0, 4.7), (1.6, 4.1))
arrow(ax, (6.0, 4.7), (4.35, 4.1))
arrow(ax, (6.0, 4.7), (7.1, 4.1))
arrow(ax, (6.0, 4.7), (10.1, 4.1))
arrow(ax, (4.35, 2.9), (3.25, 2.2))
arrow(ax, (4.35, 2.9), (9.0, 2.2))
arrow(ax, (7.1, 2.9), (9.0, 2.2))
arrow(ax, (1.6, 2.9), (3.25, 2.2))

plt.savefig(FIG_DIR / "fig_3_1_architecture.png", dpi=180, bbox_inches="tight")
plt.close()


# === Figure 3.2 — RAG hybrid pipeline =============================
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.set_xlim(0, 12); ax.set_ylim(0, 6); ax.axis("off")
ax.set_title("Hinh 3.2 — RAG-MediSign: BM25 + Dense + RRF + LazyLoader",
             fontsize=12, weight="bold", pad=12)

box(ax, (0.2, 2.4), 1.9, 1.1, "Cau hoi\nnguoi dung",
    color="#FFF3E0", edge="#E65100", weight="bold")
box(ax, (2.4, 2.4), 1.9, 1.1, "Query rewrite\n+ MEDICAL_\nSYNONYMS",
    color="#FFFDE7", edge="#F9A825")

box(ax, (4.6, 4.0), 2.3, 1.0, "BM25 Sparse\n128k records",
    color="#E1F5FE", edge="#0277BD")
box(ax, (4.6, 0.9), 2.3, 1.0, "Dense Embedding\nsentence-transformers",
    color="#E1F5FE", edge="#0277BD")

box(ax, (7.4, 2.4), 1.9, 1.1, "RRF Fusion\n(k = 60)",
    color="#E8F5E9", edge="#1B5E20", weight="bold")

box(ax, (9.6, 2.4), 2.2, 1.1,
    "MedGemma 4B\n+ LoRA adapter\nstructured JSON",
    color="#F3E5F5", edge="#4A148C", weight="bold")

box(ax, (4.6, 2.4), 2.3, 1.0, "KBLazyLoader\nfallback khi score < nguong",
    color="#FCE4EC", edge="#880E4F", fontsize=8)

arrow(ax, (2.1, 2.95), (2.4, 2.95))
arrow(ax, (4.3, 2.95), (4.6, 4.5))
arrow(ax, (4.3, 2.95), (4.6, 1.4))
arrow(ax, (4.3, 2.95), (4.6, 2.9))
arrow(ax, (6.9, 4.5), (7.6, 3.5))
arrow(ax, (6.9, 1.4), (7.6, 2.4))
arrow(ax, (6.9, 2.9), (7.4, 2.95))
arrow(ax, (9.3, 2.95), (9.6, 2.95))

plt.savefig(FIG_DIR / "fig_3_2_rag_pipeline.png", dpi=180, bbox_inches="tight")
plt.close()


# === Figure 3.3 — Triage 3 levels =================================
fig, ax = plt.subplots(figsize=(10, 4.0))
ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
ax.set_title("Hinh 3.3 — Logic Triage 3 muc khan cap (Xanh / Vang / Do)",
             fontsize=12, weight="bold", pad=10)

box(ax, (0.5, 1.3), 2.4, 1.2,
    "MUC XANH\nTu cham soc tai nha\n24-48h theo doi",
    color="#C8E6C9", edge="#2E7D32", weight="bold")
box(ax, (3.5, 1.3), 2.4, 1.2,
    "MUC VANG\nKham trong 24-48h\nKhong tu y dung thuoc",
    color="#FFF59D", edge="#F57F17", weight="bold")
box(ax, (6.5, 1.3), 2.4, 1.2,
    "MUC DO\nGoi 115 / di vien NGAY\nBypass AI",
    color="#FFCDD2", edge="#B71C1C", weight="bold")

ax.text(5.0, 3.4,
        "Tang 1: Rule-based detect emergency keyword (kho tho, dau nguc, ngat...)\n"
        "Tang 2: MedGemma + RAG cho cac case khong ro rang",
        ha="center", va="center", fontsize=9, style="italic")
plt.savefig(FIG_DIR / "fig_3_3_triage.png", dpi=180, bbox_inches="tight")
plt.close()


# === Figure 3.4 — ERD simplified ==================================
fig, ax = plt.subplots(figsize=(11, 7.2))
ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis("off")
ax.set_title("Hinh 3.4 — So do ERD rut gon (23 bang)",
             fontsize=12, weight="bold", pad=10)

tables_cloud = [
    ("users", 0.3, 6.5),
    ("user_sessions", 2.6, 6.5),
    ("password_resets", 4.9, 6.5),
    ("email_verifications", 7.2, 6.5),
    ("medicine_registry", 9.5, 6.5),
    ("hospitals", 0.3, 4.9),
    ("family_connections", 2.6, 4.9),
    ("triage_history", 4.9, 4.9),
    ("community_posts", 7.2, 4.9),
    ("post_comments", 9.5, 4.9),
    ("post_likes", 0.3, 3.3),
    ("workout_sessions", 2.6, 3.3),
    ("fitness_goals", 4.9, 3.3),
    ("chat_conversations", 7.2, 3.3),
    ("chat_messages", 9.5, 3.3),
    ("kb_pending_records", 0.3, 1.7),
    ("diagnosis_feedback", 2.6, 1.7),
    ("weight_update_proposals", 4.9, 1.7),
    ("disease_symptom_edges", 7.2, 1.7),
]
for name, x, y in tables_cloud:
    box(ax, (x, y), 2.1, 0.85, name, color="#E3F2FD", edge="#1565C0", fontsize=8)

# local
ax.text(6.0, 0.95, "Local SQLite (4 bang): daily_journals - user_profiles - my_medicines - dose_logs",
        ha="center", va="center", fontsize=9, style="italic", weight="bold",
        color="#4A148C",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#F3E5F5", edgecolor="#4A148C"))

plt.savefig(FIG_DIR / "fig_3_4_erd.png", dpi=180, bbox_inches="tight")
plt.close()


# === Figure 4.1 — LOC distribution ================================
fig, ax = plt.subplots(figsize=(8, 4.5))
labels = ["Python (backend + AI)", "Dart (Flutter app)",
          "TypeScript/TSX (Next.js + shared contracts)"]
values = [44434, 40360, 28689]
colors = ["#1B5E20", "#0277BD", "#E65100"]
bars = ax.barh(labels, values, color=colors)
for b, v in zip(bars, values):
    ax.text(v + 600, b.get_y() + b.get_height() / 2, f"{v:,}".replace(",", "."),
            va="center", fontsize=10, weight="bold")
ax.set_xlabel("So dong code (LOC)")
ax.set_title("Hinh 4.1 — Phan bo so dong code theo ngon ngu",
             fontsize=11, weight="bold")
ax.invert_yaxis()
ax.grid(axis="x", linestyle=":", alpha=0.5)
ax.set_xlim(0, 50000)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig_4_1_loc.png", dpi=180, bbox_inches="tight")
plt.close()


# === Figure 4.2 — Knowledge base composition ======================
fig, ax = plt.subplots(figsize=(7.5, 5))
labels = ["Drug interactions\n67.493", "Drugs (DAV)\n60.472",
          "Guideline chunks\n356", "Diseases VN\n10",
          "Symptom phrases\n11", "Nutrition\n38"]
sizes = [67493, 60472, 356, 10, 11, 38]
colors = ["#1565C0", "#2E7D32", "#E65100", "#6A1B9A", "#00838F", "#AD1457"]
ax.pie(sizes, labels=labels, colors=colors, startangle=90,
       wedgeprops=dict(linewidth=1, edgecolor="white"),
       textprops=dict(fontsize=8))
ax.set_title("Hinh 4.2 — Co cau Knowledge Base (128.380 records)",
             fontsize=11, weight="bold")
plt.tight_layout()
plt.savefig(FIG_DIR / "fig_4_2_kb.png", dpi=180, bbox_inches="tight")
plt.close()


# === Figure 4.3 — Crawl coverage ==================================
fig, ax = plt.subplots(figsize=(8, 4.5))
sources = ["Vinmec\n(2.348 bai)", "HelloBacsi\n(1.391 bai)",
           "Trung lap\n(35 benh)", "Sau dedup\n(3.248 benh)"]
values = [2348, 1391, 35, 3248]
colors = ["#0277BD", "#2E7D32", "#C62828", "#6A1B9A"]
bars = ax.bar(sources, values, color=colors)
for b, v in zip(bars, values):
    ax.text(b.get_x() + b.get_width() / 2, v + 60, f"{v:,}".replace(",", "."),
            ha="center", fontsize=10, weight="bold")
ax.set_ylabel("So benh / bai viet")
ax.set_title("Hinh 4.3 — Tap dieu Vinmec + HelloBacsi sau hop nhat",
             fontsize=11, weight="bold")
ax.set_ylim(0, max(values) * 1.18)
ax.grid(axis="y", linestyle=":", alpha=0.5)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig_4_3_disease_dedup.png", dpi=180, bbox_inches="tight")
plt.close()

print("All figures saved to:", FIG_DIR)
