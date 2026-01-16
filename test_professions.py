"""
Тест работы с профессиями и настройками
"""
import asyncio
from database import (
    init_db, create_user, create_project,
    create_profession, get_profession_by_project,
    add_progressive_rate, get_progressive_rates,
    add_additional_service, get_additional_services
)

async def test():
    print("🧪 Тест таблиц профессий\n")
    
    # 1. Инициализация БД
    print("1. Инициализация БД...")
    await init_db()
    print("   ✅ БД готова\n")
    
    # 2. Создаём пользователя и проект
    user_id = 999999
    await create_user(user_id, "test_profession_user")
    print(f"2. Пользователь {user_id} создан")
    
    project_id = await create_project(
        user_id=user_id,
        name="Тестовый фильм для профессий",
        description="Проект для теста настроек"
    )
    print(f"3. Проект создан с ID: {project_id}\n")
    
    # 4. Создаём профессию
    print("4. Создаём профессию...")
    profession_id = await create_profession(
        project_id=project_id,
        position="Оператор камеры",
        base_rate_net=10000,      # 10,000₽ нетто
        tax_percentage=13,         # 13% налог
        base_overtime_rate=500,    # 500₽/ч базовая переработка
        daily_allowance=1000,      # 1,000₽ суточные
        base_shift_hours=12,       # 12 часов базовая смена
        break_hours=12,            # 12 часов разрыв между сменами
        payment_schedule='monthly',
        conditions='7-й день подряд × 2'
    )
    print(f"   ✅ Профессия создана с ID: {profession_id}\n")
    
    # 5. Получаем профессию
    print("5. Получаем профессию из БД...")
    profession = await get_profession_by_project(project_id)
    print(f"   Должность: {profession['position']}")
    print(f"   Базовая ставка (нетто): {profession['base_rate_net']:,}₽")
    print(f"   Базовая ставка (брутто): {profession['base_rate_gross']:,}₽")
    print(f"   Переработка: {profession['base_overtime_rate']}₽/ч")
    print(f"   Суточные: {profession['daily_allowance']:,}₽")
    print(f"   Базовые часы: {profession['base_shift_hours']}ч")
    print(f"   Налог: {profession['tax_percentage']}%\n")
    
    # 6. Добавляем прогрессивные ставки
    print("6. Добавляем прогрессивные ставки переработки...")
    await add_progressive_rate(profession_id, 0, 2, 500, 1)    # 0-2ч: 500₽/ч
    await add_progressive_rate(profession_id, 2, 4, 600, 2)    # 2-4ч: 600₽/ч
    await add_progressive_rate(profession_id, 4, None, 700, 3) # 4+ч: 700₽/ч
    print("   ✅ Добавлено 3 диапазона ставок\n")
    
    # 7. Получаем прогрессивные ставки
    print("7. Прогрессивные ставки из БД:")
    rates = await get_progressive_rates(profession_id)
    for rate in rates:
        hours_to = f"{rate['hours_to']}" if rate['hours_to'] else "+"
        print(f"   {rate['hours_from']}-{hours_to}ч: {rate['rate']}₽/ч")
    print()
    
    # 8. Добавляем дополнительные услуги
    print("8. Добавляем дополнительные услуги...")
    await add_additional_service(
        profession_id=profession_id,
        name="обед",
        cost=500,
        application_rule='on_mention',
        keywords='["обед", "текущий обед"]'
    )
    await add_additional_service(
        profession_id=profession_id,
        name="ронин",
        cost=3000,
        application_rule='on_mention',
        keywords='["ронин"]'
    )
    print("   ✅ Добавлено 2 услуги\n")
    
    # 9. Получаем услуги
    print("9. Дополнительные услуги из БД:")
    services = await get_additional_services(profession_id)
    for service in services:
        print(f"   • {service['name']}: {service['cost']:,}₽ ({service['application_rule']})")
    
    print("\n✅ Все тесты пройдены!")

asyncio.run(test())