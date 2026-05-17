/**
 * Integration tests for the chat triage flow.
 *
 * Validates: Requirements 2.3.1 (Chat AI — triage call, summary/recommendations
 * rendering, RED urgency banner, error handling).
 *
 * Scenarios covered:
 *   1. Success case: user sends a message → user bubble appears → bot bubble
 *      shows the `summary` text and each item in the `recommendations` list.
 *   2. RED urgency case: triage returns `urgency_level: "RED"` → the RED
 *      emergency banner "Gọi 115 ngay" is shown with a `tel:115` link.
 *   3. Error case: triage API fails → an error bubble is shown in the chat.
 *
 * Strategy:
 *   - Mock `lib/api/consult` directly (same pattern as LoginModal tests) to
 *     control triage responses without MSW URL matching complexity in jsdom.
 *   - Render a thin `ChatPageContent` wrapper that mirrors the real page's
 *     state machine and calls the mocked `triage()` function.
 *   - Mock `next/navigation` so `useSearchParams()` works in jsdom.
 *   - For direct prop rendering tests, render `ChatPanel` with controlled
 *     props to verify the component's rendering logic independently.
 */

import { describe, it, expect, vi, beforeAll } from "vitest";
import {
  render,
  screen,
  fireEvent,
  waitFor,
} from "@testing-library/react";
import { Suspense, useState, useCallback } from "react";

// ---------------------------------------------------------------------------
// jsdom polyfills — jsdom does not implement scrollIntoView
// ---------------------------------------------------------------------------

beforeAll(() => {
  window.HTMLElement.prototype.scrollIntoView = vi.fn();
});

// ---------------------------------------------------------------------------
// Mock next/navigation — must be hoisted before component imports
// ---------------------------------------------------------------------------

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/app/chat",
}));

// ---------------------------------------------------------------------------
// Mock lib/api/consult — control triage responses without MSW complexity
// ---------------------------------------------------------------------------

vi.mock("../../lib/api/consult", () => ({
  triage: vi.fn(),
  triageHistory: vi.fn(() => Promise.resolve([])),
}));

// ---------------------------------------------------------------------------
// Component + API imports (after mocks)
// ---------------------------------------------------------------------------

import { ChatPanel } from "../chat/ChatPanel";
import type { ChatMessage } from "../chat/ChatPanel";
import * as consultApi from "../../lib/api/consult";
import { buildTriageResponse } from "../../test/msw/handlers";
import { ApiError } from "../../lib/api/errors";

// Typed reference to the mocked triage function.
const triageMock = consultApi.triage as ReturnType<typeof vi.fn>;

// ---------------------------------------------------------------------------
// Thin wrapper that mirrors the real ChatPageContent state machine
// ---------------------------------------------------------------------------

/**
 * Minimal page-level state owner that wires `ChatPanel` to the mocked
 * `triage()` API call — same logic as `ChatPageContent` in the real page.
 * Wrapped in a Suspense boundary because `ChatPanel` calls `useSearchParams()`.
 */
function ChatPageWrapper() {
  return (
    <Suspense fallback={<div>Loading…</div>}>
      <ChatPageContent />
    </Suspense>
  );
}

