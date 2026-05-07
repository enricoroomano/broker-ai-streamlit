from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DB_PATH: str = "data/polizze.db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
