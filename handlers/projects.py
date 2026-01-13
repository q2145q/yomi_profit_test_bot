"""
Обработчики для работы с проектами
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import create_project, get_user

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
    
    await message.answer(
        f"✅ Проект '{data['name']}' создан!\n\n"
        f"ID проекта: {project_id}\n\n"
        f"Теперь настройте профессию и тарифы.\n"
        f"(Mini App будет добавлен позже)"
    )
    
    await state.clear()