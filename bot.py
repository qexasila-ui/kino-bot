import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import os

# 1. SOZLAMALAR
API_TOKEN = "8888334220:AAEDAzYUSwQcSgvZ35zYWIdai-7K5wNfJC4" # Tokeningni kirit
bot = telebot.TeleBot(API_TOKEN)
CHANNEL = "@kinosearch_uz"
ADMIN_ID = 7081484236
VIP_FILE = "vip_users.txt"

# VIP faylini tekshirish
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
                if today <= datetime.date.fromisoformat(end_date):
                    return True
    return False

def check_subscription(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# 2. ASOSIY FUNKSIYALAR
def show_subscribe_menu(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
    markup.add(InlineKeyboardButton(text="🔄 Obuna bo'ldim", callback_data="check_sub"))
    markup.add(InlineKeyboardButton(text="💎 VIP Ta'riflar", callback_data="vip_info"))
    bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun obuna bo'ling yoki VIP ta'rifni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_handler(call):
    if check_subscription(call.message.chat.id):
        bot.answer_callback_query(call.id, "✅ Rahmat! Endi botdan foydalanishingiz mumkin.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="👋 Xush kelibsiz! Kino kodini yuboring:")
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo'lmadingiz!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "vip_info")
def vip_info_handler(call):
    text = (
        "💎 **VIP TA'RIFLAR**\n\n"
        "• 1 hafta - 5,000 so'm\n"
        "• 1 oy - 15,000 so'm\n"
        "• 6 oy - 60,000 so'm\n\n"
        "To'lov uchun admin bilan bog'laning: @kinosearch_admin"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="👤 Admin bilan bog'lanish", url="https://t.me/kinosearch_admin"))
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_handler(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
    markup.add(InlineKeyboardButton(text="🔄 Obuna bo'ldim", callback_data="check_sub"))
    markup.add(InlineKeyboardButton(text="💎 VIP Ta'riflar", callback_data="vip_info"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="⚠️ Botdan foydalanish uchun obuna bo'ling yoki VIP ta'rifni tanlang:", reply_markup=markup)

# 3. ADMIN BUYRUQLARI
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

@bot.message_handler(commands=['start', 'getid'])
def general_handlers(message):
    if message.text.startswith('/getid'):
        if message.from_user.id == ADMIN_ID and message.reply_to_message:
            bot.reply_to(message, f"👤 ID: {message.reply_to_message.from_user.id}")
        else: bot.reply_to(message, f"🆔 Sizning ID: {message.from_user.id}")
    else:
        if not check_subscription(message.from_user.id) and not is_vip(message.from_user.id):
            show_subscribe_menu(message)
        else: bot.reply_to(message, "👋 Xush kelibsiz! Kino kodini yuboring:")

@bot.message_handler(func=lambda message: True)
def check_code(message):
    if not check_subscription(message.from_user.id) and not is_vip(message.from_user.id):
        show_subscribe_menu(message)
        return
    if message.text == "1002": bot.reply_to(message, "🎬 'Weak Hero Class 1' topildi!")
    elif message.text == "777": bot.reply_to(message, "🎬 'Spider-Man: No Way Home' topildi!")
    else: bot.reply_to(message, "❌ Kod topilmadi.")

bot.infinity_polling()
