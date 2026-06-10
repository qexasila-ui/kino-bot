import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import os

# SOZLAMALAR
API_TOKEN = "8888334220:AAEDAzYUSwQcSgvZ35zYWIdai-7K5wNfJC4"
bot = telebot.TeleBot(API_TOKEN)
CHANNEL = "@kinosearch_uz"
ADMIN_ID = 7081484236
VIP_FILE = "vip_users.txt"

# KINO BAZASI (file_id larni shu yerga qo'shib borasan)
kino_bazasi = {
    "1622": "BQACAgADGQEAAUwCU2oo0rWpLt9jc7yfs4G_QoJgXNjXAAIDnQACT49JSeGlY4zBwOMtAQAHbQADOwQ",
    "777": "BQACAgIAAxkBAA..." # Boshqa kinolar uchun
}

if not os.path.exists(VIP_FILE):
    with open(VIP_FILE, "w") as f: pass

def is_vip(user_id):
    today = datetime.date.today()
    if os.path.exists(VIP_FILE):
        with open(VIP_FILE, "r") as f:
            for line in f.read().splitlines():
                if ":" in line:
                    uid, end_date = line.split(":")
                    if str(user_id) == uid and today <= datetime.date.fromisoformat(end_date):
                        return True
    return False

def check_subscription(user_id):
    try:
        status = bot.get_chat_member(CHANNEL, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def show_subscribe_menu(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="✅ Kanalga obuna bo'lish", url=f"https://t.me/{CHANNEL[1:]}"))
    markup.add(InlineKeyboardButton(text="🔄 Obuna bo'ldim", callback_data="check_sub"))
    markup.add(InlineKeyboardButton(text="💎 VIP Ta'riflar", callback_data="vip_info"))
    bot.send_message(message.chat.id, "⚠️ Botdan foydalanish uchun obuna bo'ling:", reply_markup=markup)

# VIP VA KARTA HANDLERLARI
@bot.callback_query_handler(func=lambda call: call.data == "vip_info")
def vip_info_handler(call):
    text = "💎 **VIP TA'RIFLAR**\n1 hafta - 5,000 so'm\n1 oy - 15,000 so'm\n\nTo'lov uchun karta:"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="💳 Karta orqali to'lov", callback_data="pay_card"))
    markup.add(InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_to_menu"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay_card")
def pay_card_handler(call):
    text = "💳 **Karta: 8600123456789012**\nTo'lov qilib, chekni yuboring."
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text="✅ To'lov qildim", callback_data="send_receipt"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "send_receipt")
def ask_receipt(call):
    bot.send_message(call.message.chat.id, "📸 Chekni rasm ko'rinishida yuboring:")
    bot.register_next_step_handler(call.message, process_receipt)

def process_receipt(message):
    if message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📥 Yangi chek! ID: {message.chat.id}")
        bot.reply_to(message, "✅ Chek yuborildi!")
    else: bot.reply_to(message, "❌ Iltimos, rasm yuboring.")

# KINO YUBORISH
@bot.message_handler(func=lambda message: True)
def check_code(message):
    if not check_subscription(message.from_user.id) and not is_vip(message.from_user.id):
        show_subscribe_menu(message)
        return
    
    if message.text in kino_bazasi:
        bot.send_video(message.chat.id, kino_bazasi[message.text], caption="🎬 Marhamat!")
    else:
        bot.reply_to(message, "❌ Kod topilmadi.")

@bot.message_handler(content_types=['video'])
def get_id(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, f"ID: `{message.video.file_id}`", parse_mode="Markdown")

bot.infinity_polling()
