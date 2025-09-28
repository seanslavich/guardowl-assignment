import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    sqlite_db_path: str = "guard_owl.db"
    
    # Vector Database
    chroma_persist_directory: str = "./chroma_db"
    
    # Groq API
    groq_api_key: Optional[str] = None
    
    # Embedding Model
    embedding_model: str = "all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"

settings = Settings()