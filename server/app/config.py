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
    postgres_dsn: str = Field(
        default="postgresql://resocall:resocall@127.0.0.1:5432/resocall",
        alias="RESOCALL_POSTGRES_DSN",
    )

    allowed_extensions: str = Field(default="wav,mp3", alias="RESOCALL_ALLOWED_EXTENSIONS")
    asr_model: str = Field(default="base", alias="RESOCALL_ASR_MODEL")
    denoise: bool = Field(default=True, alias="RESOCALL_DENOISE")
    external_asr_module: bool = Field(default=True, alias="RESOCALL_EXTERNAL_ASR_MODULE")
    external_asr_module_path: Path = Field(default=Path("../ASR/ASR.py"), alias="RESOCALL_ASR_MODULE_PATH")
    max_workers: int = Field(default=2, alias="RESOCALL_MAX_WORKERS")
    max_upload_mb: int = Field(default=250, alias="RESOCALL_MAX_UPLOAD_MB")
    cors_allow_origins: str = Field(default="*", alias="RESOCALL_CORS_ALLOW_ORIGINS")
    trusted_proxy_ips: str = Field(default="*", alias="RESOCALL_TRUSTED_PROXY_IPS")

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_extensions.split(",") if ext.strip()}

    @property
    def cors_allow_origins_list(self) -> list[str]:
        origins = [item.strip() for item in self.cors_allow_origins.split(",") if item.strip()]
        return origins or ["*"]

    @property
    def trusted_proxy_ips_list(self) -> list[str]:
        ips = [item.strip() for item in self.trusted_proxy_ips.split(",") if item.strip()]
        return ips or ["*"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
