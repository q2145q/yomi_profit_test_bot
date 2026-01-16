"""
Обработчик для Telegram Mini App
"""
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from database import get_user, create_project
import json

router = Router()

@router.message(Command("new_project"))
async def cmd_new_project(message: Message):
    """Открытие Mini App для создания проекта"""
    user = await get_user(message.from_user.id)
    
    if user is None:
        await message.answer("Сначала отправьте /start")
        return
    
    # URL твоего Mini App на сервере
    webapp_url = "https://024765ff09fb.ngrok-free.app/create-project.html?v=2"
    
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

@router.message(lambda message: message.web_app_data)
async def handle_web_app_data(message: Message):
    """Обработка данных из Mini App"""
    try:
        print("\n" + "="*60)
        print("📥 ПОЛУЧЕНЫ ДАННЫЕ ИЗ MINI APP")
        print("="*60)
        
        # Парсим JSON данные
        data = json.loads(message.web_app_data.data)
        action = data.get('action')
        
        print(f"Action: {action}")
        print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print("="*60 + "\n")
        
        if action == 'create_project':
            print("🔧 Создаём проект в БД...")
            
            # Создаём проект в БД
            project_id = await create_project(
                user_id=message.from_user.id,
                name=data['project_name'],
                description=data.get('project_description', '')
            )
            
            print(f"✅ Проект создан! ID: {project_id}")
            print(f"   Название: {data['project_name']}")
            print(f"   User ID: {message.from_user.id}\n")
            
            # URL страницы деталей проекта
            webapp_url = f"https://024765ff09fb.ngrok-free.app/project-details.html?project_id={project_id}&project_name={data['project_name']}"
            
            print(f"🔗 URL для деталей проекта:")
            print(f"   {webapp_url}\n")
            
            # Отправляем кнопку для открытия деталей проекта
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"📋 {data['project_name']}",
                    web_app=WebAppInfo(url=webapp_url)
                )]
            ])
            
            await message.answer(
                f"✅ Проект '{data['project_name']}' создан!\n\n"
                f"Теперь добавьте профессии и услуги:",
                reply_markup=keyboard
            )
        
        elif action == 'add_profession':
            print("🔧 Добавление профессии...")
            # Обработка добавления профессии (сделаем позже)
            await message.answer("✅ Профессия добавлена!")
        
        elif action == 'add_service':
            print("🔧 Добавление услуги...")
            # Обработка добавления услуги (сделаем позже)
            await message.answer("✅ Услуга добавлена!")
        
        else:
            print(f"⚠️ Неизвестное действие: {action}")
            await message.answer(f"⚠️ Неизвестное действие: {action}")
    
    except Exception as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
        print(f"   Тип: {type(e).__name__}\n")
        import traceback
        traceback.print_exc()
        
        await message.answer(f"❌ Ошибка обработки данных: {str(e)}")