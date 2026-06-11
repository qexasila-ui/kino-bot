import telebot
from telebot import types
import random
import time

TOKEN = "8816384633:AAEVwVo_LOyXjM-41Ob1AyccTYkiBqQd31I"
ADMIN_ID = 7081484236
CHANNEL = "@PulTopinguzz"

bot = telebot.TeleBot(TOKEN)
users = {} 
items = ["Dom", "Ko'cha", "Daraxt", "Televizor", "Gultuvak", "Tova", "Muzlatkich", "Chiroq", "Devor", "Gilam"]

# Yordamchi funksiyalar
def is_subscribed(uid):
    try:
        status = bot.get_chat_member(CHANNEL, uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def parse_time(time_str):
    try:
        unit = time_str[-1].lower()
        value = int(time_str[:-1])
        if unit == 's': return value
        if unit == 'm': return value * 60
        if unit == 'h': return value * 3600
        if unit == 'd': return value * 86400
    except: return 0
    return 0

@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.chat.id):
        return bot.send_message(message.chat.id, f"🚫 Botdan foydalanish uchun {CHANNEL} kanaliga obuna bo'ling!")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🖼 Rasm orqali", "👤 Profil", "🏆 Top 10")
    markup.add("💰 Pul yechish", "🆘 Help")
    bot.send_message(message.chat.id, "👋 Xush kelibsiz!", reply_markup=markup)

# --- ADMIN BUYRUQLARI ---
@bot.message_handler(commands=['pay'])
def admin_pay(message):
    if message.chat.id == ADMIN_ID:
        try:
            _, uid, amount = message.text.split()
            uid = int(uid)
            if uid not in users: users[uid] = {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}
            users[uid]["balans"] += int(amount)
            bot.send_message(uid, f"✅ Sizga {amount} so'm qo'shildi!")
            bot.reply_to(message, "✅ Balans yangilandi.")
        except: bot.reply_to(message, "Xato! Format: /pay <id> <amount>")

@bot.message_handler(commands=['mute', 'unmute'])
def manage_mute(message):
    if message.chat.id == ADMIN_ID:
        try:
            parts = message.text.split()
            cmd, uid = parts[0], int(parts[1])
            if uid not in users: users[uid] = {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}
            if cmd == "/mute":
                duration = parts[2]
                users[uid]["mute_until"] = time.time() + parse_time(duration)
                bot.send_message(uid, f"🚫 Siz {duration} muddatga bloklandingiz.")
                bot.reply_to(message, "✅ Bloklandi.")
            else:
                users[uid]["mute_until"] = 0
                bot.send_message(uid, "✅ Siz blokdan chiqarildingiz.")
                bot.reply_to(message, "✅ Blokdan chiqdi.")
        except: bot.reply_to(message, "Xato! Format: /mute <id> <vaqt> yoki /unmute <id>")

@bot.message_handler(commands=['msg'])
def send_msg(message):
    if message.chat.id == ADMIN_ID:
        try:
            parts = message.text.split(" ", 2)
            bot.send_message(parts[1], f"📩 Admin xabari: {parts[2]}")
            bot.reply_to(message, "✅ Xabar yuborildi!")
        except: bot.reply_to(message, "❌ Format: /msg <id> <xabar>")

# --- ASOSIY HANDLERLAR ---
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
    elif message.text == "🆘 Help":
        bot.send_message(uid, "Qoidalar: Rasm yuboring, admin tasdiqlasa pul ishlaysiz.")

def confirm_withdrawal(message):
    try:
        amount = int(message.text)
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ To'g'ri", callback_data=f"conf_{amount}"),
            types.InlineKeyboardButton("🔙 Ortga", callback_data="cancel"))
        bot.send_message(message.chat.id, f"💰 Siz *{amount}* so'm yechmoqchisiz. To'g'rimi?", parse_mode="Markdown", reply_markup=markup)
    except: bot.send_message(message.chat.id, "❌ Faqat raqam yozing!")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data.split("_")
    uid = call.message.chat.id
    
    if call.data == "upload_photo":
        msg = bot.send_message(uid, "Rasmni yuboring:")
        bot.register_next_step_handler(msg, lambda m: bot.send_photo(ADMIN_ID, m.photo[-1].file_id, 
            caption=f"👤: {uid}\n📝 Topshiriq: {users[uid]['last_task']}", 
            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅", callback_data=f"ok_{uid}"), types.InlineKeyboardButton("❌", callback_data=f"no_{uid}"))))
    elif data[0] == "conf":
        msg = bot.send_message(uid, "💳 Karta raqamingizni yozing (Humo, Uzcard, Paynet):")
        bot.register_next_step_handler(msg, lambda m: finish_withdrawal(m, data[1]))
    elif data[0] == "ok":
        bot.send_message(data[1], "✅ Tasdiqlandi! Admin chek yuborishini kuting.")
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📤 Chek yuborish", callback_data=f"sendchk_{data[1]}"))
        bot.edit_message_caption("✅ Tasdiqlandi.", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif data[0] == "sendchk":
        msg = bot.send_message(ADMIN_ID, "📸 Chek rasmini yuboring:")
        bot.register_next_step_handler(msg, lambda m: bot.send_photo(data[1], m.photo[-1].file_id, caption="✅ To'lov cheki!"))
    elif data[0] == "no":
        users[int(data[1])]["balans"] -= 500
        bot.send_message(data[1], "❌ Xato! -500 so'm.")
        bot.edit_message_caption("❌ Rad etildi.", call.message.chat.id, call.message.message_id)

def finish_withdrawal(message, amount):
    bot.send_message(message.chat.id, "⏳ Kuting... Admin so'rovingizni ko'rib chiqmoqda.")
    bot.send_message(ADMIN_ID, f"📩 Yangi so'rov!\n👤: {message.chat.id}\n💰: {amount}\n💳: {message.text}", 
                     reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{message.chat.id}")))

bot.infinity_polling()
