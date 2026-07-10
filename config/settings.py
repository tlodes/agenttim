import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "AgentTim")
    DEBUG_MODE: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
    AZURE_OPENAI_MODEL: str = os.getenv("AZURE_OPENAI_MODEL", "gpt-5.4-mini")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    MCP_BENCH_BASE_URL: str = os.getenv("MCP_BENCH_BASE_URL", "http://localhost:9000")
    MCP_BFCL_BASE_URL: str = os.getenv("MCP_BFCL_BASE_URL", "http://localhost:9100")

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
