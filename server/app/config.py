from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    host: str = Field(default="0.0.0.0", alias="RESOCALL_HOST")
    port: int = Field(default=8000, alias="RESOCALL_PORT")

    data_dir: Path = Field(default=Path("./data"), alias="RESOCALL_DATA_DIR")
    upload_dir: Path = Field(default=Path("./data/uploads"), alias="RESOCALL_UPLOAD_DIR")
    result_dir: Path = Field(default=Path("./data/results"), alias="RESOCALL_RESULT_DIR")
    log_dir: Path = Field(default=Path("./data/logs"), alias="RESOCALL_LOG_DIR")

    allowed_extensions: str = Field(default="wav,mp3", alias="RESOCALL_ALLOWED_EXTENSIONS")
    asr_model: str = Field(default="base", alias="RESOCALL_ASR_MODEL")
    denoise: bool = Field(default=True, alias="RESOCALL_DENOISE")
    max_workers: int = Field(default=2, alias="RESOCALL_MAX_WORKERS")
    max_upload_mb: int = Field(default=250, alias="RESOCALL_MAX_UPLOAD_MB")

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_extensions.split(",") if ext.strip()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
