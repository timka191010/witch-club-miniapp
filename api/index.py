from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
import random

# ... остальное как было ...

# ===== 8 ОРИГИНАЛЬНЫХ ВЕДЬМ =====
MEMBERS = [
    {"id": 1, "emoji": "🔮", "name": "Мария Зуева", "title": "👑 Верховная Ведьма"},
    {"id": 2, "emoji": "✨", "name": "Юлия Пиндюрина", "title": "⭐ Ведьма Звёздного Пути"},
    {"id": 3, "emoji": "🌿", "name": "Елена Клыкова", "title": "🌿 Ведьма Трав и Эликсиров"},
    {"id": 4, "emoji": "🕯️", "name": "Наталья Гудкова", "title": "🔥 Ведьма Огненного Круга"},
    {"id": 5, "emoji": "🌕", "name": "Екатерина Когай", "title": "🌙 Ведьма Лунного Света"},
    {"id": 6, "emoji": "💎", "name": "Елена Пустовит", "title": "💎 Ведьма Кристаллов"},
    {"id": 7, "emoji": "🌪️", "name": "Елена Правосуд", "title": "⚡ Ведьма Грозовых Ветров"},
    {"id": 8, "emoji": "🦋", "name": "Анна Моисеева", "title": "🦋 Ведьма Превращений"},
]

SURVEYS_FILE = '/tmp/surveys.json'

def get_next_member_id():
    """Получить следующий ID для новой участницы"""
    if not MEMBERS:
        return 1
    return max([m.get('id', 0) for m in MEMBERS], default=0) + 1

# ... остальной код ...

@app.route('/api/members', methods=['POST'])
def api_add_member():
    """Добавить новую участницу"""
    try:
        data = request.json
        name = data.get('name')
        title = data.get('title')
        emoji = data.get('emoji')
        
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        new_member = {
            'id': get_next_member_id(),  # ← ИЗМЕНЕНО
            'name': name,
            'title': title or '',
            'emoji': emoji or '🔮'
        }
        
        MEMBERS.append(new_member)
        logger.info(f"Added new member: {name}")
        
        return jsonify({
            'success': True,
            'member': new_member,
            'message': 'Member added'
        }), 201
        
    except Exception as e:
        logger.error(f"Error in api_add_member: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
