from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================
    # Application
    # =========================

    app_name: str = "AI Clip Agent API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # =========================
    # Database
    # =========================

    database_url: str = "sqlite:///./data/ai_clip_agent.db"

    # =========================
    # Speech
    # =========================

    speech_provider: str = "whisper"

    # =========================
    # Storage
    # =========================

    storage_provider: str = "local"
    local_storage_path: str = "data/uploads"

    r2_bucket_name: str = ""
    r2_endpoint_url: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_public_base_url: str | None = None

    # =========================
    # AI Runtime
    # =========================

    default_ai_provider: str = "gemini"

    ai_timeout_seconds: int = 60
    ai_max_retries: int = 2
    ai_temperature: float = 0.2

    # =========================
    # Gemini
    # =========================

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # =========================
    # OpenAI
    # =========================

    openai_api_key: str = ""
    openai_model: str = "gpt-5"

    # =========================
    # Claude
    # =========================

    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4"

    # =========================
    # Provider Feature Flags
    # =========================

    enable_gemini: bool = True
    enable_openai: bool = True
    enable_claude: bool = False
        # =========================
    # Asset Providers
    # =========================

    pexels_api_key: str = ""
    pixabay_api_key: str = ""
    freesound_api_key: str = ""

    enable_pexels: bool = True
    enable_pixabay: bool = True
    enable_freesound: bool = True

    default_broll_provider: str = "pexels"
    default_music_provider: str = "pixabay"
    default_sfx_provider: str = "freesound"

    asset_provider_timeout_seconds: int = 30
    asset_provider_max_retries: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()