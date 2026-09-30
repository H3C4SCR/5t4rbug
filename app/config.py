import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    INSTANCE_PATH = BASE_DIR / "instance"
    DATABASE_URL = os.environ.get("DATABASE_URL")
    DATABASE = (
        Path(os.environ["DATABASE_PATH"])
        if os.environ.get("DATABASE_PATH")
        else INSTANCE_PATH / "5t4rbug.sqlite3"
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key")
    AUTH_COOKIE_NAME = "5t4rbug_auth"
    SESSION_COOKIE_NAME = "5t4rbug_flash"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_MAX_AGE = 60 * 60 * 24 * 7
    MAX_CONTENT_LENGTH = 32 * 1024
