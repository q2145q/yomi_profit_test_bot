// Инициализация Telegram Web App
const tg = window.Telegram.WebApp;
tg.expand();

// Получаем user_id из URL
const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('user_id');

console.log('📋 Главная страница загружена');
console.log('User ID:', userId);

// API endpoint - относительный путь (так как статика и API на одном домене)
const API_URL = '/api';

// Скрываем главную кнопку (она не нужна)
tg.MainButton.hide();

// Загружаем проекты при открытии
loadProjects();

// Обработчик кнопки создания проекта
document.getElementById('create-project-btn').addEventListener('click', function() {
    console.log('➡️ Переход на create-project.html');
    window.location.href = `create-project.html?user_id=${userId}`;
});

// Функция загрузки проектов
async function loadProjects() {
    console.log('🔄 Загружаю проекты...');
    
    try {
        const response = await fetch(`${API_URL}/projects?user_id=${userId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Проекты загружены:', data);
        
        displayProjects(data.projects);
    } catch (error) {
        console.error('❌ Ошибка загрузки проектов:', error);
        document.getElementById('projects-list').innerHTML = 
            '<p class="hint">❌ Ошибка загрузки проектов</p>';
    }
}

// Функция отображения проектов
function displayProjects(projects) {
    const container = document.getElementById('projects-list');
    
    if (projects.length === 0) {
        container.innerHTML = '<p class="hint">У вас пока нет проектов</p>';
        return;
    }
    
    // Формируем HTML для каждого проекта
    let html = '';
    
    projects.forEach(project => {
        const isActive = project.is_active ? '🟢' : '⚫';
        const date = new Date(project.created_at).toLocaleDateString('ru-RU');
        
        html += `
            <div class="project-card" data-id="${project.id}">
                <div class="project-card-header">
                    <span class="project-status">${isActive}</span>
                    <span class="project-name">${project.name}</span>
                </div>
                <div class="project-card-body">
                    ${project.description ? `<p class="project-description">${project.description}</p>` : ''}
                    <p class="project-meta">Создан: ${date}</p>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Добавляем обработчики клика на проекты
    document.querySelectorAll('.project-card').forEach(card => {
        card.addEventListener('click', function() {
            const projectId = this.dataset.id;
            const projectName = this.querySelector('.project-name').textContent;
            
            console.log(`➡️ Открываю проект #${projectId}`);
            
            window.location.href = 
                `project-details.html?project_id=${projectId}&project_name=${encodeURIComponent(projectName)}&user_id=${userId}`;
        });
    });
}