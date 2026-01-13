import asyncio
from database import init_db, create_user, create_project, get_user_projects, get_active_project

async def test():
    print("🔧 Инициализация БД...")
    await init_db()
    
    # Создаём тестового пользователя
    user_id = 123456
    await create_user(user_id, "test_user")
    print(f"✅ Пользователь {user_id} готов")
    
    # Создаём проект
    print("\n📋 Создаём проект...")
    project_id = await create_project(
        user_id=user_id,
        name="Тестовый фильм",
        description="Описание тестового проекта"
    )
    print(f"✅ Проект создан с ID: {project_id}")
    
    # Получаем список всех проектов
    print("\n📚 Список всех проектов:")
    projects = await get_user_projects(user_id)
    for project in projects:
        print(f"  - ID: {project['id']}, Название: {project['name']}, Активен: {project['is_active']}")
    
    # Получаем активный проект
    print("\n🎯 Активный проект:")
    active = await get_active_project(user_id)
    if active:
        print(f"  ID: {active['id']}, Название: {active['name']}")
    else:
        print("  Активных проектов нет")
    
    print("\n✅ Тест завершён успешно!")

asyncio.run(test())