import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")
    PREFIX: str = "."
    DEBUG: bool = True

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME", "aetheris")

    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN não encontrado no .env")