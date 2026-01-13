"""
Работа с базой данных SQLite
Статус: 🚧 В разработке
"""
import aiosqlite
from config import DATABASE_PATH

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Таблица users
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                contractor_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Таблица projects
        await db.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        await db.commit()

async def create_user(user_id: int, username: str):
    """Создание нового пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()

async def get_user(user_id: int):
    """Получение пользователя по ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE id = ?", 
            (user_id,)
        ) as cursor:
            return await cursor.fetchone()

async def create_project(user_id: int, name: str, description: str = ""):
    """Создание нового проекта"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO projects (user_id, name, description) VALUES (?, ?, ?)",
            (user_id, name, description)
        )
        await db.commit()
        return cursor.lastrowid

async def get_user_projects(user_id: int):
    """Получение всех проектов пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()

async def get_active_project(user_id: int):
    """Получение активного проекта"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM projects WHERE user_id = ? AND is_active = 1 LIMIT 1",
            (user_id,)
        ) as cursor:
            return await cursor.fetchone()