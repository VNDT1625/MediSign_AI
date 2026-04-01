# project.md

Muc dich: Tong hop thong tin du an, pham vi, tien do tong, va quyet dinh lon.

## Tong quan

- Ten du an: MediSign AI
- Muc tieu: Hoan thien gan nhu toan bo trong 10 tuan voi nhieu AI lam song song.
- AI chinh: Qwen cloud.
- Fallback: Gemini (tuy chon, uu tien toi gian).
- Ngan sach AI: duoi 1.000.000 VND/10 tuan.

## Quyet dinh lon

- Personal adapter hoc tu chat + Soul Garden.
- Uu tien codebase gon, dong nhat, it file du thua.
- Branch strategy: `main`, `dev`, `feature/*`, `hotfix/*`.
- Scaffold monorepo:
  - Flutter app: `apps/mobile_flutter`
  - FastAPI app: `apps/backend_fastapi`
  - Shared contracts: `packages/shared_contracts`
- Module 6 (AI Fitness Coach) da tich hop: Goal → Exercise → Workout flow, dung Google ML Kit Pose Detection.
- FitnessGoal enum chi khai bao 1 noi duy nhat: `core/models/fitness_model.dart`.
- Achievement/Streak system: theo doi chuoi hoat dong (tap the duc, suc khoe, vuon tam hon, hoi benh, quet thuoc). Luu local bang SharedPreferences. Model: `core/models/achievement_model.dart`, Service: `core/services/achievement_service.dart`.
- 3D Doctor Hub (Module 7): man hinh tuong tac kieu Talking Tom — bac si 3D dung giua, buttons dieu huong xung quanh. Ho tro sign language, nhai giong noi, phu hop tre em + nguoi khuyet tat.
- Doctor Hub dung lazy-download: model 3D khong di kem app, tai tu server khi nguoi dung yeu cau (giong tai map PUBG). Service: `core/services/model_download_service.dart`.
- Dashboard layout (GlassTheme): Banner Bac si 3D → Streaks row → Feature cards (Hoi benh, Quet thuoc, Nhat ky, Thanh tuu) → Summary card.
- Navigation: HomeShell (4 tabs) + push routes cho DoctorHub, Achievements, MedicineScan.
- Bat buoc quality gate lint/test/format qua script va CI truoc merge.
- Local dev env dong nhat qua `.env.example`, script bootstrap, Docker Compose (optional).
