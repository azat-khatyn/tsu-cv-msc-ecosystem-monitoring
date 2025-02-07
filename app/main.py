import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from repository_models import User, SessionLocal
from model.new_model import predict
import asyncio
import cv2
import datetime

# Загружаем переменные окружения
load_dotenv()

# Токен бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Папка для сохранения фотографий
PHOTOS_DIR = "user_photos"
CAMERA_FRAME_DIR = "camera_photos"
os.makedirs(PHOTOS_DIR, exist_ok=True)  # Создаем папку, если она не существует
os.makedirs(CAMERA_FRAME_DIR, exist_ok=True)  # Создаем папку, если она не существует

# Потокобезопасная очередь для передачи сообщений
message_queue = asyncio.Queue()

# Состояния для ConversationHandler
REGISTER = 1
CLASSIFY_IMAGE = 2

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

        caption = "Неизвестный класс"
        if predicted_class == 1:
            caption = "На фотографии пожар!!!"
        elif predicted_class == 0:
            caption = "Пожара нет, не беспокойтесь."
        print(f"Предсказанный класс: {predicted_class},/n{caption}")

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


# Функция, которая выполняется в отдельном потоке и генерирует сообщения
async def generate_messages():
    # Ждем, чтобы бот успел запуститься
    await asyncio.sleep(20)

    # cоздаём объект для захвата видео с камеры (0 — индекс стандартной веб-камеры)
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print("Ошибка: Камера недоступна.")
        return

    try:
        while True:
            # ret — флаг успешности захвата, img — текущий кадр в виде массива numpy
            ret, video = capture.read()
            if not ret:
                print("Ошибка: не удалось получить кадр с камеры.")
                await asyncio.sleep(2)  # Ждем перед повторной попыткой
                continue

            # Получаем текущее время
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

            # Сохраняем изображение с текущей датой и временем
            filename =os.path.join(CAMERA_FRAME_DIR, f"frame_{timestamp}.jpg")
            cv2.imwrite(filename, video)
            print(f"Сохранён кадр: {filename}")
            await message_queue.put(filename)

            # Ожидание перед следующим кадром
            await asyncio.sleep(60)
    finally:
        # корректно освобождаем камеру и закрываем окна после завершения.
        capture.release()


# Функция для отправки сообщения в бот
async def send_messages_from_queue():
    while True:
        db = SessionLocal()
        users = db.query(User).all()
        db.close()

        message = await message_queue.get()  # Асинхронное получение из очереди
        if message is None:  # Сигнал о завершении
            break

        # Классифицируем изображение
        predicted_class = predict(message)

        caption = "Неизвестный класс"
        if predicted_class == 1:
            caption = "На фотографии пожар!!!"
        elif predicted_class == 0:
            caption = "Пожара нет, не беспокойтесь."

        for user in users:
            try:
                with open(message, 'rb') as photo:
                    await application.bot.send_photo(chat_id=user.user_id, photo=photo, caption=caption)
                print(f"Фото отправлено пользователю {user.username}")
            except Exception as e:
                print(f"Ошибка отправки фото {user.username}: {e}")

        message_queue.task_done()  # Помечаем задачу как выполненную


async def start_bot():

    global application
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

    conv_handler_resnet50 = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("ResNet50"), load_image)],
        states={
            CLASSIFY_IMAGE: [MessageHandler(filters.PHOTO, classify_image)],
        },
        fallbacks=[MessageHandler(filters.Text("Выйти в главное меню"), main_menu)],
    )

    # Регистрируем обработчики
    application.add_handler(conv_handler)
    application.add_handler(conv_handler_resnet50)
    application.add_handler(MessageHandler(filters.Text("Выйти в главное меню"), main_menu))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(MessageHandler(filters.TEXT, unknown_text))

    # Инициализация и запуск бота
    await application.initialize()
    await application.start()
    # Запуск polling’а в асинхронном режиме (не блокирует event loop)
    polling_task = asyncio.create_task(application.updater.start_polling())

    # Запуск параллельных задач для камеры и отправки сообщений
    generate_task = asyncio.create_task(generate_messages())
    send_message_task = asyncio.create_task(send_messages_from_queue())

    # Ожидаем выполнения обеих задач (или можно добавить idle для ожидания завершения)
    await asyncio.gather(polling_task, generate_task, send_message_task)


# Запуск бота
if __name__ == "__main__":
    asyncio.run(start_bot())