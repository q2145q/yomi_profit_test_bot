# План разработки: Earnings Tracker Bot

**Версия:** 1.0  
**Дата создания:** 13.01.2026  
**Общий статус:** 🚧 Не начато

---

## Обзор плана

План разбит на **6 фаз**, каждая из которых состоит из нескольких шагов.  
Каждый шаг можно выполнять в отдельном чате с Claude.

**Ориентировочное время:** 3-4 недели (при работе 2-3 часа в день)

```
Фаза 0: Подготовка [~2 часа]
    ↓
Фаза 1: Базовый бот + БД [~1 неделя]
    ↓
Фаза 2: AI-парсинг [~3 дня]
    ↓
Фаза 3: Расчёт заработка [~1 неделя]
    ↓
Фаза 4: Mini App [~1 неделя]
    ↓
Фаза 5: Статистика [~3 дня]
    ↓
Фаза 6: Тестирование и деплой [~2 дня]
```

---

## Принципы разработки

### 1. Пошаговость
- Каждый шаг заканчивается работающим кодом
- После каждого шага — тестирование
- Не переходим к следующему шагу, пока не работает текущий

### 2. Документирование
- После каждого шага обновляем:
  - `STATUS.md` — что работает
  - `CHANGELOG.md` — что изменилось
  - `NEXT_STEPS.md` — что делать дальше

### 3. Комментирование кода
- Все комментарии на русском
- В начале каждого файла — описание и статус
- Каждая функция с docstring на русском

### 4. Бэкапы
- После каждого рабочего шага — коммит в Git
- Комментарий коммита: "Шаг X.Y: Краткое описание"

---

## Фаза 0: Подготовка окружения

**Цель:** Настроить рабочее окружение на локальной машине и сервере.

**Время:** ~2 часа

---

### Шаг 0.1: Установка Python и зависимостей (локально)

**Задача:** Убедиться, что Python 3.10+ установлен, создать виртуальное окружение.

**Действия:**
1. Проверить версию Python: `python3 --version` (должно быть ≥ 3.10)
2. Создать папку проекта:
   ```bash
   mkdir ~/earnings_tracker
   cd ~/earnings_tracker
   ```
