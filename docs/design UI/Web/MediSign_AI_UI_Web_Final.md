# MediSign AI — UI Web Design Document
## Phiên bản: Final | Ngày: 15/05/2026
## Phạm vi: UI Web (Đồng bộ bố cục mẫu)

---

## MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Navigation](#2-navigation)
3. [Trang Home — Landing Page](#3-trang-home--landing-page)
4. [Login / Register](#4-login--register)
5. [Trang Chat AI — 3 Cột](#5-trang-chat-ai--3-cột)
6. [4 Mode Giao Tiếp](#6-4-mode-giao-tiếp)
7. [Trang Tủ Thuốc](#7-trang-tủ-thuốc)
8. [Trang Soul Garden](#8-trang-soul-garden)
9. [Trang Pricing](#9-trang-pricing)
10. [Trang About](#10-trang-about)
11. [Trang Download](#11-trang-download)
12. [Color Design](#12-color-design)
13. [Typography](#13-typography)
14. [Design System](#14-design-system)
15. [Animation](#15-animation)
16. [Responsive](#16-responsive)
17. [Accessibility](#17-accessibility)
18. [Kỹ thuật triển khai](#18-kỹ-thuật-triển-khai)
19. [Chưa quyết định](#19-chưa-quyết-định)

---

## 1. TỔNG QUAN DỰ ÁN

MediSign AI là ứng dụng trợ lý y tế AI tại nhà cho người Việt Nam. Website là nơi:
- Người dùng chat với AI
- Tải app về cho laptop
- Xem pricing và thông tin khác

**Nguyên tắc thiết kế:**
- Hiện đại, ấn tượng ngay từ đầu
- Phù hợp người cao tuổi (font lớn, contrast cao, dễ dùng)
- Đa dạng người dùng: người bình thường, người mù, người điếc, người điếc mù chữ

---

## 2. NAVIGATION

| STT | Trang | Mục đích |
|-----|-------|----------|
| 1 | Home | Landing page giới thiệu |
| 2 | Chat AI | Giao diện chat với AI |
| 3 | Pricing | Bảng giá, marketing |
| 4 | About | Giới thiệu team dev + bác sĩ |
| 5 | Download | Tải app mobile & desktop |

**Đặc biệt:** Desktop sử dụng Header của mobile và content của web để đảm bảo tính đồng bộ.

---

## 3. TRANG HOME — LANDING PAGE

### 3.1. Hero Section

| Yếu tố | Chi tiết |
|--------|----------|
| Visual | Bác sĩ 3D ngồi bàn, màn hình Glassmorphism hiển thị X-quang |
| Input chat | Thanh search trung tâm: "Hỏi gì cũng có, MediSign AI lo nhé..." |
| Quick links | 4 icon: An toàn, Dễ dàng, Hỗ trợ 24/7, Cá nhân hóa |

### 3.2. Các Section chính

| Section | Nội dung | Visual |
|---------|----------|--------|
| 1. Tại sao chọn | Đội ngũ bác sĩ, Hiểu bạn, Dễ sử dụng, Bảo mật | 4 Card 3D minh họa |
| 2. Cách hoạt động | Nhập triệu chứng -> AI phân tích -> Tư vấn | Quy trình 3 bước với icon |
| 3. Đa thiết bị | Demo Laptop + Mobile, nút tải App Store/Google Play | Mockup thiết bị thực tế |
| 4. Feature mới | Soul Garden & Tủ thuốc (Badge "Chỉ trên app") | Card giới thiệu tính năng |
| 5. Feedback | Đánh giá 5 sao từ người dùng thật | Avatar + Nội dung review |
| 6. Footer | Sitemap, Social media, Contact info | Standard footer |

---

## 4. LOGIN / REGISTER

| Yếu tố | Chi tiết |
|--------|----------|
| Trigger | Click "Tạo tài khoản" trên nav hoặc nút bắt đầu |
| Form | Phiếu đăng ký to, rõ, như ở bệnh viện |
| Input method | VOICE + TEXT — người dùng tự chọn |
| Voice flow | AI hỏi từng bước: "Bạn tên gì?", "Đã có tài khoản chưa?"... |

---

## 5. TRANG CHAT AI — 3 CỘT

### 5.1. Layout chi tiết

| Phần | Vị trí | Chức năng |
|------|--------|-----------|
| Sidebar Trái | Trái | Lịch sử chat, **Chuyển mode (Text/Voice/Click/Ký hiệu)**, Elderly Mode |
| Chat chính | Giữa | Luồng hội thoại, AI Analysis Cards (Đánh giá sơ bộ & Gợi ý) |
| Tóm tắt nhanh | Phải | Triệu chứng, Khuyến nghị, Tệp đính kèm |

### 5.2. AI Cards trong luồng chat

| Thẻ | Nội dung | Style |
|-----|----------|-------|
| Đánh giá sơ bộ | Nhiệt độ, Triệu chứng, X-quang phổi | Table 2 cột, icon xanh/đỏ |
| Gợi ý xử trí | Nghỉ ngơi, Uống nước, Paracetamol | List icon + text |

---

## 6. 4 MODE GIAO TIẾP

Nằm tại Sidebar trái, cho phép chuyển đổi nhanh chóng:
- **Text:** Giao diện bubble truyền thống.
- **Voice:** Hiệu ứng waveform khi đang nghe.
- **Click:** Chọn vùng trên model 3D ( Three.js).
- **Ký hiệu:** Bác sĩ 3D diễn đạt bằng ngôn ngữ ký hiệu.

---

## 7. TRANG TỦ THUỐC

| Section | Chi tiết |
|---------|----------|
| Banner | "3 loại thuốc cần uống", "Next dose: 10:00" |
| Main | Thẻ thuốc chi tiết, nút "Đánh dấu đã uống" |
| Sidebar | Lịch uống theo giờ, Tóm tắt tồn kho, Nút "Mua thêm" |

---

## 8. TRANG SOUL GARDEN

| Section | Chi tiết |
|---------|----------|
| Banner | "Hôm nay bạn chọn chăm sóc tâm hồn nhé" |
| Vườn cảm xúc | Hình ảnh 3D khu vườn với các cây cảm xúc |
| Hoạt động | Viết nhật ký, Bài tập thở, Thiền, Âm nhạc |

---

## 9. TRANG PRICING

| Gói | Giá | Tính năng nổi bật |
|-----|-----|-------------------|
| Miễn phí | 0đ | Chat AI cơ bản, lịch sử 7 ngày |
| Phổ Pro | 199k/tháng | Tư vấn 24/7, hồ sơ nâng cao, lịch sử vô hạn |
| Gia đình | 399k/tháng | Tối đa 6 thành viên, theo dõi cả nhà |

---

## 10. TRANG ABOUT
- Hero: "Đội ngũ MediSign"
- Team dev: Grid ảnh + vai trò
- Medical advisors: Thông tin chuyên gia y tế

---

## 11. TRANG DOWNLOAD
- Mobile: QR code + Store buttons
- Desktop: Windows/Mac/Linux download links

---

## 12. COLOR DESIGN (GIỮ NGUYÊN)

### 12.1. Màu chính

| Vai trò | Màu | HEX | Tỷ lệ |
|---------|-----|-----|-------|
| Nền chính | Trắng | `#FFFFFF` | 60% |
| Chủ đạo | Xanh biển | `#0284C7` | 30% |
| Accent chính | Cam | `#F97316` | 6% |
| Accent phụ | Xanh lá | `#22C55E` | 4% |

### 12.2. Màu phụ

| Vai trò | Màu | HEX |
|---------|-----|-----|
| Text chính | Xám đậm | `#1E293B` |
| Text phụ | Xám trung | `#64748B` |
| Text nhạt | Xám nhạt | `#94A3B8` |
| Nền phụ | Xanh biển nhạt | `#F0F9FF` |
| Viền | Xám viền | `#E2E8F0` |

### 12.3. Quy tắc sử dụng màu
1. **60-30-10**: Trắng 60% — Xanh biển 30% — Cam + Xanh lá 10%
2. **Contrast**: AAA 7:1 cho text nhỏ, AA 4.5:1 cho text thường
3. **Người mù màu**: Tránh cặp xanh lá + đỏ. Test bằng Stark.

---

## 13. TYPOGRAPHY (GIỮ NGUYÊN)

### 13.1. Font
- Font chính: **Inter**
- Fallback: sans-serif

### 13.2. Scale
- Hero title: 48-64px | Bold 700
- Body: 18-20px | Regular 400
- Elderly Mode: Tăng lên 22-24px, Line height 1.8

---

## 14. DESIGN SYSTEM (GIỮ NGUYÊN)

### 14.1. Icon
- Bộ: Phosphor Icons / Heroicons. Stroke 2px. Size 24px.

### 14.2. Border Radius
- Card: 12px | Button pill: 999px | Button default: 8px

### 14.3. Spacing (4px Grid)
- sm: 8px | md: 16px | lg: 24px | xl: 32px

---

## 15. ANIMATION (GIỮ NGUYÊN)

- Duration: 200-300ms
- Easing: `cubic-bezier(0.4, 0, 0.2, 1)`
- Button hover: translateY(-2px)

---

## 16. RESPONSIVE (GIỮ NGUYÊN)

- Mobile: < 640px
- Tablet: 640-1024px
- Desktop: > 1024px

---

## 17. ACCESSIBILITY (GIỮ NGUYÊN)

- Focus visible: Viền cam `#F97316` 2px
- Touch target: Tối thiểu 44x44px
- Elderly Mode: Font ≥20px, nút ≥56px

---

## 18. KỸ THUẬT TRIỂN KHAI (GIỮ NGUYÊN)

- Scroll trigger: GSAP ScrollTrigger
- Voice: Web Speech API + annyang.js
- 3D: Three.js / React Three Fiber

---

## 19. CHƯA QUYẾT ĐỊNH (GIỮ NGUYÊN)
1. Dark mode: Có hay không?
2. Lottie/Framer cho micro-animation.
3. Team dev cụ thể.

---
*Tài liệu được cập nhật bố cục theo UI mẫu ngày 16/05/2026. Các quy tắc thẩm mỹ được bảo lưu.*
