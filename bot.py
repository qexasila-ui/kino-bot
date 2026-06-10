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
CHANNEL_ID = -1002396347321 
ADMIN_ID = 7081484236
VIP_FILE = "vip_users.txt"

if not os.path.exists(VIP_FILE):
    with open(VIP_FILE, "w") as f: pass

# VIP va Obuna funksiyalari
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

# 2. MENU FUNKSIYALARI (VIP va To'lovlar saqlandi)
def show_subscribe_menu(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
    markup.add(InlineKeyboardButton(text="🔄 Obuna bo'ldim", callback_data="check_sub"))
    markup.add(InlineKeyboardButton(text="💎 VIP Ta'riflar", callback_data="vip_info"))
    bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun obuna bo'ling:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "vip_info")
def vip_info_handler(call):
    text = "💎 **VIP TA'RIFLAR**\n\n• 1 hafta - 5,000 so'm\n• 1 oy - 15,000 so'm\n• 6 oy - 60,000 so'm"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="💳 Karta orqali to'lov", callback_data="pay_card"))
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay_card")
def pay_card_handler(call):
    text = "💳 **KARTA MA'LUMOTLARI**\n\nKarta: 8600123456789012\nEga: Pasha\n\nTo'lovdan so'ng 'To'lov qildim' ni bosing."
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ To'lov qildim", callback_data="send_receipt"))
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="vip_info"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "send_receipt")
def ask_receipt(call):
    bot.send_message(call.message.chat.id, "📸 To'lov chekini yuboring:")
    bot.register_next_step_handler(call.message, process_receipt)

def process_receipt(message):
    if message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📥 Yangi chek! ID: {message.chat.id}")
        bot.reply_to(message, "✅ Chek adminlarga yuborildi.")
    else: bot.reply_to(message, "❌ Iltimos, rasm yuboring!")

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_handler(call):
    if check_subscription(call.message.chat.id):
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="👋 Xush kelibsiz! Kino kodini yuboring:")
    else: bot.answer_callback_query(call.id, "❌ Obuna bo'lmadingiz!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_handler(call):
    show_subscribe_menu(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)

# 3. KINO YUBORISH (KANAL ORQALI)
@bot.message_handler(func=lambda message: True)
def check_code(message):
    if not check_subscription(message.from_user.id) and not is_vip(message.from_user.id):
        show_subscribe_menu(message)
        return
    
    try:
        kino_msg_id = int(message.text.strip())
        bot.copy_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=kino_msg_id)
    except:
        bot.reply_to(message, "❌ Kod xato yoki kino topilmadi.")

# SERVER QISMI
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"

def run(): app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
