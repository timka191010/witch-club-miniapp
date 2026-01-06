from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from datetime import datetime
from functools import wraps
import json
import os
import logging
import random

try:
    import requests
except ImportError:
    requests = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'witch_club_secret_2025'

SURVEYS_FILE = 'surveys.json'
MEMBERS_FILE = 'members.json'
ADMIN_PASSWORD = 'ведьмы123'

# TELEGRAM CONFIG
TELEGRAM_BOT_TOKEN = '8500508012:AAEMuWXEsZsUfiDiOV50xFw928Tn7VUJRH8'
TELEGRAM_CHAT_ID = '-5015136189'
TELEGRAM_CHAT_LINK = 'https://t.me/+S32BT0FT6w0xYTBi'

EMOJIS = ['🔮', '🌙', '🧿', '✨', '🕯️', '🌑', '🧙‍♀️', '🌸', '🕊️', '🌊', '🍂', '❄️', '🌻', '🦉', '🪙', '💫', '⭐', '🔥', '🌿', '💎', '⚡', '🦋']
TITLES = ['👑 Верховная Ведьма', '⭐ Ведьма Звёздного Пути', '🌿 Ведьма Трав и Эликсиров', '🔥 Ведьма Огненного Круга', '🌙 Ведьма Лунного Света', '💎 Ведьма Кристаллов', '⚡ Ведьма Грозовых Ветров', '🦋 Ведьма Превращений', '🔮 Чародейка Утренних Туманов', '✨ Ведающая Путями Судьбы', '🌸 Магиня Звёздного Ветра', '🕊️ Берегиня Тишины', '🌑 Чтица Линий Времени', '🧿 Повелительница Чая и Таро', '🕯️ Хранительница Теней', '🌊 Ведьма Морских Глубин', '🍂 Ведьма Осенних Листьев', '❄️ Ведьма Ледяных Чар', '🌻 Ведьма Золотых Нитей', '🦉 Ведьма Ночной Мудрости']
BORDER_COLORS = ['#ff69b4', '#00ff88', '#00d4ff', '#ff6b6b', '#ffd700', '#9d4edd', '#00f5ff', '#ff10f0', '#39ff14', '#ff6348']

def init_default_members():
    """Инициализация 8 ведьм по умолчанию"""
    return {
        "1": {
            "id": 1,
            "name": "Мария Зуева",
            "emoji": "🔮",
            "title": "👑 Верховная Ведьма",
            "joinedAt": "2025-01-01T00:00:00"
        },
        "2": {
            "id": 2,
            "name": "Елена Клыкова",
            "emoji": "🌙",
            "title": "🌙 Ведьма Лунного Света",
            "joinedAt": "2025-01-02T00:00:00"
        },
        "3": {
            "id": 3,
            "name": "Елена Пустовит",
            "emoji": "✨",
            "title": "✨ Ведающая Путями Судьбы",
            "joinedAt": "2025-01-03T00:00:00"
        },
        "4": {
            "id": 4,
            "name": "Елена Провосуд",
            "emoji": "❄️",
            "title": "❄️ Ведьма Ледяных Чар",
            "joinedAt": "2025-01-04T00:00:00"
        },
        "5": {
            "id": 5,
            "name": "Наталья Гудкова",
            "emoji": "🔥",
            "title": "🔥 Ведьма Огненного Круга",
            "joinedAt": "2025-01-05T00:00:00"
        },
        "6": {
            "id": 6,
            "name": "Анна Моисеева",
            "emoji": "🧿",
            "title": "🧿 Повелительница Чая и Таро",
            "joinedAt": "2025-01-06T00:00:00"
        },
        "7": {
            "id": 7,
            "name": "Екатерина Когай",
            "emoji": "🌿",
            "title": "🌿 Ведьма Трав и Эликсиров",
            "joinedAt": "2025-01-07T00:00:00"
        },
        "8": {
            "id": 8,
            "name": "Юлия Пиндюрина",
            "emoji": "⭐",
            "title": "⭐ Ведьма Звёздного Пути",
            "joinedAt": "2025-01-08T00:00:00"
        }
    }

