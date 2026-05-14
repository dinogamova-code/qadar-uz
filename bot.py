"""
QADAR.UZ - Premium Matchmaking Bot
Bilingual: Russian / Uzbek
With tariff selection and Click payment
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

BOT_TOKEN = "8484568968:AAFuQR4xrOueBt_qR0ZjBcFLnRcTQZCo9tI"
ADMIN_ID = 1995391
CLICK_NUMBER = "+998 99 509 09 09"
SHEET_URL = "https://script.google.com/macros/s/AKfycbxrEjGQFvlC-mJ0Ri7mnF5_91lmccTBVLWYsBh0cPZKiDroj0uCkcCZanCUSZXm1hS4/exec"

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

TARIFFS = {
    "standard": ("Standard", "$100", "1 300 000"),
    "premium":  ("Premium",  "$200", "2 600 000"),
    "elite":    ("Elite",    "$300", "3 900 000"),
}

# ---- TRANSLATIONS ----
MSG = {
    "ru": {
        "welcome": (
            "\U0001f3db *QADAR \u2014 \u0417\u0430\u043a\u0440\u044b\u0442\u044b\u0439 \u043a\u043b\u0443\u0431 \u043f\u043e \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0443 \u0441\u0443\u0434\u044c\u0431\u044b*\n\n"
            "\u0414\u043e\u0431\u0440\u043e \u043f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c.\n\n"
            "QADAR \u2014 \u0438\u043d\u0441\u0442\u0438\u0442\u0443\u0442 \u0434\u043e\u0432\u0435\u0440\u0438\u044f \u0434\u043b\u044f \u0438\u043d\u0442\u0435\u043b\u043b\u0438\u0433\u0435\u043d\u0442\u043d\u044b\u0445 \u0441\u0435\u043c\u0435\u0439 \u0423\u0437\u0431\u0435\u043a\u0438\u0441\u0442\u0430\u043d\u0430.\n\n"
            "*\u041d\u0430\u0448\u0438 \u043f\u0440\u0438\u043d\u0446\u0438\u043f\u044b:*\n"
            "\u25c6 \u041f\u0435\u0440\u0432\u0430\u044f \u0432\u0441\u0442\u0440\u0435\u0447\u0430 \u2014 \u0442\u043e\u043b\u044c\u043a\u043e \u043d\u0430 \u043d\u0435\u0439\u0442\u0440\u0430\u043b\u044c\u043d\u043e\u0439 \u0442\u0435\u0440\u0440\u0438\u0442\u043e\u0440\u0438\u0438\n"
            "\u25c6 \u041e\u0442\u043a\u0440\u044b\u0442\u043e\u0439 \u0431\u0430\u0437\u044b \u043d\u0435\u0442\n"
            "\u25c6 \u041a\u0430\u0436\u0434\u044b\u0439 \u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a \u043f\u0440\u043e\u0445\u043e\u0434\u0438\u0442 \u043b\u0438\u0447\u043d\u0443\u044e \u0432\u0435\u0440\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u044e\n"
            "\u25c6 \u041a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0437\u0430\u0449\u0438\u0449\u0435\u043d\u0430 NDA\n\n"
            "_\u0414\u043b\u044f \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0435\u043d\u0438\u044f \u043e\u0437\u043d\u0430\u043a\u043e\u043c\u044c\u0442\u0435\u0441\u044c \u0441 \u043f\u0440\u0430\u0432\u0438\u043b\u0430\u043c\u0438 \u043a\u043b\u0443\u0431\u0430._"
        ),
        "rules_btn": "\U0001f4cb \u041e\u0437\u043d\u0430\u043a\u043e\u043c\u0438\u0442\u044c\u0441\u044f \u0441 \u043f\u0440\u0430\u0432\u0438\u043b\u0430\u043c\u0438",
        "rules_text": (
            "\U0001f4dc *\u0423\u0441\u043b\u043e\u0432\u0438\u044f \u0447\u043b\u0435\u043d\u0441\u0442\u0432\u0430 \u0432 \u043a\u043b\u0443\u0431\u0435 QADAR*\n\n"
            "1\ufe0f\u20e3 <b>KYC-\u0432\u0435\u0440\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u044f</b> \u2014 \u043f\u0430\u0441\u043f\u043e\u0440\u0442, \u0434\u0438\u043f\u043b\u043e\u043c, \u043c\u0435\u0434\u0441\u043f\u0440\u0430\u0432\u043a\u0438.\n\n"
            "2\ufe0f\u20e3 <b>NDA</b> \u2014 \u0434\u0430\u043d\u043d\u044b\u0435 \u0434\u0440\u0443\u0433\u0438\u0445 \u0443\u0447\u0430\u0441\u0442\u043d\u0438\u043a\u043e\u0432 \u0441\u0442\u0440\u043e\u0433\u043e \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u044b.\n\n"
            "3\ufe0f\u20e3 <b>\u041e\u0444\u0435\u0440\u0442\u0430</b> \u2014 \u0440\u0435\u0433\u0443\u043b\u0438\u0440\u0443\u0435\u0442 \u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0443\u0441\u043b\u0443\u0433.\n\n"
            "\U0001f4ce <a href='https://telegra.ph/Publichnaya-oferta-QADARUZ-05-14'>\u041f\u0443\u0431\u043b\u0438\u0447\u043d\u0430\u044f \u043e\u0444\u0435\u0440\u0442\u0430</a>\n"
            "\U0001f4ce <a href='https://telegra.ph/Politika-konfidencialnosti-QADARUZ-05-14'>\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438</a>\n\n"
            "<i>\u041d\u0430\u0436\u0438\u043c\u0430\u044f \u00ab\u041f\u0440\u0438\u043d\u0438\u043c\u0430\u044e\u00bb, \u0432\u044b \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0435\u0442\u0435 \u0441\u043e\u0433\u043b\u0430\u0441\u0438\u0435.</i>"
        ),
        "accept_btn": "\u2705 \u041f\u0440\u0438\u043d\u0438\u043c\u0430\u044e \u0443\u0441\u043b\u043e\u0432\u0438\u044f",
        "decline_btn": "\u274c \u041d\u0435 \u0441\u043e\u0433\u043b\u0430\u0441\u0435\u043d",
        "declined": "\u041f\u043e\u043d\u0438\u043c\u0430\u0435\u043c \u0432\u0430\u0448\u0435 \u0440\u0435\u0448\u0435\u043d\u0438\u0435. \u0415\u0441\u043b\u0438 \u0438\u0437\u043c\u0435\u043d\u0438\u0442\u0435 \u043c\u043d\u0435\u043d\u0438\u0435 \u2014 \u043d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 /start.",
        "accepted": "\u2705 *\u0423\u0441\u043b\u043e\u0432\u0438\u044f \u043f\u0440\u0438\u043d\u044f\u0442\u044b.*\n\n\u0412\u044b \u043f\u043e\u0434\u0430\u0451\u0442\u0435 \u0437\u0430\u044f\u0432\u043a\u0443:",
        "side_girl": "\U0001f469 \u0421\u043e \u0441\u0442\u043e\u0440\u043e\u043d\u044b \u0434\u0435\u0432\u0443\u0448\u043a\u0438",
        "side_boy": "\U0001f466 \u0421\u043e \u0441\u0442\u043e\u0440\u043e\u043d\u044b \u043f\u0430\u0440\u043d\u044f",
        "questions": [
            "\u0424\u0418\u041e \u043a\u0430\u043d\u0434\u0438\u0434\u0430\u0442\u0430",
            "\u0412\u043e\u0437\u0440\u0430\u0441\u0442 \u043a\u0430\u043d\u0434\u0438\u0434\u0430\u0442\u0430",
            "\u041d\u0430\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c",
            "\u0413\u043e\u0440\u043e\u0434 \u0438 \u0440\u0430\u0439\u043e\u043d \u043f\u0440\u043e\u0436\u0438\u0432\u0430\u043d\u0438\u044f",
            "\u041f\u0440\u043e\u043f\u0438\u0441\u043a\u0430 (\u0433\u0434\u0435 \u0437\u0430\u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u043d)",
            "\u0421 \u043a\u0435\u043c \u043f\u0440\u043e\u0436\u0438\u0432\u0430\u0435\u0442 (\u0441 \u0440\u043e\u0434\u0438\u0442\u0435\u043b\u044f\u043c\u0438 / \u043e\u0442\u0434\u0435\u043b\u044c\u043d\u043e)",
            "\u0421\u043e\u0441\u0442\u0430\u0432 \u0441\u0435\u043c\u044c\u0438 (\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u0431\u0440\u0430\u0442\u044c\u0435\u0432/\u0441\u0435\u0441\u0442\u0451\u0440, \u043a\u0430\u043a\u043e\u0439 \u043f\u043e \u0441\u0447\u0451\u0442\u0443)",
            "\u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435 (\u0432\u0443\u0437, \u0441\u043f\u0435\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c, \u0433\u043e\u0434)",
            "\u041c\u0435\u0441\u0442\u043e \u0440\u0430\u0431\u043e\u0442\u044b \u0438 \u0434\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c",
            "\u041d\u0430\u043b\u0438\u0447\u0438\u0435 \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044f (\u043c\u0430\u0440\u043a\u0430, \u0433\u043e\u0434)",
            "\u0424\u0438\u043d\u0430\u043d\u0441\u043e\u0432\u043e\u0435 \u043f\u043e\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0438 \u0436\u0438\u043b\u044c\u0451",
            "\u041e \u043a\u0430\u043d\u0434\u0438\u0434\u0430\u0442\u0435 (\u0445\u0430\u0440\u0430\u043a\u0442\u0435\u0440, \u043e\u0431\u0440\u0430\u0437 \u0436\u0438\u0437\u043d\u0438, \u0446\u0435\u043d\u043d\u043e\u0441\u0442\u0438)",
            "\u041a\u043e\u0433\u043e \u0438\u0449\u0435\u0442\u0435 (\u0432\u043e\u0437\u0440\u0430\u0441\u0442, \u043e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435, \u043a\u0440\u0438\u0442\u0435\u0440\u0438\u0438)",
            "\u041a\u043e\u043d\u0442\u0430\u043a\u0442 (\u0442\u0435\u043b\u0435\u0444\u043e\u043d \u0438\u043b\u0438 Telegram)",
        ],
        "summary_hdr": "\U0001f4cb *\u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u0434\u0430\u043d\u043d\u044b\u0435:*\n\n",
        "confirm_btn": "\u2705 \u0412\u0441\u0451 \u0432\u0435\u0440\u043d\u043e, \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c",
        "restart_btn": "\u270f\ufe0f \u0417\u0430\u043f\u043e\u043b\u043d\u0438\u0442\u044c \u0437\u0430\u043d\u043e\u0432\u043e",
        "choose_tariff": "\U0001f4b3 *\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0442\u0430\u0440\u0438\u0444 (12 \u043c\u0435\u0441\u044f\u0446\u0435\u0432):*\n\n\U0001f381 \u0421\u0443\u044e\u043d\u0447\u0438 \u043f\u0440\u0438 \u0441\u0432\u0430\u0434\u044c\u0431\u0435: \u043e\u0442 $1\u202f000 \u0434\u043e $2\u202f500",
        "pay_instruction": (
            "\U0001f4b3 *\u0422\u0430\u0440\u0438\u0444 {name}*\n\n"
            "\u0421\u0443\u043c\u043c\u0430: *{uzs} \u0441\u0443\u043c ({usd})*\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "\U0001f4f1 *\u041e\u043f\u043b\u0430\u0442\u0438\u0442\u0435 \u0447\u0435\u0440\u0435\u0437 Click:*\n\n"
            "\u041d\u043e\u043c\u0435\u0440: *+998 99 509 09 09*\n"
            "\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439: *QADAR {name}*\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "_\u041f\u043e\u0441\u043b\u0435 \u043e\u043f\u043b\u0430\u0442\u044b \u043d\u0430\u0436\u043c\u0438\u0442\u0435 \u00ab\u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b\u00bb._"
        ),
        "paid_btn": "\u2705 \u042f \u043e\u043f\u043b\u0430\u0442\u0438\u043b",
        "back_btn": "\u25c0\ufe0f \u041d\u0430\u0437\u0430\u0434",
        "paid_sent": "\u2705 *\u0417\u0430\u044f\u0432\u043a\u0430 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0430 \u043a\u0443\u0440\u0430\u0442\u043e\u0440\u0443.*\n\n\u041e\u0436\u0438\u0434\u0430\u0439\u0442\u0435 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f \u0432 \u0442\u0435\u0447\u0435\u043d\u0438\u0435 \u043d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u0438\u0445 \u0447\u0430\u0441\u043e\u0432.",
        "kyc_p1": "\U0001f4c1 *\u0428\u0430\u0433 1 \u2014 \u041f\u0430\u0441\u043f\u043e\u0440\u0442*\n\n\u041e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044e \u043f\u0430\u0441\u043f\u043e\u0440\u0442\u0430\n_(\u0440\u0430\u0437\u0432\u043e\u0440\u043e\u0442 \u0441 \u0444\u043e\u0442\u043e \u2014 \u0447\u0451\u0442\u043a\u043e\u0435, \u0431\u0435\u0437 \u0431\u043b\u0438\u043a\u043e\u0432)_",
        "kyc_p2": "\u2705 \u041f\u0430\u0441\u043f\u043e\u0440\u0442 \u043f\u043e\u043b\u0443\u0447\u0435\u043d.\n\n\U0001f4c1 *\u0428\u0430\u0433 2 \u2014 \u0414\u0438\u043f\u043b\u043e\u043c*\n\n\u041e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0444\u043e\u0442\u043e\u0433\u0440\u0430\u0444\u0438\u044e \u0434\u0438\u043f\u043b\u043e\u043c\u0430:",
        "kyc_med_girl": "\u2705 \u0414\u0438\u043f\u043b\u043e\u043c \u043f\u043e\u043b\u0443\u0447\u0435\u043d.\n\n\U0001f4c1 *\u0428\u0430\u0433 3 \u2014 \u041c\u0435\u0434\u0441\u043f\u0440\u0430\u0432\u043a\u0438*\n\n\u041e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0441\u043f\u0440\u0430\u0432\u043a\u0443 \u043e\u0442 \u043f\u0441\u0438\u0445\u043e\u043d\u0435\u0432\u0440\u043e\u043b\u043e\u0433\u0430.\n_\u041f\u043e \u0436\u0435\u043b\u0430\u043d\u0438\u044e: \u0441\u043f\u0440\u0430\u0432\u043a\u0430 \u043e\u0431 \u043e\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0438\u0438 \u043d\u0430\u0441\u043b\u0435\u0434\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0445 \u0437\u0430\u0431\u043e\u043b\u0435\u0432\u0430\u043d\u0438\u0439._\n\n\u041d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 *\u0413\u043e\u0442\u043e\u0432\u043e* \u043a\u043e\u0433\u0434\u0430 \u0437\u0430\u043a\u043e\u043d\u0447\u0438\u0442\u0435.",
        "kyc_med_boy": "\u2705 \u0414\u0438\u043f\u043b\u043e\u043c \u043f\u043e\u043b\u0443\u0447\u0435\u043d.\n\n\U0001f4c1 *\u0428\u0430\u0433 3 \u2014 \u041c\u0435\u0434\u0441\u043f\u0440\u0430\u0432\u043a\u0438*\n\n\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b:\n\u25c6 \u041d\u0430\u0440\u043a\u043e\u0434\u0438\u0441\u043f\u0430\u043d\u0441\u0435\u0440\n\u25c6 \u041f\u0441\u0438\u0445\u043e\u043d\u0435\u0432\u0440\u043e\u043b\u043e\u0433\n\u25c6 \u041d\u0430\u0441\u043b\u0435\u0434\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0435 (\u043e\u043f\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e)\n\n\u041d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 *\u0413\u043e\u0442\u043e\u0432\u043e* \u043a\u043e\u0433\u0434\u0430 \u0437\u0430\u043a\u043e\u043d\u0447\u0438\u0442\u0435.",
        "file_ok": "\U0001f4ce \u0424\u0430\u0439\u043b \u043f\u043e\u043b\u0443\u0447\u0435\u043d. \u041e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0435\u0449\u0451 \u0438\u043b\u0438 \u043d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 *\u0413\u043e\u0442\u043e\u0432\u043e*",
        "need_file": "\u26a0\ufe0f \u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u0435 \u0445\u043e\u0442\u044f \u0431\u044b \u043e\u0434\u043d\u0443 \u0441\u043f\u0440\u0430\u0432\u043a\u0443.",
        "kyc_video": "\u2705 \u0421\u043f\u0440\u0430\u0432\u043a\u0438 \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u044b.\n\n\U0001f4c1 *\u0428\u0430\u0433 4 \u2014 \u0412\u0438\u0434\u0435\u043e*\n\n\u041e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0432\u0438\u0434\u0435\u043e-\u0441\u0435\u043b\u0444\u0438 (\u043a\u0440\u0443\u0436\u043e\u043a \U0001f3a5)\n_\u0421\u043a\u0430\u0436\u0438\u0442\u0435: \u00ab\u042f, [\u0424\u0418\u041e], \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u044e \u043f\u043e\u0434\u0430\u0447\u0443 \u0437\u0430\u044f\u0432\u043a\u0438 \u0432 \u043a\u043b\u0443\u0431 QADAR\u00bb_",
        "done_word": "\u0433\u043e\u0442\u043e\u0432\u043e",
        "final": (
            "\U0001f3db *\u0414\u043e\u0441\u044c\u0435 \u0441\u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u043e \u0438 \u043f\u0435\u0440\u0435\u0434\u0430\u043d\u043e \u043a\u0443\u0440\u0430\u0442\u043e\u0440\u0443.*\n\n"
            "\u0411\u043b\u0430\u0433\u043e\u0434\u0430\u0440\u0438\u043c \u0437\u0430 \u0434\u043e\u0432\u0435\u0440\u0438\u0435 \u043a \u043a\u043b\u0443\u0431\u0443 QADAR.\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "*\u0427\u0442\u043e \u0434\u0430\u043b\u044c\u0448\u0435:*\n\n"
            "1. \u041a\u0443\u0440\u0430\u0442\u043e\u0440 \u0438\u0437\u0443\u0447\u0438\u0442 \u0432\u0430\u0448\u0438 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b\n"
            "2. \u0412 \u0442\u0435\u0447\u0435\u043d\u0438\u0435 *24 \u0447\u0430\u0441\u043e\u0432* \u0432\u044b \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u0435 \u0437\u0432\u043e\u043d\u043e\u043a\n"
            "3. \u041f\u043e\u0441\u043b\u0435 \u0438\u043d\u0442\u0435\u0440\u0432\u044c\u044e \u2014 \u0447\u043b\u0435\u043d \u043a\u043b\u0443\u0431\u0430\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "_\u0421\u043e\u0445\u0440\u0430\u043d\u044f\u0439\u0442\u0435 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c._\n\n"
            "\u0421 \u0443\u0432\u0430\u0436\u0435\u043d\u0438\u0435\u043c,\n*\u041a\u043e\u043c\u0430\u043d\u0434\u0430 QADAR*"
        ),
        "cancelled": "\u041f\u0440\u0438\u043e\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u043e. \u0414\u043b\u044f \u0432\u043e\u0437\u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f \u043d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 /start.",
        "labels": [
            "\U0001f465 \u0421\u0442\u043e\u0440\u043e\u043d\u0430", "\U0001f464 \u0424\u0418\u041e", "\U0001f382 \u0412\u043e\u0437\u0440\u0430\u0441\u0442",
            "\U0001f30d \u041d\u0430\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c", "\U0001f3d9 \u0413\u043e\u0440\u043e\u0434",
            "\U0001f4cd \u041f\u0440\u043e\u043f\u0438\u0441\u043a\u0430", "\U0001f3e0 \u041f\u0440\u043e\u0436\u0438\u0432\u0430\u0435\u0442",
            "\U0001f46a \u0421\u0435\u043c\u044c\u044f", "\U0001f393 \u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435",
            "\U0001f4bc \u0420\u0430\u0431\u043e\u0442\u0430", "\U0001f697 \u0410\u0432\u0442\u043e", "\U0001f4b0 \u0424\u0438\u043d\u0430\u043d\u0441\u044b",
            "\u2728 \u041e \u043a\u0430\u043d\u0434\u0438\u0434\u0430\u0442\u0435", "\U0001f50d \u0418\u0449\u0435\u0442",
            "\U0001f4de \u041a\u043e\u043d\u0442\u0430\u043a\u0442"
        ],
    },
    "uz": {
        "welcome": (
            "\U0001f3db *QADAR \u2014 \u0422\u0430\u049b\u0434\u0438\u0440\u043d\u0438 \u045e\u043d\u0433\u043b\u0430\u0448 \u0443\u0447\u0443\u043d \u0451\u043f\u0438\u049b \u043a\u043b\u0443\u0431*\n\n"
            "\u0425\u0443\u0448 \u043a\u0435\u043b\u0438\u0431\u0441\u0438\u0437.\n\n"
            "QADAR \u2014 \u040e\u0437\u0431\u0435\u043a\u0438\u0441\u0442\u043e\u043d\u043d\u0438\u043d\u0433 \u0437\u0438\u0451\u043b\u0438 \u043e\u0438\u043b\u0430\u043b\u0430\u0440\u0438 \u0443\u0447\u0443\u043d \u0438\u0448\u043e\u043d\u0447 \u0438\u043d\u0441\u0442\u0438\u0442\u0443\u0442\u0438.\n\n"
            "*\u0411\u0438\u0437\u043d\u0438\u043d\u0433 \u0442\u0430\u043c\u043e\u0439\u0438\u043b\u043b\u0430\u0440\u0438\u043c\u0438\u0437:*\n"
            "\u25c6 \u0411\u0438\u0440\u0438\u043d\u0447\u0438 \u0443\u0447\u0440\u0430\u0448\u0443\u0432 \u2014 \u0444\u0430\u049b\u0430\u0442 \u0431\u0435\u0442\u0430\u0440\u0430\u0444 \u04b3\u0443\u0434\u0443\u0434\u0434\u0430\n"
            "\u25c6 \u041e\u0447\u0438\u049b \u0431\u0430\u0437\u0430 \u043c\u0430\u0432\u0436\u0443\u0434 \u044d\u043c\u0430\u0441\n"
            "\u25c6 \u04b2\u0430\u0440 \u0431\u0438\u0440 \u0438\u0448\u0442\u0438\u0440\u043e\u043a\u0447\u0438 \u0448\u0430\u0445\u0441\u0438\u0439 \u0442\u0435\u043a\u0448\u0438\u0440\u0443\u0432\u0434\u0430\u043d \u045e\u0442\u0430\u0434\u0438\n"
            "\u25c6 \u041c\u0430\u0445\u0444\u0438\u0439\u043b\u0438\u043a NDA \u0431\u0438\u043b\u0430\u043d \u04b3\u0438\u043c\u043e\u044f\u043b\u0430\u043d\u0433\u0430\u043d\n\n"
            "_\u0414\u0430\u0432\u043e\u043c \u044d\u0442\u0438\u0448 \u0443\u0447\u0443\u043d \u049b\u043e\u0438\u0434\u0430\u043b\u0430\u0440 \u0431\u0438\u043b\u0430\u043d \u0442\u0430\u043d\u0438\u0448\u0438\u043d\u0433._"
        ),
        "rules_btn": "\U0001f4cb \u049a\u043e\u0438\u0434\u0430\u043b\u0430\u0440 \u0431\u0438\u043b\u0430\u043d \u0442\u0430\u043d\u0438\u0448\u0438\u0448",
        "rules_text": (
            "\U0001f4dc *QADAR \u043a\u043b\u0443\u0431\u0438\u0433\u0430 \u0430\u044a\u0437\u043e\u043b\u0438\u043a \u0448\u0430\u0440\u0442\u043b\u0430\u0440\u0438*\n\n"
            "1\ufe0f\u20e3 <b>KYC-\u0442\u0435\u043a\u0448\u0438\u0440\u0443\u0432\u0438</b> \u2014 \u043f\u0430\u0441\u043f\u043e\u0440\u0442, \u0434\u0438\u043f\u043b\u043e\u043c, \u0442\u0438\u0431\u0431\u0438\u0439 \u043c\u0430\u044a\u043b\u0443\u043c\u043e\u0442\u043d\u043e\u043c\u0430.\n\n"
            "2\ufe0f\u20e3 <b>NDA</b> \u2014 \u0431\u043e\u0448\u049b\u0430 \u0438\u0448\u0442\u0438\u0440\u043e\u043a\u0447\u0438\u043b\u0430\u0440 \u043c\u0430\u044a\u043b\u0443\u043c\u043e\u0442\u043b\u0430\u0440\u0438 \u049b\u0430\u0442\u044a\u0438\u0439 \u0441\u0438\u0440 \u0441\u0430\u049b\u043b\u0430\u043d\u0430\u0434\u0438.\n\n"
            "3\ufe0f\u20e3 <b>\u041e\u043c\u043c\u0430\u0432\u0438\u0439 \u043e\u0444\u0435\u0440\u0442\u0430</b> \u2014 \u0445\u0438\u0437\u043c\u0430\u0442\u043b\u0430\u0440 \u0442\u0430\u0440\u0442\u0438\u0431\u0438\u043d\u0438 \u0431\u0435\u043b\u0433\u0438\u043b\u0430\u0439\u0434\u0438.\n\n"
            "\U0001f4ce <a href='https://telegra.ph/Publichnaya-oferta-QADARUZ-05-14'>\u041e\u043c\u043c\u0430\u0432\u0438\u0439 \u043e\u0444\u0435\u0440\u0442\u0430</a>\n"
            "\U0001f4ce <a href='https://telegra.ph/Politika-konfidencialnosti-QADARUZ-05-14'>\u041c\u0430\u0445\u0444\u0438\u0439\u043b\u0438\u043a \u0441\u0438\u0451\u0441\u0430\u0442\u0438</a>\n\n"
            "<i>\u00ab\u049a\u0430\u0431\u0443\u043b \u049b\u0438\u043b\u0430\u043c\u0430\u043d\u00bb \u0442\u0443\u0433\u043c\u0430\u0441\u0438\u043d\u0438 \u0431\u043e\u0441\u0438\u0448 \u0431\u0430\u0440\u0447\u0430 \u0440\u043e\u0437\u0438\u043b\u0438\u0433\u0438\u043d\u0433\u0438\u0437\u043d\u0438 \u0442\u0430\u0441\u0434\u0438\u049b\u043b\u0430\u0439\u0441\u0438\u0437.</i>"
        ),
        "accept_btn": "\u2705 \u0428\u0430\u0440\u0442\u043b\u0430\u0440\u043d\u0438 \u049a\u0430\u0431\u0443\u043b \u049a\u0438\u043b\u0430\u043c\u0430\u043d",
        "decline_btn": "\u274c \u0420\u043e\u0437\u0438 \u044d\u043c\u0430\u0441\u043c\u0430\u043d",
        "declined": "\u049a\u0430\u0440\u043e\u0440\u0438\u043d\u0433\u0438\u0437\u043d\u0438 \u0442\u0443\u0448\u0443\u043d\u0430\u043c\u0438\u0437. \u0424\u0438\u043a\u0440\u0438\u043d\u0433\u0438\u0437 \u045e\u0437\u0433\u0430\u0440\u0441\u0430 \u2014 /start \u0451\u0437\u0438\u043d\u0433.",
        "accepted": "\u2705 *\u0428\u0430\u0440\u0442\u043b\u0430\u0440 \u049a\u0430\u0431\u0443\u043b \u049a\u0438\u043b\u0438\u043d\u0434\u0438.*\n\n\u0410\u0440\u0438\u0437\u0430 \u0442\u043e\u043f\u0448\u0438\u0440\u0430\u0451\u0442\u0433\u0430\u043d \u0442\u0430\u0440\u0430\u0444:",
        "side_girl": "\U0001f469 \u049a\u0438\u0437 \u0442\u0430\u0440\u0430\u0444\u0438\u0434\u0430\u043d",
        "side_boy": "\U0001f466 \u0419\u0438\u0433\u0438\u0442 \u0442\u0430\u0440\u0430\u0444\u0438\u0434\u0430\u043d",
        "questions": [
            "\u041d\u043e\u043c\u0437\u043e\u0434\u043d\u0438\u043d\u0433 \u0442\u045e\u043b\u0438\u049b \u0438\u0441\u043c\u0438 (\u0424\u0418\u041e)",
            "\u041d\u043e\u043c\u0437\u043e\u0434\u043d\u0438\u043d\u0433 \u0451\u0448\u0438",
            "\u041c\u0438\u043b\u043b\u0430\u0442\u0438",
            "\u042f\u0448\u0430\u0448 \u0448\u0430\u04b3\u0430\u0440\u0438 \u0432\u0430 \u0442\u0443\u043c\u0430\u043d\u0438",
            "\u0420\u045e\u0439\u0445\u0430\u0442\u0434\u0430\u043d \u045e\u0442\u0433\u0430\u043d \u0436\u043e\u0439",
            "\u041a\u0438\u043c \u0431\u0438\u043b\u0430\u043d \u044f\u0448\u0430\u044f\u0434\u0438 (\u043e\u0442\u0430-\u043e\u043d\u0430 / \u0430\u043b\u043e\u04b3\u0438\u0434\u0430)",
            "\u041e\u0438\u043b\u0430 \u0442\u0430\u0440\u043a\u0438\u0431\u0438 (\u043d\u0435\u0447\u0430 \u0430\u043a\u0430-\u0443\u043a\u0430/\u043e\u043f\u0430-\u0441\u0438\u043d\u0433\u0438\u043b)",
            "\u0422\u0430\u044a\u043b\u0438\u043c (\u0443\u043d\u0438\u0432\u0435\u0440\u0441\u0438\u0442\u0435\u0442, \u043c\u0443\u0442\u0430\u0445\u0430\u0441\u0441\u0438\u0441\u043b\u0438\u043a, \u0439\u0438\u043b\u0438)",
            "\u0418\u0448 \u0436\u043e\u0439\u0438 \u0432\u0430 \u043b\u0430\u0432\u043e\u0437\u0438\u043c\u0438",
            "\u0410\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c (\u0440\u0443\u0441\u0443\u043c\u0438, \u0439\u0438\u043b\u0438)",
            "\u041c\u043e\u043b\u0438\u044f\u0432\u0438\u0439 \u0430\u04b3\u0432\u043e\u043b \u0432\u0430 \u0443\u0439-\u0436\u043e\u0439",
            "\u041d\u043e\u043c\u0437\u043e\u0434 \u04b3\u0430\u049b\u0438\u0434\u0430 (\u0445\u0430\u0440\u0430\u043a\u0442\u0435\u0440, \u0442\u0443\u0440\u043c\u0443\u0448 \u0442\u0430\u0440\u0437\u0438)",
            "\u041a\u0438\u043c\u043d\u0438 \u049b\u0438\u0434\u0438\u0440\u044f\u043f\u0441\u0438\u0437 (\u0451\u0448, \u0442\u0430\u044a\u043b\u0438\u043c, \u043c\u0435\u0437\u043e\u043d\u043b\u0430\u0440)",
            "\u0410\u043b\u043e\u049b\u0430 \u0443\u0447\u0443\u043d (\u0442\u0435\u043b\u0435\u0444\u043e\u043d \u0440\u0430\u049b\u0430\u043c\u0438 \u0451\u043a\u0438 Telegram)",
        ],
        "summary_hdr": "\U0001f4cb *\u041c\u0430\u044a\u043b\u0443\u043c\u043e\u0442\u043b\u0430\u0440\u043d\u0438 \u0442\u0435\u043a\u0448\u0438\u0440\u0438\u043d\u0433:*\n\n",
        "confirm_btn": "\u2705 \u0422\u045e\u0493\u0440\u0438, \u0434\u0430\u0432\u043e\u043c \u044d\u0442\u0438\u0448",
        "restart_btn": "\u270f\ufe0f \u049a\u0430\u0439\u0442\u0430\u0434\u0430\u043d \u0442\u045e\u043b\u0434\u0438\u0440\u0438\u0448",
        "choose_tariff": "\U0001f4b3 *\u0422\u0430\u0440\u0438\u0444 \u0442\u0430\u043d\u043b\u0430\u043d\u0433 (12 \u043e\u0439):*\n\n\U0001f381 \u0422\u045e\u0439 \u0431\u045e\u043b\u0441\u0430 \u0441\u0443\u044e\u043d\u0447\u0438: $1\u202f000 \u0434\u0430\u043d $2\u202f500 \u0433\u0430\u0447\u0430",
        "pay_instruction": (
            "\U0001f4b3 *{name} \u0442\u0430\u0440\u0438\u0444\u0438*\n\n"
            "\u0422\u045e\u043b\u043e\u0432 \u0441\u0443\u043c\u043c\u0430\u0441\u0438: *{uzs} \u0441\u045e\u043c ({usd})*\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "\U0001f4f1 *Click \u043e\u0440\u049b\u0430\u043b\u0438 \u0442\u045e\u043b\u0430\u043d\u0433:*\n\n"
            "\u0420\u0430\u049b\u0430\u043c: *+998 99 509 09 09*\n"
            "\u0418\u0437\u043e\u04b3: *QADAR {name}*\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "_\u0422\u045e\u043b\u043e\u0432 \u0430\u043c\u0430\u043b\u0433\u0430 \u043e\u0448\u0438\u0440\u0438\u043b\u0433\u0430\u043d\u0434\u0430\u043d \u0441\u045e\u043d\u0433 \u00ab\u0422\u045e\u043b\u0430\u0434\u0438\u043c\u00bb \u0442\u0443\u0433\u043c\u0430\u0441\u0438\u043d\u0438 \u0431\u043e\u0441\u0438\u043d\u0433._"
        ),
        "paid_btn": "\u2705 \u0422\u045e\u043b\u0430\u0434\u0438\u043c",
        "back_btn": "\u25c0\ufe0f \u041e\u0440\u049b\u0430\u0433\u0430",
        "paid_sent": "\u2705 *\u0422\u045e\u043b\u043e\u0432 \u0430\u0440\u0438\u0437\u0430\u0441\u0438 \u043a\u0443\u0440\u0430\u0442\u0443\u0440\u0433\u0430 \u044e\u0431\u043e\u0440\u0438\u043b\u0434\u0438.*\n\n\u0411\u0438\u0440 \u043d\u0435\u0447\u0430 \u0441\u043e\u0430\u0442 \u0438\u0447\u0438\u0434\u0430 \u0442\u0430\u0441\u0434\u0438\u049b\u043b\u0430\u0448\u043d\u0438 \u043a\u0443\u0442\u0438\u043d\u0433.",
        "kyc_p1": "\U0001f4c1 *1-\u049b\u0430\u0434\u0430\u043c \u2014 \u041f\u0430\u0441\u043f\u043e\u0440\u0442*\n\n\u041f\u0430\u0441\u043f\u043e\u0440\u0442 \u0440\u0430\u0441\u043c\u0438\u043d\u0438 \u044e\u0431\u043e\u0440\u0438\u043d\u0433\n_(\u0430\u043d\u0438\u049b, \u044f\u043b\u0442\u0438\u0440\u043e\u049b\u0441\u0438\u0437)_",
        "kyc_p2": "\u2705 \u041f\u0430\u0441\u043f\u043e\u0440\u0442 \u049b\u0430\u0431\u0443\u043b \u049b\u0438\u043b\u0438\u043d\u0434\u0438.\n\n\U0001f4c1 *2-\u049b\u0430\u0434\u0430\u043c \u2014 \u0414\u0438\u043f\u043b\u043e\u043c*\n\n\u0414\u0438\u043f\u043b\u043e\u043c \u0440\u0430\u0441\u043c\u0438\u043d\u0438 \u044e\u0431\u043e\u0440\u0438\u043d\u0433:",
        "kyc_med_girl": "\u2705 \u0414\u0438\u043f\u043b\u043e\u043c \u049b\u0430\u0431\u0443\u043b \u049b\u0438\u043b\u0438\u043d\u0434\u0438.\n\n\U0001f4c1 *3-\u049b\u0430\u0434\u0430\u043c \u2014 \u0422\u0438\u0431\u0431\u0438\u0439*\n\n\u041f\u0441\u0438\u0445\u043e\u043d\u0435\u0432\u0440\u043e\u043b\u043e\u0433 \u043c\u0430\u044a\u043b\u0443\u043c\u043e\u0442\u043d\u043e\u043c\u0430\u0441\u0438\u043d\u0438 \u044e\u0431\u043e\u0440\u0438\u043d\u0433.\n_\u0418\u0441\u0442\u0430\u0441\u0430\u043d\u0433\u0438\u0437: \u0438\u0440\u0441\u0438\u0439 \u043a\u0430\u0441\u0430\u043b\u043b\u0438\u043a\u043b\u0430\u0440 \u0439\u045e\u049b\u043b\u0438\u0433\u0438 \u04b3\u0430\u049b\u0438\u0434\u0430._\n\n*\u0422\u0430\u0439\u0451\u0440* \u0451\u0437\u0438\u043d\u0433.",
        "kyc_med_boy": "\u2705 \u0414\u0438\u043f\u043b\u043e\u043c \u049b\u0430\u0431\u0443\u043b \u049b\u0438\u043b\u0438\u043d\u0434\u0438.\n\n\U0001f4c1 *3-\u049b\u0430\u0434\u0430\u043c \u2014 \u0422\u0438\u0431\u0431\u0438\u0439*\n\n\u25c6 \u041d\u0430\u0440\u043a\u043e\u043b\u043e\u0433\u0438\u043a \u0434\u0438\u0441\u043f\u0430\u043d\u0441\u0435\u0440\n\u25c6 \u041f\u0441\u0438\u0445\u043e\u043d\u0435\u0432\u0440\u043e\u043b\u043e\u0433\n\u25c6 \u0418\u0440\u0441\u0438\u0439 \u043a\u0430\u0441\u0430\u043b\u043b\u0438\u043a\u043b\u0430\u0440 (\u0438\u0445\u0442\u0438\u0451\u0440\u0438\u0439)\n\n*\u0422\u0430\u0439\u0451\u0440* \u0451\u0437\u0438\u043d\u0433.",
        "file_ok": "\U0001f4ce \u0424\u0430\u0439\u043b \u049b\u0430\u0431\u0443\u043b \u049b\u0438\u043b\u0438\u043d\u0434\u0438. \u042f\u043d\u0430 \u044e\u0431\u043e\u0440\u0438\u043d\u0433 \u0451\u043a\u0438 *\u0422\u0430\u0439\u0451\u0440* \u0451\u0437\u0438\u043d\u0433",
        "need_file": "\u26a0\ufe0f \u041a\u0430\u043c\u0438\u0434\u0430 \u0431\u0438\u0442\u0442\u0430 \u043c\u0430\u044a\u043b\u0443\u043c\u043e\u0442\u043d\u043e\u043c\u0430 \u044e\u043a\u043b\u0430\u0448 \u043a\u0435\u0440\u0430\u043a.",
        "kyc_video": "\u2705 \u041c\u0430\u044a\u043b\u0443\u043c\u043e\u0442\u043d\u043e\u043c\u0430\u043b\u0430\u0440 \u049b\u0430\u0431\u0443\u043b \u049b\u0438\u043b\u0438\u043d\u0434\u0438.\n\n\U0001f4c1 *4-\u049b\u0430\u0434\u0430\u043c \u2014 \u0412\u0438\u0434\u0435\u043e*\n\n\u0412\u0438\u0434\u0435\u043e-\u0441\u0435\u043b\u0444\u0438 \u044e\u0431\u043e\u0440\u0438\u043d\u0433 (\u0434\u043e\u0438\u0440\u0430 \U0001f3a5)\n_\u0410\u0439\u0442\u0438\u043d\u0433: \u00ab\u041c\u0435\u043d, [\u0424\u0418\u041e], QADAR \u043a\u043b\u0443\u0431\u0438\u0433\u0430 \u0430\u0440\u0438\u0437\u0430 \u0442\u043e\u043f\u0448\u0438\u0440\u0438\u0448\u0438\u043c\u043d\u0438 \u0442\u0430\u0441\u0434\u0438\u049b\u043b\u0430\u0439\u043c\u0430\u043d\u00bb_",
        "done_word": "\u0442\u0430\u0439\u0451\u0440",
        "final": (
            "\U0001f3db *\u0414\u043e\u0441\u044c\u0435 \u0448\u0430\u043a\u043b\u043b\u0430\u043d\u0442\u0438\u0440\u0438\u043b\u0434\u0438 \u0432\u0430 \u043a\u0443\u0440\u0430\u0442\u0443\u0440\u0433\u0430 \u044e\u0431\u043e\u0440\u0438\u043b\u0434\u0438.*\n\n"
            "QADAR \u043a\u043b\u0443\u0431\u0438\u0433\u0430 \u0438\u0448\u043e\u043d\u0433\u0430\u043d\u0438\u043d\u0433\u0438\u0437 \u0443\u0447\u0443\u043d \u0440\u0430\u04b3\u043c\u0430\u0442.\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "*\u041a\u0435\u0439\u0438\u043d \u043d\u0438\u043c\u0430 \u0431\u045e\u043b\u0430\u0434\u0438:*\n\n"
            "1. \u041a\u0443\u0440\u0430\u0442\u043e\u0440 \u04b3\u0443\u0436\u0436\u0430\u0442\u043b\u0430\u0440\u0438\u043d\u0433\u0438\u0437\u043d\u0438 \u043a\u045e\u0440\u0438\u0431 \u0447\u0438\u049b\u0430\u0434\u0438\n"
            "2. *24 \u0441\u043e\u0430\u0442* \u0438\u0447\u0438\u0434\u0430 \u049b\u045e\u045a\u0493\u0438\u0440\u043e\u049b \u043e\u043b\u0430\u0441\u0438\u0437\n"
            "3. \u0418\u043d\u0442\u0435\u0440\u0432\u044c\u044e\u0434\u0430\u043d \u0441\u045e\u043d\u0433 \u2014 \u043a\u043b\u0443\u0431 \u0430\u044a\u0437\u043e\u0441\u0438\n\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "_\u041c\u0430\u0445\u0444\u0438\u0439\u043b\u0438\u043a\u043d\u0438 \u0441\u0430\u049b\u043b\u0430\u043d\u0433._\n\n"
            "\u04b2\u0443\u0440\u043c\u0430\u0442 \u0431\u0438\u043b\u0430\u043d,\n*QADAR \u0436\u0430\u043c\u043e\u0430\u0441\u0438*"
        ),
        "cancelled": "\u0422\u045e\u0445\u0442\u0430\u0442\u0438\u043b\u0434\u0438. \u0414\u0430\u0432\u043e\u043c \u044d\u0442\u0438\u0448 \u0443\u0447\u0443\u043d /start \u0451\u0437\u0438\u043d\u0433.",
        "labels": [
            "\U0001f465 \u0422\u0430\u0440\u0430\u0444", "\U0001f464 \u0424\u0418\u041e", "\U0001f382 \u0401\u0448",
            "\U0001f30d \u041c\u0438\u043b\u043b\u0430\u0442\u0438", "\U0001f3d9 \u0428\u0430\u04b3\u0430\u0440",
            "\U0001f4cd \u0420\u045e\u0439\u0445\u0430\u0442", "\U0001f3e0 \u042f\u0448\u0430\u044f\u0434\u0438",
            "\U0001f46a \u041e\u0438\u043b\u0430", "\U0001f393 \u0422\u0430\u044a\u043b\u0438\u043c",
            "\U0001f4bc \u0418\u0448", "\U0001f697 \u0410\u0432\u0442\u043e", "\U0001f4b0 \u041c\u043e\u043b\u0438\u044f",
            "\u2728 \u041d\u043e\u043c\u0437\u043e\u0434", "\U0001f50d \u049a\u0438\u0434\u0438\u0440\u044f\u043f\u0442\u0438",
            "\U0001f4de \u0410\u043b\u043e\u049b\u0430"
        ],
    }
}

KEYS = ["side","fio","age","nationality","city","propiska","living","family","education","work","car","finance","about","looking","contact"]
Q_STATES = [Q_FIO,Q_AGE,Q_NATION,Q_CITY,Q_PROPISKA,Q_LIVING,Q_FAMILY,Q_EDU,Q_WORK,Q_CAR,Q_FINANCE,Q_ABOUT,Q_LOOKING,Q_CONTACT]

def m(ctx, key):
    return MSG[ctx.user_data.get("lang","ru")].get(key,"")

def is_girl(ctx):
    side = ctx.user_data.get("side","")
    return "\u0434\u0435\u0432\u0443\u0448\u043a\u0438" in side or "\u049b\u0438\u0437" in side.lower()

def total_steps(ctx):
    return 13 if is_girl(ctx) else 14

def init_db():
    conn = sqlite3.connect("qadar.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE, username TEXT, lang TEXT,
        side TEXT, fio TEXT, age TEXT, nationality TEXT,
        city TEXT, propiska TEXT, living TEXT, family TEXT,
        education TEXT, work TEXT, car TEXT, finance TEXT,
        about TEXT, looking TEXT, contact TEXT, tariff TEXT,
        status TEXT DEFAULT 'new', created_at TEXT, paid_at TEXT,
        passport_file TEXT, diploma_file TEXT, med_file TEXT, video_file TEXT
    )""")
    conn.commit(); conn.close()

