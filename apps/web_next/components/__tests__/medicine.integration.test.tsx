/**
 * Integration tests for medicine flows — task 11.4.
 *
 * Validates: Requirements 2.3.2
 *
 * Scenarios covered:
 *   1. Scan success path — fill form → submit → renders MedicineScanResponse
 *      (normalized name, risk badge, warnings list).
 *   2. Cabinet add — after scan success, click "Thêm vào tủ thuốc" →
 *      item appears in `localStorage["medisign:cabinet"]`.
 *   3. Cabinet remove — render CabinetTab with pre-populated localStorage →
 *      click remove → item removed from localStorage.
 *   4. Interaction warning — two items where one's warnings mention the
 *      other's name → conflict warning shown in CabinetTab.
 *
 * Strategy:
 *   - ScanTab is rendered standalone; the `scan()` API call is intercepted
 *     by the MSW server registered in `test/setup.ts`.
 *   - `localStorage` is cleared before each test and inspected directly to
 *     verify persistence without mocking the hook.
 *   - CabinetTab reads from `localStorage` on mount via `useMedicineCabinet`,
 *     so pre-populating storage before render is sufficient to seed state.
 *   - `next/navigation` is mocked because ScanTab / CabinetTab live inside
 *     the `/app/medicine` shell which may import router hooks transitively.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import type { MedicineScanResponse } from "@medisign/shared-contracts";

// ---------------------------------------------------------------------------
// Mock next/navigation — required for any component that imports router hooks
// ---------------------------------------------------------------------------

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/app/medicine",
}));

// ---------------------------------------------------------------------------
// Mock the fetcher's refreshOnce so no real refresh is attempted in jsdom.
// Also mock apiFetch to bypass the auth/token machinery entirely for scan
// calls — the MSW server handles the actual HTTP interception, but the
// fetcher's same-origin refresh proxy paths (/api/auth/refresh, /api/auth/logout)
// are not registered in the default MSW handlers and would trigger
// "unhandled request" errors. By mocking apiFetch we keep the test focused
// on component behaviour rather than the auth plumbing.
// ---------------------------------------------------------------------------

vi.mock("../../lib/api/fetcher", async () => {
  const actual = await vi.importActual<typeof import("../../lib/api/fetcher")>(
    "../../lib/api/fetcher",
  );
  return {
    ...actual,
    refreshOnce: vi.fn(() =>
      Promise.reject(
        Object.assign(new Error("no cookie"), {
          code: "AUTH_SESSION_EXPIRED",
          status: 401,
        }),
      ),
    ),
  };
});

// ---------------------------------------------------------------------------
// Mock lib/api/medicine so scan() resolves via a controlled promise rather
// than going through the full fetcher → MSW pipeline. This avoids the
// auth-token / refresh-proxy machinery that would fire unhandled-request
// errors in the MSW node server (which has onUnhandledRequest: "error").
// Individual tests override `scanMock` to return their desired response.
// ---------------------------------------------------------------------------

vi.mock("../../lib/api/medicine", async () => {
  const actual = await vi.importActual<typeof import("../../lib/api/medicine")>(
    "../../lib/api/medicine",
  );
  return {
    ...actual,
    scan: vi.fn(),
  };
});

// ---------------------------------------------------------------------------
// Component imports (after mocks)
// ---------------------------------------------------------------------------

import { ScanTab } from "../medicine/ScanTab";
import { CabinetTab } from "../medicine/CabinetTab";
import { buildMedicineScanResponse } from "../../test/msw/handlers";
import * as medicineApi from "../../lib/api/medicine";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CABINET_KEY = "medisign:cabinet";

/** Typed reference to the mocked scan function. */
const scanMock = medicineApi.scan as ReturnType<typeof vi.fn>;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Seed localStorage with an array of cabinet items before rendering. */
function seedCabinet(items: MedicineScanResponse[]): void {
  window.localStorage.setItem(CABINET_KEY, JSON.stringify(items));
}

/** Read the current cabinet from localStorage. */
function readCabinet(): MedicineScanResponse[] {
  const raw = window.localStorage.getItem(CABINET_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw) as MedicineScanResponse[];
  } catch {
    return [];
  }
}

/**
 * Fill the ScanTab form and submit it.
 * `medicineName` is optional (the field is optional in the UI).
 */