def load_json(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    
    if filepath == MEMBERS_FILE:
        return init_default_members()
    
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

def send_telegram_message(text):
    """Отправить сообщение в Telegram"""
    if not requests:
        logger.warning('requests library not installed')
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            logger.info('Telegram message sent successfully')
            return True
        else:
            logger.error(f'Telegram error: {response.text}')
            return False
    except Exception as e:
        logger.error(f'Telegram send error: {e}')
        return False

def send_welcome_message(name, telegram_username):
    """Отправить приветственное сообщение при одобрении"""
    if telegram_username:
        message = f"""🎉 <b>Добро пожаловать, {name}!</b>

Ты принята в клуб <b>"Ведьмы не стареют"</b>! ✨

📱 <b>Присоединяйся к нам:</b>
<a href="{TELEGRAM_CHAT_LINK}">👉 Войти в чат</a>

Ждём встречи! 🔮🌙"""
    else:
        message = f"""🎉 <b>Добро пожаловать, {name}!</b>

Ты принята в клуб <b>"Ведьмы не стареют"</b>! ✨

Администратор свяжется с тобой для отправки ссылки на чат. 📬

Ждём встречи! 🔮🌙"""
    
    send_telegram_message(message)

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
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #e0e0e0;
        }

        .navbar {
            max-width: 1100px;
            margin: 0 auto 30px;
            display: flex;
            gap: 12px;
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
            min-width: 140px;
            text-align: center;
        }

        .nav-btn:hover { 
            background: rgba(255, 215, 0, 0.2);
            border-color: #ffd700;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.2);
        }

        .nav-btn.active {
            background: rgba(255, 215, 0, 0.3);
            border-color: #ffd700;
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
        }

        .admin-btn {
            margin-left: auto;
            background: rgba(139, 0, 139, 0.3);
            border-color: #8B008B;
            color: #ff69b4;
        }

        .admin-btn:hover {
            background: rgba(139, 0, 139, 0.5);
            border-color: #ff69b4;
        }

        .page-section {
            display: none;
            max-width: 1100px;
            margin: 0 auto;
        }

        .page-section.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .form-container {
            background: rgba(30, 20, 50, 0.9);
            border: 2px solid #8b7bb8;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            max-width: 700px;
            margin: 0 auto;
        }

        h1 { 
            font-size: 32px;
            margin-bottom: 8px;
            color: #ffd700;
            text-align: center;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        }

        .tagline { 
            font-size: 16px;
            color: #b19cd9;
            font-style: italic;
            margin-bottom: 30px;
            text-align: center;
        }

        .form-group { 
            margin-bottom: 20px;
        }

        label { 
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            color: #c4a7d6;
            font-weight: bold;
        }

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

        input::placeholder, textarea::placeholder {
            color: rgba(224, 224, 224, 0.5);
        }

        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #ffd700;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
            background: rgba(255, 255, 255, 0.1);
        }

        textarea { 
            resize: vertical;
            min-height: 80px;
        }

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

        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.5);
        }

        button:disabled { 
            opacity: 0.6;
            cursor: not-allowed;
        }

        .success-message { 
            display: none;
            text-align: center;
            color: #4ade80;
            padding: 20px;
            background: rgba(74, 222, 128, 0.1);
            border: 1px solid #4ade80;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .error-message { 
            display: none;
            text-align: center;
            color: #ef4444;
            padding: 20px;
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .members-container {
            background: rgba(30, 20, 50, 0.9);
            border: 2px solid #8b7bb8;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            max-width: 900px;
            margin: 0 auto;
        }

        .members-container h1 {
            margin-bottom: 30px;
        }

        .members-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .member-card {
            background: rgba(255, 255, 255, 0.05);
            border-left: 5px solid #ffd700;
            border-radius: 12px;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .member-card:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(10px);
            box-shadow: 0 8px 15px rgba(255, 215, 0, 0.2);
        }

        .member-emoji { 
            font-size: 50px;
            flex-shrink: 0;
        }

        .member-info {
            flex: 1;
        }

        .member-name { 
            font-size: 18px;
            color: #ffd700;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .member-role { 
            font-size: 14px;
            color: #b19cd9;
            font-style: italic;
        }

        .profile-container {
            background: rgba(30, 20, 50, 0.9);
            border: 2px solid #8b7bb8;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            max-width: 700px;
            margin: 0 auto;
            text-align: center;
        }

        .profile-container h1 {
            margin-bottom: 30px;
        }

        .profile-text {
            font-size: 16px;
            line-height: 1.6;
            color: #c4a7d6;
            margin-bottom: 20px;
        }

        .footer { 
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            color: #8b7bb8;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <button class="nav-btn active" onclick="showSection('anketa', this)">📝 АНКЕТА</button>
        <button class="nav-btn" onclick="showSection('members', this)">👥 УЧАСТНИЦЫ</button>
        <button class="nav-btn" onclick="showSection('profile', this)">🔮 ПРОФИЛЬ</button>
        <a href="/admin/login" class="nav-btn admin-btn">⚙️ АДМИНКА</a>
    </div>

    <!-- АНКЕТА -->
    <div id="anketa" class="page-section active">
        <div class="form-container">
            <h1>🌙 Вступление в Клуб 🌙</h1>
            <p class="tagline">Священный клуб магических сестёр</p>

            <div class="success-message" id="successMsg">
                ✅ Ваша заявка успешно отправлена!<br>
                Спасибо за интерес. Мы свяжемся с вами вскоре.
            </div>

            <div class="error-message" id="errorMsg"></div>

            <form id="surveyForm">
                <div class="form-group">
                    <label>📝 Имя *</label>
                    <input type="text" name="name" placeholder="Ваше имя" required>
                </div>

                <div class="form-group">
                    <label>🎂 Дата рождения (ДД.МММ.ГГГГ)</label>
                    <input type="text" name="birthDate" placeholder="ДД.МММ.ГГГГ">
                </div>

                <div class="form-group">
                    <label>💬 Telegram @</label>
                    <input type="text" name="telegramUsername" placeholder="username (без @)">
                </div>

                <div class="form-group">
                    <label>💑 Семейное положение</label>
                    <select name="familyStatus">
                        <option value="">Выбрать...</option>
                        <option value="single">Одна</option>
                        <option value="married">Замужем</option>
                        <option value="divorced">Разведена</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>👶 Дети (возраст, пол)</label>
                    <input type="text" name="children" placeholder="Дети (возраст, пол)">
                </div>

                <div class="form-group">
                    <label>✨ Увлечения и хобби</label>
                    <textarea name="interests" placeholder="Расскажите о ваших увлечениях..."></textarea>
                </div>

                <div class="form-group">
                    <label>📚 Интересные темы (МК, вьезды)</label>
                    <textarea name="topics" placeholder="Какие темы вас привлекают?"></textarea>
                </div>

                <div class="form-group">
                    <label>🎯 Цель вступления в клуб</label>
                    <textarea name="goals" placeholder="Почему вы хотите присоединиться?"></textarea>
                </div>

                <div class="form-group">
                    <label>🤔 Откуда узнали о клубе?</label>
                    <input type="text" name="source" placeholder="Источник информации">
                </div>

                <button type="submit">✨ Отправить анкету ✨</button>
            </form>

            <div class="footer">
                <p>🔮 Добро пожаловать в наш священный круг 🔮</p>
            </div>
        </div>
    </div>

    <!-- УЧАСТНИЦЫ -->
    <div id="members" class="page-section">
        <div class="members-container">
            <h1>✨ Ведьмы нашего круга ✨</h1>
            <div class="members-list" id="membersList">
                <p style="text-align: center; color: #b19cd9;">Загружаем участниц...</p>
            </div>
        </div>
    </div>

    <!-- ПРОФИЛЬ -->
    <div id="profile" class="page-section">
        <div class="profile-container">
            <h1>🔮 ПРОФИЛЬ 🔮</h1>
            <div class="profile-text">
                <p>Здесь скоро появится информация о вашем профиле в клубе.</p>
                <p>После одобрения вашей заявки администратором вы получите свой уникальный титул и эмодзи!</p>
                <p style="margin-top: 30px; font-style: italic;">✨ Добро пожаловать в нашу семью магических сестёр ✨</p>
            </div>
        </div>
    </div>

    <script>
        const borderColors = ['#ff69b4', '#00ff88', '#00d4ff', '#ff6b6b', '#ffd700', '#9d4edd', '#00f5ff', '#ff10f0', '#39ff14', '#ff6348'];

        function showSection(sectionId, btn) {
            document.querySelectorAll('.page-section').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-btn:not(.admin-btn)').forEach(el => el.classList.remove('active'));
            document.getElementById(sectionId).classList.add('active');
            btn.classList.add('active');
            if (sectionId === 'members') loadMembers();
        }

        async function loadMembers() {
            try {
                const res = await fetch('/api/members');
                const members = await res.json();
                const container = document.getElementById('membersList');
                
                if (members.length === 0) {
                    container.innerHTML = '<p style="text-align: center; color: #b19cd9;">Участниц пока нет. Станьте первой! 🌙</p>';
                    return;
                }
                
                container.innerHTML = '';
                members.forEach((member, idx) => {
                    const card = document.createElement('div');
                    card.className = 'member-card';
                    const color = borderColors[idx % borderColors.length];
                    card.style.borderLeftColor = color;
                    card.innerHTML = `
                        <div class="member-emoji">${member.emoji}</div>
                        <div class="member-info">
                            <div class="member-name">${member.name}</div>
                            <div class="member-role">${member.title}</div>
                        </div>
                    `;
                    container.appendChild(card);
                });
            } catch (e) {
                console.error('Error loading members:', e);
                document.getElementById('membersList').innerHTML = '<p style="color: #ef4444;">Ошибка загрузки</p>';
            }
        }

        document.getElementById('surveyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                name: document.querySelector('input[name="name"]').value,
                birthDate: document.querySelector('input[name="birthDate"]').value,
                telegramUsername: document.querySelector('input[name="telegramUsername"]').value,
                familyStatus: document.querySelector('select[name="familyStatus"]').value,
                children: document.querySelector('input[name="children"]').value,
                interests: document.querySelector('textarea[name="interests"]').value,
                topics: document.querySelector('textarea[name="topics"]').value,
                goals: document.querySelector('textarea[name="goals"]').value,
                source: document.querySelector('input[name="source"]').value
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
                    setTimeout(() => {
                        document.getElementById('successMsg').style.display = 'none';
                    }, 5000);
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

        loadMembers();
    </script>
</body>
</html>'''

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
            'goals': data.get('goals', ''),
            'source': data.get('source', ''),
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
        
        # ОТПРАВИТЬ СООБЩЕНИЕ В ТЕЛЕГРАМ
        send_welcome_message(survey['name'], survey.get('telegramUsername', ''))
        
        return jsonify({'success': True, 'member': members[member_id]}), 200
    except Exception as e:
        logger.error(f"Error approving survey: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Witch Club API running'}), 200

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
        .logout-btn { background: #ff4444; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; font-weight: bold; }
        .logout-btn:hover { background: #cc0000; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; text-align: center; border: 1px solid rgba(255, 215, 0, 0.2); }
        .stat-number { font-size: 36px; font-weight: bold; color: #FFD700; }
        .stat-label { font-size: 14px; color: rgba(255, 255, 255, 0.8); margin-top: 5px; }
        
        .admin-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid rgba(255, 215, 0, 0.3);
        }
        
        .admin-tab {
            padding: 12px 20px;
            background: transparent;
            border: none;
            color: #b19cd9;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .admin-tab:hover {
            color: #FFD700;
        }
        
        .admin-tab.active {
            color: #FFD700;
            border-bottom-color: #FFD700;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        table { width: 100%; border-collapse: collapse; background: rgba(255, 255, 255, 0.05); border-radius: 10px; overflow: hidden; margin-bottom: 30px; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        th { background: rgba(255, 255, 255, 0.1); font-weight: bold; color: #FFD700; }
        tr:hover { background: rgba(255, 255, 255, 0.05); }
        
        .approve-btn, .view-btn, .edit-btn, .delete-btn { 
            border: none; 
            padding: 6px 12px; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 12px; 
            font-weight: bold;
            margin-right: 5px;
            transition: all 0.3s ease;
        }
        
        .approve-btn { background: #00AA00; color: white; }
        .approve-btn:hover { background: #008800; }
        
        .view-btn { background: #4488ff; color: white; }
        .view-btn:hover { background: #2266dd; }
        
        .edit-btn { background: #FFD700; color: #1a0033; }
        .edit-btn:hover { background: #ffed4e; }
        
        .delete-btn { background: #ff6666; color: white; }
        .delete-btn:hover { background: #ff4444; }
        
        h2 { color: #FFD700; margin-bottom: 20px; margin-top: 30px; font-size: 20px; }
        h1 { color: #FFD700; font-size: 28px; }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
        }
        
        .modal-content {
            background: linear-gradient(135deg, #1a0033, #330066);
            margin: 5% auto;
            padding: 30px;
            border: 2px solid #FFD700;
            border-radius: 15px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .close-btn {
            color: #FFD700;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close-btn:hover {
            color: #ffed4e;
        }
        
        .modal-field {
            margin-bottom: 15px;
        }
        
        .modal-label {
            display: block;
            margin-bottom: 5px;
            color: #FFD700;
            font-weight: bold;
            font-size: 14px;
        }
        
        .modal-value {
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 8px;
            border-left: 3px solid #FFD700;
            color: #e0e0e0;
            word-break: break-word;
        }
        
        .modal-input {
            width: 100%;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid #FFD700;
            border-radius: 8px;
            color: white;
            font-size: 14px;
        }
        
        .modal-input:focus {
            outline: none;
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        }
        
        .modal-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            justify-content: flex-end;
        }
        
        .modal-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .modal-save {
            background: #00AA00;
            color: white;
        }
        
        .modal-save:hover {
            background: #008800;
        }
        
        .modal-cancel {
            background: #666666;
            color: white;
        }
        
        .modal-cancel:hover {
            background: #555555;
        }
    </style>
</head>
<body>
    <div class="admin-container">
        <div class="admin-header">
            <h1>👑 Панель управления</h1>
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

        <div class="admin-tabs">
            <button class="admin-tab active" onclick="switchTab('surveys', this)">📋 АНКЕТЫ</button>
            <button class="admin-tab" onclick="switchTab('members', this)">👥 УЧАСТНИЦЫ</button>
        </div>

        <!-- АНКЕТЫ ТАБ -->
        <div id="surveys" class="tab-content active">
            <h2>📋 Заявки на рассмотрении</h2>
            {% if pending_list %}
            <table>
                <thead>
                    <tr>
                        <th>Имя</th>
                        <th>Telegram</th>
                        <th>Дата</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {% for survey in pending_list %}
                    <tr>
                        <td>{{ survey.name }}</td>
                        <td>@{{ survey.telegramUsername }}</td>
                        <td>{{ survey.createdAt }}</td>
                        <td>
                            <button class="view-btn" onclick="viewSurvey({{ survey | tojson }})">👁️ Просмотр</button>
                            <form method="POST" action="/api/approve/{{ survey.id }}" style="display:inline;">
                                <button type="submit" class="approve-btn">✓ Одобрить</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #b19cd9; text-align: center; padding: 20px;">Нет заявок на рассмотрении</p>
            {% endif %}
        </div>

        <!-- УЧАСТНИЦЫ ТАБ -->
        <div id="members" class="tab-content">
            <h2>👥 Одобренные участницы ({{ members_list|length }})</h2>
            {% if members_list %}
            <table>
                <thead>
                    <tr>
                        <th>Имя</th>
                        <th>Эмодзи</th>
                        <th>Титул</th>
                        <th>Присоединилась</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {% for member in members_list %}
                    <tr>
                        <td>{{ member.name }}</td>
                        <td style="font-size: 20px;">{{ member.emoji }}</td>
                        <td>{{ member.title }}</td>
                        <td>{{ member.joinedAt[:10] }}</td>
                        <td>
                            <button class="edit-btn" onclick="editMember({{ member | tojson }})">✏️ Изменить</button>
                            <button class="delete-btn" onclick="deleteMember({{ member.id }})">🗑️ Удалить</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #b19cd9; text-align: center; padding: 20px;">Нет одобренных участниц</p>
            {% endif %}
        </div>
    </div>

    <!-- МОДАЛЬНОЕ ОКНО ПРОСМОТРА АНКЕТЫ -->
    <div id="surveyModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeSurveyModal()">&times;</span>
            <h2 style="color: #FFD700; margin-bottom: 20px;">📋 Анкета</h2>
            <div id="surveyModalBody"></div>
        </div>
    </div>

    <!-- МОДАЛЬНОЕ ОКНО РЕДАКТИРОВАНИЯ УЧАСТНИЦЫ -->
    <div id="memberModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeMemberModal()">&times;</span>
            <h2 style="color: #FFD700; margin-bottom: 20px;">✏️ Редактирование участницы</h2>
            <div class="modal-field">
                <label class="modal-label">Имя</label>
                <input type="text" id="editName" class="modal-input">
            </div>
            <div class="modal-field">
                <label class="modal-label">Эмодзи</label>
                <input type="text" id="editEmoji" class="modal-input" maxlength="2">
            </div>
            <div class="modal-field">
                <label class="modal-label">Титул</label>
                <input type="text" id="editTitle" class="modal-input">
            </div>
            <div class="modal-buttons">
                <button class="modal-btn modal-cancel" onclick="closeMemberModal()">Отмена</button>
                <button class="modal-btn modal-save" onclick="saveMember()">Сохранить</button>
            </div>
        </div>
    </div>

    <script>
        const EMOJIS = ['🔮', '🌙', '🧿', '✨', '🕯️', '🌑', '🧙‍♀️', '🌸', '🕊️', '🌊', '🍂', '❄️', '🌻', '🦉', '🪙', '💫', '⭐', '🔥', '🌿', '💎', '⚡', '🦋'];
        const TITLES = ['👑 Верховная Ведьма', '⭐ Ведьма Звёздного Пути', '🌿 Ведьма Трав и Эликсиров', '🔥 Ведьма Огненного Круга', '🌙 Ведьма Лунного Света', '💎 Ведьма Кристаллов', '⚡ Ведьма Грозовых Ветров', '🦋 Ведьма Превращений', '🔮 Чародейка Утренних Туманов', '✨ Ведающая Путями Судьбы', '🌸 Магиня Звёздного Ветра', '🕊️ Берегиня Тишины', '🌑 Чтица Линий Времени', '🧿 Повелительница Чая и Таро', '🕯️ Хранительница Теней', '🌊 Ведьма Морских Глубин', '🍂 Ведьма Осенних Листьев', '❄️ Ведьма Ледяных Чар', '🌻 Ведьма Золотых Нитей', '🦉 Ведьма Ночной Мудрости'];
        
        let currentMemberId = null;

        function switchTab(tabName, btn) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.admin-tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            btn.classList.add('active');
        }

        function viewSurvey(survey) {
            const modal = document.getElementById('surveyModal');
            const body = document.getElementById('surveyModalBody');
            
            body.innerHTML = `
                <div class="modal-field">
                    <label class="modal-label">Имя</label>
                    <div class="modal-value">${survey.name}</div>
                </div>
                <div class="modal-field">
                    <label class="modal-label">Дата рождения</label>
                    <div class="modal-value">${survey.birthDate || '-'}</div>
                </div>
                <div class="modal-field">
                    <label class="modal-label">Telegram</label>
                    <div class="modal-value">@${survey.telegramUsername || '-'}</div>
                </div>
                <div class="modal-field">
                    <label class="modal-label">Семейное положение</label>
                    <div class="modal-value">${survey.familyStatus || '-'}</div>
                </div>
                <div class="modal-field">
                    <label class="modal-label">Дети</label>
                    <div class="modal-value">${survey.children || '-'}</div>
                </div>
                <div class="modal-field">
                    <label class="modal-label">Увлечения и хобби</label>
                    <div class="modal-value">${survey.interests || '-'}</div>
                </div>
                <div class="modal-field">
                    <label class="modal-label">Интересные темы</label>
                    <div class="modal-value">${survey.topics || '-'}</div>
                </div>
                <div class="modal-field">
                    <label class="modal-label">Цель вступления</label>
                    <div class="modal-value">${survey.goals || '-'}</div>
                </div>
                <div class="modal-field">
                    <label class="modal-label">Откуда узнала о клубе</label>
                    <div class="modal-value">${survey.source || '-'}</div>
                </div>
            `;
            
            modal.style.display = 'block';
        }

        function closeSurveyModal() {
            document.getElementById('surveyModal').style.display = 'none';
        }

        function editMember(member) {
            currentMemberId = member.id;
            document.getElementById('editName').value = member.name;
            document.getElementById('editEmoji').value = member.emoji;
            document.getElementById('editTitle').value = member.title;
            document.getElementById('memberModal').style.display = 'block';
        }

        function closeMemberModal() {
            document.getElementById('memberModal').style.display = 'none';
            currentMemberId = null;
        }

        function saveMember() {
            if (!currentMemberId) return;
            
            const data = {
                name: document.getElementById('editName').value,
                emoji: document.getElementById('editEmoji').value,
                title: document.getElementById('editTitle').value
            };
            
            fetch(`/api/member/${currentMemberId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => {
                if (res.ok) {
                    closeMemberModal();
                    location.reload();
                }
            });
        }

        function deleteMember(memberId) {
            if (confirm('Вы уверены? Это действие нельзя отменить.')) {
                fetch(`/api/member/${memberId}`, {
                    method: 'DELETE'
                })
                .then(res => {
                    if (res.ok) {
                        location.reload();
                    }
                });
            }
        }

        window.onclick = function(event) {
            const surveyModal = document.getElementById('surveyModal');
            const memberModal = document.getElementById('memberModal');
            
            if (event.target === surveyModal) {
                surveyModal.style.display = 'none';
            }
            if (event.target === memberModal) {
                memberModal.style.display = 'none';
            }
        }
    </script>
</body>
</html>''',
    total_surveys=len(surveys_list),
    approved_surveys=len([s for s in surveys_list if s.get('status') == 'approved']),
    pending_surveys=len([s for s in surveys_list if s.get('status') == 'pending']),
    total_members=len(members_list),
    pending_list=[s for s in surveys_list if s.get('status') == 'pending'],
    members_list=members_list
    )

@app.route('/api/member/<member_id>', methods=['PUT'])
def update_member(member_id):
    try:
        data = request.json
        members = load_json(MEMBERS_FILE)
        
        if not isinstance(members, dict):
            return jsonify({'error': 'Invalid data'}), 400
        
        if str(member_id) not in members:
            return jsonify({'error': 'Not found'}), 404
        
        members[str(member_id)].update({
            'name': data.get('name', members[str(member_id)]['name']),
            'emoji': data.get('emoji', members[str(member_id)]['emoji']),
            'title': data.get('title', members[str(member_id)]['title'])
        })
        
        save_json(MEMBERS_FILE, members)
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Error updating member: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/member/<member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        members = load_json(MEMBERS_FILE)
        
        if not isinstance(members, dict):
            return jsonify({'error': 'Invalid data'}), 400
        
        if str(member_id) not in members:
            return jsonify({'error': 'Not found'}), 404
        
        del members[str(member_id)]
        save_json(MEMBERS_FILE, members)
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Error deleting member: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
