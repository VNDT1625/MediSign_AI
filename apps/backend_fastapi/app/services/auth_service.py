"""Auth service - Business logic for authentication."""
import uuid
from datetime import datetime, timedelta
import hashlib
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database.cloud_models import User, UserSession, PasswordReset
from app.schemas.auth import (
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthTokenPair,
    AuthUserResponse,
    AuthLoginResponse,
    AuthRegisterResponse,
)
from app.services.email_service import send_password_reset_email

# Password reset token expiry
PASSWORD_RESET_EXPIRE_MINUTES = 30

# Token expiry
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days


def _normalize_phone(phone: str) -> str:
    """Normalize VN phone number to 0xxxxxxxxx format.
    Converts +84xxxxxxxxx → 0xxxxxxxxx, strips spaces/dashes.
    """
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+84"):
        phone = "0" + phone[3:]
    return phone


def register(payload: AuthRegisterRequest, db: Session, ip_address: str = None) -> AuthRegisterResponse:
    """Register new user account"""

    # Normalize phone number format (+84 → 0)
    normalized_phone = _normalize_phone(payload.phone)

    # Check if email exists
    existing_email = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "AUTH_EMAIL_EXISTS", "message": "Email da ton tai"},
        )

    # Check if username exists
    existing_username = db.query(User).filter(User.username == payload.username.lower()).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "AUTH_USERNAME_EXISTS", "message": "Ten dang nhap da ton tai"},
        )

    # Check if phone exists (if provided)
    if normalized_phone:
        existing_phone = db.query(User).filter(User.phone == normalized_phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "AUTH_PHONE_EXISTS", "message": "So dien thoai da ton tai"},
            )

    # Create new user
    user = User(
        id=str(uuid.uuid4()),
        email=payload.email.lower(),
        phone=normalized_phone,
        username=payload.username.lower(),
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        is_email_verified=False,
        is_phone_verified=False,
        is_active=True,
        account_type="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    tokens = _create_token_pair(user.id, db, ip_address)

    return AuthRegisterResponse(
        message="Dang ky thanh cong",
        user=_user_to_response(user),
        tokens=tokens,
    )


def login(payload: AuthLoginRequest, db: Session, ip_address: str = None) -> AuthLoginResponse:
    """Login with email or phone"""

    # Find user by email or phone
    user = None
    if payload.email:
        user = db.query(User).filter(User.email == payload.email.lower()).first()
    elif payload.phone:
        normalized_phone = _normalize_phone(payload.phone)
        user = db.query(User).filter(User.phone == normalized_phone).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_INVALID_CREDENTIALS", "message": "Sai email/so dien thoai hoac mat khau"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_ACCOUNT_INACTIVE", "message": "Tai khoan bi khoa"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Generate tokens
    tokens = _create_token_pair(user.id, db, ip_address)

    return AuthLoginResponse(
        user=_user_to_response(user),
        tokens=tokens,
    )


def refresh_tokens(refresh_token: str, db: Session) -> AuthTokenPair:
    """Refresh access token using refresh token"""

    # Decode refresh token
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = payload["sub"]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_INVALID_TOKEN", "message": "Refresh token khong hop le"},
        )

    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_USER_NOT_FOUND", "message": "Tai khoan khong ton tai"},
        )

    # Verify refresh token exists in database
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    session = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.refresh_token_hash == token_hash,
        UserSession.is_revoked == False,
        UserSession.expires_at > datetime.utcnow(),
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_TOKEN_EXPIRED", "message": "Refresh token da het han"},
        )

    # Generate new tokens
    return _create_token_pair(user.id, db, None)


def logout(user_id: str, db: Session) -> dict:
    """Logout - revoke all user sessions or just current one"""

    # Revoke all sessions for this user
    db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_revoked == False,
    ).update({"is_revoked": True})

    db.commit()

    return {"message": "Dang xuat thanh cong"}


def change_password(user_id: str, current_password: str, new_password: str, db: Session) -> dict:
    """Change password"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "AUTH_USER_NOT_FOUND", "message": "Tai khoan khong ton tai"},
        )

    # Verify current password
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "AUTH_WRONG_PASSWORD", "message": "Mat khau hien tai khong dung"},
        )

    # Update password
    user.password_hash = hash_password(new_password)
    db.commit()

    # Revoke all sessions for security
    db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_revoked == False,
    ).update({"is_revoked": True})
    db.commit()

    return {"message": "Doi mat khau thanh cong"}


def _create_token_pair(user_id: str, db: Session, ip_address: str = None) -> AuthTokenPair:
    """Create access and refresh token pair"""

    # Generate tokens
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    # Hash refresh token for storage
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    # Save session to database
    session = UserSession(
        user_id=user_id,
        refresh_token_hash=token_hash,
        ip_address=ip_address,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        is_revoked=False,
    )

    db.add(session)
    db.commit()

    return AuthTokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _user_to_response(user: User) -> AuthUserResponse:
    """Convert User model to response"""
    return AuthUserResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        username=user.username,
        full_name=user.full_name,
        is_email_verified=user.is_email_verified,
        is_phone_verified=user.is_phone_verified,
        account_type=user.account_type,
        created_at=user.created_at,
    )


def request_password_reset(email: str, db: Session) -> dict:
    """Tạo token đặt lại mật khẩu và gửi email.

    Luôn trả về thông báo thành công dù email có tồn tại hay không
    (tránh lộ thông tin tài khoản — security best practice).
    """
    user = db.query(User).filter(User.email == email.lower()).first()

    if user and user.is_active:
        # Vô hiệu hóa tất cả token reset cũ chưa dùng của user này
        db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.is_used == False,
        ).update({"is_used": True})
        db.commit()

        # Tạo token ngẫu nhiên 32 bytes (64 hex chars) — đủ entropy
        raw_token = secrets.token_hex(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        reset_record = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES),
            is_used=False,
        )
        db.add(reset_record)
        db.commit()

        # Gửi email (lỗi gửi mail không block response)
        send_password_reset_email(
            to_email=user.email,
            full_name=user.full_name,
            reset_token=raw_token,
        )

    return {
        "message": "Nếu email tồn tại trong hệ thống, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu."
    }


def confirm_password_reset(token: str, new_password: str, db: Session) -> dict:
    """Xác nhận token và đặt mật khẩu mới."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    reset_record = db.query(PasswordReset).filter(
        PasswordReset.token_hash == token_hash,
        PasswordReset.is_used == False,
        PasswordReset.expires_at > datetime.utcnow(),
    ).first()

    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "AUTH_INVALID_RESET_TOKEN",
                "message": "Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.",
            },
        )

    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "AUTH_INVALID_RESET_TOKEN",
                "message": "Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.",
            },
        )

    # Cập nhật mật khẩu
    user.password_hash = hash_password(new_password)

    # Đánh dấu token đã dùng
    reset_record.is_used = True

    # Thu hồi tất cả session hiện tại (bắt đăng nhập lại)
    db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_revoked == False,
    ).update({"is_revoked": True})

    db.commit()

    return {"message": "Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại."}
