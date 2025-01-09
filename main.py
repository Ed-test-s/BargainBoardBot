import telebot
from telebot import types
import sqlite3
import datetime
import re
from telebot.types import ReplyKeyboardRemove
import os
import shutil
from dotenv import load_dotenv
import time
import keyboards
import admin

# 5767703975 - филипс
# 1716228512 - жданик
# 5160115482 - Андрей
# 419202649 - Юра

# Загружаем переменные из файла .env
load_dotenv()

# Получаем токен бота из переменной окружения
API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("Токен бота не найден. Проверьте файл .env.")

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения данных об объявлениях в процессе создания объявления
advert_data = {}

# Словарь для хранения номеров пользователей в процессе создания объявления
tel_data = {}


@bot.message_handler(commands=['🐻'])
def mishka(message):
    # Открываем файл .gif.mp4 в режиме чтения
    with open("mishka.gif.mp4", "rb") as animation:
        bot.send_animation(chat_id=message.chat.id, animation=animation)


# Команда для добавления ID в список заблокированных
@bot.message_handler(commands=['ban'])
def ban_user(message):
    # Проверим, что это администратор (например, ID = 123456789, замените на свой ID)
    if message.from_user.id != 1485419781:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    try:
        # Пытаемся извлечь ID пользователя для блокировки
        user_id_to_ban = int(message.text.split()[1])
        banned_users = admin.load_banned_users()

        if user_id_to_ban in banned_users['banned']:
            bot.reply_to(message, f"Пользователь с ID {user_id_to_ban} уже заблокирован.")
        else:
            banned_users['banned'].append(user_id_to_ban)
            admin.save_banned_users(banned_users)
            bot.reply_to(message, f"Пользователь с ID {user_id_to_ban} был заблокирован.")
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите ID пользователя, который должен быть заблокирован.")
    except ValueError:
        bot.reply_to(message, "ID пользователя должен быть числом.")


# Команда для удаления ID из списка заблокированных
@bot.message_handler(commands=['unban'])
def unban_user(message):
    # Проверим, что это администратор (например, ID = 123456789, замените на свой ID)
    if message.from_user.id != 1485419781:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    try:
        # Пытаемся извлечь ID пользователя для разблокировки
        user_id_to_unban = int(message.text.split()[1])
        banned_users = admin.load_banned_users()

        if user_id_to_unban not in banned_users['banned']:
            bot.reply_to(message, f"Пользователь с ID {user_id_to_unban} не заблокирован.")
        else:
            banned_users['banned'].remove(user_id_to_unban)
            admin.save_banned_users(banned_users)
            bot.reply_to(message, f"Пользователь с ID {user_id_to_unban} был разблокирован.")
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите ID пользователя, который должен быть разблокирован.")
    except ValueError:
        bot.reply_to(message, "ID пользователя должен быть числом.")


# Декоратор для проверки, заблокирован ли пользователь
def check_banned(func):
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        banned_users = admin.load_banned_users()
        if user_id in banned_users['banned']:
            bot.reply_to(message, "Вы заблокированы. Доступ к боту ограничен.")
            return  # Прерываем выполнение функции, если пользователь заблокирован
        return func(message, *args, **kwargs)  # Если не заблокирован, выполняем исходную функцию

    return wrapper


@bot.message_handler(commands=['start'])
@check_banned
def start_message(message):
    full_datetime = datetime.datetime.now().replace(microsecond=0)
    print(f'User {message.from_user.id} launch bot at {full_datetime}')

    bot.send_message(message.chat.id,
                     'Привет! 👋 Добро пожаловать в бота для размещения объявлений по продажам!'
                     ' Здесь вы можете легко и быстро создавать объявление, чтобы продать свои товары или услуги. 📦💰'
                     '\n\nЕсли у вас возникнут вопросы или потребуется помощь, нажмите на кнопку ниже.😊'
                     '\n\nУдачи в продажах! 🎉', reply_markup=keyboards.help_kb())

    bot.send_message(message.chat.id, 'Сделайте выбор, выбрав одну из кнопок ниже:',
                     reply_markup=keyboards.main_menu_kb())


