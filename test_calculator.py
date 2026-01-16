"""
Тест модуля расчёта заработка
"""
import asyncio
from database import (
    init_db, create_user, create_project,
    create_profession, add_progressive_rate, add_additional_service,
    create_shift
)
from calculator import calculate_shift_earnings
from datetime import datetime
import json

async def test():
    print("🧪 Тест расчёта заработка\n")
    
    # 1. Инициализация БД
    print("1. Инициализация БД...")
    await init_db()
    print("   ✅ БД готова\n")
    
    # 2. Создаём пользователя и проект
    user_id = 777777
    await create_user(user_id, "test_calc_user")
    print(f"2. Пользователь {user_id} создан")
    
    project_id = await create_project(
        user_id=user_id,
        name="Тестовый проект для расчёта",
        description="Проверка calculator.py"
    )
    print(f"3. Проект создан с ID: {project_id}\n")
    
    # 4. Создаём профессию
    print("4. Создаём профессию с настройками...")
    profession_id = await create_profession(
        project_id=project_id,
        position="Тестовый оператор",
        base_rate_net=10000,
        tax_percentage=13,
        base_overtime_rate=500,
        daily_allowance=1000,
        base_shift_hours=12,
        overtime_rounding=0.5,    # Округление по 0.5 часа (30 минут)
        overtime_threshold=0.25   # Первые 15 минут не считаются
    )
    print(f"   ✅ Профессия ID: {profession_id}")
    print(f"   • Округление переработки: по 0.5 часа")
    print(f"   • Порог переработки: первые 15 минут не считаются\n")
    
    # 5. Добавляем прогрессивные ставки
    print("5. Добавляем прогрессивные ставки...")
    await add_progressive_rate(profession_id, 0, 2, 500, 1)
    await add_progressive_rate(profession_id, 2, 4, 600, 2)
    await add_progressive_rate(profession_id, 4, None, 700, 3)
    print("   ✅ Ставки: 0-2ч (500₽), 2-4ч (600₽), 4+ч (700₽)\n")
    
    # 6. Добавляем услуги
    print("6. Добавляем услуги (налог 15%)...")
    await add_additional_service(profession_id, "обед", 500, 'on_mention', 15)
    await add_additional_service(profession_id, "ронин", 3000, 'on_mention', 15)
    print("   ✅ Услуги: обед (500₽ нетто, налог 15%), ронин (3,000₽ нетто, налог 15%)\n")
    
    # 7. Создаём тестовую смену (16 часов = 12 базовых + 4 переработки)
    print("7. Создаём смену: 07:00-23:00 (16 часов)...")
    parsed_data = {
        "date": "2026-01-13",
        "start_time": "07:00",
        "end_time": "23:00",
        "services": ["обед", "ронин"],
        "confidence": 0.95
    }
    
    shift_id = await create_shift(
        project_id=project_id,
        date="2026-01-13",
        start_time="07:00",
        end_time="23:00",
        total_hours=16.0,
        original_message="Смена 07:00-23:00 + обед + ронин",
        parsed_data=json.dumps(parsed_data, ensure_ascii=False)
    )
    print(f"   ✅ Смена ID: {shift_id}\n")
    
    # 8. ЗАПУСКАЕМ РАСЧЁТ
    print("8. 💰 Запускаем расчёт заработка...\n")
    print("=" * 60)
    
    details, total_net, total_gross = await calculate_shift_earnings(
        shift_id=shift_id,
        project_id=project_id
    )
    
    # 9. Выводим результаты
    print("\n📊 РЕЗУЛЬТАТЫ РАСЧЁТА:\n")
    
    print(f"⏱ Часов отработано: {details['total_hours']} ч")
    print(f"   • Базовых: {details['base_hours']} ч")
    print(f"   • Переработка: {details['overtime_hours']} ч\n")
    
    print("💵 ДЕТАЛЬНЫЙ РАСЧЁТ:\n")
    
    # Базовая оплата
    print(f"1. Базовая ставка:")
    print(f"   • Нетто: {details['breakdown']['base_pay']['net']:,}₽")
    print(f"   • Брутто: {details['breakdown']['base_pay']['gross']:,}₽\n")
    
    # Переработки
    if details['breakdown']['overtime']:
        print(f"2. Переработка ({details['overtime_hours']} ч):")
        total_overtime_net = 0
        total_overtime_gross = 0
        for bracket in details['breakdown']['overtime']:
            print(f"   • {bracket['bracket']}: {bracket['hours']} ч × {bracket['rate_gross']}₽(брутто)/{bracket['rate_net']}₽(нетто) = {bracket['total_net']:,}₽ (нетто) / {bracket['total_gross']:,}₽ (брутто)")
            total_overtime_net += bracket['total_net']
            total_overtime_gross += bracket['total_gross']
        print(f"   Итого переработка: {total_overtime_net:,}₽ (нетто) / {total_overtime_gross:,}₽ (брутто)\n")
    
    # Суточные
    if details['breakdown']['daily_allowance'] > 0:
        print(f"3. Суточные: {details['breakdown']['daily_allowance']:,}₽\n")
    
    # Услуги
    if details['breakdown']['services']:
        print(f"4. Дополнительные услуги:")
        total_services_net = 0
        total_services_gross = 0
        for service in details['breakdown']['services']:
            print(f"   • {service['name']}: {service['cost_net']:,}₽ (нетто) / {service['cost_gross']:,}₽ (брутто) [налог {service['tax']}%]")
            total_services_net += service['cost_net']
            total_services_gross += service['cost_gross']
        print(f"   Итого услуги: {total_services_net:,}₽ (нетто) / {total_services_gross:,}₽ (брутто)\n")
    
    # Итого
    print("=" * 60)
    print(f"💰 ИТОГО (нетто): {total_net:,}₽")
    print(f"💰 ИТОГО (брутто): {total_gross:,}₽")
    print("=" * 60)
    
    print("\n✅ Тест завершён успешно!")

asyncio.run(test())