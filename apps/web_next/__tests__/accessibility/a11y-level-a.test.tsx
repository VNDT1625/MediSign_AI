/**
 * Bug Condition Exploration Tests — Level A Semantic Errors
 *
 * **Validates: Requirements 1.2, 1.3, 1.4**
 *
 * CRITICAL: These tests are EXPECTED TO FAIL on unfixed code.
 * Failure confirms the bugs exist. DO NOT fix the code or tests when they fail.
 *
 * Bug conditions being explored:
 *   - isBugCondition_A2: headings[i].level - headings[i-1].level > 1
 *     (H1 "MediSign AI" → H3 "Đánh giá sơ bộ" — gap = 2)
 *   - isBugCondition_A3: NOT dialog.hasAttribute("tabindex")
 *     (div[role="dialog"] missing tabindex="-1")
 *   - isBugCondition_A3: focus escapes dialog on Tab
 *   - isBugCondition_A3: focus does not return to trigger on close
 */

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

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
// Helpers
// ---------------------------------------------------------------------------

/**
 * Returns the numeric heading level (1–6) from an HTMLElement's tag name.
 * e.g. <h1> → 1, <h3> → 3
 */
function getHeadingLevel(el: HTMLElement): number {
  const tag = el.tagName.toLowerCase();
  const match = tag.match(/^h([1-6])$/);
  if (!match) throw new Error(`Element is not a heading: ${tag}`);
  return parseInt(match[1], 10);
}

// ---------------------------------------------------------------------------
// Test A2 — Heading Hierarchy Skip
// ---------------------------------------------------------------------------

describe("Bug Condition A2 — Heading Hierarchy Skip (EXPECTED TO FAIL on unfixed code)", () => {
  /**
   * isBugCondition_A2: headings[i].level - headings[i-1].level > 1
   *
   * Expected counterexample on unfixed code:
   *   headings[0] = H1("MediSign AI")  level=1
   *   headings[1] = H3("Đánh giá sơ bộ")  level=3
   *   gap = 3 - 1 = 2 > 1  → BUG CONFIRMED
   */
  it("A2: AnalysisCard headings SHALL NOT skip levels (H1→H3 gap=2 is a bug)", async () => {
    // Dynamically import ChatMain to avoid module-level issues with Next.js
    const { ChatMain } = await import("@/components/chat/ChatMain");

    render(<ChatMain />);

    // Query all headings in the rendered output
    const headings = screen.getAllByRole("heading");

    // Extract heading levels
    const levels = headings.map((h) => ({
      level: getHeadingLevel(h),
      text: h.textContent?.trim() ?? "",
    }));

    // Log for documentation purposes
    console.log(
      "[A2 counterexample] Heading sequence found:",
      levels.map((h) => `H${h.level}("${h.text}")`).join(" → "),
    );

    // Assert: no heading should skip more than 1 level
    // This WILL FAIL on unfixed code because H1 → H3 has gap = 2
    for (let i = 1; i < levels.length; i++) {
      const gap = levels[i].level - levels[i - 1].level;
      if (gap > 1) {
        console.log(
          `[A2 counterexample] BUG CONFIRMED: H${levels[i - 1].level}("${levels[i - 1].text}") → H${levels[i].level}("${levels[i].text}") — gap = ${gap}`,
        );
      }
      expect(gap).toBeLessThanOrEqual(1);
    }
  });
});

// ---------------------------------------------------------------------------
// Test A3 — Dialog tabindex missing
// ---------------------------------------------------------------------------

describe("Bug Condition A3 — Dialog tabindex missing (EXPECTED TO FAIL on unfixed code)", () => {
  /**
   * isBugCondition_A3: NOT dialog.hasAttribute("tabindex")
   *
   * Expected counterexample on unfixed code:
   *   div[role="dialog"] has no tabindex attribute → BUG CONFIRMED
   */
  it("A3: dialog SHALL have tabindex=-1 (missing tabindex is a bug)", async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    render(<LoginModal open={true} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog");

    // Log for documentation
    const hasTabindex = dialog.hasAttribute("tabindex");
    const tabindexValue = dialog.getAttribute("tabindex");
    console.log(
      `[A3 counterexample] dialog.hasAttribute("tabindex") = ${hasTabindex}, value = ${tabindexValue}`,
    );

    if (!hasTabindex) {
      console.log(
        "[A3 counterexample] BUG CONFIRMED: div[role='dialog'] has no tabindex attribute",
      );
    }

    // Assert: dialog MUST have tabindex="-1"
    // This WILL FAIL on unfixed code because the outer div has no tabindex
    expect(dialog).toHaveAttribute("tabindex", "-1");
  });
});

// ---------------------------------------------------------------------------
// Test A3 — Focus trap
// ---------------------------------------------------------------------------

