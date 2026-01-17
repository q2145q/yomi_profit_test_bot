"""
Главный файл Telegram бота
Статус: ✅ Работает базовая версия + AI-парсинг
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

from config import BOT_TOKEN
from database import init_db
from handlers import miniapp, start, projects, shifts

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
    
    # Создание диспетчера с хранилищем для FSM
    dp = Dispatcher(storage=MemoryStorage())
    
    # 🐛 ОТЛАДКА: Логируем ВСЕ апдейты ДО обработки
    @dp.update.outer_middleware()
    async def log_all_updates(handler, event: Update, data):
        """Middleware для логирования всех апдейтов"""
        if event.message:
            msg = event.message
            print("\n" + "🐛"*30)
            print("📨 ВХОДЯЩЕЕ СООБЩЕНИЕ:")
            print(f"  От: {msg.from_user.id} (@{msg.from_user.username})")
            
            # Проверяем web_app_data
            if hasattr(msg, 'web_app_data') and msg.web_app_data:
                print(f"  ✅ WEB_APP_DATA обнаружен!")
                print(f"  📦 Данные: {msg.web_app_data.data[:200]}...")
            else:
                print(f"  ❌ WEB_APP_DATA отсутствует")
            
            # Другие типы контента
            if msg.text:
                print(f"  💬 Текст: {msg.text}")
            if msg.photo:
                print(f"  🖼 Фото")
            
            print("🐛"*30 + "\n")
        
        # Продолжаем обработку (НЕ блокируем!)
        return await handler(event, data)
    
    # Подключение роутеров (в правильном порядке!)
    dp.include_router(miniapp.router)  # Сначала Mini App
    dp.include_router(start.router)    # Потом start
    dp.include_router(projects.router)
    dp.include_router(shifts.router)
    
    # Запуск бота
    logging.info("🚀 Бот запущен с отладочным middleware!")
    logging.info("📍 Все апдейты будут логироваться БЕЗ блокировки обработчиков")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())