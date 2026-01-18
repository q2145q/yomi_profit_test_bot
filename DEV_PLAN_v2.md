# План разработки v2: Улучшения и доработки

**Версия:** 2.0  
**Дата создания:** 18.01.2026  
**Статус:** 📋 Готов к реализации

---

## Обзор изменений

Этот план содержит доработки после завершения базовой версии (Фазы 0-5).

**Источник:** Замечания пользователя от 18.01.2026

**Общее время:** ~2-3 недели

```
Фаза 6: Критичные изменения логики [~1 неделя]
    ↓
Фаза 7: Учёт платежей и баланс [~1 неделя]
    ↓
Фаза 8: Улучшения UX [~3-5 дней]
```

---

## Фаза 6: Критичные изменения логики ⭐⭐⭐

**Цель:** Исправить логику обедов и терминологию

**Время:** ~1 неделя

---

### Шаг 6.1: Обеды как базовые данные

**Задача:** Текущий/поздний обед НЕ услуга, а +1 час к переработке

**Текущая проблема:**
- Обеды хранятся в `additional_services` как услуги
- Имеют фиксированную стоимость
- Не влияют на часы переработки

**Решение:**
- Создать таблицу `meal_types`
- Обеды добавляют часы к переработке
- Стоимость = прогрессивные ставки за эти часы

**Действия:**

1. **Создать таблицу `meal_types`:**
```python
# В database.py -> init_db()
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
```

2. **Создать таблицу `shift_meals` (связь смен и обедов):**
```python
await db.execute("""
    CREATE TABLE IF NOT EXISTS shift_meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shift_id INTEGER NOT NULL,
        meal_type_id INTEGER NOT NULL,
        FOREIGN KEY (shift_id) REFERENCES shifts(id),
        FOREIGN KEY (meal_type_id) REFERENCES meal_types(id)
    )
""")
```

3. **Добавить функции в `database.py`:**
```python
async def add_meal_type(profession_id, name, adds_hours=1.0, keywords=''):
    """Добавить тип обеда"""
    
async def get_meal_types(profession_id):
    """Получить типы обедов профессии"""
```

4. **Обновить `parser.py`:**
- Распознавать обеды отдельно от услуг
- Возвращать `meals: ["текущий обед", "поздний обед"]`

5. **Обновить `calculator.py`:**
```python
# Получаем обеды из parsed_data
meals = parsed_data.get("meals", [])

# Получаем типы обедов из БД
meal_types = await get_meal_types(profession_id)

# Добавляем часы к переработке
meal_hours = 0
for meal_name in meals:
    for meal_type in meal_types:
        if meal_name.lower() in meal_type["name"].lower():
            meal_hours += meal_type["adds_overtime_hours"]

# Добавляем к переработке
total_overtime_hours = base_overtime_hours + meal_hours
```

6. **Обновить `handlers/shifts.py`:**
- Показывать обеды в карточке подтверждения:
```
🍽 Обеды:
   • Текущий обед (+1ч)
   • Поздний обед (+1ч)
```

7. **Обновить Mini App:**
- Убрать обеды из формы "Добавить услугу"
- Добавить форму "Добавить тип обеда" (по аналогии с услугами)

8. **Миграция данных:**
- Перенести существующие обеды из `additional_services` в `meal_types`
- Удалить обеды из `additional_services`

**Критерий готовности:**
- ✅ Обеды хранятся в отдельной таблице
- ✅ AI распознаёт обеды отдельно
- ✅ Обеды добавляют часы к переработке
- ✅ Стоимость = прогрессивные ставки за эти часы

**Коммит:** `git commit -m "Шаг 6.1: Обеды как базовые данные (+1 час)"`

---

### Шаг 6.2: Убрать "нетто/брутто"

**Задача:** Заменить терминологию на понятную пользователю

**Замены:**
- "нетто" → "чистыми"
- "брутто" → "с налогом"
- "gross" → "с налогом"
- "net" → "чистыми"
- "tax" → "налог"

