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

console.log('📊 Статистика проекта');
console.log('Project ID:', projectId);

// API endpoint - относительный путь
const API_URL = '/api';

// Глобальные переменные
let allShifts = []; // Все смены
let currentFilter = 'all'; // Текущий фильтр

// Устанавливаем название
document.getElementById('project-title').textContent = `📊 ${projectName}`;

// Загружаем статистику
loadStatistics();

// Обработчики кнопок фильтров
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        // Убираем active у всех кнопок
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        
        // Добавляем active к текущей
        this.classList.add('active');
        
        // Применяем фильтр
        currentFilter = this.dataset.filter;
        displayShifts(allShifts);
        
        console.log('🔍 Фильтр:', currentFilter);
    });
});

// Обработчик кнопки экспорта
document.getElementById('export-csv-btn').addEventListener('click', function() {
    console.log('📥 Экспорт в CSV...');
    
    // Открываем URL для скачивания
    const exportUrl = `${API_URL}/projects/${projectId}/export/csv`;
    
    // Создаём скрытую ссылку и кликаем
    const link = document.createElement('a');
    link.href = exportUrl;
    link.download = `${projectName.replace(/ /g, '_')}_shifts.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Показываем уведомление
    tg.showAlert('CSV файл скачивается...');
});

// Функция загрузки статистики
async function loadStatistics() {
    console.log('🔄 Загружаю статистику...');
    
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}/statistics`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Статистика загружена:', data);
        
        // Сохраняем все смены глобально
        allShifts = data.shifts;
        
        displaySummary(data.statistics);
        displayShifts(allShifts);
        
    } catch (error) {
        console.error('❌ Ошибка загрузки статистики:', error);
        document.getElementById('stats-summary').innerHTML = 
            '<p class="hint">❌ Ошибка загрузки</p>';
    }
}

// Функция отображения общей статистики
function displaySummary(stats) {
    const container = document.getElementById('stats-summary');
    
    const html = `
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">${stats.total_shifts}</div>
                <div class="stat-label">Смен</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.total_hours}</div>
                <div class="stat-label">Часов</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.total_overtime}</div>
                <div class="stat-label">Переработка</div>
            </div>
        </div>
        
        <div class="earnings-summary">
            <p><strong>💰 Заработано (нетто):</strong> ${stats.total_net.toLocaleString()}₽</p>
            <p><strong>💰 Заработано (брутто):</strong> ${stats.total_gross.toLocaleString()}₽</p>
        </div>
    `;
    
    container.innerHTML = html;
}

// Функция фильтрации смен по периоду
function filterShiftsByPeriod(shifts, filter) {
    if (filter === 'all') {
        return shifts;
    }
    
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    let daysAgo;
    
    if (filter === 'week') {
        daysAgo = 7;
    } else if (filter === 'month') {
        daysAgo = 30;
    } else {
        return shifts;
    }
    
    const cutoffDate = new Date(today);
    cutoffDate.setDate(cutoffDate.getDate() - daysAgo);
    
    return shifts.filter(shift => {
        const shiftDate = new Date(shift.date);
        return shiftDate >= cutoffDate;
    });
}

// Функция отображения списка смен
function displayShifts(shifts) {
    const container = document.getElementById('shifts-list');
    
    // Применяем фильтр
    const filteredShifts = filterShiftsByPeriod(shifts, currentFilter);
    
    if (filteredShifts.length === 0) {
        container.innerHTML = '<p class="hint">Смен за этот период нет</p>';
        return;
    }
    
    let html = '<div class="shifts-table">';
    
    filteredShifts.forEach(shift => {
        const date = new Date(shift.date).toLocaleDateString('ru-RU');
        const overtime = shift.overtime_hours > 0 
            ? `<span class="overtime-badge">+${shift.overtime_hours}ч</span>` 
            : '';
        
        html += `
            <div class="shift-row">
                <div class="shift-date">${date}</div>
                <div class="shift-time">${shift.start_time} - ${shift.end_time}</div>
                <div class="shift-hours">${shift.total_hours}ч ${overtime}</div>
                <div class="shift-earnings">${shift.total_net.toLocaleString()}₽</div>
            </div>
        `;
    });
    
    html += '</div>';
    
    container.innerHTML = html;
}

console.log('🚀 Страница статистики готова');