# config/settings.py

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application
    app_env: str = Field(default="development", env="APP_ENV")
    app_debug: bool = Field(default=True, env="APP_DEBUG")
    app_port: int = Field(default=8000, env="APP_PORT")
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    perplexity_api_key: str = Field(..., env="PERPLEXITY_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(..., env="SUPABASE_SERVICE_KEY")
    
    # Social Media
    facebook_access_token: str = Field(..., env="FACEBOOK_ACCESS_TOKEN")
    facebook_page_id: str = Field(..., env="FACEBOOK_PAGE_ID")
    instagram_access_token: str = Field(..., env="INSTAGRAM_ACCESS_TOKEN")
    instagram_business_account_id: str = Field(..., env="INSTAGRAM_BUSINESS_ACCOUNT_ID")
    whatsapp_business_api_key: str = Field(..., env="WHATSAPP_BUSINESS_API_KEY")
    whatsapp_business_phone_number_id: str = Field(..., env="WHATSAPP_BUSINESS_PHONE_NUMBER_ID")
    
    # Payments
    wompi_public_key: str = Field(..., env="WOMPI_PUBLIC_KEY")
    wompi_private_key: str = Field(..., env="WOMPI_PRIVATE_KEY")
    wompi_webhook_secret: str = Field(..., env="WOMPI_WEBHOOK_SECRET")
    
    # Logistics
    mensajeros_urbanos_api_key: Optional[str] = Field(None, env="MENSAJEROS_URBANOS_API_KEY")
    mensajeros_urbanos_client_id: Optional[str] = Field(None, env="MENSAJEROS_URBANOS_CLIENT_ID")
    
    # Delivery Platforms
    rappi_api_key: Optional[str] = Field(None, env="RAPPI_API_KEY")
    rappi_store_id: Optional[str] = Field(None, env="RAPPI_STORE_ID")
    
    # Agent Configuration
    agent_max_iterations: int = Field(default=10, env="AGENT_MAX_ITERATIONS")
    agent_timeout_seconds: int = Field(default=300, env="AGENT_TIMEOUT_SECONDS")
    agent_temperature: float = Field(default=0.7, env="AGENT_TEMPERATURE")
    
    # Budget Limits (in COP)
    daily_marketing_budget: int = Field(default=500000, env="DAILY_MARKETING_BUDGET")
    daily_inventory_budget: int = Field(default=2000000, env="DAILY_INVENTORY_BUDGET")
    campaign_boost_limit: int = Field(default=100000, env="CAMPAIGN_BOOST_LIMIT")
    
    # Colombian Market
    colombia_tax_rate: float = Field(default=0.19, env="COLOMBIA_TAX_RATE")
    colombia_timezone: str = Field(default="America/Bogota", env="COLOMBIA_TIMEZONE")
    default_currency: str = Field(default="COP", env="DEFAULT_CURRENCY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file_path: str = Field(default="logs/app.log", env="LOG_FILE_PATH")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Database
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()