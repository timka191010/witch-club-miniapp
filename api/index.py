from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
import random

try:
    import requests
except ImportError:
    requests = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'public')

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
CORS(app, supports_credentials=True)
app.secret_key = 'witch-club-secret-2025-mystical-key-super-secure'
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 2592000

# TELEGRAM CONFIG
TELEGRAM_BOT_TOKEN = '8500508012:AAEMuWXEsZsUfiDiOV50xFw928Tn7VUJRH8'
TELEGRAM_CHAT_ID = '-5015136189'
TELEGRAM_CHAT_LINK = 'https://t.me/+S32BT0FT6w0xYTBi'

DATA_DIR = '/tmp'
MEMBERS_FILE = os.path.join(DATA_DIR, 'members.json')
SURVEYS_FILE = os.path.join(DATA_DIR, 'surveys.json')

# LISTS FOR RANDOM GENERATION
EMOJIS = ['🔮','🌙','🧿','✨','🕯️','🌑','🧙‍♀️','🌸','🕊️','🌊','🍂','❄️','🌻','🦉','🪙','💫','⭐','🔥','🌿','💎','⚡','🦋']

TITLES = [
    '👑 Верховная Ведьма',
    '⭐ Ведьма Звёздного Пути',
    '🌿 Ведьма Трав и Эликсиров',
    '🔥 Ведьма Огненного Круга',
    '🌙 Ведьма Лунного Света',
    '💎 Ведьма Кристаллов',
    '⚡ Ведьма Грозовых Ветров',
    '🦋 Ведьма Превращений',
    '🔮 Чародейка Утренних Туманов',
    '✨ Ведающая Путями Судьбы',
    '🌸 Магиня Звёздного Ветра',
    '🕊️ Берегиня Тишины',
    '🌑 Чтица Линий Времени',
    '🧿 Повелительница Чая и Таро',
    '🕯️ Хранительница Теней',
    '🌊 Ведьма Морских Глубин',
    '🍂 Ведьма Осенних Листьев',
    '❄️ Ведьма Ледяных Чар',
    '🌻 Ведьма Золотых Нитей',
    '🦉 Ведьма Ночной Мудрости',
    '🧙‍♀️ Волшебница Забытых Слов',
    '💫 Сотворительница Звёзд',
    '🪙 Хранительница Древних Тайн',
    '🔮 Ведьма Трёх Миров',
    '✨ Воплотительница Желаний',
    '🌙 Королева Ночного Неба',
    '💎 Владычица Кристаллического Замка',
    '🌿 Целительница Душ',
    '⚡ Повелительница Грома',
    '🦋 Королева Метаморфоз',
    '🌊 Госпожа Волн',
    '🍂 Танцовщица Осеннего Ветра',
    '🕯️ Свечница Магических Огней',
    '🧿 Провидица Темного Зеркала',
    '🌸 Цветущая Королева',
    '🕊️ Голубка Духов',
    '🌑 Луна Тайных Знаний',
]

def random_title():
    """Генерировать случайный титул"""
    return random.choice(TITLES)

def random_emoji():
    """Генерировать случайный эмодзи"""
    return random.choice(EMOJIS)

def init_members():
    """Инициализировать список участниц"""
    return [
        {"id": 1, "emoji": "🔮", "name": "Мария Зуева", "title": "👑 Верховная Ведьма"},
        {"id": 2, "emoji": "✨", "name": "Юлия Пиндюрина", "title": "⭐ Ведьма Звёздного Пути"},
        {"id": 3, "emoji": "🌿", "name": "Елена Клыкова", "title": "🌿 Ведьма Трав и Эликсиров"},
        {"id": 4, "emoji": "🕯️", "name": "Наталья Гудкова", "title": "🔥 Ведьма Огненного Круга"},
        {"id": 5, "emoji": "🌕", "name": "Екатерина Когай", "title": "🌙 Ведьма Лунного Света"},
        {"id": 6, "emoji": "💎", "name": "Елена Пустовит", "title": "💎 Ведьма Кристаллов"},
        {"id": 7, "emoji": "🌪️", "name": "Елена Правосуд", "title": "⚡ Ведьма Грозовых Ветров"},
        {"id": 8, "emoji": "🦋", "name": "Анна Моисеева", "title": "🦋 Ведьма Превращений"},
    ]

