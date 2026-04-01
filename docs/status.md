# status.md

Muc dich: Moi AI cap nhat phan viec vua lam xong de team nam tien do.

## Quy uoc cap nhat

- Moi lan cap nhat theo mau:
  - Ngay gio:
  - AI phu trach:
  - Viec da lam:
  - File da sua:
  - Trang thai: done/blocking
  - Ghi chu tiep theo:

## Log

- Ngay gio: 2026-02-14 18:00 UTC+07
- AI phu trach: Windsurf
- Viec da lam:
  - Hoan thien scaffold Flutter (da generate day du platform files).
  - Chuan hoa backend FastAPI scaffold + test routes health/triage.
  - Thiet lap va xac nhan lint/test/format cho mobile + backend.
  - Bo sung shared contracts that (OpenAPI + JSON Schema).
  - Bo sung local dev toolkit (.env.example, bootstrap scripts, docker-compose, git strategy script).
- File da sua:
  - `apps/mobile_flutter/*`
  - `apps/backend_fastapi/*`
  - `packages/shared_contracts/*`
  - `.github/workflows/quality-gate.yml`
  - `scripts/qa/run-quality-gate.ps1`
  - `scripts/dev/bootstrap.ps1`, `scripts/dev/bootstrap.sh`
  - `scripts/git/init-branch-strategy.ps1`
  - `.env.example`, `.gitignore`, `docker-compose.yml`
  - `docs/project.md`
- Trang thai: done
- Ghi chu tiep theo:
  - Chay `scripts/dev/bootstrap.ps1` tren may moi truoc khi vibecode.
  - Dung quality gate truoc moi PR.

- Ngay gio: 2026-02-14 18:24 UTC+07
- AI phu trach: Windsurf
- Viec da lam:
  - Mo rong governance cho `.vibecode/workflows` va `.vibecode/skills`.
  - Tao cau truc `.vibecode` va script dong bo tu nguon chuan.
  - Dong bo 1 lan workflows tu `.windsurf/workflows` va skills tu `.github/skills`.
- File da sua:
  - `docs/quy tắc.md`
  - `.vibecode/workflows/*`
  - `.vibecode/skills/*`
  - `scripts/dev/sync-vibecode.ps1`
- Trang thai: done
- Ghi chu tiep theo:
  - Khi them/sua workflow trong `.windsurf/workflows`, chay `scripts/dev/sync-vibecode.ps1` de dong bo.

- Ngay gio: 2026-02-14 18:25 UTC+07
- AI phu trach: Windsurf
- Viec da lam:
  - Them workflow `flutter-ui-accessibility-first.md` cho UI huong nguoi cham cong nghe va nguoi khuyet tat.
  - Bo sung yeu cau sketch/wireframe truoc khi code vao `flutter-component.md`.
  - Cap nhat ma tran task de Antigravity bat buoc theo workflow UI accessibility-first.
  - Da sync workflow moi sang `.vibecode/workflows`.
- File da sua:
  - `.windsurf/workflows/flutter-ui-accessibility-first.md`
  - `.windsurf/workflows/flutter-component.md`
  - `tasks/README.md`
  - `.vibecode/workflows/*`
- Trang thai: done
- Ghi chu tiep theo:
  - Uu tien dung sketch lo-fi de review nhanh truoc khi vao code UI.

- Ngay gio: 2026-02-14 18:28 UTC+07
- AI phu trach: Windsurf
- Viec da lam:
  - Cap nhat workflow UI accessibility-first voi buoc bat buoc: Pencil AI mockup -> review -> moi code.
  - Them rubric cham UI (thang diem 10) de Antigravity tu danh gia truoc khi code/merge.
  - Cap nhat task Antigravity bat buoc co mockup da duyet va rubric >= 7/10.
  - Da sync workflows sang `.vibecode/workflows`.
- File da sua:
  - `.windsurf/workflows/flutter-ui-accessibility-first.md`
  - `tasks/antigravity/ui-testing.md`
  - `.vibecode/workflows/*`
- Trang thai: done
- Ghi chu tiep theo:
  - Neu diem rubric <= 6/10, lam lai mockup Pencil AI truoc khi vao code.
- Ngay gio: 2026-02-14 18:30 UTC+07
- AI phu trach: ChatGPT Codex
- Viec da lam:
  - Nang cap backend foundation: consult/medicine/auth endpoints + JWT + error envelope co request_id.
  - Dung lai mobile foundation theo huong mobile-first: onboarding mode selector, bottom nav, emergency action, mock API pages.
  - Dong bo OpenAPI + JSON schemas voi implementation.
  - Cap nhat quality gate (local + CI) co contract validation.
  - Cap nhat docs setup/branching/API contract va README root.
