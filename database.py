"""
Работа с базой данных SQLite
Статус: 🚧 В разработке - Шаг 6.1: Добавлены таблицы для обедов
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
        
        # Таблица shifts
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

        # Таблица professions
        await db.execute("""
            CREATE TABLE IF NOT EXISTS professions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                position TEXT,
                base_rate_net INTEGER NOT NULL,
                base_rate_gross INTEGER NOT NULL,
                base_overtime_rate INTEGER DEFAULT 0,
                daily_allowance INTEGER DEFAULT 0,
                base_shift_hours REAL DEFAULT 12,
                break_hours REAL DEFAULT 12,
                tax_percentage REAL DEFAULT 13,
                payment_schedule TEXT DEFAULT 'monthly',
                conditions TEXT,
                overtime_rounding REAL DEFAULT 0,
                overtime_threshold REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)

        # Таблица progressive_rates
        await db.execute("""
            CREATE TABLE IF NOT EXISTS progressive_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profession_id INTEGER NOT NULL,
                hours_from REAL NOT NULL,
                hours_to REAL,
                rate INTEGER NOT NULL,
                order_num INTEGER NOT NULL,
                FOREIGN KEY (profession_id) REFERENCES professions(id)
            )
        """)

        # Таблица additional_services
        await db.execute("""
            CREATE TABLE IF NOT EXISTS additional_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profession_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                cost INTEGER NOT NULL,
                tax_percentage REAL DEFAULT 13,
                application_rule TEXT DEFAULT 'on_mention',
                linked_service_id INTEGER,
                keywords TEXT,
                FOREIGN KEY (profession_id) REFERENCES professions(id),
                FOREIGN KEY (linked_service_id) REFERENCES additional_services(id)
            )
        """)
        
        # === НОВЫЕ ТАБЛИЦЫ (Шаг 6.1) ===
        
        # Таблица meal_types (типы обедов: текущий, поздний и т.д.)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS meal_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profession_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                adds_overtime_hours REAL DEFAULT 1.0,
                keywords TEXT,
                FOREIGN KEY (profession_id) REFERENCES professions(id)
            )
        """)
        
        # Таблица shift_meals (связь смен и обедов)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shift_meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shift_id INTEGER NOT NULL,
                meal_type_id INTEGER NOT NULL,
                FOREIGN KEY (shift_id) REFERENCES shifts(id),
                FOREIGN KEY (meal_type_id) REFERENCES meal_types(id)
            )
        """)

        # Таблица shift_services (связь смен и услуг)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shift_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shift_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                applied BOOLEAN DEFAULT 1,
                FOREIGN KEY (shift_id) REFERENCES shifts(id),
                FOREIGN KEY (service_id) REFERENCES additional_services(id)
            )
        """)

        # Таблица earnings
        await db.execute("""
            CREATE TABLE IF NOT EXISTS earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shift_id INTEGER NOT NULL,
                base_pay_net INTEGER,
                base_pay_gross INTEGER,
                overtime_pay INTEGER DEFAULT 0,
                daily_allowance INTEGER DEFAULT 0,
                services_pay INTEGER DEFAULT 0,
                total_net INTEGER,
                total_gross INTEGER,
                calculation_details TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (shift_id) REFERENCES shifts(id)
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

# === ФУНКЦИИ ДЛЯ РАБОТЫ СО СМЕНАМИ ===

async def create_shift(
    project_id: int,
    date: str,
    start_time: str,
    end_time: str,
    total_hours: float,
    original_message: str,
    parsed_data: str
):
    """Создание новой смены"""
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
    """Подтверждение смены"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE shifts 
            SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (shift_id,))
        await db.commit()

async def get_shift(shift_id: int):
    """Получение смены по ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM shifts WHERE id = ?",
            (shift_id,)
        ) as cursor:
            return await cursor.fetchone()

async def get_user_shifts(project_id: int, limit: int = 10):
    """Получение смен проекта"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM shifts WHERE project_id = ? ORDER BY date DESC, created_at DESC LIMIT ?",
            (project_id, limit)
        ) as cursor:
            return await cursor.fetchall()

async def delete_shift(shift_id: int):
    """Удаление смены"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM shifts WHERE id = ?", (shift_id,))
        await db.commit()

# === ФУНКЦИИ ДЛЯ РАБОТЫ С ПРОФЕССИЯМИ ===

