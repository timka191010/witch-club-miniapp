from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from datetime import datetime
from functools import wraps
import json
import os

app = Flask(__name__)
app.secret_key = 'witch_club_secret_2024'

RESPONSES_FILE = 'applications.json'
MEMBERS_FILE = 'members.json'
ADMIN_PASSWORD = 'ведьмы123'

# ===================== ФУНКЦИИ ДАННЫХ =====================

def load_applications():
    if os.path.exists(RESPONSES_FILE):
        try:
            with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_applications(apps):
    with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(apps, f, ensure_ascii=False, indent=2)

def load_members():
    if os.path.exists(MEMBERS_FILE):
        try:
            with open(MEMBERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_members(members):
    with open(MEMBERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ===================== ГЛАВНАЯ СТРАНИЦА =====================

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👑 Ведьмы Не Стареют</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #e0e0e0;
        }
        .container {
            max-width: 500px;
            width: 100%;
            background: rgba(30, 20, 50, 0.9);
            border: 2px solid #8b7bb8;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        h1 { font-size: 28px; margin-bottom: 10px; color: #ffd700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
        .tagline { font-size: 14px; color: #b19cd9; font-style: italic; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-size: 14px; color: #c4a7d6; font-weight: bold; }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #6b5b95;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            color: #e0e0e0;
            font-family: inherit;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #ffd700;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
            background: rgba(255, 255, 255, 0.1);
        }
        textarea { resize: vertical; min-height: 80px; }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #ffd700, #ffed4e);
            color: #1a1a1a;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.5); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .success-message { display: none; text-align: center; color: #4ade80; padding: 20px; background: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; border-radius: 8px; margin-bottom: 20px; }
        .error-message { display: none; text-align: center; color: #ef4444; padding: 20px; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; margin-bottom: 20px; }
        .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #8b7bb8; }
    </style>
</head>
<body>
    <div class="container">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1>👑 Ведьмы Не Стареют 👑</h1>
            <p class="tagline">Священный клуб магических сестёр</p>
        </div>

        <div class="success-message" id="successMsg">
            ✅ Ваша заявка успешно отправлена!<br>
            Спасибо за интерес. Мы свяжемся с вами вскоре.
        </div>

        <div class="error-message" id="errorMsg"></div>

        <form id="surveyForm">
            <div class="form-group">
                <label>📝 Имя *</label>
                <input type="text" name="name" placeholder="Как вас зовут?" required>
            </div>

            <div class="form-group">
                <label>💬 Telegram @</label>
                <input type="text" name="telegramUsername" placeholder="username (без @)">
            </div>

            <button type="submit">✨ Отправить ✨</button>
        </form>

        <div class="footer">
            <p>🔮 Добро пожаловать в наш священный круг 🔮</p>
        </div>
    </div>

    <script>
        document.getElementById('surveyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = document.querySelector('input[name="name"]').value;
            const telegramUsername = document.querySelector('input[name="telegramUsername"]').value;

            try {
                const response = await fetch('/api/survey', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, telegramUsername })
                });

                if (response.ok) {
                    document.getElementById('surveyForm').reset();
                    document.getElementById('successMsg').style.display = 'block';
                } else {
                    const error = await response.json();
                    document.getElementById('errorMsg').textContent = '❌ Ошибка: ' + (error.error || 'Попробуйте позже');
                    document.getElementById('errorMsg').style.display = 'block';
                }
            } catch (error) {
                document.getElementById('errorMsg').textContent = '❌ Ошибка подключения';
                document.getElementById('errorMsg').style.display = 'block';
            }
        });
    </script>
