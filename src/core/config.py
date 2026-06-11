import logging
from pathlib import Path


from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_PATH = Path(__file__).resolve().parent.parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    title: str = "MemGet"
    version: str = "0.1"


class LoggerConfig(BaseModel):
    lvl: int = logging.INFO
    logs_path: Path = BASE_PATH / "logs" / "app_logs.log"
    log_format: str = (
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    max_bytes: int = 5 * 1024 * 1024
    backup_count: int = 3


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DbConfig(BaseModel):
    url: str = f"sqlite+aiosqlite:///{BASE_PATH}/memget.db"

    convention: dict = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class QdrantConfig(BaseModel):
    host: str = "localhost"
    port: int = 6333


class ModelsConfig(BaseModel):
    embed_model: str = "nomic-embed-text"
    embed_path: str = "/api/embeddings"
    llm_model: str = "qwen2.5"

class SecurityConfig(BaseModel):
    api_key: str 


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_PATH / ".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="forbid",
    )
    logger: LoggerConfig = LoggerConfig()
    api: ApiPrefix = ApiPrefix()
    run: RunConfig = RunConfig()
    db: DbConfig = DbConfig()
    qdrant: QdrantConfig = QdrantConfig()
    models: ModelsConfig = ModelsConfig()
    security: SecurityConfig


settings = Settings() # type: ignore
