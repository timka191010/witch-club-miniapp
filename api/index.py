import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.secret_key = os.getenv('SECRET_KEY', 'witch_club_secret_key_2026')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def get_db_connection():
    DATABASE_URL = os.getenv('POSTGRES_URL')
    if not DATABASE_URL:
        raise Exception("POSTGRES_URL environment variable not set")
    conn = psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor,
        sslmode='require'
    )
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                age TEXT NOT NULL,
                family_status TEXT NOT NULL,
                children TEXT NOT NULL,
                hobbies TEXT NOT NULL,
                themes TEXT NOT NULL,
                goal TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS club_members (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL UNIQUE,
                real_name TEXT NOT NULL,
                witch_name TEXT NOT NULL,
                witch_title TEXT NOT NULL,
                emoji TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

try:
    init_db()
except Exception as e:
    print(f"Failed to initialize database: {e}")

def generate_witch_name(real_name):
    prefixes = [
        "Тёмная", "Светлая", "Лунная", "Звёздная",
        "Огненная", "Водная", "Ледяная", "Грозовая", "Ветряная",
        "Таинственная", "Древняя", "Мудрая", "Вечная", "Ночная",
        "Серебряная", "Золотая", "Багровая", "Изумрудная", "Сапфировая",
        "Загадочная", "Могущественная", "Прекрасная", "Дикая", "Свободная",
        "Величественная", "Безмолвная", "Шёпчущая", "Поющая", "Танцующая",
        "Блуждающая", "Странствующая", "Вещая", "Провидящая", "Всевидящая",
        "Хрустальная", "Жемчужная", "Бархатная", "Шелковая", "Атласная"
    ]
    
    titles = [
        "Ведьма Лунного Света", "Ведьма Звёздного Пути", 
        "Ведьма Огненного Круга", "Ведьма Грозовых Ветров",
        "Ведьма Трав и Эликсиров", "Ведьма Кристаллов",
        "Ведьма Тёмного Леса", "Ведьма Серебряных Рун",
        "Ведьма Вечного Пламени", "Ведьма Небесных Врат",
        "Хранительница Древних Тайн", "Повелительница Стихий",
        "Госпожа Теней", "Владычица Снов", "Королева Ночи",
        "Ведьма Алых Закатов", "Ведьма Бирюзовых Волн",
        "Ведьма Шёпота Ветра", "Ведьма Танца Пламени",
        "Ведьма Зеркальных Озёр", "Ведьма Горных Вершин",
        "Хранительница Рассвета", "Повелительница Туманов",
        "Госпожа Морозных Узоров", "Владычица Цветущих Полей",
        "Ведьма Звёздной Пыли", "Ведьма Лунных Дорожек",
        "Ведьма Радужных Мостов", "Ведьма Северного Сияния",
        "Хранительница Сокровенных Знаний", "Повелительница Времени",
        "Госпожа Вечности", "Владычица Судеб",
        "Ведьма Серебряного Зеркала", "Ведьма Золотого Ключа",
        "Ведьма Изумрудного Сада", "Ведьма Сапфирового Неба",
        "Ведьма Алмазных Россыпей", "Ведьма Янтарных Слёз",
        "Хранительница Забытых Миров", "Повелительница Иллюзий"
    ]
    
    emojis = [
        "🔮", "✨", "🌙", "⚡", "🕯️", "💎", "🌿", "🔥", "❄️", "🌟",
        "🌺", "🦋", "🐉", "🦅", "🦢", "🌸", "🍃", "💫", "⭐", "🌊",
        "🏔️", "🌈", "☄️", "🌪️", "🌑", "🌕", "🌗", "🌘", "🪐", "🌌",
        "🦉", "🕷️", "🌹", "🥀", "🍄", "🗝️", "📿", "🧿", "🔱", "⚜️"
    ]
    
    prefix = random.choice(prefixes)
    witch_name = f"{prefix} {real_name}"
    title = random.choice(titles)
    emoji = random.choice(emojis)
    
    return {
        "witch_name": witch_name,
        "title": title,
        "emoji": emoji
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM club_members ORDER BY added_at ASC')
        members = cur.fetchall()
        cur.close()
        conn.close()
        
        members_list = [{
            'name': m['witch_name'],
            'title': m['witch_title'],
            'emoji': m['emoji']
        } for m in members]
        
        default_members = [
            {'name': 'Мария Зуева', 'title': 'Верховная Ведьма', 'emoji': '🔮'},
            {'name': 'Юлия Пиндюрина', 'title': 'Ведьма Звёздного Пути', 'emoji': '✨'},
            {'name': 'Елена Клыкова', 'title': 'Ведьма Трав и Эликсиров', 'emoji': '🌿'},
            {'name': 'Наталья Гудкова', 'title': 'Ведьма Огненного Круга', 'emoji': '🕯️'},
            {'name': 'Екатерина Когай', 'title': 'Ведьма Лунного Света', 'emoji': '🌙'},
            {'name': 'Елена Пустовит', 'title': 'Ведьма Кристаллов', 'emoji': '💎'},
            {'name': 'Елена Провосуд', 'title': 'Ведьма Грозовых Ветров', 'emoji': '⚡'},
            {'name': 'Анна Моисеева', 'title': 'Ведьма Таинственных Снов', 'emoji': '🌌'}
        ]
        
        final_members = []
        
        for default in default_members:
            found = next((m for m in members_list if default['name'].split()[-1] in m['name']), None)
            if found:
                final_members.append(found)
            else:
                final_members.append(default)
        
        default_last_names = [d['name'].split()[-1] for d in default_members]
        for m in members_list:
            is_default = any(last_name in m['name'] for last_name in default_last_names)
            if not is_default:
                final_members.append(m)
        
        return render_template('index.html', members=final_members)
    except Exception as e:
        print(f"Index error: {e}")
        members = [
            {'name': 'Мария Зуева', 'title': 'Верховная Ведьма', 'emoji': '🔮'},
            {'name': 'Юлия Пиндюрина', 'title': 'Ведьма Звёздного Пути', 'emoji': '✨'},
            {'name': 'Елена Клыкова', 'title': 'Ведьма Трав и Эликсиров', 'emoji': '🌿'},
            {'name': 'Наталья Гудкова', 'title': 'Ведьма Огненного Круга', 'emoji': '🕯️'},
            {'name': 'Екатерина Когай', 'title': 'Ведьма Лунного Света', 'emoji': '🌙'},
            {'name': 'Елена Пустовит', 'title': 'Ведьма Кристаллов', 'emoji': '💎'},
            {'name': 'Елена Провосуд', 'title': 'Ведьма Грозовых Ветров', 'emoji': '⚡'},
            {'name': 'Анна Моисеева', 'title': 'Ведьма Таинственных Снов', 'emoji': '🌌'}
        ]
        return render_template('index.html', members=members)

@app.route('/survey', methods=['GET'])
def survey():
    return render_template('survey.html')

@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

@app.route('/submit', methods=['POST'])
def submit_application():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM applications WHERE user_id = %s', (data['user_id'],))
        existing = cur.fetchone()
        if existing:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Вы уже подавали заявку!'})
        cur.execute('''
            INSERT INTO applications 
            (user_id, name, age, family_status, children, hobbies, themes, goal, source, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['user_id'], data['name'], data['age'], data['family_status'],
            data['children'], data['hobbies'], data['themes'], data['goal'],
            data['source'], 'pending'
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Анкета отправлена!'})
    except Exception as e:
        print(f"Error submitting application: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при отправке'})

@app.route('/api/user_status/<int:user_id>', methods=['GET'])
def user_status(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM applications WHERE user_id = %s', (user_id,))
        application = cur.fetchone()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'application': dict(application) if application else None
        })
    except Exception as e:
        print(f"User status error for {user_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Ошибка проверки статуса'
        }), 500

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == 'witch2026':
        session['admin_logged_in'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Неверные данные'})

@app.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/applications', methods=['GET'])
@login_required
def admin_applications():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM applications ORDER BY created_at DESC')
        applications = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({'success': True, 'applications': [dict(app) for app in applications]})
    except Exception as e:
        print(f"Error fetching applications: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при загрузке'})

@app.route('/admin/application/<int:app_id>', methods=['GET'])
@login_required
def admin_view_application(app_id):
    return render_template('admin_view_application.html', app_id=app_id)

@app.route('/admin/application/<int:app_id>/data', methods=['GET'])
@login_required
def admin_application_data(app_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM applications WHERE id = %s', (app_id,))
        application = cur.fetchone()
        cur.close()
        conn.close()
        if application:
            return jsonify({'success': True, 'application': dict(application)})
        return jsonify({'success': False, 'message': 'Заявка не найдена'})
    except Exception as e:
        print(f"Error fetching application: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при загрузке'})

@app.route('/admin/application/<int:app_id>/status', methods=['POST'])
@login_required
def update_application_status(app_id):
    try:
        data = request.get_json()
        status = data['status']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE applications SET status = %s WHERE id = %s', (status, app_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating status: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при обновлении'})

@app.route('/admin/application/<int:app_id>/add_to_club', methods=['POST'])
@login_required
def add_to_club(app_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM applications WHERE id = %s', (app_id,))
        app = cur.fetchone()
        
        if not app:
            return jsonify({'success': False, 'message': 'Заявка не найдена'})
        
        cur.execute('SELECT * FROM club_members WHERE user_id = %s', (app['user_id'],))
        existing = cur.fetchone()
        if existing:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Уже в клубе!'})
        
        witch_data = generate_witch_name(app['name'])
        
        cur.execute('''
            INSERT INTO club_members (user_id, real_name, witch_name, witch_title, emoji)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            app['user_id'],
            app['name'],
            witch_data['witch_name'],
            witch_data['title'],
            witch_data['emoji']
        ))
        
        cur.execute('UPDATE applications SET status = %s WHERE id = %s', ('approved', app_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'witch_data': witch_data
        })
    except Exception as e:
        print(f"Add to club error: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при добавлении'})

@app.route('/admin/application/<int:app_id>/remove_from_club', methods=['POST'])
@login_required
def remove_from_club(app_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM applications WHERE id = %s', (app_id,))
        app = cur.fetchone()
        
        if not app:
            return jsonify({'success': False, 'message': 'Заявка не найдена'})
        
        cur.execute('DELETE FROM club_members WHERE user_id = %s', (app['user_id'],))
        cur.execute('UPDATE applications SET status = %s WHERE id = %s', ('pending', app_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Remove from club error: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при удалении'})

@app.route('/admin/club_member/<int:user_id>/edit', methods=['POST'])
@login_required
def edit_club_member(user_id):
    try:
        data = request.get_json()
        witch_name = data.get('witch_name', '').strip()
        witch_title = data.get('witch_title', '').strip()
        emoji = data.get('emoji', '').strip()
        
        if not witch_name or not witch_title or not emoji:
            return jsonify({'success': False, 'message': 'Все поля обязательны'})
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE club_members 
            SET witch_name = %s, witch_title = %s, emoji = %s
            WHERE user_id = %s
        ''', (witch_name, witch_title, emoji, user_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Edit club member error: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при редактировании'})

@app.route('/admin/club_member/<int:user_id>/data', methods=['GET'])
@login_required
def get_club_member_data(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM club_members WHERE user_id = %s', (user_id,))
        member = cur.fetchone()
        cur.close()
        conn.close()
        
        if member:
            return jsonify({'success': True, 'member': dict(member)})
        return jsonify({'success': False, 'message': 'Участница не найдена'})
    except Exception as e:
        print(f"Get club member error: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при загрузке'})

@app.route('/admin/stats', methods=['GET'])
@login_required
def admin_stats():
    return render_template('admin_stats.html')

@app.route('/admin/stats/data', methods=['GET'])
@login_required
def admin_stats_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) as count FROM applications')
        total = cur.fetchone()['count']
        cur.execute('SELECT status, COUNT(*) as count FROM applications GROUP BY status')
        by_status = cur.fetchall()
        cur.execute('SELECT * FROM applications ORDER BY created_at DESC LIMIT 10')
        recent = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({
            'success': True, 
            'total': total, 
            'by_status': [dict(item) for item in by_status],
            'recent': [dict(item) for item in recent]
        })
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при загрузке'})

@app.route('/admin/logout', methods=['GET'])
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

app.debug = False