def db_insert(tid, uname):
    conn = sqlite3.connect("qadar.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO clients (telegram_id,username,status,created_at) VALUES (?,?,?,?)",
              (tid, uname, "new", datetime.now().isoformat()))
    conn.commit(); conn.close()

def db_update(tid, **kw):
    conn = sqlite3.connect("qadar.db")
    c = conn.cursor()
    fields = ", ".join(f"{k}=?" for k in kw)
    c.execute(f"UPDATE clients SET {fields} WHERE telegram_id=?", list(kw.values())+[tid])
    conn.commit(); conn.close()

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    db_insert(update.effective_user.id, update.effective_user.username or "")
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("\U0001f1f7\U0001f1fa \u0420\u0443\u0441\u0441\u043a\u0438\u0439", callback_data="lang_ru"),
        InlineKeyboardButton("\U0001f1fa\U0001f1ff \u040e\u0437\u0431\u0435\u043a\u0447\u0430", callback_data="lang_uz")
    ]])
    await update.message.reply_text("\U0001f3db *QADAR*\n\n\u042f\u0437\u044b\u043a / \u0422\u0438\u043b:", parse_mode="Markdown", reply_markup=kb)
    return LANG

async def set_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    lang = "ru" if q.data == "lang_ru" else "uz"
    ctx.user_data["lang"] = lang
    db_update(q.from_user.id, lang=lang)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(m(ctx,"rules_btn"), callback_data="show_rules")]])
    await q.edit_message_text(m(ctx,"welcome"), parse_mode="Markdown", reply_markup=kb)
    return RULES

