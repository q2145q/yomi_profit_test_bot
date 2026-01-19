"""
Расчёт заработка по смене
Статус: ✅ Шаг 6.1 - Обеды добавляют +1 час БАЗОВОЙ переработки
"""
from database import (
    get_profession_by_project, 
    get_progressive_rates, 
    get_additional_services,
    get_meal_types,
    get_shift_meals
)
import aiosqlite
from config import DATABASE_PATH
import json

async def calculate_shift_earnings(shift_id: int, project_id: int):
    """
    Расчёт заработка по смене
    
    Args:
        shift_id: ID смены
        project_id: ID проекта
    
    Returns:
        tuple: (calculation_details, total_net, total_gross)
    """
    # 1. Получаем данные смены
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM shifts WHERE id = ?",
            (shift_id,)
        ) as cursor:
            shift = await cursor.fetchone()
    
    if shift is None:
        raise ValueError(f"Смена с ID {shift_id} не найдена")
    
    # 2. Получаем настройки профессии
    profession = await get_profession_by_project(project_id)
    
    if profession is None:
        raise ValueError("Профессия не настроена для проекта")
    
    total_hours = shift["total_hours"]
    base_hours = profession["base_shift_hours"]
    tax_percentage = profession["tax_percentage"]
    
    # 3. Базовая оплата
    base_pay_net = profession["base_rate_net"]
    base_pay_gross = profession["base_rate_gross"]
    
    # === 4. НОВАЯ ЛОГИКА: ОБЕДЫ (считаем отдельно!) ===
    
    meal_hours = 0
    meal_pay_net = 0
    meal_pay_gross = 0
    meal_breakdown = []
    
    # Получаем обеды смены из БД
    shift_meals_from_db = await get_shift_meals(shift_id)
    
    if shift_meals_from_db:
        for meal in shift_meals_from_db:
            meal_hours += meal["adds_overtime_hours"]
            
            # ВАЖНО: Обеды оплачиваются по БАЗОВОЙ ставке переработки!
            meal_hour_net = profession["base_overtime_rate"]
            meal_hour_gross = round(meal_hour_net / (1 - tax_percentage / 100))
            
            meal_pay_net += int(meal["adds_overtime_hours"] * meal_hour_net)
            meal_pay_gross += int(meal["adds_overtime_hours"] * meal_hour_gross)
            
            meal_breakdown.append({
                "name": meal["name"],
                "adds_hours": meal["adds_overtime_hours"],
                "rate_net": meal_hour_net,
                "rate_gross": meal_hour_gross,
                "total_net": int(meal["adds_overtime_hours"] * meal_hour_net),
                "total_gross": int(meal["adds_overtime_hours"] * meal_hour_gross)
            })
    
    # Альтернативно: если обеды ещё не сохранены, получаем из parsed_data
    if not shift_meals_from_db and shift["parsed_data"]:
        try:
            parsed_data = json.loads(shift["parsed_data"])
            mentioned_meals = parsed_data.get("meals", [])
            
            if mentioned_meals:
                meal_types = await get_meal_types(profession["id"])
                
                for mentioned_meal in mentioned_meals:
                    for meal_type in meal_types:
                        meal_name_lower = meal_type["name"].lower()
                        
                        if (meal_name_lower in mentioned_meal.lower() or 
                            mentioned_meal.lower() in meal_name_lower):
                            
                            meal_hours += meal_type["adds_overtime_hours"]
                            
                            # БАЗОВАЯ ставка для обедов
                            meal_hour_net = profession["base_overtime_rate"]
                            meal_hour_gross = round(meal_hour_net / (1 - tax_percentage / 100))
                            
                            meal_pay_net += int(meal_type["adds_overtime_hours"] * meal_hour_net)
                            meal_pay_gross += int(meal_type["adds_overtime_hours"] * meal_hour_gross)
                            
                            meal_breakdown.append({
                                "name": meal_type["name"],
                                "adds_hours": meal_type["adds_overtime_hours"],
                                "rate_net": meal_hour_net,
                                "rate_gross": meal_hour_gross,
                                "total_net": int(meal_type["adds_overtime_hours"] * meal_hour_net),
                                "total_gross": int(meal_type["adds_overtime_hours"] * meal_hour_gross)
                            })
                            break
        except json.JSONDecodeError:
            pass
    
    # === 5. ПЕРЕРАБОТКИ (БЕЗ обедов - только фактические часы работы) ===
    
    base_overtime_hours = 0
    overtime_pay_net = 0
    overtime_pay_gross = 0
    overtime_breakdown = []
    
    # Рассчитываем базовые часы переработки (БЕЗ обедов!)
    if total_hours > base_hours:
        overtime_hours_raw = total_hours - base_hours
        
        # Применяем порог
        overtime_threshold = profession["overtime_threshold"]
        if overtime_hours_raw < overtime_threshold:
            base_overtime_hours = 0
        else:
            base_overtime_hours = overtime_hours_raw - overtime_threshold
            
            # Применяем округление
            overtime_rounding = profession["overtime_rounding"]
            if overtime_rounding > 0:
                import math
                base_overtime_hours = math.ceil(base_overtime_hours / overtime_rounding) * overtime_rounding
    
    # ВАЖНО: Обеды НЕ попадают в прогрессивные ставки!
    # Прогрессивные ставки только для фактических часов переработки
    
    # Получаем прогрессивные ставки
    rates = await get_progressive_rates(profession["id"])
    
    if rates and base_overtime_hours > 0:
        # Применяем прогрессивные ставки ТОЛЬКО к фактической переработке
        remaining_hours = base_overtime_hours
        
        for rate in rates:
            if remaining_hours <= 0:
                break
            
            hours_to = rate["hours_to"] if rate["hours_to"] else 999
            bracket_size = hours_to - rate["hours_from"]
            hours_in_bracket = min(remaining_hours, bracket_size)
            
            rate_net = rate["rate"]
            rate_gross = round(rate_net / (1 - tax_percentage / 100))
            
            bracket_pay_gross = round(hours_in_bracket * rate_gross)
            bracket_pay_net = round(bracket_pay_gross * (1 - tax_percentage / 100))
            
            overtime_pay_net += bracket_pay_net
            overtime_pay_gross += bracket_pay_gross
            
            bracket_label = f"{rate['hours_from']:.0f}-{rate['hours_to'] if rate['hours_to'] else '+'}ч"
            overtime_breakdown.append({
                "bracket": bracket_label,
                "hours": round(hours_in_bracket, 2),
                "rate_net": rate_net,
                "rate_gross": rate_gross,
                "total_net": bracket_pay_net,
                "total_gross": bracket_pay_gross
            })
            
            remaining_hours -= hours_in_bracket
    elif base_overtime_hours > 0:
        # Если нет прогрессивных ставок - используем базовую
        overtime_pay_net = int(base_overtime_hours * profession["base_overtime_rate"])
        overtime_pay_gross = round(overtime_pay_net / (1 - tax_percentage / 100))
        
        overtime_breakdown.append({
            "bracket": "базовая",
            "hours": round(base_overtime_hours, 2),
            "rate_net": profession["base_overtime_rate"],
            "rate_gross": round(profession["base_overtime_rate"] / (1 - tax_percentage / 100)),
            "total_net": overtime_pay_net,
            "total_gross": overtime_pay_gross
        })
    
    # ИТОГО часов переработки (для отображения)
    total_overtime_hours = base_overtime_hours + meal_hours
    
    # Обновляем overtime_hours в смене
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE shifts SET overtime_hours = ? WHERE id = ?",
            (total_overtime_hours, shift_id)
        )
        await db.commit()
    
    # 6. Суточные
    daily_allowance_pay = 0
    if shift["is_expense_day"]:
        daily_allowance_pay = profession["daily_allowance"]
    
    # 7. Дополнительные услуги (БЕЗ обедов!)
    services_pay_net = 0
    services_pay_gross = 0
    services_breakdown = []
    
    if shift["parsed_data"]:
        try:
            parsed_data = json.loads(shift["parsed_data"])
            mentioned_services = parsed_data.get("services", [])
            
            if mentioned_services:
                available_services = await get_additional_services(profession["id"])
                
                for service in available_services:
                    service_name_lower = service["name"].lower()
                    
                    is_mentioned = any(
                        service_name_lower in mentioned.lower() or mentioned.lower() in service_name_lower
                        for mentioned in mentioned_services
                    )
                    
                    if is_mentioned:
                        service_net = service["cost"]
                        service_tax = service["tax_percentage"]
                        service_gross = round(service_net / (1 - service_tax / 100))
                        
                        services_pay_net += service_net
                        services_pay_gross += service_gross
                        
                        services_breakdown.append({
                            "name": service["name"],
                            "cost_net": service_net,
                            "cost_gross": service_gross,
                            "tax": service_tax
                        })
        except json.JSONDecodeError:
            pass
    
    # 8. Итого
    total_net = base_pay_net + overtime_pay_net + meal_pay_net + daily_allowance_pay + services_pay_net
    total_gross = base_pay_gross + overtime_pay_gross + meal_pay_gross + daily_allowance_pay + services_pay_gross
    
    # 9. Детали расчёта
    calculation_details = {
        "base_hours": base_hours,
        "total_hours": round(total_hours, 2),
        "base_overtime_hours": round(base_overtime_hours, 2),  # Переработка БЕЗ обедов
        "meal_hours": round(meal_hours, 2),  # Часы обедов
        "total_overtime_hours": round(total_overtime_hours, 2),  # Всего переработки
        "breakdown": {
            "base_pay": {
                "net": base_pay_net,
                "gross": base_pay_gross
            },
            "overtime": overtime_breakdown,  # Прогрессивные ставки (БЕЗ обедов)
            "meals": meal_breakdown,  # Обеды (по базовой ставке)
            "daily_allowance": daily_allowance_pay,
            "services": services_breakdown
        }
    }
    
    # 10. Сохраняем в таблицу earnings
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO earnings (
                shift_id, base_pay_net, base_pay_gross,
                overtime_pay, daily_allowance, services_pay,
                total_net, total_gross, calculation_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shift_id, base_pay_net, base_pay_gross,
            overtime_pay_gross + meal_pay_gross,  # Сумма переработки + обеды
            daily_allowance_pay, services_pay_gross,
            total_net, total_gross, json.dumps(calculation_details, ensure_ascii=False)
        ))
        await db.commit()
    
    return calculation_details, total_net, total_gross