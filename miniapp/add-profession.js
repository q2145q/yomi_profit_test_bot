// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;

// Расширяем на весь экран
tg.expand();

// Получаем project_id из URL
const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('project_id');

// Настройка главной кнопки
tg.MainButton.setText('Сохранить профессию');
tg.MainButton.show();

// Счётчик для уникальных ID диапазонов
let rateCounter = 0;

// Массив для хранения диапазонов
let progressiveRates = [];

// Обработчик кнопки "Добавить диапазон"
document.getElementById('add-rate-btn').addEventListener('click', function() {
    addRateRange();
});

// Функция добавления диапазона
function addRateRange() {
    rateCounter++;
    const rateId = `rate-${rateCounter}`;
    
    // Создаём HTML для диапазона
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
                    <span class="hint">Оставь пустым для "бесконечности"</span>
                </div>
            </div>
            <div class="form-group">
                <label>Ставка (₽/ч нетто)</label>
                <input type="number" class="rate-value" placeholder="500">
            </div>
        </div>
    `;
    
    // Добавляем в список
    document.getElementById('progressive-rates-list').appendChild(rateCard);
}

// Функция удаления диапазона
function deleteRateRange(rateId) {
    const element = document.getElementById(rateId);
    if (element) {
        element.remove();
    }
}

// Обработчик главной кнопки
tg.MainButton.onClick(function() {
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
    
    // Валидация основных полей
    if (!position) {
        tg.showAlert('Введите должность');
        return;
    }
    
    if (baseRate <= 0) {
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
        
        // Валидация диапазона
        if (rate <= 0) {
            tg.showAlert(`Диапазон ${index + 1}: введите ставку`);
            return;
        }
        
        if (to !== null && to <= from) {
            tg.showAlert(`Диапазон ${index + 1}: "До" должно быть больше "От"`);
            return;
        }
        
        rates.push({
            hours_from: from,
            hours_to: to,
            rate: rate,
            order_num: index + 1
        });
    });
    
    // Формируем данные для отправки
    const data = {
        action: 'add_profession',
        project_id: projectId,
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
    
    // Отправляем боту
    tg.sendData(JSON.stringify(data));
    tg.close();
});

console.log('Add Profession страница загружена');
console.log('Project ID:', projectId);