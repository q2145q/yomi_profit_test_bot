// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// Скрываем главную кнопку (она не нужна)
tg.MainButton.hide();

// Получаем параметры из URL
const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('project_id');
const projectName = urlParams.get('project_name');
const userId = urlParams.get('user_id');

console.log('📂 Детали проекта');
console.log('Project ID:', projectId);
console.log('Project Name:', projectName);

// Устанавливаем название проекта сразу
document.getElementById('project-title').textContent = `📋 ${projectName}`;

// API endpoint - относительный путь
const API_URL = '/api';

// Загружаем детали проекта
loadProjectDetails();

// === ОБРАБОТЧИКИ КНОПОК ===

document.getElementById('add-profession-btn').addEventListener('click', function() {
    console.log('➡️ Переход на add-profession.html');
    window.location.href = 
        `add-profession.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}&user_id=${userId}`;
});

document.getElementById('add-service-btn').addEventListener('click', function() {
    console.log('➡️ Переход на add-service.html');
    window.location.href = 
        `add-service.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}&user_id=${userId}`;
});

document.getElementById('statistics-btn').addEventListener('click', function() {
    console.log('➡️ Переход на statistics.html');
    window.location.href = 
        `statistics.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}&user_id=${userId}`;
});

// === ЗАГРУЗКА ДАННЫХ ===

async function loadProjectDetails() {
    console.log('🔄 Загружаю детали проекта...');
    
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Детали загружены:', data);
        
        displayProfession(data.profession, data.progressive_rates);
        displayMeals(data.meals);
        displayServices(data.services);
        
    } catch (error) {
        console.error('❌ Ошибка загрузки деталей:', error);
        document.getElementById('professions-list').innerHTML = 
            '<p class="hint">❌ Ошибка загрузки</p>';
    }
}

// === ОТОБРАЖЕНИЕ ПРОФЕССИИ ===

function displayProfession(profession, rates) {
    const container = document.getElementById('professions-list');
    
    if (!profession) {
        container.innerHTML = '<p class="hint">Профессия еще не добавлена</p>';
        return;
    }
    
    // Формируем список прогрессивных ставок
    let ratesHtml = '';
    if (rates && rates.length > 0) {
        ratesHtml = '<p><strong>Прогрессивные ставки переработки:</strong></p><ul>';
        rates.forEach(rate => {
            const to = rate.hours_to ? `${rate.hours_to}` : '+';
            ratesHtml += `<li>${rate.hours_from}-${to}ч: ${rate.rate.toLocaleString()}₽/ч (чистыми)</li>`;
        });
        ratesHtml += '</ul>';
    }
    
    const html = `
        <div class="profession-card">
            <h3>${profession.position}</h3>
            <div class="profession-details">
                <p><strong>Базовая ставка:</strong> ${profession.base_rate_net.toLocaleString()}₽ (чистыми) / ${profession.base_rate_gross.toLocaleString()}₽ (с налогом)</p>
                <p><strong>Налог:</strong> ${profession.tax_percentage}%</p>
                <p><strong>Базовая смена:</strong> ${profession.base_shift_hours}ч</p>
                <p><strong>Разрыв между сменами:</strong> ${profession.break_hours}ч</p>
                <p><strong>Порог переработки:</strong> ${Math.round(profession.overtime_threshold * 60)} минут</p>
                <p><strong>Округление:</strong> по ${profession.overtime_rounding}ч</p>
                ${profession.daily_allowance > 0 ? `<p><strong>Суточные:</strong> ${profession.daily_allowance.toLocaleString()}₽</p>` : ''}
                ${ratesHtml}
                ${profession.conditions ? `<p><strong>Условия:</strong> ${profession.conditions}</p>` : ''}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// === ОТОБРАЖЕНИЕ ОБЕДОВ ===

function displayMeals(meals) {
    const container = document.getElementById('meals-list');
    
    // Проверяем существование контейнера
    if (!container) {
        console.error('❌ Контейнер meals-list не найден!');
        return;
    }
    
    // Проверяем данные
    if (!meals || !Array.isArray(meals) || meals.length === 0) {
        container.innerHTML = '<p class="hint">Типы обедов еще не добавлены</p>';
        return;
    }
    
    let html = '';
    
    meals.forEach(meal => {
        // Парсим keywords безопасно
        let keywordsText = '';
        if (meal.keywords) {
            try {
                const keywordsArray = JSON.parse(meal.keywords);
                keywordsText = `<p class="hint">Ключевые слова: ${keywordsArray.join(', ')}</p>`;
            } catch (e) {
                console.warn('Ошибка парсинга keywords:', e);
            }
        }
        
        html += `
            <div class="service-card">
                <h4>🍽 ${meal.name || 'Без названия'}</h4>
                <p><strong>Добавляет часов:</strong> ${meal.adds_overtime_hours || 1.0}</p>
                <p><strong>Оплата:</strong> По базовой ставке переработки</p>
                ${keywordsText}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// === ОТОБРАЖЕНИЕ УСЛУГ ===

function displayServices(services) {
    const container = document.getElementById('services-list');
    
    // Проверяем существование контейнера
    if (!container) {
        console.error('❌ Контейнер services-list не найден!');
        return;
    }
    
    // Проверяем данные
    if (!services || !Array.isArray(services) || services.length === 0) {
        container.innerHTML = '<p class="hint">Услуги еще не добавлены</p>';
        return;
    }
    
    let html = '';
    
    services.forEach(service => {
        const grossCost = Math.round(service.cost / (1 - (service.tax_percentage || 13) / 100));
        
        // Парсим keywords безопасно
        let keywordsText = '';
        if (service.keywords) {
            try {
                const keywordsArray = JSON.parse(service.keywords);
                keywordsText = `<p class="hint">Ключевые слова: ${keywordsArray.join(', ')}</p>`;
            } catch (e) {
                console.warn('Ошибка парсинга keywords:', e);
            }
        }
        
        html += `
            <div class="service-card">
                <h4>${service.name || 'Без названия'}</h4>
                <p><strong>Стоимость:</strong> ${service.cost.toLocaleString()}₽ (чистыми) / ${grossCost.toLocaleString()}₽ (с налогом)</p>
                <p><strong>Налог:</strong> ${service.tax_percentage || 13}%</p>
                <p><strong>Правило:</strong> ${service.application_rule === 'on_mention' ? 'При упоминании' : 'К каждой смене'}</p>
                ${keywordsText}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

console.log('🚀 Страница деталей проекта готова');