describe("Bug Condition A3 — Focus trap (EXPECTED TO FAIL on unfixed code)", () => {
  /**
   * isBugCondition_A3: focus escapes dialog on Tab
   *
   * Expected counterexample on unfixed code:
   *   After Tab presses, document.activeElement is outside the dialog
   */
  it("A3: focus SHALL remain inside dialog after Tab presses (focus escape is a bug)", async () => {
    const { LoginModal } = await import("@/components/LoginModal");

    const user = userEvent.setup();

    render(<LoginModal open={true} onClose={vi.fn()} />);

    const dialog = screen.getByRole("dialog");

    // Tab 10 times and check focus stays inside dialog each time
    let focusEscaped = false;
    for (let i = 0; i < 10; i++) {
      await user.tab();
      const isInsideDialog = dialog.contains(document.activeElement);
      if (!isInsideDialog) {
        focusEscaped = true;
        console.log(
          `[A3 counterexample] BUG CONFIRMED: After Tab #${i + 1}, focus escaped dialog. activeElement = ${document.activeElement?.tagName} (${(document.activeElement as HTMLElement)?.getAttribute?.("aria-label") ?? document.activeElement?.textContent?.trim()})`,
        );
      }
      // Assert inside the loop — will fail on first escape
      expect(isInsideDialog).toBe(true);
    }

    if (!focusEscaped) {
      console.log("[A3 focus trap] Focus stayed inside dialog for all 10 Tab presses");
    }
  });
});

// ---------------------------------------------------------------------------
// Test A3 — Focus return on close
// ---------------------------------------------------------------------------

describe("Bug Condition A3 — Focus return on close (EXPECTED TO FAIL on unfixed code)", () => {
  /**
   * isBugCondition_A3: focus does not return to trigger element on close
   *
   * Expected counterexample on unfixed code:
   *   After closing modal, document.activeElement !== triggerButton
   */
  it("A3: focus SHALL return to trigger element when modal closes (no return is a bug)", async () => {
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

    // Focus the trigger button (simulates the state before modal was opened)
    const triggerButton = document.getElementById("trigger-btn") as HTMLButtonElement;
    triggerButton.focus();

    // Verify trigger has focus before we interact with modal
    expect(document.activeElement).toBe(triggerButton);

    // Click the close button inside the modal
    const closeBtn = screen.getByRole("button", { name: /Quay về trang chủ/i });
    await user.click(closeBtn);

    // Log for documentation
    const activeAfterClose = document.activeElement;
    const returnedToTrigger = activeAfterClose === triggerButton;
    console.log(
      `[A3 counterexample] After close: activeElement = ${activeAfterClose?.tagName}#${(activeAfterClose as HTMLElement)?.id} "${activeAfterClose?.textContent?.trim()}"`,
    );

    if (!returnedToTrigger) {
      console.log(
        "[A3 counterexample] BUG CONFIRMED: focus did NOT return to trigger button after modal close",
      );
    }

    // Assert: focus must return to trigger button
    // This WILL FAIL on unfixed code because handleRequestClose doesn't save/restore focus
    expect(document.activeElement).toBe(triggerButton);
  });
});

// ---------------------------------------------------------------------------
// Test A1 — Chat Input Label (Task 4.4 verification)
// ---------------------------------------------------------------------------

describe("Bug Condition A1 — Chat Input Label (EXPECTED TO PASS — label already present)", () => {
  /**
   * isBugCondition_A1: NOT hasAssociatedLabel(element) AND NOT hasAriaLabel(element)
   *
   * Verification: ChatMain Composer has <label htmlFor="chat-input-field"> + id="chat-input-field"
   * AND aria-label="Nhập câu hỏi cho MediSign AI" on the input.
   *
   * Expected: getByLabelText("Nhập câu hỏi cho MediSign AI") does NOT throw.
   *
   * **Validates: Requirements 1.1, 2.1, 3.1**
   */
  it("A1: ChatMain Composer input SHALL be accessible via getByLabelText", async () => {
    const { ChatMain } = await import("@/components/chat/ChatMain");

    render(<ChatMain />);

    // getByLabelText will find the input via:
    //   1. <label htmlFor="chat-input-field"> association, OR
    //   2. aria-label="Nhập câu hỏi cho MediSign AI" on the input
    // Either satisfies hasAssociatedLabel OR hasAriaLabel — NOT isBugCondition_A1
    // If this throws, the bug condition is active (no label found).
    const input = screen.getByLabelText("Nhập câu hỏi cho MediSign AI");

    // Use standard assertions that don't require jest-dom
    expect(input).not.toBeNull();
    expect(input.tagName.toLowerCase()).toBe("input");
    expect(input.getAttribute("id")).toBe("chat-input-field");

    console.log(
      "[A1 verification] Chat input is accessible via label. id =",
      input.getAttribute("id"),
      "aria-label =",
      input.getAttribute("aria-label"),
    );
  });

  it("A1: chat-input has both htmlFor label association AND aria-label (redundant for robustness)", async () => {
    const { ChatMain } = await import("@/components/chat/ChatMain");

    render(<ChatMain />);

    const input = screen.getByLabelText("Nhập câu hỏi cho MediSign AI");

    // Verify the <label htmlFor="chat-input-field"> association exists
    const label = document.querySelector('label[for="chat-input-field"]');
    expect(label).not.toBeNull();
    expect(label?.textContent?.trim()).toBe("Nhập câu hỏi cho MediSign AI");

    // Verify aria-label is also present (redundant, for audit tool robustness)
    expect(input.getAttribute("aria-label")).toBe("Nhập câu hỏi cho MediSign AI");
  });
});
