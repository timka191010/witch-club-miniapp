document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram?.WebApp;

    if (tg) {
        tg.ready();
        tg.expand();
    }

    console.log('Page loaded, Telegram WebApp:', tg);

    // ==================== ФОРМА АНКЕТЫ ====================
    const form = document.getElementById('applicationForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const fd = new FormData(form);
            const user = tg?.initDataUnsafe?.user;
            const userId = user?.id || Math.floor(Math.random() * 1000000);

            const data = {
                user_id: userId,
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
                    showAlert(tg, '✅ Анкета отправлена! Проверьте статус в разделе Профиль.');
                    form.reset();
                    // Редирект на профиль
                    setTimeout(() => {
                        window.location.href = '/profile';
                    }, 1500);
                } else {
                    showAlert(tg, json.message || '❌ Ошибка отправки анкеты');
                }
            } catch (err) {
                console.error('Submit error:', err);
                showAlert(tg, '❌ Ошибка подключения к серверу');
            }
        });
    }
});

function showAlert(tg, message) {
    if (tg && tg.showAlert) {
        tg.showAlert(message);
    } else {
        alert(message);
    }
}