- File da sua:
  - `apps/backend_fastapi/*`
  - `apps/mobile_flutter/lib/*`
  - `apps/mobile_flutter/test/widget_test.dart`
  - `packages/shared_contracts/openapi/medisign-api.openapi.yaml`
  - `packages/shared_contracts/json_schema/*.json`
  - `.github/workflows/quality-gate.yml`
  - `scripts/qa/run-quality-gate.ps1`
  - `.env.example`
  - `README.md`
  - `docs/engineering/api-contract.md`
  - `docs/engineering/dev-setup.md`
  - `docs/engineering/branching.md`
- Trang thai: done
- Ghi chu tiep theo:
  - Chay quality gate sau khi cai dep backend (`pip install -e .[dev]`) va Flutter SDK da san sang.
  - Co the tiep tuc sprint sau: MFA flow day du + DB migrations.

- Ngay gio: 2026-02-14 18:56 UTC+07
- AI phu trach: ChatGPT Codex
- Viec da lam:
  - Refactor triage theo huong an toan edge-case: normalize tieng Viet co dau/khong dau, xu ly phu dinh co ban, giu nguyen contract API.
  - Refactor medicine scan: normalize input, nhan dien keyword ruou/bia, va fix logic khong bi ha muc risk khi co nhieu canh bao cung luc.
  - Bo sung regression tests cho consult/medicine (accented keywords, negation, emergency priority, high-risk ranking).
  - Xac nhan chat luong backend: `pytest`, `ruff check`, `black --check` pass; flaky guard 5 lan cho test consult+medicine deu on dinh.
- File da sua:
  - `apps/backend_fastapi/app/services/text_processing.py`
  - `apps/backend_fastapi/app/services/triage_service.py`
  - `apps/backend_fastapi/app/services/medicine_service.py`
  - `apps/backend_fastapi/tests/test_consult.py`
  - `apps/backend_fastapi/tests/test_medicine.py`
  - `docs/status.md`
- Trang thai: done
- Ghi chu tiep theo:
  - Co the tiep tuc bo sung triage keyword dictionary theo clinical review de tang do bao phu.

- Ngay gio: 2026-02-14 19:00 UTC+07
- AI phu trach: Kiro
- Viec da lam:
  - Tao JWT authentication dependency (`get_current_user`) de protect endpoints.
  - Them protected endpoint demo: `GET /api/v1/consult/triage/history` (can access token).
  - Viet test cho protected endpoints: without token (403), invalid token (401), valid token (200).
  - Chuan bi infrastructure cho Antigravity code UI khong bi block boi backend auth.
- File da sua:
  - `apps/backend_fastapi/app/core/dependencies.py` (new)
  - `apps/backend_fastapi/app/api/routes/consult.py`
  - `apps/backend_fastapi/tests/test_protected_endpoints.py` (new)
  - `docs/status.md`
- Trang thai: done
- Ghi chu tiep theo:
  - Antigravity co the dung protected endpoints khi can (da co middleware san sang).
  - ChatGPT Codex dang fix bug triage edge cases (khong trung nhiem vu).
  - Sau khi ChatGPT fix xong, Kiro se verify integration va chay regression.

- Ngay gio: 2026-02-26 02:45 UTC+07
- AI phu trach: Claude Opus
- Viec da lam:
  - Tao database models: local_models.py (DailyJournal, UserProfile, MyMedicine) va cloud_models.py (MedicineRegistry, Hospital, FamilyConnection, TriageHistory).
  - Tao real_api.dart cho mobile: RealConsultApi, RealMedicineApi, RealAuthApi voi Dio HTTP client.
  - Tao api_factory.dart: Factory de switch giua mock va real API (debug=mock, release=real).
  - Viet unit tests test_database.py voi 15+ test cases cho tat ca models.
  - Tao ai_triage_service.py: AI integration scaffold cho Gemini/Qwen voi fallback to rule-based.
- File da sua:
  - `apps/backend_fastapi/app/database/local_models.py` (new)
  - `apps/backend_fastapi/app/database/cloud_models.py` (new)
  - `apps/backend_fastapi/app/database/base.py` (new)
  - `apps/backend_fastapi/app/database/__init__.py` (updated)
  - `apps/backend_fastapi/app/core/config.py` (updated - them sqlite_url, database_url)
  - `apps/backend_fastapi/app/services/ai_triage_service.py` (new)
  - `apps/backend_fastapi/tests/test_database.py` (new)
  - `apps/mobile_flutter/lib/core/network/real_api.dart` (new)
  - `apps/mobile_flutter/lib/core/network/api_factory.dart` (new)
  - `apps/mobile_flutter/lib/app.dart` (updated - su dung ApiFactory)
