// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// Скрываем главную кнопку
tg.MainButton.hide();

// Получаем параметры из URL
const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('project_id');
const projectName = urlParams.get('project_name') || 'Проект';
const userId = urlParams.get('user_id');

console.log('📋 Детали проекта');
console.log('Project ID:', projectId);
console.log('User ID:', userId);

// API endpoint - относительный путь
const API_URL = '/api';

// Устанавливаем название проекта
document.getElementById('project-title').textContent = `📋 ${projectName}`;

// Загружаем данные проекта
loadProjectDetails();

// Обработчик кнопки "Статистика"
document.getElementById('statistics-btn').addEventListener('click', function() {
    console.log('➡️ Переход на statistics.html');
    window.location.href = 
        `statistics.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}&user_id=${userId}`;
});

// Обработчик кнопки "Добавить профессию"
document.getElementById('add-profession-btn').addEventListener('click', function() {
    console.log('➡️ Переход на add-profession.html');
    window.location.href = 
        `add-profession.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}&user_id=${userId}`;
});

// Обработчик кнопки "Добавить услугу"
document.getElementById('add-service-btn').addEventListener('click', function() {
    console.log('➡️ Переход на add-service.html');
    window.location.href = 
        `add-service.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}&user_id=${userId}`;
});

// Функция загрузки данных проекта
async function loadProjectDetails() {
    console.log('🔄 Загружаю детали проекта...');
    
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Детали загружены:', data);
        
        displayProfessions(data.profession, data.progressive_rates);
        displayServices(data.services);
        
    } catch (error) {
        console.error('❌ Ошибка загрузки деталей:', error);
        document.getElementById('professions-list').innerHTML = 
            '<p class="hint">❌ Ошибка загрузки</p>';
    }
}

// Функция отображения профессий
function displayProfessions(profession, rates) {
    const container = document.getElementById('professions-list');
    
    if (!profession) {
        container.innerHTML = '<p class="hint">Профессии еще не добавлены</p>';
        return;
    }
    
    let html = `
        <div class="profession-card">
            <h3>${profession.position}</h3>
            <div class="profession-details">
                <p><strong>Базовая ставка:</strong> ${profession.base_rate_net.toLocaleString()}₽ (нетто)</p>
                <p><strong>Базовые часы:</strong> ${profession.base_shift_hours}ч</p>
                <p><strong>Налог:</strong> ${profession.tax_percentage}%</p>
                <p><strong>Суточные:</strong> ${profession.daily_allowance.toLocaleString()}₽</p>
    `;
    
    // Прогрессивные ставки
    if (rates && rates.length > 0) {
        html += '<p><strong>Прогрессивные ставки:</strong></p><ul>';
        rates.forEach(rate => {
            const to = rate.hours_to ? `${rate.hours_to}ч` : '+';
            html += `<li>${rate.hours_from}-${to}: ${rate.rate}₽/ч</li>`;
        });
        html += '</ul>';
    }
    
    html += '</div></div>';
    
    container.innerHTML = html;
}

// Функция отображения услуг
function displayServices(services) {
    const container = document.getElementById('services-list');
    
    if (!services || services.length === 0) {
        container.innerHTML = '<p class="hint">Услуги еще не добавлены</p>';
        return;
    }
    
    let html = '';
    
    services.forEach(service => {
        html += `
            <div class="service-card">
                <h4>${service.name}</h4>
                <p>Стоимость: ${service.cost.toLocaleString()}₽ (нетто)</p>
                <p>Налог: ${service.tax_percentage}%</p>
                <p class="hint">${service.application_rule}</p>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

console.log('🚀 Страница деталей проекта готова');