---
name: "Flutter: Find Related Bugs"
description: Quy trinh tim nhanh cac phan code lien quan den loi de khoanh vung dung
category: Workflow
tags: [flutter, bug, search, triage]
---

# Flutter: Find Related Bugs

Workflow nay dung de tim dung vung loi truoc khi vao sua.

## Input

- Loi/exception dang gap
- Tu khoa tu log (vi du: RenderFlex overflow, setState after dispose)
- Man hinh/chuc nang gap loi

## Steps

1. Xac dinh keyword tim kiem
   - Ten widget, exception, service, endpoint, state class.
2. Tim trong codebase
   - Tim theo keyword exception.
   - Tim theo widget/man hinh lien quan.
   - Tim theo luong data tu API -> state -> UI.
3. Lap danh sach diem nghiem trong
   - Cac file co kha nang gay loi cao.
   - Cac file co thay doi gan day (neu co).
4. Kiem tra luong lien quan
   - lifecycle (`initState`, `dispose`, async callback)
   - state update sau khi widget bi huy
   - null/empty/loading states
5. Chot 1-2 gia thuyet nguyen nhan goc
   - Khong sua ngay khi chua co gia thuyet ro rang.
6. Ban giao sang workflow fix bug
   - Chuyen tiep qua `flutter-bug-fix-assurance.md` de sua va xac nhan.

## Output

- Danh sach file lien quan + gia thuyet nguyen nhan goc uu tien.
