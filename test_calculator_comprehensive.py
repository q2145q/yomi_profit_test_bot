"""
Комплексный тест калькулятора заработка
Проверяет расчёт с обедами, прогрессивными ставками и услугами
"""
import asyncio
from database import (
    init_db, create_user, create_project, create_profession,
    add_progressive_rate, add_additional_service, add_meal_type,
    create_shift
)
from calculator import calculate_shift_earnings
import json
from datetime import datetime, timedelta

async def test():
    print("🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ КАЛЬКУЛЯТОРА\n")
    print("=" * 70)
    
    # 1. Инициализация
    print("\n1. Инициализация БД...")
    await init_db()
    
    user_id = 999999
    await create_user(user_id, "test_calc")
    print("   ✅ Пользователь создан")
    
    project_id = await create_project(user_id, "Тест калькулятора", "")
    print(f"   ✅ Проект создан (ID: {project_id})")
    
    # 2. Создаём профессию
    print("\n2. Создаём профессию...")
    profession_id = await create_profession(
        project_id=project_id,
        position="Тестовый оператор",
        base_rate_net=10000,        # 10,000₽ чистыми
        tax_percentage=13,           # 13% налог
        base_overtime_rate=500,      # 500₽/ч для обедов и базовой переработки
        daily_allowance=1000,
        base_shift_hours=12,
        break_hours=12,
        overtime_rounding=0.5,       # По полчаса
        overtime_threshold=0.25      # Первые 15 минут не считаются
    )
    print(f"   ✅ Профессия создана (ID: {profession_id})")
    print(f"   • Базовая ставка: 10,000₽ (нетто)")
    print(f"   • Базовая переработка: 500₽/ч")
    print(f"   • Порог: 15 минут (0.25ч)")
    print(f"   • Округление: по 0.5ч")
    
    # 3. Прогрессивные ставки
    print("\n3. Добавляем прогрессивные ставки...")
    await add_progressive_rate(profession_id, 0, 2, 500, 1)    # 0-2ч: 500₽
    await add_progressive_rate(profession_id, 2, 4, 600, 2)    # 2-4ч: 600₽
    await add_progressive_rate(profession_id, 4, None, 700, 3) # 4+ч: 700₽
    print("   ✅ Ставки: 0-2ч (500₽), 2-4ч (600₽), 4+ч (700₽)")
    
    # 4. Типы обедов
    print("\n4. Добавляем типы обедов...")
    await add_meal_type(profession_id, "текущий обед", 1.0, '["текущий обед", "текущий"]')
    await add_meal_type(profession_id, "поздний обед", 1.0, '["поздний обед", "поздний"]')
    print("   ✅ Обеды: текущий (+1ч), поздний (+1ч)")
    print("   ℹ️ Обеды оплачиваются по БАЗОВОЙ ставке переработки (500₽/ч)")
    
    # 5. Услуги
    print("\n5. Добавляем услуги...")
    await add_additional_service(profession_id, "ронин", 3000, 'on_mention', 15)
    print("   ✅ Услуга: ронин (3,000₽, налог 15%)")
    
    # === ТЕСТОВЫЕ СЦЕНАРИИ ===
    
    # Используем ВЧЕРАШНЮЮ дату чтобы смены были завершены
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"\n⏰ Используем дату: {yesterday} (вчера)")
    
    test_cases = [
        {
            "name": "Базовая смена 12ч (без переработки)",
            "hours": 12,
            "start": "07:00",
            "end": "19:00",
            "meals": [],
            "services": [],
            "explanation": "12 базовых часов, переработки нет",
            "expected": {
                "base_net": 10000,
                "overtime_net": 0,
                "meals_net": 0,
                "services_net": 0,
                "total_net": 10000
            }
        },
        {
            "name": "Смена 14ч (2ч переработки после округления)",
            "hours": 14,
            "start": "07:00",
            "end": "21:00",
            "meals": [],
            "services": [],
            "explanation": "14-12=2ч, минус порог 0.25ч = 1.75ч, округление до 2ч. Ставка 0-2ч: 2ч × 500₽ = 1,000₽",
            "expected": {
                "base_net": 10000,
                "overtime_net": 1000,
                "meals_net": 0,
                "services_net": 0,
                "total_net": 11000
            }
        },
        {
            "name": "Смена 16ч + текущий обед",
            "hours": 16,
            "start": "07:00",
            "end": "23:00",
            "meals": ["текущий обед"],
            "services": [],
            "explanation": "16-12=4ч, минус порог = 3.75ч, округление до 4ч. Переработка: 0-2ч (2×500=1000) + 2-4ч (2×600=1200) = 2,200₽. Обед: 1ч × 500₽ = 500₽",
            "expected": {
                "base_net": 10000,
                "overtime_net": 2200,  # 2ч*500 + 2ч*600
                "meals_net": 500,
                "services_net": 0,
                "total_net": 12700
            }
        },
        {
            "name": "Смена 18ч (6ч переработки) + 2 обеда",
            "hours": 18,
            "start": "06:00",
            "end": "00:00",  # До полуночи
            "meals": ["текущий обед", "поздний обед"],
            "services": [],
            "explanation": "18-12=6ч, после порога и округления = 6ч. Переработка: 0-2ч (1000) + 2-4ч (1200) + 4-6ч (2×700=1400) = 3,600₽. Обеды: 2ч × 500₽ = 1,000₽",
            "expected": {
                "base_net": 10000,
                "overtime_net": 3600,  # 2*500 + 2*600 + 2*700
                "meals_net": 1000,
                "services_net": 0,
                "total_net": 14600
            }
        },
        {
            "name": "Смена 16ч + текущий обед + ронин",
            "hours": 16,
            "start": "08:00",
            "end": "00:00",
            "meals": ["текущий обед"],
            "services": ["ронин"],
            "explanation": "16-12=4ч переработки (2,200₽). Обед: 500₽. Ронин: 3,000₽",
            "expected": {
                "base_net": 10000,
                "overtime_net": 2200,
                "meals_net": 500,
                "services_net": 3000,
                "total_net": 15700
            }
        }
    ]
    
    print("\n" + "=" * 70)
    print("ЗАПУСК ТЕСТОВЫХ СЦЕНАРИЕВ")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Тест {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 70)
        print(f"  📝 Логика: {test_case['explanation']}")
        print(f"  ⏰ Время: {test_case['start']} - {test_case['end']} ({test_case['hours']}ч)")
        
        if test_case['meals']:
            print(f"  🍽 Обеды: {', '.join(test_case['meals'])}")
        if test_case['services']:
            print(f"  ✅ Услуги: {', '.join(test_case['services'])}")
        
        # Создаём смену
        parsed_data = {
            "date": yesterday,
            "start_time": test_case['start'],
            "end_time": test_case['end'],
            "services": test_case['services'],
            "meals": test_case['meals'],
            "confidence": 0.95
        }
        
        shift_id = await create_shift(
            project_id=project_id,
            date=yesterday,
            start_time=test_case['start'],
            end_time=test_case['end'],
            total_hours=test_case['hours'],
            original_message=f"Тест {i}",
            parsed_data=json.dumps(parsed_data, ensure_ascii=False)
        )
        
        # Рассчитываем
        try:
            details, total_net, total_gross = await calculate_shift_earnings(shift_id, project_id)
        except Exception as e:
            print(f"\n  ❌ ОШИБКА РАСЧЁТА: {e}")
            failed += 1
            continue
        
        # Проверяем результаты
        print(f"\n  💵 РЕЗУЛЬТАТЫ:")
        
        test_passed = True
        expected = test_case['expected']
        
        # 1. Базовая оплата
        actual_base_net = details['breakdown']['base_pay']['net']
        if actual_base_net == expected['base_net']:
            print(f"    ✅ Базовая оплата: {actual_base_net:,}₽")
        else:
            print(f"    ❌ Базовая оплата: ожидали {expected['base_net']:,}₽, получили {actual_base_net:,}₽")
            test_passed = False
        
        # 2. Переработка (с детализацией)
        actual_overtime_net = sum(b['total_net'] for b in details['breakdown']['overtime'])
        # Допускаем погрешность ±100₽ из-за округления брутто→нетто
        if abs(actual_overtime_net - expected['overtime_net']) <= 100:
            print(f"    ✅ Переработка: {actual_overtime_net:,}₽ (ожидали {expected['overtime_net']:,}₽)")
            
            # Детали по прогрессивным ставкам
            if details['breakdown']['overtime']:
                for bracket in details['breakdown']['overtime']:
                    print(f"       • {bracket['bracket']}: {bracket['hours']}ч × {bracket['rate_net']}₽ = {bracket['total_net']:,}₽")
        else:
            print(f"    ❌ Переработка: ожидали {expected['overtime_net']:,}₽, получили {actual_overtime_net:,}₽")
            test_passed = False
        
        # 3. Обеды (с детализацией)
        actual_meals_net = sum(m['total_net'] for m in details['breakdown']['meals'])
        if actual_meals_net == expected['meals_net']:
            print(f"    ✅ Обеды: {actual_meals_net:,}₽")
            
            # Детали по обедам
            if details['breakdown']['meals']:
                for meal in details['breakdown']['meals']:
                    print(f"       • {meal['name']}: {meal['adds_hours']}ч × {meal['rate_net']}₽ = {meal['total_net']:,}₽")
        else:
            print(f"    ❌ Обеды: ожидали {expected['meals_net']:,}₽, получили {actual_meals_net:,}₽")
            test_passed = False
        
        # 4. Услуги
        actual_services_net = sum(s['cost_net'] for s in details['breakdown']['services'])
        if actual_services_net == expected['services_net']:
            print(f"    ✅ Услуги: {actual_services_net:,}₽")
        else:
            print(f"    ❌ Услуги: ожидали {expected['services_net']:,}₽, получили {actual_services_net:,}₽")
            test_passed = False
        
        # 5. Итого (с погрешностью)
        expected_total = expected['total_net']
        if abs(total_net - expected_total) <= 100:
            print(f"\n  💰 ИТОГО: {total_net:,}₽ (нетто) / {total_gross:,}₽ (брутто) ✅")
        else:
            print(f"\n  💰 ИТОГО: {total_net:,}₽ (нетто) / {total_gross:,}₽ (брутто)")
            print(f"     ⚠️ Ожидали: {expected_total:,}₽ (нетто)")
            test_passed = False
        
        if test_passed:
            print(f"\n  ✅ ТЕСТ ПРОЙДЕН")
            passed += 1
        else:
            print(f"\n  ❌ ТЕСТ ПРОВАЛЕН")
            failed += 1
    
    # Общий итог
    print("\n" + "=" * 70)
    print(f"\n📊 ИТОГО:")
    print(f"  ✅ Пройдено: {passed}/{len(test_cases)}")
    print(f"  ❌ Провалено: {failed}/{len(test_cases)}")
    print(f"  📈 Успешность: {passed/len(test_cases)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print(f"\n⚠️ Есть проблемы, нужно исправить {failed} тест(ов)")

if __name__ == "__main__":
    asyncio.run(test())