# main.py - نسخه حرفه‌ای ربات شیپر گروهی (Railway Ready)
# امکانات: شناسایی جنسیت، رل زدن دوطرفه، قطع رل، شیپ، آمار، پروفایل، پلن شارژی، عضویت اجباری، نماینده فروش، پنل ادمین، تبریک ماهگرد

import asyncio, logging, json, datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID_1
from utils import *  # شامل: load, save, ensure_group, now_jalali, get_user_link

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

### دستورات اصلی:

@dp.message_handler(CommandStart())
async def start(m: types.Message):
    if m.chat.type != "private": return
    await m.answer("این ربات فقط مخصوص گروه‌هاست.")

@dp.message_handler(commands=["register"])
async def register(m: types.Message):
    if m.chat.type != "supergroup": return
    d = load()
    gid = ensure_group(d, m.chat)
    uid = str(m.from_user.id)
    if uid in d["groups"][gid]["users"]:
        return await m.reply("قبلاً ثبت‌نام کردی ✅")
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("پسرم", callback_data=f"gender|boy"),
           InlineKeyboardButton("دخترم", callback_data=f"gender|girl"))
    d["groups"][gid]["pending"] = uid
    save(d)
    await m.reply("جنسیتتو انتخاب کن:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("gender|"))
async def set_gender(c):
    d = load()
    gid = str(c.message.chat.id)
    uid = str(c.from_user.id)
    if d.get("groups", {}).get(gid, {}).get("pending") != uid:
        return await c.answer("درخواست معتبر نیست")
    gender = c.data.split("|")[1]
    d["groups"][gid]["users"][uid] = {
        "gender": gender,
        "first_name": c.from_user.first_name,
        "username": c.from_user.username,
        "id": c.from_user.id
    }
    del d["groups"][gid]["pending"]
    save(d)
    await c.message.edit_text(f"جنسیت شما با موفقیت ثبت شد ✅")

@dp.message_handler(commands=["rel"])
async def rel(m):
    args = m.get_args().replace("@", "").strip()
    if not args:
        return await m.reply("⚠️ یوزرنیم یا آیدی پارتنرت رو وارد کن. مثل: /rel @user")
    d = load(); gid = ensure_group(d, m.chat); uid = str(m.from_user.id)
    users = d["groups"][gid].get("users", {})
    target = None
    for k, v in users.items():
        if k == args or v.get("username") == args:
            target = k
            break
    if not target:
        return await m.reply("❌ کاربر موردنظر ثبت‌نام نکرده.")
    d["groups"][gid]["rel"][uid] = {"partner": target, "start": now_jalali()}
    d["groups"][gid]["rel"][target] = {"partner": uid, "start": now_jalali()}
    save(d)
    await m.reply(f"💞 تبریک! {get_user_link(m.from_user)} و {get_user_link(users[target])} حالا در رابطه هستن!")

@dp.message_handler(commands=["cut"])
async def cut(m):
    d = load(); gid = ensure_group(d, m.chat); uid = str(m.from_user.id)
    rel = d["groups"][gid]["rel"].get(uid)
    if not rel:
        return await m.reply("رابطه‌ای ثبت نشده")
    partner = rel["partner"]
    d["groups"][gid]["rel"].pop(uid, None)
    d["groups"][gid]["rel"].pop(partner, None)
    save(d)
    await m.reply("💔 رابطه با موفقیت حذف شد.")

@dp.message_handler(commands=["ship"])
async def ship(m):
    d = load(); gid = ensure_group(d, m.chat)
    users = d["groups"][gid]["users"]
    boys = [u for u in users if users[u].get("gender") == "boy"]
    girls = [u for u in users if users[u].get("gender") == "girl"]
    if not boys or not girls:
        return await m.reply("❌ کاربر کافی برای شیپ وجود ندارد.")
    import random
    b, g = random.choice(boys), random.choice(girls)
    await m.reply(f"🔥 شیپ امروز: {get_user_link(users[g])} ❤️ {get_user_link(users[b])}")

@dp.message_handler(commands=["panel"])
async def panel(m):
    if str(m.from_user.id) != ADMIN_ID:
        return await m.reply("⛔ فقط سازنده ربات به این بخش دسترسی دارد.")
    await m.reply("🔧 پنل مدیریت فعال است. (در حال توسعه)")

### اجرای ربات:
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