@bot.message_handler(commands=['help'])
@check_banned
def send_help(message):
    bot.send_message(message.chat.id,
                     'Список доступных команд:'
                     '\n1) /help - 🆘 список команд'
                     '\n2) /restart - 🔄 перезапустит бота (вызовет главное меню)'
                     '\n3) /ban - 🔐 заблокировать пользователя (доступно только для администратора)'
                     '\n4) /unban - 🔓 разблокировать пользователя (доступно только для администратора)'
                     f'\nЕсли появились какие-то вопросы касательно работы бота, свяжитесь с автором: @ADR3NAL1N41K',
                     parse_mode='HTML')


# Обработка callback запроса для кнопки "Помощь"
@bot.callback_query_handler(func=lambda call: call.data == "help")
@check_banned
def callback_help(call):
    # Отправляем команду /help от имени пользователя
    bot.answer_callback_query(call.id)  # Подтверждаем клик
    send_help(call.message)  # Вызываем функцию send_help


@bot.message_handler(commands=['restart'])
@check_banned
def start_menu(message):
    bot.send_message(message.chat.id, 'Сделайте выбор, выбрав одну из кнопок ниже:',
                     reply_markup=keyboards.main_menu_kb())


@bot.message_handler(func=lambda message: message.text == '🖊️ Подать объявление')
@check_banned
def start_creating_advert(message):
    bot.send_message(message.chat.id,
                     '<b>Учитывайте, что для создания объявления нужно иметь username пользователя или предоставить номер телефона.</b>'
                     '\nПриступим к созданию нового объявления.', parse_mode='HTML')
    create_advert(message)


@bot.message_handler(func=lambda message: message.text == '👀 Смотреть объявления')
@check_banned
def start_watching_adverts(message):
    watch_advert(message)


@bot.message_handler(func=lambda message: message.text == '📂 Мои объявления')
@check_banned
def start_watching_my_ads(message):
    watch_my_ads(message)


def create_advert(message):
    if message.from_user.username is None:
        # Отправляем сообщение с обеими клавиатурами
        bot.send_message(
            message.chat.id,
            'Добавьте username, перейдя в настройки по кнопке ниже:',
            reply_markup=keyboards.create_username_kb()
        )
        bot.send_message(
            message.chat.id,
            'Предоставьте номер телефона, нажав на кнопку ниже:',
            reply_markup=keyboards.get_telnum_kb()
        )
    else:
        bot.send_message(message.chat.id, 'Выберите категорию для объявления:',
                         reply_markup=keyboards.select_category_for_create_advert_kb())


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.contact is not None:
        phone_number = message.contact.phone_number
        bot.send_message(message.chat.id, f"Ваш номер телефона: {phone_number}. Теперь вы можете создать объявление.")
        tel_data[message.chat.id] = {'telnum': phone_number}
        print(advert_data)

    bot.send_message(message.chat.id, 'Выберите категорию для объявления:',
                     reply_markup=keyboards.select_category_for_create_advert_kb())


# Обработчик для выбора категории при создании объявления
@bot.callback_query_handler(func=lambda callback: callback.data in ['housing_create', 'product_create', 'service_create'])
@check_banned
def category_selected(callback):
    # Сохраняем выбранную категорию
    advert_data[callback.message.chat.id] = {'category': callback.data.split('_')[0]}
    bot.send_message(callback.message.chat.id, 'Введите название объявления:')
    bot.register_next_step_handler(callback.message, get_title)


