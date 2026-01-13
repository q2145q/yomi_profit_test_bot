"""
Главный файл Telegram бота
Статус: ✅ Работает базовая версия
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db
from handlers import start

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Запуск бота"""
    # Инициализация БД
    await init_db()
    
    # Создание бота
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    
    # Создание диспетчера
    dp = Dispatcher()
    
    # Подключение роутеров
    dp.include_router(start.router)
    
    # Запуск бота
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())