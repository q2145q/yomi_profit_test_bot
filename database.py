"""
Работа с базой данных SQLite
Статус: 🚧 В разработке (добавлена таблица shifts)
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
        
        # Таблица shifts (НОВАЯ)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                total_hours REAL,
                overtime_hours REAL DEFAULT 0,
                is_expense_day BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'draft',
                original_message TEXT,
                parsed_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
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

# === НОВЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ СО СМЕНАМИ ===

async def create_shift(
    project_id: int,
    date: str,
    start_time: str,
    end_time: str,
    total_hours: float,
    original_message: str,
    parsed_data: str
):
    """
    Создание новой смены
    
    Args:
        project_id: ID проекта
        date: Дата смены (YYYY-MM-DD)
        start_time: Время начала (HH:MM)
        end_time: Время окончания (HH:MM)
        total_hours: Общее количество часов
        original_message: Исходное сообщение пользователя
        parsed_data: Распознанные данные (JSON string)
    
    Returns:
        ID созданной смены
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO shifts (
                project_id, date, start_time, end_time,
                total_hours, original_message, parsed_data, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'draft')
        """, (project_id, date, start_time, end_time, total_hours, original_message, parsed_data))
        await db.commit()
        return cursor.lastrowid

async def confirm_shift(shift_id: int):
    """
    Подтверждение смены
    
    Args:
        shift_id: ID смены
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE shifts 
            SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (shift_id,))
        await db.commit()

async def get_shift(shift_id: int):
    """
    Получение смены по ID
    
    Args:
        shift_id: ID смены
    
    Returns:
        Данные смены или None
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM shifts WHERE id = ?",
            (shift_id,)
        ) as cursor:
            return await cursor.fetchone()

async def get_user_shifts(project_id: int, limit: int = 10):
    """
    Получение смен проекта
    
    Args:
        project_id: ID проекта
        limit: Максимальное количество смен
    
    Returns:
        Список смен
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM shifts WHERE project_id = ? ORDER BY date DESC, created_at DESC LIMIT ?",
            (project_id, limit)
        ) as cursor:
            return await cursor.fetchall()

async def delete_shift(shift_id: int):
    """
    Удаление смены
    
    Args:
        shift_id: ID смены
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM shifts WHERE id = ?", (shift_id,))
        await db.commit()