def get_title(message):
    if len(message.text) > 32:
        bot.send_message(message.chat.id,
                         'Название объявления не должно превышать 32 символа. Пожалуйста, введите название снова:')
        bot.register_next_step_handler(message, get_title)
        return

    count_of_underlines = 0
    for i in message.text:
        if i == '_':
            count_of_underlines = count_of_underlines + 1

    if count_of_underlines > 0:
        bot.send_message(message.chat.id,
                         "Название объявления не должно содержать символ '_'. Пожалуйста, введите название снова:")
        bot.register_next_step_handler(message, get_title)
        return

    if message.text == '🖊️ Подать объявление' or message.text == '👀 Смотреть объявления' or message.text == '📂 Мои объявления':
        bot.send_message(message.chat.id,
                         "Пожалуйста, введите корректное название:")
        bot.register_next_step_handler(message, get_title)
        return

    regular_for_title = r'^[A-Za-zА-Яа-я0-9 ]+$'
    if not re.match(regular_for_title, message.text):
        bot.send_message(message.chat.id,
                         "Нельзя использовать специальные символы! Пожалуйста, введите корректное название:")
        bot.register_next_step_handler(message, get_title)
        return

    advert_data[message.chat.id]['title'] = message.text
    bot.send_message(message.chat.id, 'Введите описание объявления:')
    bot.register_next_step_handler(message, get_description)


def get_description(message):
    if message.text == '🖊️ Подать объявление' or message.text == '👀 Смотреть объявления' or message.text == '📂 Мои объявления':
        bot.send_message(message.chat.id,
                         "Пожалуйста, введите корректное описание:")
        bot.register_next_step_handler(message, get_description)
        return

    advert_data[message.chat.id]['description'] = message.text

    bot.send_message(message.chat.id, "Введите цену объявления (BYN):\n"
                                      "Вводите цену в правильном формате (например: 100, 100.99"
                                      ", 'Договорная',  'Бесплатно'.", reply_markup=keyboards.price_kb())

    bot.register_next_step_handler(message, get_price)


def get_price(message):
    price = ''
    # Регулярное выражение для проверки формата цены (до 2 знаков после запятой)
    price_text = message.text
    price_pattern = r'^\d+(\.\d{1,2})?$'  # Цена, состоящая из целой части и до 2 знаков после запятой

    # Проверяем, соответствует ли введённый текст регулярному выражению
    if not re.match(price_pattern, price_text) and not price_text == 'Договорная' and not price_text == 'Бесплатно':
        bot.send_message(message.chat.id, "Пожалуйста, введите цену в правильном формате (например: 100 или 100.99 "
                                          "или 'Договорная' или 'Бесплатно'.")
        bot.register_next_step_handler(message, get_price)  # Запрашиваем цену снова
        return

    if price_text == 'Договорная':
        price = price_text
    elif price_text == 'Бесплатно':
        price = price_text
    elif float(price_text) <= 0:
        bot.send_message(message.chat.id, "Цена должна быть больше нуля. Пожалуйста, введите корректную цену.")
        bot.register_next_step_handler(message, get_price)  # Запрашиваем цену снова
        return
    elif float(price_text) > 0:
        price = price_text

    #Сохраняем цену объявления
    advert_data[message.chat.id]['price'] = price
    print(advert_data)
    bot.send_message(message.chat.id, "Пришлите фото для объявления (если есть).\nОтправляйте по одной фотографии!\n"
                                      "К объявлению можно прикрепить до 10 фотографий!"
                                      "\nЕсли вы хотите создать объявление без фотографий, введите /done",
                     reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_user_pics)


photo_ids = []  # Список для хранения file_id всех полученных фотографий


