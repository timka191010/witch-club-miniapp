from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'witch_club_secret_2024'

DATA_FILE = 'data.json'
ADMIN_PASSWORD = '123'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'applications': []}
    return {'applications': []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===================== ГЛАВНАЯ ФОРМА =====================

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
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
        }
        h1 { 
            font-size: 28px; 
            margin-bottom: 10px; 
            color: #ffd700; 
            text-align: center;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); 
        }
        .tagline { 
            font-size: 14px; 
            color: #b19cd9; 
            font-style: italic; 
            margin-bottom: 20px;
            text-align: center;
        }
        .form-group { margin-bottom: 20px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-size: 14px; 
            color: #c4a7d6; 
            font-weight: bold; 
        }
        input {
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
        input:focus {
            outline: none;
            border-color: #ffd700;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
            background: rgba(255, 255, 255, 0.1);
        }
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
        }
        button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.5); 
        }
        .message { 
            display: none; 
            text-align: center; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px;
            font-weight: bold;
        }
        .success { 
            background: rgba(74, 222, 128, 0.1); 
            border: 1px solid #4ade80;
            color: #4ade80;
        }
        .error { 
            background: rgba(239, 68, 68, 0.1); 
            border: 1px solid #ef4444;
            color: #ef4444;
        }
        .footer { 
            margin-top: 30px; 
            text-align: center; 
            font-size: 12px; 
            color: #8b7bb8; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>👑 Ведьмы Не Стареют 👑</h1>
        <p class="tagline">Священный клуб магических сестёр</p>

        <div class="message success" id="successMsg">✅ Заявка отправлена!</div>
        <div class="message error" id="errorMsg"></div>

        <form id="form">
            <div class="form-group">
                <label>📝 Имя *</label>
                <input type="text" name="name" placeholder="Как вас зовут?" required>
            </div>

            <div class="form-group">
                <label>💬 Telegram</label>
                <input type="text" name="telegram" placeholder="username">
            </div>

            <button type="submit">✨ Отправить ✨</button>
        </form>

        <div class="footer">
            <p>🔮 Добро пожаловать в наш священный круг 🔮</p>
        </div>
    </div>

    <script>
        document.getElementById('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.querySelector('input[name="name"]').value;
            const telegram = document.querySelector('input[name="telegram"]').value;

            try {
                const res = await fetch('/api/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, telegram })
                });

                if (res.ok) {
                    document.getElementById('form').reset();
                    document.getElementById('successMsg').style.display = 'block';
                    document.getElementById('errorMsg').style.display = 'none';
                } else {
                    const err = await res.json();
                    document.getElementById('errorMsg').textContent = '❌ ' + err.error;
                    document.getElementById('errorMsg').style.display = 'block';
                }
            } catch (e) {
                document.getElementById('errorMsg').textContent = '❌ Ошибка подключения';
                document.getElementById('errorMsg').style.display = 'block';
            }
        });
    </script>
