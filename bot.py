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

# --- YORDAMCHI ---
def is_subscribed(uid):
    try: return bot.get_chat_member(CHANNEL, uid).status in ['member', 'administrator', 'creator']
    except: return False

# --- ASOSIY ---
@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.chat.id):
        return bot.send_message(message.chat.id, f"🚫 Kanalga obuna bo'ling: {CHANNEL}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🖼 Rasm orqali", "👤 Profil", "🏆 Top 10", "💰 Pul yechish", "🆘 Help")
    bot.send_message(message.chat.id, "👋 Xush kelibsiz!", reply_markup=markup)

# --- PUL YECHISH TIZIMI ---
@bot.message_handler(func=lambda m: m.text == "💰 Pul yechish")
def start_withdrawal(message):
    if users.get(message.chat.id, {}).get("balans", 0) < 10000:
        bot.send_message(message.chat.id, "❌ Minimum 10.000 so'm!")
    else:
        msg = bot.send_message(message.chat.id, "💰 Qancha yechmoqchisiz?")
        bot.register_next_step_handler(msg, step_amount)

def step_amount(message):
    try:
        amt = int(message.text)
        if amt > users[message.chat.id]["balans"]: raise Exception
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ To'g'ri", callback_data=f"okamt_{amt}"),
            types.InlineKeyboardButton("🔙 Ortga", callback_data="cancel"))
        bot.send_message(message.chat.id, f"💰 {amt} so'm. To'g'rimi?", reply_markup=markup)
    except: bot.send_message(message.chat.id, "❌ Noto'g'ri qiymat!")

# --- RASM TIZIMI ---
@bot.message_handler(func=lambda m: m.text == "🖼 Rasm orqali")
def start_photo(message):
    task = random.choice(items)
    users[message.chat.id] = users.get(message.chat.id, {"balans":0, "last_task":""})
    users[message.chat.id]["last_task"] = task
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📤 Rasm yuborish", callback_data="btn_up"))
    bot.send_message(message.chat.id, f"📸 {task} rasmini yuboring!", reply_markup=markup)

# --- CALLBACK TIZIMI ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.message.chat.id
    if call.data == "btn_up":
        msg = bot.send_message(uid, "Rasmni yuboring:")
        bot.register_next_step_handler(msg, step_photo)
    elif call.data.startswith("okamt_"):
        amt = call.data.split("_")[1]
        msg = bot.send_message(uid, "💳 Karta raqamingizni yozing:")
        bot.register_next_step_handler(msg, lambda m: finish_with(m, amt))
    elif call.data.startswith("ok_"):
        u = int(call.data.split("_")[1])
        users[u]["balans"] = users[u].get("balans", 0) + 100
        bot.send_message(u, "✅ Tasdiqlandi! +100 so'm.")
        bot.edit_message_caption("✅ Tasdiqlandi.", uid, call.message.message_id)

def step_photo(message):
    if message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"👤 {message.chat.id}\nTopshiriq: {users[message.chat.id]['last_task']}", 
                       reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅", callback_data=f"ok_{message.chat.id}")))
        bot.send_message(message.chat.id, "✅ Admin tekshirmoqda...")
    else: bot.send_message(message.chat.id, "❌ Rasm yuboring!")

def finish_with(message, amt):
    bot.send_message(message.chat.id, "⏳ Kuting... Admin ko'rib chiqmoqda.")
    bot.send_message(ADMIN_ID, f"📩 So'rov: {message.chat.id}\n💰 {amt}\n💳 {message.text}")

# --- QOLGANLAR ---
@bot.message_handler(commands=['pay'])
def pay(m):
    if m.chat.id == ADMIN_ID:
        try:
            _, uid, amt = m.text.split()
            users[int(uid)] = users.get(int(uid), {"balans":0})
            users[int(uid)]["balans"] += int(amt)
            bot.send_message(uid, f"✅ +{amt} so'm qo'shildi!")
        except: bot.reply_to(m, "Format: /pay <id> <amt>")

bot.infinity_polling()
