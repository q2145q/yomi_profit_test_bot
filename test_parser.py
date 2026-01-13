"""
Тест парсинга - проблемные случаи из реального использования
"""
import asyncio
from parser import parse_shift_message
from datetime import datetime
import json

async def test():
    print("🧪 Тест проблемных сообщений\n")
    
    # Текущие дата и время
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    print(f"Текущая дата: {current_date}")
    print(f"Текущее время: {current_time}\n")
    
    # Проблемные сообщения из реального использования
    test_messages = [
        "Вчера с 7 до 23 + текущий",
        "вчера с 7 до 23",
        "Поза вчера с 5 до 22",
        "Поза вчера с 5 утра до 22",
        "с 9 до 18 + текущий",
    ]
    
    # Доступные услуги
    services = ["обед", "ронин", "текущий обед"]
    
    # Тестируем каждое сообщение
    for i, message in enumerate(test_messages, 1):
        print(f"Тест {i}: '{message}'")
        print("-" * 60)
        
        result = await parse_shift_message(
            message=message,
            current_date=current_date,
            current_time=current_time,
            base_hours=12,
            services=services
        )
        
        # Показываем ключевые поля
        print(f"  Дата: {result.get('date')}")
        print(f"  Начало: {result.get('start_time')}")
        print(f"  Конец: {result.get('end_time')}")
        print(f"  Услуги: {result.get('services')}")
        print(f"  Confidence: {result.get('confidence')}")
        
        if result.get('missing_fields'):
            print(f"  ⚠️ Пропущено: {result.get('missing_fields')}")
        
        if result.get('error'):
            print(f"  ❌ Ошибка: {result.get('error')}")
        
        # Решение: парсится или нет?
        if result.get('confidence', 0) >= 0.4 and result.get('start_time') and result.get('end_time'):
            print(f"  ✅ ПАРСИТСЯ")
        else:
            print(f"  ❌ НЕ ПАРСИТСЯ")
        
        print()

asyncio.run(test())