@bot.message_handler(content_types=['photo'])
@check_banned
def get_user_pics(message):
    # Путь для хранения фотографий на сервере
    user_id = message.from_user.id
    title = advert_data[message.chat.id]["title"]
    folder_name = f"{user_id}_{title}"
    folder_path = os.path.join('adv_photos_folder', folder_name)

    print('Количество элементов в file_ids: ', len(photo_ids))

    # Создаем папку, если ее нет
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if message.text == '/done':
        get_photo(message, photo_ids)
        return

    elif len(photo_ids) >= 10:
        bot.send_message(message.chat.id, 'Нельзя прикрепить больше 10 фотографий')
        get_photo(message, photo_ids)
        return

    elif message.photo:
        if message.photo[-1].file_id not in photo_ids:
            # Получаем самую высококачественную фотографию (обычно последнюю в списке)
            photo = message.photo[-1]  # Берем последний элемент
            file_id = photo.file_id
            print(file_id)
            file_path = bot.get_file(file_id).file_path
            print(bot.get_file(file_id))
            print('file_path: ', file_path)
            file_name = file_path.split('/')[-1]
            print('file_name: ', file_name)
            downloaded_file = bot.download_file(file_path)

            # Сохраняем файл в папку
            with open(os.path.join(folder_path, file_name), 'wb') as f:
                f.write(downloaded_file)

            photo_ids.append(file_id)  # Добавляем file_id фотографии в список

    elif message.document:
        bot.send_message(message.chat.id, 'Отправляйте фото в сжатом формате!')
        return

    send = bot.send_message(message.from_user.id, "Добавьте ещё фото или нажмите\n /done")
    bot.register_next_step_handler(send, get_user_pics)
    return


def get_photo(message, photo_ids):
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()
    # ДОЗАПИСЫВАЕМ ДАННЫЕ О ДАТЕ СОЗДАНИЯ ОБЪЯВЛЕНИЯ И USER_id ПОЛЬЗОВАТЕЛЯ
    full_datetime = datetime.datetime.now()
    # Преобразование в строку с нужным форматом
    current_datetime = full_datetime.strftime("%Y-%m-%d %H:%M:%S")
    advert_data[message.chat.id]['date'] = current_datetime

    if not photo_ids:
        advert_data[message.chat.id]['photo'] = None
        bot.send_message(message.chat.id, 'Фотографии не получены. Объявление будет без фото.')
    else:
        advert_data[message.chat.id]['photo'] = photo_ids  # Сохраняем list file_id
        bot.send_message(message.chat.id, 'Объявление создано с фотографиями!')

    if message.from_user.username is None:
        advert_data[message.chat.id]['telnum'] = tel_data[message.chat.id]['telnum']
    else:
        advert_data[message.chat.id]['telnum'] = None

    # Отправляем все собранные данные для пользователя
    advert = advert_data[message.chat.id]
    print(advert)

    if message.from_user.username is None:
        # Записываем данные в БД
        cursor.execute("""
                INSERT INTO AdvertTable(UserID, ChatID, Authors_username, Category, Title, Description, Price, Photos, 
                Date, TelNumber)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
            message.from_user.id,
            message.chat.id,
            None,
            advert["category"],
            advert["title"],
            advert["description"],
            advert["price"],
            ','.join(advert['photo']) if advert['photo'] else None,  # Сохраняем file_ids как строку
            current_datetime,
            advert["telnum"]
        ))

    else:
        # Записываем данные в БД
        cursor.execute("""
                INSERT INTO AdvertTable(UserID, ChatID, Authors_username, Category, Title, Description, Price, Photos, 
                Date, TelNumber)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
            message.from_user.id,
            message.chat.id,
            message.from_user.username,
            advert["category"],
            advert["title"],
            advert["description"],
            advert["price"],
            ','.join(advert['photo']) if advert['photo'] else None,  # Сохраняем file_ids как строку
            current_datetime,
            None
        ))

    connect.commit()
    connect.close()
    printed_category = 'undef'

    if advert["category"] == 'housing':
        printed_category = 'Жильё'
    elif advert["category"] == 'product':
        printed_category = 'Товар'
    elif advert["category"] == 'service':
        printed_category = 'Услуга'

    if advert["price"] == 'Бесплатно' or advert["price"] == 'Договорная':
        # Отправляем данные пользователю
        bot.send_message(message.chat.id, f'Категория: {printed_category}\n'
                                          f'<b>Название: {advert["title"]}</b>\n'
                                          f'Описание: {advert["description"]}\n'
                                          f'Цена: {advert["price"]}\n'
                                          f'Фото: {"Есть" if advert["photo"] else "Нет"}\n'
                                          f'Автор объявления: @{message.from_user.username if message.from_user.username != None else advert["telnum"]}\n'
                                          f'Время подачи объявления: {advert["date"]}', parse_mode='HTML',
                         reply_markup=keyboards.main_menu_kb())
    else:
        # Отправляем данные пользователю
        bot.send_message(message.chat.id, f'Категория: {printed_category}\n'  # f'Категория: {advert["category"]}\n'
                                          f'<b>Название: {advert["title"]}</b>\n'
                                          f'Описание: {advert["description"]}\n'
                                          f'Цена: {advert["price"]} BYN\n'
                                          f'Фото: {"Есть" if advert["photo"] else "Нет"}\n'
                                          f'Автор объявления: @{message.from_user.username if message.from_user.username != None else advert["telnum"]}\n'
                                          f'Время подачи объявления: {advert["date"]}', parse_mode='HTML',
                         reply_markup=keyboards.main_menu_kb())

    # Очистим данные для этого пользователя
    del advert_data[message.chat.id]


