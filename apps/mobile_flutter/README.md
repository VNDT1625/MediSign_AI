# Mobile Flutter

MediSign AI cross-platform app — Dart SDK ≥ 3.4, Flutter stable.

State: `flutter_riverpod 2.5`. Navigation: `go_router 14`. HTTP: `dio 5.7`.
On-device ML: `google_mlkit_pose_detection 0.12`. Voice:
`speech_to_text 6.6` + `flutter_tts 4`. Camera: `camera 0.11`.
Code gen: `freezed` + `json_serializable`.

## Install deps

```bash
flutter pub get
```

## Run

```bash
flutter run
```

## Cac module hien co (`lib/features/`)

```
auth/                — Login, register, welcome
onboarding/          — 7-step health survey + mode selector (Hybrid / Local / Cloud)
home/                — 4-tab navigation shell + emergency action button
consult/             — AI symptom consultation (rule-based + AI triage)
medicine_cabinet/    — Personal medicine tracker (cabinet, today, dose history)
medicine_scan/       — Camera-based drug recognition (OCR + MedGemma vision)
soul_garden/         — Mental health, mood journal, OARS prompts
fitness/             — Workout + on-device pose detection
community/           — Anonymous health community
achievements/        — Gamification + tree points
doctor_hub/          — Doctor-facing features
admin/               — Admin panel (mobile shell)
profile/             — User profile + consent flag
settings/            — App settings
```

Consult va medicine hien dang chay tren mock API mac dinh
(`USE_MOCK_API=true` trong `.env`); doi sang `false` va set
`API_BASE_URL=http://10.0.2.2:8000/api/v1` de goi backend FastAPI thuc.

## Test / Lint / Format

```bash
flutter test
flutter analyze
dart format --output=none --set-exit-if-changed .
```
