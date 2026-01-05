document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram?.WebApp;

    if (tg) {
        tg.ready();
        tg.expand();
    }

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

            for (const key in data) {
                if (key !== 'user_id' && (!data[key] || data[key] === '')) {
                    showAlert(tg, '❌ Заполните все поля');
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
                    showAlert(tg, '✅ Анкета отправлена!');
                    form.reset();
                    setTimeout(() => {
                        window.location.href = '/profile';
                    }, 1500);
                } else {
                    showAlert(tg, json.message || '❌ Ошибка');
                }
            } catch (err) {
                console.error('Submit error:', err);
                showAlert(tg, '❌ Ошибка подключения');
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