###################################################################       ПРОСМОТР ОБЪЯВЛЕНИЙ

# Хранилище для состояния (память на время сессии)
user_state = {}
category = ''


# Обработчик для просмотра объявлений
def watch_advert(message):
    bot.send_message(message.chat.id, 'Выберите категорию для поиска:',
                     reply_markup=keyboards.select_category_for_watch_advert_kb())


# Обработчик для выбора категории при просмотре объявлений
@bot.callback_query_handler(func=lambda callback: callback.data in ['housing_watch', 'product_watch', 'service_watch'])
@check_banned
def watch_category_handler(callback):
    # Получаем callback_data из нажатой кнопки
    category = 'undef'
    name_of_category = 'undef'
    if callback.data == 'housing_watch':
        category = 'housing'
        name_of_category = 'Жильё'
    elif callback.data == 'product_watch':
        category = 'product'
        name_of_category = 'Товар'
    elif callback.data == 'service_watch':
        category = 'service'
        name_of_category = 'Услуга'
    else:
        bot.send_message(callback.message.chat.id, "Неизвестная кнопка!")
        start_menu(callback.message)

    # Сохраняем состояние категории для пользователя
    user_state[callback.message.chat.id] = {'category': category, 'page': 0}

    # Получаем объявления по выбранной категории
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()
    cursor.execute("SELECT Title FROM AdvertTable WHERE Category = ?", (category,))
    titles_exec = cursor.fetchall()  # Получаем все записи столбца Title
    titles = [title[0] for title in titles_exec]

    # Проверяем, если не получили заголовков, то возвращаем юзера на выбор категории
    if not titles:
        bot.send_message(callback.message.chat.id, f'В категории {name_of_category} пока что отсутствуют объявления.'
                                                   f'\nПопробуйте выбрать другую.')
        return

    # Создаем клавиатуру
    keyboard = keyboards.create_inline_keyboard(titles, category, 0)
    # Отправляем сообщение с клавиатурой
    bot.send_message(callback.message.chat.id, "Выберите объявление из списка:", reply_markup=keyboard)
    connect.close()


# Обработчик для навигации по страницам
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('page_'))
@check_banned
def pagination_handler(callback):
    # Извлекаем номер страницы и категорию из callback_data
    data = callback.data.split('_')
    category = data[1]
    page = int(data[2])

    # Обновляем состояние пользователя (категория и страница)
    user_state[callback.message.chat.id] = {'category': category, 'page': page}

    print('user_state для pagination_handler:\n', user_state)

    # Подключаемся к базе данных и выполняем запрос
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()
    cursor.execute("SELECT Title FROM AdvertTable WHERE Category = ?", (category,))
    titles_exec = cursor.fetchall()
    titles = [title[0] for title in titles_exec]

    # Создаем клавиатуру с учетом текущей страницы
    keyboard = keyboards.create_inline_keyboard(titles, category, page)

    # Обновляем сообщение с новой клавиатурой
    bot.edit_message_text("Выберите объявление из списка:", chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id, reply_markup=keyboard)

    connect.close()


