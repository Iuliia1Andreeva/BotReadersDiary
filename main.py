import config
import sqlite3
import telebot
import os
from telebot import types
import pandas as pd
import random as rd
import numpy as np

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет! Хочешь поговорить на книжные темы?)"):
    keyboard_start = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Рассказать о книге')
    itembtn3 = types.KeyboardButton('Посмотреть запись о книге')
    itembtn4 = types.KeyboardButton("Найти новую книгу")
    itembtn5 = types.KeyboardButton('Пока все!')
    itembtn6 = types.KeyboardButton('Удалить запись о книге')
    keyboard_start.add(itembtn1, itembtn4)
    keyboard_start.add(itembtn3, itembtn6)
    keyboard_start.add(itembtn5)
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard_start)
    bot.register_next_step_handler(msg, callback_worker)


def boolKeaboard(message, text="Не хотел бы ты помочь другим читателям и предоставить свой отзыв по прочитанной книге в общественный доступ"):
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    btn1 = "Да"
    btn2 = "Нет"
    keyboard.add(btn1, btn2)
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker)


def add_impression(msg):
    with sqlite3.connect('books.db') as con:
        user_message = msg.text
        name_and_author = ''
        impression = ''
        key = 0
        id = msg.from_user.id
        for i in range(len(user_message)):
            if user_message[i] == ")":
                key = i
            if key == 0 and user_message[i] != "(" and user_message[i] != ')':
                name_and_author += user_message[i]
            elif user_message[i] != ")" and user_message[i] != '(':
                impression += user_message[i]
        try:
            cursor = con.cursor()
            table_of_books = f'SELECT * from books WHERE user_id={id}'
            cursor.execute(table_of_books)
            table_of_books_pd = pd.DataFrame(cursor.fetchall())
            read_books = table_of_books_pd[2].tolist()
            if name_and_author in read_books:
                file = open('name_of_authorANDrewiew.txt', 'w')
                file.write(name_and_author + '\n')
                file.write(impression)
                send_keyboard_4(msg)
            else:
                print(read_books)
                cursor.execute('INSERT INTO books (user_id, book, IMPRESSION, ReadUnread) VALUES (?, ?, ?, ?)',
                               (msg.from_user.id, name_and_author, impression, "READ"))
                con.commit()
                file = open('name_of_authorANDrewiew.txt', 'w')
                file.write(name_and_author + '\n')
                file.write(impression)
                bot.send_message(msg.chat.id, 'Очень интересный рассказ! Буду знать больше про эту книгу:)')
                boolKeaboard(msg)
                print('a')
                #bot.register_next_step_handler(msg, callback_worker)
        except:
            cursor.execute('INSERT INTO books (user_id, book, IMPRESSION, ReadUnread) VALUES (?, ?, ?, ?)',
                           (msg.from_user.id, name_and_author, impression, "READ"))
            con.commit()
            file = open('name_of_authorANDrewiew.txt', 'w')
            file.write(name_and_author + '\n')
            file.write(impression)
            bot.send_message(msg.chat.id, 'Очень интересный рассказ! Буду знать больше про эту книгу:)')
            boolKeaboard(msg)
            print('b')
            #bot.register_next_step_handler(msg, callback_worker)


@bot.message_handler(content_types=["document"])
def handle_docs_photo(message):
    try:
        file_photo = bot.get_file(message.photo[-1].file_id)
        file_path, file_extention = os.path.splitext(file_photo.file_path)
        downloaded_file_photo = bot.download_file(file_photo.file_path)
        src = 'documents/' + message.photo[-1].file_id + file_extention
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file_photo)
        bot.send_sticker(message.from_user.id, 'CAACAgIAAxkBAAECsEFhCrGA9y62sL6fP-a_ct7x5wZeIAACMAADuckUBSuSE1tTBFNbIAQ')
        bot.send_message(message.from_user.id, 'Прекрасно, добавляю в базу данных!')
        file = open('name_of_authorANDrewiew.txt', 'r')
        a = 0
        for i in file:
            if a == 0:
                nameAndAuthor = i
                print(nameAndAuthor)
            if a == 1:
                impression = i
                print(impression)
            a += 1
        print(nameAndAuthor, impression)
        file.close()
        file = open('name_of_authorANDrewiew.txt', 'w')
        file.close()
        genre = 'Главные книги отдела'
        adveses = pd.read_csv('BookData.csv')
        new = pd.DataFrame(np.array([[nameAndAuthor, impression, src, '', genre, 'UNREAD']]), columns=['list_of_book_names', 'list_of_books_descriptions', 'list_of_books_images',
                                                                                     'list_of_book_hrefs', 'list_of_books_genres', 'read/unread'])
        adveses = adveses.append(new)
        adveses = adveses.reset_index()
        print(adveses['list_of_book_names'])
        adveses.to_csv('BookData.csv')
        send_keyboard(message, text='Чем еще могу помочь?')
    except:
        bot.send_message(message.from_user.id, 'Что-то пошло не так, отправьте другой файл')


