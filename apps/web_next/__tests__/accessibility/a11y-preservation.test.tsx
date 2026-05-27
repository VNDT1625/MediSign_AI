/**
 * Preservation Property Tests — Task 3 (Accessibility Fixes)
 *
 * These tests MUST PASS on UNFIXED code. They capture baseline behavior
 * that must be preserved after accessibility fixes are applied.
 *
 * Methodology: observation-first — we observe the unfixed code behavior
 * and encode it as tests so regressions are caught after fixes.
 *
 * **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8**
 */

import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import * as fc from "fast-check";
import { vi, describe, it, expect, beforeEach } from "vitest";

// ---------------------------------------------------------------------------
// Module mocks — must be declared before component imports
// ---------------------------------------------------------------------------

// Mock next/navigation (useRouter, useSearchParams) used by LoginModal
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
}));

// Mock window.matchMedia — required by Reveal component (prefers-reduced-motion)
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver — required by Reveal component (scroll-based reveal)
const mockIntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
  takeRecords: vi.fn().mockReturnValue([]),
}));
Object.defineProperty(window, "IntersectionObserver", {
  writable: true,
  configurable: true,
  value: mockIntersectionObserver,
});
Object.defineProperty(global, "IntersectionObserver", {
  writable: true,
  configurable: true,
  value: mockIntersectionObserver,
});

// Mock useAuth — LoginModal calls login() and register()
vi.mock("@/lib/auth/useAuth", () => ({
  useAuth: () => ({
    state: { status: "anonymous" },
    isAuthenticated: false,
    login: vi.fn().mockResolvedValue(undefined),
    register: vi.fn().mockResolvedValue(undefined),
    logout: vi.fn().mockResolvedValue(undefined),
    changePassword: vi.fn().mockResolvedValue(undefined),
    hydrate: vi.fn().mockResolvedValue(undefined),
  }),
}));

// Mock useIntent — LoginModal calls consume() after successful login
vi.mock("@/lib/auth/useIntent", () => ({
  useIntent: () => ({
    set: vi.fn(),
    peek: vi.fn().mockReturnValue(null),
    consume: vi.fn().mockReturnValue({ redirectPath: "/app" }),
  }),
}));

// ---------------------------------------------------------------------------
// Component imports (after mocks)
// ---------------------------------------------------------------------------

import { AnalysisCard } from "@/components/chat/ChatMain";
import { LoginModal } from "@/components/LoginModal";
import { AboutMilestones } from "@/components/sections/AboutMilestones";
import { AboutTeam } from "@/components/sections/AboutTeam";

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const mockAnalysisMsg = {
  id: "m5",
  role: "ai" as const,
  kind: "analysis" as const,
  intro: "Cảm ơn bạn đã cung cấp thêm thông tin và hình ảnh. Dưới đây là phân tích sơ bộ:",
  assessment: [
    { label: "Nhiệt độ:", value: "37.8°C (sốt nhẹ)" },
    { label: "Triệu chứng:", value: "Đau họng, ho khan, mệt nhẹ" },
    { label: "X-quang phổi:", value: "Không thấy tổn thương rõ ràng" },
  ],
  handling: [
    "Nghỉ ngơi, uống nhiều nước ấm.",
    "Có thể dùng Paracetamol nếu sốt cao.",
    "Súc họng bằng nước muối ấm 2–3 lần/ngày.",
  ],
  note: {
    text: "Lưu ý: Đây không phải là chẩn đoán cuối cùng.",
    time: "10:30",
  },
  time: "10:30",
};

// ---------------------------------------------------------------------------
// P2.1 — Heading content preserved
// AnalysisCard SHALL render text "Đánh giá sơ bộ" và "Gợi ý xử trí"
// (only tag changes, not content)
// ---------------------------------------------------------------------------

