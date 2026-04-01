"""CLI commands for database management."""
import uuid

from app.database.base import SessionLocal, engine, Base
from app.database import cloud_models, local_models
from app.database.cloud_models import User
from app.core.security import hash_password


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def create_admin_user(
    email: str = "admin@medisign.ai",
    username: str = "admin",
    full_name: str = "Administrator",
    password: str = "Admin123!@#",
):
    """Create an admin user."""
    db = SessionLocal()
    try:
        # Check if admin exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"Admin user already exists: {email}")
            return

        # Create admin user
        admin = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            account_type="admin",
            is_active=True,
            is_email_verified=True,
        )
        db.add(admin)
        db.commit()
        print(f"Admin user created: {email}")
        print(f"Password: {password}")
    finally:
        db.close()


def create_demo_user(
    email: str = "demo@medisign.ai",
    username: str = "demo",
    full_name: str = "Demo User",
    password: str = "Demo123!@#",
):
    """Create a demo user."""
    db = SessionLocal()
    try:
        # Check if exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"Demo user already exists: {email}")
            return

        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            account_type="user",
            is_active=True,
            is_email_verified=True,
        )
        db.add(user)
        db.commit()
        print(f"Demo user created: {email}")
        print(f"Password: {password}")
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m app.cli [create-tables|create-admin|create-demo]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create-tables":
        create_tables()
    elif command == "create-admin":
        create_admin_user()
    elif command == "create-demo":
        create_demo_user()
    else:
        print(f"Unknown command: {command}")
        print("Available: create-tables, create-admin, create-demo")

