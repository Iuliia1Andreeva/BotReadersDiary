import config
import sqlite3
import telebot
from telebot import types
import pandas as pd
import random as rd

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет, хочешь поговорить на книжные темы?)"):
    keyboard_start = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Рассказать о книге')
    itembtn3 = types.KeyboardButton('Посмотреть запись о книге')
    itembtn4 = types.KeyboardButton("Найти новую книгу")
    itembtn5 = types.KeyboardButton('Пока все!')
    keyboard_start.add(itembtn1, itembtn4)
    keyboard_start.add(itembtn3)
    keyboard_start.add(itembtn5)

    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard_start)
    bot.register_next_step_handler(msg, callback_worker)


def add_impression(msg):
    with sqlite3.connect('books.db') as con:
        user_message = msg.text
        name_and_author = ''
        impression = ''
        key = 0
        for i in range(len(user_message)):
            if user_message[i] == ")":
                key = i
            if key == 0 and user_message[i] != "(" and user_message[i] != ')':
                name_and_author += user_message[i]
            elif user_message[i] != ")" and user_message[i] != '(':
                impression += user_message[i]
        cursor = con.cursor()
        cursor.execute('INSERT INTO books (user_id, book, IMPRESSION, ReadUnread) VALUES (?, ?, ?, ?)',
                       (msg.from_user.id, name_and_author, impression, "READ"))
        con.commit()
    bot.send_message(msg.chat.id, 'Очень интересный рассказ! Буду знать больше про эту книгу:)')
    send_keyboard(msg, "Что-то еще интересное про книжки?")


def send_keyboard_3(message, text="Выбери жанр)"):
    bot.send_message(message.chat.id, 'Отлично)(')
    keyboard_start_3 = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Бизнес. Экономика')
    itembtn3 = types.KeyboardButton('Естественные науки')
    itembtn4 = types.KeyboardButton("Книги для родителей")
    itembtn5 = types.KeyboardButton('Кулинария')
    itembtn6 = types.KeyboardButton('Медицина и здоровье')
    itembtn7 = types.KeyboardButton('Психология')
    itembtn8 = types.KeyboardButton('Публицистика')
    itembtn9 = types.KeyboardButton('Главные книги отдела')
    keyboard_start_3.add(itembtn1, itembtn3, itembtn4)
    keyboard_start_3.add(itembtn5, itembtn6, itembtn7)
    keyboard_start_3.add(itembtn8, itembtn9)
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard_start_3)
    bot.register_next_step_handler(msg, find_new)


def find_new(msg):
    user_message = msg.text
    pd.set_option('display.max_colwidth', 100000)
    BookData = pd.read_csv('BookData.csv')
    genre = BookData.loc[BookData['list_of_books_genres'] == user_message]
    Size = genre.shape[1]
    number = rd.randint(0, Size)
    srez = genre.iloc[[number], :]
    name = srez['list_of_book_names']
    description = str(srez['list_of_books_descriptions'].tolist()[0])
    image = srez['list_of_books_images'].tolist()[0]
    href = 'https://www.labirint.ru' + srez['list_of_book_hrefs']
    print(image)
    print(description)
    bot.send_photo(msg.chat.id, image)
    if description is None or description == 'nan':
        answer = name + '\n' + href
    else:
        description = description.replace('<p>', '')
        description = description.replace('<br', "")
        description = description.replace("</p>", '')
        description = description.replace('<br/', '')
        description = description.replace('/>', '')
        print(description)
        answer = name + '\n' + description + '\n' + href
    bot.send_message(msg.chat.id, answer)

    send_keyboard(msg, "Что-то еще интересное про книжки?")


def get_impression_string(impr):
    impr_str = []
    for val in list(enumerate(impr)):
        impr_str.append(str(val[1][2]) + '-' + str(val[1][4]) + '\n')
    return ''.join(impr_str)


def show_impressions(msg):
    print("We are here")
    with sqlite3.connect('books.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT * FROM books WHERE user_id=={}'.format(msg.from_user.id))
        tasks = get_impression_string(cursor.fetchall())
        bot.send_message(msg.chat.id, tasks)
        send_keyboard(msg, "Чем еще могу помочь?")


def callback_worker(call):
    if call.text == "Рассказать о книге":
        msg = bot.send_message(call.chat.id,
                               'Давай обсудим твои впечатления о книге! Напиши название книги и свое впечатление в следующем формате: \n (Название, автор)  Впечатления о книге')
        bot.register_next_step_handler(msg, add_impression)

    elif call.text == "Найти новую книгу":
        msg = bot.send_message(call.chat.id, 'Процесс выполняется, как ваше настроение?')
        bot.register_next_step_handler(msg, send_keyboard_3)

    elif call.text == "Посмотреть запись о книге":
        show_impressions(call)

    elif call.text == "Пока все!":
        bot.send_message(call.chat.id, 'Хорошего дня! Когда захотите продолжнить нажмите на команду /start')


if __name__ == '__main__':
    bot.infinity_polling()
