from env import config
from task import help_to_user, help_to_admin
import telebot
import random
from telebot import types
import datetime

bot = telebot.TeleBot(config.bot_token)

id_channel_chat = -1001546732017

user_dict = {}

result_update = []

class User:
    def __init__(self, full_name):
        self.full_name = full_name
        user = ['phone', 'date', 'time', 'sketch', 'nickname', 'reg_time']

        for key in user:
            self.key = None


def rand_tattoo():
    index = random.randint(1, 5)
    img = open(f'images/{str(index)}.jpg', 'rb')
    return img


@bot.message_handler(commands=['update', 'up']) #/update
def update(message):
    if message.chat.id != id_channel_chat:
        bot.send_message(message.chat.id, 'Упс, это Вам не доступно')
    else:
        msg = bot.send_message(id_channel_chat, 'Введите свободные для записи даты на данный момент, ЧЕРЕЗ ПРОБЕЛ, в формате ДД.ММ\nНапример: 01.02 02.02 03.02')
        bot.register_next_step_handler(msg, update_step)

@bot.message_handler(commands=['delete']) #/delete
def delete(message):
    if message.chat.id != id_channel_chat:
        bot.send_message(message.chat.id, 'Упс, это Вам не доступно')
    else:
        del_data = bot.send_message(id_channel_chat, f'Доступные даты: {result_update}\nВведите дату которую нужно удалить, только одну\nНапример: 01.02\n\nЕсли нужно очистьить весть список напишите в сообщении слово "ОЧИСТИТЬ"')
        bot.register_next_step_handler(del_data, del_step_data)

@bot.message_handler(commands=['randoms']) #/randoms
def randoms(message):
    bot.send_photo(message.chat.id, rand_tattoo())

@bot.message_handler(commands=['start']) #/start
def start(message):
    keybord = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.InlineKeyboardButton(text='Запись на сеанс', callback_data='seans')
    btn2 = types.InlineKeyboardButton(text='Рандомное тату', callback_data='randoms')
    btn3 = types.InlineKeyboardButton(text='Справка', callback_data='spr')
    keybord.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!', reply_markup=keybord)

@bot.message_handler(commands=['help']) #/help
def help(message):
    if message.chat.id == id_channel_chat:
        bot.send_message(id_channel_chat, help_to_admin)
    else:
        bot.send_message(message.chat.id, help_to_user)

@bot.message_handler(content_types=['text'])
def callbeck(message):
    if message.text == 'Запись на сеанс':
        global keybord_start
        keybord_start = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.InlineKeyboardButton(text='Хочу записаться')
        btn2 = types.InlineKeyboardButton(text='Хочу посмотреть свою запись')
        keybord_start.add(btn1, btn2)
        bot.send_message(message.chat.id, 'Вы хотите записаться или посмотреть на сколько записаны?', reply_markup=keybord_start)

    elif message.text == 'Рандомное тату':
        bot.send_photo(message.chat.id, rand_tattoo())

    elif message.text == 'Справка':
        bot.send_message(message.chat.id, help_to_user)

    if message.text == 'Хочу посмотреть свою запись':
        rec = user_dict.get(message.from_user.id)
        if rec == None:
            bot.send_message(message.chat.id, 'Данные не найдены, возможно Вы еще не записаны :(')
        else:
            chat_id = message.chat.id
            user = user_dict[chat_id]
            title = f'''
    ФИО: {user.full_name}
    Телефон: {user.phone}
    Дата: {user.date}
    Уточнение времени: {user.time}
    Ссылка на эскиз: {user.sketch}
    Время составления заявки: {user.reg_time}'''

            keybord = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.InlineKeyboardButton(text='Запись на сеанс', callback_data='seans')
            btn2 = types.InlineKeyboardButton(text='Рандомное тату', callback_data='randoms')
            btn3 = types.InlineKeyboardButton(text='Справка', callback_data='spr')
            keybord.add(btn1, btn2, btn3)

            bot.send_message(message.chat.id, f'Данные по Вашей записи: {title}', reply_markup=keybord)

    elif message.text == 'Хочу записаться':
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(message.chat.id, 'Введите свое ФИО', reply_markup=markup)
        bot.register_next_step_handler(msg, reg_fio_step)

