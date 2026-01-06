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
            with open(filepath, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_json(filepath, data):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
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
    return jsonify({'status': 'ok'})

@app.route('/api/survey', methods=['POST'])
def submit_survey():
    try:
        data = request.json
        if not data.get('name'):
            return jsonify({'error': 'Name required'}), 400
        
        surveys = load_json(SURVEYS_FILE)
        survey_id = str(len(surveys) + 1)
        
        surveys[survey_id] = {
            'id': survey_id,
            'name': data.get('name'),
            'telegramUsername': data.get('telegramUsername'),
            'status': 'pending',
            'createdAt': datetime.now().isoformat()
        }
        
        save_json(SURVEYS_FILE, surveys)
        send_telegram(TELEGRAM_CHAT_ID, f"📝 Новая заявка: {data.get('name')}")
        
        return jsonify({'success': True, 'survey': surveys[survey_id]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/surveys', methods=['GET'])
def get_surveys():
    surveys = load_json(SURVEYS_FILE)
    return jsonify(list(surveys.values()))

handler = app

if __name__ == '__main__':
    app.run()