function fillAndSubmitScanForm(ocrText: string, medicineName = "") {
  if (medicineName) {
    const nameInput = screen.getByPlaceholderText(/paracetamol 500mg/i);
    fireEvent.change(nameInput, { target: { value: medicineName } });
  }

  const textarea = screen.getByPlaceholderText(/dán hoặc nhập văn bản/i);
  fireEvent.change(textarea, { target: { value: ocrText } });

  const submitButton = screen.getByRole("button", { name: /phân tích thuốc/i });
  fireEvent.click(submitButton);
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

beforeEach(() => {
  window.localStorage.clear();
  scanMock.mockReset();
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("Medicine flows — integration", () => {
  // -------------------------------------------------------------------------
  // 1. Scan success path
  // -------------------------------------------------------------------------

  describe("1. Scan success path", () => {
    it("renders normalized name, risk badge, and warnings after a successful scan", async () => {
      const scanResult = buildMedicineScanResponse({
        normalized_name: "Ibuprofen 400mg",
        risk_level: "MEDIUM",
        warnings: ["Không dùng khi đói", "Tránh dùng cùng aspirin"],
        guidance: "Uống sau bữa ăn, tối đa 3 lần/ngày.",
      });

      scanMock.mockResolvedValueOnce(scanResult);

      render(<ScanTab />);

      fillAndSubmitScanForm("Ibuprofen 400mg tablet", "Ibuprofen");

      // Normalized name should appear in the result card.
      await waitFor(() => {
        expect(screen.getByText("Ibuprofen 400mg")).toBeInTheDocument();
      });

      // Risk badge — "Thận trọng" maps to MEDIUM.
      expect(screen.getByText("Thận trọng")).toBeInTheDocument();

      // Both warnings should be rendered.
      expect(screen.getByText("Không dùng khi đói")).toBeInTheDocument();
      expect(screen.getByText("Tránh dùng cùng aspirin")).toBeInTheDocument();

      // Guidance paragraph should be visible.
      expect(
        screen.getByText(/uống sau bữa ăn, tối đa 3 lần\/ngày/i),
      ).toBeInTheDocument();
    });

    it("renders LOW risk badge as 'An toàn'", async () => {
      const scanResult = buildMedicineScanResponse({
        normalized_name: "Paracetamol 500mg",
        risk_level: "LOW",
        warnings: [],
        guidance: "Dùng 1 viên mỗi 6 giờ.",
      });

      scanMock.mockResolvedValueOnce(scanResult);

      render(<ScanTab />);
      fillAndSubmitScanForm("Paracetamol 500mg");

      await waitFor(() => {
        expect(screen.getByText("Paracetamol 500mg")).toBeInTheDocument();
      });

      expect(screen.getByText("An toàn")).toBeInTheDocument();
    });

    it("renders HIGH risk badge as 'Nguy hiểm'", async () => {
      const scanResult = buildMedicineScanResponse({
        normalized_name: "Warfarin 5mg",
        risk_level: "HIGH",
        warnings: ["Nguy cơ chảy máu cao"],
        guidance: "Chỉ dùng theo chỉ định bác sĩ.",
      });

      scanMock.mockResolvedValueOnce(scanResult);

      render(<ScanTab />);
      fillAndSubmitScanForm("Warfarin 5mg anticoagulant");

      await waitFor(() => {
        expect(screen.getByText("Warfarin 5mg")).toBeInTheDocument();
      });

      expect(screen.getByText("Nguy hiểm")).toBeInTheDocument();
      expect(screen.getByText("Nguy cơ chảy máu cao")).toBeInTheDocument();
    });

    it("shows the 'Thêm vào tủ thuốc' button after a successful scan", async () => {
      scanMock.mockResolvedValueOnce(buildMedicineScanResponse());

      render(<ScanTab />);
      fillAndSubmitScanForm("Paracetamol 500mg");

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /thêm vào tủ thuốc/i }),
        ).toBeInTheDocument();
      });
    });
  });

  // -------------------------------------------------------------------------
  // 2. Cabinet add — persists to localStorage
  // -------------------------------------------------------------------------

  describe("2. Cabinet add persists to localStorage", () => {
    it("clicking 'Thêm vào tủ thuốc' writes the scan result to localStorage", async () => {
      const scanResult = buildMedicineScanResponse({
        normalized_name: "Amoxicillin 500mg",
        risk_level: "LOW",
        warnings: [],
        guidance: "Uống đủ liệu trình kháng sinh.",
      });

      scanMock.mockResolvedValueOnce(scanResult);

      render(<ScanTab />);
      fillAndSubmitScanForm("Amoxicillin 500mg antibiotic");

      // Wait for the result card to appear.
      await waitFor(() => {
        expect(screen.getByText("Amoxicillin 500mg")).toBeInTheDocument();
      });

      // Click "Thêm vào tủ thuốc".
      const addButton = screen.getByRole("button", {
        name: /thêm vào tủ thuốc/i,
      });
      fireEvent.click(addButton);

      // The button should change to a confirmation status.
      await waitFor(() => {
        expect(screen.getByText(/đã thêm vào tủ thuốc/i)).toBeInTheDocument();
      });

      // localStorage should contain the item.
      const cabinet = readCabinet();
      expect(cabinet).toHaveLength(1);
      expect(cabinet[0].normalized_name).toBe("Amoxicillin 500mg");
      expect(cabinet[0].risk_level).toBe("LOW");
    });

    it("adding a second item appends to the existing cabinet", async () => {
      // Pre-seed one item.
      seedCabinet([
        buildMedicineScanResponse({ normalized_name: "Paracetamol 500mg" }),
      ]);

      const newItem = buildMedicineScanResponse({
        normalized_name: "Ibuprofen 400mg",
        risk_level: "MEDIUM",
        warnings: [],
        guidance: "Uống sau bữa ăn.",
      });

      scanMock.mockResolvedValueOnce(newItem);

      render(<ScanTab />);
      fillAndSubmitScanForm("Ibuprofen 400mg");

      await waitFor(() => {
        expect(screen.getByText("Ibuprofen 400mg")).toBeInTheDocument();
      });

      fireEvent.click(
        screen.getByRole("button", { name: /thêm vào tủ thuốc/i }),
      );

      await waitFor(() => {
        expect(screen.getByText(/đã thêm vào tủ thuốc/i)).toBeInTheDocument();
      });

      const cabinet = readCabinet();
      expect(cabinet).toHaveLength(2);
      const names = cabinet.map((i) => i.normalized_name);
      expect(names).toContain("Paracetamol 500mg");
      expect(names).toContain("Ibuprofen 400mg");
    });

    it("adding a duplicate item replaces the existing entry (deduplication)", async () => {
      // Pre-seed the same item with old guidance.
      seedCabinet([
        buildMedicineScanResponse({
          normalized_name: "Paracetamol 500mg",
          guidance: "Cũ: 1 viên mỗi 8 giờ.",
        }),
      ]);

      const updatedItem = buildMedicineScanResponse({
        normalized_name: "Paracetamol 500mg",
        guidance: "Mới: 1 viên mỗi 6 giờ.",
      });

      scanMock.mockResolvedValueOnce(updatedItem);

      render(<ScanTab />);
      fillAndSubmitScanForm("Paracetamol 500mg updated label");

      await waitFor(() => {
        expect(screen.getByText("Paracetamol 500mg")).toBeInTheDocument();
      });

      fireEvent.click(
        screen.getByRole("button", { name: /thêm vào tủ thuốc/i }),
      );

      await waitFor(() => {
        expect(screen.getByText(/đã thêm vào tủ thuốc/i)).toBeInTheDocument();
      });

      // Should still be 1 item (replaced, not duplicated).
      const cabinet = readCabinet();
      expect(cabinet).toHaveLength(1);
      expect(cabinet[0].guidance).toBe("Mới: 1 viên mỗi 6 giờ.");
    });
  });

  // -------------------------------------------------------------------------
  // 3. Cabinet remove — persists removal to localStorage
  // -------------------------------------------------------------------------

  describe("3. Cabinet remove persists to localStorage", () => {
    it("clicking remove on a cabinet item removes it from localStorage", async () => {
      const item = buildMedicineScanResponse({
        normalized_name: "Metformin 500mg",
        risk_level: "LOW",
        warnings: [],
        guidance: "Uống cùng bữa ăn.",
      });

      seedCabinet([item]);

      render(<CabinetTab />);

      // The item should be visible.
      await waitFor(() => {
        expect(screen.getByText("Metformin 500mg")).toBeInTheDocument();
      });

      // Click the remove button (aria-label contains the medicine name).
      const removeButton = screen.getByRole("button", {
        name: /xoá metformin 500mg khỏi tủ thuốc/i,
      });
      fireEvent.click(removeButton);

      // The item should disappear from the UI.
      await waitFor(() => {
        expect(screen.queryByText("Metformin 500mg")).not.toBeInTheDocument();
      });

      // localStorage should be empty.
      const cabinet = readCabinet();
      expect(cabinet).toHaveLength(0);
    });

    it("removing one item from a multi-item cabinet leaves the others intact", async () => {
      const itemA = buildMedicineScanResponse({
        normalized_name: "Atorvastatin 10mg",
        risk_level: "LOW",
        warnings: [],
        guidance: "Uống buổi tối.",
      });
      const itemB = buildMedicineScanResponse({
        normalized_name: "Lisinopril 5mg",
        risk_level: "MEDIUM",
        warnings: [],
        guidance: "Uống buổi sáng.",
      });

      seedCabinet([itemA, itemB]);

      render(<CabinetTab />);

      await waitFor(() => {
        expect(screen.getByText("Atorvastatin 10mg")).toBeInTheDocument();
        expect(screen.getByText("Lisinopril 5mg")).toBeInTheDocument();
      });

      // Remove only itemA.
      fireEvent.click(
        screen.getByRole("button", {
          name: /xoá atorvastatin 10mg khỏi tủ thuốc/i,
        }),
      );

      await waitFor(() => {
        expect(
          screen.queryByText("Atorvastatin 10mg"),
        ).not.toBeInTheDocument();
      });

      // itemB should still be present.
      expect(screen.getByText("Lisinopril 5mg")).toBeInTheDocument();

      // localStorage should contain only itemB.
      const cabinet = readCabinet();
      expect(cabinet).toHaveLength(1);
      expect(cabinet[0].normalized_name).toBe("Lisinopril 5mg");
    });

    it("removing the last item shows the empty state", async () => {
      seedCabinet([
        buildMedicineScanResponse({ normalized_name: "Aspirin 100mg" }),
      ]);

      render(<CabinetTab />);

      await waitFor(() => {
        expect(screen.getByText("Aspirin 100mg")).toBeInTheDocument();
      });

      fireEvent.click(
        screen.getByRole("button", {
          name: /xoá aspirin 100mg khỏi tủ thuốc/i,
        }),
      );

      // Empty state message should appear.
      await waitFor(() => {
        expect(screen.getByText(/tủ thuốc trống/i)).toBeInTheDocument();
      });

      expect(readCabinet()).toHaveLength(0);
    });
  });

  // -------------------------------------------------------------------------
  // 4. Interaction warning surfaces
  // -------------------------------------------------------------------------

  describe("4. Interaction warning surfaces", () => {
    it("shows conflict warning when one item's warnings mention another item's name", async () => {
      // itemA's warnings explicitly mention itemB's normalized_name.
      const itemA = buildMedicineScanResponse({
        normalized_name: "Warfarin 5mg",
        risk_level: "HIGH",
        warnings: [
          "Tương tác với Aspirin 100mg — tăng nguy cơ chảy máu",
          "Tránh dùng cùng NSAID",
        ],
        guidance: "Theo dõi INR thường xuyên.",
      });
      const itemB = buildMedicineScanResponse({
        normalized_name: "Aspirin 100mg",
        risk_level: "MEDIUM",
        warnings: [],
        guidance: "Uống sau bữa ăn.",
      });

      seedCabinet([itemA, itemB]);

      render(<CabinetTab />);

      // Both items should be visible.
      await waitFor(() => {
        expect(screen.getAllByText("Warfarin 5mg").length).toBeGreaterThan(0);
        expect(screen.getAllByText("Aspirin 100mg").length).toBeGreaterThan(0);
      });

      // The global conflict summary banner should appear.
      expect(
        screen.getByText(/phát hiện tương tác thuốc/i),
      ).toBeInTheDocument();

      // The per-item conflict warning should appear on the conflicting card.
      expect(
        screen.getAllByText(/cảnh báo tương tác thuốc/i).length,
      ).toBeGreaterThan(0);
    });

    it("shows which medicine the conflict is with", async () => {
      const itemA = buildMedicineScanResponse({
        normalized_name: "Methotrexate 2.5mg",
        risk_level: "HIGH",
        warnings: ["Không dùng cùng Ibuprofen 400mg — độc tính thận"],
        guidance: "Chỉ dùng theo chỉ định bác sĩ.",
      });
      const itemB = buildMedicineScanResponse({
        normalized_name: "Ibuprofen 400mg",
        risk_level: "MEDIUM",
        warnings: [],
        guidance: "Uống sau bữa ăn.",
      });

      seedCabinet([itemA, itemB]);

      render(<CabinetTab />);

      await waitFor(() => {
        expect(screen.getAllByText("Methotrexate 2.5mg").length).toBeGreaterThan(0);
      });

      // The conflict detail should mention the conflicting medicine name.
      expect(
        screen.getAllByText(/có thể tương tác với/i).length,
      ).toBeGreaterThan(0);

      // "Ibuprofen 400mg" should appear in the conflict detail.
      const conflictDetails = screen.getAllByText(/ibuprofen 400mg/i);
      expect(conflictDetails.length).toBeGreaterThan(0);
    });

    it("does NOT show conflict warning when no warnings mention other items", async () => {
      const itemA = buildMedicineScanResponse({
        normalized_name: "Vitamin C 500mg",
        risk_level: "LOW",
        warnings: ["Uống nhiều nước"],
        guidance: "Uống sau bữa ăn.",
      });
      const itemB = buildMedicineScanResponse({
        normalized_name: "Zinc 10mg",
        risk_level: "LOW",
        warnings: ["Không dùng quá liều"],
        guidance: "Uống buổi sáng.",
      });

      seedCabinet([itemA, itemB]);

      render(<CabinetTab />);

      await waitFor(() => {
        expect(screen.getByText("Vitamin C 500mg")).toBeInTheDocument();
        expect(screen.getByText("Zinc 10mg")).toBeInTheDocument();
      });

      // No conflict banner should appear.
      expect(
        screen.queryByText(/phát hiện tương tác thuốc/i),
      ).not.toBeInTheDocument();

      expect(
        screen.queryByText(/cảnh báo tương tác thuốc/i),
      ).not.toBeInTheDocument();
    });

    it("shows conflict on both items when warnings are bidirectional", async () => {
      // Both items mention each other in their warnings.
      const itemA = buildMedicineScanResponse({
        normalized_name: "Drug Alpha",
        risk_level: "HIGH",
        warnings: ["Tương tác với Drug Beta"],
        guidance: "Thận trọng.",
      });
      const itemB = buildMedicineScanResponse({
        normalized_name: "Drug Beta",
        risk_level: "HIGH",
        warnings: ["Tương tác với Drug Alpha"],
        guidance: "Thận trọng.",
      });

      seedCabinet([itemA, itemB]);

      render(<CabinetTab />);

      await waitFor(() => {
        expect(screen.getAllByText("Drug Alpha").length).toBeGreaterThan(0);
        expect(screen.getAllByText("Drug Beta").length).toBeGreaterThan(0);
      });

      // Both items should show the conflict warning.
      const conflictWarnings = screen.getAllByText(/cảnh báo tương tác thuốc/i);
      expect(conflictWarnings).toHaveLength(2);
    });
  });

  // -------------------------------------------------------------------------
  // 5. CabinetTab UI — device banner and item count
  // -------------------------------------------------------------------------

  describe("5. CabinetTab UI elements", () => {
    it("shows the device storage banner", async () => {
      seedCabinet([buildMedicineScanResponse()]);

      render(<CabinetTab />);

      await waitFor(() => {
        expect(
          screen.getByText(/danh sách này lưu trên thiết bị/i),
        ).toBeInTheDocument();
      });
    });

    it("shows item count when cabinet has items", async () => {
      seedCabinet([
        buildMedicineScanResponse({ normalized_name: "Med A" }),
        buildMedicineScanResponse({ normalized_name: "Med B" }),
      ]);

      render(<CabinetTab />);

      await waitFor(() => {
        expect(screen.getByText(/2 thuốc trong tủ/i)).toBeInTheDocument();
      });
    });

    it("shows empty state when cabinet is empty", async () => {
      render(<CabinetTab />);

      await waitFor(() => {
        expect(screen.getByText(/tủ thuốc trống/i)).toBeInTheDocument();
      });
    });
  });
});
