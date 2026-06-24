import logging
import asyncio
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- SOZLAMALAR ---
BOT_TOKEN = "8274373991:AAE5lGfeJOSlaO8fIF8b7mtlP54dKVF3svc"
ADMIN_ID = 7081484236
REQUIRED_CHANNEL = "@GizaKino"
CARD_NUMBER = "4073 4200 2967 1058"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- BAZA BILAN ISHLASH ---
def init_db():
    conn = sqlite3.connect("bot_base.db")
    cursor = conn.cursor()
    # VIP foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            vip_until TEXT
        )
    """)
    # Kinolar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            movie_code TEXT PRIMARY KEY,
            file_id TEXT
        )
    """)
    conn.commit()
    conn.close()

def is_vip(user_id):
    if user_id == ADMIN_ID:
        return True
    conn = sqlite3.connect("bot_base.db")
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
    conn = sqlite3.connect("bot_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    
    now = datetime.now()
    if res and res[0]:
        current_until = datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S")
        if current_until > now:
            new_until = current_until + timedelta(days=days)
        else:
            new_until = now + timedelta(days=days)
    else:
        new_until = now + timedelta(days=days)
        
    cursor.execute("INSERT OR REPLACE INTO users (user_id, vip_until) VALUES (?, ?)", 
                   (user_id, new_until.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# --- HOZIRGI HOLATLAR (FSM) ---
class BotStates(StatesGroup):
    SEND_CHECK = State()
    ADD_MOVIE_CODE = State()
    GET_MOVIE = State()

# --- KANALA OBUNA BO'LGANLIKNI TEKSHIRISH ---
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# --- ASOSIY MENYU ---
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💎 Premium")],
            [KeyboardButton(text="🔍 Kino qidirish")]
        ],
        resize_keyboard=True
    )

# --- /START BUYRUG'I ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    is_sub = await check_subscription(user_id)
    
    if not is_sub:
        btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Obuna bo'lish 🚀", url=f"https://t.me/{REQUIRED_CHANNEL.replace('@','')}")],
            [InlineKeyboardButton(text="Tekshirish ✅", callback_data="check_sub")]
        ])
        await message.answer(f"Botdan foydalanish uchun {REQUIRED_CHANNEL} kanaliga obuna bo'ling!", reply_markup=btn)
    else:
        await message.answer(f"Xush kelibsiz, {message.from_user.full_name}!\nKerakli bo'limni tanlang:", reply_markup=main_menu())

# --- OBUNANI TEKSHIRISH TUGMASI ---
@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.delete()
        await call.message.answer(f"Obuna tasdiqlandi! Marhamat, {call.from_user.full_name}.", reply_markup=main_menu())
    else:
        await call.answer("Siz hali kanalga obuna bo'lmagansiz!", show_alert=True)

# --- PREMIUM TUGMASI ---
@dp.message(F.text == "💎 Premium")
async def premium_sec(message: types.Message):
    btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Humo 💳", callback_data="buy_humo")],
        [InlineKeyboardButton(text="Orqaga 🔙", callback_data="back_main")]
    ])
    await message.answer("Siz Premium xarid qilmoqchi bo'lsangiz xarid turini tanlang:\n\n💰 1 oy - 10.000 UZS", reply_markup=btn)

@dp.callback_query(F.data == "back_main")
async def back_main(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Asosiy menyu", reply_markup=main_menu())

# --- HUMO TANLANGANDA ---
@dp.callback_query(F.data == "buy_humo")
async def buy_humo(call: types.CallbackQuery):
    btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Chek yuborish", callback_data="send_check")],
        [InlineKeyboardButton(text="Orqaga 🔙", callback_data="back_main")]
    ])
    text = f"💳 Karta raqam: `{CARD_NUMBER}`\n\nTo'lovni amalga oshirib, pastdagi tugma orqali chekni (rasmini) yuboring."
    await call.message.edit_text(text, reply_markup=btn, parse_mode="Markdown")

# --- CHEK YUBORISH BOSHQARIYASI ---
@dp.callback_query(F.data == "send_check")
async def send_check_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Marhamat, chekni rasm ko'rinishida yuboring...")
    await state.set_state(BotStates.SEND_CHECK)
    await call.answer()

