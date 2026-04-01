---
name: "Flutter: Bug Fix Assurance"
description: Quy trinh tim nguyen nhan va xac nhan loi da duoc khac phuc, tranh tai phat
category: Workflow
tags: [flutter, bugfix, debugging, regression]
---

# Flutter: Bug Fix Assurance

Workflow nay dung khi can fix bug va dam bao loi da het that su.

## Input

- Mo ta loi
- Cach tai hien
- Man hinh/chuc nang bi anh huong
- Log loi (neu co)

## Steps

1. Tai hien loi on dinh
   - Ghi ro: thiet bi, kich thuoc man hinh, huong man hinh, network, account.
   - Neu khong tai hien duoc => khong fix vo vang.
2. Khoanh vung nguyen nhan goc
   - Tim file lien quan den stack trace/log.
   - Kiem tra data input, state, lifecycle widget, async timing.
   - Xac dinh 1 nguyen nhan goc ro rang truoc khi sua.
3. Sua toi thieu, dung diem
   - Uu tien sua mot cho, tranh lan sang code khong lien quan.
   - Khong doi API contract neu bug khong lien quan contract.
4. Them test hoi quy (regression)
   - Unit test neu bug nam o logic.
   - Widget test neu bug nam o UI/state.
   - Integration test neu bug nam o luong dau-cuoi.
5. Chay workflow `flutter-test-assurance.md` (bat buoc)
   - Dam bao test fail truoc fix (Red) va pass sau fix (Green).
   - Dam bao test khong flaky truoc khi merge.
6. Xac nhan bug da het
   - Chay lai dung case tai hien ban dau.
   - Chay them case canh bien (font lon, man hinh nho, mat mang, loading lau).
   - Dam bao khong tao bug moi.
7. Ghi nhan de tranh lap lai
   - Cap nhat `status.md`: da fix gi, file nao, test nao pass.
   - Cap nhat `learn.md`: nguyen nhan goc + bai hoc.
   - Neu co rui ro tiep dien, ghi them vao `note.md`.

## Done khi

- Loi tai hien ban dau khong con xuat hien.
- Co it nhat 1 test hoi quy cho bug do.
- Co bang chung Red -> Green theo workflow test assurance.
- Da cap nhat `status.md` va `learn.md`.
