from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'witch-club-secret'

# ===== КАК НА ФОТО =====
MEMBERS = [
    {"emoji": "🔮", "name": "Мария Зуева", "title": "👑 Верховная Ведьма"},
    {"emoji": "✨", "name": "Юлия Пиндюрина", "title": "⭐ Ведьма Звёздного Пути"},
    {"emoji": "🌿", "name": "Елена Клыкова", "title": "🌿 Ведьма Трав и Эликсиров"},
    {"emoji": "🕯️", "name": "Наталья Гудкова", "title": "🔥 Ведьма Огненного Круга"},
    {"emoji": "🌕", "name": "Екатерина Когай", "title": "🌙 Ведьма Лунного Света"},
    {"emoji": "💎", "name": "Елена Пустовит", "title": "💎 Ведьма Кристаллов"},
    {"emoji": "🌪️", "name": "Елена Правосуд", "title": "⚡ Ведьма Грозовых Ветров"},
    {"emoji": "🦋", "name": "Анна Моисеева", "title": "🦋 Ведьма Превращений"},
]

SURVEYS_FILE = '/tmp/surveys.json'

def load_surveys():
    if os.path.exists(SURVEYS_FILE):
        try:
            with open(SURVEYS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def save_surveys(data):
    try:
        with open(SURVEYS_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except:
        return False

@app.route('/api', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'members': len(MEMBERS)})

@app.route('/api/members', methods=['GET'])
def get_members():
    return jsonify({'members': MEMBERS})

@app.route('/api/submit_survey', methods=['POST'])
def submit():
    try:
        data = request.json
        surveys = load_surveys()
        
        next_id = max([s.get('id', 0) for s in surveys], default=0) + 1
        survey = {
            'id': next_id,
            'name': data.get('name'),
            'status': data.get('status'),
            'goal': data.get('goal'),
            'source': data.get('source'),
            'timestamp': datetime.now().isoformat()
        }
        
        surveys.append(survey)
        save_surveys(surveys)
        
        session['user_id'] = next_id
        session['user_name'] = survey['name']
        
        return jsonify({'success': True, 'id': next_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    surveys = load_surveys()
    for s in surveys:
        if s.get('id') == user_id:
            return jsonify({'success': True, 'profile': s})
    return jsonify({'success': False}), 404

@app.route('/submit_survey', methods=['POST'])
def submit_legacy():
    return submit()

@app.route('/get_profile', methods=['GET'])
def get_profile_legacy():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False}), 401
    return get_profile(user_id)
