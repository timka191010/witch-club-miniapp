import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'witch_club_secret_key_2026')

# Получаем DATABASE_URL из переменных окружения Vercel
DATABASE_URL = os.getenv('POSTGRES_URL')

# Админ логин/пароль
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'witch2026'

# Участницы клуба с титулами (Основательницы)
MEMBERS = [
    {'name': 'Мария Зуева', 'title': '👑 Верховная Ведьма', 'emoji': '🔮', 'color': '#8B008B'},
    {'name': 'Юлия Пиндюрина', 'title': '🌟 Ведьма Звёздного Пути', 'emoji': '✨', 'color': '#4B0082'},
    {'name': 'Елена Клыкова', 'title': '🌿 Ведьма Трав и Эликсиров', 'emoji': '🍃', 'color': '#2E8B57'},
    {'name': 'Наталья Гудкова', 'title': '🔥 Ведьма Огненного Круга', 'emoji': '🕯️', 'color': '#DC143C'},
    {'name': 'Екатерина Когай', 'title': '🌙 Ведьма Лунного Света', 'emoji': '🌕', 'color': '#483D8B'},
    {'name': 'Елена Пустовит', 'title': '💎 Ведьма Кристаллов', 'emoji': '💠', 'color': '#00CED1'},
    {'name': 'Елена Провосуд', 'title': '⚡ Ведьма Грозовых Ветров', 'emoji': '🌪️', 'color': '#FF6347'},
    {'name': 'Анна Моисеева', 'title': '🦋 Ведьма Превращений', 'emoji': '🦋', 'color': '#9370DB'}
]

# Функции работы с БД
def get_db_connection():
    """Подключение к PostgreSQL"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    """Создание таблиц"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Таблица анкет
    cur.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            name VARCHAR(255) NOT NULL,
            age VARCHAR(50),
            family_status VARCHAR(50),
            children TEXT,
            hobbies TEXT,
            themes TEXT,
            goal TEXT,
            source VARCHAR(255),
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица участниц
    cur.execute('''
        CREATE TABLE IF NOT EXISTS club_members (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            emoji VARCHAR(10) NOT NULL,
            color VARCHAR(20) NOT NULL,
            user_id BIGINT UNIQUE,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

# Инициализация БД при первом запуске
try:
    init_db()
except:
    pass

# Генераторы титулов
def generate_witch_title():
    prefixes = ["Ведьма", "Хранительница", "Повелительница", "Мастер", "Волшебница"]
    themes = ["Теней и Тайн", "Лунного Света", "Звёздного Пути", "Огненного Круга", "Кристальных Снов"]
    return f"{random.choice(prefixes)} {random.choice(themes)}"

def generate_witch_emoji():
    return random.choice(["🔮", "✨", "🌙", "🔥", "💎", "⚡", "🌟", "🦋"])

def generate_witch_color():
    return random.choice(["#8B008B", "#4B0082", "#2E8B57", "#DC143C", "#483D8B", "#00CED1"])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Главная страница"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM club_members ORDER BY joined_at DESC')
    db_members = cur.fetchall()
    cur.close()
    conn.close()
    
    all_members = MEMBERS + [dict(m) for m in db_members]
    return render_template('index.html', members=all_members)

@app.route('/api/submit_application', methods=['POST'])
def submit_application():
    """Сохранение анкеты"""
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO applications (user_id, name, age, family_status, children, hobbies, themes, goal, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['user_id'], data['name'], data['age'], data['family_status'],
            data['children'], data['hobbies'], data['themes'], data['goal'], data['source']
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Анкета принята!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/user_status/<int:user_id>', methods=['GET'])
def get_user_status(user_id):
    """Статус анкеты"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT status, name, created_at FROM applications WHERE user_id = %s ORDER BY created_at DESC LIMIT 1', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        return jsonify({'exists': True, 'status': row['status'], 'name': row['name'], 'created_at': str(row['created_at'])})
    return jsonify({'exists': False})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Вход админа"""
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error='Неверный логин или пароль')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """Админ панель"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM applications ORDER BY created_at DESC')
    applications = [dict(row) for row in cur.fetchall()]
    
    cur.execute('SELECT * FROM club_members ORDER BY joined_at DESC')
    club_members = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    stats = {
        'total': len(applications),
        'married': sum(1 for a in applications if 'married' in str(a.get('family_status', '')).lower()),
        'with_kids': sum(1 for a in applications if 'нет' not in str(a.get('children', '')).lower())
    }
    
    return render_template('admin_dashboard.html', applications=applications, stats=stats, members=MEMBERS, club_members=club_members)

@app.route('/admin/application/<int:app_id>')
@login_required
def view_application(app_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM applications WHERE id = %s', (app_id,))
    application = cur.fetchone()
    cur.close()
    conn.close()
    
    if not application:
        return "Анкета не найдена", 404
    return render_template('admin_view_application.html', app=dict(application))

@app.route('/admin/application/<int:app_id>/approve', methods=['POST'])
@login_required
def approve_application(app_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE applications SET status = %s WHERE id = %s', ('approved', app_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('view_application', app_id=app_id))

@app.route('/admin/application/<int:app_id>/reject', methods=['POST'])
@login_required
def reject_application(app_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE applications SET status = %s WHERE id = %s', ('rejected', app_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('view_application', app_id=app_id))

@app.route('/admin/application/<int:app_id>/add_to_club', methods=['POST'])
@login_required
def add_to_club(app_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM applications WHERE id = %s', (app_id,))
    application = dict(cur.fetchone())
    
    title = generate_witch_title()
    emoji = generate_witch_emoji()
    color = generate_witch_color()
    
    try:
        cur.execute('''
            INSERT INTO club_members (name, title, emoji, color, user_id)
            VALUES (%s, %s, %s, %s, %s)
        ''', (application['name'], title, emoji, color, application['user_id']))
        
        cur.execute('UPDATE applications SET status = %s WHERE id = %s', ('approved', app_id))
        conn.commit()
    except:
        pass
    
    cur.close()
    conn.close()
    return redirect(url_for('view_application', app_id=app_id))

@app.route('/admin/remove_from_club/<int:user_id>', methods=['POST'])
@login_required
def remove_from_club(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM club_members WHERE user_id = %s', (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/clear_applications', methods=['POST'])
@login_required
def clear_applications():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM applications')
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# Для Vercel
app = app
