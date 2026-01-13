import asyncio
from database import init_db, create_user, get_user

async def test():
    await init_db()
    await create_user(123456, "test_user")
    user = await get_user(123456)
    print(f"Пользователь создан: {dict(user)}")

asyncio.run(test())