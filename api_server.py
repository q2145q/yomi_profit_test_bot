"""
HTTP API сервер для Telegram Mini App
Обрабатывает запросы от Mini App и работает с БД
Также раздаёт статику из папки miniapp/
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import os
from database import (
    get_user, get_user_projects, create_project,
    get_profession_by_project, create_profession,
    add_progressive_rate, get_progressive_rates,
    add_additional_service, get_additional_services
)
import json

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
    """Получить детали проекта (профессии + услуги)"""
    try:
        # Получаем профессию
        profession = run_async(get_profession_by_project(project_id))
        
        result = {
            'project_id': project_id,
            'profession': None,
            'progressive_rates': [],
            'services': []
        }
        
        if profession:
            result['profession'] = dict(profession)
            
            # Получаем прогрессивные ставки
            rates = run_async(get_progressive_rates(profession['id']))
            result['progressive_rates'] = [dict(r) for r in rates]
            
            # Получаем услуги
            services = run_async(get_additional_services(profession['id']))
            result['services'] = [dict(s) for s in services]
        
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
    print("\n📁 Статика раздаётся из папки miniapp/")
    print("   /index.html")
    print("   /create-project.html")
    print("   /project-details.html")
    print("   и т.д.")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=8001, debug=True)