"""
HTTP API сервер для Telegram Mini App
Обрабатывает запросы от Mini App и работает с БД
Также раздаёт статику из папки miniapp/
"""
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import asyncio
import os
from database import (
    get_user, get_user_projects, create_project,
    get_profession_by_project, create_profession,
    add_progressive_rate, get_progressive_rates,
    add_additional_service, get_additional_services,
    get_meal_types, add_meal_type  # НОВОЕ!
)
import json
import aiosqlite
import csv
from io import StringIO
from urllib.parse import quote

# Путь к папке со статикой
MINIAPP_DIR = os.path.join(os.path.dirname(__file__), 'miniapp')

app = Flask(__name__, static_folder=MINIAPP_DIR, static_url_path='')
CORS(app)  # Разрешаем запросы от Mini App

# ============================================================
# СТАТИКА
# ============================================================

@app.route('/')
def index():
    """Главная страница"""
    return send_from_directory(MINIAPP_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Раздача статических файлов из miniapp/"""
    # Если запрос к API - пропускаем
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    return send_from_directory(MINIAPP_DIR, path)

# Хелпер для запуска async функций
def run_async(coro):
    """Запускает async функцию в sync контексте"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# ============================================================
# ПРОЕКТЫ
# ============================================================

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Получить список проектов пользователя"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        # Проверяем пользователя
        user = run_async(get_user(user_id))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Получаем проекты
        projects = run_async(get_user_projects(user_id))
        
        # Конвертируем Row в dict
        projects_list = [dict(p) for p in projects]
        
        return jsonify({'projects': projects_list})
    
    except Exception as e:
        print(f"❌ Ошибка get_projects: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects', methods=['POST'])
def create_project_api():
    """Создать новый проект"""
    data = request.json
    
    user_id = data.get('user_id')
    name = data.get('name')
    description = data.get('description', '')
    
    if not user_id or not name:
        return jsonify({'error': 'user_id and name required'}), 400
    
    try:
        # Создаём проект
        project_id = run_async(create_project(user_id, name, description))
        
        print(f"✅ Проект создан через API: ID={project_id}, Название={name}")
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'name': name
        })
    
    except Exception as e:
        print(f"❌ Ошибка create_project: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project_details(project_id):
    """Получить детали проекта (профессии + услуги + ОБЕДЫ)"""
    try:
        # Получаем профессию
        profession = run_async(get_profession_by_project(project_id))
        
        result = {
            'project_id': project_id,
            'profession': None,
            'progressive_rates': [],
            'services': [],
            'meals': []  # НОВОЕ!
        }
        
        if profession:
            result['profession'] = dict(profession)
            
            # Получаем прогрессивные ставки
            rates = run_async(get_progressive_rates(profession['id']))
            result['progressive_rates'] = [dict(r) for r in rates]
            
            # Получаем услуги
            services = run_async(get_additional_services(profession['id']))
            result['services'] = [dict(s) for s in services]
            
            # === НОВОЕ: Получаем типы обедов ===
            meals = run_async(get_meal_types(profession['id']))
            result['meals'] = [dict(m) for m in meals]
            # === КОНЕЦ НОВОГО ===
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Ошибка get_project_details: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================
# ПРОФЕССИИ
# ============================================================

@app.route('/api/projects/<int:project_id>/professions', methods=['POST'])
def add_profession_api(project_id):
    """Добавить профессию к проекту"""
    data = request.json
    
    try:
        # Создаём профессию
        profession_id = run_async(create_profession(
            project_id=project_id,
            position=data['position'],
            base_rate_net=data['base_rate_net'],
            tax_percentage=data['tax_percentage'],
            base_overtime_rate=data.get('base_overtime_rate', 0),
            daily_allowance=data.get('daily_allowance', 0),
            base_shift_hours=data.get('base_shift_hours', 12),
            break_hours=data.get('break_hours', 12),
            payment_schedule=data.get('payment_schedule', 'monthly'),
            conditions=data.get('conditions', ''),
            overtime_rounding=data.get('overtime_rounding', 0),
            overtime_threshold=data.get('overtime_threshold', 0)
        ))
        
        print(f"✅ Профессия создана: ID={profession_id}, Должность={data['position']}")
        
        # Добавляем прогрессивные ставки
        rates = data.get('progressive_rates', [])
        for rate in rates:
            run_async(add_progressive_rate(
                profession_id=profession_id,
                hours_from=rate['hours_from'],
                hours_to=rate.get('hours_to'),
                rate=rate['rate'],
                order_num=rate['order_num']
            ))
        
        print(f"✅ Добавлено {len(rates)} прогрессивных ставок")
        
        # === НОВОЕ: Добавляем типы обедов ===
        meals = data.get('meals', [])
        for meal in meals:
            run_async(add_meal_type(
                profession_id=profession_id,
                name=meal['name'],
                adds_hours=meal['adds_hours'],
                keywords=meal['keywords']
            ))
        
        print(f"✅ Добавлено {len(meals)} типов обедов")
        # === КОНЕЦ НОВОГО ===
        
        return jsonify({
            'success': True,
            'profession_id': profession_id
        })
    
    except Exception as e:
        print(f"❌ Ошибка add_profession: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================
# УСЛУГИ
# ============================================================

@app.route('/api/projects/<int:project_id>/services', methods=['POST'])
def add_service_api(project_id):
    """Добавить услугу к проекту"""
    data = request.json
    
    try:
        # Получаем профессию проекта
        profession = run_async(get_profession_by_project(project_id))
        
        if not profession:
            return jsonify({'error': 'Profession not found for project'}), 404
        
        # Создаём услугу
        service_id = run_async(add_additional_service(
            profession_id=profession['id'],
            name=data['name'],
            cost=data['cost'],
            tax_percentage=data.get('tax_percentage', 13),
            application_rule=data.get('application_rule', 'on_mention'),
            keywords=data.get('keywords', '')
        ))
        
        print(f"✅ Услуга создана: ID={service_id}, Название={data['name']}")
        
        return jsonify({
            'success': True,
            'service_id': service_id
        })
    
    except Exception as e:
        print(f"❌ Ошибка add_service: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================
# СТАТИСТИКА
# ============================================================

@app.route('/api/projects/<int:project_id>/statistics', methods=['GET'])
def get_project_statistics(project_id):
    """Получить статистику по проекту"""
    try:
        # Получаем все смены проекта с заработком
        async def fetch_stats():
            async with aiosqlite.connect('data.db') as db:
                db.row_factory = aiosqlite.Row
                
                # Статистика по сменам
                async with db.execute("""
                    SELECT 
                        COUNT(*) as total_shifts,
                        SUM(total_hours) as total_hours,
                        SUM(overtime_hours) as total_overtime
                    FROM shifts
                    WHERE project_id = ? AND status = 'calculated'
                """, (project_id,)) as cursor:
                    stats = await cursor.fetchone()
                
                # Статистика по заработку
                async with db.execute("""
                    SELECT 
                        SUM(e.total_net) as total_net,
                        SUM(e.total_gross) as total_gross
                    FROM earnings e
                    JOIN shifts s ON e.shift_id = s.id
                    WHERE s.project_id = ?
                """, (project_id,)) as cursor:
                    earnings = await cursor.fetchone()
                
                # Список смен с заработком
                async with db.execute("""
                    SELECT 
                        s.id,
                        s.date,
                        s.start_time,
                        s.end_time,
                        s.total_hours,
                        s.overtime_hours,
                        e.total_net,
                        e.total_gross
                    FROM shifts s
                    LEFT JOIN earnings e ON e.shift_id = s.id
                    WHERE s.project_id = ? AND s.status = 'calculated'
                    ORDER BY s.date DESC, s.created_at DESC
                """, (project_id,)) as cursor:
                    shifts = await cursor.fetchall()
                
                return stats, earnings, shifts
        
        stats, earnings, shifts = run_async(fetch_stats())
        
        result = {
            'project_id': project_id,
            'statistics': {
                'total_shifts': stats['total_shifts'] or 0,
                'total_hours': round(stats['total_hours'] or 0, 1),
                'total_overtime': round(stats['total_overtime'] or 0, 1),
                'total_net': earnings['total_net'] or 0,
                'total_gross': earnings['total_gross'] or 0
            },
            'shifts': [dict(s) for s in shifts]
        }
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Ошибка get_project_statistics: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================
# ЭКСПОРТ В CSV
# ============================================================

@app.route('/api/projects/<int:project_id>/export/csv', methods=['GET'])
def export_project_csv(project_id):
    """Экспорт смен проекта в CSV"""
    try:
        # Получаем название проекта
        async def fetch_project_name():
            async with aiosqlite.connect('data.db') as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT name FROM projects WHERE id = ?",
                    (project_id,)
                ) as cursor:
                    project = await cursor.fetchone()
                    return project['name'] if project else f"Проект {project_id}"
        
        project_name = run_async(fetch_project_name())
        
        # Получаем смены
        async def fetch_shifts():
            async with aiosqlite.connect('data.db') as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT 
                        s.date,
                        s.start_time,
                        s.end_time,
                        s.total_hours,
                        s.overtime_hours,
                        e.total_net,
                        e.total_gross
                    FROM shifts s
                    LEFT JOIN earnings e ON e.shift_id = s.id
                    WHERE s.project_id = ? AND s.status = 'calculated'
                    ORDER BY s.date ASC
                """, (project_id,)) as cursor:
                    return await cursor.fetchall()
        
        shifts = run_async(fetch_shifts())
        
        # Создаём CSV в памяти
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Заголовок
        writer.writerow([
            'Дата',
            'Начало',
            'Конец',
            'Часов',
            'Переработка',
            'Заработок (чистыми)',
            'Заработок (с налогом)'
        ])
        
        # Данные
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
        total_hours = sum(s['total_hours'] or 0 for s in shifts)
        total_overtime = sum(s['overtime_hours'] or 0 for s in shifts)
        
        writer.writerow([])
        writer.writerow([
            'ИТОГО',
            '',
            '',
            total_hours,
            total_overtime,
            total_net,
            total_gross
        ])
        
        # Возвращаем CSV как файл для скачивания
        csv_data = output.getvalue()
        output.close()
        
        # Генерируем имя файла
        filename = f"{project_name.replace(' ', '_')}_shifts.csv"
        # Кодируем имя файла для заголовка (RFC 5987)
        filename_encoded = quote(filename)
        
        print(f"✅ Экспорт в CSV: проект #{project_id}, смен: {len(shifts)}")
        
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f"attachment; filename=\"project_shifts.csv\"; filename*=UTF-8''{filename_encoded}",
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
    
    except Exception as e:
        print(f"❌ Ошибка export_csv: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================
# ЗАПУСК СЕРВЕРА
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 API сервер запущен на http://localhost:8001")
    print("📡 API эндпоинты:")
    print("   GET  /api/projects?user_id=XXX")
    print("   POST /api/projects")
    print("   GET  /api/projects/<id>")
    print("   POST /api/projects/<id>/professions")
    print("   POST /api/projects/<id>/services")
    print("   GET  /api/projects/<id>/statistics")
    print("   GET  /api/projects/<id>/export/csv")
    print("\n📁 Статика раздаётся из папки miniapp/")
    print("   /index.html")
    print("   /create-project.html")
    print("   /project-details.html")
    print("   /statistics.html")
    print("   и т.д.")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=8001, debug=True)