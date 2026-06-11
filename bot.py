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

def get_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🖼 Rasm orqali", "👤 Profil", "🏆 Top 10")
    markup.add("💰 Pul yechish", "🆘 Help")
    return markup

# --- BUYRUQLAR VA TUGMALAR ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Xush kelibsiz! Botdan foydalanish uchun kanalga obuna bo'ling.", reply_markup=get_menu())

@bot.message_handler(commands=['addid'])
def add_id(message):
    if message.chat.id == ADMIN_ID:
        try:
            uid = int(message.text.split()[1])
            users[uid] = {"balans": 0, "status": "vip", "xato": 0, "mute_until": 0}
            bot.send_message(uid, "✅ Siz VIP bo'ldingiz! Endi botdan to'liq foydalanishingiz mumkin.")
            bot.reply_to(message, "Foydalanuvchi VIP qilindi.")
        except: bot.reply_to(message, "Format: /addid user_id")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    uid = message.chat.id
    text = message.text

    if uid in users and users[uid].get("mute_until", 0) > time.time():
        return bot.send_message(uid, "🚫 Siz bloklangansiz!")

    if text == "🖼 Rasm orqali":
        if uid not in users or users[uid].get("status") != "vip":
            return bot.send_message(uid, "❌ Siz VIP emassiz! Admin bilan bog'laning.")
        item = random.choice(items)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📤 Rasm yuborish", callback_data="upload_photo"))
        bot.send_message(uid, f"📸 *{item}* rasmini yuboring!", parse_mode="Markdown", reply_markup=markup)
    
    elif text == "🆘 Help":
        bot.send_message(uid, "🆘 **Yordam:** Rasm yuboring, admin tasdiqlasa pul ishlaysiz. 3 ta xato = 12 soat mute!", parse_mode="Markdown")
    
    elif text == "👤 Profil":
        u = users.get(uid, {"balans": 0})
        bot.send_message(uid, f"💰 Balans: {u.get('balans', 0)} so'm")
    
    elif text == "🏆 Top 10":
        sorted_users = sorted(users.items(), key=lambda x: x[1].get('balans', 0), reverse=True)[:10]
        text = "🏆 Top 10:\n" + "\n".join([f"{i}. ID: {k} - {v['balans']} so'm" for i, (k, v) in enumerate(sorted_users, 1)])
        bot.send_message(uid, text)
        
    elif text == "💰 Pul yechish":
        if users.get(uid, {}).get("balans", 0) < 10000:
            bot.send_message(uid, "❌ Minimum 10.000 so'm!")
        else:
            msg = bot.send_message(uid, "💰 Qancha yechmoqchisiz?")
            bot.register_next_step_handler(msg, process_withdrawal)

def process_withdrawal(message):
    amount = int(message.text)
    uid = message.chat.id
    if 10000 <= amount <= 5000000 and amount <= users[uid]["balans"]:
        bot.send_message(ADMIN_ID, f"📩 Pul yechish: {uid} - {amount} so'm", reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ To'lash", callback_data=f"pay_out_{uid}_{amount}"),
            types.InlineKeyboardButton("❌ Rad", callback_data=f"reject_{uid}")))
        bot.send_message(uid, "✅ So'rov yuborildi.")

# --- ADMIN VA CALLBACK ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data.split("_")
    if data[0] == "upload_photo":
        msg = bot.send_message(call.message.chat.id, "Rasmni yuboring:")
        bot.register_next_step_handler(msg, lambda m: bot.send_photo(ADMIN_ID, m.photo[-1].file_id, caption=f"Foydalanuvchi: {m.chat.id}", reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅", callback_data=f"ok_{m.chat.id}"), types.InlineKeyboardButton("❌", callback_data=f"no_{m.chat.id}"))))
    elif data[0] in ["ok", "no"]:
        uid = int(data[1])
        if data[0] == "ok": users[uid]["balans"] += 100
        else:
            users[uid]["balans"] -= 500
            users[uid]["xato"] = users[uid].get("xato", 0) + 1
            if users[uid]["xato"] >= 3: users[uid]["mute_until"] = time.time() + 43200
        bot.edit_message_caption("Bajarildi.", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
