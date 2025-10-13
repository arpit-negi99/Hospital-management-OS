import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # Database URL: use DATABASE_URL if provided; otherwise build from env vars; fallback to sqlite
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if not DATABASE_URL:
        db_engine = os.environ.get("DB_ENGINE", "sqlite").lower()
        if db_engine == "mysql":
            user = os.environ.get("DB_USER", "root")
            password = quote_plus(os.environ.get("DB_PASSWORD", ""))
            host = os.environ.get("DB_HOST", "localhost")
            port = os.environ.get("DB_PORT", "3306")
            name = os.environ.get("DB_NAME", "campus_tracker")
            DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
        elif db_engine == "postgres" or db_engine == "postgresql":
            user = os.environ.get("DB_USER", "postgres")
            password = quote_plus(os.environ.get("DB_PASSWORD", ""))
            host = os.environ.get("DB_HOST", "localhost")
            port = os.environ.get("DB_PORT", "5432")
            name = os.environ.get("DB_NAME", "campus_tracker")
            DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
        else:
            DATABASE_URL = "sqlite:////workspace/backend/campus/campus.db"

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login
    REMEMBER_COOKIE_DURATION_DAYS = int(os.environ.get("REMEMBER_DAYS", "14"))

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False
