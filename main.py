# main.py - نسخه حرفه‌ای کامل ربات شیپر گروهی (Railway Ready)
# امکانات: ثبت جنسیت، تایید دوطرفه رل، قطع رل، شیپ، آمار، پروفایل، پلن شارژی، عضویت اجباری، نماینده فروش، پنل ادمین، تبریک ماهگرد

[...کد بالا ثابت می‌ماند تا بخش on_startup...]

@dp.message_handler(commands=["rel"])
async def rel(m):
    args = m.get_args().replace("@", "").strip()
    if not args:
        await m.reply("آیدی پارتنرت رو وارد کن. مثال: /rel @user یا عدد")
        return
    d = load(); gid = ensure_group(d, m.chat); uid = str(m.from_user.id)
    target = None
    for k, v in d["groups"][gid]["users"].items():
        if k == args or v.get("username") == args:
            target = k
            break
    if not target:
        await m.reply("کاربر موردنظر ثبت‌نام نکرده.")
        return
    if uid == target:
        await m.reply("نمی‌تونی با خودت رل بزنی 😅")
        return
    d["groups"][gid]["pending"][target] = {"from": uid, "date": datetime.utcnow().isoformat()}
    save(d)
    uname = d["groups"][gid]["users"][uid]["name"]
    tname = d["groups"][gid]["users"][target]["name"]
    btn = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ تایید رابطه", callback_data=f"rel_yes_{gid}_{uid}_{target}"),
        InlineKeyboardButton("❌ رد", callback_data=f"rel_no_{gid}_{uid}_{target}")
    )
    await m.reply(f"📣 درخواست رل بین {mention(uid, uname)} و {mention(target, tname)}", reply_markup=btn)

@dp.callback_query_handler(lambda c: c.data.startswith("rel_yes_") or c.data.startswith("rel_no_"))
async def rel_confirm(c):
    _, gid, u1, u2 = c.data.split("_")[1:]
    d = load()
    if gid not in d["groups"]: return
    if c.data.startswith("rel_yes"):
        for u in [u1, u2]:
            d["groups"][gid]["users"][u]["status"] = "در رابطه"
            d["groups"][gid]["users"][u]["partner_id"] = u2 if u == u1 else u1
            d["groups"][gid]["users"][u]["relationship_started"] = datetime.utcnow().isoformat()
        d["groups"][gid]["pending"].pop(u2, None)
        save(d)
        await c.message.edit_text(f"🎉 رل تایید شد! {mention(u1, d['groups'][gid]['users'][u1]['name'])} ❤️ {mention(u2, d['groups'][gid]['users'][u2]['name'])}")
    else:
        d["groups"][gid]["pending"].pop(u2, None)
        save(d)
        await c.message.edit_text("❌ درخواست رل رد شد.")

@dp.message_handler(commands=["cut"])
async def cut(m):
    d = load(); gid = ensure_group(d, m.chat); uid = str(m.from_user.id)
    u = d["groups"][gid]["users"].get(uid); pid = u.get("partner_id") if u else None
    if not pid: return await m.reply("شما در رابطه نیستید.")
    for x in [uid, pid]:
        d["groups"][gid]["users"][x].update({"status": "سینگل", "partner_id": None, "relationship_started": None})
    save(d)
    await m.reply("❌ رابطه قطع شد.")

@dp.message_handler(commands=["profile"])
async def profile(m):
    d = load(); gid = ensure_group(d, m.chat); uid = str(m.from_user.id)
    u = d["groups"][gid]["users"].get(uid)
    if not u: return await m.reply("اول ثبت‌نام کن با /register")
    msg = f"👤 {u['name']}\nجنسیت: {u['gender']}\nوضعیت: {u['status']}"
    if u["partner_id"]:
        msg += f"\nپارتنر: {mention(u['partner_id'], d['groups'][gid]['users'][u['partner_id']]['name'])}"
    if u["relationship_started"]:
        dt = datetime.fromisoformat(u["relationship_started"]).date()
        msg += f"\nشروع رابطه: {dt}"
    await m.reply(msg)