</body>
</html>'''

# ===================== API =====================

@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'error': 'Имя обязательно'}), 400
        
        all_data = load_data()
        all_data['applications'].append({
            'id': len(all_data['applications']) + 1,
            'name': name,
            'telegram': data.get('telegram', '').strip(),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending'
        })
        save_data(all_data)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/change-status', methods=['POST'])
def change_status():
    if 'logged_in' not in session:
        return redirect(url_for('admin'))
    
    app_id = int(request.form.get('app_id', 0))
    new_status = request.form.get('status', 'pending')
    
    data = load_data()
    for app in data['applications']:
        if app['id'] == app_id:
            app['status'] = new_status
            save_data(data)
            break
    
    return redirect(url_for('admin'))

@app.route('/api/delete-app', methods=['POST'])
def delete_app():
    if 'logged_in' not in session:
        return redirect(url_for('admin'))
    
    app_id = int(request.form.get('app_id', 0))
    
    data = load_data()
    data['applications'] = [a for a in data['applications'] if a['id'] != app_id]
    save_data(data)
    
    return redirect(url_for('admin'))

# ===================== АДМИНКА =====================

@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        return render_template_string('''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Админка</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .login-box {
            max-width: 400px;
            width: 90%;
            padding: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        h1 { text-align: center; margin-bottom: 30px; color: #FFD700; }
        input {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: white;
            font-size: 16px;
        }
        input:focus { outline: none; border-color: #FFD700; }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #8B008B, #4B0082);
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { transform: translateY(-2px); }
        .error { color: #ff6b6b; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>👑 Админка</h1>
        {% if error %}<div class="error">❌ Неверный пароль</div>{% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="Пароль" required autofocus>
            <button type="submit">Войти</button>
        </form>
    </div>
</body>
</html>''', error=False)
    
    data = load_data()
    apps = data['applications']
    
    return render_template_string('''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Панель</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a0033, #330066);
            color: white;
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 10px;
        }
        h1 { color: #FFD700; }
        .logout-btn {
            padding: 10px 20px;
            background: #ff4444;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .logout-btn:hover { background: #cc0000; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-box {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-number { 
            font-size: 32px; 
            font-weight: bold; 
            color: #FFD700;
        }
        .stat-label { 
            font-size: 12px; 
            color: rgba(255, 255, 255, 0.7);
            margin-top: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            overflow: hidden;
        }
        th {
            background: rgba(255, 255, 255, 0.1);
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        tr:hover { background: rgba(255, 255, 255, 0.05); }
        .status {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }
        .pending { background: rgba(255, 165, 0, 0.2); color: #FFA500; }
        .approved { background: rgba(0, 255, 0, 0.2); color: #00FF00; }
        .rejected { background: rgba(255, 68, 68, 0.2); color: #FF4444; }
        .actions {
            display: flex;
            gap: 5px;
        }
        .btn-approve, .btn-reject, .btn-delete {
            padding: 5px 10px;
            border: none;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            color: white;
            font-weight: bold;
        }
        .btn-approve { background: #00AA00; }
        .btn-reject { background: #FF6600; }
        .btn-delete { background: #ff4444; }
        .btn-approve:hover { background: #008800; }
        .btn-reject:hover { background: #CC5200; }
        .btn-delete:hover { background: #cc0000; }
    </style>
</head>
<body>
    <div class="header">
        <h1>👑 Панель управления</h1>
        <a href="/admin/logout" class="logout-btn">Выход</a>
    </div>

    <div class="stats">
        <div class="stat-box">
            <div class="stat-number">{{ total }}</div>
            <div class="stat-label">Всего</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">{{ pending }}</div>
            <div class="stat-label">На проверке</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">{{ approved }}</div>
            <div class="stat-label">Одобрено</div>
        </div>
    </div>

    <h2 style="margin-bottom: 15px; color: #FFD700;">📋 Заявки</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Имя</th>
                <th>Telegram</th>
                <th>Дата</th>
                <th>Статус</th>
                <th>Действия</th>
            </tr>
        </thead>
        <tbody>
            {% for app in apps %}
            <tr>
                <td>{{ app.id }}</td>
                <td>{{ app.name }}</td>
                <td>{{ app.telegram or '-' }}</td>
                <td>{{ app.date }}</td>
                <td><span class="status {{ app.status }}">{{ app.status }}</span></td>
                <td>
                    <div class="actions">
                        <form method="POST" action="/api/change-status" style="display:inline;">
                            <input type="hidden" name="app_id" value="{{ app.id }}">
                            <input type="hidden" name="status" value="approved">
                            <button type="submit" class="btn-approve">✓</button>
                        </form>
                        <form method="POST" action="/api/change-status" style="display:inline;">
                            <input type="hidden" name="app_id" value="{{ app.id }}">
                            <input type="hidden" name="status" value="rejected">
                            <button type="submit" class="btn-reject">✗</button>
                        </form>
                        <form method="POST" action="/api/delete-app" style="display:inline;" onsubmit="return confirm(\'Удалить заявку?\');">
                            <input type="hidden" name="app_id" value="{{ app.id }}">
                            <button type="submit" class="btn-delete">-</button>
                        </form>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>''',
    total=len(apps),
    pending=len([a for a in apps if a['status'] == 'pending']),
    approved=len([a for a in apps if a['status'] == 'approved']),
    apps=apps
    )

@app.route('/admin', methods=['POST'])
def admin_login():
    password = request.form.get('password', '')
    if password == ADMIN_PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('admin'))
    else:
        return render_template_string('''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Админка</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .login-box {
            max-width: 400px;
            width: 90%;
            padding: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        h1 { text-align: center; margin-bottom: 30px; color: #FFD700; }
        input {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: white;
            font-size: 16px;
        }
        input:focus { outline: none; border-color: #FFD700; }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #8B008B, #4B0082);
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { transform: translateY(-2px); }
        .error { color: #ff6b6b; text-align: center; margin-bottom: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>👑 Админка</h1>
        <div class="error">❌ Неверный пароль</div>
        <form method="POST">
            <input type="password" name="password" placeholder="Пароль" required autofocus>
            <button type="submit">Войти</button>
        </form>
    </div>
</body>
</html>''', error=True)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
