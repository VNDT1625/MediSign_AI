---
name: "Flutter: Mock API Mode"
description: Bat che do mock API de UI dev song song khi backend chua san sang
category: Workflow
tags: [flutter, api, mock, productivity]
---

# Flutter: Mock API Mode

Workflow nay giup UI team khong bi chan boi backend.

## Steps

1. Tao co cong tac env:
   - `USE_MOCK_API=true/false`
2. Tach service layer:
   - `RealApiService`
   - `MockApiService`
3. Dinh nghia mock response cho endpoint chinh:
   - triage
   - medicine scan
4. Giu schema mock trung voi contract that trong `docs/engineering/api-contract.md`.
5. Viet widget/integration test cho ca 2 che do:
   - mock mode
   - real mode (khi backend san sang)
6. Kiem tra fallback:
   - backend loi thi co the tam chuyen mock cho demo noi bo.

## Done khi

- UI chay duoc day du voi mock.
- Chuyen qua real API khong vo man hinh.
- Khong doi schema tuy tien.
