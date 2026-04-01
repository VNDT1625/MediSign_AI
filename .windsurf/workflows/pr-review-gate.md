---
name: "PR: Review Gate"
description: Cong gate truoc merge de chan loi rot va dam bao chat luong
category: Workflow
tags: [pr, review, quality, gate]
---

# PR: Review Gate

Workflow nay dung truoc merge cho moi PR.

## Steps

1. Kiem tra mo ta PR theo mau bat buoc trong `note.md`.
2. Kiem tra root cause ro rang (neu la bug fix).
3. Kiem tra test added + bang chung Red -> Green.
4. Kiem tra regression va flaky guard.
5. Kiem tra impact:
   - API contract co doi khong?
   - DB schema co doi khong?
   - UI co anh huong overflow/accessibility khong?
6. Kiem tra tai lieu:
   - `status.md` da cap nhat
   - `learn.md` da cap nhat neu co bai hoc moi
   - `note.md` cap nhat rui ro neu can
7. Chi merge khi tat ca muc deu pass.

## Merge blocked neu

- Thieu root cause
- Khong co Red -> Green cho bug fix
- Flaky chua xu ly
- CI fail