function ChatPageContent() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isPending, setIsPending] = useState(false);
  const [urgencyLevel, setUrgencyLevel] = useState<string | undefined>(
    undefined,
  );

  const handleSend = useCallback(async (message: string) => {
    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      text: message,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsPending(true);

    try {
      const response = await consultApi.triage({
        symptom_text: message,
        locale: "vi-VN",
      });

      setUrgencyLevel(response.urgency_level);

      const botMsg: ChatMessage = {
        id: `b-${Date.now()}`,
        role: "bot",
        text: response.summary,
        recommendations: response.recommendations,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: unknown) {
      const errorText =
        err instanceof Error
          ? err.message
          : "Đã xảy ra lỗi. Vui lòng thử lại.";

      const errMsg: ChatMessage = {
        id: `e-${Date.now()}`,
        role: "bot",
        text: errorText,
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsPending(false);
    }
  }, []);

  return (
    <ChatPanel
      messages={messages}
      isPending={isPending}
      urgencyLevel={urgencyLevel}
      onSend={handleSend}
    />
  );
}

// ---------------------------------------------------------------------------
// Helper: type a message and click Send
// ---------------------------------------------------------------------------

function sendMessage(text: string) {
  const textarea = screen.getByRole("textbox", {
    name: /nhập câu hỏi cho medisign ai/i,
  });
  fireEvent.change(textarea, { target: { value: text } });
  fireEvent.click(screen.getByRole("button", { name: /gửi tin nhắn/i }));
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("ChatPanel integration — chat triage (Requirements 2.3.1)", () => {
  // -------------------------------------------------------------------------
  // 1. Success case: summary + recommendations rendered
  // -------------------------------------------------------------------------

  describe("success case", () => {
    it("renders the user bubble after sending a message", async () => {
      triageMock.mockResolvedValueOnce(
        buildTriageResponse({
          urgency_level: "GREEN",
          summary: "Triệu chứng nhẹ, có thể theo dõi tại nhà.",
          recommendations: ["Uống nhiều nước.", "Nghỉ ngơi đầy đủ."],
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị đau đầu nhẹ");

      // User bubble should appear immediately (optimistic).
      await waitFor(() => {
        expect(screen.getByText("Tôi bị đau đầu nhẹ")).toBeInTheDocument();
      });
    });

    it("renders the bot summary text after triage responds", async () => {
      triageMock.mockResolvedValueOnce(
        buildTriageResponse({
          urgency_level: "GREEN",
          summary: "Triệu chứng nhẹ, có thể theo dõi tại nhà.",
          recommendations: ["Uống nhiều nước.", "Nghỉ ngơi đầy đủ."],
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị đau đầu nhẹ");

      await waitFor(() => {
        expect(
          screen.getByText("Triệu chứng nhẹ, có thể theo dõi tại nhà."),
        ).toBeInTheDocument();
      });
    });

    it("renders each recommendation as a list item", async () => {
      triageMock.mockResolvedValueOnce(
        buildTriageResponse({
          urgency_level: "GREEN",
          summary: "Triệu chứng nhẹ, có thể theo dõi tại nhà.",
          recommendations: ["Uống nhiều nước.", "Nghỉ ngơi đầy đủ."],
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị đau đầu nhẹ");

      await waitFor(() => {
        expect(screen.getByText("Uống nhiều nước.")).toBeInTheDocument();
        expect(screen.getByText("Nghỉ ngơi đầy đủ.")).toBeInTheDocument();
      });
    });

    it("renders all recommendations inside the 'Khuyến nghị' list", async () => {
      triageMock.mockResolvedValueOnce(
        buildTriageResponse({
          urgency_level: "YELLOW",
          summary: "Cần theo dõi thêm.",
          recommendations: ["Đo nhiệt độ mỗi 4 giờ.", "Uống thuốc hạ sốt nếu cần."],
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị sốt 38 độ");

      await waitFor(() => {
        const list = screen.getByRole("list", { name: /khuyến nghị/i });
        expect(list).toBeInTheDocument();
        // Query list items scoped to the recommendations list only.
        const recItems = Array.from(list.querySelectorAll("li"));
        expect(recItems).toHaveLength(2);
        expect(recItems[0]).toHaveTextContent("Đo nhiệt độ mỗi 4 giờ.");
        expect(recItems[1]).toHaveTextContent("Uống thuốc hạ sốt nếu cần.");
      });
    });
  });

  // -------------------------------------------------------------------------
  // 2. RED urgency case: banner "Gọi 115 ngay" with tel:115 link
  // -------------------------------------------------------------------------

  describe("RED urgency case", () => {
    it("shows the RED emergency banner when urgency_level is RED", async () => {
      triageMock.mockResolvedValueOnce(
        buildTriageResponse({
          urgency_level: "RED",
          summary: "Triệu chứng nguy hiểm, cần cấp cứu ngay.",
          recommendations: ["Gọi 115 ngay lập tức."],
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị đau ngực dữ dội");

      await waitFor(() => {
        // The banner has role="alert" and contains "Gọi 115 ngay".
        const banner = screen.getByRole("alert");
        expect(banner).toBeInTheDocument();
        expect(banner).toHaveTextContent(/gọi 115 ngay/i);
      });
    });

    it("renders a tel:115 link inside the RED banner", async () => {
      triageMock.mockResolvedValueOnce(
        buildTriageResponse({
          urgency_level: "RED",
          summary: "Triệu chứng nguy hiểm.",
          recommendations: ["Gọi cấp cứu ngay."],
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị khó thở đột ngột");

      await waitFor(() => {
        const callLink = screen.getByRole("link", {
          name: /gọi 115 ngay — cấp cứu/i,
        });
        expect(callLink).toBeInTheDocument();
        expect(callLink).toHaveAttribute("href", "tel:115");
      });
    });

    it("does NOT show the RED banner for GREEN urgency", async () => {
      triageMock.mockResolvedValueOnce(
        buildTriageResponse({
          urgency_level: "GREEN",
          summary: "Không có gì đáng lo ngại.",
          recommendations: [],
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị sổ mũi nhẹ");

      await waitFor(() => {
        expect(
          screen.getByText("Không có gì đáng lo ngại."),
        ).toBeInTheDocument();
      });

      // No alert banner should be present.
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });

    it("does NOT show the RED banner for YELLOW urgency", async () => {
      triageMock.mockResolvedValueOnce(
        buildTriageResponse({
          urgency_level: "YELLOW",
          summary: "Cần theo dõi thêm.",
          recommendations: ["Nghỉ ngơi."],
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị sốt nhẹ");

      await waitFor(() => {
        expect(screen.getByText("Cần theo dõi thêm.")).toBeInTheDocument();
      });

      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });
  });

  // -------------------------------------------------------------------------
  // 3. Error case: triage fails → error bubble shown
  // -------------------------------------------------------------------------

  describe("error case", () => {
    it("shows an error bubble when the triage API returns 500", async () => {
      triageMock.mockRejectedValueOnce(
        new ApiError({
          code: "INTERNAL_SERVER_ERROR",
          message: "Hệ thống đang bận, vui lòng thử lại sau.",
          status: 500,
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị đau bụng");

      // A bot bubble with an error message should appear.
      await waitFor(() => {
        expect(
          screen.getByText("Hệ thống đang bận, vui lòng thử lại sau."),
        ).toBeInTheDocument();
      });
    });

    it("shows an error bubble when the network request fails", async () => {
      triageMock.mockRejectedValueOnce(
        new ApiError({
          code: "NETWORK_ERROR",
          message: "Mất kết nối. Kiểm tra mạng và thử lại.",
          status: 0,
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị chóng mặt");

      await waitFor(() => {
        expect(
          screen.getByText("Mất kết nối. Kiểm tra mạng và thử lại."),
        ).toBeInTheDocument();
      });
    });

    it("still shows the user bubble even when triage fails", async () => {
      triageMock.mockRejectedValueOnce(
        new ApiError({
          code: "TIMEOUT_ERROR",
          message: "Yêu cầu hết thời gian chờ.",
          status: 0,
        }),
      );

      render(<ChatPageWrapper />);
      sendMessage("Tôi bị mệt mỏi");

      // The user bubble should always be present (optimistic add).
      await waitFor(() => {
        expect(screen.getByText("Tôi bị mệt mỏi")).toBeInTheDocument();
      });

      // And a bot error bubble should follow.
      await waitFor(() => {
        expect(
          screen.getByText("Yêu cầu hết thời gian chờ."),
        ).toBeInTheDocument();
      });
    });
  });

  // -------------------------------------------------------------------------
  // 4. ChatPanel unit-level: direct prop rendering (no API call)
  // -------------------------------------------------------------------------

  describe("ChatPanel direct prop rendering", () => {
    it("renders summary and recommendations from props without API call", () => {
      const messages: ChatMessage[] = [
        { id: "u1", role: "user", text: "Tôi bị đau đầu" },
        {
          id: "b1",
          role: "bot",
          text: "Triệu chứng nhẹ.",
          recommendations: ["Uống nước.", "Nghỉ ngơi."],
        },
      ];

      render(
        <Suspense fallback={null}>
          <ChatPanel messages={messages} onSend={vi.fn()} />
        </Suspense>,
      );

      expect(screen.getByText("Tôi bị đau đầu")).toBeInTheDocument();
      expect(screen.getByText("Triệu chứng nhẹ.")).toBeInTheDocument();
      expect(screen.getByText("Uống nước.")).toBeInTheDocument();
      expect(screen.getByText("Nghỉ ngơi.")).toBeInTheDocument();
    });

    it("shows RED banner when urgencyLevel='RED' prop is passed", () => {
      render(
        <Suspense fallback={null}>
          <ChatPanel
            messages={[]}
            onSend={vi.fn()}
            urgencyLevel="RED"
          />
        </Suspense>,
      );

      const banner = screen.getByRole("alert");
      expect(banner).toBeInTheDocument();
      expect(banner).toHaveTextContent(/gọi 115 ngay/i);

      const callLink = screen.getByRole("link", {
        name: /gọi 115 ngay — cấp cứu/i,
      });
      expect(callLink).toHaveAttribute("href", "tel:115");
    });

    it("does NOT show RED banner when urgencyLevel is undefined", () => {
      render(
        <Suspense fallback={null}>
          <ChatPanel messages={[]} onSend={vi.fn()} />
        </Suspense>,
      );

      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });

    it("does NOT show RED banner when urgencyLevel='GREEN'", () => {
      render(
        <Suspense fallback={null}>
          <ChatPanel messages={[]} onSend={vi.fn()} urgencyLevel="GREEN" />
        </Suspense>,
      );

      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });
  });
});
