"""
Обработчик команды /start
"""
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from database import create_user, get_user
import aiosqlite
from config import DATABASE_PATH

router = Router()

class ContractorTypeCallback(CallbackData, prefix="contractor_type"):
    type: str

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start"""
    # Сохраняем пользователя в БД
    await create_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "Unknown"
    )
    
    user = await get_user(message.from_user.id)
    
    if user is None or user["contractor_type"] is None:
        # Новый пользователь - выбор типа
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="👤 Я исполнитель (человек)",
                callback_data=ContractorTypeCallback(type="person").pack()
            )],
            [InlineKeyboardButton(
                text="🚗 Я владелец транспорта (скоро)",
                callback_data=ContractorTypeCallback(type="transport").pack()
            )]
        ])
        
        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "Выберите тип контрагента:",
            reply_markup=keyboard
        )
    else:
        # Существующий пользователь
        await message.answer(
            f"👋 С возвращением!\n\n"
            f"Используйте /new_project для создания проекта."
        )

@router.callback_query(ContractorTypeCallback.filter())
async def contractor_type_selected(
    callback: CallbackQuery,
    callback_data: ContractorTypeCallback
):
    """Обработка выбора типа контрагента"""
    if callback_data.type == "transport":
        await callback.answer(
            "Эта функция пока недоступна",
            show_alert=True
        )
        return
    
    # Обновляем тип контрагента в БД
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET contractor_type = ? WHERE id = ?",
            (callback_data.type, callback.from_user.id)
        )
        await db.commit()
    
    await callback.message.edit_text(
        "✅ Отлично! Теперь создайте ваш первый проект.\n\n"
        "Используйте команду /new_project"
    )
    await callback.answer()