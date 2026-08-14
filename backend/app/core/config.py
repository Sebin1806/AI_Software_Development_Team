from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

backend_dir = Path(__file__).resolve().parent.parent.parent
env_files = [
    str(backend_dir / ".env"),
    str(backend_dir.parent / ".env"),
    ".env"
]


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "AI Software Development Team"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_software_team"

    # JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Ollama / LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_TIMEOUT: int = 180
    LLM_MOCK_MODE: bool = False

    model_config = SettingsConfigDict(
        env_file=env_files,
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()