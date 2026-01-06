from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
import random

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ПУТИ
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'public')

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
CORS(app, supports_credentials=True)
app.secret_key = 'witch-club-secret-2025-mystical-key-super-secure'
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 2592000

# ФАЙЛЫ ДАННЫХ
MEMBERS_FILE = os.path.join(BASE_DIR, 'data', 'members.json')
SURVEYS_FILE = os.path.join(BASE_DIR, 'data', 'surveys.json')

# Создаём папку data если её нет
os.makedirs(os.path.dirname(MEMBERS_FILE), exist_ok=True)
os.makedirs(os.path.dirname(SURVEYS_FILE), exist_ok=True)

# ===== ФУНКЦИИ ФАЙЛОВОЙ СИСТЕМЫ =====

def load_members():
    """Загружает участниц из файла"""
    try:
        if os.path.exists(MEMBERS_FILE):
            with open(MEMBERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} members")
                return data
    except Exception as e:
        logger.error(f"Error loading members: {e}")
    return get_default_members()

def get_default_members():
    """Возвращает дефолтных участниц"""
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

def save_members(members):
    """Сохраняет участниц в файл"""
    try:
        with open(MEMBERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(members, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(members)} members")
        return True
    except Exception as e:
        logger.error(f"Error saving members: {e}")
        return False

def load_surveys():
    """Загружает анкеты из файла"""
    try:
        if os.path.exists(SURVEYS_FILE):
            with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} surveys")
                return data
    except Exception as e:
        logger.error(f"Error loading surveys: {e}")
    return []

