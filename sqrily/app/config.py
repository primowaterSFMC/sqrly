from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore", env_file=".env", case_sensitive=True)

    # App settings
    app_name: str = "Sqrily ADHD Planner"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    database_url: Optional[str] = None
    database_echo: bool = False
    
    # JWT and Security
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # OAuth Settings
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    apple_client_id: Optional[str] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_private_key: Optional[str] = None
    
    # OpenAI
    openai_api_key: str = "dev-openai-key-set-in-production"
    openai_model: str = "gpt-4-1106-preview"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.7
    
    # Redis
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Celery
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    # CORS - Environment specific configuration
    allowed_origins: List[str] = []
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: List[str] = ["*"]

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.debug:
            # Development environment - allow localhost
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001"
            ]
        else:
            # Production environment - use configured origins or default secure list
            return self.allowed_origins if self.allowed_origins else [
                "https://app.sqrily.com",
                "https://sqrily.com"
            ]
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # ADHD-specific settings
    max_overwhelm_threshold: int = 10
    default_focus_duration: int = 25
    default_break_duration: int = 5
    hyperfocus_warning_threshold: int = 90
    
    # Integrations
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            return v
        return "postgresql://user:password@localhost/sqrily_adhd_planner"

    @field_validator("celery_broker_url", mode="before")
    @classmethod
    def assemble_celery_broker(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            return v
        # Note: In Pydantic v2, we can't access other field values in validators
        # This will need to be handled differently if redis_url dependency is needed
        return "redis://localhost:6379"

    @field_validator("celery_result_backend", mode="before")
    @classmethod
    def assemble_celery_backend(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            return v
        # Note: In Pydantic v2, we can't access other field values in validators
        # This will need to be handled differently if redis_url dependency is needed
        return "redis://localhost:6379"
    


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()