import os
import json
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- ENV variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID_1 = os.getenv("CHANNEL_ID_1")  # عضویت اجباری

# --- Bot setup ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- Database ---
DATA_FILE = "data.json"
def load():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"groups": {}}, f)
    with open(DATA_FILE) as f:
        return json.load(f)

def save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f)

def ensure_group(d, chat):
    gid = str(chat.id)
    if gid not in d["groups"]:
        d["groups"][gid] = {"users": {}, "rels": {}, "plans": {"expire": None}}
        save(d)
    return gid

# --- Utility ---
def now_jalali():
    try:
        import jdatetime
        return str(jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M"))
    except:
        return str(datetime.now().strftime("%Y-%m-%d %H:%M"))

# --- Start Command ---
@dp.message_handler(commands=["start"])
async def start(m: types.Message):
    if m.chat.type != "private":
        return
    await m.reply("این ربات فقط در گروه‌ها فعال است.")

# --- Register ---
@dp.message_handler(commands=["register"])
async def register(m: types.Message):
    if m.chat.type != "supergroup": return
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("👦 پسر", callback_data=f"gender_boy"),
        InlineKeyboardButton("👧 دختر", callback_data=f"gender_girl")
    )
    await m.reply("لطفاً جنسیت خود را انتخاب کنید:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("gender_"))
async def gender_selected(c: types.CallbackQuery):
    gender = c.data.split("_")[1]
    d = load(); gid = ensure_group(d, c.message.chat)
    uid = str(c.from_user.id)
    d["groups"][gid]["users"][uid] = {
        "name": c.from_user.full_name,
        "username": c.from_user.username,
        "gender": gender,
        "rel": None
    }
    save(d)
    await c.answer("جنسیت با موفقیت ثبت شد.")
    await c.message.edit_text("ثبت‌نام شما انجام شد ✅")

# --- Rel Command ---
@dp.message_handler(commands=["rel"])
async def rel(m: types.Message):
    args = m.get_args().replace("@", "").strip()
    if not args:
        await m.reply("لطفاً آیدی پارتنرت رو وارد کن. مثل: /rel @user")
        return
    d = load(); gid = ensure_group(d, m.chat); uid = str(m.from_user.id)
    target = None
    for k, v in d["groups"][gid]["users"].items():
        if k == args or v.get("username") == args:
            target = k
            break
    if not target:
        await m.reply("❌ کاربر موردنظر ثبت‌نام نکرده.")
        return
    if d["groups"][gid]["users"][uid].get("rel") or d["groups"][gid]["users"][target].get("rel"):
        await m.reply("❌ یکی از شما قبلاً وارد رابطه شده‌اید.")
        return

    d["groups"][gid]["users"][uid]["rel"] = target
    d["groups"][gid]["users"][target]["rel"] = uid
    now = now_jalali()
    d["groups"][gid]["rels"][f"{uid}_{target}"] = {"start": now}
    save(d)
    await m.reply(f"❤️ تبریک! {m.from_user.full_name} و {d['groups'][gid]['users'][target]['name']} باهم رل زدن! \n📅 تاریخ: {now}")

# --- Cut Command ---
@dp.message_handler(commands=["cut"])
async def cut(m: types.Message):
    d = load(); gid = ensure_group(d, m.chat); uid = str(m.from_user.id)
    user = d["groups"][gid]["users"].get(uid)
    if not user or not user.get("rel"):
        await m.reply("شما در رابطه نیستید.")
        return
    target = user["rel"]
    d["groups"][gid]["users"][uid]["rel"] = None
    d["groups"][gid]["users"][target]["rel"] = None
    d["groups"][gid]["rels"].pop(f"{uid}_{target}", None)
    d["groups"][gid]["rels"].pop(f"{target}_{uid}", None)
    save(d)
    await m.reply("💔 رابطه با موفقیت قطع شد.")

# --- Ship Command ---
@dp.message_handler(commands=["ship"])
async def ship(m: types.Message):
    d = load(); gid = ensure_group(d, m.chat)
    users = list(d["groups"][gid]["users"].items())
    boys = [u for u in users if u[1].get("gender") == "boy" and not u[1].get("rel")]
    girls = [u for u in users if u[1].get("gender") == "girl" and not u[1].get("rel")]
    if not boys or not girls:
        await m.reply("🔍 کسی برای شیپ پیدا نشد.")
        return
    import random
    b = random.choice(boys)
    g = random.choice(girls)
    await m.reply(f"💞 شیپ امروز: {b[1]['name']} × {g[1]['name']}")

# --- Admin Panel Command (Placeholder) ---
@dp.message_handler(commands=["panel"])
async def panel(m: types.Message):
    if str(m.from_user.id) != str(ADMIN_ID):
        return
    await m.reply("🎛 پنل مدیریت فعال است. (در حال توسعه)")

# --- Bot start ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
