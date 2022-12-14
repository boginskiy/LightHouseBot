import os
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram import ReplyKeyboardMarkup, Bot, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import pandas as pd
import logging
import sqlite3
import random
import time

load_dotenv()

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s - %(funcName)s'
BOT_TOKEN = os.getenv('BOT_TOKEN')
MIN_PICTURE = 5335
MAX_PICTURE = 5350


def wake_up(update, context):
    """Старт чат бота. Кнопки управления"""

    chat = update.effective_chat
    bot_name = context.bot['first_name']

    button = [['Загрузить файл']]
    reply_markup = ReplyKeyboardMarkup(
        button, one_time_keyboard=True, resize_keyboard=True)

    context.bot.send_message(chat_id=chat.id,
                             text='{} готов к работе!'.format(bot_name),
                             reply_markup=reply_markup)


def text_click(update, context):
    """Функция обрабатывает текстовые сообщения."""

    chat = update.effective_chat
    full_name = (update.message.chat.first_name + ' ' +
                 update.message.chat.last_name)

    if update.message['text'] == 'Загрузить файл':
        context.bot.send_message(chat_id=chat.id,
                                 text=f'{full_name}, прикрепи файл в формате '
                                      f'xlsx и отправь мне. '
                                      f'Посмотрю, что там у тебя ))')
    else:
        context.bot.send_message(chat_id=chat.id,
                                 text=f'Выбери кнопку "загрузить файл"')


def reed_file_xlsx(user_name, file_name):
    """Функция преобразует xlsx документ в массив данных."""

    xls = pd.ExcelFile(f'temp/@{user_name} {file_name}')
    sheetX = xls.parse(0)
    result_arr = []
    name_columns = [i for i in sheetX]

    for line in range(len(sheetX)):
       delta = []

       for name_column in name_columns:
           delta.append(sheetX[name_column][line])

       result_arr.append(delta)
    return result_arr


def write_file_xlsx_database(result_arr):
    """Функция записывает данные массива в базу данных."""

    conn = sqlite3.connect("db.sqlite3")
    curs = conn.cursor()
    curs.execute("""CREATE TABLE IF NOT EXISTS ParsingData(
                     id INTEGER PRIMARY KEY, 
                     Name TEXT, 
                     URL TEXT, 
                     Xpath TEXT,
                     UNIQUE (Name, URL, Xpath));""")
    for row in result_arr:
        to_db = [row[0], row[1], row[2]]
        try:
            curs.execute("INSERT INTO ParsingData VALUES (NULL, ?, ?, ?);", to_db)
        except sqlite3.IntegrityError:
            pass
    conn.commit()


def download_file_xlsx(update, context):
    """Функция забирает xlsx документ с сервера."""

    file_name = update.message.document.file_name
    user_name = update.message.chat.username
    file_id = update.message.document.file_id

    new_file = context.bot.get_file(file_id)
    new_file.download(f'temp/@{user_name} {file_name}')
    return user_name, file_name


def format_data_list(arr):
    """Функция преобразует данные массива к строке."""

    result = ''
    for line in arr:
        result += '  '.join(line) + '\n\n'
    return result


def send_message(update, context, massage):
    """Функция отправки сообщений в Telegram чат."""

    chat = update.effective_chat
    for i in massage:
        context.bot.send_message(chat_id=chat.id, text=massage[i])
        time.sleep(2)

    context.bot.send_photo(
        chat_id=chat.id, photo=open(
            f'pictures/IMG_{random.randint(MIN_PICTURE, MAX_PICTURE)}.jpg', 'rb'))


def main_handler_file_xlsx(update, context):
    """Главная функция, обрабатывающая xlsx документ."""

    user_name, file_name = download_file_xlsx(update, context)
    array_data = reed_file_xlsx(user_name, file_name)
    write_file_xlsx_database(array_data)
    answer_text = format_data_list(array_data)

    massage = {1: 'Взгляни на обработанные данные:',
               2: answer_text,
               3: 'Картинка для настроения :)'}

    send_message(update, context, massage)


def check_tokens():
    """Проверка доступности переменных окружения."""
    return BOT_TOKEN


def main():
    """Основная логика работы бота."""

    if not check_tokens():
        # logger.critical('Ошибка переменных окружения')
        raise Exception(
            'Ошибка переменных окружения, проверить содержание файла .env')

    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', wake_up)
    dispatcher.add_handler(start_handler)

    # xlsx_handler = MessageHandler(Filters.document.file_extension("xlsx"), main_handler_file_xlsx)
    # dispatcher.add_handler(xlsx_handler)

    # message_handler = MessageHandler(Filters.text, text_click)
    # dispatcher.add_handler(message_handler)

    updater.start_polling(poll_interval=5)
    updater.idle()


if __name__ == '__main__':
    main()






# -----------------------------------------------

# result_arr = reed_file_xlsx('boginskiy_di', 'test.xlsx')
# print(result_arr)
# write_file_xlsx_database(result_arr)


# src = filepath + message.photo[0].file_id

# context.bot.send_document(chat_id=chat.id,
    #                       document=open('tests/test.xlsx', 'rb'))

# chat_id 5157087725 - Скучковская Скучкова
# мой чат id 5339853954
# API бот 5879460590:AAFAfXYX84VM4x-ze2LrSWiMXB9Oi84ELPQ
# библиотеке python-telegram-bot

# bot = Bot(token='5879460590:AAFAfXYX84VM4x-ze2LrSWiMXB9Oi84ELPQ')
# chat_id = 5339853954
# text = "Что-то пришло!"
# bot.send_message(chat_id, text)