---
name: "Performance: Smoke Check"
description: Kiem tra nhanh hieu nang de phat hien giat/tre nghiem trong truoc merge
category: Workflow
tags: [performance, smoke, flutter, backend]
---

# Performance: Smoke Check

Workflow nay la check nhanh hieu nang, khong thay the benchmark day du.

## Steps

1. Chot 3 luong can do
   - Mo app va vao Home
   - Chay luong triage chinh
   - Tai du lieu tu API chinh
2. Do nhanh tren 2 nhom thiet bi
   - 1 may yeu (hoac emulator cau hinh thap)
   - 1 may trung/khá
3. Kiem tra Flutter jank co ban
   - Bat Performance Overlay / DevTools timeline
   - Neu khung hinh giat ro ret => block merge
4. Kiem tra do tre API
   - Request chinh khong timeout bat thuong
   - Neu cham, co loading state ro rang
5. Kiem tra bo nho co ban
   - Mo/thoat man hinh lien tuc, khong tang bo nho bat thuong
6. Chot ket qua
   - Pass: khong thay giat/tre nghiem trong
   - Fail: tao task toi uu truoc release

## Done khi

- Co ghi nhan pass/fail cho 3 luong chinh.
- Neu fail, da co task va owner xu ly.
