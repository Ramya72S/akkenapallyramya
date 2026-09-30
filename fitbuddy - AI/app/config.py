from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application settings
    app_name: str = "FitBuddy"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./fitbuddy.db"

    # Gemini API
    gemini_api_key: str | None = None

    # AI models
    ai_workout_model: str = "gemini-2.5-flash"
    ai_tip_model: str = "gemini-2.5-flash"

    # Environment configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Create settings object
settings = Settings()
