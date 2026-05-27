"""Email service — gửi email qua SMTP (stdlib, không cần thư viện ngoài).

Cấu hình qua biến môi trường (xem .env.example):
  EMAIL_HOST        — SMTP host, vd: smtp.gmail.com
  EMAIL_PORT        — SMTP port, mặc định 587 (STARTTLS)
  EMAIL_USERNAME    — địa chỉ email gửi
  EMAIL_PASSWORD    — mật khẩu / app password
  EMAIL_FROM_NAME   — tên hiển thị, mặc định "MediSign AI"
  EMAIL_USE_TLS     — "true" để dùng STARTTLS (mặc định true)
  FRONTEND_BASE_URL — URL frontend để tạo link reset, vd: http://localhost:3000

Khi EMAIL_HOST không được cấu hình, service chạy ở chế độ "console" —
in link reset ra log thay vì gửi email thật. Hữu ích cho dev local.
"""

import logging
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _get_smtp_config() -> dict:
    return {
        "host": os.getenv("EMAIL_HOST", ""),
        "port": int(os.getenv("EMAIL_PORT", "587")),
        "username": os.getenv("EMAIL_USERNAME", ""),
        "password": os.getenv("EMAIL_PASSWORD", ""),
        "from_name": os.getenv("EMAIL_FROM_NAME", "MediSign AI"),
        "use_tls": os.getenv("EMAIL_USE_TLS", "true").lower() == "true",
    }


def _get_frontend_base_url() -> str:
    return os.getenv("FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")


# ---------------------------------------------------------------------------
# Core send function
# ---------------------------------------------------------------------------

def _send_email(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """Gửi email. Trả về True nếu thành công, False nếu thất bại."""
    cfg = _get_smtp_config()

    if not cfg["host"]:
        # Chế độ console — dev local không cần cấu hình SMTP
        logger.info(
            "[EMAIL CONSOLE MODE] To: %s | Subject: %s\n%s",
            to_email, subject, text_body,
        )
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{cfg['from_name']} <{cfg['username']}>"
    msg["To"] = to_email

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as server:
            if cfg["use_tls"]:
                server.starttls()
            if cfg["username"] and cfg["password"]:
                server.login(cfg["username"], cfg["password"])
            server.sendmail(cfg["username"], [to_email], msg.as_string())
        logger.info("Email sent to %s: %s", to_email, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
        return False


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------

def send_password_reset_email(to_email: str, full_name: str, reset_token: str) -> bool:
    """Gửi email chứa link đặt lại mật khẩu."""
    frontend_url = _get_frontend_base_url()
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    subject = "Đặt lại mật khẩu MediSign AI"

    text_body = f"""Xin chào {full_name},

Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản MediSign AI của bạn.

Nhấp vào liên kết sau để đặt lại mật khẩu (có hiệu lực trong 30 phút):
{reset_link}

Nếu bạn không yêu cầu đặt lại mật khẩu, hãy bỏ qua email này.
Tài khoản của bạn vẫn an toàn.

Trân trọng,
Đội ngũ MediSign AI
"""

    html_body = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Đặt lại mật khẩu</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width:480px;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#2563eb,#1d4ed8);padding:32px 40px;text-align:center;">
              <p style="margin:0;font-size:13px;font-weight:700;letter-spacing:0.12em;color:#bfdbfe;text-transform:uppercase;">MediSign AI</p>
              <h1 style="margin:8px 0 0;font-size:22px;font-weight:800;color:#ffffff;">Đặt lại mật khẩu</h1>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;">
              <p style="margin:0 0 16px;font-size:15px;color:#334155;">Xin chào <strong>{full_name}</strong>,</p>
              <p style="margin:0 0 24px;font-size:14px;color:#64748b;line-height:1.6;">
                Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.
                Nhấp vào nút bên dưới để tiếp tục — liên kết có hiệu lực trong <strong>30 phút</strong>.
              </p>
              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding:8px 0 28px;">
                    <a href="{reset_link}"
                       style="display:inline-block;background:#2563eb;color:#ffffff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:12px;">
                      Đặt lại mật khẩu
                    </a>
                  </td>
                </tr>
              </table>
              <!-- Fallback link -->
              <p style="margin:0 0 8px;font-size:12px;color:#94a3b8;">Nếu nút không hoạt động, sao chép liên kết sau vào trình duyệt:</p>
              <p style="margin:0 0 24px;font-size:11px;color:#2563eb;word-break:break-all;">{reset_link}</p>
              <!-- Warning -->
              <div style="background:#fef9c3;border:1px solid #fde047;border-radius:10px;padding:14px 16px;">
                <p style="margin:0;font-size:13px;color:#854d0e;">
                  ⚠️ Nếu bạn không yêu cầu đặt lại mật khẩu, hãy bỏ qua email này.
                  Tài khoản của bạn vẫn an toàn.
                </p>
              </div>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#f8fafc;padding:20px 40px;text-align:center;border-top:1px solid #e2e8f0;">
              <p style="margin:0;font-size:12px;color:#94a3b8;">© 2025 MediSign AI · Chăm sóc sức khỏe thông minh</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return _send_email(to_email, subject, html_body, text_body)
