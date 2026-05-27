"use client";

/**
 * Executor — chay lenh tu intent matcher tren browser DOM/Next router.
 * Khong goi backend, khong AI. Tat ca cuc bo.
 */

import type { IntentMatch, FontDir } from "./intents";
import {
  scrollToNextSection,
  scrollToPrevSection,
  scrollToSection,
  PAGE_SECTIONS,
} from "./pageScenarios";

export interface ExecuteContext {
  navigate: (path: string) => void;
  closeOverlay: () => void;
  stopListening: () => void;
  /** Click DOM hook do trang chu dong cung cap (vd: mo modal login). */
  triggerEvent?: (name: string, detail?: unknown) => void;
  /** Lay reply truoc do de "noi lai". */
  getLastReply?: () => string;
  /** Speak helper de TTS doc lai (cho intent repeat / read_page). */
  speak?: (text: string) => void;
  /** Kiem tra trang thai da dang nhap chua. */
  isLoggedIn?: () => boolean;
}

/** Tim element click duoc theo nhan (text/aria-label). */
function findClickable(label: string): HTMLElement | null {
  if (typeof document === "undefined") return null;
  const want = label.toLowerCase().trim();

  const byData = document.querySelector<HTMLElement>(`[data-voice="${CSS.escape(want)}"]`);
  if (byData) return byData;

  const ariaNodes = Array.from(
    document.querySelectorAll<HTMLElement>("button[aria-label], a[aria-label], [role='button'][aria-label]")
  );
  const aria = ariaNodes.find((n) => (n.getAttribute("aria-label") || "").toLowerCase().includes(want));
  if (aria) return aria;

  const candidates = Array.from(
    document.querySelectorAll<HTMLElement>("button, a, [role='button']")
  );
  const byText = candidates.find((n) => (n.innerText || "").toLowerCase().includes(want));
  return byText ?? null;
}

function getEditable(): HTMLInputElement | HTMLTextAreaElement | HTMLElement | null {
  if (typeof document === "undefined") return null;
  // Uu tien element dang focus
  const active = document.activeElement as HTMLElement | null;
  if (active && (active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement || active.isContentEditable)) {
    return active;
  }
  // Fallback: input/textarea co data-voice="input" hoac textarea cuoi cung trong main
  const explicit = document.querySelector<HTMLElement>('[data-voice="input"]');
  if (explicit) return explicit;
  const all = Array.from(document.querySelectorAll<HTMLInputElement | HTMLTextAreaElement>("textarea, input[type='text'], input:not([type])"));
  return all[all.length - 1] ?? null;
}

function setEditableValue(el: HTMLElement, value: string): void {
  if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
    const proto = el instanceof HTMLInputElement ? HTMLInputElement.prototype : HTMLTextAreaElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, "value")?.set;
    setter?.call(el, value);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    el.focus();
  } else if (el.isContentEditable) {
    el.innerText = value;
    el.dispatchEvent(new InputEvent("input", { bubbles: true }));
    el.focus();
  }
}

function focusSearch(): boolean {
  if (typeof document === "undefined") return false;
  const el =
    document.querySelector<HTMLInputElement>('[data-voice="search"]') ||
    document.querySelector<HTMLInputElement>('input[type="search"]') ||
    document.querySelector<HTMLInputElement>('input[name*="search" i], input[placeholder*="tim" i], input[placeholder*="search" i]');
  if (el) {
    el.focus();
    return true;
  }
  return false;
}

function submitNearestForm(): boolean {
  if (typeof document === "undefined") return false;
  const explicit = document.querySelector<HTMLElement>('[data-voice="submit"]');
  if (explicit) {
    explicit.click();
    return true;
  }
  const editable = getEditable();
  if (editable) {
    const form = editable.closest("form");
    if (form) {
      const btn = form.querySelector<HTMLButtonElement>('button[type="submit"], [data-voice="submit"]');
      if (btn) {
        btn.click();
        return true;
      }
      form.requestSubmit?.();
      return true;
    }
    // Khong co form -> Enter event
    editable.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", code: "Enter", bubbles: true }));
    return true;
  }
  return false;
}

function adjustFontSize(dir: FontDir): boolean {
  if (typeof document === "undefined") return false;
  const root = document.documentElement;
  const STEP = 2;
  const MIN = 12;
  const MAX = 22;
  const current = parseFloat(root.style.fontSize || "");
  const base = isFinite(current) && current > 0 ? current : 16;
  let next = base;
  if (dir === "increase") next = Math.min(MAX, base + STEP);
  else if (dir === "decrease") next = Math.max(MIN, base - STEP);
  else next = 16;
  root.style.fontSize = `${next}px`;
  return true;
}

