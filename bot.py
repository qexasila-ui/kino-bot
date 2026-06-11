import telebot
from telebot import types
import random
import time

TOKEN = "8816384633:AAEVwVo_LOyXjM-41Ob1AyccTYkiBqQd31I"
ADMIN_ID = 7081484236
CHANNEL = "@PulTopinguzz"

bot = telebot.TeleBot(TOKEN)
# users format: {uid: {"balans": 0, "status": "vip", "xato": 0, "last_task": ""}}
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
    if uid not in users: users[uid] = {"balans": 0, "xato": 0, "last_task": ""}
    
    if message.text == "🖼 Rasm orqali":
        task = random.choice(items)
        users[uid]["last_task"] = task # Topshiriqni saqlash
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📤 Rasm yuborish", callback_data="upload_photo"))
        bot.send_message(uid, f"📸 Topshiriq: *{task}* rasmini yuboring!", parse_mode="Markdown", reply_markup=markup)
    
    elif message.text == "👤 Profil":
        bot.send_message(uid, f"💰 Balans: {users[uid]['balans']} so'm")
    # ... qolgan tugmalar (Help, Top 10, Pul yechish) avvalgidek qoladi ...

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data.split("_")
    
    if call.data == "upload_photo":
        msg = bot.send_message(call.message.chat.id, "Rasmni yuboring:")
        bot.register_next_step_handler(msg, lambda m: bot.send_photo(ADMIN_ID, m.photo[-1].file_id, 
            caption=f"Foydalanuvchi: {m.chat.id}\n📝 Berilgan topshiriq: {users[m.chat.id].get('last_task', 'Noma\'lum')}", 
            reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅", callback_data=f"ok_{m.chat.id}"), 
            types.InlineKeyboardButton("❌", callback_data=f"no_{m.chat.id}"))))
            
    elif data[0] == "ok":
        uid = int(data[1])
        users[uid]["balans"] += 100
        bot.send_message(uid, "✅ Rasm tasdiqlandi! +100 so'm.")
        bot.edit_message_caption(f"✅ Tasdiqlandi. Foydalanuvchi: {uid}", call.message.chat.id, call.message.message_id)
        
    elif data[0] == "no":
        uid = int(data[1])
        users[uid]["balans"] -= 500
        bot.send_message(uid, "❌ Rasm xato! -500 so'm.")
        bot.edit_message_caption(f"❌ Xato deb belgilandi. Foydalanuvchi: {uid}", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