3. Создать виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS
   ```
4. Создать файл `requirements.txt`:
   ```
   aiogram==3.3.0
   aiosqlite==0.19.0
   openai==1.10.0
   python-dotenv==1.0.0
   ```
5. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

**Критерий готовности:**
- ✅ Python 3.10+ установлен
- ✅ Виртуальное окружение создано и активировано
- ✅ Все библиотеки установлены без ошибок

**Что обновить:** `STATUS.md` — отметить, что окружение готово.

---

### Шаг 0.2: Получение токенов и ключей

**Задача:** Получить необходимые токены для работы бота.

**Действия:**
1. **Telegram Bot Token:**
   - Открыть [@BotFather](https://t.me/BotFather)
   - Отправить `/newbot`
   - Следовать инструкциям (название, username)
   - Сохранить токен (формат: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **OpenAI API Key:**
   - Зайти на [platform.openai.com](https://platform.openai.com)
   - Перейти в "API keys"
   - Создать новый ключ
   - Сохранить ключ (формат: `sk-proj-...`)

3. Создать файл `.env` в корне проекта:
   ```env
   BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   OPENAI_API_KEY=sk-proj-...
   DATABASE_PATH=data.db
   ```

4. Добавить `.env` в `.gitignore`:
   ```gitignore
   .env
   venv/
   __pycache__/
   *.pyc
   data.db
   ```

**Критерий готовности:**
- ✅ Telegram бот создан, токен получен
- ✅ OpenAI API ключ получен
- ✅ Файл `.env` создан с корректными значениями
- ✅ `.gitignore` настроен

**Что обновить:** `API_KEYS.md` — описать где хранятся ключи (БЕЗ самих ключей!).

---

### Шаг 0.3: Инициализация Git репозитория

**Задача:** Создать Git репозиторий для контроля версий.

**Действия:**
1. Инициализировать репозиторий:
   ```bash
   git init
   ```
2. Создать базовые файлы документации:
   ```bash
   touch README.md STATUS.md CHANGELOG.md NEXT_STEPS.md
   ```
3. Сделать первый коммит:
   ```bash
   git add .
   git commit -m "Инициализация проекта"
   ```

**Критерий готовности:**
- ✅ Git репозиторий инициализирован
- ✅ Базовые файлы созданы
- ✅ Первый коммит выполнен

**Что обновить:** `README.md` — краткое описание проекта и инструкция по запуску.

---

## Фаза 1: Базовый бот + База данных

**Цель:** Создать рабочего Telegram бота с базовыми командами и базой данных.

**Время:** ~1 неделя

---

### Шаг 1.1: Создание структуры проекта

**Задача:** Создать файлы и папки проекта.

**Действия:**
1. Создать структуру:
   ```
   earnings_tracker/
   ├── bot.py              # Главный файл бота
   ├── config.py           # Настройки
   ├── database.py         # Работа с БД
   ├── handlers/           # Обработчики команд
   │   ├── __init__.py
   │   ├── start.py        # /start команда
   │   └── common.py       # Общие обработчики
   ├── utils/              # Утилиты
   │   ├── __init__.py
   │   └── logger.py       # Логирование
   ├── requirements.txt
   ├── .env
   └── .gitignore
   ```

2. Создать файл `config.py`:
   ```python
   """
   Конфигурация бота
   Загружает переменные окружения из .env
   """
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   BOT_TOKEN = os.getenv("BOT_TOKEN")
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   DATABASE_PATH = os.getenv("DATABASE_PATH", "data.db")
   ```

**Критерий готовности:**
- ✅ Структура папок создана
- ✅ `config.py` загружает переменные из `.env`

**Коммит:** `git commit -m "Шаг 1.1: Создана структура проекта"`

---

### Шаг 1.2: Базовая база данных (пользователи)

**Задача:** Создать базу данных SQLite и таблицу `users`.

**Действия:**
1. Создать файл `database.py`:
   ```python
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
                   contractor_type TEXT DEFAULT 'person',
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   is_active BOOLEAN DEFAULT 1
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
   ```

2. Протестировать создание БД:
   ```python
   # test_db.py
   import asyncio
   from database import init_db, create_user, get_user
   
   async def test():
       await init_db()
       await create_user(123456, "test_user")
       user = await get_user(123456)
       print(user)
   
   asyncio.run(test())
   ```

**Критерий готовности:**
- ✅ Файл `data.db` создаётся автоматически
- ✅ Таблица `users` существует
- ✅ Можно создать и получить пользователя

**Коммит:** `git commit -m "Шаг 1.2: Создана БД с таблицей users"`

---

### Шаг 1.3: Простой бот с командой /start

**Задача:** Создать работающего бота, который отвечает на `/start`.

**Действия:**
1. Создать файл `handlers/start.py`:
   ```python
   """
   Обработчик команды /start
   """
   from aiogram import Router
   from aiogram.types import Message
   from aiogram.filters import Command
   from database import create_user, get_user
   
   router = Router()
   
   @router.message(Command("start"))
   async def cmd_start(message: Message):
       """Команда /start"""
       # Сохраняем пользователя в БД
       await create_user(
           user_id=message.from_user.id,
           username=message.from_user.username or "Unknown"
       )
       
       # Проверяем, новый ли пользователь
       user = await get_user(message.from_user.id)
       
       await message.answer(
           "👋 Добро пожаловать в Earnings Tracker!\n\n"
           "Я помогу вам вести учёт смен и автоматически рассчитывать заработок."
       )
   ```

2. Создать главный файл `bot.py`:
   ```python
   """
   Главный файл Telegram бота
   Статус: ✅ Работает базовая версия
   """
   import asyncio
   import logging
   from aiogram import Bot, Dispatcher
   from aiogram.client.default import DefaultBotProperties
   from aiogram.enums import ParseMode
   
   from config import BOT_TOKEN
   from database import init_db
   from handlers import start
   
   # Настройка логирования
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   
   async def main():
       """Запуск бота"""
       # Инициализация БД
       await init_db()
       
       # Создание бота
       bot = Bot(
           token=BOT_TOKEN,
           default=DefaultBotProperties(parse_mode=ParseMode.HTML)
       )
       
       # Создание диспетчера
       dp = Dispatcher()
       
       # Подключение роутеров
       dp.include_router(start.router)
       
       # Запуск бота
       logging.info("Бот запущен!")
       await dp.start_polling(bot)
   
   if __name__ == "__main__":
       asyncio.run(main())
   ```

3. Запустить бота:
   ```bash
   python bot.py
   ```

4. Протестировать в Telegram:
   - Найти своего бота
   - Отправить `/start`
   - Получить приветствие

**Критерий готовности:**
- ✅ Бот запускается без ошибок
- ✅ Отвечает на `/start`
- ✅ Пользователь сохраняется в БД

**Коммит:** `git commit -m "Шаг 1.3: Базовый бот с /start"`

---

### Шаг 1.4: Выбор типа контрагента

**Задача:** Добавить кнопки для выбора типа (человек/транспорт).

**Действия:**
1. Обновить `handlers/start.py`:
   ```python
   from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
   from aiogram.types import CallbackQuery
   from aiogram.filters.callback_data import CallbackData
   
   class ContractorTypeCallback(CallbackData, prefix="contractor_type"):
       type: str
   
   @router.message(Command("start"))
   async def cmd_start(message: Message):
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
       if callback_data.type == "transport":
           await callback.answer(
               "Эта функция пока недоступна",
               show_alert=True
           )
           return
       
       # Обновить тип контрагента в БД
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
   ```

**Критерий готовности:**
- ✅ При `/start` новому пользователю показываются кнопки
- ✅ При выборе "Человек" тип сохраняется в БД
- ✅ При повторном `/start` показывается другое сообщение

**Коммит:** `git commit -m "Шаг 1.4: Выбор типа контрагента"`

---

### Шаг 1.5: Таблица projects в БД

**Задача:** Добавить таблицу `projects` для хранения проектов.

**Действия:**
1. Обновить `database.py` — добавить в `init_db()`:
   ```python
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
   ```

2. Добавить функции для работы с проектами:
   ```python
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
   ```

**Критерий готовности:**
- ✅ Таблица `projects` создаётся в БД
- ✅ Можно создать проект
- ✅ Можно получить список проектов пользователя

**Коммит:** `git commit -m "Шаг 1.5: Таблица projects"`

---

### Шаг 1.6: Команда /new_project (без формы)

**Задача:** Добавить команду для создания проекта через текст.

**Действия:**
1. Создать файл `handlers/projects.py`:
   ```python
   """
   Обработчики для работы с проектами
   """
   from aiogram import Router, F
   from aiogram.types import Message
   from aiogram.filters import Command, StateFilter
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
   ```

2. Подключить в `bot.py`:
   ```python
   from handlers import start, projects
   
   dp.include_router(projects.router)
   ```

3. Обновить `bot.py` для работы с FSM:
   ```python
   from aiogram.fsm.storage.memory import MemoryStorage
   
   dp = Dispatcher(storage=MemoryStorage())
   ```

**Критерий готовности:**
- ✅ Команда `/new_project` работает
- ✅ Можно ввести название и описание
- ✅ Проект создаётся в БД

**Коммит:** `git commit -m "Шаг 1.6: Команда /new_project"`

---

**Итог Фазы 1:**
- ✅ Бот запускается и работает
- ✅ База данных создаётся автоматически
- ✅ Можно создать пользователя и проект
- ✅ Есть выбор типа контрагента

**Обновить:**
- `STATUS.md` — отметить, что Фаза 1 завершена
- `CHANGELOG.md` — добавить все изменения
- `NEXT_STEPS.md` — описать Фазу 2

---

## Фаза 2: AI-парсинг сообщений

**Цель:** Реализовать парсинг текстовых сообщений с помощью OpenAI API.

**Время:** ~3 дня

---

### Шаг 2.1: Создание модуля parser.py

**Задача:** Создать функцию для отправки запросов в OpenAI.

**Действия:**
1. Создать файл `parser.py`:
   ```python
   """
   AI-парсинг сообщений для извлечения данных о смене
   Статус: 🚧 В разработке
   """
   from openai import AsyncOpenAI
   from config import OPENAI_API_KEY
   import json
   from datetime import datetime
   
   client = AsyncOpenAI(api_key=OPENAI_API_KEY)
   
   async def parse_shift_message(
       message: str,
       current_date: str,
       base_hours: int = 12,
       services: list = None
   ) -> dict:
       """
       Парсинг сообщения о смене с помощью AI
       
       Args:
           message: Сообщение пользователя
           current_date: Текущая дата (YYYY-MM-DD)
           base_hours: Базовое количество часов
           services: Список доступных услуг
       
       Returns:
           dict с полями: date, start_time, end_time, services, confidence, missing_fields
       """
       if services is None:
           services = []
       
       # Формируем промпт
       prompt = f"""Ты — парсер сообщений для учёта рабочих смен.

Контекст:
- Текущая дата: {current_date}
- Базовое количество часов: {base_hours}
- Доступные услуги: {json.dumps(services, ensure_ascii=False)}

Сообщение пользователя:
"{message}"

Верни JSON в следующем формате:
{{
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "services": ["service_name_1", "service_name_2"],
  "confidence": 0.95,
  "missing_fields": []
}}

Правила:
1. Если дата не указана - используй текущую дату
2. "вчера" = текущая дата - 1 день
3. "позавчера" = текущая дата - 2 дня
4. Время в формате 24 часа (HH:MM)
5. Если не можешь определить поле - добавь его в "missing_fields"
6. confidence - твоя уверенность в распознавании (0.0-1.0)

Верни ТОЛЬКО JSON, без дополнительного текста."""
       
       try:
           response = await client.chat.completions.create(
               model="gpt-4o-mini",  # Используем более дешевую модель
               messages=[
                   {"role": "system", "content": "Ты — точный парсер данных. Отвечай только валидным JSON."},
                   {"role": "user", "content": prompt}
               ],
               temperature=0.1,
               max_tokens=300
           )
           
           # Извлекаем JSON из ответа
           content = response.choices[0].message.content.strip()
           
           # Убираем markdown если есть
           if content.startswith("```"):
               content = content.split("```")[1]
               if content.startswith("json"):
                   content = content[4:]
           
           result = json.loads(content)
           return result
           
       except Exception as e:
           # В случае ошибки возвращаем структуру с ошибкой
           return {
               "date": current_date,
               "start_time": None,
               "end_time": None,
               "services": [],
               "confidence": 0.0,
               "missing_fields": ["start_time", "end_time"],
               "error": str(e)
           }
   ```

2. Протестировать парсинг:
   ```python
   # test_parser.py
   import asyncio
   from parser import parse_shift_message
   from datetime import datetime
   
   async def test():
       result = await parse_shift_message(
           message="Смена 07:00 до 23:00 + обед + ронин",
           current_date=datetime.now().strftime("%Y-%m-%d"),
           base_hours=12,
           services=["обед", "ронин", "текущий обед"]
       )
       print(json.dumps(result, indent=2, ensure_ascii=False))
   
   asyncio.run(test())
   ```

**Критерий готовности:**
- ✅ Функция `parse_shift_message` работает
- ✅ Возвращает корректный JSON
- ✅ Обрабатывает ошибки

**Коммит:** `git commit -m "Шаг 2.1: Модуль AI-парсинга"`

---

### Шаг 2.2: Обработка текстовых сообщений

**Задача:** Бот должен реагировать на любое текстовое сообщение и пытаться распарсить его как смену.

**Действия:**
1. Создать файл `handlers/shifts.py`:
   ```python
   """
   Обработчики для работы со сменами
   """
   from aiogram import Router, F
   from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
   from datetime import datetime
   from database import get_active_project, get_user
   from parser import parse_shift_message
   
   router = Router()
   
   @router.message(F.text & ~F.text.startswith("/"))
   async def handle_text_message(message: Message):
       """Обработка текстовых сообщений как потенциальных смен"""
       user = await get_user(message.from_user.id)
       
       if user is None:
           await message.answer("Сначала отправьте /start")
           return
       
       # Проверяем наличие активного проекта
       project = await get_active_project(message.from_user.id)
       
       if project is None:
           await message.answer(
               "У вас нет активных проектов.\n"
               "Создайте проект командой /new_project"
           )
           return
       
       # Показываем процесс обработки
       processing_msg = await message.answer("⏳ Обрабатываю...")
       
       # Парсим сообщение
       result = await parse_shift_message(
           message=message.text,
           current_date=datetime.now().strftime("%Y-%m-%d"),
           base_hours=12,  # TODO: Брать из настроек проекта
           services=["обед", "ронин"]  # TODO: Брать из БД
       )
       
       # Удаляем сообщение о процессе
       await processing_msg.delete()
       
       # Проверяем результат
       if result.get("confidence", 0) < 0.5:
           await message.answer(
               "🤔 Не смог распознать данные смены.\n\n"
               "Попробуйте написать так:\n"
               "\"Смена 07:00 до 19:00\""
           )
           return
       
       # Проверяем обязательные поля
       if result.get("missing_fields"):
           missing = ", ".join(result["missing_fields"])
           await message.answer(
               f"⚠️ Не хватает данных: {missing}\n\n"
               f"Пожалуйста, уточните."
           )
           return
       
       # Формируем карточку для подтверждения
       date_str = datetime.strptime(result["date"], "%Y-%m-%d").strftime("%d.%m.%Y")
       
       text = f"""📋 Проверьте данные смены:

📅 Дата: {date_str}
🕐 Начало: {result['start_time']}
🕔 Конец: {result['end_time']}

Проект: {project['name']}
"""
       
       if result.get("services"):
           text += "\nУслуги:\n"
           for service in result["services"]:
               text += f"✅ {service}\n"
       
       # Кнопки
       keyboard = InlineKeyboardMarkup(inline_keyboard=[
           [
               InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_shift"),
               InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_shift")
           ],
           [
               InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_shift")
           ]
       ])
       
       await message.answer(text, reply_markup=keyboard)
   ```

2. Подключить в `bot.py`:
   ```python
   from handlers import start, projects, shifts
   
   dp.include_router(shifts.router)
   ```

**Критерий готовности:**
- ✅ Бот реагирует на текстовые сообщения
- ✅ Парсит сообщение через AI
- ✅ Показывает карточку подтверждения

**Коммит:** `git commit -m "Шаг 2.2: Обработка текстовых сообщений"`

---

### Шаг 2.3: Таблица shifts в БД

**Задача:** Добавить таблицу для хранения смен.

**Действия:**
1. Обновить `database.py` — добавить в `init_db()`:
   ```python
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
   ```

2. Добавить функции:
   ```python
   async def create_shift(
       project_id: int,
       date: str,
       start_time: str,
       end_time: str,
       original_message: str,
       parsed_data: str
   ):
       """Создание новой смены"""
       # Вычисляем общее количество часов
       from datetime import datetime
       
       start = datetime.strptime(start_time, "%H:%M")
       end = datetime.strptime(end_time, "%H:%M")
       
       # Если окончание раньше начала - значит переход через полночь
       if end < start:
           end = end.replace(day=end.day + 1)
       
       total_hours = (end - start).total_seconds() / 3600
       
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
   ```

**Критерий готовности:**
- ✅ Таблица `shifts` создаётся
- ✅ Можно создать смену
- ✅ Можно подтвердить смену

**Коммит:** `git commit -m "Шаг 2.3: Таблица shifts"`

---

### Шаг 2.4: Сохранение подтверждённой смены

**Задача:** При нажатии "Подтвердить" сохранять смену в БД.

**Действия:**
1. Обновить `handlers/shifts.py`:
   ```python
   from aiogram.types import CallbackQuery
   from database import create_shift, confirm_shift
   import json
   
   # Временное хранилище распарсенных смен (в памяти)
   # TODO: В будущем использовать Redis или FSM storage
   pending_shifts = {}
   
   @router.message(F.text & ~F.text.startswith("/"))
   async def handle_text_message(message: Message):
       # ... существующий код ...
       
       # Сохраняем распарсенные данные
       pending_shifts[message.from_user.id] = {
           "result": result,
           "project_id": project["id"],
           "original_message": message.text
       }
       
       # ... показываем карточку ...
   
   @router.callback_query(F.data == "confirm_shift")
   async def confirm_shift_callback(callback: CallbackQuery):
       """Подтверждение смены"""
       if callback.from_user.id not in pending_shifts:
           await callback.answer("Данные смены не найдены", show_alert=True)
           return
       
       data = pending_shifts[callback.from_user.id]
       result = data["result"]
       
       # Создаём смену в БД
       shift_id = await create_shift(
           project_id=data["project_id"],
           date=result["date"],
           start_time=result["start_time"],
           end_time=result["end_time"],
           original_message=data["original_message"],
           parsed_data=json.dumps(result, ensure_ascii=False)
       )
       
       # Подтверждаем смену
       await confirm_shift(shift_id)
       
       # Удаляем из временного хранилища
       del pending_shifts[callback.from_user.id]
       
       await callback.message.edit_text(
           f"✅ Смена #{shift_id} подтверждена!\n\n"
           f"(Расчёт заработка будет добавлен в следующей фазе)"
       )
       await callback.answer()
   
   @router.callback_query(F.data == "cancel_shift")
   async def cancel_shift_callback(callback: CallbackQuery):
       """Отмена смены"""
       if callback.from_user.id in pending_shifts:
           del pending_shifts[callback.from_user.id]
       
       await callback.message.edit_text("❌ Смена отменена")
       await callback.answer()
   ```

**Критерий готовности:**
- ✅ При нажатии "Подтвердить" смена сохраняется
- ✅ При нажатии "Отменить" смена удаляется из памяти
- ✅ Смена имеет статус "confirmed" в БД

**Коммит:** `git commit -m "Шаг 2.4: Сохранение подтверждённых смен"`

---

**Итог Фазы 2:**
- ✅ AI-парсинг текстовых сообщений работает
- ✅ Смены сохраняются в БД
- ✅ Есть подтверждение/отмена смен

**Обновить:**
- `STATUS.md` — отметить Фазу 2 завершённой
- `CHANGELOG.md` — добавить изменения
- `NEXT_STEPS.md` — описать Фазу 3

---

## Фаза 3: Расчёт заработка

**Цель:** Реализовать автоматический расчёт заработка по смене.

**Время:** ~1 неделя

---

### Шаг 3.1: Таблицы для настроек профессии

**Задача:** Добавить таблицы `professions`, `progressive_rates`, `additional_services`.

**Действия:**
1. Обновить `database.py` — добавить в `init_db()`:
   ```python
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
           application_rule TEXT DEFAULT 'on_mention',
           linked_service_id INTEGER,
           keywords TEXT,
           FOREIGN KEY (profession_id) REFERENCES professions(id),
           FOREIGN KEY (linked_service_id) REFERENCES additional_services(id)
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
   ```

2. Добавить функции:
   ```python
   async def create_profession(
       project_id: int,
       position: str,
       base_rate_net: int,
       tax_percentage: float,
       **kwargs
   ):
       """Создание настроек профессии"""
       # Расчёт брутто из нетто
       base_rate_gross = round(base_rate_net / (1 - tax_percentage / 100))
       
       async with aiosqlite.connect(DATABASE_PATH) as db:
           cursor = await db.execute("""
               INSERT INTO professions (
                   project_id, position, base_rate_net, base_rate_gross,
                   tax_percentage, base_overtime_rate, daily_allowance,
                   base_shift_hours, break_hours, payment_schedule, conditions
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           """, (
               project_id, position, base_rate_net, base_rate_gross,
               tax_percentage, kwargs.get('base_overtime_rate', 0),
               kwargs.get('daily_allowance', 0), kwargs.get('base_shift_hours', 12),
               kwargs.get('break_hours', 12), kwargs.get('payment_schedule', 'monthly'),
               kwargs.get('conditions', '')
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
   ```

**Критерий готовности:**
- ✅ Все таблицы создаются
- ✅ Можно создать профессию
- ✅ Можно получить профессию по проекту

**Коммит:** `git commit -m "Шаг 3.1: Таблицы для настроек"`

---

### Шаг 3.2: Временное создание профессии для тестов

**Задача:** Добавить команду для быстрого создания профессии (до создания Mini App).

**Действия:**
1. Обновить `handlers/projects.py`:
   ```python
   from database import create_profession, get_profession_by_project
   
   @router.message(NewProjectStates.waiting_for_description)
   async def project_description_entered(message: Message, state: FSMContext):
       # ... существующий код создания проекта ...
       
       # Создаём базовую профессию для тестов
       profession_id = await create_profession(
           project_id=project_id,
           position="Оператор",  # Временное значение
           base_rate_net=10000,   # Временное значение
           tax_percentage=13,     # Временное значение
           base_overtime_rate=500,
           daily_allowance=1000,
           base_shift_hours=12,
           break_hours=12
       )
       
       await message.answer(
           f"✅ Проект '{data['name']}' создан!\n\n"
           f"📋 Созданы базовые настройки:\n"
           f"• Базовая ставка: 10,000 ₽\n"
           f"• Переработка: 500 ₽/ч\n"
           f"• Базовая смена: 12 ч\n\n"
           f"Теперь можете вносить смены через чат!"
       )
       
       await state.clear()
   ```

**Критерий готовности:**
- ✅ При создании проекта автоматически создаётся профессия
- ✅ Можно начать вносить смены

**Коммит:** `git commit -m "Шаг 3.2: Автосоздание профессии"`

---

### Шаг 3.3: Модуль calculator.py

**Задача:** Создать модуль для расчёта заработка.

**Действия:**
1. Создать файл `calculator.py`:
   ```python
   """
   Расчёт заработка по смене
   Статус: 🚧 В разработке
   """
   from database import get_profession_by_project
   import aiosqlite
   from config import DATABASE_PATH
   
   async def calculate_shift_earnings(shift_id: int, project_id: int):
       """
       Расчёт заработка по смене
       
       Args:
           shift_id: ID смены
           project_id: ID проекта
       
       Returns:
           dict с расчётом
       """
       # Получаем данные смены
       async with aiosqlite.connect(DATABASE_PATH) as db:
           db.row_factory = aiosqlite.Row
           async with db.execute(
               "SELECT * FROM shifts WHERE id = ?",
               (shift_id,)
           ) as cursor:
               shift = await cursor.fetchone()
       
       # Получаем настройки профессии
       profession = await get_profession_by_project(project_id)
       
       if profession is None:
           raise ValueError("Профессия не настроена для проекта")
       
       total_hours = shift["total_hours"]
       base_hours = profession["base_shift_hours"]
       
       # 1. Базовая оплата
       base_pay_net = profession["base_rate_net"]
       base_pay_gross = profession["base_rate_gross"]
       
       # 2. Переработки
       if total_hours > base_hours:
           overtime_hours = total_hours - base_hours
           overtime_pay = int(overtime_hours * profession["base_overtime_rate"])
       else:
           overtime_hours = 0
           overtime_pay = 0
       
       # Обновляем overtime_hours в смене
       async with aiosqlite.connect(DATABASE_PATH) as db:
           await db.execute(
               "UPDATE shifts SET overtime_hours = ? WHERE id = ?",
               (overtime_hours, shift_id)
           )
           await db.commit()
       
       # 3. Суточные (пока 0, будет в будущем)
       daily_allowance_pay = 0
       
       # 4. Доп. услуги (пока 0, будет в будущем)
       services_pay = 0
       
       # 5. Итого
       total_net = base_pay_net + overtime_pay + daily_allowance_pay + services_pay
       tax_percentage = profession["tax_percentage"]
       total_gross = round(total_net / (1 - tax_percentage / 100))
       
       # Детали расчёта
       calculation_details = {
           "base_hours": base_hours,
           "total_hours": total_hours,
           "overtime_hours": overtime_hours,
           "breakdown": {
               "base_pay": {
                   "net": base_pay_net,
                   "gross": base_pay_gross
               },
               "overtime": {
                   "hours": overtime_hours,
                   "rate": profession["base_overtime_rate"],
                   "total": overtime_pay
               },
               "daily_allowance": daily_allowance_pay,
               "services": services_pay
           }
       }
       
       # Сохраняем в таблицу earnings
       async with aiosqlite.connect(DATABASE_PATH) as db:
           await db.execute("""
               INSERT INTO earnings (
                   shift_id, base_pay_net, base_pay_gross,
                   overtime_pay, daily_allowance, services_pay,
                   total_net, total_gross, calculation_details
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
           """, (
               shift_id, base_pay_net, base_pay_gross,
               overtime_pay, daily_allowance_pay, services_pay,
               total_net, total_gross, str(calculation_details)
           ))
           await db.commit()
       
       return calculation_details, total_net, total_gross
   ```

2. Протестировать расчёт:
   ```python
   # test_calculator.py
   import asyncio
   from calculator import calculate_shift_earnings
   
   async def test():
       # Предполагаем, что есть смена с ID=1
       details, net, gross = await calculate_shift_earnings(
           shift_id=1,
           project_id=1
       )
       print(f"Нетто: {net} ₽")
       print(f"Брутто: {gross} ₽")
       print(f"Детали: {details}")
   
   asyncio.run(test())
   ```

**Критерий готовности:**
- ✅ Функция `calculate_shift_earnings` работает
- ✅ Расчёт сохраняется в таблицу `earnings`
- ✅ Возвращает детальный расчёт

**Коммит:** `git commit -m "Шаг 3.3: Модуль расчёта заработка"`

---

### Шаг 3.4: Автоматический расчёт при подтверждении

**Задача:** После подтверждения смены автоматически запускать расчёт.

**Действия:**
1. Обновить `handlers/shifts.py`:
   ```python
   from calculator import calculate_shift_earnings
   
   @router.callback_query(F.data == "confirm_shift")
   async def confirm_shift_callback(callback: CallbackQuery):
       # ... существующий код создания смены ...
       
       # Подтверждаем смену
       await confirm_shift(shift_id)
       
       # Запускаем расчёт
       try:
           details, total_net, total_gross = await calculate_shift_earnings(
               shift_id=shift_id,
               project_id=data["project_id"]
           )
           
           # Обновляем статус смены
           async with aiosqlite.connect(DATABASE_PATH) as db:
               await db.execute(
                   "UPDATE shifts SET status = 'calculated' WHERE id = ?",
                   (shift_id,)
               )
               await db.commit()
           
           # Формируем сообщение с расчётом
           overtime_info = ""
           if details["overtime_hours"] > 0:
               overtime_info = (
                   f"• Переработка ({details['overtime_hours']:.1f}ч): "
                   f"{details['breakdown']['overtime']['total']:,} ₽\n"
               )
           
           text = f"""✅ Смена #{shift_id} подтверждена и рассчитана!

📅 Дата: {result['date']}
⏱ Часов: {details['total_hours']:.1f} ч ({details['base_hours']} базовых + {details['overtime_hours']:.1f} переработка)

💵 Расчёт:
• Базовая ставка: {details['breakdown']['base_pay']['net']:,} ₽
{overtime_info}
💰 Итого (нетто): {total_net:,} ₽
💰 Итого (брутто): {total_gross:,} ₽"""
           
           await callback.message.edit_text(text)
           
       except Exception as e:
           await callback.message.edit_text(
               f"✅ Смена подтверждена, но ошибка расчёта:\n{str(e)}"
           )
       
       # Удаляем из временного хранилища
       del pending_shifts[callback.from_user.id]
       await callback.answer()
   ```

**Критерий готовности:**
- ✅ После подтверждения смены запускается расчёт
- ✅ Показывается детальная карточка с расчётом
- ✅ Статус смены меняется на "calculated"

**Коммит:** `git commit -m "Шаг 3.4: Автоматический расчёт"`

---

### Шаг 3.5: Прогрессивные ставки переработки

**Задача:** Реализовать расчёт с прогрессивными ставками.

**Действия:**
1. Обновить `calculator.py`:
   ```python
   async def calculate_shift_earnings(shift_id: int, project_id: int):
       # ... существующий код до переработок ...
       
       # 2. Переработки с прогрессивными ставками
       overtime_pay = 0
       overtime_breakdown = []
       
       if total_hours > base_hours:
           overtime_hours = total_hours - base_hours
           
           # Получаем прогрессивные ставки
           async with aiosqlite.connect(DATABASE_PATH) as db:
               db.row_factory = aiosqlite.Row
               async with db.execute("""
                   SELECT * FROM progressive_rates 
                   WHERE profession_id = ?
                   ORDER BY order_num
               """, (profession["id"],)) as cursor:
                   rates = await cursor.fetchall()
           
           if rates:
               # Применяем прогрессивные ставки
               remaining_hours = overtime_hours
               
               for rate in rates:
                   if remaining_hours <= 0:
                       break
                   
                   bracket_size = (rate["hours_to"] or 999) - rate["hours_from"]
                   hours_in_bracket = min(remaining_hours, bracket_size)
                   
                   bracket_pay = int(hours_in_bracket * rate["rate"])
                   overtime_pay += bracket_pay
                   
                   overtime_breakdown.append({
                       "bracket": f"{rate['hours_from']}-{rate['hours_to'] or '+'}ч",
                       "hours": hours_in_bracket,
                       "rate": rate["rate"],
                       "total": bracket_pay
                   })
                   
                   remaining_hours -= hours_in_bracket
           else:
               # Базовая ставка переработки
               overtime_pay = int(overtime_hours * profession["base_overtime_rate"])
               overtime_breakdown.append({
                   "bracket": "базовая",
                   "hours": overtime_hours,
                   "rate": profession["base_overtime_rate"],
                   "total": overtime_pay
               })
       
       # ... остальной код ...
       
       calculation_details = {
           # ...
           "breakdown": {
               # ...
               "overtime": overtime_breakdown,
               # ...
           }
       }
   ```

2. Добавить функцию для добавления прогрессивных ставок в `database.py`:
   ```python
   async def add_progressive_rate(
       profession_id: int,
       hours_from: float,
       hours_to: float or None,
       rate: int,
       order_num: int
   ):
       """Добавление прогрессивной ставки"""
       async with aiosqlite.connect(DATABASE_PATH) as db:
           await db.execute("""
               INSERT INTO progressive_rates (
                   profession_id, hours_from, hours_to, rate, order_num
               ) VALUES (?, ?, ?, ?, ?)
           """, (profession_id, hours_from, hours_to, rate, order_num))
           await db.commit()
   ```

3. Временно добавить прогрессивные ставки при создании проекта:
   ```python
   # В handlers/projects.py
   from database import add_progressive_rate
   
   # После создания профессии:
   await add_progressive_rate(profession_id, 0, 2, 500, 1)
   await add_progressive_rate(profession_id, 2, 4, 600, 2)
   await add_progressive_rate(profession_id, 4, None, 700, 3)
   ```

**Критерий готовности:**
- ✅ Прогрессивные ставки применяются к переработкам
- ✅ В карточке показывается детальный расчёт по диапазонам

**Коммит:** `git commit -m "Шаг 3.5: Прогрессивные ставки"`

---

**Итог Фазы 3:**
- ✅ Расчёт заработка работает
- ✅ Прогрессивные ставки применяются
- ✅ Результат сохраняется в БД

**Обновить:**
- `STATUS.md` — отметить Фазу 3
- `CHANGELOG.md` — изменения
- `NEXT_STEPS.md` — описать Фазу 4

---

## Фаза 4: Telegram Mini App для настройки проектов

**Цель:** Создать веб-форму для настройки проектов и профессий.

**Время:** ~1 неделя

_(Детальные шаги будут добавлены после завершения Фазы 3)_

**Основные шаги:**
1. Создание базового HTML/CSS/JS
2. Подключение Telegram Web App API
3. Форма создания проекта
4. Форма настройки профессии
5. Добавление прогрессивных ставок (динамический список)
6. Добавление доп. услуг
7. Интеграция с ботом

---

## Фаза 5: Статистика и отчёты

**Цель:** Добавить просмотр статистики и экспорт данных.

**Время:** ~3 дня

**Основные шаги:**
1. Команда `/stats`
2. Mini App со статистикой
3. Фильтры по периодам
4. Экспорт в CSV
5. Список всех смен

---

## Фаза 6: Тестирование и деплой

**Цель:** Протестировать все функции и развернуть на сервере.

**Время:** ~2 дня

**Основные шаги:**
1. Создание тестовых сценариев
2. Тестирование всех функций
3. Исправление багов
4. Настройка сервера
5. Деплой бота
6. Настройка автозапуска (systemd)
7. Настройка бэкапов БД

---

## Правила работы

### После каждого шага:

1. **Тестирование:**
   - Запустить бота
   - Проверить функционал
   - Убедиться, что ничего не сломалось

2. **Документирование:**
   - Обновить `STATUS.md`:
     ```markdown
     ## Фаза 1: Базовый бот + БД
     - [x] Шаг 1.1: Структура проекта ✅
     - [x] Шаг 1.2: База данных ✅
     - [ ] Шаг 1.3: Простой бот 🚧
     ```
   - Обновить `CHANGELOG.md`:
     ```markdown
     ## [13.01.2026] Шаг 1.2
     ### Добавлено
     - Таблица `users` в БД
     - Функции `create_user`, `get_user`
     ### Изменено
     - Обновлён `database.py`
     ```
   - Обновить `NEXT_STEPS.md`:
     ```markdown
     ## Следующий шаг: 1.3
     Создать простого бота с командой /start
     
     Что нужно сделать:
     1. Создать handlers/start.py
     2. ...
     ```

3. **Коммит:**
   ```bash
   git add .
   git commit -m "Шаг X.Y: Краткое описание"
   ```

4. **Бэкап:**
   - Скопировать весь проект
   - Или запушить в Git remote

---

## Работа в новом чате

Когда начинаешь работу в новом чате с Claude:

1. **Загрузить файлы:**
   - `STATUS.md`
   - `NEXT_STEPS.md`
   - `CHANGELOG.md`
   - Файлы кода, которые будешь менять

2. **Сказать Claude:**
   ```
   Привет! Я работаю над проектом Earnings Tracker Bot.
   Загружаю текущий статус проекта и следующий шаг.
   
   Пожалуйста, изучи STATUS.md и NEXT_STEPS.md,
   и помоги мне с текущим шагом.
   ```

3. **Claude сразу в контексте!** 🎯

---

## Контрольные точки

После каждой фазы делаем полное тестирование:

### Контрольная точка 1 (после Фазы 1):
- ✅ Бот запускается
- ✅ Можно создать пользователя
- ✅ Можно создать проект
- ✅ БД работает корректно

### Контрольная точка 2 (после Фазы 2):
- ✅ Парсинг сообщений работает
- ✅ Смены сохраняются в БД
- ✅ Можно подтвердить/отменить смену

### Контрольная точка 3 (после Фазы 3):
- ✅ Расчёт заработка корректен
- ✅ Прогрессивные ставки применяются
- ✅ Показывается детальная карточка
