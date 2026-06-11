import telebot
from telebot import types
import random
import time

TOKEN = "8816384633:AAEVwVo_LOyXjM-41Ob1AyccTYkiBqQd31I"
ADMIN_ID = 7081484236
CHANNEL = "@PulTopinguzz"
ADMIN_USERNAME = "@PulTopBot_admin" # O'zingning usernameingni yoz

bot = telebot.TeleBot(TOKEN)
# users format: {user_id: {"balans": 0, "status": "vip", "xato": 0, "mute_until": 0}}
users = {} 
items = ["Dom", "Ko'cha", "Daraxt", "Televizor", "Gultuvak", "Tova", "Muzlatkich", "Chiroq", "Devor", "Gilam"]

def get_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🖼 Rasm orqali", "👤 Profil", "🏆 Top 10")
    markup.add("💰 Pul yechish", "🆘 Help")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    if uid in users and users[uid].get("mute_until", 0) > time.time():
        return bot.send_message(uid, "🚫 Siz 12 soatlik mute holatidasiz.")
    bot.send_message(uid, "👋 Xush kelibsiz! Botdan foydalanish uchun kanalga obuna bo'ling va to'lov qiling.", reply_markup=get_menu())

# --- PROFIL VA REYTING ---
@bot.message_handler(func=lambda message: message.text == "👤 Profil")
def profile(message):
    u = users.get(message.chat.id, {"balans": 0})
    bot.send_message(message.chat.id, f"👤 Profilingiz:\n🆔 ID: {message.chat.id}\n💰 Balans: {u.get('balans', 0)} so'm")

@bot.message_handler(func=lambda message: message.text == "🏆 Top 10")
def top_list(message):
    sorted_users = sorted(users.items(), key=lambda x: x[1].get('balans', 0), reverse=True)[:10]
    text = "🏆 Top 10 foydalanuvchi:\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        text += f"{i}. ID: {uid} — {data['balans']} so'm\n"
    bot.send_message(message.chat.id, text)

# --- PUL YECHISH ---
@bot.message_handler(func=lambda message: message.text == "💰 Pul yechish")
def withdraw_money(message):
    uid = message.chat.id
    balance = users.get(uid, {}).get("balans", 0)
    if balance < 10000:
        bot.send_message(uid, f"❌ Minimum 10.000 so'm kerak. Balansingiz: {balance} so'm")
    else:
        msg = bot.send_message(uid, "💰 Qancha mablag' yechmoqchisiz? (10.000 - 5.000.000 so'm):")
        bot.register_next_step_handler(msg, process_withdrawal)

def process_withdrawal(message):
    try:
        amount = int(message.text)
        uid = message.chat.id
        if 10000 <= amount <= 5000000 and amount <= users[uid]["balans"]:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ To'lab berish", callback_data=f"pay_out_{uid}_{amount}"),
                       types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{uid}"))
            bot.send_message(ADMIN_ID, f"📩 Pul yechish so'rovi!\nFoydalanuvchi: {uid}\nMiqdor: {amount} so'm", reply_markup=markup)
            bot.send_message(uid, "✅ So'rovingiz adminga yuborildi.")
        else: bot.send_message(uid, "❌ Xato miqdor yoki balans yetarli emas!")
    except: bot.send_message(uid, "❌ Iltimos, raqam kiriting.")

# --- ADMIN ACTION ---
@bot.callback_query_handler(func=lambda call: call.data.startswith(("ok_", "no_", "pay_out_", "reject_")))
def admin_action(call):
    data = call.data.split("_")
    action, uid = data[0], int(data[1])
    
    if action == "ok":
        users[uid]["balans"] = users[uid].get("balans", 0) + 100
        bot.send_message(uid, f"✅ Rasm tasdiqlandi! Balans: {users[uid]['balans']} so'm")
    elif action == "no":
        users[uid]["balans"] = users[uid].get("balans", 0) - 500
        users[uid]["xato"] = users[uid].get("xato", 0) + 1
        if users[uid]["xato"] >= 3:
            users[uid]["mute_until"] = time.time() + (12 * 3600)
            users[uid]["xato"] = 0
            bot.send_message(uid, "❌ 3 ta xato! 12 soatga mute oldingiz.")
        else: bot.send_message(uid, f"❌ Rasm xato! {3 - users[uid]['xato']} ta imkoniyat qoldi.")
    elif action == "pay_out":
        amount = int(data[2])
        users[uid]["balans"] -= amount
        bot.send_message(uid, f"✅ {amount} so'm to'lab berildi!")
    elif action == "reject":
        bot.send_message(uid, "❌ Pul yechish so'rovingiz rad etildi.")
    bot.edit_message_caption("Bajarildi.", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
