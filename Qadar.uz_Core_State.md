# Qadar.uz — Core State
**Дата среза:** 16.05.2026
**Статус:** АКТИВНЫЙ ПРОЕКТ

---

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

```
Клиент
  ↓
@qadaruz_bot (Telegram)
  ↓
DigitalOcean сервер 167.172.95.149
  ├── bot.py (systemd: qadar.service, PID ~282671)
  ├── trading_bot.py (systemd: trading.service)
  └── /root/qadar_env/ (Python venv)
  ↓
Google Sheets (QADAR Заявки)
  ↑
Apps Script Webhook
  ↓
Admin (Telegram ID: 1995391)
```

**Сайт:**
```
GitHub Pages (github.com/dinogamova-code/qadar-uz)
  ↓ DNS через IT Service Group
qadar.uz
```

---

## 🔑 КЛЮЧЕВЫЕ ПЕРЕМЕННЫЕ

| Переменная | Значение |
|---|---|
| BOT_TOKEN | 8484568968:AAEo1sEgBUM5fjfzfYZeNP87BGwjSIxbXis |
| ADMIN_ID | 1995391 |
| SERVER_IP | 167.172.95.149 |
| CLICK_NUM | +998995090909 |
| SHEET_URL | https://script.google.com/macros/s/AKfycbxdNYv-AxQfjWjyLBF-vu3jyHgNPwfds7YhklK-2e4koUTaYo387Y-_RHxff4Da0z-O/exec |
| GOOGLE_SHEET | https://docs.google.com/spreadsheets/d/1T9ph06b7GUiPXWtVP6m-wEIqZc_5p1dLK1Fbc1Q5mYY |
| DOMAIN | qadar.uz |
| GITHUB | github.com/dinogamova-code/qadar-uz |
| EMAIL | qadaruz.official@gmail.com |
| INSTAGRAM | @qadaruz.uz |

---

## 📋 ЮРИДИЧЕСКИЕ ДОКУМЕНТЫ

- Оферта: https://telegra.ph/Publichnaya-oferta-QADARUZ-05-14
- Политика конфиденциальности: https://telegra.ph/Politika-konfidencialnosti-QADARUZ-05-14

---

## 💰 ТАРИФЫ

| Тариф | Членство | Суюнчи |
|---|---|---|
| Standard | $100/год | $1000 |
| Premium | $200/год | $1500 |
| Elite | $300/год | $2000–$2500 |

Суюнчи выплачивается только при фатихе или свадьбе.

---

## 🤖 БОТ — ВОРОНКА

```
/start
  → Язык (🇷🇺 Русский / 🇺🇿 Ўзбекча)
  → Правила + NDA
  → Выбор пула:
      🌸 Впервые (QADAR)
      🌿 Хочу начать заново (Yangi Hayot)
  → Сторона (девушка / парень)
  → Анкета 14 шагов:
      ФИО → Возраст → Национальность → Город → Прописка
      → Жильё → Семья → Образование → Работа
      → Авто → Финансы → О себе → Ищу → Контакт
  → Транспорт (4 кнопки)
  → Фото кандидата
  → Выбор тарифа
  → Оплата Click → Скриншот
  → KYC (паспорт → диплом → справки → видео)
  → Google Sheets

  [Yangi Hayot — дополнительно после контакта:]
  → Есть ли дети? (Да/Нет)
  → Возраст детей (если Да)
  → Готовность принять детей партнёра?
  → Транспорт → далее стандартно
```

---

## 🗄️ GOOGLE SHEETS — КОЛОНКИ

| # | Колонка | Описание |
|---|---|---|
| A | Дата | Автоматически |
| B | Тип | Сторона (девушка/парень) |
| C | ФИО | Полное имя |
| D | Возраст | Число |
| E | Город | + район |
| F | Образование | Уровень |
| G | Работа | Место работы |
| H | О кандидате | О себе |
| I | Ищет | Критерии партнёра |
| J | Контакт | Телефон или @username |
| K | Тариф | Standard/Premium/Elite + статус |
| L | Пул | QADAR / Yangi Hayot |
| M | Дети | Да / Нет |
| N | Возраст детей | Текст или — |
| O | Принять детей | Да / Нет / Открыта для обсуждения |
| P | Статус | ❌ Не добавлен (Admin-панель) |
| Q | Заметки | ❌ Не добавлен (Admin-панель) |

---

## 🌐 САЙТ — СТРУКТУРА

**Хостинг:** GitHub Pages → qadar.uz (DNS: IT Service Group)
**Файл:** index.html (44630 байт)

**Секции:**
- Hero слайдер
- О нас
- Боли клиента
- KYC процесс
- Тарифы (Standard/Premium/Elite)
- Галерея
- Суюнчи (без цен)
- Как подать заявку (цены: $100/$200/$300, суюнчи: при договорённости)
- CTA
- 🌿 Yangi Hayot секция
- Футер (Telegram + Instagram + Email)

**SEO:**
- Google Search Console: подключён
- sitemap.xml: добавлен
- robots.txt: добавлен
- OG теги: добавлены

---

## 🚫 ЖЁСТКИЕ ОГРАНИЧЕНИЯ

1. **DNS** — менять только через IT Service Group. Самостоятельно НЕ трогать.
2. **Сайт** — остаётся на GitHub Pages. На сервер НЕ переносить без разрешения.
3. **DigitalOcean сервер** — только для бота. Не для сайта.
4. **Данные клиентов** — не переносить на Notion/Airtable/внешние платформы.
5. **Токен бота** — не хранить в открытом GitHub репозитории.
6. **IT Service Group** — не писать им без разрешения.

---

## ✅ СТАТУС ЗАДАЧ

| Задача | Статус |
|---|---|
| Telegram бот — полная воронка | ✅ |
| Валидация ФИО/возраст/контакт | ✅ |
| Yangi Hayot — второй пул | ✅ |
| Google Sheets интеграция | ✅ |
| Сайт qadar.uz | ✅ |
| Yangi Hayot секция на сайте | ✅ |
| OG теги + SEO | ✅ |
| Google Search Console | ✅ |
| Самозанятость Soliq | ✅ |
| Click Business заявка | ✅ ждём менеджера |
| Токен бота обновлён | ✅ |
| Claude Code → сервер SSH | ✅ |
| Admin-панель куратора | ❌ в работе |
| Instagram посты 03-09 | ⏳ по расписанию |
| Yangi Hayot Instagram посты | ❌ |

---

## 🔜 СЛЕДУЮЩИЙ ШАГ

**Admin-панель куратора** — Telegram команды в боте:
- `/admin` — список новых заявок
- `/view ID` — полная анкета
- `/approve ID` — одобрить
- `/reject ID` — отклонить
- `/match ID1 ID2` — соединить кандидатов

Добавить в Google Sheets колонки P (Статус) и Q (Заметки куратора).

---

## 🏗️ ИНФРАСТРУКТУРА СЕРВЕРА

```
/root/
├── bot.py (63KB+ — основной бот)
├── qadar_env/ (Python venv)
├── mt-project/ (trading bot)
└── .ssh/authorized_keys (ed25519 asus@DESKTOP-R07P0HC)

/var/www/qadar/ (nginx — резерв, не используется)
/etc/nginx/ (nginx установлен, сайт отключён)
```

---

*Файл сгенерирован [Архивариусом] | Qadar.uz Multi-Agent System*
