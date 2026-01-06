from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

RESPONSES_FILE = 'responses.json'

def load_responses():
    if os.path.exists(RESPONSES_FILE):
        try:
            with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_responses(responses):
    with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)

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
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #e0e0e0;
        }
        .container {
            max-width: 500px;
            width: 100%;
            background: rgba(30, 20, 50, 0.9);
            border: 2px solid #8b7bb8;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        h1 { font-size: 28px; margin-bottom: 10px; color: #ffd700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
        .tagline { font-size: 14px; color: #b19cd9; font-style: italic; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-size: 14px; color: #c4a7d6; font-weight: bold; }
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
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #ffd700;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
            background: rgba(255, 255, 255, 0.1);
        }
        textarea { resize: vertical; min-height: 80px; }
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
        button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.5); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .success-message { display: none; text-align: center; color: #4ade80; padding: 20px; background: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; border-radius: 8px; margin-bottom: 20px; }
        .error-message { display: none; text-align: center; color: #ef4444; padding: 20px; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; margin-bottom: 20px; }
        .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #8b7bb8; }
    </style>
</head>
<body>
    <div class="container">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1>👑 Ведьмы Не Стареют 👑</h1>
            <p class="tagline">Священный клуб магических сестёр</p>
        </div>

        <div class="success-message" id="successMsg">
            ✅ Ваша заявка успешно отправлена!<br>
            Спасибо за интерес. Мы свяжемся с вами вскоре.
        </div>

        <div class="error-message" id="errorMsg"></div>

        <form id="surveyForm">
            <div class="form-group">
                <label>📝 Имя *</label>
                <input type="text" name="name" placeholder="Как вас зовут?" required>
            </div>

            <div class="form-group">
                <label>💬 Telegram @</label>
                <input type="text" name="telegramUsername" placeholder="username (без @)">
            </div>

            <button type="submit">✨ Отправить ✨</button>
        </form>

        <div class="footer">
            <p>🔮 Добро пожаловать в наш священный круг 🔮</p>
        </div>
    </div>

    <script>
        document.getElementById('surveyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const name = document.querySelector('input[name="name"]').value;
            const telegramUsername = document.querySelector('input[name="telegramUsername"]').value;

            try {
                const response = await fetch('/api/survey', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, telegramUsername })
                });

                if (response.ok) {
                    document.getElementById('surveyForm').reset();
                    document.getElementById('successMsg').style.display = 'block';
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
    </script>
</body>
</html>'''

@app.route('/api/survey', methods=['POST'])
def survey():
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Имя обязательно'}), 400
        
        response = {
            'timestamp': datetime.now().isoformat(),
            'name': data.get('name', '').strip(),
            'telegramUsername': data.get('telegramUsername', '').strip()
        }
        
        responses = load_responses()
        responses.append(response)
        save_responses(responses)
        
        return jsonify({'success': True, 'message': 'Спасибо! Ваша заявка принята.'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@app.route('/api/responses', methods=['GET'])
def get_responses():
    try:
        responses = load_responses()
        return jsonify({'success': True, 'count': len(responses), 'responses': responses}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        responses = load_responses()
        return jsonify({'success': True, 'total': len(responses)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Witch Club API running'}), 200

if __name__ == '__main__':
    app.run(debug=True)