function readableText(): string {
  if (typeof document === "undefined") return "";
  const main = document.querySelector("main") || document.body;
  const text = (main as HTMLElement).innerText || "";
  // Cat ngan de TTS khong qua dai
  const trimmed = text.replace(/\s+/g, " ").trim();
  return trimmed.length > 600 ? trimmed.slice(0, 600) + "..." : trimmed;
}

export function executeIntent(intent: IntentMatch, ctx: ExecuteContext): string {
  switch (intent.kind) {
    case "navigate": {
      if (intent.target) ctx.navigate(intent.target);
      return intent.reply;
    }
    case "scroll": {
      if (typeof window === "undefined") return intent.reply;
      const pathname = window.location.pathname;
      const hasSections = Boolean(PAGE_SECTIONS[pathname]?.length);
      const h = window.innerHeight || 600;
      switch (intent.action) {
        case "top": window.scrollTo({ top: 0, behavior: "smooth" }); break;
        case "bottom": window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" }); break;
        case "up":
          if (hasSections) {
            scrollToPrevSection();
          } else {
            window.scrollBy({ top: -h * 0.8, behavior: "smooth" });
          }
          break;
        case "down":
          if (hasSections) {
            scrollToNextSection();
          } else {
            window.scrollBy({ top: h * 0.8, behavior: "smooth" });
          }
          break;
      }
      return intent.reply;
    }
    case "scroll_section": {
      if (!intent.sectionId) return "Mình chưa rõ bạn muốn cuộn tới phần nào.";
      const ok = scrollToSection(intent.sectionId);
      return ok ? intent.reply : "Không tìm thấy phần này trên trang hiện tại.";
    }
    case "page": {
      if (typeof window === "undefined") return intent.reply;
      switch (intent.action) {
        case "back": window.history.back(); break;
        case "forward": window.history.forward(); break;
        case "reload": window.location.reload(); break;
      }
      return intent.reply;
    }
    case "ui_search": {
      const ok = focusSearch();
      return ok ? intent.reply : "Trang này không có ô tìm kiếm.";
    }
    case "ui_click": {
      if (!intent.label) return "Mình chưa rõ tên nút bạn muốn bấm.";
      const el = findClickable(intent.label);
      if (!el) return `Mình không tìm thấy nút "${intent.label}" trên trang này.`;
      el.click();
      return intent.reply;
    }
    case "ui_submit": {
      const ok = submitNearestForm();
      return ok ? intent.reply : "Mình không tìm thấy nút gửi trên trang này.";
    }
    case "ui_clear": {
      const el = getEditable();
      if (!el) return "Mình không tìm thấy ô nhập để xóa.";
      setEditableValue(el, "");
      return intent.reply;
    }
    case "ui_dictate": {
      const el = getEditable();
      if (!el) return "Mình không tìm thấy ô nhập để viết.";
      setEditableValue(el, intent.text ?? "");
      return intent.reply;
    }
    case "auth_login": {
      // Kiem tra da dang nhap chua
      if (ctx.isLoggedIn?.()) {
        return "Bạn đã đăng nhập rồi ạ. Bạn muốn mình làm gì tiếp?";
      }
      ctx.triggerEvent?.("medisign:login");
      // Fallback: bam nut co aria-label/label "dang nhap"
      const el = findClickable("đăng nhập");
      if (el) el.click();
      return intent.reply;
    }
    case "auth_logout": {
      ctx.triggerEvent?.("medisign:logout");
      const el = findClickable("đăng xuất");
      if (el) el.click();
      return intent.reply;
    }
    case "chat_mode": {
      if (intent.chatMode) {
        ctx.triggerEvent?.("medisign:chat-mode", intent.chatMode);
      }
      return intent.reply;
    }
    case "elderly_toggle": {
      ctx.triggerEvent?.("medisign:elderly-toggle");
      return intent.reply;
    }
    case "font_size": {
      if (intent.fontDir) adjustFontSize(intent.fontDir);
      return intent.reply;
    }
    case "read_page": {
      const text = readableText();
      ctx.speak?.(text || "Trang này không có nội dung để đọc.");
      return intent.reply;
    }
    case "repeat": {
      const last = ctx.getLastReply?.() ?? "";
      if (last) ctx.speak?.(last);
      return last || "Chưa có nội dung để nhắc lại.";
    }
    case "close": {
      ctx.closeOverlay();
      return intent.reply;
    }
    case "stop": {
      ctx.stopListening();
      return intent.reply;
    }
    case "help":
    case "unknown":
    default:
      return intent.reply;
  }
}
