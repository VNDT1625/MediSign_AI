---
name: "Flutter: API Endpoint Integration"
description: Ket noi endpoint backend vao Flutter theo cach an toan va de bao tri
category: Workflow
tags: [flutter, api, endpoint]
---

# Flutter: API Endpoint Integration

Ket noi API vao Flutter theo hop dong endpoint va xu ly loi ro rang.

## Input

Endpoint, request schema, response schema, auth rule.

## Steps

1. Doc hop dong trong `docs/engineering/api-contract.md`.
2. Tao model request/response (co parse ro rang).
3. Tao service layer goi API (Dio), khong goi truc tiep trong UI.
4. Xu ly loi thong nhat:
   - timeout
   - 4xx
   - 5xx
   - mat mang
5. Mapping error -> thong bao than thien cho user.
6. Viet test cho service va 1 widget test cho luong thanh cong/that bai.
7. Cap nhat `status.md` va neu co pattern moi thi ghi `learn.md`.

## Output

- Endpoint da ket noi, co xu ly loi, co test co ban.
