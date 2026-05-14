"""
QADAR.UZ — Telegram Bot
Сценарий: приём заявок от семей
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)

# ─── НАСТРОЙКИ ───────────────────────────────────────────
BOT_TOKEN = "8484568968:AAFuQR4xrOueBt_qR0ZjBcFLnRcTQZCo9tI"
ADMIN_ID   = 000000000  # ← ЗАМЕНИ на свой Telegram ID (число)

# ─── ШАГИ АНКЕТЫ ─────────────────────────────────────────
(
    SIDE, NAME, AGE, CITY,
    EDUCATION, PROFESSION, ABOUT,
    LOOKING_FOR, CONTACT, TARIFF, CONFIRM
) = range(11)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── СТАРТ ───────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Ассалому алейкум, {user.first_name} 👋\n\n"
        "Добро пожаловать в *QADAR.UZ* — закрытый матримониальный клуб.\n\n"
        "Мы подбираем достойных партнёров для ваших детей.\n"
        "Все данные строго конфиденциальны.\n\n"
        "Для подачи заявки нажмите /anketa\n"
        "Для информации нажмите /info",
        parse_mode="Markdown"
    )


async def info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *О QADAR.UZ*\n\n"
        "Мы — закрытый клуб подбора партнёров для узбекских семей.\n\n"
        "✅ 100% верификация каждого участника\n"
        "✅ 1–3 кандидата — не список из 10\n"
        "✅ Фото закрыты до взаимного согласия\n"
        "✅ Уровни не смешиваются\n\n"
        "🌐 Сайт: qadar.uz\n"
        "📩 Подать заявку: /anketa",
        parse_mode="Markdown"
    )


# ─── НАЧАЛО АНКЕТЫ ───────────────────────────────────────
async def anketa(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [["👩 Со стороны девушки", "👦 Со стороны парня"]]
    await update.message.reply_text(
        "📋 *Анкета QADAR.UZ*\n\n"
        "Вы подаёте заявку от имени семьи.\n"
        "Ответьте на несколько вопросов — это займёт 3–4 минуты.\n\n"
        "*Вы подаёте заявку:*",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return SIDE


async def get_side(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["side"] = update.message.text
    await update.message.reply_text(
        "👤 *Имя и фамилия* вашего сына/дочери:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return NAME


async def get_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["name"] = update.message.text
    await update.message.reply_text("🎂 *Возраст:*", parse_mode="Markdown")
    return AGE


async def get_age(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["age"] = update.message.text
    await update.message.reply_text("🏙 *Город проживания:*", parse_mode="Markdown")
    return CITY


async def get_city(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["city"] = update.message.text
    await update.message.reply_text(
        "🎓 *Образование* (университет, специальность, год окончания):",
        parse_mode="Markdown"
    )
    return EDUCATION


async def get_education(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["education"] = update.message.text
    await update.message.reply_text(
        "💼 *Профессия / Место работы / Деятельность:*",
        parse_mode="Markdown"
    )
    return PROFESSION


async def get_profession(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["profession"] = update.message.text
    await update.message.reply_text(
        "🏠 *Расскажите о своей семье*\n"
        "(откуда вы, семейные ценности, образ жизни, религиозность):",
        parse_mode="Markdown"
    )
    return ABOUT


async def get_about(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["about"] = update.message.text
    await update.message.reply_text(
        "🔍 *Кого вы ищете?*\n"
        "(возраст, образование, характер, важные критерии):",
        parse_mode="Markdown"
    )
    return LOOKING_FOR


async def get_looking(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["looking_for"] = update.message.text
    await update.message.reply_text(
        "📞 *Контакт для связи*\n"
        "(номер телефона или Telegram — только с вами, конфиденциально):",
        parse_mode="Markdown"
    )
    return CONTACT


async def get_contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["contact"] = update.message.text
    keyboard = [["🥈 Standard", "🥇 Premium", "💎 Elite"]]
    await update.message.reply_text(
        "📦 *Выберите тариф:*\n\n"
        "🥈 *Standard* — до 3 кандидатов в месяц\n"
        "🥇 *Premium* — личный консьерж + до 5 кандидатов\n"
        "💎 *Elite* — VIP, неограниченный поиск, организация встречи\n\n"
        "_Стоимость уточняется индивидуально._",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return TARIFF


async def get_tariff(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["tariff"] = update.message.text
    d = ctx.user_data

    summary = (
        f"📋 *Проверьте вашу анкету:*\n\n"
        f"👥 Заявка: {d.get('side')}\n"
        f"👤 Имя: {d.get('name')}\n"
        f"🎂 Возраст: {d.get('age')}\n"
        f"🏙 Город: {d.get('city')}\n"
        f"🎓 Образование: {d.get('education')}\n"
        f"💼 Профессия: {d.get('profession')}\n"
        f"🏠 О семье: {d.get('about')}\n"
        f"🔍 Кого ищу: {d.get('looking_for')}\n"
        f"📞 Контакт: {d.get('contact')}\n"
        f"📦 Тариф: {d.get('tariff')}\n"
    )

    keyboard = [["✅ Отправить", "❌ Отменить"]]
    await update.message.reply_text(
        summary,
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return CONFIRM


async def confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if "Отправить" in update.message.text:
        d = ctx.user_data
        user = update.effective_user

        # Уведомление админу
        admin_msg = (
            f"🔔 *НОВАЯ ЗАЯВКА — QADAR.UZ*\n\n"
            f"👥 Тип: {d.get('side')}\n"
            f"👤 Имя: {d.get('name')}\n"
            f"🎂 Возраст: {d.get('age')}\n"
            f"🏙 Город: {d.get('city')}\n"
            f"🎓 Образование: {d.get('education')}\n"
            f"💼 Профессия: {d.get('profession')}\n"
            f"🏠 О семье: {d.get('about')}\n"
            f"🔍 Кого ищет: {d.get('looking_for')}\n"
            f"📞 Контакт: {d.get('contact')}\n"
            f"📦 Тариф: {d.get('tariff')}\n\n"
            f"📱 TG пользователь: @{user.username or 'нет'} (ID: {user.id})"
        )

        try:
            await ctx.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_msg,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить админу: {e}")

        await update.message.reply_text(
            "✅ *Ваша заявка принята!*\n\n"
            "Мы свяжемся с вами в течение *24 часов*.\n\n"
            "Благодарим за доверие к QADAR.UZ 🤍\n\n"
            "_Все данные строго конфиденциальны._",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "Заявка отменена. Вы можете начать заново: /anketa",
            reply_markup=ReplyKeyboardRemove()
        )

    ctx.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(
        "Отменено. Начать заново: /anketa",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ─── ЗАПУСК ──────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("anketa", anketa)],
        states={
            SIDE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_side)],
            NAME:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            CITY:        [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            EDUCATION:   [MessageHandler(filters.TEXT & ~filters.COMMAND, get_education)],
            PROFESSION:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_profession)],
            ABOUT:       [MessageHandler(filters.TEXT & ~filters.COMMAND, get_about)],
            LOOKING_FOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_looking)],
            CONTACT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact)],
            TARIFF:      [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tariff)],
            CONFIRM:     [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(conv)

    print("✅ QADAR бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
