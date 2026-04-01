---
name: "Flutter: Build Component"
description: Tao component UI tai su dung duoc, co test va tai lieu toi thieu
category: Workflow
tags: [flutter, component, ui]
---

# Flutter: Build Component

Tao component Flutter theo chuan team, de tai su dung va giam loi UI.

## Input

Ten component, muc dich, state (loading/error/empty/success).

## Steps

1. Sketch/wireframe nhanh truoc khi code (bat buoc).
   - Co the dung giay, whiteboard, hoac Figma lo-fi.
   - Chot bo cuc + hanh dong chinh truoc khi viet code.
2. Tao file component trong `lib/shared/widgets/` hoac `lib/features/<feature>/widgets/`.
3. Dat API props ro rang (required/optional, callback, style).
4. Ho tro day du cac state can thiet (loading, empty, error neu co).
5. Dam bao responsive:
   - khong hard-code width/height vo ly
   - uu tien `LayoutBuilder`, `Flexible`, `Expanded`
6. Viet widget test co ban:
   - render duoc
   - callback duoc goi
   - state chinh hien dung
7. Neu UI huong toi nguoi cham cong nghe/nguoi khuyet tat, bat buoc chay them workflow `flutter-ui-accessibility-first.md`.
8. Cap nhat `status.md` va `learn.md` neu co bai hoc moi.

## Output

- Component san sang tai su dung + test co ban pass.
