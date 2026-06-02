# config/settings.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    llm_timeout_seconds: float = 120.0
    llm_max_retries: int = 3

    # Database
    db_url: str = "sqlite+aiosqlite:///./data/edusystem.db"
    knowledge_graph_path: str = "./data/kuzu_db"
    learner_graph_path: str = "./data/learner_graph"

    # System
    watch_folder: str = "./watch"
    log_level: str = "DEBUG"
    stream_dir: str = "./config/streams"
    markdown_cache_dir: str = "./data/markdown_cache"

    # Application
    app_name: str = "EduSystem"
    app_version: str = "0.1.0"

    def ensure_directories(self) -> None:
        """Create all required directories on startup."""
        dirs = [
            Path(self.knowledge_graph_path).parent,
            Path(self.learner_graph_path).parent,
            Path(self.watch_folder),
            Path(self.markdown_cache_dir),
            Path("logs"),
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)


# Single instance — import this everywhere
settings = Settings()