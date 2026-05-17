from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MediSign AI Backend"
    app_version: str = "0.2.0"
    api_prefix: str = "/api/v1"

    jwt_secret_key: str = "change-this-secret-key-at-least-32-bytes"
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = 15
    jwt_refresh_token_days: int = 30

    password_hash_iterations: int = 120_000

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
    medgemma_medical_adapter_path: str = "../../output/medisign_medgemma4b/adapter"
    medgemma_psychology_adapter_path: str = "../../output/medisign_medgemma4b_psychology/adapter"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="BACKEND_", extra="ignore")


settings = Settings()
