"""
QADAR.UZ — Premium Matchmaking Bot
6 узлов: Префрейминг → Юр.фильтр → Анкета (14 шагов) → Оплата → KYC → Финализация
"""

import logging
import sqlite3
import json
import urllib.request
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)

BOT_TOKEN  = "8484568968:AAFuQR4xrOueBt_qR0ZjBcFLnRcTQZCo9tI"
ADMIN_ID   = 1995391
SHEET_URL  = "https://script.google.com/macros/s/AKfycbxrEjGQFvlC-mJ0Ri7mnF5_91lmccTBVLWYsBh0cPZKiDroj0uCkcCZanCUSZXm1hS4/exec"

(
    RULES, LEGAL,
    Q_FIO, Q_AGE, Q_NATION, Q_CITY, Q_PROPISKA,
    Q_LIVING, Q_FAMILY, Q_EDU, Q_WORK,
    Q_CAR, Q_FINANCE, Q_ABOUT, Q_LOOKING, Q_CONTACT,
    PAY_WAIT,
    KYC_PASSPORT, KYC_DIPLOMA, KYC_MED, KYC_VIDEO
) = range(21)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('qadar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE, username TEXT,
        side TEXT, fio TEXT, age TEXT, nationality TEXT,
        city TEXT, propiska TEXT, living TEXT, family TEXT,
        education TEXT, work TEXT, car TEXT, finance TEXT,
        about TEXT, looking TEXT, contact TEXT,
        status TEXT DEFAULT 'new', created_at TEXT, paid_at TEXT,
        passport_file TEXT, diploma_file TEXT, med_file TEXT, video_file TEXT
    )''')
    conn.commit(); conn.close()

def db_insert(tid, uname):
    conn = sqlite3.connect('qadar.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO clients (telegram_id,username,status,created_at) VALUES (?,?,?,?)',
              (tid, uname, 'new', datetime.now().isoformat()))
    conn.commit(); conn.close()

def db_update(tid, **kw):
    conn = sqlite3.connect('qadar.db')
    c = conn.cursor()
    fields = ', '.join(f"{k}=?" for k in kw)
    c.execute(f"UPDATE clients SET {fields} WHERE telegram_id=?", list(kw.values())+[tid])
    conn.commit(); conn.close()

def is_girl(ctx):
    return 'девушки' in ctx.user_data.get('side', '')

def total_steps(ctx):
    return 13 if is_girl(ctx) else 14

# УЗЕЛ 1: /start
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_insert(user.id, user.username or '')
    text = (
        "🏛 *QADAR — Закрытый клуб по устройству судьбы*\n\n"
        "Добро пожаловать.\n\n"
        "QADAR — институт доверия для интеллигентных семей Узбекистана.\n\n"
        "*Наши принципы:*\n"
        "◆ Первая встреча — только на нейтральной территории\n"
        "◆ Открытой базы кандидатов не существует\n"
        "◆ Каждый участник проходит личную верификацию\n"
        "◆ Конфиденциальность защищена соглашением NDA\n\n"
        "_Для продолжения ознакомьтесь с правилами клуба._"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("📋 Ознакомиться с правилами", callback_data="show_rules")]])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    return RULES

# УЗЕЛ 2: Юридический фильтр
async def show_rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    text = (
        "📜 *Условия членства в клубе QADAR*\n\n"
        "1️⃣ <b>KYC-верификация</b> — вы обязуетесь предоставить подлинные документы: "
        "паспорт, диплом, медицинские справки.\n\n"
        "2️⃣ <b>NDA</b> — данные других участников строго конфиденциальны. "
        "Распространение информации преследуется.\n\n"
        "3️⃣ <b>Публичная оферта</b> — регулирует порядок услуг и ответственность сторон.\n\n"
        "📎 <a href='https://telegra.ph/Publichnaya-oferta-QADARUZ-05-14'>Публичная оферта</a>\n"
        "📎 <a href='https://telegra.ph/Politika-konfidencialnosti-QADARUZ-05-14'>Политика конфиденциальности</a>\n\n"
        "<i>Нажимая «Принимаю», вы подтверждаете согласие со всеми условиями.</i>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Принимаю условия", callback_data="accept")],
        [InlineKeyboardButton("❌ Не согласен", callback_data="decline")]
    ])
    await q.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    return LEGAL

async def accept(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    db_update(q.from_user.id, status='accepted')
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("👩 Со стороны девушки", callback_data="side_girl")],
        [InlineKeyboardButton("👦 Со стороны парня", callback_data="side_boy")]
    ])
    await q.edit_message_text(
        "✅ *Условия приняты.*\n\n"
        "Приступаем к формированию досье.\n\n"
        "Вы подаёте заявку:",
        parse_mode="Markdown", reply_markup=kb
    )
    return RULES

async def set_side(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data['side'] = 'девушки' if q.data == 'side_girl' else 'парня'
    db_update(q.from_user.id, side=ctx.user_data['side'])
    t = total_steps(ctx)
    await q.edit_message_text(
        f"*Шаг 1 из {t}*\n\nУкажите полное имя кандидата (ФИО):",
        parse_mode="Markdown"
    )
    return Q_FIO

async def decline(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("Понимаем ваше решение. Если измените мнение — напишите /start.")
    return ConversationHandler.END

# УЗЕЛ 3: Анкета
async def q_fio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['fio'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(f"*Шаг 2 из {t}*\n\nВозраст кандидата:", parse_mode="Markdown")
    return Q_AGE

async def q_age(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['age'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(f"*Шаг 3 из {t}*\n\nНациональность:", parse_mode="Markdown")
    return Q_NATION

async def q_nation(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['nationality'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(
        f"*Шаг 4 из {t}*\n\nГород и район проживания:",
        parse_mode="Markdown"
    )
    return Q_CITY

async def q_city(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['city'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(
        f"*Шаг 5 из {t}*\n\nПрописка — где зарегистрирован(а)?\n"
        "_например: Ташкент, Юнусабадский район_",
        parse_mode="Markdown"
    )
    return Q_PROPISKA

async def q_propiska(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['propiska'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(
        f"*Шаг 6 из {t}*\n\nС кем проживает?\n"
        "_например: с родителями / отдельно / с родственниками_",
        parse_mode="Markdown"
    )
    return Q_LIVING

async def q_living(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['living'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(
        f"*Шаг 7 из {t}*\n\nСостав семьи:\n"
        "_сколько братьев/сестёр, каким по счёту является кандидат_\n"
        "_например: 3 брата, 1 сестра — он/она средний(яя)_",
        parse_mode="Markdown"
    )
    return Q_FAMILY

async def q_family(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['family'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(
        f"*Шаг 8 из {t}*\n\nОбразование:\n"
        "_университет, специальность, год окончания_",
        parse_mode="Markdown"
    )
    return Q_EDU

async def q_edu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['education'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(
        f"*Шаг 9 из {t}*\n\nМесто работы и должность:\n"
        "_если не работает — укажите причину_",
        parse_mode="Markdown"
    )
    return Q_WORK

async def q_work(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['work'] = update.message.text.strip()
    t = total_steps(ctx)
    if is_girl(ctx):
        await update.message.reply_text(
            f"*Шаг 10 из {t}*\n\nРасскажите о кандидате:\n"
            "_характер, религиозность, образ жизни, увлечения_",
            parse_mode="Markdown"
        )
        return Q_ABOUT
    else:
        await update.message.reply_text(
            f"*Шаг 10 из {t}*\n\nНаличие автомобиля:\n"
            "_есть/нет, если есть — укажите марку и год_",
            parse_mode="Markdown"
        )
        return Q_CAR

async def q_car(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['car'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(
        f"*Шаг 11 из {t}*\n\nФинансовое положение и жильё:\n"
        "_есть ли собственное жильё, общий уровень дохода_",
        parse_mode="Markdown"
    )
    return Q_FINANCE

async def q_finance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['finance'] = update.message.text.strip()
    t = total_steps(ctx)
    await update.message.reply_text(
        f"*Шаг 12 из {t}*\n\nРасскажите о кандидате:\n"
        "_характер, религиозность, образ жизни, увлечения_",
        parse_mode="Markdown"
    )
    return Q_ABOUT

async def q_about(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['about'] = update.message.text.strip()
    t = total_steps(ctx)
    step = 11 if is_girl(ctx) else 13
    await update.message.reply_text(
        f"*Шаг {step} из {t}*\n\nКого ищете?\n"
        "_возраст, образование, характер, важные критерии_",
        parse_mode="Markdown"
    )
    return Q_LOOKING

async def q_looking(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['looking'] = update.message.text.strip()
    t = total_steps(ctx)
    step = 12 if is_girl(ctx) else 14
    await update.message.reply_text(
        f"*Шаг {step} из {t}*\n\nКонтакт для связи:\n"
        "_номер телефона или Telegram — только для куратора, строго конфиденциально_",
        parse_mode="Markdown"
    )
    return Q_CONTACT

async def q_contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['contact'] = update.message.text.strip()
    user = update.effective_user
    d = ctx.user_data

    db_update(user.id,
        side=d.get('side',''), fio=d.get('fio',''), age=d.get('age',''),
        nationality=d.get('nationality',''), city=d.get('city',''),
        propiska=d.get('propiska',''), living=d.get('living',''),
        family=d.get('family',''), education=d.get('education',''),
        work=d.get('work',''), car=d.get('car','—'),
        finance=d.get('finance','—'), about=d.get('about',''),
        looking=d.get('looking',''), contact=d.get('contact',''),
        status='questionnaire_done'
    )

    girl = is_girl(ctx)
    summary = (
        f"📋 *Проверьте данные:*\n\n"
        f"👥 Заявка со стороны: {d.get('side','')}\n"
        f"👤 ФИО: {d.get('fio','')}\n"
        f"🎂 Возраст: {d.get('age','')}\n"
        f"🌍 Национальность: {d.get('nationality','')}\n"
        f"🏙 Город/район: {d.get('city','')}\n"
        f"📍 Прописка: {d.get('propiska','')}\n"
        f"🏠 Проживает: {d.get('living','')}\n"
        f"👨‍👩‍👧‍👦 Состав семьи: {d.get('family','')}\n"
        f"🎓 Образование: {d.get('education','')}\n"
        f"💼 Работа: {d.get('work','')}\n"
    )
    if not girl:
        summary += (
            f"🚗 Автомобиль: {d.get('car','—')}\n"
            f"💰 Финансы/жильё: {d.get('finance','—')}\n"
        )
    summary += (
        f"✨ О кандидате: {d.get('about','')}\n"
        f"🔍 Ищет: {d.get('looking','')}\n"
        f"📞 Контакт: {d.get('contact','')}\n"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Всё верно, продолжить", callback_data="go_pay")],
        [InlineKeyboardButton("✏️ Заполнить заново", callback_data="restart")]
    ])
    await update.message.reply_text(summary, parse_mode="Markdown", reply_markup=kb)
    return PAY_WAIT

# УЗЕЛ 4: Оплата
async def go_pay(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    text = (
        "🔐 *Входной аудит безопасности*\n\n"
        "Для перехода к верификации необходимо оплатить членство.\n\n"
        "*Тарифы (12 месяцев):*\n"
        "◆ Standard — $100 (~1 300 000 сум)\n"
        "◆ Premium — $200 (~2 600 000 сум)\n"
        "◆ Elite — $300 (~3 900 000 сум)\n\n"
        "🎊 *Суюнчи при свадьбе:* от $1 000 до $2 500\n\n"
        "_Для выбора тарифа и оплаты свяжитесь с куратором:_"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Написать куратору", url="https://t.me/qadar_curator")],
        [InlineKeyboardButton("✅ Я оплатил", callback_data="paid_manual")]
    ])
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    return PAY_WAIT

async def restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data.clear()
    await q.edit_message_text("Начинаем заново. Напишите /start")
    return ConversationHandler.END

async def paid_manual(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    user = q.from_user
    db_update(user.id, status='paid', paid_at=datetime.now().isoformat())
    d = ctx.user_data
    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"💳 *ЗАЯВКА НА ОПЛАТУ — QADAR*\n\n"
                f"👥 Сторона: {d.get('side','')}\n"
                f"👤 {d.get('fio','')} | 🎂 {d.get('age','')}\n"
                f"🌍 {d.get('nationality','')} | 🏙 {d.get('city','')}\n"
                f"💼 {d.get('work','')}\n"
                f"📱 @{user.username or user.id}\n\n"
                f"Подтвердите: /confirm {user.id}"
            ),
            parse_mode="Markdown"
        )
    except: pass
    await q.edit_message_text(
        "✅ *Заявка на оплату отправлена куратору.*\n\n"
        "Как только оплата будет подтверждена — вы получите доступ к загрузке документов.\n\n"
        "Ожидайте сообщения в течение нескольких часов.",
        parse_mode="Markdown"
    )
    return PAY_WAIT

async def admin_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text("Использование: /confirm <telegram_id>")
        return
    tid = int(parts[1])
    db_update(tid, status='paid', paid_at=datetime.now().isoformat())
    await ctx.bot.send_message(
        chat_id=tid,
        text=(
            "✅ *Оплата подтверждена.*\n\n"
            "📁 *Загрузка документов — Шаг 1*\n\n"
            "Отправьте *фотографию паспорта* кандидата\n"
            "_(разворот с фото — чёткое, без бликов)_"
        ),
        parse_mode="Markdown"
    )
    await update.message.reply_text(f"✅ Подтверждено для ID {tid}")

# УЗЕЛ 5: KYC
async def kyc_passport(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo and not update.message.document:
        await update.message.reply_text("⚠️ Отправьте *фотографию* паспорта.", parse_mode="Markdown")
        return KYC_PASSPORT
    fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
    ctx.user_data['passport_file'] = fid
    await update.message.reply_text(
        "✅ Паспорт получен.\n\n📁 *Шаг 2*\n\nОтправьте *фотографию диплома*:",
        parse_mode="Markdown"
    )
    return KYC_DIPLOMA

async def kyc_diploma(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo and not update.message.document:
        await update.message.reply_text("⚠️ Отправьте *фотографию* диплома.", parse_mode="Markdown")
        return KYC_DIPLOMA
    fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
    ctx.user_data['diploma_file'] = fid
    ctx.user_data['med_files'] = []

    if is_girl(ctx):
        med_text = (
            "✅ Диплом получен.\n\n📁 *Шаг 3*\n\n"
            "Отправьте *справку от психоневролога*.\n"
            "_По желанию: справка об отсутствии наследственных заболеваний._\n\n"
            "Когда всё загрузите — напишите *Готово*"
        )
    else:
        med_text = (
            "✅ Диплом получен.\n\n📁 *Шаг 3*\n\n"
            "Отправьте *медицинские справки:*\n"
            "◆ Нарко-диспансер\n"
            "◆ Психоневролог\n"
            "◆ Опционально: наследственные заболевания\n\n"
            "Можно несколько файлов. Когда всё загрузите — напишите *Готово*"
        )
    await update.message.reply_text(med_text, parse_mode="Markdown")
    return KYC_MED

async def kyc_med(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.photo or update.message.document:
        fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
        ctx.user_data.setdefault('med_files', []).append(fid)
        await update.message.reply_text("📎 Файл получен. Отправьте ещё или напишите *Готово*", parse_mode="Markdown")
        return KYC_MED
    if update.message.text and 'готово' in update.message.text.lower():
        if not ctx.user_data.get('med_files'):
            await update.message.reply_text("⚠️ Загрузите хотя бы одну справку.")
            return KYC_MED
        ctx.user_data['med_file'] = ','.join(ctx.user_data['med_files'])
        await update.message.reply_text(
            "✅ Справки получены.\n\n📁 *Шаг 4*\n\n"
            "Отправьте *видео-селфи* (кружок 🎥)\n"
            "_Скажите: «Я, [ФИО], подтверждаю подачу заявки в клуб QADAR»_",
            parse_mode="Markdown"
        )
        return KYC_VIDEO
    await update.message.reply_text("Отправьте файл или напишите *Готово*", parse_mode="Markdown")
    return KYC_MED

async def kyc_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.video and not update.message.video_note:
        await update.message.reply_text("⚠️ Отправьте *видео-сообщение* (кружок) или видеофайл.", parse_mode="Markdown")
        return KYC_VIDEO
    fid = update.message.video_note.file_id if update.message.video_note else update.message.video.file_id
    ctx.user_data['video_file'] = fid
    user = update.effective_user
    d = ctx.user_data

    db_update(user.id,
        passport_file=d.get('passport_file',''),
        diploma_file=d.get('diploma_file',''),
        med_file=d.get('med_file',''),
        video_file=fid,
        status='awaiting_interview'
    )

    girl = is_girl(ctx)
    try:
        admin_msg = (
            f"🔔 *ДОСЬЕ ГОТОВО — QADAR*\n\n"
            f"👥 Сторона: {d.get('side','')}\n"
            f"👤 {d.get('fio','')} | 🎂 {d.get('age','')} | 🌍 {d.get('nationality','')}\n"
            f"🏙 {d.get('city','')} | 📍 {d.get('propiska','')}\n"
            f"🏠 {d.get('living','')} | 👨‍👩‍👧‍👦 {d.get('family','')}\n"
            f"🎓 {d.get('education','')} | 💼 {d.get('work','')}\n"
        )
        if not girl:
            admin_msg += f"🚗 {d.get('car','—')} | 💰 {d.get('finance','—')}\n"
        admin_msg += (
            f"✨ {d.get('about','')}\n"
            f"🔍 {d.get('looking','')}\n"
            f"📞 {d.get('contact','')}\n"
            f"📱 @{user.username or 'нет'} (ID: {user.id})\n\n"
            f"Статус: awaiting_interview"
        )
        await ctx.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
    except: pass

    try:
        sheet_data = {
            'side': d.get('side',''), 'name': d.get('fio',''),
            'age': d.get('age',''), 'city': d.get('city',''),
            'education': d.get('education',''), 'profession': d.get('work',''),
            'about': d.get('about',''), 'looking_for': d.get('looking',''),
            'contact': d.get('contact',''), 'tariff': 'KYC Complete'
        }
        data = json.dumps(sheet_data).encode('utf-8')
        req = urllib.request.Request(SHEET_URL, data=data, headers={'Content-Type':'application/json'})
        urllib.request.urlopen(req, timeout=5)
    except: pass

    # УЗЕЛ 6: Финализация
    await update.message.reply_text(
        "🏛 *Досье сформировано и передано куратору.*\n\n"
        "Благодарим вас за доверие к клубу QADAR.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "*Что происходит далее:*\n\n"
        "1. Куратор изучит ваши документы\n"
        "2. В течение *24 часов* вы получите звонок для назначения видеоинтервью\n"
        "3. После интервью вы станете полноправным членом клуба\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "_Сохраняйте конфиденциальность. "
        "Разглашение данных клуба является нарушением NDA._\n\n"
        "С уважением,\n*Команда QADAR*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    ctx.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("Приостановлено. Для возобновления напишите /start.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            RULES: [
                CallbackQueryHandler(show_rules, pattern="show_rules"),
                CallbackQueryHandler(set_side, pattern="side_girl|side_boy")
            ],
            LEGAL: [
                CallbackQueryHandler(accept, pattern="accept"),
                CallbackQueryHandler(decline, pattern="decline")
            ],
            Q_FIO:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q_fio)],
            Q_AGE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q_age)],
            Q_NATION:   [MessageHandler(filters.TEXT & ~filters.COMMAND, q_nation)],
            Q_CITY:     [MessageHandler(filters.TEXT & ~filters.COMMAND, q_city)],
            Q_PROPISKA: [MessageHandler(filters.TEXT & ~filters.COMMAND, q_propiska)],
            Q_LIVING:   [MessageHandler(filters.TEXT & ~filters.COMMAND, q_living)],
            Q_FAMILY:   [MessageHandler(filters.TEXT & ~filters.COMMAND, q_family)],
            Q_EDU:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q_edu)],
            Q_WORK:     [MessageHandler(filters.TEXT & ~filters.COMMAND, q_work)],
            Q_CAR:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q_car)],
            Q_FINANCE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, q_finance)],
            Q_ABOUT:    [MessageHandler(filters.TEXT & ~filters.COMMAND, q_about)],
            Q_LOOKING:  [MessageHandler(filters.TEXT & ~filters.COMMAND, q_looking)],
            Q_CONTACT:  [MessageHandler(filters.TEXT & ~filters.COMMAND, q_contact)],
            PAY_WAIT: [
                CallbackQueryHandler(go_pay, pattern="go_pay"),
                CallbackQueryHandler(paid_manual, pattern="paid_manual"),
                CallbackQueryHandler(restart, pattern="restart")
            ],
            KYC_PASSPORT: [MessageHandler(filters.PHOTO | filters.Document.ALL, kyc_passport)],
            KYC_DIPLOMA:  [MessageHandler(filters.PHOTO | filters.Document.ALL, kyc_diploma)],
            KYC_MED:      [MessageHandler(filters.PHOTO | filters.Document.ALL | filters.TEXT, kyc_med)],
            KYC_VIDEO:    [MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, kyc_video)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("confirm", admin_confirm))
    print("✅ QADAR Premium Bot — запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