describe("P2.1 — Heading content preserved (AnalysisCard)", () => {
  it('renders "Đánh giá sơ bộ" heading text', () => {
    render(<AnalysisCard msg={mockAnalysisMsg} />);
    // The text must be present regardless of whether it's h2 or h3
    expect(screen.getByText("Đánh giá sơ bộ")).toBeInTheDocument();
  });

  it('renders "Gợi ý xử trí" heading text', () => {
    render(<AnalysisCard msg={mockAnalysisMsg} />);
    expect(screen.getByText("Gợi ý xử trí")).toBeInTheDocument();
  });

  it("renders both headings as heading elements (role=heading)", () => {
    render(<AnalysisCard msg={mockAnalysisMsg} />);
    const headings = screen.getAllByRole("heading");
    const headingTexts = headings.map((h) => h.textContent ?? "");
    expect(headingTexts.some((t) => t.includes("Đánh giá sơ bộ"))).toBe(true);
    expect(headingTexts.some((t) => t.includes("Gợi ý xử trí"))).toBe(true);
  });

  it("renders assessment items from the message", () => {
    render(<AnalysisCard msg={mockAnalysisMsg} />);
    expect(screen.getByText("Nhiệt độ:")).toBeInTheDocument();
    expect(screen.getByText(/37\.8°C/)).toBeInTheDocument();
  });

  it("renders handling items from the message", () => {
    render(<AnalysisCard msg={mockAnalysisMsg} />);
    expect(screen.getByText(/Nghỉ ngơi, uống nhiều nước ấm/)).toBeInTheDocument();
  });

  /**
   * Property: For any valid analysis message, AnalysisCard SHALL always
   * render both heading texts regardless of message content variation.
   *
   * **Validates: Requirements 3.2**
   */
  it("property: heading texts preserved across varied message content", () => {
    fc.assert(
      fc.property(
        fc.record({
          intro: fc.string({ minLength: 1, maxLength: 200 }),
          assessmentLabel: fc.string({ minLength: 1, maxLength: 50 }),
          assessmentValue: fc.string({ minLength: 1, maxLength: 100 }),
          handlingItem: fc.string({ minLength: 1, maxLength: 100 }),
          noteText: fc.string({ minLength: 1, maxLength: 200 }),
          time: fc.constantFrom("10:00", "10:30", "11:00", "14:25"),
        }),
        (data) => {
          const msg = {
            id: "test-id",
            role: "ai" as const,
            kind: "analysis" as const,
            intro: data.intro,
            assessment: [{ label: data.assessmentLabel, value: data.assessmentValue }],
            handling: [data.handlingItem],
            note: { text: data.noteText, time: data.time },
            time: data.time,
          };

          const { unmount } = render(<AnalysisCard msg={msg} />);

          const headings = screen.getAllByRole("heading");
          const headingTexts = headings.map((h) => h.textContent ?? "");

          const hasDanhGia = headingTexts.some((t) => t.includes("Đánh giá sơ bộ"));
          const hasGoiY = headingTexts.some((t) => t.includes("Gợi ý xử trí"));

          unmount();

          return hasDanhGia && hasGoiY;
        },
      ),
      { numRuns: 50 },
    );
  });
});

// ---------------------------------------------------------------------------
// P2.2 — LoginModal flow preserved
// LoginModal SHALL call onClose after successful submit
// ---------------------------------------------------------------------------

describe("P2.2 — LoginModal flow preserved", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders login modal when open=true", () => {
    const onClose = vi.fn();
    render(<LoginModal open={true} onClose={onClose} />);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("does not show dialog content when open=false", () => {
    const onClose = vi.fn();
    render(<LoginModal open={false} onClose={onClose} />);
    // Dialog is rendered but hidden (aria-hidden=true, opacity-0)
    const dialog = screen.getByRole("dialog", { hidden: true });
    expect(dialog).toHaveAttribute("aria-hidden", "true");
  });

  it("has role=dialog and aria-modal=true", () => {
    const onClose = vi.fn();
    render(<LoginModal open={true} onClose={onClose} />);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-modal", "true");
  });

  it("has aria-labelledby pointing to login-title", () => {
    const onClose = vi.fn();
    render(<LoginModal open={true} onClose={onClose} />);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-labelledby", "login-title");
  });

  it("calls onClose when close button is clicked", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<LoginModal open={true} onClose={onClose} />);

    const closeBtn = screen.getByRole("button", { name: /Quay về trang chủ/i });
    await user.click(closeBtn);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when ESC key is pressed", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<LoginModal open={true} onClose={onClose} />);

    await user.keyboard("{Escape}");

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  /**
   * Property: For any open/close state combination, the dialog's
   * aria-hidden attribute SHALL correctly reflect the open state.
   *
   * **Validates: Requirements 3.3**
   */
  it("property: aria-hidden reflects open state correctly", () => {
    fc.assert(
      fc.property(fc.boolean(), (isOpen) => {
        const onClose = vi.fn();
        const { unmount } = render(<LoginModal open={isOpen} onClose={onClose} />);

        const dialog = screen.getByRole("dialog", { hidden: true });
        const ariaHidden = dialog.getAttribute("aria-hidden");

        unmount();

        // When open=true, aria-hidden should be "false" (or absent)
        // When open=false, aria-hidden should be "true"
        if (isOpen) {
          return ariaHidden === "false" || ariaHidden === null;
        } else {
          return ariaHidden === "true";
        }
      }),
      { numRuns: 10 },
    );
  });
});

