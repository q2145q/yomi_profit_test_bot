// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// Получаем параметры из URL
const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('project_id');
const projectName = urlParams.get('project_name');
const userId = urlParams.get('user_id');

console.log('👤 Добавление профессии');
console.log('Project ID:', projectId);

// API endpoint - относительный путь
const API_URL = '/api';

// Настройка главной кнопки
tg.MainButton.setText('Сохранить профессию');
tg.MainButton.show();

// Счётчик для диапазонов
let rateCounter = 0;

// Обработчик кнопки "Добавить диапазон"
document.getElementById('add-rate-btn').addEventListener('click', function() {
    addRateRange();
});

// Функция добавления диапазона
function addRateRange() {
    rateCounter++;
    const rateId = `rate-${rateCounter}`;
    
    const rateCard = document.createElement('div');
    rateCard.className = 'rate-card';
    rateCard.id = rateId;
    rateCard.innerHTML = `
        <div class="rate-card-header">
            <span class="rate-card-title">Диапазон ${rateCounter}</span>
            <button type="button" class="delete-btn" onclick="deleteRateRange('${rateId}')">✕</button>
        </div>
        <div class="rate-card-body">
            <div class="form-row">
                <div class="form-group">
                    <label>От (часы)</label>
                    <input type="number" class="rate-from" step="0.1" placeholder="0">
                </div>
                <div class="form-group">
                    <label>До (часы)</label>
                    <input type="number" class="rate-to" step="0.1" placeholder="2">
                    <span class="hint">Пусто = бесконечность</span>
                </div>
            </div>
            <div class="form-group">
                <label>Ставка (₽/ч нетто)</label>
                <input type="number" class="rate-value" placeholder="500">
            </div>
        </div>
    `;
    
    document.getElementById('progressive-rates-list').appendChild(rateCard);
}

// Функция удаления диапазона
function deleteRateRange(rateId) {
    const element = document.getElementById(rateId);
    if (element) {
        element.remove();
    }
}

// Делаем функцию глобальной для onclick
window.deleteRateRange = deleteRateRange;

// Обработчик главной кнопки
tg.MainButton.onClick(async function() {
    console.log('🔵 Сохраняю профессию...');
    
    // Блокируем кнопку
    tg.MainButton.showProgress();
    
    // Собираем основные данные
    const position = document.getElementById('position').value.trim();
    const baseRate = parseInt(document.getElementById('base-rate').value) || 0;
    const tax = parseFloat(document.getElementById('tax').value) || 13;
    const baseHours = parseFloat(document.getElementById('base-hours').value) || 12;
    const breakHours = parseFloat(document.getElementById('break-hours').value) || 12;
    const overtimeThreshold = parseFloat(document.getElementById('overtime-threshold').value) || 0.25;
    const overtimeRounding = parseFloat(document.getElementById('overtime-rounding').value) || 0.5;
    const dailyAllowance = parseInt(document.getElementById('daily-allowance').value) || 0;
    const conditions = document.getElementById('conditions').value.trim();
    
    // Валидация
    if (!position) {
        tg.MainButton.hideProgress();
        tg.showAlert('Введите должность');
        return;
    }
    
    if (baseRate <= 0) {
        tg.MainButton.hideProgress();
        tg.showAlert('Введите базовую ставку');
        return;
    }
    
    // Собираем прогрессивные ставки
    const rateCards = document.querySelectorAll('.rate-card');
    const rates = [];
    
    rateCards.forEach((card, index) => {
        const from = parseFloat(card.querySelector('.rate-from').value) || 0;
        const toInput = card.querySelector('.rate-to').value.trim();
        const to = toInput === '' ? null : parseFloat(toInput);
        const rate = parseInt(card.querySelector('.rate-value').value) || 0;
        
        if (rate > 0) {
            rates.push({
                hours_from: from,
                hours_to: to,
                rate: rate,
                order_num: index + 1
            });
        }
    });
    
    try {
        // Формируем данные для отправки
        const data = {
            position: position,
            base_rate_net: baseRate,
            tax_percentage: tax,
            base_shift_hours: baseHours,
            break_hours: breakHours,
            overtime_threshold: overtimeThreshold,
            overtime_rounding: overtimeRounding,
            daily_allowance: dailyAllowance,
            conditions: conditions,
            progressive_rates: rates
        };
        
        console.log('📤 Отправляю данные:', data);
        
        // Отправляем запрос к API
        const response = await fetch(`${API_URL}/projects/${projectId}/professions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Профессия создана:', result);
        
        // Возвращаемся на страницу проекта
        window.location.href = 
            `project-details.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}&user_id=${userId}`;
        
    } catch (error) {
        console.error('❌ Ошибка сохранения профессии:', error);
        tg.MainButton.hideProgress();
        tg.showAlert('Ошибка сохранения: ' + error.message);
    }
});

console.log('🚀 Страница добавления профессии готова');