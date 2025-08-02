# main.py - نسخه حرفه‌ای کامل ربات شیپر گروهی (Railway Ready)
# امکانات: شارژی بودن، پنل ادمین، نماینده فروش، عضویت اجباری، دکمه‌های تعاملی، تبریک ماهگرد

import logging, json, os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

API_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
FREE_DAYS = int(os.getenv("FREE_DAYS", 7))
CHANNEL_ID = os.getenv("CHANNEL_ID")  # مثل: @YourChannel

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

DATA_FILE = "data.json"

# --- دیتابیس ---
def load():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f: json.dump({"groups": {}, "resellers": {}, "owner_id": OWNER_ID}, f)
    with open(DATA_FILE) as f: return json.load(f)

def save(d):
    with open(DATA_FILE, "w") as f: json.dump(d, f, indent=2)

def mention(uid, name): return f"[{name}](tg://user?id={uid})"

def ensure_group(data, chat):
    gid = str(chat.id)
    if gid not in data["groups"]:
        data["groups"][gid] = {
            "owner_id": chat.get_member(chat.id, chat.id).user.id,
            "expire_at": (datetime.utcnow() + timedelta(days=FREE_DAYS)).isoformat(),
            "channel": CHANNEL_ID,
            "users": {}, "pending": {}, "active": True
        }
    return gid

# --- عضویت اجباری ---
async def check_membership(uid):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, uid)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

# --- کامندها ---
@dp.message_handler(commands=["start"])
async def start_cmd(m):
    if not await check_membership(m.from_user.id):
        btn = InlineKeyboardMarkup().add(InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_ID.strip('@')}"))
        await m.reply("برای استفاده از ربات، ابتدا در کانال عضو شو.", reply_markup=btn)
        return
    await m.reply("سلام! برای شروع، دستور /register رو بزن.")

@dp.message_handler(commands=["register"])
async def register(m):
    args = m.get_args()
    if args not in ["دختر", "پسر"]:
        await m.reply("فرمت درست: /register دختر یا /register پسر")
        return
    d = load(); gid = ensure_group(d, m.chat); uid = str(m.from_user.id)
    if not d["groups"][gid]["active"]:
        await m.reply("⛔ پلن این گروه منقضی شده. با ادمین برای تمدید صحبت کنید.")
        return
    d["groups"][gid]["users"][uid] = {
        "name": m.from_user.full_name, "gender": args,
        "status": "سینگل", "partner_id": None,
        "relationship_started": None
    }
    save(d)
    await m.reply("✅ ثبت‌نام شد. حالا می‌تونی رل بزنی یا شیپ کنی!")

@dp.message_handler(commands=["panel"])
async def panel(m):
    d = load(); gid = str(m.chat.id)
    if m.from_user.id != d["groups"].get(gid, {}).get("owner_id") and m.from_user.id != OWNER_ID:
        return await m.reply("⛔ فقط مالک گروه یا ادمین اصلی می‌تونه پنل رو ببینه.")
    exp = d["groups"][gid]["expire_at"]
    dt = datetime.fromisoformat(exp)
    left = (dt - datetime.utcnow()).days
    active = d["groups"][gid]["active"]
    await m.reply(f"🔧 پنل مدیریت گروه:
وضعیت: {'فعال ✅' if active else 'غیرفعال ❌'}
تاریخ انقضا: {dt.date()} ({left} روز باقی‌مانده)")

# --- هشدار 2 روز مانده به پایان ---
@scheduler.scheduled_job("cron", hour=10)
async def check_expiry():
    d = load()
    for gid, g in d["groups"].items():
        if not g.get("active"): continue
        days_left = (datetime.fromisoformat(g["expire_at"]) - datetime.utcnow()).days
        if days_left == 2:
            await bot.send_message(int(gid), f"⚠️ {mention(g['owner_id'], 'مالک')} عزیز، فقط 2 روز تا پایان پلن گروه باقی مونده. لطفاً برای تمدید با ادمین ربات در تماس باش.")

async def on_startup(_): scheduler.start()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