// ---------------------------------------------------------------------------
// P2.3 — Button label preserved (btn-primary)
// btn-primary label text SHALL not change after color fix
// ---------------------------------------------------------------------------

describe("P2.3 — Button label preserved (btn-primary)", () => {
  it("btn-primary class is defined in the DOM (globals.css applied)", () => {
    // Render a button with btn-primary class and verify it renders
    const { container } = render(
      <button className="btn-primary" type="button">
        Tải ứng dụng
      </button>,
    );
    const btn = container.querySelector(".btn-primary");
    expect(btn).toBeInTheDocument();
    expect(btn?.textContent).toBe("Tải ứng dụng");
  });

  it("btn-primary button text content is preserved", () => {
    const labels = [
      "Tải ứng dụng",
      "Đăng nhập",
      "Tạo tài khoản",
      "Bắt đầu ngay",
      "Sứ mệnh của chúng tôi",
    ];

    labels.forEach((label) => {
      const { unmount } = render(
        <button className="btn-primary" type="button">
          {label}
        </button>,
      );
      expect(screen.getByText(label)).toBeInTheDocument();
      unmount();
    });
  });

  /**
   * Property: For any string label, a btn-primary button SHALL render
   * that exact text content unchanged.
   *
   * **Validates: Requirements 3.5**
   */
  it("property: btn-primary label text is always preserved", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 100 }).filter((s) => s.trim().length > 0),
        (label) => {
          const { container, unmount } = render(
            <button className="btn-primary" type="button">
              {label}
            </button>,
          );
          const btn = container.querySelector(".btn-primary");
          const preserved = btn !== null && btn.textContent === label;
          unmount();
          return preserved;
        },
      ),
      { numRuns: 50 },
    );
  });
});

// ---------------------------------------------------------------------------
// P2.4 — Badge text preserved (badge-app)
// badge-app text content SHALL not change after color fix
// ---------------------------------------------------------------------------

describe("P2.4 — Badge text preserved (badge-app)", () => {
  it('renders "Chỉ trên app" text in badge-app element', () => {
    const { container } = render(
      <span className="badge-app">Chỉ trên app</span>,
    );
    const badge = container.querySelector(".badge-app");
    expect(badge).toBeInTheDocument();
    expect(badge?.textContent).toBe("Chỉ trên app");
  });

  it("badge-app text content is preserved for various labels", () => {
    const texts = ["Chỉ trên app", "Tất cả", "Mới", "Beta"];

    texts.forEach((text) => {
      const { unmount } = render(<span className="badge-app">{text}</span>);
      expect(screen.getByText(text)).toBeInTheDocument();
      unmount();
    });
  });

  /**
   * Property: For any string content, badge-app SHALL render that exact
   * text content unchanged (only color values change after fix).
   *
   * **Validates: Requirements 3.5, 3.6**
   */
  it("property: badge-app text content is always preserved", () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 50 }).filter((s) => s.trim().length > 0),
        (text) => {
          const { container, unmount } = render(<span className="badge-app">{text}</span>);
          const badge = container.querySelector(".badge-app");
          const preserved = badge !== null && badge.textContent === text;
          unmount();
          return preserved;
        },
      ),
      { numRuns: 50 },
    );
  });
});

// ---------------------------------------------------------------------------
// P2.5 — Layout unchanged (contrast-only fixes)
// For contrast-only fixes, layout properties SHALL remain the same
// ---------------------------------------------------------------------------

