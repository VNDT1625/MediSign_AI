---
name: "Flutter: Add Feature Workflow"
description: Quy trinh them tinh nang moi tu spec den test va merge
category: Workflow
tags: [flutter, feature, workflow]
---

# Flutter: Add Feature Workflow

Quy trinh them tinh nang moi de tranh thieu buoc va tang toc phoi hop nhieu AI.

## Steps

1. Chot pham vi tinh nang (input/output, UI, API, test).
2. Tach task cho AI:
   - UI (Antigravity)
   - Backend/API (Kiro/Cursor)
   - Bug reasoning (ChatGPT Codex)
   - Integration/review (Windsurf)
3. Tao branch va implement theo tung lop:
   - model -> repository/service -> state -> UI
4. Chay lint + test truoc khi merge.
5. Review contract API va anh huong nguoc.
6. Cap nhat tai lieu co dinh:
   - `status.md`, `project.md`, `note.md`, `learn.md` (neu can)
7. Merge khi dat checklist release.

## Output

- Tinh nang moi day du code + test + cap nhat tai lieu.