async def show_rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(m(ctx,"accept_btn"), callback_data="accept")],
        [InlineKeyboardButton(m(ctx,"decline_btn"), callback_data="decline")]
    ])
    await q.edit_message_text(m(ctx,"rules_text"), parse_mode="HTML", reply_markup=kb)
    return LEGAL

async def accept(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    db_update(q.from_user.id, status="accepted")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(m(ctx,"side_girl"), callback_data="side_girl")],
        [InlineKeyboardButton(m(ctx,"side_boy"),  callback_data="side_boy")]
    ])
    await q.edit_message_text(m(ctx,"accepted"), parse_mode="Markdown", reply_markup=kb)
    return RULES

async def set_side(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data["side"] = m(ctx,"side_girl") if q.data=="side_girl" else m(ctx,"side_boy")
    questions = MSG[ctx.user_data.get("lang","ru")]["questions"]
    await q.edit_message_text(f"{questions[0]}:", parse_mode="Markdown")
    return Q_FIO

async def decline(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    await q.edit_message_text(m(ctx,"declined"))
    return ConversationHandler.END

async def ask_q(update, ctx, idx):
    questions = MSG[ctx.user_data.get("lang","ru")]["questions"]
    await update.message.reply_text(f"{questions[idx]}:", parse_mode="Markdown")

async def q_fio(u,c):
    c.user_data["fio"]=u.message.text.strip(); await ask_q(u,c,1); return Q_AGE
async def q_age(u,c):
    c.user_data["age"]=u.message.text.strip(); await ask_q(u,c,2); return Q_NATION
async def q_nation(u,c):
    c.user_data["nationality"]=u.message.text.strip(); await ask_q(u,c,3); return Q_CITY
async def q_city(u,c):
    c.user_data["city"]=u.message.text.strip(); await ask_q(u,c,4); return Q_PROPISKA
async def q_propiska(u,c):
    c.user_data["propiska"]=u.message.text.strip(); await ask_q(u,c,5); return Q_LIVING
async def q_living(u,c):
    c.user_data["living"]=u.message.text.strip(); await ask_q(u,c,6); return Q_FAMILY
async def q_family(u,c):
    c.user_data["family"]=u.message.text.strip(); await ask_q(u,c,7); return Q_EDU
async def q_edu(u,c):
    c.user_data["education"]=u.message.text.strip(); await ask_q(u,c,8); return Q_WORK

async def q_work(u,c):
    c.user_data["work"]=u.message.text.strip()
    if is_girl(c):
        await ask_q(u,c,11); return Q_ABOUT
    else:
        await ask_q(u,c,9); return Q_CAR

async def q_car(u,c):
    c.user_data["car"]=u.message.text.strip(); await ask_q(u,c,10); return Q_FINANCE
async def q_finance(u,c):
    c.user_data["finance"]=u.message.text.strip(); await ask_q(u,c,11); return Q_ABOUT
async def q_about(u,c):
    c.user_data["about"]=u.message.text.strip(); await ask_q(u,c,12); return Q_LOOKING
async def q_looking(u,c):
    c.user_data["looking"]=u.message.text.strip(); await ask_q(u,c,13); return Q_CONTACT

async def q_contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["contact"] = update.message.text.strip()
    user = update.effective_user
    d = ctx.user_data
    db_update(user.id,
        side=d.get("side",""), fio=d.get("fio",""), age=d.get("age",""),
        nationality=d.get("nationality",""), city=d.get("city",""),
        propiska=d.get("propiska",""), living=d.get("living",""),
        family=d.get("family",""), education=d.get("education",""),
        work=d.get("work",""), car=d.get("car",""),
        finance=d.get("finance",""), about=d.get("about",""),
        looking=d.get("looking",""), contact=d.get("contact",""),
        status="questionnaire_done"
    )
    labels = MSG[ctx.user_data.get("lang","ru")]["labels"]
    keys_girl = ["side","fio","age","nationality","city","propiska","living","family","education","work","about","looking","contact"]
    keys_boy  = ["side","fio","age","nationality","city","propiska","living","family","education","work","car","finance","about","looking","contact"]
    use_keys = keys_girl if is_girl(ctx) else keys_boy
    summary = m(ctx,"summary_hdr")
    for i,k in enumerate(KEYS):
        if k not in use_keys: continue
        val = d.get(k,"")
        if val:
            lbl = labels[KEYS.index(k)] if KEYS.index(k) < len(labels) else k
            summary += f"{lbl}: {val}\n"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(m(ctx,"confirm_btn"), callback_data="go_pay")],
        [InlineKeyboardButton(m(ctx,"restart_btn"), callback_data="restart")]
    ])
    await update.message.reply_text(summary, parse_mode="Markdown", reply_markup=kb)
    return PAY_WAIT

