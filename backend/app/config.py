# Source of truth for parsing, validating, and serving JWT secrets and algorithm settings to the rest of your FastAPI app
import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve absolute path to the root .env (config.py -> app -> backend -> root)
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore" # Prevents crashes from DB variables in the same .env
    )
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings()