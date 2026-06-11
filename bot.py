import telebot
from telebot import types
import random

TOKEN = "8816384633:AAEVwVo_LOyXjM-41Ob1AyccTYkiBqQd31I"
ADMIN_ID = 7081484236
CHANNEL = "@PulTopinguzz"
bot = telebot.TeleBot(TOKEN)

users = {} 
items = ["Dom", "Ko'cha", "Daraxt", "Televizor", "Gultuvak", "Tova", "Muzlatkich", "Chiroq", "Devor", "Gilam"]

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def get_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🖼 Rasm orqali", "🆘 Help")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    if not check_sub(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("🔄 Tasdiqlash", callback_data="check_sub"))
        bot.send_message(message.chat.id, f"⚠️ Botdan foydalanish uchun {CHANNEL} kanaliga obuna bo'ling va pastdagi tugmani bosing:", reply_markup=markup)
        return
    
    # Obuna bo'lgan bo'lsa
    bot.send_message(message.chat.id, "👋 Xush kelibsiz! Botdan foydalanish uchun to'lov qiling.", reply_markup=get_payment_markup())

def get_payment_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 To'lov qilish", callback_data="pay"),
               types.InlineKeyboardButton("👤 Admin orqali", callback_data="admin_contact"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    if check_sub(call.message.chat.id):
        bot.edit_message_text("✅ Obuna tasdiqlandi!", call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Botdan foydalanish uchun 5.000 so'm to'lov qiling:", reply_markup=get_payment_markup())
    else:
        bot.answer_callback_query(call.id, "❌ Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data in ["pay", "admin_contact"])
def handle_pay(call):
    if call.data == "pay":
        bot.edit_message_text("💳 Karta: 4073420029671058\nEga: Boymurodova N.\nTo'lov qilganingizdan so'ng chekni yuboring.", call.message.chat.id, call.message.message_id)
    else:
        text = "Assalomu Aleykum men PUL TOP botiga tolov qilmoqchi edim iltimos karta raqam yuboring!"
        bot.send_message(call.message.chat.id, f"Adminga yozish uchun: [Murojaat](https://t.me/{ADMIN_ID}?text={text})", parse_mode="Markdown")

@bot.message_handler(commands=['addid'])
def add_id(message):
    if message.chat.id == ADMIN_ID:
        try:
            uid = int(message.text.split()[1])
            users[uid] = {"balans": 0, "status": "vip", "xato": 0}
            bot.send_message(uid, "✅ Assalomu aleykum! Marhamat, botdan foydalanishni boshlash uchun tugmalardan birini tanlang.", reply_markup=get_menu())
            bot.reply_to(message, "Foydalanuvchi VIP qilindi.")
        except: bot.reply_to(message, "Xato! Format: /addid user_id")

@bot.message_handler(func=lambda message: message.text == "🖼 Rasm orqali")
def send_task(message):
    if message.chat.id not in users or users[message.chat.id].get("status") != "vip":
        bot.reply_to(message, "❌ Siz hali VIP emassiz!")
        return
    item = random.choice(items)
    msg = f"📸 Marhamat qilib *{item}* rasmini rasmga olib yuboring!\n\nBalans: {users[message.chat.id]['balans']} so'm\n⚠️ 3 marta xato qilsangiz 12 soatga bloklanasiz."
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📤 Rasm yuborish", callback_data="upload_photo"))
    bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "upload_photo")
def ask_photo(call):
    msg = bot.send_message(call.message.chat.id, "Marhamat rasmingizni yuboring:")
    bot.register_next_step_handler(msg, verify_photo)

def verify_photo(message):
    if message.photo:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{message.chat.id}"),
                   types.InlineKeyboardButton("❌ Xato", callback_data=f"no_{message.chat.id}"))
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"Foydalanuvchi: {message.chat.id}", reply_markup=markup)
        bot.reply_to(message, "Rasm admin tekshiruviga yuborildi.")
    else: bot.reply_to(message, "Iltimos, faqat rasm yuboring!")

@bot.callback_query_handler(func=lambda call: call.data.startswith(("ok_", "no_")))
def admin_action(call):
    uid = int(call.data.split("_")[1])
    if "ok_" in call.data:
        users[uid]["balans"] += 100
        bot.send_message(uid, f"✅ Rasm tasdiqlandi! Balans: {users[uid]['balans']} so'm")
    else:
        users[uid]["balans"] -= 500
        bot.send_message(uid, f"❌ Rasm xato! Balans: {users[uid]['balans']} so'm")
    bot.edit_message_caption("Bajarildi.", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
