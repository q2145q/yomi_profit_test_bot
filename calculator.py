"""
Расчёт заработка по смене
Статус: ✅ Исправлена логика брутто/нетто
"""
from database import get_profession_by_project, get_progressive_rates, get_additional_services
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
        - calculation_details: детальный расчёт (dict)
        - total_net: итого нетто (int)
        - total_gross: итого брутто (int)
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
    
    # 3. Базовая оплата (всегда выплачивается, даже если отработано меньше)
    base_pay_net = profession["base_rate_net"]
    base_pay_gross = profession["base_rate_gross"]
    
    # 4. Переработки (с прогрессивными ставками)
    # ВАЖНО: ставки переработки указаны в нетто, но умножаем на брутто
    overtime_hours = 0
    overtime_pay_net = 0
    overtime_pay_gross = 0
    overtime_breakdown = []
    
    if total_hours > base_hours:
        overtime_hours_raw = total_hours - base_hours
        
        # Применяем порог (threshold) - первые X часов не считаются
        overtime_threshold = profession["overtime_threshold"]
        if overtime_hours_raw < overtime_threshold:
            overtime_hours = 0
        else:
            overtime_hours = overtime_hours_raw - overtime_threshold
            
            # Применяем округление (rounding)
            overtime_rounding = profession["overtime_rounding"]
            if overtime_rounding > 0:
                # Округляем вверх до ближайшего значения
                import math
                overtime_hours = math.ceil(overtime_hours / overtime_rounding) * overtime_rounding
        
        # Обновляем overtime_hours в смене
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "UPDATE shifts SET overtime_hours = ? WHERE id = ?",
                (overtime_hours, shift_id)
            )
            await db.commit()
        
        # Получаем прогрессивные ставки
        rates = await get_progressive_rates(profession["id"])
        
        if rates:
            # Применяем прогрессивные ставки
            remaining_hours = overtime_hours
            
            for rate in rates:
                if remaining_hours <= 0:
                    break
                
                # Определяем размер диапазона
                hours_to = rate["hours_to"] if rate["hours_to"] else 999
                bracket_size = hours_to - rate["hours_from"]
                
                # Сколько часов попадает в этот диапазон
                hours_in_bracket = min(remaining_hours, bracket_size)
                
                # ПРАВИЛЬНЫЙ РАСЧЁТ: умножаем часы на БРУТТО ставку
                rate_net = rate["rate"]
                rate_gross = round(rate_net / (1 - tax_percentage / 100))
                
                # Считаем по брутто
                bracket_pay_gross = round(hours_in_bracket * rate_gross)
                # Получаем нетто обратно
                bracket_pay_net = round(bracket_pay_gross * (1 - tax_percentage / 100))
                
                overtime_pay_net += bracket_pay_net
                overtime_pay_gross += bracket_pay_gross
                
                # Добавляем в детальный расчёт
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
        else:
            # Если нет прогрессивных ставок - используем базовую
            overtime_pay_net = int(overtime_hours * profession["base_overtime_rate"])
            # ИСПРАВЛЕНО: пересчитываем в брутто
            overtime_pay_gross = round(overtime_pay_net / (1 - tax_percentage / 100))
            
            overtime_breakdown.append({
                "bracket": "базовая",
                "hours": round(overtime_hours, 2),
                "rate_net": profession["base_overtime_rate"],
                "rate_gross": round(profession["base_overtime_rate"] / (1 - tax_percentage / 100)),
                "total_net": overtime_pay_net,
                "total_gross": overtime_pay_gross
            })
    
    # 5. Суточные (только если установлен флаг is_expense_day)
    daily_allowance_pay = 0
    if shift["is_expense_day"]:
        daily_allowance_pay = profession["daily_allowance"]
    
    # 6. Дополнительные услуги
    # ВАЖНО: стоимость услуг указана в нетто, каждая услуга может иметь свой налог
    services_pay_net = 0
    services_pay_gross = 0
    services_breakdown = []
    
    if shift["parsed_data"]:
        try:
            parsed_data = json.loads(shift["parsed_data"])
            mentioned_services = parsed_data.get("services", [])
            
            if mentioned_services:
                # Получаем все доступные услуги
                available_services = await get_additional_services(profession["id"])
                
                # Ищем совпадения
                for service in available_services:
                    service_name_lower = service["name"].lower()
                    
                    # Проверяем, упоминается ли услуга
                    is_mentioned = any(
                        service_name_lower in mentioned.lower() or mentioned.lower() in service_name_lower
                        for mentioned in mentioned_services
                    )
                    
                    if is_mentioned:
                        service_net = service["cost"]
                        # ИСПРАВЛЕНО: каждая услуга использует свой налог!
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
            pass  # Если не можем распарсить - пропускаем услуги
    
    # 7. Итого
    total_net = base_pay_net + overtime_pay_net + daily_allowance_pay + services_pay_net
    total_gross = base_pay_gross + overtime_pay_gross + daily_allowance_pay + services_pay_gross
    
    # 8. Детали расчёта
    calculation_details = {
        "base_hours": base_hours,
        "total_hours": round(total_hours, 2),
        "overtime_hours": round(overtime_hours, 2),
        "breakdown": {
            "base_pay": {
                "net": base_pay_net,
                "gross": base_pay_gross
            },
            "overtime": overtime_breakdown,
            "daily_allowance": daily_allowance_pay,
            "services": services_breakdown
        }
    }
    
    # 9. Сохраняем в таблицу earnings
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO earnings (
                shift_id, base_pay_net, base_pay_gross,
                overtime_pay, daily_allowance, services_pay,
                total_net, total_gross, calculation_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shift_id, base_pay_net, base_pay_gross,
            overtime_pay_gross, daily_allowance_pay, services_pay_gross,
            total_net, total_gross, json.dumps(calculation_details, ensure_ascii=False)
        ))
        await db.commit()
    
    return calculation_details, total_net, total_gross