import telebot
from telebot import types
import re

bot = telebot.TeleBot('6056246270:AAG_Wyp9uNDSq0O0gz65x8b2SLP1Jzcn7xg')

menu = {
    'Страви': {
        'Вареники': {
            'price': 50,
            'photo': 'photos/varenyk.jpg'  # Шлях до фотографії в папці
        },
        'Деруни': {
            'price': 70,
            'photo': 'photos/deruny.jpg'  # Шлях до фотографії в папці
        },
        'Борщ': {
            'price': 60,
            'photo': 'photos/borshch.jpg'  # Шлях до фотографії в папці
        }
    },
    'Салати': {
        'Салат Цезар': {
            'price': 80,
            'photo': 'photos/salat_cezar.png'  # Шлях до фотографії в папці
        },
        'Олів\'є': {
            'price': 90,
            'photo': 'photos/salat_olive.jpg'  # Шлях до фотографії в папці
        },
        'Салат Айзберг': {
            'price': 75,
            'photo': 'photos/salat_iceberg.jpg'  # Шлях до фотографії в папці
        }
    },
    'Напої': {
        'Кока-Кола': {
            'price': 30,
            'photo': 'photos/photo_koka_cola.jpg'  # Шлях до фотографії в папці
        },
        'Фанта': {
            'price': 30,
            'photo': 'photos/photo_fanta.jpg'  # Шлях до фотографії в папці
        },
        'Соки': {
            'price': 40,
            'photo': 'photos/photo_soki.jpg'  # Шлях до фотографії в папці
        }
    }
}

cart = {}
user_data = {}


# Створення меню категорій
def create_category_menu(category):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    items = menu[category]
    for item in items:
        markup.add(item)
    markup.add('Назад', 'Оформити замовлення', 'Залишити відгук')
    return markup

# Обробка команди /start
@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message)

# Головне меню
@bot.message_handler(func=lambda message: message.text == 'Асортимент')
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=5, resize_keyboard=True)
    markup.add('Страви', 'Салати', 'Напої', 'Оформити замовлення', 'Залишити відгук')
    bot.send_message(message.chat.id, 'Оберіть категорію товару:', reply_markup=markup)

# Обробка команди "Назад"
@bot.message_handler(func=lambda message: message.text == 'Назад')
def go_back(message):
    main_menu(message)

