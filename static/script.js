document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram ? window.Telegram.WebApp : null;

    if (tg) {
        tg.expand();
    }

    // Переключение табов
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tabName).classList.add('active');

            if (tabName === 'profile') {
                loadProfile(tg);
            }
        });
    });

    // Обработчик формы
    const form = document.getElementById('applicationForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const fd = new FormData(form);
            const data = {
                user_id: tg?.initDataUnsafe?.user?.id || 0,
                name: fd.get('name').trim(),
                age: fd.get('age').trim(),
                family_status: fd.get('family_status').trim(),
                children: fd.get('children').trim(),
                hobbies: fd.get('hobbies').trim(),
                themes: fd.get('themes').trim(),
                goal: fd.get('goal').trim(),
                source: fd.get('source').trim()
            };

            // Простая проверка пустых полей
            for (const key in data) {
                if (key !== 'user_id' && (!data[key] || data[key] === '')) {
                    showAlert(tg, 'Заполните все поля анкеты');
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
                    showAlert(tg, 'Анкета отправлена! Ожидайте проверки.');
                    form.reset();
                    document.querySelector('.tab[data-tab="profile"]').click();
                } else {
                    showAlert(tg, json.message || 'Ошибка отправки анкеты');
                }
            } catch (err) {
                console.error('Submit error:', err);
                showAlert(tg, 'Ошибка подключения к серверу');
            }
        });
    }

    // Автозагрузка профиля, если вкладка активна
    if (document.querySelector('.tab[data-tab="profile"]').classList.contains('active')) {
        loadProfile(tg);
    }
});

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

    document.getElementById('userName').textContent = userName;
    document.getElementById('userId').textContent = userId || '—';

    if (!userId) {
        document.getElementById('statusText').textContent = 'Открыто вне Telegram';
        return;
    }

    try {
        const res = await fetch(`/api/user_status/${userId}`);
        const json = await res.json();

        const statusSpan = document.getElementById('statusText');

        if (json.success && json.application) {
            const st = json.application.status;
            let text = 'Неизвестно';
            let cls = 'status-pending';

            if (st === 'pending') { text = '⏳ Ожидает проверки'; cls = 'status-pending'; }
            else if (st === 'approved') { text = '✅ Одобрена'; cls = 'status-approved'; }
            else if (st === 'rejected') { text = '❌ Отклонена'; cls = 'status-rejected'; }

            statusSpan.textContent = text;
            statusSpan.className = cls;
        } else {
            statusSpan.textContent = 'Анкета не подана';
            statusSpan.className = 'status-pending';
        }
    } catch (err) {
        console.error('Profile load error:', err);
        const statusSpan = document.getElementById('statusText');
        statusSpan.textContent = 'Ошибка загрузки статуса';
        statusSpan.className = 'status-pending';
    }
}
