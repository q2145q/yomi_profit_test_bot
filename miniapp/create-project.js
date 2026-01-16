// Проверка что Telegram WebApp доступен
if (!window.Telegram || !window.Telegram.WebApp) {
    alert('ОШИБКА: Telegram WebApp не найден!');
    document.body.innerHTML = '<h1 style="color:red;">Ошибка: запустите из Telegram!</h1>';
} else {
    alert('✅ Telegram WebApp найден!');
    
    // Инициализация Telegram Web App
    const tg = window.Telegram.WebApp;
    
    alert('✅ Расширяем окно...');
    tg.expand();
    
    alert('✅ Настраиваем кнопку...');
    tg.MainButton.setText('Сохранить проект');
    tg.MainButton.show();
    
    alert('✅ Всё готово! Заполните форму.');
    
    // Обработчик нажатия на главную кнопку
    tg.MainButton.onClick(function() {
        alert('🔵 КНОПКА НАЖАТА!');
        
        // Собираем данные
        const projectName = document.getElementById('project-name').value.trim();
        const projectDescription = document.getElementById('project-description').value.trim();
        
        // Валидация
        if (!projectName) {
            alert('❌ Введите название!');
            tg.showAlert('Введите название проекта');
            return;
        }
        
        alert('✅ Название: ' + projectName);
        
        // Отправляем данные боту
        const data = {
            action: 'create_project',
            project_name: projectName,
            project_description: projectDescription
        };
        
        alert('📤 Отправляю данные боту...');
        
        tg.sendData(JSON.stringify(data));
        
        alert('🚪 Закрываю Mini App...');
        
        tg.close();
    });
}

console.log('Create Project страница загружена');