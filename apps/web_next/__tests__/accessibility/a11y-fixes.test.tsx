/**
 * Unit Tests — Level A Accessibility Fixes (Post-Fix Verification)
 *
 * **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**
 *
 * These tests verify that the Level A accessibility fixes are correctly
 * applied. They SHOULD PASS on fixed code.
 *
 * Fixes verified:
 *   - A2: AnalysisCard headings use H2 (no H1→H3 skip)
 *   - A3: LoginModal dialog has tabindex="-1", aria-modal="true", role="dialog"
 *   - A3: Focus is trapped inside dialog on Tab
 *   - A3: Focus returns to trigger element when modal closes
 *   - A1: ChatMain Composer input is accessible via getByLabelText
 */

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi, describe, it, expect, beforeEach } from "vitest";

// ---------------------------------------------------------------------------
// Try to import jest-axe — skip axe tests if not available
// ---------------------------------------------------------------------------

let axe: ((container: Element | Document) => Promise<unknown>) | null = null;
try {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const jestAxe = require("jest-axe");
  axe = jestAxe.axe;
  if (jestAxe.toHaveNoViolations) {
    expect.extend(jestAxe.toHaveNoViolations);
  }
} catch {
  // jest-axe not installed — axe tests will be skipped
  axe = null;
}

// ---------------------------------------------------------------------------
// Mock Next.js navigation hooks — LoginModal uses useRouter and useSearchParams
// ---------------------------------------------------------------------------

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/",
}));

// ---------------------------------------------------------------------------
// Mock useAuth — LoginModal calls useAuth() for login/register
// ---------------------------------------------------------------------------

vi.mock("@/lib/auth/useAuth", () => ({
  useAuth: () => ({
    state: { status: "unauthenticated" },
    isAuthenticated: false,
    login: vi.fn().mockResolvedValue(undefined),
    register: vi.fn().mockResolvedValue(undefined),
    logout: vi.fn().mockResolvedValue(undefined),
    changePassword: vi.fn().mockResolvedValue(undefined),
    hydrate: vi.fn().mockResolvedValue(undefined),
  }),
}));

// ---------------------------------------------------------------------------
// Mock useIntent — LoginModal calls useIntent() for smart redirect
// ---------------------------------------------------------------------------

vi.mock("@/lib/auth/useIntent", () => ({
  useIntent: () => ({
    set: vi.fn(),
    peek: vi.fn().mockReturnValue(null),
    consume: vi.fn().mockReturnValue({ redirectPath: "/app" }),
  }),
}));

// ---------------------------------------------------------------------------
// Mock data for AnalysisCard
// ---------------------------------------------------------------------------

const mockAnalysisMsg = {
  id: "m-fix-test",
  role: "ai" as const,
  kind: "analysis" as const,
  intro: "Dưới đây là phân tích sơ bộ dựa trên thông tin bạn cung cấp:",
  assessment: [
    { label: "Nhiệt độ:", value: "37.8°C (sốt nhẹ)" },
    { label: "Triệu chứng:", value: "Đau họng, ho khan" },
  ],
  handling: [
    "Nghỉ ngơi, uống nhiều nước ấm.",
    "Có thể dùng Paracetamol nếu sốt cao.",
  ],
  note: {
    text: "Lưu ý: Đây không phải là chẩn đoán cuối cùng.",
    time: "10:30",
  },
  time: "10:30",
};

// ---------------------------------------------------------------------------
// Helper: get numeric heading level from element tag name
// ---------------------------------------------------------------------------

function getHeadingLevel(el: HTMLElement): number {
  const tag = el.tagName.toLowerCase();
  const match = tag.match(/^h([1-6])$/);
  if (!match) throw new Error(`Element is not a heading: ${tag}`);
  return parseInt(match[1], 10);
}

// ---------------------------------------------------------------------------
// Test A2 — Heading hierarchy (post-fix)
// AnalysisCard should use H2 for "Đánh giá sơ bộ" and "Gợi ý xử trí"
// ---------------------------------------------------------------------------

