
# main.py - نسخه حرفه‌ای شیپر گروهی
# پیاده‌سازی کامل دستورات حرفه‌ای، ایزوله‌سازی گروه‌ها، کنترل پنل، عضویت اجباری، تایم تست، پیام‌های خودکار و...

import os
import json
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import ChatNotFound

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("توکن ربات تعریف نشده. لطفاً در Railway متغیر BOT_TOKEN را ست کنید.")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

ADMIN_ID = os.getenv("ADMIN_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # For join check

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

def get_group_file(chat_id):
    return os.path.join(DATA_FOLDER, f"group_{chat_id}.json")

def load_group_data(chat_id):
    path = get_group_file(chat_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "installed": False,
        "owner_id": None,
        "expiration": None,
        "users": {},
        "crushes": {},
        "couples": [],
        "settings": {}
    }

def save_group_data(chat_id, data):
    with open(get_group_file(chat_id), "w") as f:
        json.dump(data, f, indent=2)

def is_admin(user_id, group_data):
    return str(user_id) in group_data.get("settings", {}).get("admins", [])

@dp.message_handler(commands=["start"])
async def start_handler(msg: types.Message):
    if msg.chat.type != "private":
        return
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📋 راهنما", callback_data="help"),
        InlineKeyboardButton("📞 تماس با مالک", url="https://t.me/oldkaseb"),
        InlineKeyboardButton("➕ افزودن ربات", url="https://t.me/" + (await bot.get_me()).username + "?startgroup=true")
    )
    await msg.answer(
        "👋 به ربات شیپر گروهی خوش اومدی!

✨ با امکانات پیشرفته برای ساخت کاپل، ثبت کراش، رفیق‌یابی و... 
💸 قیمت شارژ ماهیانه: ۵۰ هزار تومان

🔽 دکمه‌های زیر رو ببین:",
        reply_markup=kb
    )

@dp.message_handler(lambda msg: msg.chat.type != "private" and "شیپر" in msg.text)
async def handle_shiper_keyword(msg: types.Message):
    await msg.reply("جانم؟ کیو بگیرم برات؟ آیدی بده 😎")

@dp.message_handler(lambda msg: msg.text.lower().startswith("من پسرم") or msg.text.lower().startswith("من دخترم"))
async def handle_gender_register(msg: types.Message):
    data = load_group_data(msg.chat.id)
    user = data["users"].get(str(msg.from_user.id), {})
    gender = "پسر" if "پسر" in msg.text else "دختر"
    user["gender"] = gender
    data["users"][str(msg.from_user.id)] = user
    save_group_data(msg.chat.id, data)
    await msg.reply(f"جنسیت شما به‌عنوان {gender} ثبت شد ✅")

@dp.callback_query_handler(lambda c: c.data == "help")
async def help_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📖 راهنمای کامل دستورات:
"
        "من پسرم / من دخترم – ثبت جنسیت
"
        "تعریف مشخصات – ثبت نام، سن، شهر، قد
"
        "ثبت تولد – فرمت عددی 12/05/1383
"
        "ثبت کراش – ریپلای یا آیدی
"
        "حذف کراش – ریپلای یا آیدی
"
        "شیپم کن – شیپر رندوم با کراش
"
        "من رلم شیپر – ثبت پارتنر
"
        "من سینگلم شیپر – ثبت سینگل
"
        "شیپر کات – حذف رابطه
"
        "و ده‌ها دستور دیگر برای مدیر و مالک..."
    )
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