</body>
</html>'''

# ===================== API ENDPOINTS =====================

@app.route('/api/survey', methods=['POST'])
def survey():
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Имя обязательно'}), 400
        
        application = {
            'id': len(load_applications()) + 1,
            'timestamp': datetime.now().isoformat(),
            'name': data.get('name', '').strip(),
            'telegramUsername': data.get('telegramUsername', '').strip(),
            'status': 'pending',
            'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        applications = load_applications()
        applications.append(application)
        save_applications(applications)
        
        return jsonify({'success': True, 'message': 'Спасибо! Ваша заявка принята.'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@app.route('/api/responses', methods=['GET'])
def get_responses():
    try:
        applications = load_applications()
        return jsonify({'success': True, 'count': len(applications), 'responses': applications}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        applications = load_applications()
        members = load_members()
        
        stats = {
            'total': len(applications),
            'approved': len([a for a in applications if a.get('status') == 'approved']),
            'pending': len([a for a in applications if a.get('status') == 'pending']),
            'rejected': len([a for a in applications if a.get('status') == 'rejected']),
            'membersCount': len(members)
        }
        
        return jsonify({'success': True, 'stats': stats}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Witch Club API running'}), 200

# ===================== АДМИНКА =====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template_string('''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход Админ</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .login-container {
            max-width: 420px;
            width: 90%;
            padding: 40px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 { text-align: center; margin-bottom: 10px; font-size: 28px; color: #FFD700; }
        .subtitle { text-align: center; color: rgba(255, 255, 255, 0.6); margin-bottom: 30px; font-size: 14px; }
        input {
            width: 100%;
            padding: 15px 20px;
            margin-bottom: 15px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            color: white;
            font-size: 16px;
        }
        input:focus { outline: none; background: rgba(255, 255, 255, 0.15); border-color: #FFD700; }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #8B008B, #4B0082);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        button:hover { transform: translateY(-2px); }
        .error { background: rgba(255, 68, 68, 0.15); border: 1px solid rgba(255, 68, 68, 0.3); color: #ff6b6b; padding: 12px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>👑 Админка</h1>
        <p class="subtitle">Вход в панель управления</p>
        <div class="error">Неверный пароль</div>
        <form method="POST">
            <input type="password" name="password" placeholder="Пароль" required>
            <button type="submit">Войти</button>
        </form>
    </div>
</body>
</html>''', error=True)
    
    return render_template_string('''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход Админ</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .login-container {
            max-width: 420px;
            width: 90%;
            padding: 40px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 { text-align: center; margin-bottom: 10px; font-size: 28px; color: #FFD700; }
        .subtitle { text-align: center; color: rgba(255, 255, 255, 0.6); margin-bottom: 30px; font-size: 14px; }
        input {
            width: 100%;
            padding: 15px 20px;
            margin-bottom: 15px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            color: white;
            font-size: 16px;
        }
        input:focus { outline: none; background: rgba(255, 255, 255, 0.15); border-color: #FFD700; }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #8B008B, #4B0082);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        button:hover { transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>👑 Админка</h1>
        <p class="subtitle">Вход в панель управления</p>
        <form method="POST">
            <input type="password" name="password" placeholder="Пароль" required>
            <button type="submit">Войти</button>
        </form>
    </div>
</body>
</html>''')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    applications = load_applications()
    members = load_members()
    
    return render_template_string('''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Панель Администратора</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a0033, #330066);
            color: white;
            padding: 20px;
        }
        .admin-container { max-width: 1200px; margin: 0 auto; }
        .admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .header-buttons { display: flex; gap: 10px; }
        .btn { padding: 10px 20px; border: none; border-radius: 8px; color: white; text-decoration: none; cursor: pointer; }
        .logout-btn { background: #ff4444; }
        .logout-btn:hover { background: #cc0000; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; text-align: center; }
        .stat-number { font-size: 36px; font-weight: bold; color: #FFD700; }
        .stat-label { font-size: 14px; color: rgba(255, 255, 255, 0.8); margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; background: rgba(255, 255, 255, 0.05); border-radius: 10px; overflow: hidden; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        th { background: rgba(255, 255, 255, 0.1); font-weight: bold; }
        tr:hover { background: rgba(255, 255, 255, 0.05); }
        .status { padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
        .status-pending { background: rgba(255, 165, 0, 0.2); color: #FFA500; }
        .status-approved { background: rgba(0, 255, 0, 0.2); color: #00FF00; }
        .status-rejected { background: rgba(255, 68, 68, 0.2); color: #FF4444; }
    </style>
</head>
<body>
    <div class="admin-container">
        <div class="admin-header">
            <h1>👑 Панель Управления</h1>
            <div class="header-buttons">
                <a href="/admin/logout" class="btn logout-btn">Выход</a>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ total }}</div>
                <div class="stat-label">Всего заявок</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ approved }}</div>
                <div class="stat-label">Одобрено</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ pending }}</div>
                <div class="stat-label">На рассмотрении</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ members_count }}</div>
                <div class="stat-label">Участниц</div>
            </div>
        </div>

        <h2>📋 Заявки</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Имя</th>
                    <th>Telegram</th>
                    <th>Статус</th>
                    <th>Дата</th>
                </tr>
            </thead>
            <tbody>
                {% for app in applications %}
                <tr>
                    <td>{{ app.id }}</td>
                    <td>{{ app.name }}</td>
                    <td>@{{ app.telegramUsername }}</td>
                    <td><span class="status status-{{ app.status }}">{{ app.status }}</span></td>
                    <td>{{ app.createdAt }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>''', 
    total=len(applications),
    approved=len([a for a in applications if a.get('status') == 'approved']),
    pending=len([a for a in applications if a.get('status') == 'pending']),
    members_count=len(members),
    applications=applications
    )

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