- Trang thai: done
- Ghi chu tiep theo:
  - Hoan thien AI integration: cai dat google-generativeai hoac qwen SDK.
  - Chay pytest de xac nhan tests pass.

- Ngay gio: 2026-02-26 15:25 UTC+07
- AI phu trach: Windsurf (Cascade)
- Viec da lam:
  - Thiet ke lai giao dien 3 trang fitness (GoalPage, ExerciseSelectionPage, WorkoutPage) theo design system chung cua app: Outfit font, green #059669 theme, gradient background, Semantics accessibility, card style dong nhat voi Dashboard.
  - Fix loi FitnessGoal enum khai bao trung 2 noi: xoa ban trong fitness_goal_page.dart, import tu fitness_model.dart duy nhat.
  - Tao FitnessFlowPage (coordinator widget) quan ly luong Goal → Exercise → Workout voi back navigation va AnimatedSwitcher.
  - Gan fitness vao navigation chinh: Dashboard feature card "Tap the duc" → HomeShell._openFitness() → FitnessFlowPage.
  - Thay the card "Nhat ky suc khoe" (coming soon) bang card "Tap the duc" (functional) tren Dashboard grid.
  - Cap nhat UI.md: them Nhom 11b AI Fitness Coach voi dac ta day du (layout, voice script, accessibility).
  - Cap nhat project.md: them thong tin Module 6 Fitness, navigation flow, FitnessGoal single source of truth.
- File da sua:
  - `apps/mobile_flutter/lib/features/fitness/presentation/fitness_goal_page.dart` (redesign + fix import)
  - `apps/mobile_flutter/lib/features/fitness/presentation/exercise_selection_page.dart` (redesign)
  - `apps/mobile_flutter/lib/features/fitness/presentation/fitness_flow_page.dart` (new - coordinator)
  - `apps/mobile_flutter/lib/features/home/presentation/dashboard_page.dart` (them onOpenFitness + fitness card)
  - `apps/mobile_flutter/lib/features/home/presentation/home_shell.dart` (them _openFitness + import)
  - `docs/UI.md` (them Nhom 11b)
  - `docs/project.md` (them thong tin fitness)
  - `docs/status.md`
- Trang thai: done
- Ghi chu tiep theo:
  - Workout page co `_startFrameProcessing()` dang de trong — can implement camera stream processing de pose detection chay real-time.
  - Voice command "Tap the duc" chua duoc implement trong voice navigation system.
  - Can test tren thiet bi that voi camera de xac nhan ML Kit Pose Detection hoat dong.

- Ngay gio: 2026-02-26 15:50 UTC+07
- AI phu trach: Windsurf (Cascade)
- Viec da lam:
  - Fix compile error: HomeShell van pass onOpenFitness cho DashboardPage da bi user xoa → loai bo param va unused import.
  - Tao Achievement/Streak system hoan chinh:
    - `core/models/achievement_model.dart`: AchievementCategory, AchievementTier, AchievementDefinition, AchievementProgress, ActivityStreak, UserAchievementSummary, AchievementDatabase (16 thanh tuu predefined).
    - `core/services/achievement_service.dart`: Quan ly streak, progress, XP, luu local bang SharedPreferences. Tu dong check achievement khi record activity.
    - `features/achievements/presentation/achievements_page.dart`: UI hien thi level/XP, streaks, filter theo category, progress bar cho tung achievement. GlassTheme.
  - Tao 3D Doctor Hub (Module 7 — Talking Tom style):
    - `core/services/model_download_service.dart`: Lazy-download 3D model (khong di kem app, tai khi can). Mock download flow, san sang thay bang HTTP thuc.
    - `features/doctor_hub/presentation/doctor_hub_page.dart`: Man hinh tuong tac voi bac si 3D giua man hinh, 6 nut dieu huong xung quanh (Hoi benh, Quet thuoc, Tap the duc, Vuon Tam Hon, Thanh tuu, Ho so). Speech bubble, breathing animation, sign language bar, download prompt, settings bottom sheet.
  - Cap nhat Dashboard (StatefulWidget):
    - Them banner "Bac si 3D" de truy cap Doctor Hub.
    - Them Streaks row hien thi chuoi hoat dong dang active.
    - Them card "Thanh tuu" trong feature list.
    - Thay card "Ho so ca nhan" bang "Thanh tuu" de tang tuong tac.
  - Cap nhat HomeShell: them _openDoctorHub() va_openAchievements(), wire navigation tu Dashboard.
  - Cap nhat project.md: them thong tin Achievement system, Doctor Hub, lazy-download, navigation moi.
