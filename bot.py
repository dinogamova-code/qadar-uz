"""
QADAR.UZ — Premium Matchmaking Bot
Двуязычный: Русский / Узбекский (кириллица)
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
    LANG, RULES, LEGAL,
    Q_FIO, Q_AGE, Q_NATION, Q_CITY, Q_PROPISKA,
    Q_LIVING, Q_FAMILY, Q_EDU, Q_WORK,
    Q_CAR, Q_FINANCE, Q_ABOUT, Q_LOOKING, Q_CONTACT,
    PAY_WAIT,
    KYC_PASSPORT, KYC_DIPLOMA, KYC_MED, KYC_VIDEO
) = range(22)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── ПЕРЕВОДЫ ─────────────────────────────────────────────────────────────────
T = {
    'ru': {
        'welcome': (
            "🏛 *QADAR — Закрытый клуб по устройству судьбы*\n\n"
            "Добро пожаловать.\n\n"
            "QADAR — институт доверия для интеллигентных семей Узбекистана.\n\n"
            "*Наши принципы:*\n"
            "◆ Первая встреча — только на нейтральной территории\n"
            "◆ Открытой базы кандидатов не существует\n"
            "◆ Каждый участник проходит личную верификацию\n"
            "◆ Конфиденциальность защищена соглашением NDA\n\n"
            "_Для продолжения ознакомьтесь с правилами клуба._"
        ),
        'rules_btn': "📋 Ознакомиться с правилами",
        'rules_text': (
            "📜 *Условия членства в клубе QADAR*\n\n"
            "1️⃣ <b>KYC-верификация</b> — вы обязуетесь предоставить подлинные документы: "
            "паспорт, диплом, медицинские справки.\n\n"
            "2️⃣ <b>NDA</b> — данные других участников строго конфиденциальны.\n\n"
            "3️⃣ <b>Публичная оферта</b> — регулирует порядок услуг.\n\n"
            "📎 <a href='https://telegra.ph/Publichnaya-oferta-QADARUZ-05-14'>Публичная оферта</a>\n"
            "📎 <a href='https://telegra.ph/Politika-konfidencialnosti-QADARUZ-05-14'>Политика конфиденциальности</a>\n\n"
            "<i>Нажимая «Принимаю», вы подтверждаете согласие.</i>"
        ),
        'accept_btn': "✅ Принимаю условия",
        'decline_btn': "❌ Не согласен",
        'declined': "Понимаем ваше решение. Если измените мнение — напишите /start.",
        'accepted': "✅ *Условия приняты.*\n\nВы подаёте заявку:",
        'side_girl': "👩 Со стороны девушки",
        'side_boy': "👦 Со стороны парня",
        'q1': "ФИО кандидата",
        'q2': "Возраст кандидата",
        'q3': "Национальность",
        'q4': "Город и район проживания",
        'q5': "Прописка — где зарегистрирован(а)?\n_например: Ташкент, Юнусабадский район_",
        'q6': "С кем проживает?\n_например: с родителями / отдельно / с родственниками_",
        'q7': "Состав семьи:\n_сколько братьев/сестёр, каким по счёту является кандидат_",
        'q8': "Образование:\n_университет, специальность, год окончания_",
        'q9': "Место работы и должность:\n_если не работает — укажите причину_",
        'q10_car': "Наличие автомобиля:\n_есть/нет, если есть — марка и год_",
        'q11_fin': "Финансовое положение и жильё:\n_есть ли собственное жильё, уровень дохода_",
        'q_about': "Расскажите о кандидате:\n_характер, религиозность, образ жизни, увлечения_",
        'q_looking': "Кого ищете?\n_возраст, образование, характер, важные критерии_",
        'q_contact': "Контакт для связи:\n_номер телефона или Telegram — строго конфиденциально_",
        'step': "Шаг",
        'of': "из",
        'summary_title': "📋 *Проверьте данные:*\n\n",
        'confirm_btn': "✅ Всё верно, продолжить",
        'restart_btn': "✏️ Заполнить заново",
        'pay_title': (
            "🔐 *Входной аудит безопасности*\n\n"
            "Для перехода к верификации необходимо оплатить членство.\n\n"
            "*Тарифы (12 месяцев):*\n"
            "◆ Standard — $100 (~1 300 000 сум)\n"
            "◆ Premium — $200 (~2 600 000 сум)\n"
            "◆ Elite — $300 (~3 900 000 сум)\n\n"
            "🎊 *Суюнчи при свадьбе:* от $1 000 до $2 500\n\n"
            "_Для выбора тарифа и оплаты свяжитесь с куратором:_"
        ),
        'curator_btn': "💬 Написать куратору",
        'paid_btn': "✅ Я оплатил",
        'paid_sent': "✅ *Заявка на оплату отправлена куратору.*\n\nОжидайте подтверждения в течение нескольких часов.",
        'kyc_passport': "📁 *Шаг 1*\n\nОтправьте *фотографию паспорта*\n_(разворот с фото — чёткое, без бликов)_",
        'kyc_passport_ok': "✅ Паспорт получен.\n\n📁 *Шаг 2*\n\nОтправьте *фотографию диплома*:",
        'kyc_diploma_ok_girl': "✅ Диплом получен.\n\n📁 *Шаг 3*\n\nОтправьте *справку от психоневролога*.\n_По желанию: справка об отсутствии наследственных заболеваний._\n\nКогда всё загрузите — напишите *Готово*",
        'kyc_diploma_ok_boy': "✅ Диплом получен.\n\n📁 *Шаг 3*\n\nОтправьте *медицинские справки:*\n◆ Нарко-диспансер\n◆ Психоневролог\n◆ Опционально: наследственные заболевания\n\nКогда всё загрузите — напишите *Готово*",
        'file_received': "📎 Файл получен. Отправьте ещё или напишите *Готово*",
        'need_file': "⚠️ Загрузите хотя бы одну справку.",
        'kyc_video': "✅ Справки получены.\n\n📁 *Шаг 4*\n\nОтправьте *видео-селфи* (кружок 🎥)\n_Скажите: «Я, [ФИО], подтверждаю подачу заявки в клуб QADAR»_",
        'done_word': "готово",
        'final': (
            "🏛 *Досье сформировано и передано куратору.*\n\n"
            "Благодарим вас за доверие к клубу QADAR.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "*Что происходит далее:*\n\n"
            "1. Куратор изучит ваши документы\n"
            "2. В течение *24 часов* вы получите звонок для видеоинтервью\n"
            "3. После интервью вы станете членом клуба\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "_Сохраняйте конфиденциальность._\n\nС уважением,\n*Команда QADAR*"
        ),
        'cancelled': "Приостановлено. Для возобновления напишите /start.",
        'summary_fields': {
            'side': '👥 Заявка', 'fio': '👤 ФИО', 'age': '🎂 Возраст',
            'nationality': '🌍 Национальность', 'city': '🏙 Город',
            'propiska': '📍 Прописка', 'living': '🏠 Проживает',
            'family': '👨‍👩‍👧‍👦 Семья', 'education': '🎓 Образование',
            'work': '💼 Работа', 'car': '🚗 Авто', 'finance': '💰 Финансы',
            'about': '✨ О кандидате', 'looking': '🔍 Ищет', 'contact': '📞 Контакт'
        }
    },
    'uz': {
        'welcome': (
            "🏛 *QADAR — Тақдирни ўнглаш учун ёпиқ клуб*\n\n"
            "Хуш келибсиз.\n\n"
            "QADAR — Ўзбекистоннинг зиёли оилалари учун ишонч институти.\n\n"
            "*Бизнинг тамойилларимиз:*\n"
            "◆ Биринчи учрашув — фақат бетараф ҳудудда\n"
            "◆ Номзодларнинг очиқ базаси мавжуд эмас\n"
            "◆ Ҳар бир иштирокчи шахсий текширувдан ўтади\n"
            "◆ Махфийлик NDA шартномаси билан ҳимояланган\n\n"
            "_Давом этиш учун клуб қоидалари билан танишинг._"
        ),
        'rules_btn': "📋 Қоидалар билан танишиш",
        'rules_text': (
            "📜 *QADAR клубига аъзолик шартлари*\n\n"
            "1️⃣ <b>KYC-текшируви</b> — ҳақиқий ҳужжатлар тақдим этишга мажбурсиз: "
            "паспорт, диплом, тиббий маълумотнома.\n\n"
            "2️⃣ <b>NDA</b> — бошқа иштирокчилар маълумотлари қатъий сир сақланади.\n\n"
            "3️⃣ <b>Оммавий оферта</b> — хизматлар тартибини тартибга солади.\n\n"
            "📎 <a href='https://telegra.ph/Publichnaya-oferta-QADARUZ-05-14'>Оммавий оферта</a>\n"
            "📎 <a href='https://telegra.ph/Politika-konfidencialnosti-QADARUZ-05-14'>Махфийлик сиёсати</a>\n\n"
            "<i>«Қабул қиламан» тугмасини босиш орқали барча шартларга розилигингизни тасдиқлайсиз.</i>"
        ),
        'accept_btn': "✅ Шартларни қабул қиламан",
        'decline_btn': "❌ Рози эмасман",
        'declined': "Қарорингизни тушунамиз. Фикрингиз ўзгарса — /start ёзинг.",
        'accepted': "✅ *Шартлар қабул қилинди.*\n\nАризани топшираётган тараф:",
        'side_girl': "👩 Қиз тарафидан",
        'side_boy': "👦 Йигит тарафидан",
        'q1': "Номзоднинг тўлиқ исми (ФИО)",
        'q2': "Номзоднинг ёши",
        'q3': "Миллати",
        'q4': "Яшаш шаҳри ва тумани",
        'q5': "Рўйхатдан ўтган жой:\n_масалан: Тошкент, Юнусобод тумани_",
        'q6': "Ким билан яшайди?\n_масалан: ота-она билан / алоҳида / қариндошлар билан_",
        'q7': "Оила таркиби:\n_неча ака-ука/опа-сингил, номзод нечанчи фарзанд_",
        'q8': "Таълим:\n_университет, мутахассислик, тугатган йили_",
        'q9': "Иш жойи ва лавозими:\n_ишламаса — сабабини кўрсатинг_",
        'q10_car': "Автомобиль мавжудлиги:\n_бор/йўқ, бор бўлса — русуми ва йили_",
        'q11_fin': "Молиявий аҳвол ва уй-жой:\n_шахсий уй-жой борми, даромад даражаси_",
        'q_about': "Номзод ҳақида:\n_характер, диндорлик, турмуш тарзи, қизиқишлари_",
        'q_looking': "Кимни қидиряпсиз?\n_ёш, таълим, характер, муҳим мезонлар_",
        'q_contact': "Алоқа учун:\n_телефон рақами ёки Telegram — қатъий махфий_",
        'step': "Қадам",
        'of': "дан",
        'summary_title': "📋 *Маълумотларни текширинг:*\n\n",
        'confirm_btn': "✅ Тўғри, давом этиш",
        'restart_btn': "✏️ Қайтадан тўлдириш",
        'pay_title': (
            "🔐 *Хавфсизлик аудити*\n\n"
            "Текширувга ўтиш учун аъзолик тўловини амалга ошириш керак.\n\n"
            "*Тарифлар (12 ой):*\n"
            "◆ Standard — $100 (~1 300 000 сўм)\n"
            "◆ Premium — $200 (~2 600 000 сўм)\n"
            "◆ Elite — $300 (~3 900 000 сўм)\n\n"
            "🎊 *Тўй бўлса суюнчи:* $1 000 дан $2 500 гача\n\n"
            "_Тариф танлаш ва тўлов учун куратор билан боғланинг:_"
        ),
        'curator_btn': "💬 Куратор билан ёзишиш",
        'paid_btn': "✅ Тўладим",
        'paid_sent': "✅ *Тўлов аризаси куратурга юборилди.*\n\nБир неча соат ичида тасдиқлашни кутинг.",
        'kyc_passport': "📁 *1-қадам*\n\nПаспорт *расмини* юборинг\n_(сурат билан саҳифа — аниқ, ялтироқсиз)_",
        'kyc_passport_ok': "✅ Паспорт қабул қилинди.\n\n📁 *2-қадам*\n\nДиплом *расмини* юборинг:",
        'kyc_diploma_ok_girl': "✅ Диплом қабул қилинди.\n\n📁 *3-қадам*\n\nПсихоневролог маълумотномасини юборинг.\n_Истасангиз: ирсий касалликлар йўқлиги ҳақида маълумотнома._\n\nҲаммасини юкладингиз — *Тайёр* ёзинг",
        'kyc_diploma_ok_boy': "✅ Диплом қабул қилинди.\n\n📁 *3-қадам*\n\nТиббий маълумотномалар:\n◆ Наркологик диспансер\n◆ Психоневролог\n◆ Ихтиёрий: ирсий касалликлар\n\nБир нечта файл юбориш мумкин. Тугатсангиз — *Тайёр* ёзинг",
        'file_received': "📎 Файл қабул қилинди. Яна юборинг ёки *Тайёр* ёзинг",
        'need_file': "⚠️ Камида битта маълумотнома юклаш керак.",
        'kyc_video': "✅ Маълумотномалар қабул қилинди.\n\n📁 *4-қадам*\n\nВидео-селфи юборинг (доира 🎥)\n_Айтинг: «Мен, [ФИО], QADAR клубига ариза топширишимни тасдиқлайман»_",
        'done_word': "тайёр",
        'final': (
            "🏛 *Досье шакллантирилди ва куратурга юборилди.*\n\n"
            "QADAR клубига ишонганингиз учун раҳмат.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "*Кейин нима бўлади:*\n\n"
            "1. Куратор ҳужжатларингизни кўриб чиқади\n"
            "2. *24 соат* ичида видео-интервью учун қўнғироқ оласиз\n"
            "3. Интервьюдан сўнг клуб аъзосига айланасиз\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "_Махфийликни сақланг._\n\nҲурмат билан,\n*QADAR жамоаси*"
        ),
        'cancelled': "Тўхтатилди. Давом этиш учун /start ёзинг.",
        'summary_fields': {
            'side': '👥 Ариза', 'fio': '👤 ФИО', 'age': '🎂 Ёш',
            'nationality': '🌍 Миллати', 'city': '🏙 Шаҳар',
            'propiska': '📍 Рўйхат', 'living': '🏠 Яшаш',
            'family': '👨‍👩‍👧‍👦 Оила', 'education': '🎓 Таълим',
            'work': '💼 Иш', 'car': '🚗 Авто', 'finance': '💰 Молия',
            'about': '✨ Номзод ҳақида', 'looking': '🔍 Қидиряпти', 'contact': '📞 Алоқа'
        }
    }
}

def t(ctx, key):
    lang = ctx.user_data.get('lang', 'ru')
    return T[lang].get(key, T['ru'].get(key, ''))

def is_girl(ctx):
    side = ctx.user_data.get('side', '')
    return 'девушки' in side or 'қиз' in side.lower()

def total_steps(ctx):
    return 13 if is_girl(ctx) else 14

def init_db():
    conn = sqlite3.connect('qadar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE, username TEXT, lang TEXT,
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

# ─── СТАРТ — ВЫБОР ЯЗЫКА ─────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_insert(user.id, user.username or '')
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇺🇿 Ўзбекча", callback_data="lang_uz")]
    ])
    await update.message.reply_text(
        "🏛 *QADAR*\n\nЯзык / Тил seçin:",
        parse_mode="Markdown", reply_markup=kb
    )
    return LANG

async def set_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    lang = 'ru' if q.data == 'lang_ru' else 'uz'
    ctx.user_data['lang'] = lang
    db_update(q.from_user.id, lang=lang)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(t(ctx,'rules_btn'), callback_data="show_rules")]])
    await q.edit_message_text(t(ctx,'welcome'), parse_mode="Markdown", reply_markup=kb)
    return RULES

# ─── ПРАВИЛА ──────────────────────────────────────────────────────────────────
async def show_rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(ctx,'accept_btn'), callback_data="accept")],
        [InlineKeyboardButton(t(ctx,'decline_btn'), callback_data="decline")]
    ])
    await q.edit_message_text(t(ctx,'rules_text'), parse_mode="HTML", reply_markup=kb)
    return LEGAL

async def accept(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    db_update(q.from_user.id, status='accepted')
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(ctx,'side_girl'), callback_data="side_girl")],
        [InlineKeyboardButton(t(ctx,'side_boy'), callback_data="side_boy")]
    ])
    await q.edit_message_text(t(ctx,'accepted'), parse_mode="Markdown", reply_markup=kb)
    return RULES

async def set_side(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == 'side_girl':
        ctx.user_data['side'] = t(ctx,'side_girl')
    else:
        ctx.user_data['side'] = t(ctx,'side_boy')
    tot = total_steps(ctx)
    await q.edit_message_text(
        f"*{t(ctx,'step')} 1 {t(ctx,'of')} {tot}*\n\n{t(ctx,'q1')}:",
        parse_mode="Markdown"
    )
    return Q_FIO

async def decline(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(t(ctx,'declined'))
    return ConversationHandler.END

# ─── АНКЕТА ───────────────────────────────────────────────────────────────────
async def q_fio(u, c):
    c.user_data['fio'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 2 {t(c,'of')} {tot}*\n\n{t(c,'q2')}:", parse_mode="Markdown")
    return Q_AGE

async def q_age(u, c):
    c.user_data['age'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 3 {t(c,'of')} {tot}*\n\n{t(c,'q3')}:", parse_mode="Markdown")
    return Q_NATION

async def q_nation(u, c):
    c.user_data['nationality'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 4 {t(c,'of')} {tot}*\n\n{t(c,'q4')}:", parse_mode="Markdown")
    return Q_CITY

async def q_city(u, c):
    c.user_data['city'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 5 {t(c,'of')} {tot}*\n\n{t(c,'q5')}:", parse_mode="Markdown")
    return Q_PROPISKA

async def q_propiska(u, c):
    c.user_data['propiska'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 6 {t(c,'of')} {tot}*\n\n{t(c,'q6')}:", parse_mode="Markdown")
    return Q_LIVING

async def q_living(u, c):
    c.user_data['living'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 7 {t(c,'of')} {tot}*\n\n{t(c,'q7')}:", parse_mode="Markdown")
    return Q_FAMILY

async def q_family(u, c):
    c.user_data['family'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 8 {t(c,'of')} {tot}*\n\n{t(c,'q8')}:", parse_mode="Markdown")
    return Q_EDU

async def q_edu(u, c):
    c.user_data['education'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 9 {t(c,'of')} {tot}*\n\n{t(c,'q9')}:", parse_mode="Markdown")
    return Q_WORK

async def q_work(u, c):
    c.user_data['work'] = u.message.text.strip()
    tot = total_steps(c)
    if is_girl(c):
        await u.message.reply_text(f"*{t(c,'step')} 10 {t(c,'of')} {tot}*\n\n{t(c,'q_about')}:", parse_mode="Markdown")
        return Q_ABOUT
    else:
        await u.message.reply_text(f"*{t(c,'step')} 10 {t(c,'of')} {tot}*\n\n{t(c,'q10_car')}:", parse_mode="Markdown")
        return Q_CAR

async def q_car(u, c):
    c.user_data['car'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 11 {t(c,'of')} {tot}*\n\n{t(c,'q11_fin')}:", parse_mode="Markdown")
    return Q_FINANCE

async def q_finance(u, c):
    c.user_data['finance'] = u.message.text.strip()
    tot = total_steps(c)
    await u.message.reply_text(f"*{t(c,'step')} 12 {t(c,'of')} {tot}*\n\n{t(c,'q_about')}:", parse_mode="Markdown")
    return Q_ABOUT

async def q_about(u, c):
    c.user_data['about'] = u.message.text.strip()
    tot = total_steps(c)
    step = 11 if is_girl(c) else 13
    await u.message.reply_text(f"*{t(c,'step')} {step} {t(c,'of')} {tot}*\n\n{t(c,'q_looking')}:", parse_mode="Markdown")
    return Q_LOOKING

async def q_looking(u, c):
    c.user_data['looking'] = u.message.text.strip()
    tot = total_steps(c)
    step = 12 if is_girl(c) else 14
    await u.message.reply_text(f"*{t(c,'step')} {step} {t(c,'of')} {tot}*\n\n{t(c,'q_contact')}:", parse_mode="Markdown")
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
    fields = t(ctx, 'summary_fields')
    girl = is_girl(ctx)
    summary = t(ctx, 'summary_title')
    for key, label in fields.items():
        if key in ('car', 'finance') and girl:
            continue
        val = d.get(key, '—')
        if val:
            summary += f"{label}: {val}\n"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(ctx,'confirm_btn'), callback_data="go_pay")],
        [InlineKeyboardButton(t(ctx,'restart_btn'), callback_data="restart")]
    ])
    await update.message.reply_text(summary, parse_mode="Markdown", reply_markup=kb)
    return PAY_WAIT

# ─── ОПЛАТА ───────────────────────────────────────────────────────────────────
async def go_pay(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(ctx,'curator_btn'), url="https://t.me/qadar_curator")],
        [InlineKeyboardButton(t(ctx,'paid_btn'), callback_data="paid_manual")]
    ])
    await q.edit_message_text(t(ctx,'pay_title'), parse_mode="Markdown", reply_markup=kb)
    return PAY_WAIT

async def restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data.clear()
    await q.edit_message_text("Начинаем заново. / Қайтадан бошлаймиз. /start")
    return ConversationHandler.END

async def paid_manual(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    user = q.from_user
    d = ctx.user_data
    db_update(user.id, status='paid', paid_at=datetime.now().isoformat())
    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"💳 *ТЎЛОВ АРИЗАСИ — QADAR*\n\n"
                f"👥 {d.get('side','')} | 🌍 {d.get('nationality','')}\n"
                f"👤 {d.get('fio','')} | 🎂 {d.get('age','')}\n"
                f"🏙 {d.get('city','')} | 💼 {d.get('work','')}\n"
                f"📱 @{user.username or user.id}\n\n"
                f"Тасдиқлаш: /confirm {user.id}"
            ),
            parse_mode="Markdown"
        )
    except: pass
    await q.edit_message_text(t(ctx,'paid_sent'), parse_mode="Markdown")
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
            "✅ Оплата подтверждена. / Тўлов тасдиқланди.\n\n"
            "📁 *Шаг 1 / 1-қадам*\n\n"
            "Паспорт расмини юборинг / Отправьте фото паспорта\n"
            "_(чёткое, без бликов / аниқ, ялтироқсиз)_"
        ),
        parse_mode="Markdown"
    )
    await update.message.reply_text(f"✅ Подтверждено для ID {tid}")

# ─── KYC ──────────────────────────────────────────────────────────────────────
async def kyc_passport(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(t(ctx,'kyc_passport'), parse_mode="Markdown")
        return KYC_PASSPORT
    fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
    ctx.user_data['passport_file'] = fid
    await update.message.reply_text(t(ctx,'kyc_passport_ok'), parse_mode="Markdown")
    return KYC_DIPLOMA

async def kyc_diploma(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(t(ctx,'kyc_passport_ok'), parse_mode="Markdown")
        return KYC_DIPLOMA
    fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
    ctx.user_data['diploma_file'] = fid
    ctx.user_data['med_files'] = []
    key = 'kyc_diploma_ok_girl' if is_girl(ctx) else 'kyc_diploma_ok_boy'
    await update.message.reply_text(t(ctx, key), parse_mode="Markdown")
    return KYC_MED

async def kyc_med(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.photo or update.message.document:
        fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
        ctx.user_data.setdefault('med_files', []).append(fid)
        await update.message.reply_text(t(ctx,'file_received'), parse_mode="Markdown")
        return KYC_MED
    if update.message.text:
        txt = update.message.text.lower()
        if t(ctx,'done_word') in txt or 'готово' in txt or 'тайёр' in txt:
            if not ctx.user_data.get('med_files'):
                await update.message.reply_text(t(ctx,'need_file'))
                return KYC_MED
            ctx.user_data['med_file'] = ','.join(ctx.user_data['med_files'])
            await update.message.reply_text(t(ctx,'kyc_video'), parse_mode="Markdown")
            return KYC_VIDEO
    await update.message.reply_text(t(ctx,'file_received'), parse_mode="Markdown")
    return KYC_MED

async def kyc_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.video and not update.message.video_note:
        await update.message.reply_text(t(ctx,'kyc_video'), parse_mode="Markdown")
        return KYC_VIDEO
    fid = update.message.video_note.file_id if update.message.video_note else update.message.video.file_id
    ctx.user_data['video_file'] = fid
    user = update.effective_user
    d = ctx.user_data
    db_update(user.id,
        passport_file=d.get('passport_file',''), diploma_file=d.get('diploma_file',''),
        med_file=d.get('med_file',''), video_file=fid, status='awaiting_interview'
    )
    try:
        girl = is_girl(ctx)
        msg = (
            f"🔔 *ДОСЬЕ ТАЙЁР — QADAR*\n\n"
            f"👥 {d.get('side','')} | 🌍 {d.get('nationality','')}\n"
            f"👤 {d.get('fio','')} | 🎂 {d.get('age','')}\n"
            f"🏙 {d.get('city','')} | 📍 {d.get('propiska','')}\n"
            f"🏠 {d.get('living','')} | 👨‍👩‍👧‍👦 {d.get('family','')}\n"
            f"🎓 {d.get('education','')} | 💼 {d.get('work','')}\n"
        )
        if not girl:
            msg += f"🚗 {d.get('car','—')} | 💰 {d.get('finance','—')}\n"
        msg += (
            f"✨ {d.get('about','')}\n🔍 {d.get('looking','')}\n"
            f"📞 {d.get('contact','')}\n📱 @{user.username or 'нет'} (ID: {user.id})\n"
            f"Статус: awaiting_interview"
        )
        await ctx.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")
    except: pass
    try:
        data = json.dumps({
            'side': d.get('side',''), 'name': d.get('fio',''), 'age': d.get('age',''),
            'city': d.get('city',''), 'education': d.get('education',''),
            'profession': d.get('work',''), 'about': d.get('about',''),
            'looking_for': d.get('looking',''), 'contact': d.get('contact',''), 'tariff': 'KYC'
        }).encode('utf-8')
        req = urllib.request.Request(SHEET_URL, data=data, headers={'Content-Type':'application/json'})
        urllib.request.urlopen(req, timeout=5)
    except: pass
    await update.message.reply_text(t(ctx,'final'), parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    ctx.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(t(ctx,'cancelled'), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG:  [CallbackQueryHandler(set_lang, pattern="lang_ru|lang_uz")],
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
    print("✅ QADAR Bot — Рус/Ўзбек тили — запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