def load_members():
    """Загрузить участниц из файла"""
    try:
        if os.path.exists(MEMBERS_FILE):
            with open(MEMBERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading members: {e}")
    return init_members()

def save_members(members):
    """Сохранить участниц в файл"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(MEMBERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(members, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving members: {e}")
        return False

def load_surveys():
    """Загрузить заявки из файла"""
    try:
        if os.path.exists(SURVEYS_FILE):
            with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading surveys: {e}")
    return []

def save_surveys(surveys):
    """Сохранить заявки в файл"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SURVEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(surveys, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving surveys: {e}")
        return False

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

def send_welcome_message(name):
    """Отправить приветственное сообщение при одобрении"""
    message = f"""🎉 <b>Добро пожаловать, {name}!</b>

Ты принята в клуб <b>"Ведьмы не стареют"</b>! ✨

📱 <b>Присоединяйся к нам:</b>
<a href="{TELEGRAM_CHAT_LINK}">👉 Войти в чат</a>

Ждём встречи! 🔮🌙"""
    
    send_telegram_message(message)

# ========== HTML ROUTES ==========

@app.route('/')
def index():
    members = load_members()
    return render_template('index.html', members=members)

@app.route('/admin.html')
def admin():
    return render_template('admin.html')

@app.route('/admin_login.html')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin_dashboard.html')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin_stats.html')
def admin_stats():
    return render_template('admin_stats.html')

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

# ========== API ROUTES ==========

@app.route('/api/admin_login', methods=['POST'])
def api_admin_login():
    try:
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        
        if username == 'admin' and password == 'ведьма2025':
            session['admin_logged_in'] = True
            session.permanent = True
            logger.info('Admin logged in')
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            logger.warning(f'Failed login attempt: {username}')
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f'Login error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/submit_survey', methods=['POST'])
def submit_survey():
    try:
        data = request.json
        surveys = load_surveys()
        next_id = max([s.get('id', 0) for s in surveys], default=0) + 1
        
        new_survey = {
            'id': next_id,
            'name': data.get('name', ''),
            'birthDate': data.get('birthDate', ''),
            'status': data.get('statusField', ''),
            'children': data.get('children', ''),
            'interests': data.get('interests', ''),
            'topics': data.get('topics', ''),
            'goal': data.get('goal', ''),
            'source': data.get('source', ''),
            'applicationStatus': 'pending',
            'createdAt': datetime.now().isoformat()
        }
        
        surveys.append(new_survey)
        save_surveys(surveys)
        
        session['user_id'] = next_id
        session['user_name'] = data.get('name', '')
        session.permanent = True
        
        logger.info(f'New survey submitted: {next_id}')
        return jsonify({'success': True, 'user_id': next_id}), 201
    except Exception as e:
        logger.error(f'Survey submission error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
def get_profile():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'No session'}), 401
        
        surveys = load_surveys()
        profile = next((s for s in surveys if s.get('id') == user_id), None)
        
        if profile:
            return jsonify({'success': True, 'profile': profile}), 200
        return jsonify({'success': False, 'message': 'Profile not found'}), 404
    except Exception as e:
        logger.error(f'Profile fetch error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications', methods=['GET'])
