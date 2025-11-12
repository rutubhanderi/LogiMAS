import os
from dotenv import load_dotenv
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    DB_CONNECTION_STRING: str = os.getenv("DB_CONNECTION_STRING")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    SUPABASE_URL: str = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_DB_PASSWORD: str = os.getenv("SUPABASE_DB_PASSWORD")

    # CORS Settings
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # Security Settings
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = os.getenv("SECRET_KEY", JWT_SECRET_KEY)

    def __init__(self):
        """Validate required settings"""
        if not self.DATABASE_URL:
            print("ERROR: DATABASE_URL is not set in .env file", file=sys.stderr)
            print(
                "Please check your .env file and ensure DATABASE_URL is configured",
                file=sys.stderr,
            )

        if not self.JWT_SECRET_KEY:
            print("WARNING: JWT_SECRET_KEY is not set in .env file", file=sys.stderr)
            print("Using default key - NOT SECURE FOR PRODUCTION!", file=sys.stderr)


settings = Settings()
