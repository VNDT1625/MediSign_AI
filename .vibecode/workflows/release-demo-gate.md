---
name: "Release: Demo Gate"
description: Checklist truoc demo/release de tranh vo luong va co phuong an du phong
category: Workflow
tags: [release, demo, checklist, reliability]
---

# Release: Demo Gate

Workflow nay duoc chay truoc demo noi bo, demo voi stakeholder, va release.

## Steps

1. Kiem tra luong chinh end-to-end
   - onboarding -> triage -> result
   - login (neu co) -> feature chinh
2. Kiem tra quality gate
   - CI xanh
   - Red -> Green da co cho bug fix quan trong
   - Regression pass
3. Kiem tra du lieu va API
   - Endpoint chinh phan hoi on dinh
   - Error map hien thong bao de hieu
4. Kiem tra man hinh va accessibility
   - Khong overflow o man hinh nho/lon
   - Font scale lon van su dung duoc
5. Kiem tra fallback demo
   - Co mock mode neu backend gap su co
   - Co san tai khoan test + du lieu test
6. Kiem tra tai lieu
   - `status.md` cap nhat nhung muc vua xong
   - `note.md` cap nhat rui ro con ton dong
7. Chot go/no-go
   - Go: tat ca muc pass
   - No-go: ghi ro block + owner + ETA

## Done khi

- Co ket luan go/no-go ro rang.
- Team co ke hoach fallback neu gap su co trong demo.
