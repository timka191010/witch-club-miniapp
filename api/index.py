from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app, supports_credentials=True)
app.secret_key = 'witch-club-2025'

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

def load_surveys():
    if not os.path.exists(SURVEYS_FILE):
        return []
    try:
        with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_surveys(surveys):
    try:
        with open(SURVEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(surveys, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html', members=MEMBERS)

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    try:
        data = request.json
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
        save_surveys(surveys)
        
        session['user_id'] = next_id
        session['user_name'] = new_survey['name']
        
        return jsonify({'success': True, 'user_id': next_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/profile')
def api_profile():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'profile': None}), 401
        
        surveys = load_surveys()
        for survey in surveys:
            if survey.get('id') == user_id:
                return jsonify({'success': True, 'profile': survey}), 200
        
        return jsonify({'success': False, 'profile': None}), 404
    except:
        return jsonify({'success': False}), 500

@app.route('/get_profile')
def get_profile():
    return api_profile()

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)
