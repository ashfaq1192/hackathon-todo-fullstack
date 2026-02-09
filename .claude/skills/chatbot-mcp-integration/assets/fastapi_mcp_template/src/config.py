import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings class to load environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # Ignore extra env vars not defined here
        case_sensitive=False,  # Case-insensitive matching for env var names
    )

    DATABASE_URL: str
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-xxx") # Default for development
    BETTER_AUTH_SECRET: str # Secret for JWT validation
    JWT_ALGORITHM: str = "HS256"


settings = Settings()