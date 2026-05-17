/**
 * Card profile chính: avatar trái, info giữa, illustration thực vật bên phải.
 * Illustration đang là placeholder SVG đơn giản — sẽ thay bằng ảnh thật khi có.
 */
export function ProfileCard() {
  return (
    <section
      aria-label="Thẻ hồ sơ người dùng"
      className="relative overflow-hidden rounded-card border border-ink-200 bg-white p-6 shadow-soft sm:p-7"
    >
      {/* Illustration mảng bên phải — placeholder soft botanical */}
      <BotanicalDecor />

      <div className="relative grid items-center gap-5 sm:grid-cols-[120px_1fr]">
        {/* Avatar */}
        <div className="relative w-fit">
          <div className="grid h-[120px] w-[120px] place-items-center overflow-hidden rounded-pill border-4 border-white bg-gradient-to-br from-brand-50 to-accent/15 text-3xl font-bold text-brand-700 shadow-card">
            NA
          </div>
          <button
            type="button"
            aria-label="Đổi ảnh đại diện"
            className="absolute -bottom-1 -right-1 grid h-9 w-9 place-items-center rounded-pill bg-white text-ink-700 shadow-card hover:text-brand cursor-pointer"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path
                d="M3 17l11-11 4 4-11 11H3v-4z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        {/* Info */}
        <div>
          <h2 className="text-[28px] font-bold leading-tight text-ink-900 sm:text-3xl">
            Nguyễn An
          </h2>
          <p className="mt-2 flex items-center gap-2 text-sm text-ink-600">
            <span className="grid h-5 w-5 place-items-center rounded-full bg-success/15 text-success">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M12 21c-3-3-7-6-7-11a4 4 0 0 1 7-2 4 4 0 0 1 7 2c0 5-4 8-7 11z"
                  stroke="currentColor"
                  strokeWidth="2.4"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            Đang trên hành trình chăm sóc tâm hồn
          </p>
          <span className="mt-3 inline-flex items-center gap-1.5 rounded-pill bg-success/12 px-3 py-1 text-xs font-medium text-success">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            Thành viên Soul Garden
          </span>
        </div>
      </div>

      {/* Edit button — góc phải-trên */}
      <button
        type="button"
        className="absolute top-5 right-5 inline-flex items-center gap-1.5 rounded-pill border border-ink-200 bg-white px-3.5 py-1.5 text-sm font-medium text-ink-800 hover:border-brand hover:text-brand cursor-pointer"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M3 17l11-11 4 4-11 11H3v-4z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
        </svg>
        Chỉnh sửa hồ sơ
      </button>
    </section>
  );
}

function BotanicalDecor() {
  return (
    <span aria-hidden="true" className="pointer-events-none absolute inset-y-0 right-0 hidden w-[42%] sm:block">
      {/* Soft gradient nền */}
      <span className="absolute inset-0 bg-gradient-to-l from-success/12 via-success/6 to-transparent" />

      {/* Cây + chậu — SVG đơn giản, sẽ thay bằng ảnh thật */}
      <svg
        viewBox="0 0 320 200"
        className="absolute inset-0 h-full w-full"
        preserveAspectRatio="xMidYMid slice"
      >
        {/* Lá lớn trái-trên */}
        <path
          d="M40 60c20-30 60-30 90-10-15 25-50 30-90 10z"
          fill="#86EFAC"
          opacity="0.7"
        />
        <path
          d="M70 80c10-20 35-22 55-15-10 18-30 24-55 15z"
          fill="#22C55E"
          opacity="0.55"
        />
        {/* Cây giữa */}
        <ellipse cx="200" cy="100" rx="38" ry="48" fill="#22C55E" opacity="0.55" />
        <ellipse cx="220" cy="90" rx="22" ry="32" fill="#86EFAC" opacity="0.7" />
        {/* Chậu */}
        <path
          d="M170 145h60l-6 36c0 4-4 6-8 6h-32c-4 0-8-2-8-6l-6-36z"
          fill="#FED7AA"
        />
        <rect x="166" y="138" width="68" height="10" rx="3" fill="#FDBA74" />
        {/* Đá nhỏ phía trước */}
        <ellipse cx="120" cy="180" rx="14" ry="6" fill="#E2E8F0" />
        <ellipse cx="100" cy="184" rx="10" ry="4" fill="#CBD5E1" />
        <ellipse cx="260" cy="178" rx="16" ry="6" fill="#E2E8F0" />
        {/* Lá nhỏ rơi */}
        <circle cx="50" cy="40" r="3" fill="#22C55E" opacity="0.5" />
        <circle cx="290" cy="50" r="4" fill="#86EFAC" opacity="0.6" />
      </svg>
    </span>
  );
}
