"""
Script tạo user test cho MediSign AI
"""
import uuid
import hashlib
import secrets
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Cấu hình database
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'medisign',
    'user': 'postgres',
    'password': 'postgres'
}

def hash_password(password: str) -> str:
    """Hash password theo cách của project (secrets.token_hex(16) = 32 ký tự hex)"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        bytes.fromhex(salt),
        120000  # iterations từ config
    ).hex()
    return f"pbkdf2_sha256$120000${salt}${password_hash}"

def create_user(username: str, email: str, password: str, full_name: str, account_type: str = 'user'):
    """Tạo user mới trong database"""
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    now = datetime.now()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            INSERT INTO users (
                id, username, email, password_hash, full_name,
                is_email_verified, is_phone_verified, is_active,
                account_type, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
            )
            ON CONFLICT (username) DO NOTHING
            RETURNING id, username, email, account_type
        """, (
            user_id, username, email, password_hash, full_name,
            True, False, True,
            account_type, now, now
        ))

        result = cur.fetchone()
        conn.commit()

        if result:
            print(f"✓ Tạo user thành công!")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            print(f"  Account type: {account_type}")
            print(f"  Password: {password}")
        else:
            print(f"⚠ User '{username}' đã tồn tại!")

    except Exception as e:
        print(f"✗ Lỗi: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Xóa user cũ và tạo mới
    import psycopg2
    conn = psycopg2.connect(host='localhost', port=5432, database='medisign', user='postgres', password='postgres')
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = 'testuser'")
    conn.commit()
    cur.close()
    conn.close()
    print("Đã xóa user cũ")

    # Tạo user test mới
    create_user(
        username="testuser",
        email="testuser@example.com",
        password="Test@123",
        full_name="Test User",
        account_type="user"
    )
