# app/core/config.py

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    Values are loaded from environment variables (or a local .env file).
    """

    # --- App metadata ---
    APP_NAME: str = "Iloilo River Plains Subdivision Village 3 - HOA Management System"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True

    # --- Session / security ---
    SECRET_KEY: str
    SESSION_COOKIE_NAME: str = "hoa_session"

    # --- Supabase ---
    SUPABASE_URL: str
    SUPABASE_PUBLISHABLE_KEY: str
    SUPABASE_SECRET_KEY: str

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance so environment variables
    are parsed only once per process.
    """
    return Settings()