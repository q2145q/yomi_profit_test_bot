"""
AI-парсинг сообщений для извлечения данных о смене
Статус: 🚧 В разработке
"""
from openai import AsyncOpenAI
from config import OPENAI_API_KEY
import json
from datetime import datetime

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

def find_matching_services(text: str, available_services: list) -> list:
    """
    Умный поиск услуг в тексте
    Ищет как полные, так и частичные совпадения
    
    Args:
        text: Текст для поиска
        available_services: Список доступных услуг
    
    Returns:
        Список найденных услуг
    """
    text_lower = text.lower()
    found_services = []
    
    for service in available_services:
        service_lower = service.lower()
        
        # Точное совпадение
        if service_lower in text_lower:
            found_services.append(service)
        # Частичное совпадение (каждое слово)
        else:
            words = service_lower.split()
            if any(word in text_lower for word in words if len(word) > 3):
                found_services.append(service)
    
    return found_services

async def parse_shift_message(
    message: str,
    current_date: str,
    current_time: str,
    base_hours: int = 12,
    services: list = None
) -> dict:
    """
    Парсинг сообщения о смене с помощью AI
    
    Args:
        message: Сообщение пользователя
        current_date: Текущая дата (YYYY-MM-DD)
        current_time: Текущее время (HH:MM)
        base_hours: Базовое количество часов
        services: Список доступных услуг
    
    Returns:
        dict с полями: date, start_time, end_time, services, confidence, missing_fields
    """
    if services is None:
        services = []
    
    # Формируем промпт для OpenAI
    prompt = f"""Ты — парсер сообщений для учёта рабочих смен. Люди пишут в вольной форме.

Контекст:
- Текущая дата: {current_date}
- Текущее время: {current_time}
- Базовое количество часов: {base_hours}
- Доступные услуги: {json.dumps(services, ensure_ascii=False)}

Сообщение пользователя:
"{message}"

Верни JSON в следующем формате:
{{
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "services": ["service_name_1", "service_name_2"],
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

3. УСЛУГИ (ищи гибко):
   - Ищи ЧАСТИЧНЫЕ совпадения с доступными услугами
   - "текущий" может означать "текущий обед" из списка
   - "обед" может означать любой вариант с "обед"
   - Если не нашел точное совпадение - попробуй частичное

4. ЛОГИКА ВРЕМЕНИ:
   - Если смена "сегодня" ({current_date}) и end_time > {current_time} → ОШИБКА
   - В таком случае добавь "end_time" в missing_fields

5. СТРОГОСТЬ (но не слишком):
   - Если указано ЛЮБОЕ время - парси его, не бойся
   - missing_fields только если ВООБЩЕ нет информации о времени
   - "до вечера" без цифр → missing_fields
   - "с 7 до вечера" → start: "07:00", end: missing
   - confidence снижай только если реально не понятно (< 0.4)

ПРИМЕРЫ УСПЕШНОГО ПАРСИНГА:
- "Вчера с 7 до 23" → date: вчера, start: "07:00", end: "23:00", confidence: 0.95
- "Поза с 5 утра до 22" → date: позавчера, start: "05:00", end: "22:00", confidence: 0.95
- "с 9 до 18 + текущий" → start: "09:00", end: "18:00", services: ["текущий обед"], confidence: 0.9
- "работал до 20" → end: "20:00", start: missing_fields, confidence: 0.6

Верни ТОЛЬКО JSON, без дополнительного текста."""
    
    try:
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
        
        # Дополнительная проверка услуг - если AI не нашел, ищем сами
        if not result.get("services") and services:
            found_services = find_matching_services(message, services)
            if found_services:
                result["services"] = found_services
        
        # Дополнительная проверка логики времени
        if result.get("date") == current_date and result.get("end_time"):
            # Сравниваем время окончания с текущим временем
            end_time_obj = datetime.strptime(result["end_time"], "%H:%M").time()
            current_time_obj = datetime.strptime(current_time, "%H:%M").time()
            
            if end_time_obj > current_time_obj:
                # Смена заканчивается в будущем - это ошибка!
                result["confidence"] = 0.3
                if "end_time" not in result.get("missing_fields", []):
                    result.setdefault("missing_fields", []).append("end_time")
                result["error"] = "Смена не может закончиться в будущем"
        
        # Если confidence слишком низкий - очищаем сомнительные данные
        if result.get("confidence", 0) < 0.4:
            if result.get("start_time") and "start_time" in result.get("missing_fields", []):
                result["start_time"] = None
            if result.get("end_time") and "end_time" in result.get("missing_fields", []):
                result["end_time"] = None
        
        return result
        
    except Exception as e:
        # В случае ошибки возвращаем структуру с ошибкой
        return {
            "date": current_date,
            "start_time": None,
            "end_time": None,
            "services": [],
            "confidence": 0.0,
            "missing_fields": ["start_time", "end_time"],
            "error": str(e)
        }