def add(msg):
    # print(msg)
    file = open('name_of_authorANDrewiew.txt', 'r')
    a = 0
    for i in file:
        if a == 0:
            nameAndAuthor = i[:-1]
        if a == 1:
            impression = i
        a += 1
    file.close()
    # print(nameAndAuthor)
    with sqlite3.connect('books.db') as con:
        cursor = con.cursor()
        id = msg.from_user.id
        # print(id)
        cursor.execute(f'SELECT IMPRESSION FROM books WHERE user_id=? AND book=?', (id, nameAndAuthor))
        DB = pd.DataFrame(cursor.fetchall())
        currentImpression = DB[0].tolist()[0]
        impression += currentImpression
        cursor.execute(f'UPDATE books SET IMPRESSION=? WHERE user_id=? AND book=?', (impression, id, nameAndAuthor))
        #send_keyboard(msg, "Чем еще могу помочь?")
    print("Все получилось")
    boolKeaboard(msg)
    print('c')


def rewrite(msg):
    file = open('name_of_authorANDrewiew.txt', 'r')
    a = 0
    for i in file:
        if a == 0:
            nameAndAuthor = i[:-1]
        if a == 1:
            impression = i
        a += 1
    file.close()
    # print(nameAndAuthor)
    with sqlite3.connect('books.db') as con:
        cursor = con.cursor()
        id = msg.from_user.id
        # print(id)
        cursor.execute(f'UPDATE books SET IMPRESSION=? WHERE user_id=? AND book=?', (impression, id, nameAndAuthor))
        cursor.execute(f'SELECT * FROM books WHERE user_id={id} AND book=?', (nameAndAuthor,))
        DB = pd.DataFrame(cursor.fetchall())
        print(DB)
    # print("Все получилось")
    boolKeaboard(msg)


def delete(msg):
    nameAndAuthor = msg.text
    id = msg.from_user.id
    with sqlite3.connect('books.db') as con:
        try:
            cursor = con.cursor()
            cursor.execute(f'SELECT * FROM books WHERE user_id=={id} AND book=?', (nameAndAuthor,))
            print(pd.DataFrame(cursor.fetchall())[0])
            cursor.execute(f'DELETE FROM books WHERE user_id=={id} AND book=?', (nameAndAuthor,))
            send_keyboard(msg, "Успешно удалено. Чем еще могу помочь?")
        except:
            send_keyboard(msg, 'Кажется, такой книги нет. Посмотрите список прочитанных книг и рецензий к ним')


def send_keyboard_3(message, text="Выбери жанр)"):
    stickers = ['CAACAgIAAxkBAAECsLdhCv2MiJxHogEdmXReyBDxdanaYQACNgADuckUBUtjiHPFOrLlIAQ', 'CAACAgIAAxkBAAECsLlhCv2T84GdkNEhWvWFCAQHbiwlFQACNAADuckUBf3Xa4sz0PmlIAQ',
                'CAACAgIAAxkBAAECsLthCv2WkjwPVpIScx8YsEUfcFCQ4QACTwADuckUBfgyMI_CGDtiIAQ',
                'CAACAgIAAxkBAAECsL9hCv2eO_6oKX7kEaaPxmCtUJ8FmAACLgADuckUBWfYOWYOsSSKIAQ', 'CAACAgIAAxkBAAECsSphC7StJm95dZMoIpNn6Uh_dCsBtQACSwADuckUBSIpdYZnu9mTIAQ',
                'CAACAgIAAxkBAAECsS5hC7UB7AQBCoHgqzKsTlEjfHj8hAACRQADuckUBVKBVFo9MTfAIAQ']
    number = rd.randint(0,  5)
    bot.send_sticker(message.chat.id, stickers[number])
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


def send_keyboard_4(message,
                    text="Похоже Вы уже читали эту книгу. Вы хотите дополнить свою рецензию или перезаписать?)"):
    keyboard_start_4 = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('Дополнить')
    itembtn3 = types.KeyboardButton('Перезаписать')
    keyboard_start_4.add(itembtn1, itembtn3)
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard_start_4)
    bot.register_next_step_handler(msg, callback_worker)


