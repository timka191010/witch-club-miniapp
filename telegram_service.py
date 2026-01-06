import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
INVITE_LINK = os.getenv('INVITE_LINK')

def send_approval_message(telegram_username, user_name):
    message = f"""🎉 <b>Поздравляем, {user_name}!</b> 🎉

<i>Вы успешно прошли отбор и приняты в наш священный клуб</i>
👑 <b>Ведьмы Не Стареют</b> 👑

Мы рады видеть вас в нашей магической семье ✨

<b>📍 Присоединяйтесь к нашему чату прямо сейчас:</b>
{INVITE_LINK}

Ждём вас в кругу сестёр! 🔮"""
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    try:
        response = requests.post(url, json={
            'chat_id': f'@{telegram_username}',
            'text': message,
            'parse_mode': 'HTML'
        }, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Сообщение отправлено {user_name}")
            return True
        else:
            print(f"⚠️ Ошибка: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def send_admin_notification(app_name, app_id):
    message = f"""✅ <b>НОВАЯ УЧАСТНИЦА</b> ✅

👤 Имя: <b>{app_name}</b>
🔢 ID заявки: <code>#{app_id}</code>

Поздравительное сообщение отправлено! 🎉"""
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    try:
        response = requests.post(url, json={
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Уведомление отправлено администраторам")
            return True
        else:
            print(f"⚠️ Ошибка: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
