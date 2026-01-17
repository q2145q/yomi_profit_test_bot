// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// Получаем user_id из URL
const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('user_id');

console.log('📝 Создание проекта');
console.log('User ID:', userId);

// API endpoint - относительный путь
const API_URL = '/api';

// Настройка главной кнопки
tg.MainButton.setText('Создать проект');
tg.MainButton.show();

// Обработчик главной кнопки
tg.MainButton.onClick(async function() {
    console.log('🔵 Создаю проект...');
    
    // Блокируем кнопку
    tg.MainButton.showProgress();
    
    // Собираем данные
    const projectName = document.getElementById('project-name').value.trim();
    const projectDescription = document.getElementById('project-description').value.trim();
    
    // Валидация
    if (!projectName) {
        tg.MainButton.hideProgress();
        tg.showAlert('Введите название проекта');
        return;
    }
    
    try {
        // Отправляем запрос к API
        const response = await fetch(`${API_URL}/projects`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: parseInt(userId),
                name: projectName,
                description: projectDescription
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Проект создан:', data);
        
        // Переходим на страницу проекта БЕЗ закрытия Mini App
        window.location.href = 
            `project-details.html?project_id=${data.project_id}&project_name=${encodeURIComponent(data.name)}&user_id=${userId}`;
        
    } catch (error) {
        console.error('❌ Ошибка создания проекта:', error);
        tg.MainButton.hideProgress();
        tg.showAlert('Ошибка создания проекта: ' + error.message);
    }
});

console.log('🚀 Страница создания проекта готова');