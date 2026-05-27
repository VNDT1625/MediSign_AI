# Voice Control Enhancement — Testing Conventions

Tài liệu này mô tả convention testing cho feature **voice-control-enhancement**, áp dụng cho mọi module trong `apps/web_next/lib/voice/`. Convention này thoả mãn các Acceptance Criteria thuộc **Requirement 6 (Correctness Properties)** trong `requirements.md`.

---

## 1. Test Runner

- **Framework**: [Vitest](https://vitest.dev/) `^3.2.4` (đã cài trong `apps/web_next/package.json`).
- **Property-based engine**: [`fast-check`](https://github.com/dubzzz/fast-check) `^4.8.0`.
- **Environment**: `jsdom` (cấu hình tại `apps/web_next/vitest.config.ts`).
- **Setup file**: `apps/web_next/test/setup.ts`.

Vitest `include` pattern hiện tại:

```ts
include: ["**/*.{test,spec,property.test}.{ts,tsx}"]
```

Pattern này tự động pickup cả `*.test.ts` và `*.property.test.ts` mà **không cần thêm cấu hình**. Glob `{test,spec,property.test}` mở rộng thành `test`, `spec`, và `property.test`, cho phép suffix `.property.test.ts` được nhận diện như một loại test riêng.

---

## 2. File Naming & Layout

| Loại test | Suffix | Vị trí | Ví dụ |
|---|---|---|---|
| **Unit / example-based** | `*.test.ts` | Co-located bên cạnh source file trong `lib/voice/` | `transcriptCorrector.test.ts` đặt cạnh `transcriptCorrector.ts` |
| **Property-based** | `*.property.test.ts` | Co-located bên cạnh source file trong `lib/voice/` | `transcriptCorrector.property.test.ts` |
| **Integration** | `*.integration.test.ts` | `lib/voice/` hoặc `__tests__/` lân cận | `voice-pipeline.integration.test.ts` |

Quy tắc:

- Một module có thể có **cả** unit test và property test (chúng bổ sung lẫn nhau, không thay thế).
- Không đặt test trong thư mục `e2e/` (đã được `exclude` khỏi Vitest và dành cho Playwright).
- Không sử dụng `__tests__` riêng cho feature voice — co-location giúp dễ thấy coverage và đồng bộ với phần còn lại của `lib/voice/`.

---

## 3. Property Test Tag Format (BẮT BUỘC)

Mỗi property test **phải** có comment tag đặt **ngay trên** lệnh `test(...)` hoặc `it(...)` theo format sau:

```ts
// Feature: voice-control-enhancement, Property N: <property text>
// Validates: Requirements X.Y, X.Z
test("descriptive test name", () => {
  fc.assert(
    fc.property(/* generator */, (input) => {
      // assertion
    }),
    { numRuns: 100 }
  );
});
```

Trong đó:

- `N` là số thứ tự của property trong `design.md` (ví dụ: `Property 13` cho idempotency của transcript corrector).
- `<property text>` là tên ngắn của property như đã đặt ở `tasks.md` / `design.md` (ví dụ `Transcript corrector is idempotent`).
- Dòng `Validates: Requirements ...` liệt kê các Acceptance Criteria từ `requirements.md` mà property này phủ.

Mục đích: traceability hai chiều giữa requirements ↔ design ↔ test, hỗ trợ audit và refactor.

### Ví dụ cụ thể

```ts
// Feature: voice-control-enhancement, Property 13: Transcript corrector is idempotent
// Validates: Requirements 4.6, 6.2
test("correct(correct(x)) === correct(x) for any string", () => {
  fc.assert(
    fc.property(fc.string({ minLength: 1, maxLength: 500 }), (x) => {
      expect(correct(correct(x))).toBe(correct(x));
    }),
    { numRuns: 200 }
  );
});
```

---

## 4. Iteration Counts

| Property loại | `numRuns` tối thiểu |
|---|---|
| **Mặc định** | `100` |
| **High-priority** (idempotency, low-confidence filter, barge-in timing) | `200` |

High-priority bao gồm các property thuộc Requirement 1, 2, và 4.6 (transcript idempotency) vì chúng bảo vệ invariant cốt lõi của pipeline.

---

## 5. NPM Scripts

`package.json` cung cấp các script sau (tương thích Vitest 3.x):

| Script | Mô tả |
|---|---|
| `npm run test` | Chạy Vitest ở watch mode (mọi loại test). |
| `npm run test:run` | Chạy mọi test một lần (CI mode). |
| `npm run test:unit` | Chỉ chạy unit/example-based tests, **loại trừ** `*.property.test.ts`. |
| `npm run test:property` | Chỉ chạy property-based tests (`**/*.property.test.ts`). |
| `npm run test:coverage` | Chạy mọi test một lần với báo cáo coverage. |

Single quotes quanh glob pattern (`'**/*.property.test.ts'`) cần thiết trên POSIX shells để ngăn shell expansion. Trên Windows PowerShell / `cmd.exe`, npm parse string này nguyên vẹn và truyền cho Vitest, nên hoạt động đồng nhất cross-platform. Nếu shell cụ thể từ chối glob, bạn có thể dùng `--include`:

```bash
npx vitest run --include "**/*.property.test.ts"
```

---

## 6. Generator Best Practices

- **Constrain input space khi cần**: ví dụ `fc.float({ min: 0.01, max: 0.39, noNaN: true })` cho transcript có confidence dưới ngưỡng — không generate NaN/Infinity nếu code không xử lý chúng.
- **Dùng `fc.constantFrom(...)` cho dictionary keys**: ví dụ `fc.constantFrom(...Object.keys(FUZZY_DICTIONARY))`.
- **Tránh side effect ngoài DOM mock**: property tests chạy trên `jsdom`; mọi DOM interaction phải reset giữa các runs (Vitest's default cleanup hooks giúp việc này).
- **Tránh mock không cần thiết**: pure functions (như `levenshteinDistance`, `correct`) test thẳng không cần mock.

---

## 7. Requirements Coverage

Convention này phục vụ trực tiếp các Acceptance Criteria sau từ `requirements.md`:

| Requirement | Cơ chế đáp ứng |
|---|---|
| **6.1** Barge-in TTS stop ≤ 100ms | Property tests trong `bargein.property.test.ts` (Property 1). |
| **6.2** `correct(correct(x)) === correct(x)` | Property test trong `transcriptCorrector.property.test.ts` (Property 13, `numRuns: 200`). |
| **6.3** Logged-in `auth_login` không dispatch event | Property test trong `executor.property.test.ts` (Property 8). |
| **6.4** `scrollToNextSection` trả về sectionId hợp lệ hoặc `null` | Property test trong `pageScenarios.property.test.ts` (Property 17). |
| **6.5** Confidence < threshold → bỏ qua Intent_Matcher | Property test trong `noiseFilter.property.test.ts` (Property 5). |
| **6.6** `correct("cũng xuốn")` chứa `"cuon xuong"` sau normalize | Unit test trong `transcriptCorrector.test.ts`. |
| **6.7** Threshold ngoài (0, 1) → fallback 0.4 | Property test trong `noiseFilter.property.test.ts` (Property 7). |

Các Requirement chỉ định kiểm thử (6.x) đều được phủ bởi ít nhất một property test có tag annotation đầy đủ.

---

## 8. Triaging Failing Property Tests

Khi một property test fail, fast-check trả counter-example. Quy trình triage:

1. **Test sai?** Generator có thể generate input ngoài contract (ví dụ NaN cho float). Sửa generator.
2. **Code có bug?** Counter-example là input hợp lệ mà code xử lý sai. Fix code.
3. **Spec strange?** Test đúng theo Acceptance Criteria nhưng AC có lỗ hổng. **Không tự sửa AC** — báo lại cho team / user qua `update_pbt_status` để họ quyết định cập nhật `requirements.md`.

---

## 9. References

- Spec: `.kiro/specs/voice-control-enhancement/`
  - `requirements.md` — Acceptance Criteria gốc.
  - `design.md` — danh sách Property 1–17 đầy đủ.
  - `tasks.md` — mapping task ↔ property.
- Vitest config: `apps/web_next/vitest.config.ts`.
- Test setup: `apps/web_next/test/setup.ts`.
