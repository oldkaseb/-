# main.py - نسخه حرفه‌ای شیپر گروهی

import os
import json
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("توکن BOT_TOKEN تنظیم نشده. لطفاً آن را در Railway وارد کن.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)
def get_group_file(chat_id):
    return os.path.join(DATA_FOLDER, f"group_{chat_id}.json")

def load_group_data(chat_id):
    path = get_group_file(chat_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "installed": False,
        "owner_id": None,
        "expiration": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "users": {},
        "crushes": {},
        "couples": [],
        "settings": {
            "admins": [],
            "forced_channel": None,
            "sales": [],
            "owners": [],
        }
    }

def save_group_data(chat_id, data):
    with open(get_group_file(chat_id), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    if msg.chat.type != "private":
        return

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📋 راهنما", callback_data="help"),
        InlineKeyboardButton("📞 تماس با مالک", url="https://t.me/oldkaseb"),
        InlineKeyboardButton("➕ افزودن ربات", url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true")
    )

    await msg.answer(
        """👋 به ربات شیپر گروهی خوش اومدی!

✨ با امکانات کامل برای کراش، رل، رفیق‌یابی، پروفایل حرفه‌ای و...

🆓 استفاده رایگان ۷ روزه برای هر گروه پس از نصب
💸 شارژ ماهیانه: ۵۰ هزار تومان

🔘 دکمه‌های زیر رو ببین:""",
        reply_markup=kb
    )
@dp.message_handler(lambda m: m.chat.type != "private" and "شیپر" in m.text.lower())
async def keyword_handler(msg: types.Message):
    await msg.reply("جانم؟ کیو بگیرم برات؟ آیدی بده 😎")
@dp.message_handler(lambda m: m.chat.type != "private" and ("من پسرم" in m.text or "من دخترم" in m.text))
async def gender_register(msg: types.Message):
    data = load_group_data(msg.chat.id)
    gender = "پسر" if "پسر" in msg.text else "دختر"
    uid = str(msg.from_user.id)
    if uid not in data["users"]:
        data["users"][uid] = {}
    data["users"][uid]["gender"] = gender
    save_group_data(msg.chat.id, data)
    await msg.reply(f"جنسیت شما به عنوان {gender} ثبت شد ✅")
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("تعریف مشخصات"))
async def define_user_info(msg: types.Message):
    parts = msg.text.split()
    if len(parts) != 6:
        await msg.reply("فرمت صحیح: تعریف مشخصات اسم سن قد شهر\nمثال: تعریف مشخصات علی 21 180 تهران")
        return
    _, _, name, age, height, city = parts
    if not name.isalpha() or not age.isdigit() or not height.isdigit() or not city.isalpha():
        await msg.reply("ورودی‌ها نامعتبر هستند. فقط از حروف برای اسم/شهر و از عدد برای سن/قد استفاده کنید.")
        return
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    if uid not in data["users"]:
        data["users"][uid] = {}
    data["users"][uid].update({"name": name, "age": int(age), "height": int(height), "city": city})
    save_group_data(msg.chat.id, data)
    await msg.reply("اطلاعات با موفقیت ثبت شد ✅")
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("ثبت تولد"))
async def birth_register(msg: types.Message):
    parts = msg.text.split()
    if len(parts) != 3:
        await msg.reply("فرمت صحیح: ثبت تولد روز/ماه/سال\nمثال: ثبت تولد 25/03/1382")
        return
    _, date_str = parts[0], parts[2] if len(parts) == 3 else parts[1]
    if not all(x.isdigit() for x in date_str.split("/")):
        await msg.reply("فرمت نادرست است. مثال: ثبت تولد 25/03/1382")
        return
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    data["users"].setdefault(uid, {})["birthday"] = date_str
    save_group_data(msg.chat.id, data)
    await msg.reply("تاریخ تولد ثبت شد ✅")
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("شیپر من کیم"))
async def whoami(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    user = data["users"].get(uid)
    if not user:
        await msg.reply("شما هنوز هیچ اطلاعاتی ثبت نکردید.")
        return

    info = "📋 مشخصات شما:\n"
    info += f"👤 اسم: {user.get('name', '-')}\n"
    info += f"🎂 سن: {user.get('age', '-')}\n"
    info += f"📏 قد: {user.get('height', '-')}\n"
    info += f"🏙 شهر: {user.get('city', '-')}\n"
    info += f"🚻 جنسیت: {user.get('gender', '-')}\n"
    info += f"📆 تولد: {user.get('birthday', '-')}\n"
    info += f"❤️ رل: {user.get('partner', '-')}\n"
    info += f"💔 اکس: {user.get('ex', '-')}\n"
    crushes = data.get("crushes", {}).get(uid, [])
    info += f"💘 کراش‌ها: {len(crushes)} نفر"

    await msg.reply(info)
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("ثبت کراش"))
async def add_crush(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)

    target = None
    if msg.reply_to_message:
        target = msg.reply_to_message.from_user.id
    else:
        parts = msg.text.split()
        if len(parts) == 3:
            try:
                target = int(parts[2].replace("@", "").replace(" ", ""))
            except:
                pass
    if not target or str(target) == uid:
        await msg.reply("آیدی کراش معتبر نیست یا نمی‌تونید خودتون رو کراش کنید!")
        return

    data.setdefault("crushes", {}).setdefault(uid, [])
    if str(target) not in data["crushes"][uid]:
        data["crushes"][uid].append(str(target))
        save_group_data(msg.chat.id, data)
        await msg.reply("کراش با موفقیت اضافه شد! 💘")
    else:
        await msg.reply("این شخص از قبل تو لیست کراش‌هات بود!")

