import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import os
from flask import Flask
from threading import Thread

# 1. SOZLAMALAR
API_TOKEN = "8888334220:AAEDAzYUSwQcSgvZ35zYWIdai-7K5wNfJC4"
bot = telebot.TeleBot(API_TOKEN)
CHANNEL = "@Flmsssss"
CHANNEL_ID = -1003951637129 # Sening yangi ID'ing
ADMIN_ID = 7081484236
VIP_FILE = "vip_users.txt"

# ... (VIP va Obuna funksiyalari o'zgarishsiz) ...

def is_vip(user_id):
    today = datetime.date.today()
    if os.path.exists(VIP_FILE):
        with open(VIP_FILE, "r") as f:
            for line in f.read().splitlines():
                if ":" in line:
                    uid, end_date = line.split(":")
                    if str(user_id) == uid and today <= datetime.date.fromisoformat(end_date):
                        return True
    return False

def check_subscription(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def show_subscribe_menu(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
    markup.add(InlineKeyboardButton(text="🔄 Obuna bo'ldim", callback_data="check_sub"))
    bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun obuna bo'ling:", reply_markup=markup)

# KINO YUBORISH (KANAL ORQALI)
@bot.message_handler(func=lambda message: True)
def check_code(message):
    if not check_subscription(message.from_user.id) and not is_vip(message.from_user.id):
        show_subscribe_menu(message)
        return
    
    # Faqat raqam (ID) qabul qilamiz
    code = message.text.strip()
    if code.isdigit():
        try:
            bot.copy_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=int(code))
        except Exception as e:
            bot.reply_to(message, "❌ Kino topilmadi. Kodni (post ID) tekshiring.")
            print(f"Xato: {e}")
    else:
        bot.reply_to(message, "❌ Iltimos, kino kodini (raqam) yuboring.")

# SERVER QISMI
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"

def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
