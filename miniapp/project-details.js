// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;

// Расширяем на весь экран
tg.expand();

// Скрываем главную кнопку (она не нужна на этом экране)
tg.MainButton.hide();

// Получаем project_id из URL параметров
const urlParams = new URLSearchParams(window.location.search);
const projectId = urlParams.get('project_id');
const projectName = urlParams.get('project_name') || 'Проект';

// Устанавливаем название проекта
document.getElementById('project-title').textContent = `📋 ${projectName}`;

// Загрузка профессий и услуг
// TODO: В будущем загружать данные с сервера через API
// Пока отображаем заглушку

console.log('Project ID:', projectId);

// Обработчик кнопки "Добавить профессию"
document.getElementById('add-profession-btn').addEventListener('click', function() {
    // Переходим на страницу добавления профессии
    window.location.href = `add-profession.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}`;
});

// Обработчик кнопки "Добавить услугу"
document.getElementById('add-service-btn').addEventListener('click', function() {
    // Переходим на страницу добавления услуги
    window.location.href = `add-service.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}`;
});

console.log('Project Details страница загружена');