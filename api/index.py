from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from datetime import datetime
from functools import wraps
import json
import os
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'witch_club_secret_2025'

# Files
SURVEYS_FILE = 'surveys.json'
MEMBERS_FILE = 'members.json'
ADMIN_PASSWORD = 'ведьмы123'

# Lists
EMOJIS = ['🔮', '🌙', '🧿', '✨', '🕯️', '🌑', '🧙‍♀️', '🌸', '🕊️', '🌊', '🍂', '❄️', '🌻', '🦉', '🪙', '💫', '⭐', '🔥', '🌿', '💎', '⚡', '🦋']
TITLES = ['👑 Верховная Ведьма', '⭐ Ведьма Звёздного Пути', '🌿 Ведьма Трав и Эликсиров', '🔥 Ведьма Огненного Круга', '🌙 Ведьма Лунного Света', '💎 Ведьма Кристаллов', '⚡ Ведьма Грозовых Ветров', '🦋 Ведьма Превращений', '🔮 Чародейка Утренних Туманов', '✨ Ведающая Путями Судьбы', '🌸 Магиня Звёздного Ветра', '🕊️ Берегиня Тишины', '🌑 Чтица Линий Времени', '🧿 Повелительница Чая и Таро', '🕯️ Хранительница Теней', '🌊 Ведьма Морских Глубин', '🍂 Ведьма Осенних Листьев', '❄️ Ведьма Ледяных Чар', '🌻 Ведьма Золотых Нитей', '🦉 Ведьма Ночной Мудрости']

