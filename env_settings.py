from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent

class EnvSettings(BaseSettings):
    GOOGLE_API_KEY : str = None
    PINECONE_API_KEY: str = None
    PINECONE_INDEX_NAME: str = None
    GOOGLE_EMBEDDINGS_MODEL: str = None
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )