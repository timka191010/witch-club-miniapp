import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor

# ==== PATHS FOR VERCEL ====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.secret_key = os.getenv('SECRET_KEY', 'witch_club_secret_key_2026')

# ==================== DATABASE ====================

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

# ==================== HELPERS ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== PUBLIC ROUTES ====================

@app.route('/', methods=['GET'])
def index():
    members = [
        {'name': 'Мария Зуева', 'title': 'Верховная Ведьма', 'emoji': '🔮', 'title_emoji': '👑'},
        {'name': 'Юлия Пиндюрина', 'title': 'Ведьма Звёздного Пути', 'emoji': '✨', 'title_emoji': '⭐'},
        {'name': 'Елена Клыкова', 'title': 'Ведьма Трав и Эликсиров', 'emoji': '🌿', 'title_emoji': '🌿'},
        {'name': 'Наталья Гудкова', 'title': 'Ведьма Огненного Круга', 'emoji': '🕯️', 'title_emoji': '🔥'},
        {'name': 'Екатерина Когай', 'title': 'Ведьма Лунного Света', 'emoji': '🌙', 'title_emoji': '🌙'},
        {'name': 'Елена Пустовит', 'title': 'Ведьма Кристаллов', 'emoji': '💎', 'title_emoji': '💎'},
        {'name': 'Елена Провосуд', 'title': 'Ведьма Грозовых Ветров', 'emoji': '⚡', 'title_emoji': '⚡'}
    ]
    return render_template('index.html', members=members)

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

# ==================== PROFILE ====================

@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

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

# ==================== ADMIN ====================

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

# ==================== VERCEL ====================

app.debug = False
