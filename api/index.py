from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app, supports_credentials=True)
app.secret_key = 'witch-club-secret-2025-mystical-key-super-secure'
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 2592000  # 30 days

# ========== ОРИГИНАЛЬНЫЕ 8 УЧАСТНИЦ ==========
MEMBERS = [
    {"emoji": "🔮", "name": "Мария Зуева", "title": "Ведьма Таро"},
    {"emoji": "✨", "name": "Юлия Пиндюрина", "title": "Травница Луны"},
    {"emoji": "🌙", "name": "Екатерина Когай", "title": "Звёздная знахарка"},
    {"emoji": "🕯️", "name": "Елена Пустовит", "title": "Огненная ведьма"},
    {"emoji": "🌿", "name": "Елена Правосуд", "title": "Хранительница леса"},
    {"emoji": "🔥", "name": "Анна Моисеева", "title": "Ведьма огня"},
    {"emoji": "💫", "name": "Наталья Гудкова", "title": "Звёздный путь"},
    {"emoji": "🌊", "name": "Елена Клыкова", "title": "Морская ведьма"},
]

SURVEYS_FILE = 'surveys.json'

def ensure_surveys_file():
    """Создаёт файл если его нет"""
    if not os.path.exists(SURVEYS_FILE):
        with open(SURVEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def load_surveys():
    """Загружает все анкеты"""
    ensure_surveys_file()
    try:
        with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} surveys")
            return data
    except Exception as e:
        logger.error(f"Error loading surveys: {e}")
        return []

def save_surveys(surveys):
    """Сохраняет анкеты"""
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
    if not data.get('status'):
        return False, 'Status is required'
    if not data.get('goal'):
        return False, 'Goal is required'
    if not data.get('source'):
        return False, 'Source is required'
    return True, 'Valid'

# ============ MAIN ROUTES ============

@app.route('/')
def index():
    """Главная страница с участницами"""
    logger.debug(f"Index page, user_id: {session.get('user_id')}")
    return render_template('index.html', members=MEMBERS)

@app.route('/survey')
def survey():
    """Страница анкеты"""
    logger.debug(f"Survey page, user_id: {session.get('user_id')}")
    return render_template('survey.html')

@app.route('/profile')
def profile():
    """Страница профиля"""
    logger.debug(f"Profile page, user_id: {session.get('user_id')}")
    return render_template('profile.html')

# ============ API ROUTES - SURVEY ============

@app.route('/api/submit_survey', methods=['POST'])
def api_submit_survey():
    """Отправка анкеты"""
    try:
        data = request.json
        logger.info(f"Submitting survey: {data.get('name')}")
        
        # Валидация
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
            'status': data.get('status', ''),
            'children': data.get('children', ''),
            'interests': data.get('interests', ''),
            'topics': data.get('topics', ''),
            'goal': data.get('goal', ''),
            'source': data.get('source', ''),
            'applicationStatus': 'pending',
            'timestamp': datetime.now().isoformat()
        }
        
        surveys.append(new_survey)
        
        if not save_surveys(surveys):
            logger.error("Failed to save surveys")
            return jsonify({'success': False, 'error': 'Failed to save survey'}), 500
        
        # Сохраняем в сессию
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
    """Legacy endpoint для совместимости"""
    return api_submit_survey()

# ============ API ROUTES - PROFILE ============

@app.route('/api/profile', methods=['GET'])
def api_get_profile():
    """Получить профиль текущего пользователя"""
    try:
        user_id = session.get('user_id')
        logger.debug(f"Getting profile for user_id: {user_id}")
        
        if not user_id:
            logger.warning("No user_id in session")
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
            logger.warning(f"Profile not found for user {user_id}")
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
    """Legacy endpoint для совместимости"""
    return api_get_profile()

@app.route('/api/profiles', methods=['GET'])
def api_get_all_profiles():
    """Получить все анкеты (для администраторов)"""
    try:
        surveys = load_surveys()
        logger.info(f"Fetched {len(surveys)} profiles")
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
            logger.info(f"Retrieved profile {profile_id}")
            return jsonify({
                'success': True,
                'profile': profile
            }), 200
        else:
            logger.warning(f"Profile {profile_id} not found")
            return jsonify({
                'success': False,
                'message': 'Profile not found'
            }), 404
    except Exception as e:
        logger.error(f"Error in api_get_profile_by_id: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/profile/<int:profile_id>/status', methods=['PUT'])
def api_update_profile_status(profile_id):
    """Обновить статус анкеты"""
    try:
        data = request.json
        new_status = data.get('status')  # pending, approved, rejected
        
        if new_status not in ['pending', 'approved', 'rejected']:
            logger.warning(f"Invalid status: {new_status}")
            return jsonify({
                'success': False,
                'error': 'Invalid status'
            }), 400
        
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
                    logger.error(f"Failed to save surveys after status update")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to update status'
                    }), 500
        
        logger.warning(f"Profile {profile_id} not found for status update")
        return jsonify({
            'success': False,
            'message': 'Profile not found'
        }), 404
        
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
                # Обновляем только разрешённые поля
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
                return jsonify({
                    'success': True,
                    'message': 'Profile deleted'
                }), 200
            else:
                return jsonify({'success': False, 'error': 'Failed to delete profile'}), 500
        else:
            logger.warning(f"Profile {profile_id} not found for deletion")
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
            
    except Exception as e:
        logger.error(f"Error in api_delete_profile: {e}", exc_info=True)
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
        pending = sum(1 for s in surveys if s.get('applicationStatus') == 'pending')
        approved = sum(1 for s in surveys if s.get('applicationStatus') == 'approved')
        rejected = sum(1 for s in surveys if s.get('applicationStatus') == 'rejected')
        
        logger.info(f"Stats: total={len(surveys)}, pending={pending}, approved={approved}, rejected={rejected}")
        
        return jsonify({
            'success': True,
            'total': len(surveys),
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'members': len(MEMBERS)
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
        'version': '1.0.0',
        'members': len(MEMBERS)
    }), 200

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    """404 handler"""
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """405 handler"""
    logger.warning(f"405 Method Not Allowed: {request.method} {request.path}")
    return jsonify({'success': False, 'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def server_error(error):
    """500 handler"""
    logger.error(f"500 Server Error: {error}", exc_info=True)
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ============ BEFORE REQUEST ============

@app.before_request
def before_request():
    """Логирует каждый запрос"""
    logger.debug(f"{request.method} {request.path}")

@app.after_request
def after_request(response):
    """Логирует ответ"""
    logger.debug(f"Response: {response.status_code}")
    return response

# ============ MAIN ============

if __name__ == '__main__':
    ensure_surveys_file()
    logger.info("=" * 50)
    logger.info("Starting Witch Club MiniApp")
    logger.info(f"Members count: {len(MEMBERS)}")
    logger.info("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
