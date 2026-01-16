// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;

// Расширяем приложение на весь экран
tg.expand();

// Получаем данные пользователя
const user = tg.initDataUnsafe?.user;

console.log('Telegram Web App инициализирован');
console.log('Пользователь:', user);

// Настройка главной кнопки
tg.MainButton.setText('Сохранить проект');
tg.MainButton.show();

// Обработчик нажатия на главную кнопку
tg.MainButton.onClick(function() {
    // Собираем данные из формы
    const formData = collectFormData();
    
    // Проверяем обязательные поля
    const validation = validateForm(formData);
    
    if (!validation.valid) {
        tg.showAlert('Заполните обязательные поля: ' + validation.missing.join(', '));
        return;
    }
    
    // Отправляем данные боту
    tg.sendData(JSON.stringify(formData));
    
    // Закрываем Mini App
    tg.close();
});

// Функция сбора данных из формы
function collectFormData() {
    return {
        // Общая информация
        project_name: document.getElementById('project-name').value.trim(),
        project_description: document.getElementById('project-description').value.trim(),
        
        // Настройка профессии
        position: document.getElementById('position').value.trim(),
        base_rate_net: parseInt(document.getElementById('base-rate').value) || 0,
        tax_percentage: parseFloat(document.getElementById('tax').value) || 13,
        base_shift_hours: parseFloat(document.getElementById('base-hours').value) || 12,
        break_hours: parseFloat(document.getElementById('break-hours').value) || 12,
        overtime_threshold: parseFloat(document.getElementById('overtime-threshold').value) || 0.25,
        overtime_rounding: parseFloat(document.getElementById('overtime-rounding').value) || 0.5,
        daily_allowance: parseInt(document.getElementById('daily-allowance').value) || 0,
        conditions: document.getElementById('conditions').value.trim(),
        
        // TODO: Прогрессивные ставки (будут в следующем шаге)
        progressive_rates: [],
        
        // TODO: Дополнительные услуги (будут в следующем шаге)
        services: []
    };
}

// Функция валидации формы
function validateForm(data) {
    const required = [];
    
    if (!data.project_name) required.push('Название проекта');
    if (!data.position) required.push('Должность');
    if (data.base_rate_net <= 0) required.push('Базовая ставка');
    if (data.base_shift_hours <= 0) required.push('Базовые часы');
    
    return {
        valid: required.length === 0,
        missing: required
    };
}

// Автоматический расчёт брутто при вводе нетто
document.getElementById('base-rate').addEventListener('input', function() {
    const net = parseFloat(this.value) || 0;
    const tax = parseFloat(document.getElementById('tax').value) || 13;
    const gross = Math.round(net / (1 - tax / 100));
    
    console.log(`Нетто: ${net}₽ → Брутто: ${gross}₽`);
});

// Автоматический пересчёт брутто при изменении налога
document.getElementById('tax').addEventListener('input', function() {
    const net = parseFloat(document.getElementById('base-rate').value) || 0;
    const tax = parseFloat(this.value) || 13;
    const gross = Math.round(net / (1 - tax / 100));
    
    console.log(`Налог изменён на ${tax}%. Брутто: ${gross}₽`);
});