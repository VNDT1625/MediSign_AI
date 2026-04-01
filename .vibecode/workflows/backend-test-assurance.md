---
name: "Backend: Test Assurance"
description: Quy trinh dam bao test backend bat dung loi, tranh pass gia
category: Workflow
tags: [backend, testing, bugfix, regression]
---

# Backend: Test Assurance

Workflow nay dam bao neu loi backend con ton tai thi test phai fail.

## Input

- Mo ta bug backend
- API/Service bi anh huong
- Test case da viet

## Steps

1. Red step (bat buoc)
   - Chay test tren ban code chua fix.
   - Test phai fail dung loi.
   - Neu pass => test chua bat dung loi, sua test.
2. Green step
   - Ap dung ban fix toi thieu.
   - Chay lai test, test phai pass.
3. Regression step
   - Chay test module lien quan (API/service/repository).
4. Negative cases
   - Them case bien: timeout, invalid payload, null/empty, unauthorized.
5. Flaky guard
   - Chay test bug do 5 lan lien tiep.
   - Neu ket qua khong on dinh => chua merge.
6. CI gate
   - Bat buoc pass trong GitHub Actions quality gate.
7. Ghi nhan
   - Cap nhat `status.md` va `learn.md`.

## Done khi

- Co bang chung Red -> Green.
- Regression pass.
- Khong flaky.
- CI pass.
