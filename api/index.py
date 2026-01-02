import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
import random
from datetime import datetime

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = os.getenv('SECRET_KEY', 'witch_club_secret_key_2026')

# ==================== DATABASE ====================

def get_db_connection():
    DATABASE_URL = os.getenv('POSTGRES_URL')
    if not DATABASE_URL:
        raise Exception("POSTGRES_URL environment variable not set")
    
    # Neon requires SSL
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

# Initialize database on startup
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

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_application():
    try:
        data = request.json
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if user already applied
        cur.execute('SELECT * FROM applications WHERE user_id = %s', (data['user_id'],))
        existing = cur.fetchone()
        
        if existing:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Вы уже подавали заявку!'})
        
        # Insert new application
        cur.execute('''
            INSERT INTO applications 
            (user_id, name, age, family_status, children, hobbies, themes, goal, source, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['user_id'],
            data['name'],
            data['age'],
            data['family_status'],
            data['children'],
            data['hobbies'],
            data['themes'],
            data['goal'],
            data['source'],
            'pending'
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Анкета отправлена!'})
    except Exception as e:
        print(f"Error submitting application: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при отправке'})

# ==================== ADMIN ====================

@app.route('/admin')
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    data = request.json
    
    if data['username'] == 'admin' and data['password'] == 'witch2026':
        session['admin_logged_in'] = True
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Неверные данные'})

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/applications')
@login_required
def admin_applications():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM applications ORDER BY created_at DESC')
        applications = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'applications': applications})
    except Exception as e:
        print(f"Error fetching applications: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при загрузке'})

@app.route('/admin/application/<int:app_id>')
@login_required
def admin_view_application(app_id):
    return render_template('admin_view_application.html', app_id=app_id)

@app.route('/admin/application/<int:app_id>/data')
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
            return jsonify({'success': True, 'application': application})
        return jsonify({'success': False, 'message': 'Заявка не найдена'})
    except Exception as e:
        print(f"Error fetching application: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при загрузке'})

@app.route('/admin/application/<int:app_id>/status', methods=['POST'])
@login_required
def update_application_status(app_id):
    try:
        data = request.json
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

@app.route('/admin/stats')
@login_required
def admin_stats():
    return render_template('admin_stats.html')

@app.route('/admin/stats/data')
@login_required
def admin_stats_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Total applications
        cur.execute('SELECT COUNT(*) as count FROM applications')
        total = cur.fetchone()['count']
        
        # By status
        cur.execute('SELECT status, COUNT(*) as count FROM applications GROUP BY status')
        by_status = cur.fetchall()
        
        # Recent applications
        cur.execute('SELECT * FROM applications ORDER BY created_at DESC LIMIT 10')
        recent = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'total': total,
            'by_status': by_status,
            'recent': recent
        })
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при загрузке'})

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# ==================== VERCEL ====================

# For Vercel serverless
app.debug = False