async def create_profession(
    project_id: int,
    position: str,
    base_rate_net: int,
    tax_percentage: float,
    base_overtime_rate: int = 0,
    daily_allowance: int = 0,
    base_shift_hours: float = 12,
    break_hours: float = 12,
    payment_schedule: str = 'monthly',
    conditions: str = '',
    overtime_rounding: float = 0,
    overtime_threshold: float = 0
):
    """Создание настроек профессии для проекта"""
    # Расчёт брутто из нетто
    base_rate_gross = round(base_rate_net / (1 - tax_percentage / 100))
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO professions (
                project_id, position, base_rate_net, base_rate_gross,
                tax_percentage, base_overtime_rate, daily_allowance,
                base_shift_hours, break_hours, payment_schedule, conditions,
                overtime_rounding, overtime_threshold
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, position, base_rate_net, base_rate_gross,
            tax_percentage, base_overtime_rate, daily_allowance,
            base_shift_hours, break_hours, payment_schedule, conditions,
            overtime_rounding, overtime_threshold
        ))
        await db.commit()
        return cursor.lastrowid

async def get_profession_by_project(project_id: int):
    """Получение настроек профессии по проекту"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM professions WHERE project_id = ?",
            (project_id,)
        ) as cursor:
            return await cursor.fetchone()

async def add_progressive_rate(
    profession_id: int,
    hours_from: float,
    hours_to: float or None,
    rate: int,
    order_num: int
):
    """Добавление прогрессивной ставки переработки"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO progressive_rates (
                profession_id, hours_from, hours_to, rate, order_num
            ) VALUES (?, ?, ?, ?, ?)
        """, (profession_id, hours_from, hours_to, rate, order_num))
        await db.commit()

async def get_progressive_rates(profession_id: int):
    """Получение прогрессивных ставок профессии"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM progressive_rates WHERE profession_id = ? ORDER BY order_num",
            (profession_id,)
        ) as cursor:
            return await cursor.fetchall()

async def add_additional_service(
    profession_id: int,
    name: str,
    cost: int,
    application_rule: str = 'on_mention',
    tax_percentage: float = 13,
    keywords: str = ''
):
    """Добавление дополнительной услуги"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO additional_services (
                profession_id, name, cost, tax_percentage, application_rule, keywords
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (profession_id, name, cost, tax_percentage, application_rule, keywords))
        await db.commit()
        return cursor.lastrowid

async def get_additional_services(profession_id: int):
    """Получение дополнительных услуг профессии"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM additional_services WHERE profession_id = ?",
            (profession_id,)
        ) as cursor:
            return await cursor.fetchall()

# === НОВЫЕ ФУНКЦИИ (Шаг 6.1): РАБОТА С ОБЕДАМИ ===

async def add_meal_type(
    profession_id: int,
    name: str,
    adds_overtime_hours: float = 1.0,
    keywords: str = ''
):
    """
    Добавление типа обеда
    
    Args:
        profession_id: ID профессии
        name: Название обеда (например, "текущий обед", "поздний обед")
        adds_overtime_hours: Сколько часов добавляет к переработке (по умолчанию 1.0)
        keywords: Ключевые слова для парсинга (JSON array)
    
    Returns:
        ID созданного типа обеда
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO meal_types (
                profession_id, name, adds_overtime_hours, keywords
            ) VALUES (?, ?, ?, ?)
        """, (profession_id, name, adds_overtime_hours, keywords))
        await db.commit()
        return cursor.lastrowid

async def get_meal_types(profession_id: int):
    """
    Получение типов обедов профессии
    
    Args:
        profession_id: ID профессии
    
    Returns:
        Список типов обедов
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM meal_types WHERE profession_id = ?",
            (profession_id,)
        ) as cursor:
            return await cursor.fetchall()

async def add_shift_meal(shift_id: int, meal_type_id: int):
    """
    Привязать обед к смене
    
    Args:
        shift_id: ID смены
        meal_type_id: ID типа обеда
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO shift_meals (shift_id, meal_type_id)
            VALUES (?, ?)
        """, (shift_id, meal_type_id))
        await db.commit()

async def get_shift_meals(shift_id: int):
    """
    Получить все обеды смены с деталями
    
    Args:
        shift_id: ID смены
    
    Returns:
        Список обедов с информацией о типе обеда
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT mt.* 
            FROM shift_meals sm
            JOIN meal_types mt ON sm.meal_type_id = mt.id
            WHERE sm.shift_id = ?
        """, (shift_id,)) as cursor:
            return await cursor.fetchall()