---
name: "Flutter: UI Overflow Guard"
description: Kiem tra va xu ly tran layout (RenderFlex overflow) theo quy trinh nhanh
category: Workflow
tags: [flutter, ui, overflow, debug]
---

# Flutter: UI Overflow Guard

Workflow chuan de tranh va sua loi overflow tren mobile/tablet.

## Steps

1. Tai hien tren nhieu kich thuoc man hinh:
   - nho, vua, lon
   - portrait va landscape
2. Kiem tra vi tri gay tran:
   - `Row/Column` khong co `Flexible/Expanded`
   - text qua dai, button qua nhieu
3. Cac cach fix uu tien:
   - dung `Expanded/Flexible`
   - boc bang `SingleChildScrollView` neu noi dung dai
   - gioi han text (`maxLines`, `overflow: TextOverflow.ellipsis`)
   - dung `Wrap` thay `Row` khi danh sach ngang dai
4. Test lai voi font scale lon (nguoi gia):
   - dam bao van khong tran
5. Them test UI smoke cho man hinh da fix.
6. Ghi kinh nghiem vao `learn.md`.

## Output

- Man hinh khong con overflow trong cac context da test.
