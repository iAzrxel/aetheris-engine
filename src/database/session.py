import mysql.connector
from config import Config

def get_connection():
    try:
        return mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
    except Exception as e:
        print(f'Erro ao conectar ao MySQL: {e}')
