from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
import random

try:
    import requests
except ImportError:
    requests = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'public')

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
CORS(app, supports_credentials=True)
app.secret_key = 'witch-club-secret-2025-mystical-key-super-secure'
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 2592000

# TELEGRAM CONFIG
TELEGRAM_BOT_TOKEN = '8500508012:AAEMuWXEsZsUfiDiOV50xFw928Tn7VUJRH8'
TELEGRAM_CHAT_ID = '-5015136189'
TELEGRAM_CHAT_LINK = 'https://t.me/+S32BT0FT6w0xYTBi'

DATA_DIR = '/tmp'
MEMBERS_FILE = os.path.join(DATA_DIR, 'members.json')
SURVEYS_FILE = os.path.join(DATA_DIR, 'surveys.json')

# LISTS FOR RANDOM GENERATION
EMOJIS = ['🔮','🌙','🧿','✨','🕯️','🌑','🧙‍♀️','🌸','🕊️','🌊','🍂','❄️','🌻','🦉','🪙','💫','⭐','🔥','🌿','💎','⚡','🦋']

TITLES = [
    '👑 Верховная Ведьма',
    '⭐ Ведьма Звёздного Пути',
    '🌿 Ведьма Трав и Эликсиров',
    '🔥 Ведьма Огненного Круга',
    '🌙 Ведьма Лунного Света',
    '💎 Ведьма Кристаллов',
    '⚡ Ведьма Грозовых Ветров',
    '🦋 Ведьма Превращений',
    '🔮 Чародейка Утренних Туманов',
    '✨ Ведающая Путями Судьбы',
    '🌸 Магиня Звёздного Ветра',
    '🕊️ Берегиня Тишины',
    '🌑 Чтица Линий Времени',
    '🧿 Повелительница Чая и Таро',
    '🕯️ Хранительница Теней',
    '🌊 Ведьма Морских Глубин',
    '🍂 Ведьма Осенних Листьев',
    '❄️ Ведьма Ледяных Чар',
    '🌻 Ведьма Золотых Нитей',
    '🦉 Ведьма Ночной Мудрости',
    '🧙‍♀️ Волшебница Забытых Слов
