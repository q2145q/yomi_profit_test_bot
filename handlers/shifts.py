"""
Обработчики для работы со сменами
"""
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
import json
import aiosqlite
from config import DATABASE_PATH
from database import get_active_project, get_user, create_shift, confirm_shift
from parser import parse_shift_message
from calculator import calculate_shift_earnings

router = Router()

# Временное хранилище распарсенных смен (в памяти)
# TODO: В будущем использовать Redis или FSM storage
pending_shifts = {}

@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_message(message: Message):
    """Обработка текстовых сообщений как потенциальных смен"""
    user = await get_user(message.from_user.id)
    
    if user is None:
        await message.answer("Сначала отправьте /start")
        return
    
    # Проверяем наличие активного проекта
    project = await get_active_project(message.from_user.id)
    
    if project is None:
        await message.answer(
            "У вас нет активных проектов.\n"
            "Создайте проект командой /new_project"
        )
        return
    
    # Показываем процесс обработки
    processing_msg = await message.answer("⏳ Обрабатываю...")
    
    # Получаем текущие дату и время
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    
    # Парсим сообщение
    result = await parse_shift_message(
        message=message.text,
        current_date=current_date,
        current_time=current_time,
        base_hours=12,  # TODO: Брать из настроек проекта
        services=["обед", "ронин", "текущий обед"]  # TODO: Брать из БД
    )
    
    # Удаляем сообщение о процессе
    await processing_msg.delete()
    
    # Проверяем результат
    if result.get("confidence", 0) < 0.4:
        # Формируем сообщение об ошибке
        error_text = "🤔 Не смог распознать данные смены.\n\n"
        
        if result.get("error"):
            error_text += f"Причина: {result['error']}\n\n"
        
        if result.get("missing_fields"):
            missing = ", ".join(result["missing_fields"])
            error_text += f"⚠️ Не хватает данных: {missing}\n\n"
        
        error_text += "Попробуйте написать так:\n\"Вчера работал с 07:00 до 19:00\""
        
        await message.answer(error_text)
        return
    
    # Проверяем обязательные поля
    if not result.get("start_time") or not result.get("end_time"):
        missing = []
        if not result.get("start_time"):
            missing.append("время начала")
        if not result.get("end_time"):
            missing.append("время окончания")
        
        await message.answer(
            f"⚠️ Не хватает данных: {', '.join(missing)}\n\n"
            f"Пожалуйста, уточните."
        )
        return
    
    # Формируем карточку для подтверждения
    date_obj = datetime.strptime(result["date"], "%Y-%m-%d")
    date_str = date_obj.strftime("%d.%m.%Y")
    
    # Определяем относительную дату
    today = datetime.now().date()
    shift_date = date_obj.date()
    
    if shift_date == today:
        date_label = "сегодня"
    elif shift_date == today.replace(day=today.day - 1):
        date_label = "вчера"
    elif shift_date == today.replace(day=today.day - 2):
        date_label = "позавчера"
    else:
        date_label = date_str
    
    # Вычисляем продолжительность смены
    start = datetime.strptime(result["start_time"], "%H:%M")
    end = datetime.strptime(result["end_time"], "%H:%M")
    
    # Если окончание раньше начала - значит переход через полночь
    if end < start:
        end = end.replace(day=end.day + 1)
    
    total_hours = (end - start).total_seconds() / 3600
    
    text = f"""📋 Проверьте данные смены:

📅 Дата: {date_str} ({date_label})
🕐 Начало: {result['start_time']}
🕔 Конец: {result['end_time']}
⏱ Часов: {total_hours:.1f} ч

📁 Проект: {project['name']}
"""
    
    if result.get("services"):
        text += "\n✅ Дополнительные услуги:\n"
        for service in result["services"]:
            text += f"   • {service}\n"
    
    # Кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_shift"),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_shift")
        ],
        [
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_shift")
        ]
    ])
    
    # Сохраняем распарсенные данные
    pending_shifts[message.from_user.id] = {
        "result": result,
        "project_id": project["id"],
        "original_message": message.text,
        "total_hours": total_hours
    }
    
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "confirm_shift")
async def confirm_shift_callback(callback: CallbackQuery):
    """Подтверждение смены"""
    if callback.from_user.id not in pending_shifts:
        await callback.answer("Данные смены не найдены", show_alert=True)
        return
    
    data = pending_shifts[callback.from_user.id]
    result = data["result"]
    
    # Создаём смену в БД
    shift_id = await create_shift(
        project_id=data["project_id"],
        date=result["date"],
        start_time=result["start_time"],
        end_time=result["end_time"],
        total_hours=data["total_hours"],
        original_message=data["original_message"],
        parsed_data=json.dumps(result, ensure_ascii=False)
    )
    
    # Подтверждаем смену
    await confirm_shift(shift_id)
    
    # === НОВЫЙ КОД: Запускаем расчёт ===
    try:
        details, total_net, total_gross = await calculate_shift_earnings(
            shift_id=shift_id,
            project_id=data["project_id"]
        )
        
        # Обновляем статус смены на "calculated"
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "UPDATE shifts SET status = 'calculated' WHERE id = ?",
                (shift_id,)
            )
            await db.commit()
        
        # Формируем детальную карточку с расчётом
        date_obj = datetime.strptime(result["date"], "%Y-%m-%d")
        date_str = date_obj.strftime("%d.%m.%Y")
        
        text = f"""✅ Смена #{shift_id} подтверждена и рассчитана!

📅 Дата: {date_str}
⏱ Часов: {details['total_hours']:.1f} ч (из них {details['base_hours']:.0f} базовых)

💵 РАСЧЁТ:

1️⃣ Базовая ставка:
   • {details['breakdown']['base_pay']['net']:,}₽ (нетто)
   • {details['breakdown']['base_pay']['gross']:,}₽ (брутто)
"""
        
        # Добавляем переработки
        if details['overtime_hours'] > 0:
            text += f"\n2️⃣ Переработка ({details['overtime_hours']:.1f} ч):\n"
            
            total_overtime_net = 0
            total_overtime_gross = 0
            
            for bracket in details['breakdown']['overtime']:
                text += f"   • {bracket['bracket']}: {bracket['hours']:.1f}ч × {bracket['rate_gross']}₽ = {bracket['total_gross']:,}₽\n"
                total_overtime_net += bracket['total_net']
                total_overtime_gross += bracket['total_gross']
            
            text += f"   Итого: {total_overtime_net:,}₽ (нетто) / {total_overtime_gross:,}₽ (брутто)\n"
        
        # Добавляем суточные
        if details['breakdown']['daily_allowance'] > 0:
            text += f"\n3️⃣ Суточные: {details['breakdown']['daily_allowance']:,}₽\n"
        
        # Добавляем услуги
        if details['breakdown']['services']:
            text += f"\n4️⃣ Дополнительные услуги:\n"
            
            total_services_net = 0
            total_services_gross = 0
            
            for service in details['breakdown']['services']:
                text += f"   • {service['name']}: {service['cost_net']:,}₽ (нетто) / {service['cost_gross']:,}₽ (брутто)\n"
                total_services_net += service['cost_net']
                total_services_gross += service['cost_gross']
            
            text += f"   Итого: {total_services_net:,}₽ (нетто) / {total_services_gross:,}₽ (брутто)\n"
        
        # Итого
        text += f"""
━━━━━━━━━━━━━━━━━━━━
💰 ИТОГО:
   • Нетто: {total_net:,}₽
   • Брутто: {total_gross:,}₽
━━━━━━━━━━━━━━━━━━━━"""
        
        await callback.message.edit_text(text)
        
    except Exception as e:
        # Если ошибка расчёта - показываем базовую информацию
        date_obj = datetime.strptime(result["date"], "%Y-%m-%d")
        date_str = date_obj.strftime("%d.%m.%Y")
        
        await callback.message.edit_text(
            f"✅ Смена #{shift_id} подтверждена!\n\n"
            f"📅 Дата: {date_str}\n"
            f"⏱ Часов: {data['total_hours']:.1f} ч\n\n"
            f"⚠️ Ошибка расчёта: {str(e)}\n\n"
            f"Смена сохранена, но заработок не рассчитан."
        )
    
    # Удаляем из временного хранилища
    del pending_shifts[callback.from_user.id]
    await callback.answer()


@router.callback_query(F.data == "edit_shift")
async def edit_shift_callback(callback: CallbackQuery):
    """Изменение смены (пока заглушка)"""
    await callback.answer(
        "Функция редактирования будет добавлена позже через Mini App",
        show_alert=True
    )


@router.callback_query(F.data == "cancel_shift")
async def cancel_shift_callback(callback: CallbackQuery):
    """Отмена смены"""
    if callback.from_user.id in pending_shifts:
        del pending_shifts[callback.from_user.id]
    
    await callback.message.edit_text("❌ Смена отменена")
    await callback.answer()