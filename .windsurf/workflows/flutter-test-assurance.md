---
name: "Flutter: Test Assurance"
description: Quy trinh xac nhan test that su bat duoc loi, tranh pass gia
category: Workflow
tags: [flutter, testing, bugfix, quality]
---

# Flutter: Test Assurance

Workflow nay dam bao test co gia tri that: neu loi con ton tai thi test phai fail.

## Input

- Bug ID hoac mo ta loi
- Test case vua viet
- File da sua

## Steps

1. Red step (bat buoc)
   - Chay test tren code chua fix (hoac revert tam phan fix).
   - Test **phai FAIL** dung loi do.
   - Neu test van PASS => test vo dung, sua test truoc.
2. Green step
   - Ap dung ban fix.
   - Chay lai test vua viet.
   - Test phai PASS.
3. Regression step
   - Chay toan bo test lien quan module.
   - Dam bao khong pha hanh vi cu.
4. Negative-case step
   - Them it nhat 1 case canh bien de test van bat duoc loi gan giong.
   - Vi du: font lon, man hinh nho, API timeout, data null/rong.
5. Flaky guard
   - Chay test bug do 5 lan lien tiep.
   - Neu pass/fail khong on dinh => danh dau flaky, sua test hoac code async.
6. CI gate
   - Test bug fix phai duoc chay trong CI.
   - Neu fail trong CI => khong merge.
7. Ghi nhan
   - Cap nhat `status.md`: test nao fail truoc, pass sau.
   - Cap nhat `learn.md`: vi sao test ban dau khong bat duoc loi (neu co).

## Done khi

- Co bang chung Red -> Green ro rang.
- Co regression pass.
- Khong con flaky.
- CI pass.