@dp.message_handler(commands=["stats"])
async def stats(m):
    d = load(); gid = ensure_group(d, m.chat)
    us = d["groups"][gid]["users"]
    g = sum(1 for u in us.values() if u["gender"] == "دختر")
    b = sum(1 for u in us.values() if u["gender"] == "پسر")
    r = sum(1 for u in us.values() if u["status"] == "در رابطه") // 2
    await m.reply(f"👥 آمار گروه:
کل: {len(us)} | 👧 دختر: {g} | 👦 پسر: {b} | 💞 رل: {r}")

@dp.message_handler(commands=["ship"])
async def ship(m):
    d = load(); gid = ensure_group(d, m.chat)
    us = d["groups"][gid]["users"]
    girls = [k for k, v in us.items() if v["gender"] == "دختر" and v["status"] == "سینگل"]
    boys = [k for k, v in us.items() if v["gender"] == "پسر" and v["status"] == "سینگل"]
    if not girls or not boys: return await m.reply("افراد کافی برای شیپ نیستند.")
    from random import choice
    g = choice(girls); b = choice(boys)
    await m.reply(f"💘 شیپ امروز:
👧 {mention(g, us[g]['name'])} + 👦 {mention(b, us[b]['name'])}")

@scheduler.scheduled_job("cron", hour=22)
async def night_ship():
    d = load()
    for gid, g in d["groups"].items():
        if not g["active"]: continue
        us = g["users"]
        girls = [k for k, v in us.items() if v["gender"] == "دختر" and v["status"] == "سینگل"]
        boys = [k for k, v in us.items() if v["gender"] == "پسر" and v["status"] == "سینگل"]
        if girls and boys:
            g1, b1 = choice(girls), choice(boys)
            await bot.send_message(int(gid), f"💘 شیپ شب:
👧 {mention(g1, us[g1]['name'])} + 👦 {mention(b1, us[b1]['name'])}")

@scheduler.scheduled_job("cron", hour=9)
async def anniversaries():
    d = load()
    for gid, g in d["groups"].items():
        us = g["users"]
        for uid, u in us.items():
            pid = u.get("partner_id")
            if u["status"] == "در رابطه" and pid and uid < pid:
                start = datetime.fromisoformat(u["relationship_started"]).date()
                today = datetime.utcnow().date()
                if start.day == today.day:
                    delta = (today.year - start.year) * 12 + (today.month - start.month)
                    if delta > 0:
                        await bot.send_message(int(gid), f"🎊 تبریک به {mention(uid, u['name'])} و {mention(pid, us[pid]['name'])} برای ماهگرد {delta} 💞")

@dp.message_handler(commands=["reseller"])
async def reseller_panel(m):
    d = load(); uid = str(m.from_user.id)
    if uid not in d["resellers"]:
        return await m.reply("⛔ شما نماینده فروش نیستید.")
    groups = d["resellers"][uid].get("groups_managed", [])
    await m.reply(f"🧑‍💼 پنل نماینده فروش:
گروه‌های شارژشده: {len(groups)}
{chr(10).join(groups)}")

@dp.message_handler(commands=["addreseller"])
async def add_reseller(m):
    if m.from_user.id != OWNER_ID: return
    args = m.get_args()
    d = load(); d["resellers"][args] = {"groups_managed": []}; save(d)
    await m.reply("✅ نماینده اضافه شد.")

@dp.message_handler(commands=["extend"])
async def extend_group(m):
    if m.from_user.id != OWNER_ID: return
    args = m.get_args().split()
    gid, days = args[0], int(args[1])
    d = load(); g = d["groups"].get(gid)
    if not g: return await m.reply("گروه پیدا نشد.")
    g["expire_at"] = (datetime.utcnow() + timedelta(days=days)).isoformat()
    g["active"] = True
    save(d)
    await m.reply(f"✅ گروه {gid} تمدید شد تا {g['expire_at']}")
