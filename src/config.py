import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN')

    PREFIX: str = '.'
    DEBUG: bool = True

    if not DISCORD_TOKEN:
        raise RuntimeError('DISCORD_TOKEN não encontrado no .env')