async def go_pay(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    lang = ctx.user_data.get("lang","ru")
    if lang == "uz":
        btns = [
            [InlineKeyboardButton("Standard \u2014 $100 (~1 300 000 \u0441\u045e\u043c)", callback_data="tariff_standard")],
            [InlineKeyboardButton("Premium \u2014 $200 (~2 600 000 \u0441\u045e\u043c)",  callback_data="tariff_premium")],
            [InlineKeyboardButton("Elite \u2014 $300 (~3 900 000 \u0441\u045e\u043c)",    callback_data="tariff_elite")]
        ]
    else:
        btns = [
            [InlineKeyboardButton("Standard \u2014 $100 (~1 300 000 \u0441\u0443\u043c)", callback_data="tariff_standard")],
            [InlineKeyboardButton("Premium \u2014 $200 (~2 600 000 \u0441\u0443\u043c)",  callback_data="tariff_premium")],
            [InlineKeyboardButton("Elite \u2014 $300 (~3 900 000 \u0441\u0443\u043c)",    callback_data="tariff_elite")]
        ]
    await q.edit_message_text(m(ctx,"choose_tariff"), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns))
    return PAY_WAIT

async def show_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key = q.data.replace("tariff_","")
    name, usd, uzs = TARIFFS[key]
    ctx.user_data["tariff"] = name
    text = m(ctx,"pay_instruction").format(name=name, usd=usd, uzs=uzs)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(m(ctx,"paid_btn"),  callback_data="paid_manual")],
        [InlineKeyboardButton(m(ctx,"back_btn"), callback_data="go_pay")]
    ])
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    return PAY_WAIT