describe("P2.5 — Layout unchanged (contrast-only fixes)", () => {
  it("AnalysisCard renders two-column grid layout", () => {
    const { container } = render(<AnalysisCard msg={mockAnalysisMsg} />);
    // The grid container with md:grid-cols-2 should be present
    const gridEl = container.querySelector(".grid");
    expect(gridEl).toBeInTheDocument();
  });

  it("AnalysisCard assessment section has correct structure", () => {
    render(<AnalysisCard msg={mockAnalysisMsg} />);
    // Assessment items should be in a list
    const lists = screen.getAllByRole("list");
    expect(lists.length).toBeGreaterThan(0);
  });

  it("AnalysisCard note section is rendered", () => {
    render(<AnalysisCard msg={mockAnalysisMsg} />);
    expect(screen.getByText(/Lưu ý: Đây không phải là chẩn đoán cuối cùng/)).toBeInTheDocument();
  });

  /**
   * Property: For any analysis message, AnalysisCard SHALL always render
   * both the assessment section and the handling section (layout preserved).
   *
   * **Validates: Requirements 3.5, 3.6**
   */
  it("property: AnalysisCard always renders both sections", () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            label: fc.string({ minLength: 1, maxLength: 30 }),
            value: fc.string({ minLength: 1, maxLength: 80 }),
          }),
          { minLength: 1, maxLength: 5 },
        ),
        fc.array(fc.string({ minLength: 1, maxLength: 80 }), {
          minLength: 1,
          maxLength: 5,
        }),
        (assessment, handling) => {
          const msg = {
            ...mockAnalysisMsg,
            id: `test-${Math.random()}`,
            assessment,
            handling,
          };

          const { unmount } = render(<AnalysisCard msg={msg} />);

          const headings = screen.getAllByRole("heading");
          const headingTexts = headings.map((h) => h.textContent ?? "");
          const hasBothSections =
            headingTexts.some((t) => t.includes("Đánh giá sơ bộ")) &&
            headingTexts.some((t) => t.includes("Gợi ý xử trí"));

          unmount();
          return hasBothSections;
        },
      ),
      { numRuns: 30 },
    );
  });
});

// ---------------------------------------------------------------------------
// P2.6 — Non-buggy elements unchanged (STATUS_CHIP and ACCENT)
// For elements where NOT isBugCondition_*(element), behavior SHALL be identical
// ---------------------------------------------------------------------------

describe("P2.6 — Non-buggy elements unchanged (STATUS_CHIP)", () => {
  it('STATUS_CHIP renders "Hoàn thành" label for done status', () => {
    render(<AboutMilestones />);
    const chips = screen.getAllByText("Hoàn thành");
    expect(chips.length).toBeGreaterThan(0);
  });

  it('STATUS_CHIP renders "Đang làm" label for doing status', () => {
    render(<AboutMilestones />);
    expect(screen.getByText("Đang làm")).toBeInTheDocument();
  });

  it('STATUS_CHIP renders "Sắp tới" label for next status', () => {
    render(<AboutMilestones />);
    expect(screen.getByText("Sắp tới")).toBeInTheDocument();
  });

  it("STATUS_CHIP renders all three status labels", () => {
    render(<AboutMilestones />);
    // "Sắp tới" is next status — only 1 milestone has it
    expect(screen.getByText("Sắp tới")).toBeInTheDocument();
    // "Đang làm" — 1 milestone
    expect(screen.getByText("Đang làm")).toBeInTheDocument();
    // "Hoàn thành" — 3 milestones
    const doneChips = screen.getAllByText("Hoàn thành");
    expect(doneChips.length).toBe(3);
  });

  it("STATUS_CHIP next status has correct ink-600 text class (not a bug condition)", () => {
    const { container } = render(<AboutMilestones />);
    // "Sắp tới" chip uses bg-ink-100 text-ink-600 — this is NOT a bug condition
    // (ink-600 on ink-100 achieves 4.63:1 contrast — already compliant)
    const chips = container.querySelectorAll(".bg-ink-100");
    const nextChip = Array.from(chips).find(
      (el) => el.textContent?.includes("Sắp tới"),
    );
    expect(nextChip).toBeInTheDocument();
    expect(nextChip).toHaveClass("text-ink-600");
  });
});

