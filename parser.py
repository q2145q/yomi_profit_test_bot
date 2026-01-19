"""
AI-парсинг сообщений для извлечения данных о смене
Статус: ✅ Шаг 6.1 - Добавлено распознавание обедов отдельно от услуг
"""
from openai import AsyncOpenAI
import json
from datetime import datetime

# Предполагаем, что OPENAI_API_KEY есть в окружении или в config
try:
    from config import OPENAI_API_KEY
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
except:
    # Для теста используем заглушку
    client = None

def find_matching_services(text: str, available_services: list) -> list:
    """
    Умный поиск УСЛУГ в тексте (БЕЗ обедов!)
    Ищет как полные, так и частичные совпадения
    
    Args:
        text: Текст для поиска
        available_services: Список доступных услуг
    
    Returns:
        Список найденных услуг
    """
    text_lower = text.lower()
    found_services = []
    
    # Исключаем слова, связанные с обедами
    meal_keywords = ['обед', 'текущий', 'поздний']
    
    for service in available_services:
        service_lower = service.lower()
        
        # Пропускаем, если это обед
        if any(keyword in service_lower for keyword in meal_keywords):
            continue
        
        # Точное совпадение
        if service_lower in text_lower:
            found_services.append(service)
        # Частичное совпадение (каждое слово)
        else:
            words = service_lower.split()
            if any(word in text_lower for word in words if len(word) > 3):
                found_services.append(service)
    
    return found_services

def find_matching_meals(text: str, available_meals: list) -> list:
    """
    Умный поиск ОБЕДОВ в тексте
    
    Args:
        text: Текст для поиска
        available_meals: Список доступных типов обедов
    
    Returns:
        Список найденных обедов
    """
    text_lower = text.lower()
    found_meals = []
    
    for meal in available_meals:
        meal_lower = meal.lower()
        
        # Точное совпадение
        if meal_lower in text_lower:
            found_meals.append(meal)
        # Частичное совпадение (каждое слово)
        else:
            words = meal_lower.split()
            if any(word in text_lower for word in words if len(word) > 3):
                found_meals.append(meal)
    
    return found_meals