@bot.callback_query_handler(func=lambda callback: callback.data.count('_') == 1)
@check_banned
def show_advert_detail(callback):
    # Извлекаем категорию и название объявления из callback_data
    category, title = callback.data.split('_', 1)
    printed_category = 'undef'

    if category == 'housing':
        printed_category = 'Жильё'
    elif category == 'product':
        printed_category = 'Товар'
    elif category == 'service':
        printed_category = 'Услуга'

    # Подключаемся к базе данных
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()

    # Выполняем SQL запрос для получения всех данных по выбранному объявлению
    cursor.execute("""
        SELECT UserID, Title, Description, Price, Photos, Authors_username, Date, TelNumber
        FROM AdvertTable 
        WHERE Category = ? AND Title = ?
    """, (category, title))

    advert = cursor.fetchone()

    if advert:
        user_id, title, description, price, photos, username, date, telnum = advert

        if price == 'Бесплатно' or price == 'Договорная':
            # Формируем сообщение с деталями объявления
            message = f"Категория: {printed_category}\n" \
                      f"Название: {title}\n" \
                      f"Описание: {description}\n" \
                      f"Цена: {price}\n" \
                      f"Автор: @{username if username != None else telnum}\n" \
                      f"Дата создания: {date}\n"
        else:
            # Формируем сообщение с деталями объявления
            message = f"Категория: {printed_category}\n" \
                      f"Название: {title}\n" \
                      f"Описание: {description}\n" \
                      f"Цена: {price} BYN\n" \
                      f"Автор: @{username if username != None else telnum}\n" \
                      f"Дата создания: {date}\n"

        # Отправляем фотографии, если они есть
        if photos:
            folder_path = os.path.join('adv_photos_folder', f"{user_id}_{title}")
            # Проверяем существование папки
            if not os.path.exists(folder_path):
                print(f"Папка {folder_path} не существует.")
            else:
                files = os.listdir(folder_path)
                for file in files:
                    full_file_path = os.path.join(folder_path, file)  # Полный путь к файлу

                    if os.path.isfile(full_file_path):  # Проверяем полный путь
                        try:
                            with open(full_file_path, 'rb') as photo:
                                bot.send_photo(callback.message.chat.id, photo)
                        except Exception as e:
                            print(f"Ошибка при отправке фото {file}: {e}")

        else:
            message += "Фото: Нет\n"

        # Отправляем сообщение с подробностями объявления
        kb = types.InlineKeyboardMarkup()
        button_back_to_menu = types.InlineKeyboardButton(text='Вернуться к объявлениями', callback_data='back_to_ads')
        kb.add(button_back_to_menu)
        bot.send_message(callback.message.chat.id, message, reply_markup=kb)

    else:
        bot.send_message(callback.message.chat.id, "Извините, объявление не найдено.")

    connect.close()


@bot.callback_query_handler(func=lambda callback: callback.data == 'back_to_ads')
@check_banned
def back_to_ads(callback):
    # Извлекаем состояние пользователя (категория и страница)
    user_info = user_state.get(callback.message.chat.id)

    if not user_info:
        bot.send_message(callback.message.chat.id, "Возврат невозможен. Попробуйте выбрать категорию снова.")
        return

    category = user_info.get('category')
    page = user_info.get('page', 0)

    # Подключаемся к базе данных для получения списка заголовков объявлений
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()
    cursor.execute("SELECT Title FROM AdvertTable WHERE Category = ?", (category,))
    titles_exec = cursor.fetchall()  # Получаем все записи столбца Title
    titles = [title[0] for title in titles_exec]

    # Создаем клавиатуру с объявлениями для текущей страницы
    keyboard = keyboards.create_inline_keyboard(titles, category, page)

    # Обновляем сообщение с новой клавиатурой
    bot.edit_message_text("Выберите объявление из списка:", chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id, reply_markup=keyboard)

    connect.close()


