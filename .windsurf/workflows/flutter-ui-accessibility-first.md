---
name: "Flutter: UI Accessibility-First"
description: Workflow tao UI de dung voi nguoi cham cong nghe va nguoi khuyet tat, bat buoc sketch truoc khi code
category: Workflow
tags: [flutter, ui, accessibility, ux]
---

# Flutter: UI Accessibility-First

Workflow nay dat uu tien su de hieu, de su dung, va kha nang truy cap.

## Input

- Muc tieu man hinh
- Doi tuong nguoi dung (nguoi moi, nguoi cao tuoi, nguoi co han che thi luc/van dong)
- Luong chinh can hoan thanh

## Steps

1. Tao mockup bang Pencil AI truoc khi code (bat buoc)
   - Mo ta man hinh cho Pencil AI: muc tieu, doi tuong nguoi dung, hanh dong chinh.
   - Xuat 1-2 phuong an giao dien (lo-fi).
   - Chon 1 phuong an de review voi team.
2. Sketch bo sung neu can
   - Ve nhanh tay/whiteboard/Figma wireframe o muc thap.
   - Danh dau ro: tieu de, nut chinh, nut phu, vung canh bao, trang thai loi.
   - Chot voi team truoc khi viet code UI.
3. Viet UI spec ngan gon
   - Muc tieu cua man hinh trong 1 cau.
   - 3 tac vu chinh nguoi dung phai lam duoc trong <= 3 buoc.
   - Dinh nghia state: loading, empty, error, success.
4. Nguyen tac de dung voi nguoi cham cong nghe
   - Uu tien 1 hanh dong chinh moi man hinh.
   - Ngon ngu don gian, tranh thuat ngu ky thuat.
   - Nut to, de bam, co nhan ro rang.
   - Luong don gian, tranh qua nhieu lua chon cung luc.
5. Nguyen tac accessibility (A11y)
   - Text co do tuong phan cao, co the doc ro trong anh sang kem.
   - Co semantic labels cho thanh phan quan trong.
   - Ho tro font scale lon (khong vo layout).
   - Focus order hop ly cho ban phim/doc man hinh.
   - Khong chi dung mau sac de truyen dat thong tin.
6. Code UI theo component
   - Tach component nho, tai su dung duoc.
   - Uu tien `LayoutBuilder`, `Flexible`, `Expanded`, `Wrap`.
   - Tren mobile nho, co the cuon duoc khi noi dung dai.
7. Test bat buoc
   - Widget test render duoc state chinh.
   - Test voi textScaleFactor lon.
   - Test khong overflow tren man hinh nho.
   - Test luong chinh hoan thanh duoc boi nguoi moi.
8. Xac nhan voi checklist truoc merge
   - Da co mockup Pencil AI + UI spec.
   - Da qua `flutter-ui-overflow.md` neu man hinh phuc tap.
   - Da qua `flutter-test-assurance.md` neu sua bug UI.

## Rubric danh gia UI cho Antigravity (thang diem 10)

Cham moi muc 0-2 diem:

1. Do ro rang voi nguoi cham cong nghe
   - 0: Kho hieu, nhieu thuat ngu.
   - 1: Tam duoc, van can huong dan.
   - 2: De hieu ngay, khong can giai thich nhieu.
2. De thao tac
   - 0: Qua nhieu lua chon, luong roi.
   - 1: Lam duoc nhung con loanh quanh.
   - 2: Luong ngan, hanh dong chinh ro rang.
3. Accessibility co ban
   - 0: Thieu semantic/focus/contrast.
   - 1: Co mot phan.
   - 2: Dat day du semantic + contrast + focus.
4. Do ben layout
   - 0: Co overflow tren man hinh nho/font lon.
   - 1: It loi nho.
   - 2: Khong overflow tren cac context da test.
5. Tin hieu trang thai
   - 0: Loading/error/empty khong ro.
   - 1: Co nhung chua than thien.
   - 2: Trang thai day du, thong diep ro rang.

Tong diem:

- 9-10: Tot, co the code ngay.
- 7-8: Chinh nhe roi code.
- <=6: Lam lai mockup Pencil AI truoc khi code.

## Done khi

- Nguoi dung moi co the hoan thanh tac vu chinh ma khong can huong dan dai.
- UI khong overflow voi font lon/man hinh nho.
- Co test cho state chinh va A11y co ban.