async def paid_manual(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    user = q.from_user; d = ctx.user_data
    tariff = d.get("tariff","?")
    db_update(user.id, status="paid", paid_at=datetime.now().isoformat(), tariff=tariff)
    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"\U0001f4b3 *\u0422\u040e\u041b\u041e\u0412 \u0410\u0420\u0418\u0417\u0410\u0421\u0418 \u2014 QADAR*\n\n"
                f"\U0001f4e6 \u0422\u0430\u0440\u0438\u0444: *{tariff}*\n"
                f"\U0001f465 {d.get('side','')} | \U0001f30d {d.get('nationality','')}\n"
                f"\U0001f464 {d.get('fio','')} | \U0001f382 {d.get('age','')}\n"
                f"\U0001f3d9 {d.get('city','')} | \U0001f4bc {d.get('work','')}\n"
                f"\U0001f4de {d.get('contact','')}\n"
                f"\U0001f4f1 @{user.username or user.id}\n\n"
                f"\u2705 \u0422\u0430\u0441\u0434\u0438\u049b\u043b\u0430\u0448: /confirm {user.id}"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Admin notify error: {e}")
    await q.edit_message_text(m(ctx,"paid_sent"), parse_mode="Markdown")
    return PAY_WAIT

async def restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data.clear()
    await q.edit_message_text("/start")
    return ConversationHandler.END

async def admin_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    parts = update.message.text.split()
    if len(parts) < 2: await update.message.reply_text("/confirm <id>"); return
    tid = int(parts[1])
    db_update(tid, status="paid", paid_at=datetime.now().isoformat())
    await ctx.bot.send_message(
        chat_id=tid,
        text="\u2705 \u041e\u043f\u043b\u0430\u0442\u0430 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430. / \u0422\u045e\u043b\u043e\u0432 \u0442\u0430\u0441\u0434\u0438\u049b\u043b\u0430\u043d\u0434\u0438.\n\n" + "\U0001f4c1 \u041f\u0430\u0441\u043f\u043e\u0440\u0442 \u0444\u043e\u0442\u043e\u0441\u0438\u043d\u0438 \u044e\u0431\u043e\u0440\u0438\u043d\u0433 / \u0424\u043e\u0442\u043e \u043f\u0430\u0441\u043f\u043e\u0440\u0442\u0430\u0301 \u043e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435:",
        parse_mode="Markdown"
    )
    await update.message.reply_text(f"\u2705 ID {tid}")

async def kyc_passport(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(m(ctx,"kyc_p1"), parse_mode="Markdown"); return KYC_PASSPORT
    fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
    ctx.user_data["passport_file"] = fid
    await update.message.reply_text(m(ctx,"kyc_p2"), parse_mode="Markdown")
    return KYC_DIPLOMA

async def kyc_diploma(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(m(ctx,"kyc_p2"), parse_mode="Markdown"); return KYC_DIPLOMA
    fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
    ctx.user_data["diploma_file"] = fid
    ctx.user_data["med_files"] = []
    key = "kyc_med_girl" if is_girl(ctx) else "kyc_med_boy"
    await update.message.reply_text(m(ctx,key), parse_mode="Markdown")
    return KYC_MED

async def kyc_med(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.photo or update.message.document:
        fid = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
        ctx.user_data.setdefault("med_files",[]).append(fid)
        await update.message.reply_text(m(ctx,"file_ok"), parse_mode="Markdown"); return KYC_MED
    if update.message.text:
        txt = update.message.text.lower()
        if "\u0433\u043e\u0442\u043e\u0432\u043e" in txt or "\u0442\u0430\u0439\u0451\u0440" in txt:
            if not ctx.user_data.get("med_files"):
                await update.message.reply_text(m(ctx,"need_file")); return KYC_MED
            ctx.user_data["med_file"] = ",".join(ctx.user_data["med_files"])
            await update.message.reply_text(m(ctx,"kyc_video"), parse_mode="Markdown"); return KYC_VIDEO
    await update.message.reply_text(m(ctx,"file_ok"), parse_mode="Markdown"); return KYC_MED

async def kyc_video(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.video and not update.message.video_note:
        await update.message.reply_text(m(ctx,"kyc_video"), parse_mode="Markdown"); return KYC_VIDEO
    fid = update.message.video_note.file_id if update.message.video_note else update.message.video.file_id
    ctx.user_data["video_file"] = fid
    user = update.effective_user; d = ctx.user_data
    db_update(user.id, passport_file=d.get("passport_file",""),
              diploma_file=d.get("diploma_file",""), med_file=d.get("med_file",""),
              video_file=fid, status="awaiting_interview")
    try:
        girl = is_girl(ctx)
        msg = (f"\U0001f514 *\u0414\u041e\u0421\u042c\u0415 \u0422\u0410\u0419\u0401\u0420 \u2014 QADAR*\n\n"
               f"\U0001f465 {d.get('side','')} | \U0001f30d {d.get('nationality','')}\n"
               f"\U0001f464 {d.get('fio','')} | \U0001f382 {d.get('age','')}\n"
               f"\U0001f3d9 {d.get('city','')} | \U0001f393 {d.get('education','')}\n"
               f"\U0001f4bc {d.get('work','')} | \U0001f4de {d.get('contact','')}\n")
        if not girl: msg += f"\U0001f697 {d.get('car','')} | \U0001f4b0 {d.get('finance','')}\n"
        msg += f"\U0001f4f1 @{user.username or 'none'} (ID:{user.id})\nStatus: awaiting_interview"
        await ctx.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="Markdown")
    except: pass
    try:
        data = json.dumps({"side":d.get("side",""),"name":d.get("fio",""),"age":d.get("age",""),
            "city":d.get("city",""),"education":d.get("education",""),"profession":d.get("work",""),
            "about":d.get("about",""),"looking_for":d.get("looking",""),
            "contact":d.get("contact",""),"tariff":d.get("tariff","")}).encode("utf-8")
        req = urllib.request.Request(SHEET_URL, data=data, headers={"Content-Type":"application/json"})
        urllib.request.urlopen(req, timeout=5)
    except: pass
    await update.message.reply_text(m(ctx,"final"), parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    ctx.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(m(ctx,"cancelled"), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG:  [CallbackQueryHandler(set_lang,  pattern="lang_ru|lang_uz")],
            RULES: [CallbackQueryHandler(show_rules, pattern="show_rules"),
                    CallbackQueryHandler(set_side,   pattern="side_girl|side_boy")],
            LEGAL: [CallbackQueryHandler(accept,  pattern="accept"),
                    CallbackQueryHandler(decline, pattern="decline")],
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
                CallbackQueryHandler(go_pay,       pattern="go_pay"),
                CallbackQueryHandler(show_payment, pattern="tariff_standard|tariff_premium|tariff_elite"),
                CallbackQueryHandler(paid_manual,  pattern="paid_manual"),
                CallbackQueryHandler(restart,      pattern="restart"),
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
    print("QADAR Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
