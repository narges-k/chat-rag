"""Application settings, loaded from environment variables / .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-5"
    docs_dir: str = "docs"
    chroma_dir: str = ".chroma"
    top_k: int = 4


settings = Settings()