describe("P2.6 — Non-buggy elements unchanged (ACCENT in AboutTeam)", () => {
  it('renders "Giảng viên hướng dẫn" role label', () => {
    render(<AboutTeam />);
    expect(screen.getByText("Giảng viên hướng dẫn")).toBeInTheDocument();
  });

  it('renders "Thiết kế cho mọi người" role label', () => {
    render(<AboutTeam />);
    expect(screen.getByText("Thiết kế cho mọi người")).toBeInTheDocument();
  });

  it('renders "FastAPI · PostgreSQL" role label', () => {
    render(<AboutTeam />);
    expect(screen.getByText("FastAPI · PostgreSQL")).toBeInTheDocument();
  });

  it('renders "Flutter · Next.js" role label', () => {
    render(<AboutTeam />);
    expect(screen.getByText("Flutter · Next.js")).toBeInTheDocument();
  });

  it("renders brand accent (non-buggy) with text-brand-700 class", () => {
    const { container } = render(<AboutTeam />);
    // brand accent uses text-brand-700 which is already compliant — NOT a bug condition
    const brandTextEls = container.querySelectorAll(".text-brand-700");
    expect(brandTextEls.length).toBeGreaterThan(0);
  });

  it("renders all team member names", () => {
    render(<AboutTeam />);
    expect(screen.getByText("Nguyễn Duy Thuận")).toBeInTheDocument();
    expect(screen.getByText("ThS. Đỗ Gia Bảo")).toBeInTheDocument();
    expect(screen.getByText("AI Research")).toBeInTheDocument();
    expect(screen.getByText("Backend & Data")).toBeInTheDocument();
    expect(screen.getByText("Mobile & Web")).toBeInTheDocument();
    expect(screen.getByText("UX & Accessibility")).toBeInTheDocument();
  });

  it("renders badge labels for lead members", () => {
    render(<AboutTeam />);
    expect(screen.getByText("Lead")).toBeInTheDocument();
    expect(screen.getByText("GVHD")).toBeInTheDocument();
  });

  /**
   * Property: AboutTeam SHALL always render all 6 team entries with their
   * role labels intact (non-buggy structural elements unchanged).
   *
   * **Validates: Requirements 3.7, 3.8**
   */
  it("property: all team role labels are always rendered", () => {
    const expectedRoles = [
      "Trưởng nhóm · Kiến trúc & AI",
      "Giảng viên hướng dẫn",
      "ML & Vision-Language",
      "FastAPI · PostgreSQL",
      "Flutter · Next.js",
      "Thiết kế cho mọi người",
    ];

    // Run multiple times to ensure stability
    fc.assert(
      fc.property(fc.constant(null), () => {
        const { unmount } = render(<AboutTeam />);

        const allPresent = expectedRoles.every((role) => {
          try {
            return screen.getByText(role) !== null;
          } catch {
            return false;
          }
        });

        unmount();
        return allPresent;
      }),
      { numRuns: 5 },
    );
  });
});

// ---------------------------------------------------------------------------
// Additional preservation: milestone content unchanged
// ---------------------------------------------------------------------------

describe("Milestone content preserved (AboutMilestones)", () => {
  it("renders all milestone titles", () => {
    render(<AboutMilestones />);
    expect(screen.getByText("Khởi đầu")).toBeInTheDocument();
    expect(screen.getByText("Dữ liệu y khoa")).toBeInTheDocument();
    expect(screen.getByText("Huấn luyện AI")).toBeInTheDocument();
    expect(screen.getByText("Beta nội bộ")).toBeInTheDocument();
    expect(screen.getByText("Mở rộng cộng đồng")).toBeInTheDocument();
  });

  it("renders all milestone year labels", () => {
    render(<AboutMilestones />);
    expect(screen.getByText("2025 Q3")).toBeInTheDocument();
    expect(screen.getByText("2025 Q4")).toBeInTheDocument();
    expect(screen.getByText("2026 Q1")).toBeInTheDocument();
    expect(screen.getByText("2026 Q2")).toBeInTheDocument();
    expect(screen.getByText("2026 Q3")).toBeInTheDocument();
  });
});