# Обробка вибору категорії товару
@bot.message_handler(func=lambda message: message.text in menu.keys() and message.text != 'Оформити замовлення')
def category_menu(message):
    category = message.text
    markup = create_category_menu(category)

    items = menu[category]
    for item, details in items.items():
        price = details['price']
        photo_path = details['photo']
        with open(photo_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
            bot.send_message(message.chat.id, f'{item} - {price} грн')

    bot.send_message(message.chat.id, 'Оберіть товар:', reply_markup=markup)

# Обробка вибору страви з категорії страв
@bot.message_handler(func=lambda message: message.text in menu['Страви'].keys())
def dish_menu(message):
    dish = message.text
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['item'] = dish
    bot.send_message(user_id, 'Введіть кількість:')
    bot.register_next_step_handler(message, process_quantity)

# Обробка вибору салату з категорії салатів
@bot.message_handler(func=lambda message: message.text in menu['Салати'].keys())
def salad_menu(message):
    salad = message.text
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['item'] = salad
    bot.send_message(user_id, 'Введіть кількість:')
    bot.register_next_step_handler(message, process_quantity)


# Обробка вибору напою з категорії напоїв
@bot.message_handler(func=lambda message: message.text in menu['Напої'].keys())
def drink_menu(message):
    drink = message.text
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['item'] = drink
    bot.send_message(user_id, 'Введіть кількість:')
    bot.register_next_step_handler(message, process_quantity)

# Обробка введеної користувачем кількості товару
def process_quantity(message):
    user_id = message.chat.id
    if user_id not in user_data or 'item' not in user_data[user_id]:
        return

    item = user_data[user_id]['item']

    if item in menu['Страви'].keys():
        category = 'Страви'
    elif item in menu['Салати'].keys():
        category = 'Салати'
    elif item in menu['Напої'].keys():
        category = 'Напої'
    else:
        return

    dish = item
    price = menu[category][dish]['price']

    try:
        quantity = int(message.text)
    except ValueError:
        bot.send_message(user_id, 'Введіть дійсне число для кількості.')
        return

    total_price = price * quantity

    if category not in cart:
        cart[category] = {}

    cart[category][dish] = {
        'price': price,
        'quantity': quantity,
        'total_price': total_price
    }

    bot.send_message(user_id, f'Добавлено {quantity} позиції {dish} в корзину.')

    bot.clear_step_handler_by_chat_id(user_id)

# Обробка команди "Оформити замовлення"
@bot.message_handler(func=lambda message: message.text == 'Оформити замовлення')
def place_order(message):
    user_id = message.chat.id
    if not cart:
        bot.send_message(user_id, 'Ваш кошик порожній.')
        return

    bot.send_message(user_id, 'Будь ласка, введіть своє ім\'я:')
    bot.register_next_step_handler(message, process_name)


# Обробка введеного користувачем імені для оформлення замовлення
def process_name(message):
    user_id = message.chat.id
    name = message.text
    user_data[user_id]['name'] = name

    bot.send_message(user_id, 'Будь ласка, введіть адресу доставки:')
    bot.register_next_step_handler(message, process_address)


# Обробка введеної користувачем адреси для оформлення замовлення
def process_address(message):
    user_id = message.chat.id
    address = message.text
    user_data[user_id]['address'] = address

    bot.send_message(user_id, 'Будь ласка, введіть номер телефону:')
    bot.register_next_step_handler(message, process_phone)


 # Обробка введеного користувачем номера телефону для оформлення замовлення
def process_phone(message):
    user_id = message.chat.id
    phone = message.text

    # Перевірка формату номера телефону (тільки цифри)
    if not re.match(r'^\d{1,12}$', phone):
        bot.send_message(user_id, 'Невірний формат номера телефону. Введіть тільки цифри, не більше 12 символів.')
        bot.send_message(user_id, 'Будь ласка, введіть номер телефону ще раз:')
        bot.register_next_step_handler(message, process_phone)
        return

    user_data[user_id]['phone'] = phone

    order_details = 'Ваше замовлення:\n'
    total_price = 0

    for category, items in cart.items():
        order_details += f'\n{category}:\n'
        for item, details in items.items():
            order_details += f'{item} - {details["quantity"]} шт. - {details["total_price"]} грн\n'
            total_price += details['total_price']

    order_details += f'\nЗагальна сума: {total_price} грн\n\n'
    order_details += f'Ім\'я: {user_data[user_id]["name"]}\n'
    order_details += f'Адреса доставки: {user_data[user_id]["address"]}\n'
    order_details += f'Номер телефону: {user_data[user_id]["phone"]}'

    # Відправка замовлення адміністратору
    admin_chat_id = '5788780546'
    bot.send_message(admin_chat_id, order_details)

    # Очищення кошика
    cart.clear()
    user_data.pop(user_id, None)

    bot.send_message(user_id, 'Дякуємо за ваше замовлення! Ми зв\'яжемося з вами найближчим часом')
    main_menu(message)

# Обробка команди "Залишити відгук"
@bot.message_handler(func=lambda message: message.text == 'Залишити відгук')
def leave_feedback(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Напишіть, будь ласка, відгук про наш сервіс, щоб ми могли вдосконалюватись!')
    bot.register_next_step_handler(message, process_feedback)

# Обробка введеного користувачем відгуку
def process_feedback(message):
    user_id = message.chat.id
    feedback = message.text
    bot.send_message(user_id, 'Дякуємо за відгук! Ваша думка важлива для нас!')

    # Відправка відгука адміністратору
    admin_chat_id = '5788780546'
    bot.send_message(admin_chat_id, f'Відгук від користувача {user_id}:\n{feedback}')

    main_menu(message)

if __name__ == '__main__':
    bot.polling()