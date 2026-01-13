"""
AI-парсинг сообщений для извлечения данных о смене
Статус: 🚧 В разработке
"""
from openai import AsyncOpenAI
from config import OPENAI_API_KEY
import json
from datetime import datetime

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

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
    prompt = f"""Ты — парсер сообщений для учёта рабочих смен.

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

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:
1. Если дата не указана - используй текущую дату
2. "вчера" = текущая дата - 1 день
3. "позавчера" = текущая дата - 2 дня
4. Время в формате 24 часа (HH:MM)

5. ЛОГИКА ВРЕМЕНИ:
   - Если смена "сегодня" ({current_date}) и end_time > {current_time} - это ОШИБКА!
   - Смена не может закончиться в будущем!
   - В таком случае добавь "end_time" в missing_fields

6. СТРОГОСТЬ:
   - Если НЕ УВЕРЕН в start_time или end_time - НЕ ПРИДУМЫВАЙ!
   - Лучше добавь поле в missing_fields, чем угадывай
   - Если указано только "до вечера" без точного времени - это missing_fields!
   - confidence ставь 0.3 или ниже, если данных недостаточно

7. Если не можешь определить поле - добавь его в "missing_fields"
8. confidence - твоя уверенность в распознавании (0.0-1.0)

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
        if result.get("confidence", 0) < 0.5:
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
