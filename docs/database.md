# database.md

Muc dich: Mo ta schema, migration, va quy tac thay doi du lieu.

## Cau hinh

- **Database:** PostgreSQL
- **Host:** localhost:5432
- **Database name:** medisign
- **User:** postgres / password: postgres

---

## 1. Cloud Database (PostgreSQL)

### 1.1 Bang nguoi dung

| Column | Type | Constraint | Mo ta |
|--------|------|------------|-------|
| id | VARCHAR(36) | PRIMARY KEY | UUID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Ten dang nhap |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email |
| phone | VARCHAR(20) | INDEX | So dien thoai |
| password_hash | VARCHAR(255) | NOT NULL | Mat khau da hash |
| full_name | VARCHAR(255) | NOT NULL | Ho ten |
| is_email_verified | BOOLEAN | DEFAULT false | Xac thuc email |
| is_phone_verified | BOOLEAN | DEFAULT false | Xac thuc phone |
| is_active | BOOLEAN | DEFAULT true | Tai khoan hoat dong |
| account_type | VARCHAR(20) | DEFAULT 'user' | Loai: user, doctor, admin |
| last_login | TIMESTAMP | NULL | Lan dang nhap cuoi |
| created_at | TIMESTAMP | NOT NULL | Ngay tao |
| updated_at | TIMESTAMP | NOT NULL | Ngay cap nhat |

### 1.2 Bang session

| Table | Description |
|-------|-------------|
| user_sessions | Token dang nhap, refresh token |
| password_resets | Token dat lai mat khau |
| email_verifications | Token xac thuc email |

### 1.3 Bang du lieu cong khai

| Table | Description |
|-------|-------------|
| medicine_registry | Danh muc thuoc (tu Cục Dược VN) |
| hospitals | Danh sach benh vien, phong kham |

### 1.4 Bang user data

| Table | Description |
|-------|-------------|
| family_connections | Ket noi nguoi than (Care Connect) |
| triage_history | Lich su phan loai benh (anonymized) |

### 1.5 Bang community

| Table | Description |
|-------|-------------|
| community_posts | Bai viet chia se (an danh, kiem duyet truoc) |
| post_comments | Binh luan |
| post_likes | Thich bai viet |
| post_reports | Bao cao vi pham |
| post_bookmarks | Luu bai viet |
| community_profiles | Nickname, avatar emoji, unique ID (#LQ2024) |
| friend_requests | Loi moi ket ban (an danh) |
| friendships | Quan he ban be |
| chat_messages | Tin nhan 1-1 (an danh, moderated) |
| moderation_logs | Lich su kiem duyet (AI auto + manual) |
| daily_affirmations | Cau noi lac quan hang ngay |

### 1.6 Bang fitness

| Table | Description |
|-------|-------------|
| workout_sessions | Lich su tap luyen |
| fitness_goals | Muc tieu the duc |

---

## 2. Local Database (SQLite - Mobile)

| Table | Description |
|-------|-------------|
| daily_journals | Nhat ky hang ngay (Soul Garden) |
| user_profiles | Ho so suc khoe ca nhan |
| my_medicines | Tu thuoc ca nhan |

---

## 3. Quy tac DB

- Moi thay doi schema phai co migration.
- Moi thay doi schema phai cap nhat tai lieu nay.
- Khong sua truc tiep DB production.
- Su dung SQLAlchemy ORM cho tat ca thao tac.

---

## 4. Admin API

Cac endpoint quan ly:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/admin/stats | Thong ke tong quan |
| GET/POST/PATCH/DELETE | /api/v1/admin/users | Quan ly user |
| GET/POST/PATCH/DELETE | /api/v1/admin/medicines | Quan ly thuoc |
| GET/POST/PATCH/DELETE | /api/v1/admin/hospitals | Quan ly benh vien |
| GET/PATCH/DELETE | /api/v1/admin/posts | Quan ly bai viet |
| GET | /api/v1/admin/stats/posts | Thong ke community |
| GET | /api/v1/admin/workouts | Xem lich su tap luyen |
| GET | /api/v1/admin/goals | Xem muc tieu the duc |
| GET | /api/v1/admin/stats/workouts | Thong ke fitness |

