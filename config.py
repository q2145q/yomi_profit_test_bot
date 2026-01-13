"""
Конфигурация бота
Загружает переменные окружения из .env
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "data.db")