- File da sua:
  - `apps/mobile_flutter/lib/core/models/achievement_model.dart` (new)
  - `apps/mobile_flutter/lib/core/services/achievement_service.dart` (new)
  - `apps/mobile_flutter/lib/core/services/model_download_service.dart` (new)
  - `apps/mobile_flutter/lib/features/achievements/presentation/achievements_page.dart` (new)
  - `apps/mobile_flutter/lib/features/doctor_hub/presentation/doctor_hub_page.dart` (new)
  - `apps/mobile_flutter/lib/features/home/presentation/dashboard_page.dart` (updated: StatefulWidget, streaks, doctor hub banner, achievements card)
  - `apps/mobile_flutter/lib/features/home/presentation/home_shell.dart` (updated: them navigation methods + imports)
  - `docs/project.md` (updated)
  - `docs/status.md` (updated)
- Trang thai: done
- TODO cho user (3D Model):
  - Tao model 3D bac si (.glb format, ~25MB) voi animation set: idle, wave, talk, sign_language.
  - Host model tren CDN (Firebase Storage hoac tuong tu), cap nhat downloadUrl trong model_download_service.dart.
  - Tich hop flutter package: `model_viewer_plus` hoac `flutter_3d_controller` de render model trong doctor_hub_page.dart.
  - Tao bo animation ngon ngu ky hieu Viet Nam cho model.
  - Implement voice mimic (nhai giong noi) su dung flutter_tts + audio processing.
- Ghi chu tiep theo:
  - Achievement service chua ket noi voi cac feature thuc te (fitness workout completion, consult completion, etc.) — can goi `recordActivity()` tai cac diem tuong ung.
  - Doctor Hub dang dung placeholder emoji thay vi model 3D that — can 3D model + model_viewer package.
  - Can them model_viewer_plus vao pubspec.yaml khi co model that.

### UI/UX Psychology Audit & Fixes (Feb 2026)

- Danh gia toan bo UI dua tren: Hick's Law, Fitts's Law, Gestalt, Color Psychology, Cognitive Load, WCAG
- Diem tong: 6.1/10 truoc fix → ~8/10 sau fix
- 6 khuyết điểm da sua:
  1. **Bottom nav trang pha vo glass theme (Gestalt Continuity)** → Thay bang glass-style dark nav voi animation
  2. **Dashboard qua tai (Hick's Law)** → Tai cau truc thanh 5 zones: Primary CTA → Streaks → Features → Explore → Summary, them section labels voi accent bar
  3. **Profile dung gradient xanh duong rieng (Gestalt Similarity)** → Doi sang GlassTheme.scaffoldBackground thong nhat
  4. **textMuted 50% khong dat WCAG AA (Accessibility)** → Tang len 65% (0xA6), textDisabled 30%→40%
  5. **Nut khan cap trong dua gion (Trust/Safety)** → Thiet ke lai voi Icon + "115" text + Semantics label + wired EmergencyService
  6. **Du lieu khuyet tat thu thap nhung khong dung (Phantom Accessibility)** → Tao AccessibilityConfig service, wire vao app.dart, Dashboard tu dieu chinh font/icon/spacing/contrast, Profile hien thi trang thai dieu chinh
- Files modified:
  - `apps/mobile_flutter/lib/features/home/presentation/home_shell.dart` (glass bottom nav)
  - `apps/mobile_flutter/lib/features/home/presentation/dashboard_page.dart` (5-zone layout, section labels, emergency button, adaptive cards)
  - `apps/mobile_flutter/lib/features/profile/presentation/profile_page.dart` (GlassTheme bg, a11y indicator)
  - `apps/mobile_flutter/lib/core/theme/glass_theme.dart` (textMuted/textDisabled contrast fix)
  - `apps/mobile_flutter/lib/app.dart` (wire AccessibilityConfig)
- Files created:
  - `apps/mobile_flutter/lib/core/services/accessibility_config.dart` (singleton, computed adaptive values from HealthProfile.difficulties)
- Trang thai: done
- QUAN TRONG cho AI agents khac: Khi tao UI moi, luon doc AccessibilityConfig.instance de lay fontScale, iconScale, minTouchTarget, elementSpacing, highContrast. Khong hardcode font size/spacing.
