from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()  # Loads environment variables from .env file

secret_key = os.getenv("PERDIX_JWT")
storage_type = os.getenv("STORAGE_TYPE")
if storage_type == "s3":
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
else:
    STORAGE_TYPE = "local"
class Settings(BaseSettings):
    PROJECT_NAME: str = "Munify API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Server Configuration
    HOST: str = "127.0.0.1"  # Server host
    PORT: int = 8000  # Server port
    
    # Environment
    APP_ENV: str = "dev"  # dev, staging, prod
    
    # Database (PostgreSQL)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "root"
    POSTGRES_DB: str = "munify_db"
    SQL_ECHO: bool = False  # SQLAlchemy echo setting
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080","http://localhost:5173"]
    
    # External Perdix user service
    PERDIX_BASE_URL: str = "https://uat-lp.perdix.co.in/perdix-server"
    PERDIX_JWT: str =secret_key;
    PERDIX_PAGE_URI: str = "Page/Engine/user.UserMaintanence"
    PERDIX_ORIGIN: str = "https://uat-lp.perdix.co.in"

    FRONTEND_ORIGIN: str = "http://localhost:5173"
    
    # S3 Storage Configuration
    AWS_ACCESS_KEY_ID: str =""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_NAME: str = ""
    AWS_S3_ENDPOINT_URL: str = ""  # Optional: for S3-compatible services (MinIO, etc.)
    STORAGE_TYPE: str = "local"  # s3 or local (for development)
    
    # File Upload Settings
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf,doc,docx,xls,xlsx,mp4,avi,mov,zip"
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
