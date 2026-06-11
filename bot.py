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

# ADMIN BUYRUQLARI
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
            cmd = parts[0]
            uid = int(parts[1])
            if uid not in users: users[uid] = {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}
            
            if cmd == "/mute":
                duration_str = parts[2]
                users[uid]["mute_until"] = time.time() + parse_time(duration_str)
                bot.send_message(uid, f"🚫 Siz {duration_str} muddatga bloklandingiz.")
                bot.reply_to(message, "✅ Bloklandi.")
            else:
                users[uid]["mute_until"] = 0
                bot.send_message(uid, "✅ Siz blokdan chiqarildingiz.")
                bot.reply_to(message, "✅ Blokdan chiqdi.")
        except: bot.reply_to(message, "Xato! Format: /mute <id> <vaqt> yoki /unmute <id>")

# ASOSIY HANDLERLAR
@bot.message_handler(content_types=['text'])
def handle_text(message):
    uid = message.chat.id
    if uid not in users: users[uid] = {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}
    
    if users[uid].get("mute_until", 0) > time.time():
        return bot.send_message(uid, "🚫 Siz bloklangansiz!")

    if message.text == "🖼 Rasm orqali":
        task = random.choice(items)
        users[uid]["last_task"] = task
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📤 Rasm yuborish", callback_data="upload_photo"))
        bot.send_message(uid, f"📸 Topshiriq: *{task}* rasmini yuboring!", parse_mode="Markdown", reply_markup=markup)
    elif message.text == "🆘 Help":
        bot.send_message(uid, "Qoidalar: Rasm yuboring, admin tasdiqlasa pul ishlaysiz. 3 ta xato = Mute.")
    elif message.text == "👤 Profil":
        bot.send_message(uid, f"💰 Balans: {users[uid]['balans']} so'm")
    elif message.text == "🏆 Top 10":
        top = sorted(users.items(), key=lambda x: x[1]['balans'], reverse=True)[:10]
        bot.send_message(uid, "🏆 Top 10:\n" + "\n".join([f"{i}. ID: {k} - {v['balans']} so'm" for i, (k, v) in enumerate(top, 1)]))
    elif message.text == "💰 Pul yechish":
        if users[uid]["balans"] < 10000: bot.send_message(uid, "❌ Minimum 10.000 so'm!")
        else:
            msg = bot.send_message(uid, "💰 Qancha yechmoqchisiz?")
            bot.register_next_step_handler(msg, lambda m: bot.send_message(ADMIN_ID, f"📩 So'rov: {uid} - {m.text} so'm"))

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data.split("_")
    if call.data == "upload_photo":
        msg = bot.send_message(call.message.chat.id, "Rasmni yuboring:")
        bot.register_next_step_handler(msg, lambda m: bot.send_photo(ADMIN_ID, m.photo[-1].file_id, 
            caption=f"👤: {m.chat.id}\n📝 Topshiriq: {users[m.chat.id]['last_task']}", 
            reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅", callback_data=f"ok_{m.chat.id}"), 
            types.InlineKeyboardButton("❌", callback_data=f"no_{m.chat.id}"))))
    elif data[0] == "ok":
        users[int(data[1])]["balans"] += 100
        bot.send_message(data[1], "✅ Tasdiqlandi! +100 so'm.")
        bot.edit_message_caption("✅ Tasdiqlandi.", call.message.chat.id, call.message.message_id)
    elif data[0] == "no":
        users[int(data[1])]["balans"] -= 500
        users[int(data[1])]["xato"] += 1
        if users[int(data[1])]["xato"] >= 3: users[int(data[1])]["mute_until"] = time.time() + 43200
        bot.send_message(data[1], "❌ Xato! -500 so'm.")
        bot.edit_message_caption("❌ Rad etildi.", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