**Действия:**

1. **Обновить `handlers/shifts.py`:**
```python
# Было:
text = f"💰 Итого (нетто): {total_net:,}₽"
text += f"💰 Итого (брутто): {total_gross:,}₽"

# Стало:
text = f"💰 Итого чистыми: {total_net:,}₽"
text += f"💰 С налогом: {total_gross:,}₽"
text += f"💰 Налог: {total_gross - total_net:,}₽"
```

2. **Обновить `miniapp/add-profession.js`:**
```javascript
// Было: "Базовая ставка (нетто)"
// Стало: "Базовая ставка (чистыми)"
```

3. **Обновить все файлы Mini App:**
- `add-profession.html`
- `add-service.html`
- `project-details.js`
- `statistics.js`

4. **Обновить комментарии в коде:**
```python
# Было: base_rate_net
# Комментарий: "Базовая ставка нетто"

# Стало: base_rate_net
# Комментарий: "Базовая ставка чистыми"
```

**Критерий готовности:**
- ✅ Во всех интерфейсах нет слов "нетто/брутто"
- ✅ Везде "чистыми" / "с налогом" / "налог"

**Коммит:** `git commit -m "Шаг 6.2: Убрана терминология нетто/брутто"`

---

## Фаза 7: Учёт платежей и баланс ⭐⭐

**Цель:** Отслеживание прихода средств и задолженности

**Время:** ~1 неделя

---

### Шаг 7.1: Таблица payments и структура

**Задача:** Создать структуру для учёта платежей

**Действия:**

1. **Создать таблицу `payments`:**
```python
# В database.py -> init_db()
await db.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        date DATE NOT NULL,
        original_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
""")
```

2. **Создать таблицу `payment_allocations` (распределение платежа):**
```python
await db.execute("""
    CREATE TABLE IF NOT EXISTS payment_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        amount_clean INTEGER NOT NULL,
        amount_tax INTEGER NOT NULL,
        description TEXT,
        FOREIGN KEY (payment_id) REFERENCES payments(id)
    )
""")
```
Где `type` = 'profession' или 'service'

3. **Добавить функции в `database.py`:**
```python
async def create_payment(project_id, amount, date, original_message):
    """Создать платёж"""

async def get_project_payments(project_id):
    """Получить все платежи проекта"""

async def allocate_payment(payment_id, type, amount_clean, amount_tax, description):
    """Распределить платёж (за профессию/услуги)"""

async def get_project_balance(project_id):
    """
    Получить баланс проекта
    
    Returns:
        {
            'earned_profession_clean': int,
            'earned_profession_tax': int,
            'earned_services_clean': int,
            'earned_services_tax': int,
            'paid_total': int,
            'paid_profession': int,
            'paid_services': int,
            'balance': int,
            'debt_profession': int,
            'debt_services': int
        }
    """
```

**Критерий готовности:**
- ✅ Таблицы созданы
- ✅ Функции работают

**Коммит:** `git commit -m "Шаг 7.1: Таблицы payments"`

---

### Шаг 7.2: AI-парсинг платежей

**Задача:** Распознавать сообщения о приходе денег

**Примеры сообщений:**
- "пришло 100 000 руб проект Тест"
- "получил 50 тысяч на проект Кино"
- "100000 на Тест"

**Действия:**

1. **Создать `payment_parser.py`:**
```python
async def parse_payment_message(
    message: str,
    current_date: str,
    user_projects: list
) -> dict:
    """
    Парсинг сообщения о платеже
    
    Returns:
        {
            "amount": 100000,
            "project_name": "Тест",
            "date": "2026-01-18",
            "confidence": 0.95,
            "missing_fields": []
        }
    """
```