#######################################################                       MY ADVERTISMENTS

# Хранилище состояния для объявлений пользователя (по chat.id), ключ - значение это userID - page
user_state_my_ads = {}


def watch_my_ads(message):
    # Подключаемся к базе данных
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()

    current_user = message.chat.id  # поменял на id вместо username

    # Сохраняем состояние пользователя для работы с его объявлениями (его id и номер страницы)
    user_state_my_ads[current_user] = {'userID': current_user, 'page': 0}

    # Выполняем SQL запрос для получения всех объявлений с юзернеймом текущего пользователя
    cursor.execute("""
           SELECT Category, Title, Description, Price, Photos 
           FROM AdvertTable 
           WHERE UserID = ?
       """, (current_user,))

    my_ads_exec = cursor.fetchall()  # Получаем все записи с указанным юзернеймом
    my_ads = [my_ad[1] for my_ad in my_ads_exec]

    # Проверяем, если у пользоваиеля нет объявлений, то так и пишем
    if not my_ads:
        bot.send_message(message.chat.id, 'На данный момент у вас нет размещённых объявлений.')
        return

    # Создаем клавиатуру
    keyboard = keyboards.create_inline_keyboard_for_my_ads(my_ads, current_user, 0)
    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Ваши объявления:", reply_markup=keyboard)

    connect.close()


# Обработчик для навигации по страницам
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('my_page_'))
@check_banned
def for_my_ads_pagination_handler(callback):
    # Извлекаем номер страницы и юзер id из callback_data
    data = callback.data.split('_')
    user_id = data[2]
    page = int(data[3])

    # Обновляем состояние пользователя (юзернейм и страница)
    user_state_my_ads[int(user_id)] = {'userID': user_id, 'page': page}

    print('user_state для my_pagination_handler:\n', user_state_my_ads)

    # Подключаемся к базе данных и выполняем запрос
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()
    # Выполняем SQL запрос для получения всех объявлений с юзернеймом текущего пользователя
    cursor.execute("""
               SELECT Category, Title, Description, Price 
               FROM AdvertTable 
               WHERE UserID = ?
           """, (user_id,))

    my_ads_exec = cursor.fetchall()  # Получаем все записи с указанным юзернеймом
    my_ads = [my_ad[1] for my_ad in my_ads_exec]

    # Создаем клавиатуру с учетом текущей страницы
    keyboard = keyboards.create_inline_keyboard_for_my_ads(my_ads, user_id, page)

    # Обновляем сообщение с новой клавиатурой
    bot.edit_message_text("Ваши объявления:", chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id, reply_markup=keyboard)

    connect.close()


@bot.callback_query_handler(func=lambda callback: callback.data.count('_') == 2)
@check_banned
def show_my_advert_detail(callback):
    # Извлекаем user id и название объявления из callback_data
    splitted_callback = callback.data.split('_')
    user_id = splitted_callback[1]
    title = splitted_callback[2]

    # Подключаемся к базе данных
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()

    # Выполняем SQL запрос для получения всех данных по выбранному объявлению
    cursor.execute("""
        SELECT Category, Title, Description, Price, Photos, Date 
        FROM AdvertTable 
        WHERE UserID = ? AND Title = ?
    """, (user_id, title))

    advert = cursor.fetchone()

    if advert:
        category, title, description, price, photos, date = advert
        printed_category = 'undef'
        if category == 'housing':
            printed_category = 'Жильё'
        elif category == 'product':
            printed_category = 'Товар'
        elif category == 'service':
            printed_category = 'Услуга'

        if price == 'Бесплатно' or price == 'Договорная':
            # Формируем сообщение с деталями объявления
            message = f"Категория: {printed_category}\n" \
                      f"Название: {title}\n" \
                      f"Описание: {description}\n" \
                      f"Цена: {price}\n" \
                      f"Дата создания: {date}\n"
        else:
            # Формируем сообщение с деталями объявления
            message = f"Категория: {printed_category}\n" \
                      f"Название: {title}\n" \
                      f"Описание: {description}\n" \
                      f"Цена: {price} BYN\n" \
                      f"Дата создания: {date}\n"

        # Отправляем фотографии, если они есть
        if photos:
            folder_path = os.path.join('adv_photos_folder', f"{user_id}_{title}")
            # Проверяем существование папки
            if not os.path.exists(folder_path):
                print(f"Папка {folder_path} не существует.")
            else:
                files = os.listdir(folder_path)
                for file in files:
                    full_file_path = os.path.join(folder_path, file)  # Полный путь к файлу

                    if os.path.isfile(full_file_path):  # Проверяем полный путь
                        try:
                            with open(full_file_path, 'rb') as photo:
                                bot.send_photo(callback.message.chat.id, photo)
                        except Exception as e:
                            print(f"Ошибка при отправке фото {file}: {e}")

        else:
            message += "Фото: Нет\n"

        bot.send_message(callback.message.chat.id, message, reply_markup=keyboards.my_advert_kb(title, category, price))

    else:
        bot.send_message(callback.message.chat.id, "Извините, объявление не найдено.")

    connect.close()


