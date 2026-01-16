"""
Обработчики для работы с проектами
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import (
    create_project, get_user, create_profession,
    add_progressive_rate, add_additional_service
)

router = Router()

class NewProjectStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()

@router.message(Command("new_project"))
async def cmd_new_project(message: Message, state: FSMContext):
    """Создание нового проекта"""
    user = await get_user(message.from_user.id)
    
    if user is None:
        await message.answer("Сначала отправьте /start")
        return
    
    await message.answer("Введите название проекта:")
    await state.set_state(NewProjectStates.waiting_for_name)

@router.message(NewProjectStates.waiting_for_name)
async def project_name_entered(message: Message, state: FSMContext):
    """Получено название проекта"""
    await state.update_data(name=message.text)
    await message.answer(
        "Введите описание проекта (или отправьте '-' чтобы пропустить):"
    )
    await state.set_state(NewProjectStates.waiting_for_description)

@router.message(NewProjectStates.waiting_for_description)
async def project_description_entered(message: Message, state: FSMContext):
    """Получено описание проекта"""
    data = await state.get_data()
    description = message.text if message.text != "-" else ""
    
    # Создаём проект
    project_id = await create_project(
        user_id=message.from_user.id,
        name=data["name"],
        description=description
    )
    
    # === НОВЫЙ КОД: Автоматическое создание профессии ===
    
    # Создаём базовую профессию для тестирования
    profession_id = await create_profession(
        project_id=project_id,
        position="Оператор",           # Временное значение
        base_rate_net=10000,            # 10,000₽ нетто
        tax_percentage=13,              # 13% налог
        base_overtime_rate=500,         # 500₽/ч базовая переработка
        daily_allowance=1000,           # 1,000₽ суточные
        base_shift_hours=12,            # 12 часов базовая смена
        break_hours=12,                 # 12 часов разрыв
        payment_schedule='monthly',
        conditions='7-й день подряд × 2',
        overtime_rounding=0.5,          # Округление по 0.5 часа
        overtime_threshold=0.25         # Первые 15 минут не считаются
    )
    
    # Добавляем прогрессивные ставки переработки
    # 0-2 часа: 500₽/ч
    await add_progressive_rate(profession_id, 0, 2, 500, 1)
    # 2-4 часа: 600₽/ч
    await add_progressive_rate(profession_id, 2, 4, 600, 2)
    # 4+ часа: 700₽/ч
    await add_progressive_rate(profession_id, 4, None, 700, 3)
    
    # Добавляем дополнительные услуги
    # Услуги облагаются налогом 15% (а не 13% как базовая ставка)
    await add_additional_service(
        profession_id=profession_id,
        name="обед",
        cost=500,
        tax_percentage=15,  # Налог для услуги
        application_rule='on_mention',
        keywords='["обед", "текущий обед"]'
    )
    await add_additional_service(
        profession_id=profession_id,
        name="ронин",
        cost=3000,
        tax_percentage=15,  # Налог для услуги
        application_rule='on_mention',
        keywords='["ронин"]'
    )
    
    # === КОНЕЦ НОВОГО КОДА ===
    
    await message.answer(
        f"✅ Проект '{data['name']}' создан!\n\n"
        f"📋 Созданы базовые настройки:\n"
        f"• Должность: Оператор\n"
        f"• Базовая ставка: 10,000₽ (нетто)\n"
        f"• Переработка:\n"
        f"  - 0-2ч: 500₽/ч (нетто) / 575₽/ч (брутто)\n"
        f"  - 2-4ч: 600₽/ч (нетто) / 690₽/ч (брутто)\n"
        f"  - 4+ч: 700₽/ч (нетто) / 805₽/ч (брутто)\n"
        f"  - Округление: по 0.5 часа\n"
        f"  - Порог: первые 15 минут не считаются\n"
        f"• Суточные: 1,000₽\n"
        f"• Услуги: обед (500₽), ронин (3,000₽)\n\n"
        f"Теперь можете вносить смены через чат!\n"
        f"Например: \"Смена 07:00 до 23:00 + обед\""
    )
    
    await state.clear()