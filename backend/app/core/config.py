from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Clip Agent API"
    app_version: str = "1.0.0"
    environment: str = "development"
    speech_provider: str = "whisper"
    database_url: str = "sqlite:///./data/ai_clip_agent.db"

    storage_provider: str = "local"
    local_storage_path: str = "data/uploads"

    r2_bucket_name: str = ""
    r2_endpoint_url: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_public_base_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()