describe("A2 — Heading hierarchy (post-fix)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("AnalysisCard headings do not skip levels (no gap > 1)", async () => {
    const { AnalysisCard } = await import("@/components/chat/ChatMain");

    render(<AnalysisCard msg={mockAnalysisMsg} />);

    const headings = screen.getAllByRole("heading");
    const levels = headings.map((h) => getHeadingLevel(h));

    // Assert: no consecutive heading gap > 1
    for (let i = 1; i < levels.length; i++) {
      const gap = levels[i] - levels[i - 1];
      expect(gap).toBeLessThanOrEqual(1);
    }
  });

  it('AnalysisCard renders "Đánh giá sơ bộ" as a level-2 heading', async () => {
    const { AnalysisCard } = await import("@/components/chat/ChatMain");

    render(<AnalysisCard msg={mockAnalysisMsg} />);

    // After fix: H3 → H2, so getByRole("heading", { level: 2 }) should find it
    const heading = screen.getByRole("heading", {
      level: 2,
      name: /Đánh giá sơ bộ/,
    });
    expect(heading).toBeInTheDocument();
  });

  it('AnalysisCard renders "Gợi ý xử trí" as a level-2 heading', async () => {
    const { AnalysisCard } = await import("@/components/chat/ChatMain");

    render(<AnalysisCard msg={mockAnalysisMsg} />);

    const heading = screen.getByRole("heading", {
      level: 2,
      name: /Gợi ý xử trí/,
    });
    expect(heading).toBeInTheDocument();
  });

  it("AnalysisCard heading tags are <h2> elements (not <h3>)", async () => {
    const { AnalysisCard } = await import("@/components/chat/ChatMain");

    const { container } = render(<AnalysisCard msg={mockAnalysisMsg} />);

    // Verify the actual DOM tags are h2
    const h2Elements = container.querySelectorAll("h2");
    const h3Elements = container.querySelectorAll("h3");

    // Should have exactly 2 h2 headings (Đánh giá sơ bộ + Gợi ý xử trí)
    expect(h2Elements.length).toBe(2);
    // Should have no h3 headings (the bug was h3 being used)
    expect(h3Elements.length).toBe(0);

    const headingTexts = Array.from(h2Elements).map((h) => h.textContent ?? "");
    expect(headingTexts.some((t) => t.includes("Đánh giá sơ bộ"))).toBe(true);
    expect(headingTexts.some((t) => t.includes("Gợi ý xử trí"))).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Test A3 — Dialog attributes (post-fix)
// LoginModal dialog should have tabindex="-1", aria-modal="true", role="dialog"
// ---------------------------------------------------------------------------

describe("A3 — Dialog attributes (post-fix)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('dialog has tabindex="-1"', async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    render(<LoginModal open={true} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog");
    expect(dialog.getAttribute("tabindex")).toBe("-1");
  });

  it('dialog has aria-modal="true"', async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    render(<LoginModal open={true} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog");
    expect(dialog.getAttribute("aria-modal")).toBe("true");
  });

  it('dialog has role="dialog"', async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    render(<LoginModal open={true} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog");
    expect(dialog.getAttribute("role")).toBe("dialog");
  });

  it("dialog has all required ARIA attributes together", async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    render(<LoginModal open={true} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog");
    expect(dialog.getAttribute("tabindex")).toBe("-1");
    expect(dialog.getAttribute("aria-modal")).toBe("true");
    expect(dialog.getAttribute("role")).toBe("dialog");
    expect(dialog.getAttribute("aria-labelledby")).toBe("login-title");
  });
});

// ---------------------------------------------------------------------------
// Test A3 — Focus trap (post-fix)
// Tabbing 10 times should keep focus inside the dialog
// ---------------------------------------------------------------------------

describe("A3 — Focus trap (post-fix)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("focus stays inside dialog after 10 Tab presses", async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    const user = userEvent.setup();

    render(<LoginModal open={true} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog");

    // Tab 10 times — focus must remain inside dialog each time
    for (let i = 0; i < 10; i++) {
      await user.tab();
      const isInsideDialog = dialog.contains(document.activeElement);
      expect(isInsideDialog).toBe(true);
    }
  });

  it("focus stays inside dialog after Shift+Tab presses (reverse cycle)", async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    const user = userEvent.setup();

    render(<LoginModal open={true} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog");

    // Shift+Tab 5 times — focus must remain inside dialog
    for (let i = 0; i < 5; i++) {
      await user.tab({ shift: true });
      const isInsideDialog = dialog.contains(document.activeElement);
      expect(isInsideDialog).toBe(true);
    }
  });
});

// ---------------------------------------------------------------------------
// Test A3 — Focus return (post-fix)
// Focus should return to trigger button when modal closes
// ---------------------------------------------------------------------------