2. **Промпт для OpenAI:**
```python
prompt = f"""Ты — парсер сообщений о получении денег.

Текущая дата: {current_date}
Проекты пользователя: {[p['name'] for p in user_projects]}

Сообщение:
"{message}"

Верни JSON:
{{
  "amount": 100000,
  "project_name": "Тест",
  "date": "YYYY-MM-DD",
  "confidence": 0.95,
  "missing_fields": []
}}

Правила:
1. Распознавай различные форматы сумм: "100 000", "100000", "100к", "100 тысяч"
2. Ищи название проекта из списка доступных
3. Если проект не указан - missing_fields += ["project_name"]
4. Если дата не указана - используй текущую дату
"""
```

3. **Обработчик в `handlers/payments.py`:**
```python
from payment_parser import parse_payment_message

@router.message(F.text.lower().contains("пришло") | F.text.lower().contains("получил"))
async def handle_payment_message(message: Message):
    """Обработка сообщений о платежах"""
    # Парсинг
    # Если проект не указан - спросить
    # Сохранить платёж
    # Рассчитать распределение и баланс
    # Показать карточку
```

**Критерий готовности:**
- ✅ AI распознаёт суммы и проекты
- ✅ Сохраняет платежи в БД

**Коммит:** `git commit -m "Шаг 7.2: AI-парсинг платежей"`

---

### Шаг 7.3: Расчёт распределения и баланса

**Задача:** При получении платежа определить за что он пришёл

**Логика:**
1. Получить все неоплаченные смены проекта
2. Рассчитать:
   - Заработано за профессию (чистыми)
   - Налог с профессии
   - Заработано за услуги (чистыми)
   - Налог с услуг
3. Если платёж >= задолженность - закрыть всё
4. Если платёж < задолженность - распределить пропорционально

**Действия:**

1. **Создать `payment_calculator.py`:**
```python
async def calculate_payment_distribution(project_id: int, payment_amount: int):
    """
    Рассчитать распределение платежа
    
    Returns:
        {
            'total_owed_clean': int,
            'total_owed_tax': int,
            'total_owed': int,
            'profession_owed_clean': int,
            'profession_owed_tax': int,
            'services_owed_clean': int,
            'services_owed_tax': int,
            'profession_paid_clean': int,
            'profession_paid_tax': int,
            'services_paid_clean': int,
            'services_paid_tax': int,
            'balance_after': int
        }
    """
```

2. **Алгоритм распределения:**
```python
# 1. Получаем все заработанные деньги по проекту
earned_prof_clean = SUM(earnings.base_pay + earnings.overtime_pay)
earned_prof_tax = earned_prof_clean * (tax_profession / (100 - tax_profession))

earned_serv_clean = SUM(earnings.services_pay)
# Для каждой услуги свой налог!
earned_serv_tax = SUM(service_cost * (tax_service / (100 - tax_service)))

# 2. Получаем уже оплаченное
paid_total = SUM(payments.amount)

# 3. Рассчитываем долг
total_owed = (earned_prof_clean + earned_prof_tax + 
              earned_serv_clean + earned_serv_tax) - paid_total

# 4. Распределяем новый платёж
if payment_amount >= total_owed:
    # Закрываем весь долг
    profession_paid = earned_prof_clean + earned_prof_tax
    services_paid = earned_serv_clean + earned_serv_tax
    balance = payment_amount - total_owed
else:
    # Распределяем пропорционально
    prof_ratio = (earned_prof_clean + earned_prof_tax) / total_owed
    serv_ratio = (earned_serv_clean + earned_serv_tax) / total_owed
    
    profession_paid = int(payment_amount * prof_ratio)
    services_paid = int(payment_amount * serv_ratio)
    balance = 0
```

3. **Обновить обработчик:**
```python
# В handlers/payments.py
async def handle_payment_message(message: Message):
    # ... парсинг ...
    
    # Рассчитываем распределение
    distribution = await calculate_payment_distribution(project_id, amount)
    
    # Сохраняем платёж
    payment_id = await create_payment(project_id, amount, date, message.text)
    
    # Сохраняем распределение
    await allocate_payment(
        payment_id, 'profession',
        distribution['profession_paid_clean'],
        distribution['profession_paid_tax'],
        'За работу'
    )
    await allocate_payment(
        payment_id, 'service',
        distribution['services_paid_clean'],
        distribution['services_paid_tax'],
        'За услуги'
    )
    
    # Показываем карточку
    await message.answer(format_payment_card(distribution))
```

