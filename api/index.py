from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging

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

DATA_DIR = '/tmp'
MEMBERS_FILE = os.path.join(DATA_DIR, 'members.json')
SURVEYS_FILE = os.path.join(DATA_DIR, 'surveys.json')

def init_members():
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
    try:
        if os.path.exists(MEMBERS_FILE):
            with open(MEMBERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading members: {e}")
    return init_members()

def save_members(members):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(MEMBERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(members, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving members: {e}")
        return False

def load_surveys():
    try:
        if os.path.exists(SURVEYS_FILE):
            with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading surveys: {e}")
    return []

def save_surveys(surveys):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SURVEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(surveys, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving surveys: {e}")
        return False

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
    '🪙 Хранительница Древних Тайн'
]

EMOJIS = ['🔮','🌙','🧿','✨','🕯️','🌑','🧙‍♀️','🌸','🕊️','🌊','🍂','❄️','🌻','🦉','🪙','💫','⭐','🔥','🌿','💎','⚡','🦋']

import random

def random_title():
    return TITLES[random.randint(0, len(TITLES)-1)]

def random_emoji():
    return EMOJIS[random.randint(0, len(EMOJIS)-1)]

@app.route('/')
def index():
    members = load_members()
    return render_template('index.html', members=members)

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

@app.route('/api/admin_login', methods=['POST'])
def api_admin_login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if username == 'admin' and password == 'ведьма2025':
            session['admin_logged_in'] = True
            session.permanent = True
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
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
        
        return jsonify({'success': True, 'user_id': next_id}), 201
    except Exception as e:
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
        return jsonify({'success': False, 'message': 'Not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications', methods=['GET'])
def get_applications():
    try:
        surveys = load_surveys()
        return jsonify({'success': True, 'applications': surveys, 'total': len(surveys)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['PATCH'])
def update_application(app_id):
    try:
        data = request.json
        surveys = load_surveys()
        
        for survey in surveys:
            if survey.get('id') == app_id:
                survey['applicationStatus'] = data.get('status')
                save_surveys(surveys)
                return jsonify({'success': True, 'application': survey}), 200
        
        return jsonify({'success': False, 'message': 'Not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['DELETE'])
def delete_application(app_id):
    try:
        surveys = load_surveys()
        surveys = [s for s in surveys if s.get('id') != app_id]
        save_surveys(surveys)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members', methods=['GET'])
def get_members():
    try:
        members = load_members()
        return jsonify({'success': True, 'members': members, 'count': len(members)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members', methods=['POST'])
def add_member():
    try:
        data = request.json
        members = load_members()
        next_id = max([m.get('id', 0) for m in members], default=0) + 1
        
        new_member = {
            'id': next_id,
            'name': data.get('name'),
            'title': data.get('title', random_title()),
            'emoji': data.get('emoji', random_emoji())
        }
        
        members.append(new_member)
        save_members(members)
        
        return jsonify({'success': True, 'member': new_member}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        members = load_members()
        members = [m for m in members if m.get('id') != member_id]
        save_members(members)
        return jsonify({'success': True}), 200
    except Exception as e:
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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