@bot.callback_query_handler(func=lambda callback: callback.data == 'back_to_my_ads')
@check_banned
def back_to_my_ads(callback):
    # Извлекаем состояние пользователя (категория и страница)
    user_info = user_state_my_ads.get(callback.message.chat.id)
    print(user_info)

    if not user_info:
        bot.send_message(callback.message.chat.id, "Возврат невозможен. Попробуйте выбрать категорию снова.")
        return

    user_id = user_info.get('userID')
    page = user_info.get('page', 0)

    # Подключаемся к базе данных для получения списка заголовков объявлений
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()
    cursor.execute("SELECT Title FROM AdvertTable WHERE UserID = ?", (user_id,))
    my_ads_exec = cursor.fetchall()  # Получаем все записи с указанным юзернеймом
    my_ads = [my_ad[0] for my_ad in my_ads_exec]

    # Создаем клавиатуру с объявлениями для текущей страницы
    keyboard = keyboards.create_inline_keyboard_for_my_ads(my_ads, user_id, page)

    # Обновляем сообщение с новой клавиатурой
    bot.edit_message_text("Ваши объявления:", chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id, reply_markup=keyboard)

    connect.close()


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('delete_'))
@check_banned
def delete_my_ad(callback):
    connect = sqlite3.connect('AdvertDataBase.db')
    cursor = connect.cursor()
    received_callback = callback.data.split('_')

    user_id = 0

    title = received_callback[1]
    category = received_callback[2]
    price = received_callback[3]

    # ПОЛУЧАЕМ USERid АВТОРА ОБЪЯВЛЕНИЯ ПЕРЕД УДАЛЕНИЕМ

    cursor.execute("SELECT UserID FROM AdvertTable WHERE Title = ? AND Category = ? AND Price = ?",
                   (title, category, price))

    user_id_tuple = cursor.fetchone()  # Возвращает кортеж, например (12345,)
    if user_id_tuple:  # Проверяем, что результат не пустой
        user_id = user_id_tuple[0]  # Извлекаем первый элемент
    else:
        print("UserID не найден.")

    # Выполняем SQL запрос для получения всех данных по выбранному объявлению
    cursor.execute("""
            DELETE FROM AdvertTable 
            WHERE Category = ? AND Title = ? AND Price = ?
        """, (category, title, price))

    connect.commit()

    # Путь к папке с фотографиями
    folder_path = os.path.join('adv_photos_folder', f"{user_id}_{title}")

    # Удаление папки с фотографиями, если она существует
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        bot.send_message(callback.message.chat.id, 'Объявление удалено.')
    else:
        bot.send_message(callback.message.chat.id, 'Ошибка удаления, фотографии не найдены!')

    connect.close()


while True:
    try:
        bot.polling(none_stop=True)
        print('bot started')
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)  # Задержка перед повторной попыткой
