from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

TELEGRAM_BOT_TOKEN = '8500508012:AAEMuWXEsZsUfiDiOV50xFw928Tn7VUJRH8'
TELEGRAM_CHAT_ID = '-5015136189'

DATA_DIR = '/tmp'
SURVEYS_FILE = os.path.join(DATA_DIR, 'surveys.json')

def load_json(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_json(filepath, data):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def send_telegram(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}, timeout=5)
    except:
        pass

@app.route('/', methods=['GET'])
def index():
    return jsonify({'status': 'ok', 'message': 'Witch Club API'})

@app.route('/api/survey', methods=['POST', 'OPTIONS'])
def submit_survey():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'error': 'Name required'}), 400
        
        surveys = load_json(SURVEYS_FILE)
        if not isinstance(surveys, dict):
            surveys = {}
        
        survey_id = str(len(surveys) + 1)
        
        surveys[survey_id] = {
            'id': survey_id,
            'name': name,
            'birthDate': data.get('birthDate', ''),
            'telegramUsername': data.get('telegramUsername', ''),
            'familyStatus': data.get('familyStatus', ''),
            'children': data.get('children', ''),
            'interests': data.get('interests', ''),
            'topics': data.get('topics', ''),
            'goal': data.get('goal', ''),
            'source': data.get('source', ''),
            'status': 'pending',
            'createdAt': datetime.now().isoformat()
        }
        
        if save_json(SURVEYS_FILE, surveys):
            send_telegram(TELEGRAM_CHAT_ID, f"📝 Новая заявка: {name}")
            return jsonify({'success': True, 'survey': surveys[survey_id]}), 200
        
        return jsonify({'error': 'Save failed'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/surveys', methods=['GET'])
def get_surveys():
    try:
        surveys = load_json(SURVEYS_FILE)
        return jsonify(list(surveys.values()) if isinstance(surveys, dict) else []), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