**Критерий готовности:**
- ✅ Платёж распределяется на профессию/услуги
- ✅ Учитываются разные проценты налога
- ✅ Рассчитывается баланс

**Коммит:** `git commit -m "Шаг 7.3: Расчёт распределения платежей"`

---

### Шаг 7.4: Карточка платежа и баланс на главной

**Задача:** Показывать информацию о балансе

**Действия:**

1. **Карточка подтверждения платежа:**
```python
# В handlers/payments.py
def format_payment_card(distribution):
    text = f"""✅ Платёж принят!

💵 Получено: {distribution['payment_amount']:,}₽

📊 Задолженность была:
• За работу (чистыми): {distribution['profession_owed_clean']:,}₽
• Налог: {distribution['profession_owed_tax']:,}₽
• За услуги (чистыми): {distribution['services_owed_clean']:,}₽
• Налог: {distribution['services_owed_tax']:,}₽
• ИТОГО: {distribution['total_owed']:,}₽

💰 Оплачено:
• За работу: {distribution['profession_paid_clean'] + distribution['profession_paid_tax']:,}₽
• За услуги: {distribution['services_paid_clean'] + distribution['services_paid_tax']:,}₽

"""
    
    if distribution['balance_after'] > 0:
        text += f"✅ Переплата: {distribution['balance_after']:,}₽\n"
    elif distribution['balance_after'] < 0:
        debt = abs(distribution['balance_after'])
        text += f"⚠️ Остаток долга: {debt:,}₽\n"
        text += f"   • За работу: {distribution['profession_debt']:,}₽\n"
        text += f"   • За услуги: {distribution['services_debt']:,}₽\n"
    else:
        text += "✅ Задолженность полностью погашена!\n"
    
    return text
```

2. **Баланс на главной странице Mini App:**
```javascript
// В miniapp/index.js -> displayProjects()
projects.forEach(project => {
    // Запрашиваем баланс
    const balance = await fetch(`${API_URL}/projects/${project.id}/balance`);
    
    // Добавляем в карточку
    let balanceText = '';
    if (balance.balance > 0) {
        balanceText = `<p class="project-balance positive">💰 Переплата: ${balance.balance.toLocaleString()}₽</p>`;
    } else if (balance.balance < 0) {
        const debt = Math.abs(balance.balance);
        balanceText = `<p class="project-balance negative">⚠️ Долг: ${debt.toLocaleString()}₽</p>`;
    } else {
        balanceText = `<p class="project-balance zero">✅ Баланс: 0₽</p>`;
    }
    
    // Вставляем в HTML карточки
});
```

3. **API эндпоинт баланса:**
```python
# В api_server.py
@app.route('/api/projects/<int:project_id>/balance', methods=['GET'])
def get_project_balance_api(project_id):
    balance = run_async(get_project_balance(project_id))
    return jsonify(balance)
```

**Критерий готовности:**
- ✅ При платеже показывается детальная карточка
- ✅ На главной странице виден баланс проекта

**Коммит:** `git commit -m "Шаг 7.4: Баланс на главной и карточка платежа"`

---

## Фаза 8: Улучшения UX ⭐

**Цель:** Улучшить удобство использования

**Время:** ~3-5 дней

---

### Шаг 8.1: Кнопка "Назад"

**Задача:** Добавить BackButton во все страницы Mini App

**Действия:**

1. **Обновить все JS файлы:**
```javascript
// В начале каждого файла (кроме index.js)
tg.BackButton.show();

tg.BackButton.onClick(function() {
    // Возврат на предыдущую страницу
    window.history.back();
});
```