def reg_fio_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = User(message.text)
        print(user_dict[chat_id].full_name)

        msg = bot.send_message(message.chat.id, 'Введите свой номер телефона.')
        bot.register_next_step_handler(msg, reg_phone_step)

    except Exception:
        bot.reply_to(message, 'oops!')

def reg_phone_step(message):
    try:
        int(message.text)

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.phone = message.text
        user.reg_time = datetime.datetime.now()
        print(user_dict[chat_id].phone)

        #Динамическая подгрузка кнопок
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

        for i in range(0, len(result_update)):
            keyboard.add(types.InlineKeyboardButton(text=result_update[i]))
        msg = bot.send_message(message.chat.id, 'Дата сеанса. Выбирайте из меню.', reply_markup=keyboard)
        bot.register_next_step_handler(msg, reg_date_step)

    except Exception:
        msg = bot.reply_to(message, 'Вы ввели что то другое, введите номер телефона заново')
        bot.register_next_step_handler(msg, reg_phone_step)

def reg_date_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.date = message.text
        print(user_dict[chat_id].date)

        markup2 = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(message.chat.id, 'Для уточнения времени с Вами свяжутся в Telegram, если согласны - напишите "ок", если нет - подскажите куда Вам написать.', reply_markup=markup2)
        bot.register_next_step_handler(msg, reg_time_step)
    except Exception:
        bot.reply_to(message, 'oops!')

def reg_time_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.time = message.text
        user.nickname = message.from_user.username
        print(user_dict[chat_id].time)
        print(user_dict[chat_id].nickname)

        msg = bot.send_message(message.chat.id, 'Пришлите ссылку на эскиз')
        bot.register_next_step_handler(msg, reg_sketch_step)
    except Exception:
        bot.reply_to(message, 'oops!')

def reg_sketch_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.sketch = message.text
        print(user_dict[chat_id].sketch)

        title = f'''
ФИО: {user.full_name}
Телефон: {user.phone}
Дата: {user.date}
Уточнение времени: {user.time}
Ссылка на эскиз: {user.sketch}
Время составления заявки: {user.reg_time}'''

        keybord = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.InlineKeyboardButton(text='Запись на сеанс', callback_data='seans')
        btn2 = types.InlineKeyboardButton(text='Рандомное тату', callback_data='randoms')
        btn3 = types.InlineKeyboardButton(text='Справка', callback_data='spr')
        keybord.add(btn1, btn2, btn3)

        bot.send_message(message.chat.id, f'Ваша заявка принята!\n{title}', reply_markup=keybord)

        #Отсылаем готовую заявку в канал с мастером
        bot.send_message(id_channel_chat, f'Появилась новая запись:\n{title}\nТелеграм: @{user_dict[chat_id].nickname}')

    except Exception as e:
        bot.reply_to(message, f'oops! {e}')


def update_step(message):
    '''Получение списка дат, сортировка и исключение повтарений'''
    try:
        data_session = list(set(message.text.split()))
        ind_val = []

        for i, j in enumerate(data_session):
            ind_val.append((int(j[:2]), i))

        for item in sorted(ind_val):
            result_update.append(data_session[item[1]])
        bot.send_message(id_channel_chat, 'Данные успешно внесены')
    except Exception:
        bot.send_message(id_channel_chat, 'Что то введено не так, давай по новой')

def del_step_data(message):
    '''Редактирование списка дат для записи'''
    try:
        if message.text == 'ОЧИСТИТЬ':
            result_update.clear()
            bot.reply_to(message, f'Готово! Список дат пустой.\nДоказательство: {result_update}')
        elif message.text == 'отмена':
            pass
        else:
            try:
                result_update.remove(message.text)
                bot.send_message(id_channel_chat, f'Дата {message.text} удалена. Остались даты {result_update}')
            except Exception:
                bot.reply_to(message, 'Видимо такой даты нет в списке или она введена не правильно. Нужно повторить удаление заново')
    except Exception:
        bot.reply_to(message, 'Что то пошло не так')

bot.polling()