def get_applications():
    try:
        surveys = load_surveys()
        return jsonify({'success': True, 'applications': surveys, 'total': len(surveys)}), 200
    except Exception as e:
        logger.error(f'Applications fetch error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['GET'])
def get_application(app_id):
    try:
        surveys = load_surveys()
        application = next((s for s in surveys if s.get('id') == app_id), None)
        
        if application:
            return jsonify({'success': True, 'application': application}), 200
        return jsonify({'success': False, 'message': 'Application not found'}), 404
    except Exception as e:
        logger.error(f'Application fetch error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['PATCH'])
def update_application(app_id):
    try:
        data = request.json
        surveys = load_surveys()
        
        for survey in surveys:
            if survey.get('id') == app_id:
                new_status = data.get('status')
                survey['applicationStatus'] = new_status
                save_surveys(surveys)
                
                # ОТПРАВИТЬ СООБЩЕНИЕ В ТЕЛЕГРАМ если одобрена
                if new_status == 'approved':
                    send_welcome_message(survey.get('name', 'Путешественница'))
                
                logger.info(f'Application {app_id} updated to {new_status}')
                return jsonify({'success': True, 'application': survey}), 200
        
        return jsonify({'success': False, 'message': 'Application not found'}), 404
    except Exception as e:
        logger.error(f'Application update error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['DELETE'])
def delete_application(app_id):
    try:
        surveys = load_surveys()
        surveys = [s for s in surveys if s.get('id') != app_id]
        save_surveys(surveys)
        logger.info(f'Application {app_id} deleted')
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f'Application delete error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members', methods=['GET'])
def get_members():
    try:
        members = load_members()
        return jsonify({'success': True, 'members': members, 'count': len(members)}), 200
    except Exception as e:
        logger.error(f'Members fetch error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members', methods=['POST'])
def add_member():
    try:
        data = request.json
        members = load_members()
        next_id = max([m.get('id', 0) for m in members], default=0) + 1
        
        new_member = {
            'id': next_id,
            'name': data.get('name', 'Unnamed'),
            'title': data.get('title', random_title()),
            'emoji': data.get('emoji', random_emoji())
        }
        
        members.append(new_member)
        save_members(members)
        
        logger.info(f'New member added: {next_id} - {new_member["name"]}')
        return jsonify({'success': True, 'member': new_member}), 201
    except Exception as e:
        logger.error(f'Member add error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/<int:member_id>', methods=['PATCH'])
def update_member(member_id):
    """Изменить титул, имя или эмодзи участницы"""
    try:
        data = request.json
        members = load_members()
        
        for member in members:
            if member.get('id') == member_id:
                if 'title' in data:
                    member['title'] = data.get('title')
                if 'name' in data:
                    member['name'] = data.get('name')
                if 'emoji' in data:
                    member['emoji'] = data.get('emoji')
                
                save_members(members)
                logger.info(f'Member {member_id} updated: {member}')
                return jsonify({'success': True, 'member': member}), 200
        
        return jsonify({'success': False, 'message': 'Member not found'}), 404
    except Exception as e:
        logger.error(f'Member update error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        members = load_members()
        members = [m for m in members if m.get('id') != member_id]
        save_members(members)
        logger.info(f'Member {member_id} deleted')
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f'Member delete error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/random-title', methods=['GET'])
def get_random_title():
    """Получить случайный титул"""
    try:
        return jsonify({'success': True, 'title': random_title()}), 200
    except Exception as e:
        logger.error(f'Random title error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/random-emoji', methods=['GET'])
def get_random_emoji():
    """Получить случайный эмодзи"""
    try:
        return jsonify({'success': True, 'emoji': random_emoji()}), 200
    except Exception as e:
        logger.error(f'Random emoji error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        surveys = load_surveys()
        members = load_members()
        pending = sum(1 for s in surveys if s.get('applicationStatus') == 'pending')
        approved = sum(1 for s in surveys if s.get('applicationStatus') == 'approved')
        rejected = sum(1 for s in surveys if s.get('applicationStatus') == 'rejected')
        
        return jsonify({
            'success': True,
            'total': len(surveys),
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'members': len(members)
        }), 200
    except Exception as e:
        logger.error(f'Stats fetch error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f'Server error: {e}')
    return jsonify({'success': False, 'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
