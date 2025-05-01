import telebot

TOKEN = '7992592517:AAFZDbIbxeKGQAWueLdlf1Evh1U2Yrza-q0'
bot = telebot.TeleBot(TOKEN)

# Словари с эмодзи для факультетов
faculty_emojis = {
    "Лечфак": "🩺",
    "Стомфак": "🦷",
    "Фармфак": "💊"
}

# Структура библиотеки
library = {
    "Лечфак": {
        "Основы медицины": ["https://example.com/lech_book1.pdf"],
        "Терапевтическая медицина": ["https://example.com/lech_book2.pdf"]
    },
    "Стомфак": {
        "Терапия": ["https://example.com/stom_therapy_book1.pdf"],
        "Хирургия": ["https://example.com/stom_surgery_book1.pdf"],
        "Ортопедия": ["https://example.com/stom_orthopedics_book1.pdf"],
        "Ортодонтия": ["https://example.com/stom_orthodontics_book1.pdf"],
        "Детская стоматология": ["https://example.com/stom_pediatric_book1.pdf"]
    },
    "Фармфак": {
        "Фармакология": ["https://example.com/pharm_book1.pdf"]
    }
}

user_state = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for faculty in library:
        label = f"{faculty_emojis.get(faculty, '')} {faculty}"
        markup.add(label)
    bot.send_message(message.chat.id, "👋 Привет! Я — бот-библиотека. Выберите факультет:", reply_markup=markup)
    user_state[message.chat.id] = {'state': 'start'}

@bot.message_handler(func=lambda msg: msg.text.strip("🩺🦷💊 ").strip() in library)
def send_categories(message):
    faculty_raw = message.text.strip()
    faculty = faculty_raw.split()[-1]  # убираем эмодзи
    user_state[message.chat.id] = {'faculty': faculty, 'state': 'faculty'}

    categories = library[faculty]
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        markup.add(category)
    markup.add("⬅️ Назад")

    bot.send_message(message.chat.id, f"📂 Категории факультета {faculty}:", reply_markup=markup)

@bot.message_handler(func=lambda msg: any(msg.text.strip() in cat for cat in library.values()))
def send_books(message):
    category_raw = message.text.strip()
    category = category_raw  # просто категория, без эмодзи

    for faculty, categories in library.items():
        if category in categories:
            books = categories[category]

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("⬅️ Назад")

            bot.send_message(message.chat.id, f"📚 Книги из категории «{category}»:",
                             reply_markup=markup)
            for book in books:
                bot.send_message(message.chat.id, f"📘 {book}")

            user_state[message.chat.id] = {'faculty': faculty, 'category': category, 'state': 'category'}
            break

@bot.message_handler(func=lambda msg: msg.text == "⬅️ Назад")
def go_back(message):
    current = user_state.get(message.chat.id, {})
    if current.get('state') == 'category':
        faculty = current['faculty']
        categories = library[faculty]
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for category in categories:
            markup.add(category)
        markup.add("⬅️ Назад")
        bot.send_message(message.chat.id, f"📂 Категории факультета {faculty}:", reply_markup=markup)
        user_state[message.chat.id] = {'faculty': faculty, 'state': 'faculty'}
    else:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for faculty in library:
            label = f"{faculty_emojis.get(faculty, '')} {faculty}"
            markup.add(label)
        bot.send_message(message.chat.id, "📚 Выберите факультет:", reply_markup=markup)
        user_state[message.chat.id] = {'state': 'start'}

@bot.message_handler(func=lambda msg: True)
def handle_unknown(message):
    bot.send_message(message.chat.id, "❗ Не понимаю. Пожалуйста, используйте кнопки или команду /start.")

bot.polling()
