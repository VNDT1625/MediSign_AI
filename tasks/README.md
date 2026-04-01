# Task Board by AI

Thu muc nay chia task theo tung AI de lam song song, tranh trung lap va de review.

## Quy tac tai lieu (bat buoc)

- Khong tu tao them file `.md` tuy bien.
- Tat ca cap nhat tai lieu phai ghi vao bo file co dinh o root:
  - `status.md`
  - `learn.md`
  - `project.md`
  - `note.md`
  - `database.md`
  - `quy tắc.md`

- `tasks/antigravity`: UI va test UI
- `tasks/kiro`: backend core va test CLI
- `tasks/chatgpt-codex`: bug kho, reasoning fix
- `tasks/cursor`: backend task lap lai
- `tasks/windsurf`: integration, review, release

## Ma tran AI x Workflow (bat buoc)

- **Antigravity**
  - Workflow chinh: `flutter-component.md`, `flutter-ui-accessibility-first.md`, `flutter-ui-overflow.md`, `flutter-mock-api-mode.md`
  - Bug/test bat buoc: `flutter-find-related-bugs.md`, `flutter-bug-fix-assurance.md`, `flutter-test-assurance.md`

- **Kiro**
  - Workflow chinh: `flutter-api-endpoint.md`, `flutter-feature-workflow.md`, `api-error-map-sync.md`
  - Bug/test bat buoc: `flutter-find-related-bugs.md`, `flutter-bug-fix-assurance.md`, `backend-test-assurance.md`

- **ChatGPT Codex**
  - Workflow chinh: `flutter-find-related-bugs.md`
  - Bug/test bat buoc: `flutter-bug-fix-assurance.md`, `flutter-test-assurance.md`

- **Cursor**
  - Workflow chinh: `flutter-feature-workflow.md`, `api-error-map-sync.md`
  - Bug/test bat buoc: `backend-test-assurance.md`

- **Windsurf**
  - Workflow chinh: `flutter-feature-workflow.md`, `flutter-testing.md`, `pr-review-gate.md`, `release-demo-gate.md`, `performance-smoke.md`
  - Bug/test bat buoc: review ket qua Red -> Green + regression + flaky guard + PR gate

## Checklist chung truoc khi dong task

- [ ] Da ghi cap nhat vao `status.md`
- [ ] Neu co bai hoc moi, da ghi `learn.md`
- [ ] Neu fix bug: co bang chung Red -> Green
- [ ] Regression pass
- [ ] Khong flaky (lap lai test 5 lan on dinh)
- [ ] Da qua `pr-review-gate.md` truoc khi merge

## Checklist truoc demo/release

- [ ] Da chay `performance-smoke.md`
- [ ] Da chay `release-demo-gate.md`
- [ ] Co ket luan go/no-go ro rang

## Task template dung chung

Su dung mau nay cho moi task cua moi AI:

```text
# <AI> - <Task name>

## Owner
- AI:
- Nguoi review:

## Muc tieu
-

## Input/Pham vi
-

## Steps
1.
2.
3.

## Test bat buoc
- [ ] Red -> Green (neu la bug fix)
- [ ] Regression pass
- [ ] Flaky guard (5 lan)

## Done khi
-

## File da sua
-
```
