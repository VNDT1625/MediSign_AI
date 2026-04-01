# TODO - Fix bugs in apps folder

- [x] 1. `app/services/ai_triage_service.py` - Đổi `find_phrase_stems` → `find_phrase_starts`
- [x] 2. `app/services/ai_triage_service.py` - Sửa f-string: `""` → `"""`
- [x] 3. `app/services/ai_triage_service.py` - Sửa `_build_triage_prompt` dùng `getattr` an toàn cho `age`, `gender`, `duration`
- [x] 4. `app/database/cloud_models.py` - Sửa `latitude`/`longitude` type annotation: `Mapped[Optional[float]]` → `Mapped[Optional[str]]`
- [x] 5. `app/database/cloud_models.py` - Sửa `FitnessGoal.target_value`/`current_progress` column: `Integer` → `Float`
- [x] 6. `pyproject.toml` - Thêm `sqlalchemy>=2.0.0` và `psycopg[binary]>=3.1.0` dependencies
- [x] 7. `tests/test_auth.py` - Sửa truy cập response: `login_payload["tokens"]["access_token"]`
- [x] 8. `tests/test_protected_endpoints.py` - Sửa truy cập response: `login_payload["tokens"]["access_token"]`
