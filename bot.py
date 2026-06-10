import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import os
from flask import Flask
from threading import Thread

# 1. SOZLAMALAR
API_TOKEN = "8888334220:AAEDAzYUSwQcSgvZ35zYWIdai-7K5wNfJC4"
bot = telebot.TeleBot(API_TOKEN)
CHANNEL = "@kinosearch_uz"
ADMIN_ID = 7081484236
VIP_FILE = "vip_users.txt"

if not os.path.exists(VIP_FILE):
    with open(VIP_FILE, "w") as f: pass

def get_vip_list():
    with open(VIP_FILE, "r") as f:
        return f.read().splitlines()

def is_vip(user_id):
    lines = get_vip_list()
    today = datetime.date.today()
    for line in lines:
        if ":" in line:
            uid, end_date = line.split(":")
            if str(user_id) == uid:
                if today <= datetime.date.fromisoformat(end_date): return True
    return False

def check_subscription(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# 2. MENU FUNKSIYALARI
def show_subscribe_menu(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
    markup.add(InlineKeyboardButton(text="🔄 Obuna bo'ldim", callback_data="check_sub"))
    markup.add(InlineKeyboardButton(text="💎 VIP Ta'riflar", callback_data="vip_info"))
    bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun obuna bo'ling yoki VIP ta'rifni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "vip_info")
def vip_info_handler(call):
    text = "💎 **VIP TA'RIFLAR**\n\n• 1 hafta - 5,000 so'm\n• 1 oy - 15,000 so'm\n• 6 oy - 60,000 so'm"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="💳 Karta orqali to'lov", callback_data="pay_card"))
    markup.add(InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url="https://t.me/kinosearch_admin"))
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay_card")
def pay_card_handler(call):
    text = "💳 **KARTA MA'LUMOTLARI**\n\nKarta raqami: 8600123456789012\nEga: Pasha\n\nTo'lov qilganingizdan so'ng 'To'lov qildim' tugmasini bosing."
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ To'lov qildim", callback_data="send_receipt"))
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="vip_info"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "send_receipt")
def ask_receipt(call):
    bot.send_message(call.message.chat.id, "📸 Iltimos, to'lov chekini (screenshot) yuboring:")
    bot.register_next_step_handler(call.message, process_receipt)

def process_receipt(message):
    if message.photo:
        photo_id = message.photo[-1].file_id
        bot.send_photo(ADMIN_ID, photo_id, caption=f"📥 **Yangi to'lov cheki!**\n👤 Foydalanuvchi ID: {message.chat.id}")
        bot.reply_to(message, "✅ Chek adminlarga yuborildi. Tekshirilgach, VIP aktivlashtiriladi!")
    else:
        bot.reply_to(message, "❌ Iltimos, rasm (chek) yuboring!")

# 3. ASOSIY HANDLERLAR
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_handler(call):
    if check_subscription(call.message.chat.id):
        bot.answer_callback_query(call.id, "✅ Rahmat!")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="👋 Xush kelibsiz! Kino kodini yuboring:")
    else: bot.answer_callback_query(call.id, "❌ Hali obuna bo'lmadingiz!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_handler(call):
    show_subscribe_menu(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['addvip'])
def add_vip(message):
    if message.from_user.id == ADMIN_ID:
        try:
            parts = message.text.split()
            vip_id, days = parts[1], int(parts[2])
            end_date = datetime.date.today() + datetime.timedelta(days=days)
            with open(VIP_FILE, "a") as f: f.write(f"{vip_id}:{end_date}\n")
            bot.reply_to(message, f"✅ {vip_id} {days} kunga VIP bo'ldi!")
        except: bot.reply_to(message, "⚠️ Xato! /addvip [ID] [kun]")
    else: bot.reply_to(message, "❌ Siz admin emassiz!")

@bot.message_handler(commands=['start'])
def start(message):
    if not check_subscription(message.from_user.id) and not is_vip(message.from_user.id):
        show_subscribe_menu(message)
    else: bot.reply_to(message, "👋 Xush kelibsiz! Kino kodini yuboring:")

@bot.message_handler(func=lambda message: True)
def check_code(message):
    if not check_subscription(message.from_user.id) and not is_vip(message.from_user.id):
        show_subscribe_menu(message)
        return
    
    code = message.text.strip()
    
    if code == "1622":
        bot.send_video(message.chat.id, " AAMCAgADGQEAAUwCU2oo0rWpLt9jc7yfs4G_QoJgXNjXAAIDnQACT49JSeGlY4zBwOMtAQAHbQADOwQ", caption="🎬 **Kino topildi!**\n\n🍿 Nomi: 'Chin muhabbat' filmi (2014)\n🔥 Sifati: 720HD")
    elif code == "1002":
        bot.send_video(message.chat.id, "BQACAgADGQEAAUwCU2oo0rWpLt9jc7yfs4G_QoJgXNjXAAIDnQACT49JSeGlY4zBwOMtAQAHbQADOwQ", caption="🎬 'Weak Hero Class 1' topildi!")
    else:
        bot.reply_to(message, "❌ Kod topilmadi.")

# RENDER SERVER QISMI
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
