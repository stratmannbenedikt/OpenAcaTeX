import toml
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class OpenRouterConfig(BaseModel):
    api_key: str = ""
    model: str = "anthropic/claude-3-haiku"
    model_config = ConfigDict(extra="ignore")


class MockConfig(BaseModel):
    enabled: bool = True
    model_config = ConfigDict(extra="ignore")


class ApiConfig(BaseModel):
    openrouter: OpenRouterConfig = OpenRouterConfig()
    mock: MockConfig = MockConfig()
    active_provider: str = "mock"
    model_config = ConfigDict(extra="ignore")


class AppConfig(BaseModel):
    api: ApiConfig = ApiConfig()
    model_config = ConfigDict(extra="ignore")


CONFIG_DIR = Path(".openacatex")
CONFIG_FILE = CONFIG_DIR / "config.toml"


def load_config() -> AppConfig:
    if not CONFIG_FILE.exists():
        return AppConfig()
    data = toml.loads(CONFIG_FILE.read_text())
    return AppConfig.model_validate(data)


def save_config(config: AppConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(toml.dumps(config.model_dump(mode='python')))