2. **Список файлов для обновления:**
- `create-project.js`
- `project-details.js`
- `add-profession.js`
- `add-service.js`
- `statistics.js`

**Критерий готовности:**
- ✅ На всех страницах (кроме главной) есть кнопка "Назад"
- ✅ Кнопка работает корректно

**Коммит:** `git commit -m "Шаг 8.1: Кнопка Назад"`

---

### Шаг 8.2: AI понимает проект из сообщения

**Задача:** "Смена 07:00-19:00 проект Тест" → определить проект

**Действия:**

1. **Обновить промпт в `parser.py`:**
```python
prompt = f"""...

Проекты пользователя: {[p['name'] for p in user_projects]}

...

Верни JSON:
{{
  ...
  "project_name": "Тест",  # НОВОЕ ПОЛЕ
  ...
}}

Правила:
...
5. Ищи упоминание проекта в сообщении:
   - "проект Тест"
   - "на проекте Кино"
   - "работа Фильм"
   Если нашёл - верни project_name
   Если не нашёл - project_name = null
"""
```

2. **Обновить `handlers/shifts.py`:**
```python
async def handle_text_message(message: Message):
    # ... парсинг ...
    
    project = None
    
    # Если AI распознал проект
    if result.get("project_name"):
        # Ищем проект по названию
        projects = await get_user_projects(message.from_user.id)
        for p in projects:
            if result["project_name"].lower() in p["name"].lower():
                project = p
                break
        
        if not project:
            # Проект не найден
            await message.answer(
                f"🤔 Проект '{result['project_name']}' не найден.\n\n"
                f"Используем последний активный проект."
            )
    
    # Если проект не указан или не найден
    if not project:
        project = await get_active_project(message.from_user.id)
        
        if not project:
            await message.answer("У вас нет активных проектов.")
            return
        
        # Уведомляем пользователя
        await message.answer(
            f"ℹ️ Проект не указан, используем: {project['name']}"
        )
    
    # ... дальше как обычно ...
```

3. **Если несколько похожих проектов:**
```python
# Нашли несколько проектов с похожим названием
matching_projects = [p for p in projects 
                     if result["project_name"].lower() in p["name"].lower()]

if len(matching_projects) > 1:
    # Запрашиваем уточнение
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=p["name"],
            callback_data=f"select_project_{p['id']}"
        )] for p in matching_projects
    ])
    
    await message.answer(
        "Найдено несколько проектов. Выберите:",
        reply_markup=keyboard
    )
    return
```

**Критерий готовности:**
- ✅ AI распознаёт название проекта из сообщения
- ✅ Если не указан - использует последний активный (с уведомлением)
- ✅ Если несколько похожих - запрашивает уточнение

**Коммит:** `git commit -m "Шаг 8.2: AI понимает проект"`

---

### Шаг 8.3: Порог переработки в минутах

**Задача:** UI в минутах, хранение в часах

**Действия:**

1. **Обновить `add-profession.html`:**
```html
<div class="form-group">
    <label for="overtime-threshold">Порог переработки</label>
    <input type="number" id="overtime-threshold" value="15" step="5">
    <span class="hint">минут (первые не считаются)</span>
</div>
```

2. **Обновить `add-profession.js`:**
```javascript
// При отправке формы
const overtimeThresholdMinutes = parseInt(document.getElementById('overtime-threshold').value) || 15;
const overtimeThresholdHours = overtimeThresholdMinutes / 60;

// Отправляем в БД в часах
data: {
    ...
    overtime_threshold: overtimeThresholdHours
}
```

3. **При отображении существующих данных:**
```javascript
// При загрузке профессии
const thresholdHours = profession.overtime_threshold;
const thresholdMinutes = Math.round(thresholdHours * 60);

document.getElementById('overtime-threshold').value = thresholdMinutes;
```

**Критерий готовности:**
- ✅ Пользователь вводит минуты
- ✅ В БД сохраняется в часах
- ✅ При отображении конвертируется обратно в минуты

