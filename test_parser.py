"""
Тест модуля парсинга сообщений
"""
import asyncio
from parser import parse_shift_message
from datetime import datetime
import json

async def test():
    print("🧪 Тест парсинга сообщений\n")
    
    # Текущая дата и время для тестов
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    print(f"Текущая дата: {current_date}")
    print(f"Текущее время: {current_time}\n")
    
    # Список тестовых сообщений
    test_messages = [
        "Смена 07:00 до 23:00 + обед + ронин",
        "Работал вчера с 9 до 18",
        "07:00 - 19:00 текущий обед",
        "Работал до вечера",  # Недостаточно данных
    ]
    
    # Доступные услуги
    services = ["обед", "ронин", "текущий обед"]
    
    # Тестируем каждое сообщение
    for i, message in enumerate(test_messages, 1):
        print(f"Тест {i}: '{message}'")
        print("-" * 50)
        
        result = await parse_shift_message(
            message=message,
            current_date=current_date,
            current_time=current_time,
            base_hours=12,
            services=services
        )
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n")

asyncio.run(test())
