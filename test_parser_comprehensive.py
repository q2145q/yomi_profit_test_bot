"""
Комплексный тест парсера смен
Проверяет все сценарии из реального использования
"""
import asyncio
from parser import parse_shift_message
from datetime import datetime, timedelta
import json

# Вычисляем даты
today = datetime.now()
yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
day_before_yesterday = (today - timedelta(days=2)).strftime("%Y-%m-%d")
CURRENT_DATE = today.strftime("%Y-%m-%d")
CURRENT_TIME = today.strftime("%H:%M")

# Тестовые данные
BASE_HOURS = 12
SERVICES = ["ронин"]
MEALS = ["обед", "текущий обед", "поздний обед"]

# Тестовые сценарии
TEST_CASES = [
    {
        "name": "Вчерашняя смена",
        "message": "Вчера с 07:00 до 19:00",
        "expected": {
            "date": yesterday,
            "start_time": "07:00",
            "end_time": "19:00",
            "services": [],
            "meals": [],
            "confidence_min": 0.8
        }
    },
    {
        "name": "Вчера с текущим обедом",
        "message": "Вчера 07:00 до 23:00 + текущий обед",
        "expected": {
            "date": yesterday,
            "start_time": "07:00",
            "end_time": "23:00",
            "services": [],
            "meals": ["текущий обед"],
            "confidence_min": 0.8
        }
    },
    {
        "name": "Вчера с обедом и услугой",
        "message": "вчера с 9 до 18 + текущий + ронин",
        "expected": {
            "date": yesterday,
            "start_time": "09:00",
            "end_time": "18:00",
            "services": ["ронин"],
            "meals": ["текущий обед"],
            "confidence_min": 0.7
        }
    },
    {
        "name": "Позавчера",
        "message": "Позавчера с 7 до 23",
        "expected": {
            "date": day_before_yesterday,
            "start_time": "07:00",
            "end_time": "23:00",
            "services": [],
            "meals": [],
            "confidence_min": 0.8
        }
    },
    {
        "name": "Позавчера (сокращённо)",
        "message": "Поза вчера с 5 утра до 22",
        "expected": {
            "date": day_before_yesterday,
            "start_time": "05:00",
            "end_time": "22:00",
            "services": [],
            "meals": [],
            "confidence_min": 0.7
        }
    },
    {
        "name": "Вчера с поздним обедом",
        "message": "Вчера работал с 7 до 20 с поздним обедом",
        "expected": {
            "date": yesterday,
            "start_time": "07:00",
            "end_time": "20:00",
            "services": [],
            "meals": ["поздний обед"],
            "confidence_min": 0.7
        }
    },
    {
        "name": "Вчера с двумя обедами",
        "message": "Вчера смена 6-22 текущий обед + поздний",
        "expected": {
            "date": yesterday,
            "start_time": "06:00",
            "end_time": "22:00",
            "services": [],
            "meals": ["текущий обед", "поздний обед"],
            "confidence_min": 0.7
        }
    },
    {
        "name": "Только обед (должен быть в meals)",
        "message": "вчера с 7 до 19 + обед",
        "expected": {
            "date": yesterday,
            "start_time": "07:00",
            "end_time": "19:00",
            "services": [],
            "meals": ["обед"],
            "confidence_min": 0.7
        }
    }
]

async def run_tests():
    """Запуск всех тестов"""
    print("🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ПАРСЕРА\n")
    print("=" * 70)
    print(f"📅 Сегодня: {CURRENT_DATE} ({CURRENT_TIME})")
    print(f"📅 Вчера: {yesterday}")
    print(f"📅 Позавчера: {day_before_yesterday}")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\nТест {i}/{len(TEST_CASES)}: {test_case['name']}")
        print(f"Сообщение: \"{test_case['message']}\"")
        print("-" * 70)
        
        # Парсим
        result = await parse_shift_message(
            message=test_case['message'],
            current_date=CURRENT_DATE,
            current_time=CURRENT_TIME,
            base_hours=BASE_HOURS,
            services=SERVICES,
            meals=MEALS
        )
        
        # === ОТЛАДКА: Показываем ошибку если есть ===
        if result.get('error'):
            print(f"  ⚠️ ОШИБКА API: {result['error']}")
            print(f"  📊 Весь результат: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # Проверяем результат
        expected = test_case['expected']
        test_passed = True
        errors = []
        
        # Проверка даты
        if result.get('date') != expected['date']:
            test_passed = False
            errors.append(f"  ❌ Дата: ожидали {expected['date']}, получили {result.get('date')}")
        else:
            print(f"  ✅ Дата: {result.get('date')}")
        
        # Проверка времени начала
        if result.get('start_time') != expected['start_time']:
            test_passed = False
            errors.append(f"  ❌ Начало: ожидали {expected['start_time']}, получили {result.get('start_time')}")
        else:
            print(f"  ✅ Начало: {result.get('start_time')}")
        
        # Проверка времени окончания
        if result.get('end_time') != expected['end_time']:
            test_passed = False
            errors.append(f"  ❌ Конец: ожидали {expected['end_time']}, получили {result.get('end_time')}")
        else:
            print(f"  ✅ Конец: {result.get('end_time')}")
        
        # Проверка услуг
        result_services = result.get('services', [])
        if set(result_services) != set(expected['services']):
            test_passed = False
            errors.append(f"  ❌ Услуги: ожидали {expected['services']}, получили {result_services}")
        else:
            print(f"  ✅ Услуги: {result_services}")
        
        # Проверка обедов (ВАЖНО!)
        result_meals = result.get('meals', [])
        # Гибкая проверка - достаточно частичного совпадения
        if expected['meals']:
            meals_match = all(
                any(exp_meal.lower() in res_meal.lower() or res_meal.lower() in exp_meal.lower() 
                    for res_meal in result_meals) 
                for exp_meal in expected['meals']
            )
        else:
            meals_match = len(result_meals) == 0
        
        if not meals_match:
            test_passed = False
            errors.append(f"  ❌ Обеды: ожидали {expected['meals']}, получили {result_meals}")
        else:
            print(f"  ✅ Обеды: {result_meals}")
        
        # Проверка уверенности
        confidence = result.get('confidence', 0)
        if confidence < expected['confidence_min']:
            test_passed = False
            errors.append(f"  ❌ Confidence: {confidence} < {expected['confidence_min']}")
        else:
            print(f"  ✅ Confidence: {confidence}")
        
        # Итог теста
        if test_passed:
            print(f"\n✅ ТЕСТ ПРОЙДЕН")
            passed += 1
        else:
            print(f"\n❌ ТЕСТ ПРОВАЛЕН:")
            for error in errors:
                print(error)
            failed += 1
    
    # Общий итог
    print("\n" + "=" * 70)
    print(f"\n📊 ИТОГО:")
    print(f"  ✅ Пройдено: {passed}/{len(TEST_CASES)}")
    print(f"  ❌ Провалено: {failed}/{len(TEST_CASES)}")
    print(f"  📈 Успешность: {passed/len(TEST_CASES)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print(f"\n⚠️ Есть проблемы, нужно исправить {failed} тест(ов)")

if __name__ == "__main__":
    asyncio.run(run_tests())