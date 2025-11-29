"""Configuration loader for the Privacy Sandbox."""

from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "settings.yaml"


class AppConfig(BaseModel):
    name: str = "Privacy Sandbox"
    debug: bool = False
    max_file_size_mb: int = 20
    supported_extensions: list[str] = Field(default_factory=lambda: [".csv", ".tsv", ".xlsx"])


class DataConfig(BaseModel):
    min_rows: int = 5
    upload_dir: Path = ROOT_DIR / "data" / "uploads"
    examples_dir: Path = ROOT_DIR / "data" / "examples"

    @validator("upload_dir", "examples_dir", pre=True)
    def _as_path(cls, value: Any) -> Path:
        return Path(value)


class PrivacyDefaults(BaseModel):
    default_k: int = 5
    default_l: int = 2
    default_t: float = 0.2
    default_epsilon: float = 1.0


class Settings(BaseSettings):
    app: AppConfig = AppConfig()
    data: DataConfig = DataConfig()
    privacy: PrivacyDefaults = PrivacyDefaults()

    class Config:
        frozen = True


def load_settings(config_path: Path | None = None) -> Settings:
    """Load settings from YAML and return Settings object."""
    path = config_path or DEFAULT_CONFIG_PATH
    with path.open("r", encoding="utf-8") as stream:
        payload: Dict[str, Any] = yaml.safe_load(stream) or {}
    return Settings(**payload)


settings = load_settings()