@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("حذف کراش"))
async def remove_crush(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    crushes = data.setdefault("crushes", {}).get(uid, [])

    target = None
    if msg.reply_to_message:
        target = msg.reply_to_message.from_user.id
    else:
        parts = msg.text.split()
        if len(parts) == 3:
            try:
                target = int(parts[2].replace("@", ""))
            except:
                pass

    if str(target) in crushes:
        crushes.remove(str(target))
        save_group_data(msg.chat.id, data)
        await msg.reply("کراش حذف شد ✅")
    else:
        await msg.reply("این کاربر در لیست کراش‌های شما نیست.")
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("لیست کراش"))
async def list_crushes(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    crush_ids = data.get("crushes", {}).get(uid, [])
    if not crush_ids:
        await msg.reply("شما هنوز هیچ کراشی ثبت نکردید.")
        return

    text = "💘 لیست کراش‌های شما:\n"
    for cid in crush_ids:
        try:
            user = await bot.get_chat(cid)
            text += f"• {user.full_name} (@{user.username or 'ندارد'})\n"
        except:
            text += f"• {cid}\n"
    await msg.reply(text)
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("شیپم کن"))
async def do_ship(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    user_gender = data["users"].get(uid, {}).get("gender")

    crush_ids = data.get("crushes", {}).get(uid, [])

    candidates = []
    if crush_ids:
        candidates = crush_ids
        method = "با کراش شما"
    else:
        for u, info in data["users"].items():
            if u != uid and info.get("gender") != user_gender:
                candidates.append(u)
        method = "با فردی از جنس مخالف"

    if not candidates:
        await msg.reply("هیچ کسی برای شیپ شدن پیدا نشد!")
        return

    partner_id = random.choice(candidates)
    try:
        user2 = await bot.get_chat(partner_id)
        await msg.reply(f"❤️ شیپ شدید با {user2.full_name} (@{user2.username or 'ندارد'})\n({method})")
    except:
        await msg.reply("خطا در دسترسی به کاربر مقابل.")
# افزودن کراش با ریپلای یا شناسه
@dp.message_handler(lambda m: m.chat.type != "private" and m.reply_to_message and "ثبت کراش" in m.text.lower())
async def register_crush_reply(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    crush_id = str(msg.reply_to_message.from_user.id)
    if uid == crush_id:
        await msg.reply("نمیشه خودتو کراش بزنی 😅")
        return
    data["crushes"].setdefault(uid, [])
    if crush_id not in data["crushes"][uid]:
        data["crushes"][uid].append(crush_id)
        save_group_data(msg.chat.id, data)
        await msg.reply("کراش ثبت شد 💘")
    else:
        await msg.reply("قبلاً این شخص رو کراش کردی!")

# حذف کراش با ریپلای یا آیدی
@dp.message_handler(lambda m: m.chat.type != "private" and ("حذف کراش" in m.text.lower() or "شیپر کات" in m.text.lower()))
async def remove_crush(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    crush_id = None

    if msg.reply_to_message:
        crush_id = str(msg.reply_to_message.from_user.id)
    else:
        parts = msg.text.split()
        if len(parts) == 3 and parts[2].isdigit():
            crush_id = parts[2]
        elif len(parts) == 3 and parts[2].startswith("@"):
            try:
                user = await bot.get_chat(parts[2])
                crush_id = str(user.id)
            except:
                await msg.reply("یوزرنیم اشتباه است.")
                return

    if not crush_id:
        await msg.reply("فرمت صحیح: حذف کراش [ریپلای] یا شیپر کات [ریپلای/یوزرنیم/آیدی]")
        return

    if crush_id in data.get("crushes", {}).get(uid, []):
        data["crushes"][uid].remove(crush_id)
        save_group_data(msg.chat.id, data)
        await msg.reply("کراش حذف شد ❌")
    else:
        await msg.reply("این فرد جزو کراش‌های شما نیست.")

# نمایش لیست کراش‌ها
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower() == "لیست کراش ها")
async def list_crushes(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    crush_ids = data.get("crushes", {}).get(uid, [])
    if not crush_ids:
        await msg.reply("شما کراشی ثبت نکردید!")
        return
    crush_list = []
    for cid in crush_ids:
        try:
            user = await bot.get_chat(cid)
            crush_list.append(f"- {user.full_name} ({cid})")
        except:
            crush_list.append(f"- کاربر حذف‌شده ({cid})")
    await msg.reply("💘 لیست کراش‌های شما:\n" + "\n".join(crush_list))
# دستور "شیپم کن" → شیپ با یکی از کراش‌ها یا فرد تصادفی از جنس مخالف
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("شیپم کن"))
async def ship_user(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    user = data["users"].get(uid, {})
    gender = user.get("gender")
    if not gender:
        await msg.reply("اول جنسیتت رو ثبت کن با 'من پسرم' یا 'من دخترم'")
        return

    # سعی در شیپ با کراش
    crush_ids = data.get("crushes", {}).get(uid, [])
    target_id = None
    if crush_ids:
        target_id = random.choice(crush_ids)
    else:
        # پیدا کردن فرد تصادفی از جنس مخالف
        opposite = "دختر" if gender == "پسر" else "پسر"
        pool = [uid2 for uid2, info in data["users"].items() if info.get("gender") == opposite and uid2 != uid]
        if pool:
            target_id = random.choice(pool)

    if not target_id:
        await msg.reply("کسی برای شیپ پیدا نشد 😔")
        return

    # ذخیره کاپل
    couple = {"a": uid, "b": target_id, "date": datetime.now().strftime("%Y-%m-%d")}
    data.setdefault("couples", []).append(couple)
    save_group_data(msg.chat.id, data)

    user1 = await bot.get_chat(int(uid))
    user2 = await bot.get_chat(int(target_id))
    await msg.reply(f"💞 {user1.full_name} و {user2.full_name} با هم شیپ شدن!\nمبارکه! 🎉")

# دستور ثبت سینگل – "من سینگلم شیپر"
@dp.message_handler(lambda m: m.chat.type != "private" and "من سینگلم شیپر" in m.text.lower())
async def set_single(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    user = data["users"].setdefault(uid, {})
    user["relationship"] = "سینگل"
    save_group_data(msg.chat.id, data)
    await msg.reply("وضعیت شما به عنوان سینگل ثبت شد ✅")

# دستور ثبت رل – "من رلم شیپر"
@dp.message_handler(lambda m: m.chat.type != "private" and "من رلم شیپر" in m.text.lower())
async def set_relationship(msg: types.Message):
    parts = msg.text.split()
    if len(parts) < 5:
        await msg.reply("فرمت: من رلم شیپر @username یا آیدی عددی")
        return
    partner_id = parts[4]
    try:
        if partner_id.startswith("@"):
            user = await bot.get_chat(partner_id)
            partner_id = str(user.id)
        elif partner_id.isdigit():
            partner_id = str(partner_id)
        else:
            raise ValueError
    except:
        await msg.reply("آیدی یا یوزرنیم معتبر نیست.")
        return

    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    if uid == partner_id:
        await msg.reply("با خودت نمیشه رل زد! 😅")
        return

    data["users"].setdefault(uid, {})["relationship"] = f"با {partner_id}"
    save_group_data(msg.chat.id, data)
    await msg.reply("رابطه با موفقیت ثبت شد 💖")

# دستور ثبت پارتنر – "ثبت پارتنر @username"
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("ثبت پارتنر"))
async def register_partner(msg: types.Message):
    parts = msg.text.split()
    if len(parts) != 3:
        await msg.reply("فرمت صحیح: ثبت پارتنر @username")
        return
    try:
        user = await bot.get_chat(parts[2])
        partner_id = str(user.id)
    except:
        await msg.reply("یوزرنیم نامعتبر است.")
        return

    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    data["users"].setdefault(uid, {})["partner"] = partner_id
    save_group_data(msg.chat.id, data)
    await msg.reply("پارتنر ثبت شد ✅")

# دستور ثبت اکس – "ثبت اکس @username"
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("ثبت اکس"))
async def register_ex(msg: types.Message):
    parts = msg.text.split()
    if len(parts) != 3:
        await msg.reply("فرمت صحیح: ثبت اکس @username")
        return
    try:
        user = await bot.get_chat(parts[2])
        ex_id = str(user.id)
    except:
        await msg.reply("یوزرنیم نامعتبر است.")
        return

    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    data["users"].setdefault(uid, {}).setdefault("ex_list", []).append(ex_id)
    save_group_data(msg.chat.id, data)
    await msg.reply("اکس ثبت شد ❌💔")

# ارسال تبریک ماهگرد شیپ‌ها
async def check_month_anniversaries():
    for file in os.listdir(DATA_FOLDER):
        if file.startswith("group_") and file.endswith(".json"):
            chat_id = int(file.split("_")[1].split(".")[0])
            data = load_group_data(chat_id)
            for c in data.get("couples", []):
                try:
                    start_date = datetime.strptime(c["date"], "%Y-%m-%d")
                    now = datetime.now()
                    months = (now.year - start_date.year) * 12 + now.month - start_date.month
                    if start_date.day == now.day and months > 0:
                        a = await bot.get_chat(int(c["a"]))
                        b = await bot.get_chat(int(c["b"]))
                        await bot.send_message(chat_id, f"🎉 ماهگرد {months} ام {a.full_name} و {b.full_name} مبارک!")
                except:
                    continue

# اجرای خودکار ماهگردها هر روز (در فریم‌ورک‌های کامل میشه زمان‌بندی کرد)
# چک نصب بودن ربات در گروه
def check_installed(chat_id):
    data = load_group_data(chat_id)
    return data.get("installed", False)

# دستور "شیپر نصب" – فعال‌سازی شیپر برای گروه
@dp.message_handler(lambda m: m.chat.type != "private" and "شیپر نصب" in m.text.lower())
async def install_shiper(msg: types.Message):
    data = load_group_data(msg.chat.id)
    if data["installed"]:
        await msg.reply("ربات قبلاً در این گروه نصب شده ✅")
        return
    data["installed"] = True
    data["owner_id"] = msg.from_user.id
    data["expiration"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    save_group_data(msg.chat.id, data)
    await msg.reply("ربات با موفقیت برای این گروه فعال شد ✅\n۷ روز تست رایگان آغاز شد.")

# دستور "شیپر لغو نصب" – حذف نصب شیپر
@dp.message_handler(lambda m: m.chat.type != "private" and "شیپر لغو نصب" in m.text.lower())
async def uninstall_shiper(msg: types.Message):
    data = load_group_data(msg.chat.id)
    if msg.from_user.id != data.get("owner_id"):
        await msg.reply("فقط مالک گروه می‌تونه ربات رو لغو نصب کنه ❌")
        return
    data["installed"] = False
    save_group_data(msg.chat.id, data)
    await msg.reply("ربات برای این گروه غیرفعال شد ❌")

# دستور "شیپر خروج" – خروج ربات از گروه
@dp.message_handler(lambda m: m.chat.type != "private" and "شیپر خروج" in m.text.lower())
async def leave_group(msg: types.Message):
    await msg.reply("بدرود! 👋")
    await bot.leave_chat(msg.chat.id)

# دستور "تنظیم اجبار @channelusername"
@dp.message_handler(lambda m: m.chat.type != "private" and m.text.lower().startswith("تنظیم اجبار"))
async def set_mandatory_channel(msg: types.Message):
    parts = msg.text.split()
    if len(parts) != 3:
        await msg.reply("فرمت صحیح: تنظیم اجبار @channelusername")
        return
    data = load_group_data(msg.chat.id)
    if msg.from_user.id != data.get("owner_id"):
        await msg.reply("فقط مالک گروه می‌تونه اجبار رو تنظیم کنه ❌")
        return
    channel = parts[2]
    data.setdefault("settings", {})["mandatory_channel"] = channel
    save_group_data(msg.chat.id, data)
    await msg.reply(f"عضویت اجباری در {channel} تنظیم شد ✅")

# دستور "شیپر فروشنده" – افزودن فروشنده
@dp.message_handler(lambda m: m.chat.type != "private" and "شیپر فروشنده" in m.text.lower())
async def add_seller(msg: types.Message):
    if not msg.reply_to_message:
        await msg.reply("برای افزودن فروشنده باید روی پیامش ریپلای کنید.")
        return
    uid = str(msg.reply_to_message.from_user.id)
    data = load_group_data(msg.chat.id)
    data.setdefault("settings", {}).setdefault("sellers", []).append(uid)
    save_group_data(msg.chat.id, data)
    await msg.reply("فروشنده اضافه شد ✅")

# دستور "حذف شیپر فروشنده"
@dp.message_handler(lambda m: m.chat.type != "private" and "حذف شیپر فروشنده" in m.text.lower())
async def remove_seller(msg: types.Message):
    if not msg.reply_to_message:
        await msg.reply("برای حذف فروشنده باید روی پیامش ریپلای کنید.")
        return
    uid = str(msg.reply_to_message.from_user.id)
    data = load_group_data(msg.chat.id)
    if uid in data.get("settings", {}).get("sellers", []):
        data["settings"]["sellers"].remove(uid)
        save_group_data(msg.chat.id, data)
        await msg.reply("فروشنده حذف شد ❌")

# هشدار ۲ روز مانده به پایان تست
async def notify_expiring_groups():
    now = datetime.now().date()
    for file in os.listdir(DATA_FOLDER):
        if not file.startswith("group_"): continue
        path = os.path.join(DATA_FOLDER, file)
        data = load_group_data(int(file.split("_")[1].split(".")[0]))
        expiration = datetime.strptime(data.get("expiration"), "%Y-%m-%d").date()
        if expiration - now == timedelta(days=2):
            owner_id = data.get("owner_id")
            if owner_id:
                try:
                    await bot.send_message(int(file.split("_")[1].split(".")[0]), f"⏳ فقط ۲ روز تا پایان اعتبار تست باقی مانده!\nلطفاً با @{ADMIN_USERNAME} تماس بگیرید.")
                except:
                    continue
# دستور "لیست کراش‌ها"
@dp.message_handler(lambda m: m.chat.type != "private" and "لیست کراش" in m.text.lower())
async def crush_list(msg: types.Message):
    data = load_group_data(msg.chat.id)
    uid = str(msg.from_user.id)
    crushes = data.get("crushes", {}).get(uid, [])
    if not crushes:
        await msg.reply("لیست کراش شما خالیه 💔")
        return
    txt = "💘 کراش‌های شما:\n" + "\n".join(crushes)
    await msg.reply(txt)

# دستور "لیست مدیران"
@dp.message_handler(lambda m: m.chat.type != "private" and "لیست مدیران" in m.text.lower())
async def admin_list(msg: types.Message):
    data = load_group_data(msg.chat.id)
    admins = data.get("settings", {}).get("admins", [])
    if not admins:
        await msg.reply("هنوز مدیری ثبت نشده.")
        return
    names = []
    for uid in admins:
        try:
            user = await bot.get_chat_member(msg.chat.id, int(uid))
            names.append(f"{user.user.full_name} (@{user.user.username})")
        except:
            continue
    await msg.reply("👮‍♂️ مدیران شیپر:\n" + "\n".join(names))

# دستور "لیست کاپل‌ها"
@dp.message_handler(lambda m: m.chat.type != "private" and "لیست کاپل" in m.text.lower())
async def couple_list(msg: types.Message):
    data = load_group_data(msg.chat.id)
    couples = data.get("settings", {}).get("couples", [])
    if not couples:
        await msg.reply("💔 هنوز کاپلی ثبت نشده.")
        return
    txt = "💑 لیست کاپل‌ها:\n"
    for c in couples:
        txt += f"{c['user1']} ❤️ {c['user2']} – از {c['since']}\n"
    await msg.reply(txt)

# واسطه‌گری درخواست رل با دکمه بله/نه
@dp.message_handler(lambda m: m.chat.type != "private" and "شیپر بهش بگو" in m.text.lower() and msg.reply_to_message)
async def propose_request(msg: types.Message):
    partner = msg.reply_to_message.from_user
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("💍 با اجازه بزرگترا بله", callback_data=f"accept_{msg.from_user.id}"),
        InlineKeyboardButton("❌ متاسفم نه", callback_data=f"reject_{msg.from_user.id}")
    )
    await msg.reply_to_message.reply(f"{partner.first_name} آیا بنده وکیلم؟", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("accept_") or c.data.startswith("reject_"))
async def proposal_response(callback: types.CallbackQuery):
    data = load_group_data(callback.message.chat.id)
    from_uid = callback.from_user.id
    target_uid = int(callback.data.split("_")[1])
    if callback.data.startswith("accept"):
        await callback.message.edit_text("💖 بله گفته شد! تبریک می‌گم به این دو عاشق!")
        # اینجا می‌تونید اطلاعات رل ثبت کنید
    else:
        await callback.message.edit_text("🫤 درخواست رد شد... ولش کن شانس آوردی قیافه نداشت!")

    await callback.answer()

# پاک‌سازی پیام‌های موقت پس از پاسخ
@dp.message_handler(lambda m: m.chat.type != "private" and "پاکسازی پیام" in m.text.lower())
async def cleanup_msgs(msg: types.Message):
    await msg.delete()
