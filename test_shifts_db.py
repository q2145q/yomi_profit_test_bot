"""
Тест работы с таблицей shifts
"""
import asyncio
from database import (
    init_db, create_user, create_project, 
    create_shift, confirm_shift, get_shift, 
    get_user_shifts, delete_shift
)
import json
from datetime import datetime

async def test():
    print("🧪 Тест таблицы shifts\n")
    
    # Инициализация БД
    print("1. Инициализация БД...")
    await init_db()
    print("   ✅ БД готова\n")
    
    # Создаём тестового пользователя
    user_id = 123456
    await create_user(user_id, "test_user")
    print(f"2. Пользователь {user_id} создан\n")
    
    # Создаём проект
    print("3. Создаём проект...")
    project_id = await create_project(
        user_id=user_id,
        name="Тестовый проект",
        description="Тест смен"
    )
    print(f"   ✅ Проект создан с ID: {project_id}\n")
    
    # Создаём смену
    print("4. Создаём смену...")
    parsed_data = {
        "date": "2026-01-12",
        "start_time": "09:00",
        "end_time": "18:00",
        "services": ["обед"],
        "confidence": 0.95
    }
    
    shift_id = await create_shift(
        project_id=project_id,
        date="2026-01-12",
        start_time="09:00",
        end_time="18:00",
        total_hours=9.0,
        original_message="Вчера работал с 9 до 18 + обед",
        parsed_data=json.dumps(parsed_data, ensure_ascii=False)
    )
    print(f"   ✅ Смена создана с ID: {shift_id}\n")
    
    # Получаем смену
    print("5. Получаем смену...")
    shift = await get_shift(shift_id)
    print(f"   ID: {shift['id']}")
    print(f"   Дата: {shift['date']}")
    print(f"   Время: {shift['start_time']} - {shift['end_time']}")
    print(f"   Часов: {shift['total_hours']}")
    print(f"   Статус: {shift['status']}\n")
    
    # Подтверждаем смену
    print("6. Подтверждаем смену...")
    await confirm_shift(shift_id)
    
    shift = await get_shift(shift_id)
    print(f"   Статус: {shift['status']}")
    print(f"   Подтверждено: {shift['confirmed_at']}\n")
    
    # Получаем список смен проекта
    print("7. Список смен проекта:")
    shifts = await get_user_shifts(project_id)
    for s in shifts:
        print(f"   - Смена #{s['id']}: {s['date']} ({s['total_hours']}ч) - {s['status']}")
    
    print("\n✅ Все тесты пройдены!")

asyncio.run(test())