**Коммит:** `git commit -m "Шаг 8.3: Порог в минутах"`

---

### Шаг 8.4: Округление - 3 варианта

**Задача:** Выбор из списка вместо ввода числа

**Действия:**

1. **Обновить `add-profession.html`:**
```html
<div class="form-group">
    <label for="overtime-rounding">Округление переработки</label>
    <select id="overtime-rounding">
        <option value="1.0">По часам</option>
        <option value="0.5" selected>По полчаса</option>
        <option value="0.25">По 15 минут</option>
    </select>
</div>
```

2. **Обновить `add-profession.js`:**
```javascript
const overtimeRounding = parseFloat(document.getElementById('overtime-rounding').value);
```

**Критерий готовности:**
- ✅ Выбор из 3 вариантов
- ✅ Сохраняется корректно

**Коммит:** `git commit -m "Шаг 8.4: Округление - 3 варианта"`

---

### Шаг 8.5: Услуга "при другой услуге"

**Задача:** Выбор связанной услуги из существующих

**Действия:**

1. **Обновить `add-service.html`:**
```html
<div class="form-group">
    <label for="application-rule">Правило применения *</label>
    <select id="application-rule">
        <option value="on_mention">При упоминании в сообщении</option>
        <option value="every_shift">Автоматически к каждой смене</option>
        <option value="with_service">При наличии другой услуги</option>
    </select>
</div>

<!-- НОВОЕ ПОЛЕ (скрыто по умолчанию) -->
<div class="form-group" id="linked-service-group" style="display: none;">
    <label for="linked-service">Связанная услуга *</label>
    <select id="linked-service">
        <!-- Заполняется из API -->
    </select>
</div>
```

2. **Обновить `add-service.js`:**
```javascript
// Загрузить существующие услуги
const services = await fetch(`${API_URL}/projects/${projectId}/services`);

// Заполнить select
const linkedServiceSelect = document.getElementById('linked-service');
services.forEach(service => {
    const option = document.createElement('option');
    option.value = service.id;
    option.text = service.name;
    linkedServiceSelect.appendChild(option);
});

// Показать/скрыть поле при изменении правила
document.getElementById('application-rule').addEventListener('change', function() {
    const group = document.getElementById('linked-service-group');
    group.style.display = (this.value === 'with_service') ? 'block' : 'none';
});

// При отправке
const linkedServiceId = (applicationRule === 'with_service') 
    ? parseInt(document.getElementById('linked-service').value)
    : null;
```

3. **Обновить API:**
```python
# В api_server.py
@app.route('/api/projects/<int:project_id>/services', methods=['GET'])
def get_services_api(project_id):
    """Получить услуги проекта"""
    profession = run_async(get_profession_by_project(project_id))
    if not profession:
        return jsonify({'services': []})
    
    services = run_async(get_additional_services(profession['id']))
    return jsonify({'services': [dict(s) for s in services]})
```

**Критерий готовности:**
- ✅ Выбор связанной услуги из существующих
- ✅ Поле показывается только при выборе "with_service"

**Коммит:** `git commit -m "Шаг 8.5: Услуга при другой услуге"`

---

### Шаг 8.6: Команда `/export`

**Задача:** Экспорт CSV через бота (без Mini App)

**Действия:**

