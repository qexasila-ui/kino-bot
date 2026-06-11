import telebot
from telebot import types
import random
import time

TOKEN = "8816384633:AAEVwVo_LOyXjM-41Ob1AyccTYkiBqQd31I"
ADMIN_ID = 7081484236
CHANNEL = "@PulTopinguzz"

bot = telebot.TeleBot(TOKEN)
users = {} # {uid: {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}}
items = ["Dom", "Ko'cha", "Daraxt", "Televizor", "Gultuvak", "Tova", "Muzlatkich", "Chiroq", "Devor", "Gilam"]

# --- YORDAMCHI FUNKSIYALAR ---
def is_subscribed(uid):
    try:
        status = bot.get_chat_member(CHANNEL, uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def parse_time(time_str):
    try:
        unit = time_str[-1].lower()
        val = int(time_str[:-1])
        if unit == 's': return val
        if unit == 'm': return val * 60
        if unit == 'h': return val * 3600
        if unit == 'd': return val * 86400
    except: return 0
    return 0

# --- ADMIN BUYRUQLARI ---
@bot.message_handler(commands=['pay'])
def admin_pay(message):
    if message.chat.id == ADMIN_ID:
        try:
            parts = message.text.split()
            uid, amount = int(parts[1]), int(parts[2])
            if uid not in users: users[uid] = {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}
            users[uid]["balans"] += amount
            bot.send_message(uid, f"✅ Sizga {amount} so'm qo'shildi! Balansingiz: {users[uid]['balans']}")
            bot.reply_to(message, f"✅ {uid} ga {amount} so'm qo'shildi.")
        except: bot.reply_to(message, "❌ Format: /pay <id> <amount>")

@bot.message_handler(commands=['mute', 'unmute'])
def manage_mute(message):
    if message.chat.id == ADMIN_ID:
        try:
            parts = message.text.split()
            uid = int(parts[1])
            if uid not in users: users[uid] = {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}
            if parts[0] == "/mute":
                users[uid]["mute_until"] = time.time() + parse_time(parts[2])
                bot.send_message(uid, "🚫 Siz admin tomonidan bloklandingiz.")
                bot.reply_to(message, "✅ Foydalanuvchi bloklandi.")
            else:
                users[uid]["mute_until"] = 0
                bot.send_message(uid, "✅ Siz blokdan chiqarildingiz.")
                bot.reply_to(message, "✅ Blokdan chiqdi.")
        except: bot.reply_to(message, "❌ Xato!")

@bot.message_handler(commands=['msg'])
def send_msg(message):
    if message.chat.id == ADMIN_ID:
        try:
            parts = message.text.split(" ", 2)
            bot.send_message(parts[1], f"📩 Admin xabari: {parts[2]}")
            bot.reply_to(message, "✅ Xabar yuborildi!")
        except: bot.reply_to(message, "❌ Format: /msg <id> <xabar>")

# --- ASOSIY HANDLER ---
@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.chat.id):
        return bot.send_message(message.chat.id, f"🚫 Botdan foydalanish uchun {CHANNEL} kanaliga obuna bo'ling!")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🖼 Rasm orqali", "👤 Profil", "🏆 Top 10")
    markup.add("💰 Pul yechish", "🆘 Help")
    bot.send_message(message.chat.id, "👋 Xush kelibsiz!", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    uid = message.chat.id
    if uid not in users: users[uid] = {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}
    if users[uid].get("mute_until", 0) > time.time(): return bot.send_message(uid, "🚫 Siz bloklangansiz!")

    if message.text == "🖼 Rasm orqali":
        task = random.choice(items)
        users[uid]["last_task"] = task
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📤 Rasm yuborish", callback_data="upload_photo"))
        bot.send_message(uid, f"📸 Topshiriq: *{task}* rasmini yuboring!", parse_mode="Markdown", reply_markup=markup)
    elif message.text == "💰 Pul yechish":
        if users[uid]["balans"] < 10000: bot.send_message(uid, "❌ Minimum 10.000 so'm!")
        else:
            msg = bot.send_message(uid, "💰 Qancha yechmoqchisiz?")
            bot.register_next_step_handler(msg, lambda m: confirm_withdrawal(m))
    elif message.text == "👤 Profil":
        bot.send_message(uid, f"💰 Balans: {users[uid]['balans']} so'm")
    elif message.text == "🏆 Top 10":
        top = sorted(users.items(), key=lambda x: x[1]['balans'], reverse=True)[:10]
        bot.send_message(uid, "🏆 Top 10:\n" + "\n".join([f"{i}. ID: {k} - {v['balans']} so'm" for i, (k, v) in enumerate(top, 1)]))

def confirm_withdrawal(message):
    try:
        amt = int(message.text)
        if amt > users[message.chat.id]["balans"]: return bot.send_message(message.chat.id, "❌ Balans kam!")
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ To'g'ri", callback_data=f"conf_{amt}"),
            types.InlineKeyboardButton("🔙 Ortga", callback_data="cancel"))
        bot.send_message(message.chat.id, f"💰 Siz *{amt}* so'm yechmoqchisiz. To'g'rimi?", parse_mode="Markdown", reply_markup=markup)
    except: bot.send_message(message.chat.id, "❌ Raqam kiriting!")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data.split("_")
    uid = call.message.chat.id
    if data[0] == "conf":
        msg = bot.send_message(uid, "💳 Karta raqamingizni yozing:")
        bot.register_next_step_handler(msg, lambda m: finish_withdrawal(m, data[1]))
    elif data[0] == "ok":
        bot.send_message(data[1], "✅ Tasdiqlandi! Admin chek yuborishini kuting.")
        m = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📤 Chek yuborish", callback_data=f"sendchk_{data[1]}"))
        bot.edit_message_caption("✅ Tasdiqlandi.", call.message.chat.id, call.message.message_id, reply_markup=m)
    elif data[0] == "sendchk":
        msg = bot.send_message(ADMIN_ID, "📸 Chek rasmini yuboring:")
        bot.register_next_step_handler(msg, lambda m: bot.send_photo(data[1], m.photo[-1].file_id, caption="✅ To'lov cheki!"))
    elif call.data == "upload_photo":
        msg = bot.send_message(uid, "Rasmni yuboring:")
        bot.register_next_step_handler(msg, lambda m: bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=f"👤 {uid}\nTopshiriq: {users[uid]['last_task']}", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅", callback_data=f"ok_{uid}"), types.InlineKeyboardButton("❌", callback_data=f"no_{uid}"))))

def finish_withdrawal(message, amount):
    bot.send_message(message.chat.id, "⏳ Kuting... Admin so'rovingizni ko'rib chiqmoqda.")
    bot.send_message(ADMIN_ID, f"📩 Yangi so'rov!\n👤: {message.chat.id}\n💰: {amount}\n💳: {message.text}", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{message.chat.id}")))

bot.infinity_polling()