# Helper functions
def load_json(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return {}

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False

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
            padding: 20px;
            color: #e0e0e0;
        }
        .navbar {
            max-width: 900px;
            margin: 0 auto 30px;
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .nav-btn {
            padding: 12px 24px;
            background: rgba(139, 123, 184, 0.3);
            border: 2px solid #8b7bb8;
            color: #ffd700;
            border-radius: 12px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .nav-btn:hover { 
            background: rgba(255, 215, 0, 0.2);
            border-color: #ffd700;
            transform: translateY(-2px);
        }
        .admin-btn {
            margin-left: auto;
            background: rgba(139, 0, 139, 0.3);
            border-color: #8B008B;
        }
        .admin-btn:hover {
            background: rgba(139, 0, 139, 0.5);
        }
        .main-container {
            display: flex;
            gap: 30px;
            max-width: 1000px;
            margin: 0 auto;
            flex-wrap: wrap;
            justify-content: center;
        }
        .form-section {
            flex: 1;
            min-width: 300px;
            max-width: 500px;
        }
        .members-section {
            flex: 1;
            min-width: 300px;
            max-width: 350px;
        }
        .container {
            background: rgba(30, 20, 50, 0.9);
            border: 2px solid #8b7bb8;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        h1 { font-size: 28px; margin-bottom: 10px; color: #ffd700; text-align: center; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
        .tagline { font-size: 14px; color: #b19cd9; font-style: italic; margin-bottom: 20px; text-align: center; }
        h2 { font-size: 20px; color: #ffd700; margin-bottom: 20px; text-align: center; }
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
        .members-list {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .member-card {
            background: rgba(255, 215, 0, 0.05);
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }
        .member-emoji { font-size: 32px; margin-bottom: 8px; }
        .member-name { font-size: 13px; color: #ffd700; font-weight: bold; margin-bottom: 5px; }
        .member-role { font-size: 11px; color: #b19cd9; font-style: italic; }
    </style>
</head>
<body>
    <div class="navbar">
        <button class="nav-btn" onclick="scrollToForm()">📝 Анкета</button>
        <button class="nav-btn" onclick="scrollToMembers()">👥 Участницы</button>
        <button class="nav-btn" onclick="scrollToProfile()">🔮 Профиль</button>
        <a href="/admin/login" class="nav-btn admin-btn">⚙️ Админка</a>
    </div>

    <div class="main-container">
        <div class="form-section">
            <div class="container" id="formSection">
                <h1>👑 Ведьмы Не Стареют 👑</h1>
                <p class="tagline">Священный клуб магических сестёр</p>

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
                        <label>🎂 Дата рождения</label>
                        <input type="date" name="birthDate">
                    </div>

                    <div class="form-group">
                        <label>💬 Telegram @</label>
                        <input type="text" name="telegramUsername" placeholder="username (без @)">
                    </div>

                    <div class="form-group">
                        <label>💑 Семейный статус</label>
                        <select name="familyStatus">
                            <option value="">Выбрать...</option>
                            <option value="single">Одна</option>
                            <option value="married">Замужем</option>
                            <option value="divorced">Разведена</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>👶 Дети</label>
                        <select name="children">
                            <option value="">Выбрать...</option>
                            <option value="no">Нет</option>
                            <option value="yes">Да</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>✨ Интересы</label>
                        <textarea name="interests" placeholder="Расскажите о ваших интересах..."></textarea>
                    </div>

                    <div class="form-group">
                        <label>📚 Интересующие темы</label>
                        <textarea name="topics" placeholder="Какие темы вас привлекают?"></textarea>
                    </div>

                    <button type="submit">✨ Отправить ✨</button>
                </form>

                <div class="footer">
                    <p>🔮 Добро пожаловать в наш священный круг 🔮</p>
                </div>
            </div>
        </div>

        <div class="members-section">
            <div class="container" id="membersSection">
                <h2>✨ Участницы ✨</h2>
                <div class="members-list" id="membersList">
                </div>
            </div>
        </div>
    </div>

    <script>
        function scrollToForm() {
            document.getElementById('formSection').scrollIntoView({ behavior: 'smooth' });
        }
        function scrollToMembers() {
            document.getElementById('membersSection').scrollIntoView({ behavior: 'smooth' });
        }
        function scrollToProfile() {
            alert('Раздел профиля будет скоро добавлен');
        }

        // Load members
        async function loadMembers() {
            try {
                const res = await fetch('/api/members');
                const members = await res.json();
                const container = document.getElementById('membersList');
                container.innerHTML = '';
                
                members.forEach(member => {
                    const card = document.createElement('div');
                    card.className = 'member-card';
                    card.innerHTML = `
                        <div class="member-emoji">${member.emoji}</div>
                        <div class="member-name">${member.name}</div>
                        <div class="member-role">${member.title}</div>
                    `;
                    container.appendChild(card);
                });
            } catch (e) {
                console.error('Error loading members:', e);
            }
        }

        // Submit form
        document.getElementById('surveyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                name: document.querySelector('input[name="name"]').value,
                birthDate: document.querySelector('input[name="birthDate"]').value,
                telegramUsername: document.querySelector('input[name="telegramUsername"]').value,
                familyStatus: document.querySelector('select[name="familyStatus"]').value,
                children: document.querySelector('select[name="children"]').value,
                interests: document.querySelector('textarea[name="interests"]').value,
                topics: document.querySelector('textarea[name="topics"]').value
            };

            try {
                const response = await fetch('/api/survey', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    document.getElementById('surveyForm').reset();
                    document.getElementById('successMsg').style.display = 'block';
                    document.getElementById('errorMsg').style.display = 'none';
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

        // Load members on page load
        loadMembers();
    </script>
</body>
</html>'''

# ===================== API ENDPOINTS =====================

@app.route('/api/survey', methods=['POST'])
def submit_survey():
    try:
        data = request.json
        if not data or not data.get('name'):
            return jsonify({'error': 'Имя обязательно'}), 400
        
        surveys = load_json(SURVEYS_FILE)
        if not isinstance(surveys, dict):
            surveys = {}
        
        survey_id = str(len(surveys) + 1)
        surveys[survey_id] = {
            'id': survey_id,
            'name': data.get('name', '').strip(),
            'birthDate': data.get('birthDate', ''),
            'telegramUsername': data.get('telegramUsername', '').strip(),
            'familyStatus': data.get('familyStatus', ''),
            'children': data.get('children', ''),
            'interests': data.get('interests', ''),
            'topics': data.get('topics', ''),
            'status': 'pending',
            'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if save_json(SURVEYS_FILE, surveys):
            return jsonify({'success': True, 'survey': surveys[survey_id]}), 200
        return jsonify({'error': 'Save failed'}), 500
    except Exception as e:
        logger.error(f"Error submitting survey: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/members', methods=['GET'])
def api_members():
    members = load_json(MEMBERS_FILE)
    if isinstance(members, dict):
        return jsonify(list(members.values()))
    return jsonify(members if members else [])

@app.route('/api/surveys', methods=['GET'])
def api_surveys():
    surveys = load_json(SURVEYS_FILE)
    if isinstance(surveys, dict):
        return jsonify(list(surveys.values()))
    return jsonify(surveys if surveys else [])

@app.route('/api/approve/<survey_id>', methods=['POST'])
def approve_survey(survey_id):
    try:
        surveys = load_json(SURVEYS_FILE)
        if not isinstance(surveys, dict):
            return jsonify({'error': 'Invalid data'}), 400
        
        survey = surveys.get(survey_id)
        if not survey:
            return jsonify({'error': 'Not found'}), 404
        
        members = load_json(MEMBERS_FILE)
        if not isinstance(members, dict):
            members = {}
        
        member_id = str(len(members) + 1)
        members[member_id] = {
            'id': member_id,
            'name': survey['name'],
            'emoji': random.choice(EMOJIS),
            'title': random.choice(TITLES),
            'joinedAt': datetime.now().isoformat()
        }
        
        survey['status'] = 'approved'
        
        save_json(SURVEYS_FILE, surveys)
        save_json(MEMBERS_FILE, members)
        
        return jsonify({'success': True, 'member': members[member_id]}), 200
    except Exception as e:
        logger.error(f"Error approving survey: {e}")
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
</html>''')
    
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
    surveys = load_json(SURVEYS_FILE)
    members = load_json(MEMBERS_FILE)
    
    surveys_list = list(surveys.values()) if isinstance(surveys, dict) else surveys
    members_list = list(members.values()) if isinstance(members, dict) else members
    
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
        .admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; flex-wrap: wrap; gap: 10px; }
        .logout-btn { background: #ff4444; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; }
        .logout-btn:hover { background: #cc0000; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; text-align: center; }
        .stat-number { font-size: 36px; font-weight: bold; color: #FFD700; }
        .stat-label { font-size: 14px; color: rgba(255, 255, 255, 0.8); margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; background: rgba(255, 255, 255, 0.05); border-radius: 10px; overflow: hidden; margin-bottom: 30px; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        th { background: rgba(255, 255, 255, 0.1); font-weight: bold; }
        tr:hover { background: rgba(255, 255, 255, 0.05); }
        .status { padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
        .status-pending { background: rgba(255, 165, 0, 0.2); color: #FFA500; }
        .status-approved { background: rgba(0, 255, 0, 0.2); color: #00FF00; }
        .approve-btn { background: #00AA00; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }
        .approve-btn:hover { background: #008800; }
        h2 { color: #FFD700; margin-bottom: 20px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="admin-container">
        <div class="admin-header">
            <h1>👑 Панель Управления</h1>
            <a href="/admin/logout" class="logout-btn">Выход</a>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ total_surveys }}</div>
                <div class="stat-label">Всего заявок</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ approved_surveys }}</div>
                <div class="stat-label">Одобрено</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ pending_surveys }}</div>
                <div class="stat-label">На рассмотрении</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_members }}</div>
                <div class="stat-label">Участниц</div>
            </div>
        </div>

        <h2>📋 Заявки на рассмотрении</h2>
        <table>
            <thead>
                <tr>
                    <th>Имя</th>
                    <th>Telegram</th>
                    <th>Дата</th>
                    <th>Действие</th>
                </tr>
            </thead>
            <tbody>
                {% for survey in pending_list %}
                <tr>
                    <td>{{ survey.name }}</td>
                    <td>@{{ survey.telegramUsername }}</td>
                    <td>{{ survey.createdAt }}</td>
                    <td>
                        <form method="POST" action="/api/approve/{{ survey.id }}" style="display:inline;">
                            <button type="submit" class="approve-btn">✓ Одобрить</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h2>👥 Одобренные участницы</h2>
        <table>
            <thead>
                <tr>
                    <th>Имя</th>
                    <th>Титул</th>
                    <th>Присоединилась</th>
                </tr>
            </thead>
            <tbody>
                {% for member in members_list %}
                <tr>
                    <td>{{ member.emoji }} {{ member.name }}</td>
                    <td>{{ member.title }}</td>
                    <td>{{ member.joinedAt[:10] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>''',
    total_surveys=len(surveys_list),
    approved_surveys=len([s for s in surveys_list if s.get('status') == 'approved']),
    pending_surveys=len([s for s in surveys_list if s.get('status') == 'pending']),
    total_members=len(members_list),
    pending_list=[s for s in surveys_list if s.get('status') == 'pending'],
    members_list=members_list
    )

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