async def parse_shift_message(
    message: str,
    current_date: str,
    current_time: str,
    base_hours: int = 12,
    services: list = None,
    meals: list = None  # НОВЫЙ ПАРАМЕТР!
) -> dict:
    """
    Парсинг сообщения о смене с помощью AI
    
    Args:
        message: Сообщение пользователя
        current_date: Текущая дата (YYYY-MM-DD)
        current_time: Текущее время (HH:MM)
        base_hours: Базовое количество часов
        services: Список доступных УСЛУГ (без обедов!)
        meals: Список доступных ТИПОВ ОБЕДОВ
    
    Returns:
        dict с полями: date, start_time, end_time, services, meals, confidence, missing_fields
    """
    if services is None:
        services = []
    
    if meals is None:
        meals = []
    
    # Формируем промпт для OpenAI
    prompt = f"""Ты — парсер сообщений для учёта рабочих смен. Люди пишут в вольной форме.

Контекст:
- Текущая дата: {current_date}
- Текущее время: {current_time}
- Базовое количество часов: {base_hours}
- Доступные УСЛУГИ: {json.dumps(services, ensure_ascii=False)}
- Доступные ТИПЫ ОБЕДОВ: {json.dumps(meals, ensure_ascii=False)}

Сообщение пользователя:
"{message}"

Верни JSON в следующем формате:
{{
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "services": ["service_name_1", "service_name_2"],
  "meals": ["текущий обед", "поздний обед"],
  "confidence": 0.95,
  "missing_fields": []
}}

ПРАВИЛА ПАРСИНГА:

1. ДАТА (будь гибким):
   - Не указана → текущая дата
   - "вчера" → текущая дата - 1 день
   - "позавчера", "поза", "позо" → текущая дата - 2 дня
   - "11.01" или "11 января" → конкретная дата

2. ВРЕМЯ (понимай разные форматы):
   - "7" → "07:00"
   - "23" → "23:00"
   - "5 утра" → "05:00"
   - "10 вечера" → "22:00"
   - "с 7 до 23" → start: "07:00", end: "23:00"
   - ЕСЛИ указано хоть какое-то время (даже "7" или "утра") - ОБЯЗАТЕЛЬНО распознай!

3. ОБЕДЫ (НОВОЕ - распознавай отдельно от услуг!):
   - Ищи упоминания типов обедов из списка доступных
   - "текущий обед", "текущий", "обед" → добавь в массив meals
   - "поздний обед", "поздний" → добавь в массив meals
   - ВАЖНО: обеды НЕ добавляй в services, только в meals!

4. УСЛУГИ (ищи гибко, БЕЗ обедов):
   - Ищи ЧАСТИЧНЫЕ совпадения с доступными услугами
   - НЕ путай обеды и услуги - обеды только в meals!
   - Если не нашел точное совпадение - попробуй частичное

5. СТРОГОСТЬ (но не слишком):
   - Если указано ЛЮБОЕ время - парси его, не бойся
   - missing_fields только если ВООБЩЕ нет информации о времени
   - "до вечера" без цифр → missing_fields
   - "с 7 до вечера" → start: "07:00", end: missing
   - confidence снижай только если реально не понятно (< 0.4)

ПРИМЕРЫ УСПЕШНОГО ПАРСИНГА:
- "Вчера с 7 до 23" → date: вчера, start: "07:00", end: "23:00", confidence: 0.95
- "Поза с 5 утра до 22 + текущий" → date: позавчера, start: "05:00", end: "22:00", meals: ["текущий обед"], confidence: 0.95
- "с 9 до 18 + текущий + ронин" → start: "09:00", end: "18:00", meals: ["текущий обед"], services: ["ронин"], confidence: 0.9
- "работал до 20 с обедом" → end: "20:00", meals: ["обед"], start: missing_fields, confidence: 0.6

Верни ТОЛЬКО JSON, без дополнительного текста."""
    
    try:
        # Если клиента нет (тестовый режим) - возвращаем заглушку
        if client is None:
            return {
                "date": current_date,
                "start_time": "07:00",
                "end_time": "19:00",
                "services": [],
                "meals": ["текущий обед"],
                "confidence": 0.95,
                "missing_fields": []
            }
        
        # Отправляем запрос в OpenAI
        response = await client.chat.completions.create(
            model="gpt-4.1-nano",  # Используем более дешевую модель
            messages=[
                {"role": "system", "content": "Ты — точный парсер данных. Отвечай только валидным JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Низкая температура для точности
            max_tokens=300
        )
        
        # Извлекаем JSON из ответа
        content = response.choices[0].message.content.strip()
        
        # Убираем markdown если есть
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        # Парсим JSON
        result = json.loads(content)
        
        # Дополнительная проверка услуг - если AI не нашел, ищем сами (БЕЗ обедов!)
        if not result.get("services") and services:
            found_services = find_matching_services(message, services)
            if found_services:
                result["services"] = found_services
        
        # Дополнительная проверка обедов - если AI не нашел, ищем сами
        if not result.get("meals") and meals:
            found_meals = find_matching_meals(message, meals)
            if found_meals:
                result["meals"] = found_meals
        
        # Если поле meals отсутствует - добавляем пустой массив
        if "meals" not in result:
            result["meals"] = []
        
        return result
        
    except Exception as e:
        # В случае ошибки возвращаем структуру с ошибкой
        return {
            "date": current_date,
            "start_time": None,
            "end_time": None,
            "services": [],
            "meals": [],  # НОВОЕ ПОЛЕ!
            "confidence": 0.0,
            "missing_fields": ["start_time", "end_time"],
            "error": str(e)
        }