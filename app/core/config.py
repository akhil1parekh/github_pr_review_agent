from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # API Settings
    API_HOST: str = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT: int = os.environ.get("API_PORT", 8000)
    DEBUG: bool = os.environ.get("DEBUG", False)
    PROJECT_NAME: str = "GitHub PR Review Agent"

    # GitHub Settings
    GITHUB_TOKEN: str

    # Celery Settings
    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://redis:6379/0"
    )

    # Redis Settings
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")
    REDIS_PORT: int = os.environ.get("REDIS_PORT", 6379)

    # LLM Settings
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY")
    LLM_MODEL: str = os.environ.get("LLM_MODEL", "gpt-4o")

    @field_validator("GITHUB_TOKEN", "OPENAI_API_KEY")
    def validate_api_keys(cls, v, values, **kwargs):
        if not v:
            raise ValueError(f"API key is required")
        return v

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
