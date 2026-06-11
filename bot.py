import telebot
from telebot import types
import random
import time

TOKEN = "8816384633:AAEVwVo_LOyXjM-41Ob1AyccTYkiBqQd31I"
ADMIN_ID = 7081484236
CHANNEL = "@PulTopinguzz"

bot = telebot.TeleBot(TOKEN)
# users format: {uid: {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}}
users = {} 
items = ["Dom", "Ko'cha", "Daraxt", "Televizor", "Gultuvak", "Tova", "Muzlatkich", "Chiroq", "Devor", "Gilam"]

def get_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🖼 Rasm orqali", "👤 Profil", "🏆 Top 10")
    markup.add("💰 Pul yechish", "🆘 Help")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Xush kelibsiz!", reply_markup=get_menu())

@bot.message_handler(content_types=['text'])
def handle_text(message):
    uid = message.chat.id
    if uid not in users: users[uid] = {"balans": 0, "xato": 0, "mute_until": 0, "last_task": ""}
    
    if uid in users and users[uid].get("mute_until", 0) > time.time():
        return bot.send_message(uid, "🚫 Siz bloklangansiz!")

    # 1. Rasm orqali
    if message.text == "🖼 Rasm orqali":
        task = random.choice(items)
        users[uid]["last_task"] = task
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📤 Rasm yuborish", callback_data="upload_photo"))
        bot.send_message(uid, f"📸 Topshiriq: *{task}* rasmini yuboring!", parse_mode="Markdown", reply_markup=markup)
    
    # 2. Help
    elif message.text == "🆘 Help":
        bot.send_message(uid, "Qoida: Rasm yuboring, admin tasdiqlasa pul ishlaysiz. 3 ta xato = 12 soat mute.")
        
    # 3. Profil
    elif message.text == "👤 Profil":
        bot.send_message(uid, f"💰 Balansingiz: {users[uid]['balans']} so'm")
        
    # 4. Top 10
    elif message.text == "🏆 Top 10":
        top = sorted(users.items(), key=lambda x: x[1]['balans'], reverse=True)[:10]
        text = "🏆 Top 10 foydalanuvchi:\n" + "\n".join([f"{i}. {k}: {v['balans']} so'm" for i, (k, v) in enumerate(top, 1)])
        bot.send_message(uid, text)
        
    # 5. Pul yechish
    elif message.text == "💰 Pul yechish":
        if users[uid]["balans"] < 10000:
            bot.send_message(uid, "❌ Minimum 10.000 so'm kerak!")
        else:
            msg = bot.send_message(uid, "💰 Qancha yechmoqchisiz? (10.000 - 5.000.000):")
            bot.register_next_step_handler(msg, process_withdrawal)

def process_withdrawal(message):
    try:
        amount = int(message.text)
        uid = message.chat.id
        if 10000 <= amount <= 5000000 and amount <= users[uid]["balans"]:
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ To'lash", callback_data=f"pay_{uid}_{amount}"),
                types.InlineKeyboardButton("❌ Rad", callback_data=f"rej_{uid}"))
            bot.send_message(ADMIN_ID, f"📩 Pul yechish so'rovi!\nFoydalanuvchi: {uid}\nMiqdor: {amount} so'm", reply_markup=markup)
            bot.send_message(uid, "✅ So'rov yuborildi.")
        else: bot.send_message(uid, "❌ Xato miqdor!")
    except: bot.send_message(uid, "❌ Raqam kiriting!")

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
        uid = int(data[1])
        users[uid]["balans"] += 100
        bot.send_message(uid, "✅ +100 so'm qo'shildi!")
        bot.edit_message_caption("✅ Tasdiqlandi.", call.message.chat.id, call.message.message_id)
        
    elif data[0] == "no":
        uid = int(data[1])
        users[uid]["balans"] -= 500
        users[uid]["xato"] += 1
        if users[uid]["xato"] >= 3: users[uid]["mute_until"] = time.time() + 43200
        bot.send_message(uid, f"❌ Xato! -500 so'm. {3 - users[uid]['xato']} imkoniyat qoldi.")
        bot.edit_message_caption("❌ Rad etildi.", call.message.chat.id, call.message.message_id)
        
    elif data[0] == "pay":
        uid, amount = int(data[1]), int(data[2])
        users[uid]["balans"] -= amount
        bot.send_message(uid, "✅ To'lab berildi!")
        bot.edit_message_caption("✅ To'landi.", call.message.chat.id, call.message.message_id)
        
    elif data[0] == "rej":
        bot.send_message(int(data[1]), "❌ Pul yechish rad etildi.")
        bot.edit_message_caption("❌ Rad etildi.", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
