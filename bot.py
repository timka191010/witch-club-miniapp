from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8500508012:AAEMuWXEsZsUfiDiOV50xFw928Tn7VUJRH8"  # токен от BotFather

WEBAPP_URL = "https://witch-club-miniapp.vercel.app"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(
        "🌙 Открыть Клуб Ведьм",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )]]
    await update.message.reply_text(
        "✨ Добро пожаловать в Клуб Ведьм!\n\nНажми кнопку ниже, чтобы открыть приложение:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Бот запущен. Напиши ему /start")
    app.run_polling()

if __name__ == "__main__":
    main()
