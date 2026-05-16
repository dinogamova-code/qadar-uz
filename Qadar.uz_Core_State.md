# Qadar.uz — Core State
**Дата среза:** 16.05.2026 — финал дня
**Статус:** АКТИВНЫЙ ПРОЕКТ ✅

---

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

```
Клиент
  ↓
@qadaruz_bot (Telegram)
  ↓
DigitalOcean сервер 167.172.95.149
  ├── bot.py (systemd: qadar.service, ~65KB)
  ├── qadar.db (SQLite, 34 колонки)
  ├── trading_bot.py (systemd: trading.service)
  └── /root/qadar_env/ (Python venv)
  ↓
Google Sheets (QADAR Заявки)
  ↑
Apps Script Webhook (новый URL)
  ↓
Admin Telegram ID: 1995391
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
| SSH_KEY | ed25519 asus@DESKTOP-R07P0HC |

---

## 📋 ЮРИДИЧЕСКИЕ ДОКУМЕНТЫ

- Оферта: https://telegra.ph/Publichnaya-oferta-QADARUZ-05-14
- Политика: https://telegra.ph/Politika-konfidencialnosti-QADARUZ-05-14

---

## 💰 ТАРИФЫ

| Тариф | Членство |
|---|---|
| Standard | $100/год |
| Premium | $200/год |
| Elite | $300/год |

**Суюнчи:** $1000–$2500 (при фатихе или свадьбе)

---

## 🤖 БОТ — ВОРОНКА

```
/start
  → Язык (Русский / Ўзбекча)
  → Правила + NDA
  → Выбор пула:
      🌸 Впервые (QADAR)
      🌿 Хочу начать заново (Yangi Hayot)
  → Сторона (девушка / парень)
  → Анкета 14 шагов
  → Транспорт (4 кнопки)
  → Фото кандидата
  → Выбор тарифа
  → Оплата Click → Скриншот
  → KYC (паспорт → диплом → справки → видео)
  → Google Sheets + SQLite

  [Yangi Hayot — дополнительно:]
  → Есть ли дети? (Да/Нет)
  → Возраст детей (если Да)
  → Готовность принять детей партнёра?
  → Транспорт → далее стандартно
```

---

## ✅ ВАЛИДАЦИЯ

| Поле | Правило |
|---|---|
| ФИО | Минимум 2 слова |
| Возраст | Число 18–65 |
| Контакт | +998XXXXXXXXX или @username |

---

## 👑 ADMIN-ПАНЕЛЬ (Telegram)

| Команда | Действие |
|---|---|
| `/admin` | Список 15 заявок |
| `/view ID` | Полная анкета (34 поля) |
| `/approve ID` | Одобрить |
| `/reject ID` | Отклонить |
| `/match ID1 ID2` | Соединить кандидатов |

---

## 🗄️ GOOGLE SHEETS — КОЛОНКИ

A: Дата | B: Тип | C: ФИО | D: Возраст | E: Город
F: Образование | G: Работа | H: О кандидате | I: Ищет
J: Контакт | K: Тариф | L: Пул | M: Дети
N: Возраст детей | O: Принять детей

---

## 🌐 САЙТ

**Хостинг:** GitHub Pages → qadar.uz
**Секции:** Hero → О нас → Боли → KYC → Тарифы →
Галерея → Суюнчи → Регистрация → CTA → Yangi Hayot → Футер
**SEO:** Search Console ✅ | sitemap.xml ✅ | robots.txt ✅ | OG теги ✅
**Индексация Google:** ждём 3-7 дней (с 16.05.2026)

---

## 🚫 ЖЁСТКИЕ ОГРАНИЧЕНИЯ

1. DNS — менять только через IT Service Group
2. Сайт — остаётся на GitHub Pages
3. Сервер — только для бота
4. Данные клиентов — не на Notion/Airtable
5. Токен бота — не в открытом GitHub
6. IT Service Group — не писать без разрешения

---

## ✅ СТАТУС ЗАДАЧ

| Задача | Статус |
|---|---|
| Telegram бот — полная воронка | ✅ |
| Валидация ФИО/возраст/контакт | ✅ |
| Yangi Hayot — второй пул | ✅ |
| Google Sheets интеграция | ✅ |
| Сайт qadar.uz | ✅ |
| OG теги + SEO + robots.txt | ✅ |
| Google Search Console | ✅ |
| Самозанятость Soliq | ✅ |
| Click Business заявка | ✅ ждём менеджера |
| Токен бота обновлён | ✅ |
| Claude Code → сервер SSH | ✅ |
| Admin-панель куратора | ✅ |
| Instagram посты 01-02 | ✅ опубликованы |
| Instagram посты 03-09 | ⏳ по расписанию 18:00 |
| Yangi Hayot Instagram посты | ❌ |
| Компьютер организован | ✅ 636MB освобождено |

---

## 🧠 ВТОРОЙ МОЗГ

```
Obsidian (локально, C:\Users\Asus\Documents\SecondBrain\)
  ├── 28 заметок
  ├── QADAR/ EDUCATION/ FAMILY/ FINANCE/
  ├── LEGAL/ NEGOTIATIONS/ REAL_ESTATE/ _SYSTEM/
  └── context-summary.md ← главный файл памяти
  ↓ автосинхронизация каждый час
GitHub: dinogamova-code/second-brain (приватный)
  ↓
n8n: "Second Brain - GitHub Reader"
  └── Webhook → GitHub → Claude (OpenRouter) → Telegram
  ↓
Telegram бот: Dila_SecondBrain_bot
  Token: 8818277058:AAEPRxQ6wB4kAnk7oYBAGgHrHsUWasVcJMw
```

⚠️ Добавить Qadar.uz_Core_State.md в context-summary.md

---

## 🤖 N8N — ПЛАН ЗАВТРА (приоритет)

| # | Воркфлоу | Время | Результат |
|---|---|---|---|
| 1 | Умные уведомления о заявках | 30 мин | Нет ручного мониторинга |
| 2 | AI скоринг кандидатов | 1 час | Куратор видит только 7+ |
| 3 | Еженедельный отчёт | 30 мин | Авто-аналитика |
| 4 | Obsidian автообновление | 45 мин | Актуальная статистика |
| 5 | Instagram автопостинг | 2 часа | 18 постов без труда |

---

## 📁 СТРУКТУРА КОМПЬЮТЕРА

```
C:\Users\Asus\Documents\
├── QADAR\
│   ├── bot.py, oferta.md, privacy.md
│   ├── Qadar.uz_Core_State.md
│   ├── Code.gs (Apps Script)
│   ├── Сайт\ (index.html + 16 фото)
│   └── Instagram\ (партия 1, 2, Yangi Hayot)
├── Клиенты\
│   ├── Ibrahim\ (14 PDF)
│   └── Mirmuhammad\ (5 файлов)
├── Личное\
│   └── Виза Малайзия\ (3 PDF)
└── SecondBrain\ (Obsidian)
```

---

## 🔜 ЗАВТРА

1. n8n воркфлоу 1-5 (автоматизация QADAR)
2. Малайзия — подготовка Мухаммеда к IELTS (23 мая)
3. Обновить context-summary.md в Obsidian

---

## ⏰ НАПОМИНАНИЯ

- 19-20 мая: проверить site:qadar.uz в Google
- 23 мая: IELTS Мухаммед
- 30 мая: IELTS Ибрагим
- Ждём: Click Business менеджера (1-3 дня)

---

*[Архивариус] | Qadar.uz 8-Agent System | 16.05.2026 — конец дня*
