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
    '🧙‍♀️ Волшебница Забытых Слов'
]

# ============================================
# HELPER FUNCTIONS
# ============================================

def load_json(filepath):
    """Load JSON file safely"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return {}

def save_json(filepath, data):
    """Save JSON file safely"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False

def send_telegram_message(chat_id, message_text):
    """Send message to Telegram"""
    if not requests:
        logger.warning("requests library not available")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message_text,
            'parse_mode': 'HTML'
        }, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False

def get_members():
    """Get all members"""
    return load_json(MEMBERS_FILE)

def get_surveys():
    """Get all surveys"""
    return load_json(SURVEYS_FILE)

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/members', methods=['GET'])
def api_members():
    """Get all members"""
    members = get_members()
    return jsonify(list(members.values()) if isinstance(members, dict) else members)

@app.route('/api/member/<member_id>', methods=['GET'])
def api_member(member_id):
    """Get single member"""
    members = get_members()
    if isinstance(members, dict):
        member = members.get(member_id)
    else:
        member = next((m for m in members if m.get('id') == member_id), None)
    
    if member:
        return jsonify(member)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/add-member', methods=['POST'])
def add_member():
    """Add new member"""
    try:
        data = request.json
        members = get_members()
        if not isinstance(members, dict):
            members = {}
        
        member_id = str(len(members) + 1)
        members[member_id] = {
            'id': member_id,
            'name': data.get('name'),
            'emoji': random.choice(EMOJIS),
            'title': random.choice(TITLES),
            'joinedAt': datetime.now().isoformat(),
            'color': f'#{random.randint(0, 0xFFFFFF):06x}'
        }
        
        if save_json(MEMBERS_FILE, members):
            # Notify telegram
            msg = f"✨ Новая участница: {data.get('name')}"
            send_telegram_message(TELEGRAM_CHAT_ID, msg)
            return jsonify({'success': True, 'member': members[member_id]})
        
        return jsonify({'error': 'Save failed'}), 500
    except Exception as e:
        logger.error(f"Error adding member: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/surveys', methods=['GET'])
def api_surveys():
    """Get all surveys"""
    surveys = get_surveys()
    return jsonify(list(surveys.values()) if isinstance(surveys, dict) else surveys)

@app.route('/api/survey', methods=['POST'])
def submit_survey():
    """Submit survey/application"""
    try:
        data = request.json
        surveys = get_surveys()
        if not isinstance(surveys, dict):
            surveys = {}
        
        survey_id = str(len(surveys) + 1)
        surveys[survey_id] = {
            'id': survey_id,
            'name': data.get('name'),
            'birthDate': data.get('birthDate'),
            'telegramUsername': data.get('telegramUsername'),
            'familyStatus': data.get('familyStatus'),
            'children': data.get('children'),
            'interests': data.get('interests'),
            'topics': data.get('topics'),
            'goal': data.get('goal'),
            'source': data.get('source'),
            'status': 'pending',
            'createdAt': datetime.now().isoformat()
        }
        
        if save_json(SURVEYS_FILE, surveys):
            # Notify telegram about new application
            msg = f"📝 Новая заявка от: {data.get('name')}"
            send_telegram_message(TELEGRAM_CHAT_ID, msg)
            return jsonify({'success': True, 'survey': surveys[survey_id]})
        
        return jsonify({'error': 'Save failed'}), 500
    except Exception as e:
        logger.error(f"Error submitting survey: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/approve/<survey_id>', methods=['POST'])
def approve_survey(survey_id):
    """Approve survey and add to members"""
    try:
        surveys = get_surveys()
        if not isinstance(surveys, dict):
            return jsonify({'error': 'Invalid data'}), 400
        
        survey = surveys.get(survey_id)
        if not survey:
            return jsonify({'error': 'Not found'}), 404
        
        # Create member
        members = get_members()
        if not isinstance(members, dict):
            members = {}
        
        member_id = str(len(members) + 1)
        members[member_id] = {
            'id': member_id,
            'name': survey['name'],
            'emoji': random.choice(EMOJIS),
            'title': random.choice(TITLES),
            'joinedAt': datetime.now().isoformat(),
            'color': f'#{random.randint(0, 0xFFFFFF):06x}'
        }
        
        # Update survey status
        survey['status'] = 'approved'
        
        # Save both
        save_json(SURVEYS_FILE, surveys)
        save_json(MEMBERS_FILE, members)
        
        # Send telegram messages
        congratulations = f"""🎉 <b>Поздравляем, {survey['name']}!</b> 🎉

<i>Вы успешно прошли отбор и приняты в наш священный клуб</i>
👑 <b>Ведьмы Не Стареют</b> 👑

Присоединяйтесь к нам: {TELEGRAM_CHAT_LINK}

Ждём вас в кругу сестёр! 🔮"""
        
        # Send to user
        if survey.get('telegramUsername'):
            send_telegram_message(f"@{survey['telegramUsername']}", congratulations)
        
        # Notify admins
        admin_msg = f"""✅ <b>НОВАЯ УЧАСТНИЦА</b> ✅

👤 Имя: <b>{survey['name']}</b>
🔢 ID: <code>#{member_id}</code>

Поздравительное сообщение отправлено! 🎉"""
        send_telegram_message(TELEGRAM_CHAT_ID, admin_msg)
        
        return jsonify({'success': True, 'member': members[member_id]})
    except Exception as e:
        logger.error(f"Error approving survey: {e}")
        return jsonify({'error': str(e)}), 400

# ============================================
# WSGI APP FOR VERCEL
# ============================================

handler = app

if __name__ == '__main__':
    app.run(debug=True)
