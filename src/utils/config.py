"""Configuración del proyecto usando Pydantic Settings."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Configuración principal del proyecto."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # Pinecone Configuration (opcional)
    pinecone_api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(None, env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field("legal-assistant-index", env="PINECONE_INDEX_NAME")
    
    # Database Configuration
    database_url: str = Field(
        "postgresql://username:password@localhost:5432/legal_assistant",
        env="DATABASE_URL"
    )
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # API Configuration
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    api_debug: bool = Field(True, env="API_DEBUG")
    
    # Scraping Configuration
    scrape_delay: int = Field(1, env="SCRAPE_DELAY")
    user_agent: str = Field("LegalAssistant/1.0", env="USER_AGENT")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/app.log", env="LOG_FILE")
    
    # Vector Database Configuration
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="CHUNK_OVERLAP")
    embedding_model: str = Field("text-embedding-ada-002", env="EMBEDDING_MODEL")
    
    # Legal Sources URLs
    dof_base_url: str = Field("https://www.dof.gob.mx/", env="DOF_BASE_URL")
    constitucion_url: str = Field(
        "https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf",
        env="CONSTITUCION_URL"
    )
    orden_juridico_url: str = Field(
        "http://www.ordenjuridico.gob.mx/",
        env="ORDEN_JURIDICO_URL"
    )
    
    # Web scraping settings
    user_agent: str = Field("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", env="USER_AGENT")
    scrape_delay: float = Field(1.0, env="SCRAPE_DELAY")  # Delay between requests in seconds
    request_timeout: int = Field(30, env="REQUEST_TIMEOUT")  # Request timeout in seconds
    max_retries: int = Field(3, env="MAX_RETRIES")  # Maximum number of retries for failed requests
    
    # Project Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "data")
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "logs")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()