import telebot
from telebot import types
import random

TOKEN = "8816384633:AAEVwVo_LOyXjM-41Ob1AyccTYkiBqQd31I"
ADMIN_ID = 7081484236
ADMIN_USERNAME = "@PulTopBot_admin" # O'zingning usernameingni yoz
CHANNEL = "@PulTopinguzz"

bot = telebot.TeleBot(TOKEN)
users = {} 
items = ["Dom", "Ko'cha", "Daraxt", "Televizor", "Gultuvak", "Tova", "Muzlatkich", "Chiroq", "Devor", "Gilam"]

# --- YORDAMCHI FUNKSIYALAR ---
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def get_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🖼 Rasm orqali", "🆘 Help")
    return markup

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    if not check_sub(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
        markup.add(types.InlineKeyboardButton("🔄 Tasdiqlash", callback_data="check_sub"))
        bot.send_message(message.chat.id, f"⚠️ Botdan foydalanish uchun {CHANNEL} kanaliga obuna bo'ling va tugmani bosing:", reply_markup=markup)
        return
    
    bot.send_message(message.chat.id, "👋 Xush kelibsiz! Botdan foydalanish uchun to'lov qiling:", reply_markup=get_payment_markup())

def get_payment_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 To'lov qilish", callback_data="pay"),
               types.InlineKeyboardButton("👤 Admin orqali", callback_data="admin_contact"))
    return markup

# --- TO'LOV VA ADMIN ---
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    if check_sub(call.message.chat.id):
        bot.edit_message_text("✅ Obuna tasdiqlandi!", call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Botdan foydalanish uchun 5.000 so'm to'lov qiling:", reply_markup=get_payment_markup())
    else:
        bot.answer_callback_query(call.id, "❌ Obuna bo'lmadingiz!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data in ["pay", "admin_contact", "send_receipt"])
def handle_pay(call):
    if call.data == "pay":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📤 Chek yuborish", callback_data="send_receipt"))
        bot.edit_message_text("💳 Karta: 4073420029671058\nEga: Boymurodova N.\nTo'lov qilganingizdan so'ng chekni yuboring.", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data == "admin_contact":
        bot.send_message(call.message.chat.id, f"👤 Admin bilan bog'lanish: {ADMIN_USERNAME}")
    elif call.data == "send_receipt":
        msg = bot.send_message(call.message.chat.id, "Iltimos, to'lov chekini rasm ko'rinishida yuboring:")
        bot.register_next_step_handler(msg, forward_receipt)

def forward_receipt(message):
    if message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📥 Yangi to'lov cheki!\nFoydalanuvchi: {message.chat.id}")
        bot.reply_to(message, "✅ Chekingiz adminga yuborildi.")
    else: bot.reply_to(message, "❌ Iltimos, faqat rasm yuboring.")

# --- ADMIN PANEL ---
@bot.message_handler(commands=['addid'])
def add_id(message):
    if message.chat.id == ADMIN_ID:
        try:
            uid = int(message.text.split()[1])
            users[uid] = {"balans": 0, "status": "vip"}
            bot.send_message(uid, "✅ To'lovingiz tasdiqlandi! Endi botdan foydalanishingiz mumkin.", reply_markup=get_menu())
            bot.reply_to(message, "Foydalanuvchi VIP qilindi.")
        except: bot.reply_to(message, "Format: /addid user_id")

# --- O'YIN ---
@bot.message_handler(func=lambda message: message.text == "🖼 Rasm orqali")
def send_task(message):
    if message.chat.id not in users or users[message.chat.id].get("status") != "vip":
        return bot.reply_to(message, "❌ Siz hali VIP emassiz!")
    item = random.choice(items)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📤 Rasm yuborish", callback_data="upload_photo"))
    bot.send_message(message.chat.id, f"📸 *{item}* rasmini yuboring!\n⚠️ 3 marta xato qilsangiz 12 soatga bloklanasiz.", parse_mode="Markdown", reply_markup=markup)

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
    else: bot.reply_to(message, "❌ Rasm yuboring!")

@bot.callback_query_handler(func=lambda call: call.data.startswith(("ok_", "no_")))
def admin_action(call):
    uid = int(call.data.split("_")[1])
    if "ok_" in call.data:
        users[uid]["balans"] = users[uid].get("balans", 0) + 100
        bot.send_message(uid, f"✅ Rasm tasdiqlandi! Balans: {users[uid]['balans']} so'm")
    else:
        users[uid]["balans"] = users[uid].get("balans", 0) - 500
        bot.send_message(uid, f"❌ Rasm xato! Balans: {users[uid]['balans']} so'm")
    bot.edit_message_caption("Bajarildi.", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