def save_surveys(surveys):
    """Сохраняет анкеты в файл"""
    try:
        with open(SURVEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(surveys, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(surveys)} surveys")
        return True
    except Exception as e:
        logger.error(f"Error saving surveys: {e}")
        return False

def get_user_profile(user_id):
    """Получает профиль пользователя"""
    surveys = load_surveys()
    for survey in surveys:
        if survey.get('id') == user_id:
            return survey
    return None

def validate_survey_data(data):
    """Валидирует данные анкеты"""
    if not data.get('name'):
        return False, 'Name is required'
    if not data.get('statusField'):
        return False, 'Status is required'
    if not data.get('goal'):
        return False, 'Goal is required'
    if not data.get('source'):
        return False, 'Source is required'
    return True, 'Valid'

# ===== MAIN ROUTES ============

@app.route('/')
def index():
    """Главная страница"""
    members = load_members()
    return render_template('index.html', members=members)

@app.route('/admin.html')
def admin():
    """Админ страница"""
    return render_template('admin.html')

@app.route('/admin_login.html')
def admin_login():
    """Админ логин"""
    return render_template('admin_login.html')

@app.route('/admin_dashboard.html')
def admin_dashboard():
    """Админ дашборд"""
    return render_template('admin_dashboard.html')

@app.route('/admin_stats.html')
def admin_stats():
    """Админ статистика"""
    return render_template('admin_stats.html')

@app.route('/survey')
def survey():
    """Страница анкеты"""
    return render_template('survey.html')

@app.route('/profile')
def profile():
    """Страница профиля"""
    return render_template('profile.html')

# ============ API ROUTES - ADMIN AUTH ============

@app.route('/api/admin_login', methods=['POST'])
def api_admin_login():
    """Логин в админку"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        ADMIN_USERNAME = 'admin'
        ADMIN_PASSWORD = 'ведьма2025'
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.permanent = True
            logger.info(f"Admin login successful")
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            logger.warning(f"Failed admin login attempt")
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Error in api_admin_login: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ API ROUTES - SURVEY ============

@app.route('/api/submit_survey', methods=['POST'])
def api_submit_survey():
    """Отправка анкеты"""
    try:
        data = request.json
        logger.info(f"Submitting survey: {data.get('name')}")
        
        is_valid, message = validate_survey_data(data)
        if not is_valid:
            logger.warning(f"Invalid survey data: {message}")
            return jsonify({'success': False, 'error': message}), 400
        
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
            'createdAt': datetime.now().isoformat(),
            'timestamp': datetime.now().isoformat()
        }
        
        surveys.append(new_survey)
        
        if not save_surveys(surveys):
            return jsonify({'success': False, 'error': 'Failed to save survey'}), 500
        
        session['user_id'] = new_survey['id']
        session['user_name'] = new_survey['name']
        session.permanent = True
        
        logger.info(f"Survey saved with ID: {new_survey['id']}")
        
        return jsonify({
            'success': True,
            'user_id': new_survey['id'],
            'message': 'Survey submitted successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error in api_submit_survey: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    """Legacy endpoint"""
    return api_submit_survey()

# ============ API ROUTES - PROFILE ============

@app.route('/api/profile', methods=['GET'])
def api_get_profile():
    """Получить профиль текущего пользователя"""
    try:
        user_id = session.get('user_id')
        logger.debug(f"Getting profile for user_id: {user_id}")
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'No user session',
                'profile': None
            }), 401
        
        profile = get_user_profile(user_id)
        
        if profile:
            logger.info(f"Profile found for user {user_id}")
            return jsonify({
                'success': True,
                'profile': profile,
                'message': 'Profile loaded'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Profile not found',
                'profile': None
            }), 404
            
    except Exception as e:
        logger.error(f"Error in api_get_profile: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'profile': None
        }), 500

@app.route('/get_profile', methods=['GET'])
def get_profile_legacy():
    """Legacy endpoint"""
    return api_get_profile()

@app.route('/api/profiles', methods=['GET'])
def api_get_all_profiles():
    """Получить все анкеты"""
    try:
        surveys = load_surveys()
        return jsonify({
            'success': True,
            'profiles': surveys,
            'total': len(surveys)
        }), 200
    except Exception as e:
        logger.error(f"Error in api_get_all_profiles: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/<int:profile_id>', methods=['GET'])
def api_get_profile_by_id(profile_id):
    """Получить профиль по ID"""
    try:
        profile = get_user_profile(profile_id)
        if profile:
            return jsonify({'success': True, 'profile': profile}), 200
        else:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
    except Exception as e:
        logger.error(f"Error in api_get_profile_by_id: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/<int:profile_id>/status', methods=['PUT'])
def api_update_profile_status(profile_id):
    """Обновить статус анкеты"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['pending', 'approved', 'rejected']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        surveys = load_surveys()
        
        for survey in surveys:
            if survey.get('id') == profile_id:
                survey['applicationStatus'] = new_status
                if save_surveys(surveys):
                    logger.info(f"Updated profile {profile_id} status to {new_status}")
                    return jsonify({
                        'success': True,
                        'message': f'Status updated to {new_status}',
                        'profile': survey
                    }), 200
                else:
                    return jsonify({'success': False, 'error': 'Failed to update status'}), 500
        
        return jsonify({'success': False, 'message': 'Profile not found'}), 404
        
    except Exception as e:
        logger.error(f"Error in api_update_profile_status: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/<int:profile_id>', methods=['PUT'])
def api_update_profile(profile_id):
    """Обновить профиль"""
    try:
        data = request.json
        surveys = load_surveys()
        
        for survey in surveys:
            if survey.get('id') == profile_id:
                allowed_fields = ['name', 'birthDate', 'status', 'children', 'interests', 'topics', 'goal', 'source']
                for field in allowed_fields:
                    if field in data:
                        survey[field] = data[field]
                
                if save_surveys(surveys):
                    logger.info(f"Updated profile {profile_id}")
                    return jsonify({
                        'success': True,
                        'message': 'Profile updated',
                        'profile': survey
                    }), 200
                else:
                    return jsonify({'success': False, 'error': 'Failed to update profile'}), 500
        
        return jsonify({'success': False, 'message': 'Profile not found'}), 404
        
    except Exception as e:
        logger.error(f"Error in api_update_profile: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/<int:profile_id>', methods=['DELETE'])
def api_delete_profile(profile_id):
    """Удалить профиль"""
    try:
        surveys = load_surveys()
        original_count = len(surveys)
        
        surveys = [s for s in surveys if s.get('id') != profile_id]
        
        if len(surveys) < original_count:
            if save_surveys(surveys):
                logger.info(f"Deleted profile {profile_id}")
                return jsonify({'success': True, 'message': 'Profile deleted'}), 200
            else:
                return jsonify({'success': False, 'error': 'Failed to delete profile'}), 500
        else:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
            
    except Exception as e:
        logger.error(f"Error in api_delete_profile: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ API ROUTES - APPLICATIONS ============

@app.route('/api/applications', methods=['GET'])
def api_get_applications():
    """Получить все заявки"""
    try:
        surveys = load_surveys()
        logger.info(f"Fetched {len(surveys)} applications")
        return jsonify({
            'success': True,
            'applications': surveys,
            'total': len(surveys)
        }), 200
    except Exception as e:
        logger.error(f"Error in api_get_applications: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['GET'])
def api_get_application(app_id):
    """Получить одну заявку"""
    try:
        app = get_user_profile(app_id)
        if app:
            return jsonify({'success': True, 'application': app}), 200
        return jsonify({'success': False, 'message': 'Not found'}), 404
    except Exception as e:
        logger.error(f"Error in api_get_application: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['PATCH'])
def api_update_application_status(app_id):
    """Обновить статус заявки"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['pending', 'approved', 'rejected']:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        surveys = load_surveys()
        
        for survey in surveys:
            if survey.get('id') == app_id:
                survey['applicationStatus'] = new_status
                if save_surveys(surveys):
                    logger.info(f"Updated application {app_id} status to {new_status}")
                    return jsonify({
                        'success': True,
                        'message': f'Status updated to {new_status}',
                        'application': survey
                    }), 200
                else:
                    return jsonify({'success': False, 'error': 'Failed to update'}), 500
        
        return jsonify({'success': False, 'message': 'Not found'}), 404
        
    except Exception as e:
        logger.error(f"Error in api_update_application_status: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['DELETE'])
def api_delete_application(app_id):
    """Удалить заявку"""
    try:
        surveys = load_surveys()
        original_count = len(surveys)
        
        surveys = [s for s in surveys if s.get('id') != app_id]
        
        if len(surveys) < original_count:
            if save_surveys(surveys):
                logger.info(f"Deleted application {app_id}")
                return jsonify({'success': True, 'message': 'Application deleted'}), 200
            else:
                return jsonify({'success': False, 'error': 'Failed to delete'}), 500
        else:
            return jsonify({'success': False, 'message': 'Not found'}), 404
            
    except Exception as e:
        logger.error(f"Error in api_delete_application: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ API ROUTES - MEMBERS ============

@app.route('/api/members', methods=['GET'])
def api_get_members_list():
    """Получить список участниц"""
    try:
        members = load_members()
        logger.info(f"Fetched {len(members)} members")
        return jsonify({
            'success': True,
            'members': members,
            'count': len(members)
        }), 200
    except Exception as e:
        logger.error(f"Error in api_get_members_list: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members', methods=['POST'])
def api_add_member():
    """Добавить новую участницу"""
    try:
        data = request.json
        name = data.get('name')
        title = data.get('title')
        emoji = data.get('emoji')
        
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        members = load_members()
        next_id = max([m.get('id', 0) for m in members], default=0) + 1
        
        new_member = {
            'id': next_id,
            'name': name,
            'title': title or '',
            'emoji': emoji or '🔮'
        }
        
        members.append(new_member)
        
        if not save_members(members):
            return jsonify({'success': False, 'error': 'Failed to save member'}), 500
        
        logger.info(f"Added new member: {name}")
        
        return jsonify({
            'success': True,
            'member': new_member,
            'message': 'Member added'
        }), 201
        
    except Exception as e:
        logger.error(f"Error in api_add_member: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/<int:member_id>', methods=['GET'])
def api_get_member(member_id):
    """Получить одного участника"""
    try:
        members = load_members()
        member = next((m for m in members if m.get('id') == member_id), None)
        if member:
            return jsonify({'success': True, 'member': member}), 200
        return jsonify({'success': False, 'message': 'Not found'}), 404
    except Exception as e:
        logger.error(f"Error in api_get_member: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def api_delete_member(member_id):
    """Удалить участницу"""
    try:
        members = load_members()
        original_count = len(members)
        members = [m for m in members if m.get('id') != member_id]
        
        if len(members) < original_count:
            if save_members(members):
                logger.info(f"Deleted member {member_id}")
                return jsonify({'success': True, 'message': 'Member deleted'}), 200
            else:
                return jsonify({'success': False, 'error': 'Failed to delete'}), 500
        else:
            return jsonify({'success': False, 'message': 'Not found'}), 404
            
    except Exception as e:
        logger.error(f"Error in api_delete_member: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ API ROUTES - UTILITY ============

@app.route('/api/session', methods=['GET'])
def api_get_session():
    """Получить информацию о сессии"""
    return jsonify({
        'user_id': session.get('user_id'),
        'user_name': session.get('user_name'),
        'has_session': 'user_id' in session
    }), 200

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Статистика"""
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
        logger.error(f"Error in api_stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Выход из системы"""
    user_id = session.get('user_id')
    logger.info(f"Logout for user_id: {user_id}")
    session.clear()
    return redirect('/')

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'app': 'Witch Club MiniApp',
        'version': '1.0.0'
    }), 200

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    logger.warning(f"405 Method Not Allowed: {request.method} {request.path}")
    return jsonify({'success': False, 'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def server_error(error):
    logger.error(f"500 Server Error: {error}", exc_info=True)
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.before_request
def before_request():
    logger.debug(f"{request.method} {request.path}")

@app.after_request
def after_request(response):
    logger.debug(f"Response: {response.status_code}")
    return response

# ============ MAIN ============

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Starting Witch Club MiniApp")
    logger.info("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
