"""
Обработчик для Telegram Mini App
"""
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, ReplyKeyboardRemove
from aiogram.filters import Command
from database import get_user

router = Router()

@router.message(Command("projects"))
async def cmd_projects(message: Message):
    """Открытие Mini App со списком проектов"""
    user = await get_user(message.from_user.id)
    
    if user is None:
        await message.answer("Сначала отправьте /start")
        return
    
    # URL главной страницы Mini App с user_id
    # Замени на свой ngrok URL!
    webapp_url = f"https://21bf2587f988.ngrok-free.app/index.html?user_id={message.from_user.id}"
    
    # Создаём кнопку для открытия Mini App
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="📋 Мои проекты",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "📋 Управление проектами\n\n"
        "Нажмите кнопку ниже, чтобы открыть список проектов.\n"
        "Там вы сможете:\n"
        "• Создавать проекты\n"
        "• Настраивать профессии\n"
        "• Добавлять услуги",
        reply_markup=keyboard
    )