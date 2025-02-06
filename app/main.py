import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from repository_models import User, SessionLocal  # Импортируем модель и сессию из предыдущего шага
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from model.new_model import predict

# Загружаем переменные окружения
load_dotenv()

# Токен бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Папка для сохранения фотографий
PHOTOS_DIR = "user_photos"
os.makedirs(PHOTOS_DIR, exist_ok=True)  # Создаем папку, если она не существует

# Состояния для ConversationHandler
REGISTER = 1

CLASSIFY_IMAGE = 1

main_keyboard = [["ResNet50", "Yolo", "GoogLeNet"]]

# Функция для проверки пользователя в базе данных
def check_user_in_db(user_id: int) -> bool:
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == user_id).first()
    db.close()
    return user is not None

# Функция для добавления пользователя в базу данных
def add_user_to_db(user_id: int, username: str):
    db = SessionLocal()
    new_user = User(user_id=user_id, username=username)
    db.add(new_user)
    db.commit()
    db.close()


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Проверяем, есть ли пользователь в базе данных
    if check_user_in_db(user_id):
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            f"Привет, {username}! Выбери модель, которую следует применить",
            reply_markup=reply_markup,
        )

    else:
        # Создаем клавиатуру с кнопкой "Зарегистрироваться"
        keyboard = [["Зарегистрироваться", "Отмена"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            f"Привет, {username}! Ты не зарегистрирован. Нажми кнопку ниже, чтобы зарегистрироваться.",
            reply_markup=reply_markup,
        )
        return REGISTER


# Обработка нажатия кнопки "Зарегистрироваться"
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(123)
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Добавляем пользователя в базу данных
    add_user_to_db(user_id, username)

    reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Вы успешно зарегистрированы!",
        reply_markup=reply_markup,
    )

    return ConversationHandler.END


# Обработка неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Начать"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        f"Извините, я не понимаю эту команду. Воспользуйтесь кнопками меню",
        reply_markup=reply_markup,
    )

# Обработка неизвестного текста
async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Начать"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        f"Извините, я не понимаю эту команду. Воспользуйтесь кнопками меню",
        reply_markup=reply_markup,
    )

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    text = update.message.text

    # Проверяем, зарегистрирован ли пользователь
    if check_user_in_db(user_id):
        await update.message.reply_text(f"{username}, ты написал: {text}")
    else:
        await update.message.reply_text("Сначала зарегистрируйся с помощью команды /start.")

# Обработка текстовых сообщений
async def load_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if check_user_in_db(user_id):
        keyboard = [["Выйти в главное меню"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            f"Прошу загрузить изображение",
            reply_markup = reply_markup,
        )
        return CLASSIFY_IMAGE
    else:
        await update.message.reply_text("Сначала зарегистрируйся с помощью команды /start.")



async def classify_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Проверяем, есть ли пользователь в базе данных
    if check_user_in_db(user_id):
        # Получаем фотографию
        photo_file = await update.message.photo[-1].get_file()  # Берем фото с самым высоким разрешением
        file_path = os.path.join(PHOTOS_DIR, f"{user_id}.jpg")  # Сохраняем фото с именем user_id.jpg

        # Скачиваем фото
        await photo_file.download_to_drive(file_path)

        # Предсказание класса
        predicted_class = predict(file_path)
        print(f"Предсказанный класс: {predicted_class}")

        keyboard = [["Выйти в главное меню"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            f"Сlass = {predicted_class}\n Загрузите следующее изображение",
            reply_markup=reply_markup,

        )

    else:
        # Создаем клавиатуру с кнопкой "Зарегистрироваться"
        keyboard = [["Зарегистрироваться", "Отмена"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            f"Привет, {username}! Ты не зарегистрирован. Нажми кнопку ниже, чтобы зарегистрироваться.",
            reply_markup=reply_markup,
        )



# Отмена регистрации
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    keyboard = [["Начать"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    # Проверяем, есть ли пользователь в базе данных
    if check_user_in_db(user_id):
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            f"Привет, {username}! Выбери модель, которую следует применить",
            reply_markup=reply_markup,
        )

        return ConversationHandler.END

    await update.message.reply_text(
        "Отмена действия. Начните заново с помощью команды /start",
        reply_markup=reply_markup,
    )
    return ConversationHandler.END

# Выход в главное меню
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Проверяем, есть ли пользователь в базе данных
    if check_user_in_db(user_id):
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Вы перешли в главное меню!",
            reply_markup=reply_markup,
        )

    else:
        # Создаем клавиатуру с кнопкой "Зарегистрироваться"
        keyboard = [["Зарегистрироваться", "Отмена"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            f"Привет, {username}! Ты не зарегистрирован. Нажми кнопку ниже, чтобы зарегистрироваться.",
            reply_markup=reply_markup,
        )


    return ConversationHandler.END


# Запуск бота
if __name__ == "__main__":
    # Создаем приложение бота
    application = Application.builder().token(TOKEN).build()

    # Создаем ConversationHandler для обработки регистрации
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("Начать"), start)],
        states={
            REGISTER: [MessageHandler(filters.Text("Зарегистрироваться"), register)],
        },
        fallbacks=[MessageHandler(filters.Text("Отмена"), cancel)],
    )


    conv_handler_ResNet50 = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("ResNet50"), load_image)],
        states={
            CLASSIFY_IMAGE: [MessageHandler(filters.PHOTO, classify_image)],
        },
        fallbacks=[MessageHandler(filters.Text("Выйти в главное меню"), main_menu)],
    )

    # Регистрируем обработчики
    application.add_handler(conv_handler)
    application.add_handler(conv_handler_ResNet50)
    application.add_handler(MessageHandler(filters.Text("Выйти в главное меню"), main_menu))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(MessageHandler(filters.TEXT, unknown_text))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()