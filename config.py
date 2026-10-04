import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "sih26086-local-dev-secret")
    DATABASE_PATH = os.environ.get(
        "DATABASE_PATH", str(BASE_DIR / "database" / "sih26086.sqlite3")
    )
    DATA_DIR = BASE_DIR / "data"
    SAMPLE_DATA_DIR = DATA_DIR / "sample"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    MODELS_DIR = BASE_DIR / "models"
    FRONTEND_DIR = BASE_DIR / "frontend"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB maximum file upload limit
    SUPPORTED_LANGUAGES = ["en", "te", "hi", "ta", "kn", "ur", "ml"]
    DEFAULT_LANGUAGE = "en"
    PRODUCT_NAME = "VarshaSetu"
    PRODUCT_TAGLINE = "Bridging Climate Intelligence with Every Farmer"
    PRODUCT_SUBTITLE = "Hyperlocal Monsoon Onset, Break & Agricultural Advisory System"
