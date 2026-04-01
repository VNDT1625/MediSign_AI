---
name: "Flutter: Testing Stack"
description: Thiet lap va viet test Flutter (unit, widget, integration) theo chuan hien dai
category: Workflow
tags: [flutter, testing, quality]
---

# Flutter: Testing Stack

Thiet lap bo test de giam bug hoi quy va tang toc fix loi.

## Steps

1. Chot pham vi test theo 3 tang:
   - unit test cho logic
   - widget test cho UI
   - integration test cho luong chinh
2. Viet test truoc cho bug quan trong (neu dang fix bug).
3. Widget test bat buoc cho:
   - Home
   - Onboarding
   - Triage Result
4. Integration test cho luong:
   - vao app -> triage -> result
5. Chay test:
   - `flutter test`
   - `flutter test integration_test`
6. Cap nhat `status.md` ket qua pass/fail va phan dang block.

## Output

- Bo test chay duoc trong local va CI.
