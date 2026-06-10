import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# KINO SEARCH BOT - Video yuboradigan tayyor kod
API_TOKEN = "8701965201:AAHAHaUiXmDM_aZmYS7nFiI9qKKrQcRImd4"
bot = telebot.TeleBot(API_TOKEN)

# /start buyrug'i
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    kanal_tugmasi = InlineKeyboardButton(text="🎬 Boshqa Kinolar (Kanalimiz) 🎬", url="https://t.me/telegram")
    markup.add(kanal_tugmasi)
    
    bot.send_message(
        message.chat.id,
        "👋 Assalomu alaykum, KINO SEARCH BOTga xush kelibsiz!\n\n"
        "🔢 Marhamat, ko'rmoqchi bo'lgan kino kodini yuboring:\n\n"
        "⚠️ Diqqat! Boshqa kinolar kerak bo'lsa, pastdagi tugma orqali kanalimizga o'ting: 👇",
        reply_markup=markup
    )

# 🎬 KINO QO'SHISH VA TEKSHIRISH BO'LIMI
@bot.message_handler(func=lambda message: True)
def check_code(message):
    user_text = message.text

    # 1-KINO (Video yuborish)
    if user_text == "5117":
        bot.send_video(
            message.chat.id, 
            "AAMCAgADGQEAAUwCU2oo0rWpLt9jc7yfs4G_QoJgXNjXAAIDnQACT49JSeGlY4zBwOMtAQAHbQADOwQ", 
            caption="🎬 **Kino topildi!**\n\n🍿 Nomi: 'Chin Muhabbat' filmi (2014)\n🔥 Sifati: 720HD\n\nMarhamat, tomosha qiling!"
        )
        
    # 2-KINO
    elif user_text == "1002":
        bot.reply_to(
            message,
            "🎬 **Kino topildi!**\n\n"
            "🍿 Nomi: 'Weak Hero Class 1' (Uzbek Dublyaj)\n"
            "🔥 Janri: Drama / Action\n\n"
            "Marhamat, tomosha qiling!"
        )
        
    # 3-KINO
    elif user_text == "777":
        bot.reply_to(
            message,
            "🎬 **Kino topildi!**\n\n"
            "🍿 Nomi: 'Spider-Man: No Way Home'\n"
            "🔥 Janri: Superkahramon / Marvel\n\n"
            "Marhamat, tomosha qiling!"
        )

    # 4-YANGI KINO
    elif user_text == "2026":
        bot.reply_to(
            message,
            "🎬 **Kino topildi!**\n\n"
            "🍿 Nomi: 'Captain America: Brave New World'\n"
            "🔥 Janri: Action / Sci-Fi\n\n"
            "Marhamat, tomosha qiling!"
        )

    # 🚷 AGAR KOD TOPILMASA
    else:
        bot.reply_to(
            message,
            "❌ **Xato!** Bu kod bo'yicha hech qanday kino topilmadi.\n"
            "Iltimos, kodni qaytadan tekshirib ko'ring!"
        )

# Botni uzluksiz ishga tushirish
print("KINO SEARCH BOT videofayl bilan tayyor...")
bot.infinity_polling()
