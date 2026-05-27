from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    app_name: str = "MediSign AI Backend"
    app_version: str = "0.2.0"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    # Default to False so production deployments don't accidentally enable
    # auto-reload. Local devs explicitly set BACKEND_RELOAD=true in .env.
    backend_reload: bool = False
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite:///data/dev_backend.sqlite3"
    api_base_url: str = "http://10.0.2.2:8000/api/v1"
    use_mock_api: bool = True

    email_host: str = ""
    email_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_from_name: str = "MediSign AI"
    email_use_tls: bool = True
    frontend_base_url: str = "http://localhost:3000"

    # Comma-separated list of allowed CORS origins (in addition to localhost
    # which is always permitted by `cors_allow_origin_regex`). Example:
    #   BACKEND_CORS_ALLOWED_ORIGINS=https://app.medisign.vn,https://staging.medisign.vn
    cors_allowed_origins: str = ""
    cors_allow_origin_regex: str = (
        r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$"
    )

    # JWT — default value is intentionally invalid in production. Production
    # deployments MUST override BACKEND_JWT_SECRET_KEY with a 32+ byte secret.
    # `app.core.security.assert_production_secret()` enforces this at startup.
    jwt_secret_key: str = "change-this-secret-key-at-least-32-bytes"
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = 15
    jwt_refresh_token_days: int = 30

    password_hash_iterations: int = 120_000

    # Rate-limiting (slowapi). Format: "<count>/<period>" e.g. "5/minute".
    rate_limit_enabled: bool = True
    rate_limit_login: str = "10/minute"
    rate_limit_forgot_password: str = "5/minute"
    rate_limit_register: str = "5/minute"
    rate_limit_ai_chat: str = "30/minute"

    ai_provider: str = "rule_based"
    ai_model: str = "google/medgemma-1.5-4b-it"
    ai_medical_model: str = "medisign-medgemma-medical"
    ai_psychology_model: str = "medisign-medgemma-psychology"
    ai_base_url: str = "http://localhost:8080/v1"
    ai_api_key: str = ""
    ai_request_timeout_seconds: float = 30.0

    rag_enabled: bool = True
    rag_knowledge_base_path: str = "data/knowledge_base/knowledge_base.json"
    rag_default_top_k: int = 5
    rag_max_context_chars: int = 6000
    rag_min_score: float = 0.15

    medgemma_base_model: str = "google/medgemma-1.5-4b-it"
    medgemma_medical_adapter_path: str = "../../output/medisign-medgemma4b-adapter"
    medgemma_psychology_adapter_path: str = "../../output/medisign_medgemma4b_psychology/adapter"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="BACKEND_", extra="ignore")


settings = Settings()
