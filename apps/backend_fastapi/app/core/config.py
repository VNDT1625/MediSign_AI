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

    model_config = SettingsConfigDict(env_file=".env", env_prefix="BACKEND_")


settings = Settings()
