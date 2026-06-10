import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import os

# 1. SOZLAMALAR
API_TOKEN = "8701965201:AAHAHaUiXmDM_aZmYS7nFiI9qKKrQcRImd4"
bot = telebot.TeleBot(API_TOKEN)
CHANNEL = "@kinosearch_uz"
ADMIN_ID = 7081484236
VIP_FILE = "vip_users.txt"

# VIP faylini tekshirish
if not os.path.exists(VIP_FILE):
    with open(VIP_FILE, "w") as f: pass

def get_vip_list():
    with open(VIP_FILE, "r") as f:
        return f.read().splitlines()

def is_vip(user_id):
    lines = get_vip_list()
    today = datetime.date.today()
    for line in lines:
        if ":" in line:
            uid, end_date = line.split(":")
            if str(user_id) == uid:
                if today <= datetime.date.fromisoformat(end_date):
                    return True
    return False

def check_subscription(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# 2. Rasm va To'lovni boshqarish
@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    if message.from_user.id != ADMIN_ID:
        user_id = message.from_user.id
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"👤 Foydalanuvchi ID: {user_id}\nTo'lov cheki keldi. Tarifni tanlang:")
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("1 hafta (5k)", callback_data=f"vip_7_{user_id}"),
            InlineKeyboardButton("1 oy (15k)", callback_data=f"vip_30_{user_id}"),
            InlineKeyboardButton("6 oy (60k)", callback_data=f"vip_180_{user_id}")
        )
        bot.send_message(ADMIN_ID, "Tanlang:", reply_markup=markup)
        bot.reply_to(message, "✅ Chekingiz qabul qilindi. Administrator tasdiqlashini kuting.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('vip_'))
def set_vip_callback(call):
    if call.from_user.id == ADMIN_ID:
        data = call.data.split('_')
        days = int(data[1])
        user_id = data[2]
        
        end_date = datetime.date.today() + datetime.timedelta(days=days)
        with open(VIP_FILE, "a") as f:
            f.write(f"{user_id}:{end_date}\n")
            
        bot.answer_callback_query(call.id, f"✅ Foydalanuvchi {days} kunga VIP bo'ldi!")
        bot.edit_message_text(f"✅ {user_id} foydalanuvchisi {days} kunga VIP qilindi.", 
                              chat_id=call.message.chat.id, message_id=call.message.message_id)
        try:
            bot.send_message(user_id, "🎉 Tabriklaymiz! To'lovingiz tasdiqlandi va VIP statusi berildi.")
        except: pass

# 3. ASOSIY FUNKSIYALAR
def show_subscribe_menu(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
    markup.add(InlineKeyboardButton(text="🔄 Obuna bo'ldim", callback_data="check_sub"))
    markup.add(InlineKeyboardButton(text="💎 VIP Ta'riflar", callback_data="vip_info"))
    bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun obuna bo'ling yoki VIP ta'rifni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_handler(call):
    if check_subscription(call.message.chat.id):
        bot.answer_callback_query(call.id, "✅ Rahmat! Endi botdan foydalanishingiz mumkin.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="👋 Xush kelibsiz! Kino kodini yuboring:")
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo'lmadingiz!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "vip_info")
def vip_info_handler(call):
    text = (
        "💎 **VIP TA'RIFLAR**\n\n"
        "• 1 hafta - 5,000 so'm\n"
        "• 1 oy - 15,000 so'm\n"
        "• 6 oy - 60,000 so'm\n\n"
        "To'lov uchun screenshot yuboring."
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def back_handler(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
    markup.add(InlineKeyboardButton(text="🔄 Obuna bo'ldim", callback_data="check_sub"))
    markup.add(InlineKeyboardButton(text="💎 VIP Ta'riflar", callback_data="vip_info"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="⚠️ Botdan foydalanish uchun obuna bo'ling yoki VIP ta'rifni tanlang:", reply_markup=markup)

@bot.message_handler(commands=['start', 'getid'])
def general_handlers(message):
    if message.text.startswith('/getid'):
        if message.from_user.id == ADMIN_ID and message.reply_to_message:
            bot.reply_to(message, f"👤 ID: {message.reply_to_message.from_user.id}")
        else: bot.reply_to(message, f"🆔 Sizning ID: {message.from_user.id}")
    else:
        if not check_subscription(message.from_user.id) and not is_vip(message.from_user.id):
            show_subscribe_menu(message)
        else: bot.reply_to(message, "👋 Xush kelibsiz! Kino kodini yuboring:")

@bot.message_handler(func=lambda message: True)
def check_code(message):
    if not check_subscription(message.from_user.id) and not is_vip(message.from_user.id):
        show_subscribe_menu(message)
        return
    if message.text == "1002": bot.reply_to(message, "🎬 'Weak Hero Class 1' topildi!")
    elif message.text == "777": bot.reply_to(message, "🎬 'Spider-Man: No Way Home' topildi!")
    else: bot.reply_to(message, "❌ Kod topilmadi.")

bot.infinity_polling()
