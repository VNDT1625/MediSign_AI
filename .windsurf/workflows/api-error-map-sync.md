---
name: "API: Error Map Sync"
description: Dong bo ma loi API va thong diep UI de tranh xu ly loi moi noi mot kieu
category: Workflow
tags: [api, error-handling, backend, flutter]
---

# API: Error Map Sync

Workflow nay dong bo cach bao loi giua backend va Flutter.

## Steps

1. Chot bang ma loi chung (vd: `AUTH_401`, `TRIAGE_TIMEOUT`, `MED_NOT_FOUND`).
2. Backend tra response loi theo format thong nhat:
   - `code`
   - `message`
   - `trace_id` (neu co)
3. Flutter mapping `code` -> thong bao than thien theo ngu canh.
4. Viet test backend cho format loi.
5. Viet test Flutter cho mapping thong bao loi.
6. Cap nhat `docs/engineering/api-contract.md` khi them/sua ma loi.

## Done khi

- Cung 1 loi, backend va UI hien thi dong nhat.
- Khong con thong bao loi mo ho voi nguoi dung.
