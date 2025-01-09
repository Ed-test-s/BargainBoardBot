from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def help_kb():
    # Создаем inline-кнопку для команды /help
    markup = types.InlineKeyboardMarkup()
    help_button = types.InlineKeyboardButton(text="Помощь", callback_data="help")
    markup.add(help_button)
    return markup


def main_menu_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_add_advert = types.KeyboardButton('🖊️ Подать объявление')
    btn_watch_advert = types.KeyboardButton('👀 Смотреть объявления')
    btn_my_advert = types.KeyboardButton('📂 Мои объявления')
    kb.add(btn_add_advert, btn_watch_advert, btn_my_advert)
    return kb


def create_username_kb():
    inline_kb = types.InlineKeyboardMarkup()
    btn_username = types.InlineKeyboardButton("Создать username телеграм", url="tg://settings")
    inline_kb.add(btn_username)
    return inline_kb


def get_telnum_kb():
    # Создаём Reply клавиатуру для номера телефона
    reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_number = types.KeyboardButton('Предоставить номер телефона', request_contact=True)
    reply_kb.add(btn_number)
    return reply_kb


def select_category_for_create_advert_kb():
    kb = types.InlineKeyboardMarkup()
    btn_housing = types.InlineKeyboardButton(text='🏠 Жильё', callback_data='housing_create')
    btn_product = types.InlineKeyboardButton(text='🛍️ Товар', callback_data='product_create')
    btn_service = types.InlineKeyboardButton(text='📞 Услуга', callback_data='service_create')
    kb.add(btn_housing, btn_product, btn_service)
    return kb


def select_category_for_watch_advert_kb():
    kb = types.InlineKeyboardMarkup()
    btn_housing = types.InlineKeyboardButton(text='🏠 Жильё', callback_data='housing_watch')
    btn_product = types.InlineKeyboardButton(text='🛍️ Товар', callback_data='product_watch')
    btn_service = types.InlineKeyboardButton(text='📞 Услуга', callback_data='service_watch')
    kb.add(btn_housing, btn_product, btn_service)
    return kb


def price_kb():
    # Создаем клавиатуру для цены
    price_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    price_keyboard.add(KeyboardButton("Договорная"), KeyboardButton("Бесплатно"))
    return price_keyboard


def my_advert_kb(title, category, price):
    # Отправляем сообщение с подробностями объявления
    kb = types.InlineKeyboardMarkup()
    button_back_to_my_menu = types.InlineKeyboardButton(text='Вернуться к объявлениями',
                                                        callback_data='back_to_my_ads')
    delete_ad_button = types.InlineKeyboardButton(text='Удалить объявление',
                                                  callback_data=f'delete_{title}_{category}_{price}')
    kb.add(button_back_to_my_menu, delete_ad_button)
    return kb


# Функция для создания клавиатуры с кнопками
def create_inline_keyboard_for_my_ads(my_ads, current_user, page=0):
    buttons_per_page = 5
    start_index = page * buttons_per_page
    end_index = start_index + buttons_per_page
    page_ads = my_ads[start_index:end_index]

    keyboard = []

    # Добавляем кнопки с названиями
    for ad in page_ads:
        keyboard.append([types.InlineKeyboardButton(ad, callback_data=f'my_{current_user}_{ad}')])
        # ad это Title объявления из списка тайтлов, которые влазят на этой странице

    # Добавляем кнопки для навигации
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            types.InlineKeyboardButton('◀️ Назад', callback_data=f'my_page_{current_user}_{page - 1}'))
    if end_index < len(my_ads):
        navigation_buttons.append(
            types.InlineKeyboardButton('Вперед ▶️', callback_data=f'my_page_{current_user}_{page + 1}'))

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    return types.InlineKeyboardMarkup(keyboard)


# Функция для создания клавиатуры с кнопками
def create_inline_keyboard(titles, category, page=0):
    buttons_per_page = 5
    start_index = page * buttons_per_page
    end_index = start_index + buttons_per_page
    page_titles = titles[start_index:end_index]

    keyboard = []

    # Добавляем кнопки с названиями
    for title in page_titles:
        keyboard.append([types.InlineKeyboardButton(title, callback_data=f'{category}_{title}')])

    # Добавляем кнопки для навигации
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(types.InlineKeyboardButton('◀️ Назад', callback_data=f'page_{category}_{page - 1}'))
    if end_index < len(titles):
        navigation_buttons.append(types.InlineKeyboardButton('Вперед ▶️', callback_data=f'page_{category}_{page + 1}'))

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    return types.InlineKeyboardMarkup(keyboard)