@dp.message(BotStates.SEND_CHECK, F.photo)
async def receive_check(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"
    
    # Adminga chek yuborish
    admin_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{user_id}")]
    ])
    
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        caption=f"🔔 Yangi to'lov cheki!\n👤 Foydalanuvchi: {message.from_user.full_name}\n🆔 ID: `{user_id}`\nUsername: {username}\n\nTasdiqlash uchun: `/addvip {user_id}`",
        parse_mode="Markdown",
        reply_markup=admin_btn
    )
    
    await message.answer("Kuting, admin ko'rib chiqmoqda...")
    await state.clear()

# --- ADMIN RAD ETGANDA ---
@dp.callback_query(F.data.startswith("reject_"))
async def reject_payment(call: types.CallbackQuery):
    target_user_id = int(call.data.split("_")[1])
    try:
        await bot.send_message(chat_id=target_user_id, text="❌ Xaridingiz tasdiqlanmadi. Tekshirib qayta yuboring.")
        await call.message.reply("Foydalanuvchiga rad etilgani haqida xabar yuborildi.")
    except Exception as e:
        await call.message.reply(f"Xabar yuborishda xatolik: {e}")
    await call.answer()

# --- ADMIN /ADDVIP KAMANDASI ---
@dp.message(Command("addvip"), F.from_user.id == ADMIN_ID)
async def cmd_addvip(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            return await message.answer("Xato foydalanish. Namuna: `/addvip ID`")
        
        target_id = int(args[1])
        add_vip_days(target_id, 30)
        
        await message.answer(f"✅ {target_id} foydalanuvchiga 1 oy VIP berildi.")
        
        # Foydalanuvchini ogohlantirish
        user_info = await bot.get_chat(target_id)
        nick = user_info.full_name
        await bot.send_message(
            chat_id=target_id,
            text=f"🎉 To'lovingiz tasdiqlandi!\nMarhamat {nick}, kino kodini yuboring (Pastdagi 'Kino qidirish' tugmasini bosing)."
        )
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")

# --- ADMIN KINO QO'SHISH (VIDEO YUBORGANDA ID OLISH) ---
@dp.message(F.video, F.from_user.id == ADMIN_ID)
async def admin_get_video_id(message: types.Message, state: FSMContext):
    video_id = message.video.file_id
    await state.update_data(current_video_id=video_id)
    await message.answer(f"🎬 Video ID-si olindi!\n\nEndi ushbu kino uchun **kod** kiriting (Masalan: 101):")
    await state.set_state(BotStates.ADD_MOVIE_CODE)

@dp.message(BotStates.ADD_MOVIE_CODE, F.from_user.id == ADMIN_ID)
async def admin_save_movie(message: types.Message, state: FSMContext):
    movie_code = message.text.strip()
    data = await state.get_data()
    video_id = data.get("current_video_id")
    
    conn = sqlite3.connect("bot_base.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO movies (movie_code, file_id) VALUES (?, ?)", (movie_code, video_id))
        conn.commit()
        await message.answer(f"✅ Kino muvaffaqiyatli bazaga qo'shildi!\n🔑 Kodi: `{movie_code}`")
    except Exception as e:
        await message.answer(f"Xatolik: {e}")
    finally:
        conn.close()
    await state.clear()

# --- KINO QIDIRISH TUGMASI ---
@dp.message(F.text == "🔍 Kino qidirish")
async def search_movie_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not await check_subscription(user_id):
        return await message.answer(f"Avval kanalga obuna bo'ling {REQUIRED_CHANNEL}")
        
    if not is_vip(user_id):
        return await message.answer("⚠️ Kinolarni ko'rish uchun sizda Premium status bo'lishi kerak. Iltimos, menyudan '💎 Premium' bo'limiga o'tib faollashtiring.")
        
    await message.answer(f"Marhamat {message.from_user.full_name}, kino kodini yuboring:")
    await state.set_state(BotStates.GET_MOVIE)

# --- KOD ORQALI KINO YUBORISH ---
@dp.message(BotStates.GET_MOVIE)
async def send_movie_by_code(message: types.Message, state: FSMContext):
    movie_code = message.text.strip()
    
    conn = sqlite3.connect("bot_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT file_id FROM movies WHERE movie_code = ?", (movie_code,))
    res = cursor.fetchone()
    conn.close()
    
    if res:
        await message.answer_video(video=res[0], caption=f"🎬 Kod: {movie_code}\n\n@GizaKino kanali uchun maxsus!")
    else:
        await message.answer("❌ Afsuski, bunday kodli kino topilmadi. Kodni to'g'ri kiritganingizni tekshiring.")
    
    await state.clear()

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    init_db()
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
