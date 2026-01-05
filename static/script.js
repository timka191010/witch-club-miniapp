document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram ? window.Telegram.WebApp : null;

    if (tg) {
        tg.expand();
    }

    // ==================== ТАБЫ ====================
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            // Убрать активные классы со всех табов и контента
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Добавить активные классы на выбранный таб и его контент
            tab.classList.add('active');
            document.getElementById(tabName).classList.add('active');

            // Загрузить профиль если открыта вкладка профиля
            if (tabName === 'profile') {
                loadProfile(tg);
            }
        });
    });

    // ==================== ФОРМА ====================
    const form = document.getElementById('applicationForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const fd = new FormData(form);
            const data = {
                user_id: tg?.initDataUnsafe?.user?.id || Math.floor(Math.random() * 1000000),
                name: fd.get('name').trim(),
                age: fd.get('age').trim(),
                family_status: fd.get('family_status').trim(),
                children: fd.get('children').trim(),
                hobbies: fd.get('hobbies').trim(),
                themes: fd.get('themes').trim(),
                goal: fd.get('goal').trim(),
                source: fd.get('source').trim()
            };

            // Проверка пустых полей
            for (const key in data) {
                if (key !== 'user_id' && (!data[key] || data[key] === '')) {
                    showAlert(tg, '❌ Заполните все поля анкеты');
                    return;
                }
            }

            try {
                const res = await fetch('/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const json = await res.json();

                if (json.success) {
                    showAlert(tg, '✅ Анкета отправлена! Ожидайте проверки.');
                    form.reset();
                    // Переключиться на вкладку профиля
                    document.querySelector('.tab[data-tab="profile"]').click();
                } else {
                    showAlert(tg, json.message || '❌ Ошибка отправки анкеты');
                }
            } catch (err) {
                console.error('Submit error:', err);
                showAlert(tg, '❌ Ошибка подключения к серверу');
            }
        });
    }

    // Загрузить профиль если вкладка уже активна при загрузке страницы
    if (document.querySelector('.tab[data-tab="profile"]')?.classList.contains('active')) {
        loadProfile(tg);
    }
});

// ==================== ФУНКЦИИ ====================

function showAlert(tg, message) {
    if (tg && tg.showAlert) {
        tg.showAlert(message);
    } else {
        alert(message);
    }
}

async function loadProfile(tg) {
    const userId = tg?.initDataUnsafe?.user?.id || 0;
    const userName = tg?.initDataUnsafe?.user?.first_name || 'Пользователь';

    console.log('Loading profile for:', { userId, userName });

    // Проверяем, существуют ли элементы
    const userNameEl = document.getElementById('userName');
    const userIdEl = document.getElementById('userId');
    const statusSpan = document.getElementById('statusText');

    if (!userNameEl || !userIdEl || !statusSpan) {
        console.error('Profile elements not found!');
        return;
    }

    // Мгновенно обновляем имя и ID
    userNameEl.textContent = userName;
    userIdEl.textContent = userId || '—';

    // Если нет Telegram user_id — показываем сообщение
    if (!userId) {
        statusSpan.textContent = '📱 Откройте в Telegram боте';
        statusSpan.className = 'status-pending';
        return;
    }

    statusSpan.textContent = '🔄 Проверяем статус...';
    statusSpan.className = 'status-pending';

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 сек таймаут

        const response = await fetch(`/api/user_status/${userId}`, {
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        const json = await response.json();
        console.log('User status response:', json);

        if (json.success) {
            if (json.application) {
                const st = json.application.status;
                let text = '', cls = 'status-pending';

                switch (st) {
                    case 'pending':
                        text = '⏳ Ожидает проверки';
                        break;
                    case 'approved':
                        text = '✅ Одобрена! Добро пожаловать!';
                        cls = 'status-approved';
                        break;
                    case 'rejected':
                        text = '❌ Отклонена';
                        cls = 'status-rejected';
                        break;
                    default:
                        text = '❓ Неизвестный статус';
                }

                statusSpan.textContent = text;
                statusSpan.className = cls;
            } else {
                statusSpan.textContent = '📝 Анкета не подана';
                statusSpan.className = 'status-pending';
            }
        } else {
            statusSpan.textContent = '⚠️ Ошибка проверки';
            statusSpan.className = 'status-rejected';
        }
    } catch (error) {
        console.error('Profile error:', error.name, error.message);
        if (error.name === 'AbortError') {
            statusSpan.textContent = '⚠️ Превышено время ожидания';
        } else {
            statusSpan.textContent = '⚠️ Ошибка загрузки';
        }
        statusSpan.className = 'status-pending';
    }
}
