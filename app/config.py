# app/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "Fyndly App"
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "chroma_db")
    collection_name: str = os.getenv("CHROMA_COLLECTION", "site_content")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    web_site: str = "https://lycheethings.com"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

settings = Settings()

