import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta

# Token va Ma'lumotlar (ID raqamingiz to'g'riligini tekshiring)
TOKEN = "8274373991:AAE5lGfeJOSlaO8fIF8b7mtlP54dKVF3svc"  
ADMIN_ID = 7081484236
CHANNEL = "@GizaKino"  
CARD_NUMBER = "4073 4200 2967 1058"

bot = telebot.TeleBot(TOKEN)

# --- BAZA ISHLARI ---
def init_db():
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, vip_until TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS movies (movie_code TEXT PRIMARY KEY, file_id TEXT)")
    conn.commit()
    conn.close()

init_db()

def is_vip(user_id):
    if user_id == ADMIN_ID:
        return True
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    if res and res[0]:
        until = datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S")
        if until > datetime.now():
            return True
    return False

def add_vip_days(user_id, days=30):
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    now = datetime.now()
    if res and res[0]:
        current_until = datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S")
        new_until = (current_until if current_until > now else now) + timedelta(days=days)
    else:
        new_until = now + timedelta(days=days)
    cursor.execute("INSERT OR REPLACE INTO users (user_id, vip_until) VALUES (?, ?)", (user_id, new_until.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("💎 Premium"), types.KeyboardButton("🔍 Kino qidirish"))
    return markup

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Obuna bo'lish 🚀", url=f"https://t.me/{CHANNEL.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("Tekshirish ✅", callback_data="check_sub"))
        bot.send_message(message.chat.id, f"Botdan foydalanish uchun avval {CHANNEL} kanaliga obuna bo'ling!", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"Xush kelibsiz, {message.from_user.full_name}!", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub_callback(call):
    if check_subscription(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f"Obuna tasdiqlandi! Marhamat, {call.from_user.full_name}.", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "Siz hali kanalga obuna bo'lmagansiz!", show_alert=True)

# --- PREMIUM BO'LIMI ---
@bot.message_handler(func=lambda message: message.text == "💎 Premium")
def premium_sec(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("Humo 💳", callback_data="buy_humo"), types.InlineKeyboardButton("Orqaga 🔙", callback_data="back_main"))
    bot.send_message(message.chat.id, "Siz Premium xarid qilmoqchi bo'lsangiz xarid turini tanlang:\n\n💰 1 oy - 10.000 UZS", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["buy_humo", "back_main", "send_check"])
def inline_navigation(call):
    if call.data == "back_main":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Asosiy menyu", reply_markup=main_menu())
    
    elif call.data == "buy_humo":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📸 Chek yuborish", callback_data="send_check"))
        markup.add(types.InlineKeyboardButton("Orqaga 🔙", callback_data="back_main"))
        text = f"💳 Karta raqam: `{CARD_NUMBER}`\n\nTo'lovni amalga oshirib, pastdagi tugma orqali chekni (rasmini) yuboring."
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        
    elif call.data == "send_check":
        msg = bot.send_message(call.message.chat.id, "Marhamat, chekni yuboring (Rasm, fayl yoki matn ko'rinishida)...")
        bot.register_next_step_handler(msg, receive_all_checks)

# --- HAR QANDAY CHEKNI QABUL QILISH (YANGILANDI) ---
def receive_all_checks(message):
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}"))
    
    caption_text = f"🔔 Yangi to'lov cheki!\n👤 Foydalanuvchi: {message.from_user.full_name}\n🆔 ID: `{user_id}`\nUsername: {username}\n\nTasdiqlash uchun: `/addvip {user_id}`"
    
    try:
        # Agar rasm bo'lsa
        if message.photo:
            photo_id = message.photo[-1].file_id
            bot.send_photo(ADMIN_ID, photo_id, caption=caption_text, parse_mode="Markdown", reply_markup=markup)
        # Agar fayl/hujjat bo'lsa
        elif message.document:
            doc_id = message.document.file_id
            bot.send_document(ADMIN_ID, doc_id, caption=caption_text, parse_mode="Markdown", reply_markup=markup)
        # Agar shunchaki tekst yuborgan bo'lsa
        else:
            bot.send_message(ADMIN_ID, f"{caption_text}\n\n📝 Xabar matni: {message.text}", parse_mode="Markdown", reply_markup=markup)
            
        bot.send_message(message.chat.id, "Kuting admin ko'rib chiqmoqda...")
    except Exception as e:
        bot.send_message(message.chat.id, f"Xatolik yuz berdi, qayta urinib ko'ring yoki adminga yozing.")
        bot.send_message(ADMIN_ID, f"Botda xabar yuborishda xato: {e}")

# --- ADMIN RAD ETGANDA ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_payment(call):
    target_user_id = int(call.data.split("_")[1])
    try:
        bot.send_message(target_user_id, "❌ Xaridingiz tasdiqlanmadi tekshirib qayta yuboring")
        bot.reply_to(call.message, "Foydalanuvchiga rad etish xabari yuborildi.")
    except Exception as e:
        bot.reply_to(call.message, f"Xatolik: {e}")

# --- ADMIN /ADDVIP BUYRUG'I ---
@bot.message_handler(commands=['addvip'])
def cmd_addvip(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Namuna: `/addvip ID`")
            return
        target_id = int(args[1])
        add_vip_days(target_id, 30)
        bot.reply_to(message, f"✅ {target_id} foydalanuvchiga 1 oy VIP berildi.")
        
        user_info = bot.get_chat(target_id)
        bot.send_message(target_id, f"🎉 To'lovingiz tasdiqlandi!\nMarhamat {user_info.first_name} kino kodini yuboring (Pastdagi 'Kino qidirish' tugmasini bosing).")
    except Exception as e:
        bot.reply_to(message, f"Xatolik: {e}")

# --- ADMIN VIDEO QABUL QILISH ---
@bot.message_handler(content_types=['video'])
def admin_get_video(message):
    if message.from_user.id != ADMIN_ID:
        return
    video_id = message.video.file_id
    msg = bot.reply_to(message, f"🎬 Video ID-si olindi!\n\nEndi ushbu kino uchun **kod** kiriting:")
    bot.register_next_step_handler(msg, admin_save_movie, video_id)

def admin_save_movie(message, video_id):
    if message.from_user.id != ADMIN_ID:
        return
    movie_code = message.text.strip()
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO movies (movie_code, file_id) VALUES (?, ?)", (movie_code, video_id))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"✅ Kino bazaga qo'shildi!\n🔑 Kodi: `{movie_code}`")

# --- KINO QIDIRISH ---
@bot.message_handler(func=lambda message: message.text == "🔍 Kino qidirish")
def search_movie_start(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        bot.send_message(message.chat.id, f"Avval kanalga obuna bo'ling {CHANNEL}")
        return
    if not is_vip(user_id):
        bot.send_message(message.chat.id, "⚠️ Kinolarni ko'rish uchun sizda Premium status bo'lishi kerak. Iltimos, '💎 Premium' bo'limidan faollashtiring.")
        return
    msg = bot.send_message(message.chat.id, "Marhamat, kino kodini yuboring:")
    bot.register_next_step_handler(msg, send_movie_by_code)

def send_movie_by_code(message):
    movie_code = message.text.strip()
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT file_id FROM movies WHERE movie_code = ?", (movie_code,))
    res = cursor.fetchone()
    conn.close()
    
    if res:
        bot.send_video(message.chat.id, res[0], caption=f"🎬 Kod: {movie_code}\n\n{CHANNEL} kanali uchun maxsus!")
    else:
        bot.send_message(message.chat.id, "❌ Afsuski, bunday kodli kino topilmadi.")

print("Bot ishlamoqda...")
bot.infinity_polling()
