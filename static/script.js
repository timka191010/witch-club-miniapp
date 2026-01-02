// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();

// Переключение табов
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        
        // Убрать активные классы
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        // Добавить активные классы
        tab.classList.add('active');
        document.getElementById(tabName).classList.add('active');
        
        // Загрузить данные профиля при открытии вкладки
        if (tabName === 'profile') {
            loadProfile();
        }
    });
});

// Отправка формы
document.getElementById('applicationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        user_id: tg.initDataUnsafe.user?.id || Math.floor(Math.random() * 1000000), // Fallback для теста
        name: formData.get('name'),
        age: formData.get('age'),
        family_status: formData.get('family_status'),
        children: formData.get('children'),
        hobbies: formData.get('hobbies'),
        themes: formData.get('themes'),
        goal: formData.get('goal'),
        source: formData.get('source')
    };
    
    // Проверка: все поля заполнены?
    for (let key in data) {
        if (!data[key] || data[key].trim() === '') {
            tg.showAlert(`❌ Заполните все поля!`);
            return;
        }
    }
    
    try {
        const response = await fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            tg.showAlert('✅ Анкета отправлена! Ожидайте проверки.');
            e.target.reset();
            
            // Переключиться на профиль
            document.querySelector('.tab[data-tab="profile"]').click();
        } else {
            tg.showAlert('❌ ' + result.message);
        }
    } catch (error) {
        console.error('Ошибка отправки:', error);
        tg.showAlert('❌ Ошибка подключения к серверу');
    }
});

// Загрузка профиля
async function loadProfile() {
    const userId = tg.initDataUnsafe.user?.id || 123456;
    const userName = tg.initDataUnsafe.user?.first_name || 'Пользователь';
    
    document.getElementById('userName').textContent = userName;
    document.getElementById('userId').textContent = userId;
    
    try {
        const response = await fetch(`/api/user_status/${userId}`);
        const data = await response.json();
        
        if (data.success) {
            const app = data.application;
            const statusText = {
                'pending': '⏳ Ожидает проверки',
                'approved': '✅ Одобрена',
                'rejected': '❌ Отклонена'
            }[app.status] || '❓ Неизвестно';
            
            document.querySelector('.status-pending').textContent = statusText;
            document.querySelector('.status-pending').className = `status-${app.status}`;
        } else {
            document.querySelector('.status-pending').textContent = '📝 Анкета не подана';
        }
    } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
        document.querySelector('.status-pending').textContent = '❌ Ошибка загрузки';
    }
}

// Загрузить профиль при открытии страницы
if (document.querySelector('.tab[data-tab="profile"]').classList.contains('active')) {
    loadProfile();
}

