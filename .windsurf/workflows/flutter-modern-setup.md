---
name: "Flutter: Modern Setup"
description: Khoi tao va chuan hoa du an Flutter theo phien ban stable moi nhat
category: Workflow
tags: [flutter, setup, modern]
---

# Flutter: Modern Setup

Chuan hoa du an Flutter theo cach hien dai, de doi AI code dong nhat.

## Steps

1. Kiem tra Flutter stable moi nhat:
   - `flutter upgrade`
   - `flutter --version`
2. Kiem tra moi truong:
   - `flutter doctor -v`
3. Chuan hoa static analysis:
   - bat `flutter_lints`
   - bo sung quy tac lint duoc team thong nhat
4. Khoi tao cau truc thu muc:
   - `lib/core`, `lib/features`, `lib/shared`, `test`, `integration_test`
5. Chot package hien dai (tuy nhu cau):
   - dieu huong: `go_router`
   - state: `riverpod`
   - network: `dio`
   - model: `freezed`, `json_serializable`
6. Tao man hinh mau + route mau + test smoke.

## Output

- Du an Flutter chay duoc, lint pass, cau truc thong nhat cho team.
