// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// Получаем параметры из URL
const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('project_id');
const projectName = urlParams.get('project_name');
const userId = urlParams.get('user_id');

console.log('💼 Добавление услуги');
console.log('Project ID:', projectId);

// API endpoint - относительный путь
const API_URL = '/api';

// Настройка главной кнопки
tg.MainButton.setText('Сохранить услугу');
tg.MainButton.show();

// Обработчик главной кнопки
tg.MainButton.onClick(async function() {
    console.log('🔵 Сохраняю услугу...');
    
    // Блокируем кнопку
    tg.MainButton.showProgress();
    
    // Собираем данные
    const serviceName = document.getElementById('service-name').value.trim();
    const serviceCost = parseInt(document.getElementById('service-cost').value) || 0;
    const serviceTax = parseFloat(document.getElementById('service-tax').value) || 15;
    const keywords = document.getElementById('keywords').value.trim();
    const applicationRule = document.getElementById('application-rule').value;
    
    // Валидация
    if (!serviceName) {
        tg.MainButton.hideProgress();
        tg.showAlert('Введите название услуги');
        return;
    }
    
    if (serviceCost <= 0) {
        tg.MainButton.hideProgress();
        tg.showAlert('Введите стоимость услуги');
        return;
    }
    
    try {
        // Формируем массив ключевых слов
        const keywordsArray = keywords ? keywords.split(',').map(k => k.trim()).filter(k => k) : [serviceName];
        
        // Формируем данные для отправки
        const data = {
            name: serviceName,
            cost: serviceCost,
            tax_percentage: serviceTax,
            application_rule: applicationRule,
            keywords: JSON.stringify(keywordsArray)
        };
        
        console.log('📤 Отправляю данные:', data);
        
        // Отправляем запрос к API
        const response = await fetch(`${API_URL}/projects/${projectId}/services`, {
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
        console.log('✅ Услуга создана:', result);
        
        // Возвращаемся на страницу проекта
        window.location.href = 
            `project-details.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}&user_id=${userId}`;
        
    } catch (error) {
        console.error('❌ Ошибка сохранения услуги:', error);
        tg.MainButton.hideProgress();
        tg.showAlert('Ошибка сохранения: ' + error.message);
    }
});

console.log('🚀 Страница добавления услуги готова');