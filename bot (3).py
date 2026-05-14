"""
QADAR.UZ — Premium Matchmaking Bot
6 узлов: Префрейминг → Юр.фильтр → Анкета → Оплата → KYC → Финализация
"""

import logging
import sqlite3
import json
import urllib.request
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, PreCheckoutQueryHandler, filters, ContextTypes
)

BOT_TOKEN  = "8484568968:AAFuQR4xrOueBt_qR0ZjBcFLnRcTQZCo9tI"
ADMIN_ID   = 1995391
SHEET_URL  = "https://script.google.com/macros/s/AKfycbxrEjGQFvlC-mJ0Ri7mnF5_91lmccTBVLWYsBh0cPZKiDroj0uCkcCZanCUSZXm1hS4/exec"

(RULES, LEGAL, Q_FIO, Q_AGE, Q_CITY, Q_EDU,
 PAY_WAIT, KYC_PASSPORT, KYC_DIPLOMA, KYC_MED, KYC_VIDEO) = range(11)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('qadar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE, username TEXT,
        fio TEXT, age TEXT, city TEXT, education TEXT,
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

def db_get(tid):
    conn = sqlite3.connect('qadar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM clients WHERE telegram_id=?", (tid,))
    row = c.fetchone(); conn.close(); return row

# УЗЕЛ 1: /start
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_insert(user.id, user.username or '')
    text = (
        "🏛 *QADAR — Закрытый клуб по устройству судьбы*\n\n"
        "Добро пожаловать.\n\n"
        "Мы не являемся сайтом знакомств или агентством. "
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
        "паспорт, диплом, медицинские справки (нарко-, психо-, СПИД).\n\n"
        "2️⃣ <b>NDA</b> — данные других участников строго конфиденциальны. "
        "Распространение информации преследуется.\n\n"
        "3️⃣ <b>Публичная оферта</b> — регулирует порядок услуг и ответственность сторон.\n\n"
        "📎 <a href='https://qadar.uz/oferta'>Публичная оферта</a>\n"
        "📎 <a href='https://qadar.uz/privacy'>Политика конфиденциальности</a>\n\n"
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
    await q.edit_message_text(
        "✅ *Условия приняты.*\n\n"
        "Приступаем к формированию вашего досье.\n\n"
        "*Шаг 1 из 4*\n\nУкажите ваше полное имя (ФИО):",
        parse_mode="Markdown"
    )
    return Q_FIO

async def decline(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text("Понимаем ваше решение. Если измените мнение — напишите /start.")
    return ConversationHandler.END

# УЗЕЛ 3: Анкета
async def get_fio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['fio'] = update.message.text.strip()
    await update.message.reply_text("*Шаг 2 из 4*\n\nУкажите ваш возраст:", parse_mode="Markdown")
    return Q_AGE

async def get_age(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['age'] = update.message.text.strip()
    await update.message.reply_text("*Шаг 3 из 4*\n\nВ каком городе вы проживаете?", parse_mode="Markdown")
    return Q_CITY

async def get_city(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['city'] = update.message.text.strip()
    await update.message.reply_text(
        "*Шаг 4 из 4*\n\nУкажите образование и сферу деятельности:\n"
        "_(например: ТГЮУ, юрист / собственный бизнес — импорт)_",
        parse_mode="Markdown"
    )
    return Q_EDU

async def get_edu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['education'] = update.message.text.strip()
    user = update.effective_user; d = ctx.user_data
    db_update(user.id, fio=d['fio'], age=d['age'], city=d['city'],
              education=d['education'], status='questionnaire_done')
    text = (
        f"📋 *Ваши данные:*\n\n"
        f"👤 {d['fio']}\n🎂 {d['age']}\n🏙 {d['city']}\n🎓 {d['education']}\n\n"
        "_Данные сохранены. Переходим к следующему этапу._"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Продолжить к оплате", callback_data="go_pay")]])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    return PAY_WAIT

# УЗЕЛ 4: Оплата
async def go_pay(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    text = (
        "🔐 *Входной аудит безопасности*\n\n"
        "Для перехода к верификации необходимо оплатить *Аудит безопасности*.\n\n"
        "*Что входит:*\n"
        "◆ Проверка подлинности документов\n"
        "◆ Видеоинтервью с куратором клуба\n"
        "◆ Членство в закрытой базе на 12 месяцев\n\n"
        "💳 *Стоимость: 500 000 сум*\n\n"
        "_Оплата является гарантией серьёзности ваших намерений._\n\n"
        "📌 Для оплаты свяжитесь с куратором:"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Написать куратору", url="https://t.me/qadar_curator")],
        [InlineKeyboardButton("✅ Я оплатил", callback_data="paid_manual")]
    ])
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    return PAY_WAIT

async def paid_manual(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    user = q.from_user
    db_update(user.id, status='paid', paid_at=datetime.now().isoformat())
    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💳 Заявка на оплату от @{user.username or user.id}\nПроверьте и подтвердите.",
            parse_mode="Markdown"
        )
    except: pass
    await q.edit_message_text(
        "✅ *Заявка на оплату отправлена куратору.*\n\n"
        "Как только оплата будет подтверждена — куратор откроет доступ к загрузке документов.\n\n"
        "Ожидайте сообщения в течение нескольких часов.",
        parse_mode="Markdown"
    )
    return PAY_WAIT

async def admin_confirm_pay(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Команда /confirm <telegram_id> для подтверждения оплаты администратором
    if update.effective_user.id != ADMIN_ID:
        return
    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text("Использование: /confirm <telegram_id>")
        return
    tid = int(parts[1])
    db_update(tid, status='paid', paid_at=datetime.now().isoformat())
    await ctx.bot.send_message(
        chat_id=tid,
        text=(
            "✅ *Оплата подтверждена куратором.*\n\n"
            "📁 *Загрузка документов — Шаг 1 из 4*\n\n"
            "Отправьте *фотографию вашего паспорта*\n"
            "_(разворот с фото — чёткое, без бликов)_"
        ),
        parse_mode="Markdown"
    )
    await update.message.reply_text(f"✅ Оплата подтверждена для ID {tid}")

# УЗЕЛ 5: KYC документы
async def kyc_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📁 *Загрузка документов — Шаг 1 из 4*\n\n"
        "Отправьте *фотографию вашего паспорта*\n"
        "_(разворот с фото — чёткое, без бликов)_",
        parse_mode="Markdown"
    )
    return KYC_PASSPORT

async def kyc_passport(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo and not update.message.document:
        await update.message.reply_text("⚠️ Отправьте *фотографию* паспорта.", parse_mode="Markdown")
        return KYC_PASSPORT
    fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
    ctx.user_data['passport_file'] = fid
    await update.message.reply_text(
        "✅ Паспорт получен.\n\n📁 *Шаг 2 из 4*\n\nОтправьте *фотографию диплома*:",
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
    await update.message.reply_text(
        "✅ Диплом получен.\n\n📁 *Шаг 3 из 4*\n\n"
        "Отправьте *медицинские справки* (нарко-, психо-, СПИД).\n"
        "Можно несколько файлов. Когда всё загрузите — напишите *Готово*",
        parse_mode="Markdown"
    )
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
            "✅ Справки получены.\n\n📁 *Шаг 4 из 4*\n\n"
            "Отправьте *видео-селфи* (кружок 🎥)\n"
            "Скажите: _«Я, [ФИО], подтверждаю подачу заявки в клуб QADAR»_",
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
    user = update.effective_user; d = ctx.user_data
    db_update(user.id,
              passport_file=d.get('passport_file',''),
              diploma_file=d.get('diploma_file',''),
              med_file=d.get('med_file',''),
              video_file=fid,
              status='awaiting_interview')
    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"🔔 *ДОСЬЕ ГОТОВО — QADAR*\n\n"
                f"👤 {d.get('fio','—')} | 🎂 {d.get('age','—')}\n"
                f"🏙 {d.get('city','—')} | 🎓 {d.get('education','—')}\n"
                f"📱 @{user.username or 'нет'} (ID: {user.id})\n\n"
                f"Статус: *awaiting_interview*\nНазначьте видеоинтервью."
            ),
            parse_mode="Markdown"
        )
    except: pass
    try:
        data = json.dumps({'side':'KYC','name':d.get('fio',''),'age':d.get('age',''),
            'city':d.get('city',''),'education':d.get('education',''),
            'profession':'','about':'','looking_for':'',
            'contact':f"@{user.username or user.id}",'tariff':'KYC Complete'}).encode('utf-8')
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
        "2. В течение *24 часов* вы получите звонок или сообщение "
        "в WhatsApp/Telegram для назначения видеоинтервью (Zoom)\n"
        "3. После интервью вы станете полноправным членом клуба\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "_Пожалуйста, сохраняйте конфиденциальность. "
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
            RULES:        [CallbackQueryHandler(show_rules, pattern="show_rules")],
            LEGAL:        [CallbackQueryHandler(accept, pattern="accept"),
                          CallbackQueryHandler(decline, pattern="decline")],
            Q_FIO:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fio)],
            Q_AGE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            Q_CITY:       [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            Q_EDU:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edu)],
            PAY_WAIT:     [CallbackQueryHandler(go_pay, pattern="go_pay"),
                          CallbackQueryHandler(paid_manual, pattern="paid_manual")],
            KYC_PASSPORT: [MessageHandler(filters.PHOTO | filters.Document.ALL, kyc_passport),
                          MessageHandler(filters.TEXT & ~filters.COMMAND, kyc_passport)],
            KYC_DIPLOMA:  [MessageHandler(filters.PHOTO | filters.Document.ALL, kyc_diploma),
                          MessageHandler(filters.TEXT & ~filters.COMMAND, kyc_diploma)],
            KYC_MED:      [MessageHandler(filters.PHOTO | filters.Document.ALL | filters.TEXT, kyc_med)],
            KYC_VIDEO:    [MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, kyc_video),
                          MessageHandler(filters.TEXT & ~filters.COMMAND, kyc_video)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("confirm", admin_confirm_pay))
    print("✅ QADAR Premium Bot — 6 узлов активны")
    app.run_polling()

if __name__ == "__main__":
    main()
