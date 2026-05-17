// Trang Chat AI — bố cục 3 cột theo mục 5 spec MediSign_AI_UI_Web_Final.md.
// Sidebar trái: lịch sử + 4 mode | Giữa: hội thoại + AI Card | Phải: tóm tắt nhanh.
//
// Khóa toàn shell vào h-screen + overflow-hidden để không bao giờ scroll trang ngoài;
// mọi vùng cuộn (history, stream, summary) đều cuộn nội bộ trong cột của chúng.

import { ChatHeader } from "@/components/chat/ChatHeader";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { ChatMain } from "@/components/chat/ChatMain";
import { ChatSummary } from "@/components/chat/ChatSummary";

export const metadata = {
  title: "Chat AI — MediSign AI",
  description:
    "Trò chuyện với MediSign AI để được tư vấn nhanh về sức khỏe của bạn."
};

export default function ChatPage() {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#F1F5F9]">
      <ChatHeader />

      <main
        id="main"
        className="mx-auto flex w-full min-h-0 max-w-[1440px] flex-1 px-4 pb-4 pt-3 lg:px-6"
      >
        <div
          className="
            grid h-full w-full gap-4
            grid-cols-1
            md:grid-cols-[300px_1fr]
            xl:grid-cols-[300px_1fr_320px]
          "
        >
          {/* Cột trái */}
          <div className="hidden h-full min-h-0 overflow-hidden rounded-card border border-ink-200 bg-white shadow-soft md:block">
            <ChatSidebar />
          </div>

          {/* Cột giữa */}
          <div className="h-full min-h-0 overflow-hidden rounded-card border border-ink-200 bg-white shadow-soft">
            <ChatMain />
          </div>

          {/* Cột phải */}
          <div className="hidden h-full min-h-0 overflow-hidden rounded-card border border-ink-200 bg-white shadow-soft xl:block">
            <ChatSummary />
          </div>
        </div>
      </main>
    </div>
  );
}
