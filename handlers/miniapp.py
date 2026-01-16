"""
Обработчик для Telegram Mini App
"""
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from database import get_user

router = Router()

@router.message(Command("new_project"))
async def cmd_new_project(message: Message):
    """Открытие Mini App для создания проекта"""
    user = await get_user(message.from_user.id)
    
    if user is None:
        await message.answer("Сначала отправьте /start")
        return
    
    # URL твоего Mini App на сервере
    webapp_url = "https://37821a0c5434.ngrok-free.app/miniapp/index.html"
    
    # Создаём кнопку с Web App
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📋 Открыть форму",
            web_app=WebAppInfo(url=webapp_url)
        )]
    ])
    
    await message.answer(
        "📋 Создание нового проекта\n\n"
        "Нажмите кнопку ниже, чтобы открыть форму настройки.",
        reply_markup=keyboard
    )