def find_new(msg):
    user_message = msg.text
    id = msg.from_user.id
    pd.set_option('display.max_colwidth', 100000)
    BookData = pd.read_csv('BookData.csv')
    genre = BookData.loc[BookData['list_of_books_genres'] == user_message]
    genre = genre.loc[genre['read/unread'] == "UNREAD"].reset_index(drop=True)
    Size = genre.shape[0]
    number = rd.randint(0, Size - 1)
    srez = genre.iloc[[number], :]
    with sqlite3.connect('books.db') as con:
        cursor = con.cursor()
        cursor.execute(f'SELECT * FROM books WHERE user_id={id}')
        #print(pd.DataFrame(cursor.fetchall())[2])
    name = srez['list_of_book_names'].tolist()[0]
    print(name)
    description = str(srez['list_of_books_descriptions'].tolist()[0])
    image = srez['list_of_books_images'].tolist()[0]
    href = 'https://www.labirint.ru' + srez['list_of_book_hrefs']
    if 'documents' in image:
        bot.send_photo(msg.chat.id, open(image, 'rb'))
    else:
        bot.send_photo(msg.chat.id, image)
    if description is None or description == 'nan':
        answer = '<b>' + name + '</b>' + '\n' + href
    elif str(srez['list_of_book_hrefs'].tolist()[0]) == 'nan':
        answer = '<b>' + name + '</b>' + '\n' + description + '\n'
    else:
        description = description.replace('<p>', '')
        description = description.replace('<br', "")
        description = description.replace("</p>", '')
        description = description.replace('<br/', '')
        description = description.replace('/>', '')
        answer = '<b>' + name + '</b>' + '\n' + description + '\n' + href
    bot.send_message(msg.chat.id, answer, parse_mode='HTML')
    bot.send_sticker(msg.chat.id, 'CAACAgIAAxkBAAECsAlhCoLJSxkdXmdoE2uwfRxsYow87QACEQADuckUBQbHsrdmH3ouIAQ')
    send_keyboard(msg, "Что-то еще интересное про книжки?")


def get_impression_string(impr):
    impr_str = []
    for val in list(enumerate(impr)):
        impr_str.append('<b>' + str(val[1][2]) + '</b>' + ': ' + str(val[1][4]) + '\n')
    return ''.join(impr_str)


def show_impressions(msg):
    try:
        with sqlite3.connect('books.db') as con:
            cursor = con.cursor()
            e = f'SELECT * FROM books WHERE user_id={msg.from_user.id}'
            cursor.execute(e)
            tasks = get_impression_string(cursor.fetchall())
            bot.send_message(msg.chat.id, tasks, parse_mode='HTML')
            bot.send_sticker(msg.chat.id,
                             'CAACAgIAAxkBAAECsAlhCoLJSxkdXmdoE2uwfRxsYow87QACEQADuckUBQbHsrdmH3ouIAQ')
            send_keyboard(msg, "Чем еще могу помочь?")
    except:
        send_keyboard(msg, 'Кажется, тут пусто, хочешь найти что почитать? Тогда выбери Найти новую книгу')
        bot.send_sticker(msg.from_user.id,
                         'CAACAgIAAxkBAAECr_dhCnmJ78rYOpF7OtZ-jPJcrrRoIwACUQADuckUBfjOOzqvotGpIAQ')


def callback_worker(call):
    if call.text == "Рассказать о книге":
        msg = bot.send_message(call.chat.id,
                               'Давай обсудим твои впечатления о книге! Напиши название книги и свое впечатление в следующем формате: \n(Автор - Название.)  Впечатления о книге')
        bot.register_next_step_handler(msg, add_impression)

    elif call.text == "Найти новую книгу":
        msg = bot.send_message(call.chat.id, 'Процесс выполняется, расскажите, как ваше настроение?')
        bot.register_next_step_handler(msg, send_keyboard_3)

    elif call.text == "Посмотреть запись о книге":
        show_impressions(call)

    elif call.text == "Пока все!":
        bot.send_message(call.chat.id, 'Хорошего дня! Когда захотите продолжнить нажмите на команду /start')
        bot.send_sticker(call.chat.id, 'CAACAgIAAxkBAAECsAdhCoK3tDTk0PG05UKx1n6O-eo9cQACOAADuckUBVDrjOKJyS8KIAQ')

    elif call.text == "Дополнить":
        # print(call)
        bot.send_sticker(call.from_user.id, 'CAACAgIAAxkBAAECruFhCaWdGEmFFESzP7T1RRMgs4mMKwACIQADuckUBeDxc-802m99IAQ')
        ms = bot.send_message(call.from_user.id, 'Записываю! Какую книгу планируете читать сейчас?)')
        bot.register_next_step_handler(ms, add)

    elif call.text == "Перезаписать":
        bot.send_sticker(call.from_user.id, 'CAACAgIAAxkBAAECr8dhCmmNOhhDSDKK939AEnfVY0Uu2gACLAADuckUBZNB-VhNoa7-IAQ')
        ms = bot.send_message(call.from_user.id, 'Записываю! Какую книгу планируете читать сейчас?)')
        bot.register_next_step_handler(ms, rewrite)

    elif call.text == 'Удалить запись о книге':
        msg = bot.send_message(call.from_user.id, 'Какую книгу удаляем? Напишите в следующем формате: Название, автор')
        bot.register_next_step_handler(msg, delete)

    elif call.text == "Да":
        msg = bot.send_message(call.from_user.id, 'Давай немного поработаем над внешним видом, отправь фотографию твоей книги')
        bot.register_next_step_handler(msg, handle_docs_photo)

    elif call.text == "Нет":
        file = open('name_of_authorANDrewiew.txt', 'w')
        file.close()
        send_keyboard(call.from_user.id, 'Чем я еще могу Вам помочь?')

    else:
        bot.send_message(call.from_user.id, 'Не совсем понимаю, начните сначала /start')


if __name__ == '__main__':
    bot.infinity_polling()