1. **Создать `handlers/export.py`:**
```python
from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from database import get_user_projects, get_user_shifts
import csv
from io import StringIO

router = Router()

@router.message(Command("export"))
async def cmd_export(message: Message):
    """Экспорт смен в CSV"""
    projects = await get_user_projects(message.from_user.id)
    
    if not projects:
        await message.answer("У вас нет проектов")
        return
    
    if len(projects) == 1:
        # Один проект - сразу экспортируем
        await export_project(message, projects[0]['id'], projects[0]['name'])
    else:
        # Несколько проектов - показываем кнопки выбора
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=p["name"],
                callback_data=f"export_{p['id']}"
            )] for p in projects
        ])
        
        await message.answer(
            "Выберите проект для экспорта:",
            reply_markup=keyboard
        )

@router.callback_query(F.data.startswith("export_"))
async def export_project_callback(callback: CallbackQuery):
    project_id = int(callback.data.split("_")[1])
    
    # Получаем название проекта
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT name FROM projects WHERE id = ?",
            (project_id,)
        ) as cursor:
            project = await cursor.fetchone()
    
    await export_project(callback.message, project_id, project['name'])
    await callback.answer()

async def export_project(message, project_id, project_name):
    """Генерация и отправка CSV файла"""
    # Получаем смены
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT 
                s.date, s.start_time, s.end_time,
                s.total_hours, s.overtime_hours,
                e.total_net, e.total_gross
            FROM shifts s
            LEFT JOIN earnings e ON e.shift_id = s.id
            WHERE s.project_id = ? AND s.status = 'calculated'
            ORDER BY s.date ASC
        """, (project_id,)) as cursor:
            shifts = await cursor.fetchall()
    
    # Создаём CSV
    output = StringIO()
    writer = csv.writer(output, delimiter=';')
    
    writer.writerow(['Дата', 'Начало', 'Конец', 'Часов', 'Переработка', 'Чистыми', 'С налогом'])
    
    for shift in shifts:
        writer.writerow([
            shift['date'],
            shift['start_time'],
            shift['end_time'],
            shift['total_hours'],
            shift['overtime_hours'] or 0,
            shift['total_net'] or 0,
            shift['total_gross'] or 0
        ])
    
    # Итоговая строка
    total_net = sum(s['total_net'] or 0 for s in shifts)
    total_gross = sum(s['total_gross'] or 0 for s in shifts)
    
    writer.writerow([])
    writer.writerow(['ИТОГО', '', '', '', '', total_net, total_gross])
    
    csv_data = output.getvalue()
    output.close()
    
    # Отправляем файл
    filename = f"{project_name.replace(' ', '_')}_shifts.csv"
    file = BufferedInputFile(csv_data.encode('utf-8'), filename=filename)
    
    await message.answer_document(file, caption=f"📊 Экспорт проекта: {project_name}")
```

2. **Подключить в `bot.py`:**
```python
from handlers import start, projects, shifts, miniapp, export

dp.include_router(export.router)
```

**Критерий готовности:**
- ✅ Команда `/export` работает
- ✅ Если один проект - экспортирует сразу
- ✅ Если несколько - показывает выбор
- ✅ CSV файл отправляется в чат

**Коммит:** `git commit -m "Шаг 8.6: Команда /export"`

---

## Контрольные точки

### Контрольная точка 1 (после Фазы 6):
- ✅ Обеды работают как +1 час переработки
- ✅ Нет терминов "нетто/брутто"
- ✅ Все существующие смены пересчитаны

### Контрольная точка 2 (после Фазы 7):
- ✅ Можно внести платёж через чат
- ✅ Платёж распределяется на профессию/услуги
- ✅ Баланс показывается на главной
- ✅ Показывается задолженность

### Контрольная точка 3 (после Фазы 8):
- ✅ Все страницы имеют кнопку "Назад"
- ✅ AI понимает проект из сообщения
- ✅ Все улучшения UX работают
- ✅ Команда `/export` работает

---

## Порядок реализации

**Рекомендуемый порядок:**
1. Шаг 6.1 (обеды) - САМОЕ ВАЖНОЕ
2. Шаг 6.2 (терминология)
3. Шаг 7.1-7.4 (платежи и баланс) - всё вместе
4. Шаг 8.1-8.6 (улучшения UX) - по одному

**Время на каждый шаг:**
- Шаг 6.1: ~2-3 дня (сложный)
- Шаг 6.2: ~1 день (простой)
- Фаза 7: ~1 неделя (средней сложности)
- Фаза 8: ~3-5 дней (простые задачи)

---

**Готовы начинать! 🚀**