describe("A3 — Focus return on close (post-fix)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("focus returns to trigger button when modal is closed via close button", async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    const user = userEvent.setup();
    const onClose = vi.fn();

    render(
      <div>
        <button id="trigger-btn" type="button">
          Đăng nhập
        </button>
        <LoginModal open={true} onClose={onClose} />
      </div>,
    );

    // Focus the trigger button (simulates state before modal was opened)
    const triggerButton = document.getElementById("trigger-btn") as HTMLButtonElement;
    triggerButton.focus();
    expect(document.activeElement).toBe(triggerButton);

    // Click the close button inside the modal
    const closeBtn = screen.getByRole("button", { name: /Quay về trang chủ/i });
    await user.click(closeBtn);

    // After close, focus should return to the trigger button
    expect(document.activeElement).toBe(triggerButton);
  });

  it("focus returns to trigger button when modal is closed via ESC key", async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    const user = userEvent.setup();
    const onClose = vi.fn();

    render(
      <div>
        <button id="trigger-esc-btn" type="button">
          Mở modal
        </button>
        <LoginModal open={true} onClose={onClose} />
      </div>,
    );

    // Focus the trigger button
    const triggerButton = document.getElementById("trigger-esc-btn") as HTMLButtonElement;
    triggerButton.focus();
    expect(document.activeElement).toBe(triggerButton);

    // Press ESC to close the modal
    await user.keyboard("{Escape}");

    // After ESC close, focus should return to the trigger button
    expect(document.activeElement).toBe(triggerButton);
  });
});

// ---------------------------------------------------------------------------
// Test A1 — Chat input label (post-fix)
// ChatMain Composer input should be accessible via getByLabelText
// ---------------------------------------------------------------------------

describe("A1 — Chat input label (post-fix)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("ChatMain Composer input is accessible via getByLabelText (does not throw)", async () => {
    const { ChatMain } = await import("@/components/chat/ChatMain");

    render(<ChatMain />);

    // getByLabelText will find the input via:
    //   1. <label htmlFor="chat-input-field"> association, OR
    //   2. aria-label="Nhập câu hỏi cho MediSign AI" on the input
    // This should NOT throw after the fix
    const input = screen.getByLabelText(/Nhập câu hỏi/);
    expect(input).toBeInTheDocument();
    expect(input.tagName.toLowerCase()).toBe("input");
  });

  it("chat input has id='chat-input-field' matching the label's htmlFor", async () => {
    const { ChatMain } = await import("@/components/chat/ChatMain");

    render(<ChatMain />);

    const input = screen.getByLabelText(/Nhập câu hỏi/);
    expect(input.getAttribute("id")).toBe("chat-input-field");

    // Verify the <label htmlFor="chat-input-field"> association exists
    const label = document.querySelector('label[for="chat-input-field"]');
    expect(label).toBeInTheDocument();
  });

  it("chat input has aria-label for redundant accessibility", async () => {
    const { ChatMain } = await import("@/components/chat/ChatMain");

    render(<ChatMain />);

    const input = screen.getByLabelText(/Nhập câu hỏi/);
    // aria-label provides redundant labeling for audit tool robustness
    expect(input.getAttribute("aria-label")).toMatch(/Nhập câu hỏi/);
  });
});

// ---------------------------------------------------------------------------
// Axe-core tests (skipped if jest-axe is not installed)
// ---------------------------------------------------------------------------

describe("Axe-core accessibility checks (post-fix)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("AnalysisCard has no axe violations (skipped if jest-axe unavailable)", async () => {
    if (!axe) {
      console.log("[axe] jest-axe not installed — skipping axe test");
      return;
    }

    const { AnalysisCard } = await import("@/components/chat/ChatMain");
    const { container } = render(<AnalysisCard msg={mockAnalysisMsg} />);

    const results = await axe(container);
    // @ts-expect-error — toHaveNoViolations is added by jest-axe extend
    expect(results).toHaveNoViolations();
  });

  it("LoginModal has no axe violations when open (skipped if jest-axe unavailable)", async () => {
    if (!axe) {
      console.log("[axe] jest-axe not installed — skipping axe test");
      return;
    }

    const { LoginModal } = await import("@/components/LoginModal");
    const { container } = render(<LoginModal open={true} onClose={vi.fn()} />);

    const results = await axe(container);
    // @ts-expect-error — toHaveNoViolations is added by jest-axe extend
    expect(results).toHaveNoViolations();
  });
});
