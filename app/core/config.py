from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # Database Configuration
    DATABASE_URL: PostgresDsn
    
    # Model Configuration
    ASR_MODEL: str = "whisper-large-v2"
    TTS_MODEL: str = "resemble-ai"
    LLM_MODEL: str = "mistral-7b"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    
    # Vector Database
    VECTOR_DB_TYPE: str = "faiss"
    VECTOR_DB_PATH: str = "./data/vector_store"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    RESEMBLE_AI_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Monitoring
    PROMETHEUS_MULTIPROC_DIR: str = "./data/prometheus"
    LOG_LEVEL: str = "INFO"
    
    # Cache Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600
    
    # Storage
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            raise ValueError("DATABASE_URL must be set")
        return v
    
    @validator("JWT_SECRET_KEY", pre=True)
    def validate_jwt_secret(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            raise ValueError("JWT_SECRET_KEY must be set")
        return v
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 