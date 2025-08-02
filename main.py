# main.py (نسخه نهایی ربات شیپر)
# شامل تمام قابلیت‌ها و دستورات توافق‌شده
# کدنویسی بر اساس aiogram 3 و کاملاً ایزوله برای گروه‌ها

import os
import asyncio
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode, ChatType
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# مسیر ذخیره دیتای گروه‌ها
DATA_DIR = "group_data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_group_file(group_id):
    return os.path.join(DATA_DIR, f"{group_id}.json")

def load_data(group_id):
    path = get_group_file(group_id)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(group_id, data):
    with open(get_group_file(group_id), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ارسال پیام خوش‌آمد و دکمه‌ها در استارت
@router.message(CommandStart(), F.chat.type == ChatType.GROUP)
async def start_group(msg: Message):
    buttons = [
        [InlineKeyboardButton(text="📚 راهنما", callback_data="help")],
        [InlineKeyboardButton(text="📞 تماس با مالک", url="https://t.me/oldkaseb")],
        [InlineKeyboardButton(text="➕ افزودن ربات با تست رایگان", url="https://t.me/{}/?startgroup=true".format((await bot.me()).username))]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await msg.reply(
        "🎉 به ربات شیپر خوش آمدید!\nمدت تست: ۷ روز رایگان\n💸 شارژ ماهانه: ۵۰ هزار تومان",
        reply_markup=markup
    )
    # ذخیره شروع برای شارژ تست
    group_id = str(msg.chat.id)
    data = load_data(group_id)
    if 'started_at' not in data:
        data['started_at'] = datetime.now().isoformat()
        data['owner_id'] = msg.from_user.id
        data['active'] = True
        save_data(group_id, data)

# جلوگیری از پاسخ به پیام‌های غیر از گروه و فقط دستورات خاص
@router.message(F.chat.type != ChatType.GROUP)
async def ignore_private(msg: Message):
    await msg.answer("این ربات فقط در گروه‌ها قابل استفاده است.")

@router.message(F.text)
async def handle_keywords(msg: Message):
    if msg.chat.type != ChatType.GROUP:
        return

    txt = msg.text.strip().lower()
    group_id = str(msg.chat.id)
    data = load_data(group_id)
    user_id = str(msg.from_user.id)
    username = msg.from_user.username or msg.from_user.full_name

    # بررسی فعال بودن گروه
    if not data.get('active', False):
        return

    # شیپر = پاسخ ابتدایی و درخواست آیدی
    if txt == "شیپر":
        await msg.reply("جانم کیو بگیرم برات؟ آیدی بده")

    # من دخترم / من پسرم
    if txt == "من دخترم":
        data.setdefault('users', {})[user_id] = {"gender": "girl"}
        save_data(group_id, data)
        await msg.reply("ثبت شد. خوش اومدی دختر شیپری ❤️")
    if txt == "من پسرم":
        data.setdefault('users', {})[user_id] = {"gender": "boy"}
        save_data(group_id, data)
        await msg.reply("ثبت شد. خوش اومدی پسر شیپری 💙")

    # تعریف مشخصات
    if txt.startswith("تعریف"):
        # تعریف اسم=حامد سن=22 قد=180 شهر=تهران
        parts = dict(part.split("=") for part in txt.replace("تعریف", "").split() if "=" in part)
        if not parts:
            await msg.reply("فرمت تعریف: تعریف اسم=حامد سن=22 قد=180 شهر=تهران")
            return
        user = data.setdefault('users', {}).setdefault(user_id, {})
        user.update({k: v for k, v in parts.items() if k in ['اسم','سن','قد','شهر']})
        save_data(group_id, data)
        await msg.reply("✅ مشخصاتت ثبت شد")

    # ثبت تولد
    if txt.startswith("ثبت تولد"):
        # ثبت تولد 01/05/1380
        try:
            parts = txt.replace("ثبت تولد", "").strip()
            day, month, year = map(int, parts.split("/"))
            user = data.setdefault('users', {}).setdefault(user_id, {})
            user['birthday'] = f"{day:02}/{month:02}/{year}"
            save_data(group_id, data)
            await msg.reply(f"🎂 تولدت {user['birthday']} ثبت شد")
        except:
            await msg.reply("❌ فرمت صحیح: ثبت تولد 01/01/1380")

    # دستور آیدی شیپر
    if txt == "آیدی شیپر":
        user = data.get('users', {}).get(user_id, {})
        res = f"👤 اطلاعات شما:\n"
        res += f"👨‍💼 اسم: {user.get('اسم', 'تعریف نشده')}\n"
        res += f"🎂 تولد: {user.get('birthday', 'تعریف نشده')}\n"
        res += f"📏 قد: {user.get('قد', 'تعریف نشده')}\n"
        res += f"🏙️ شهر: {user.get('شهر', 'تعریف نشده')}\n"
        res += f"❤️ وضعیت: {user.get('status', 'نامشخص')}\n"
        await msg.reply(res)

# راه‌اندازی ربات
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
