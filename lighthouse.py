import os
import sys
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
import pandas as pd
import logging
from logging import FileHandler, StreamHandler
import sqlite3
import random
import time

load_dotenv()

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s - %(funcName)s'
BOT_TOKEN = os.getenv('BOT_TOKEN')
ID_ADMIN = os.getenv('ID_ADMIN')
MIN_PICTURE = 5335
MAX_PICTURE = 5350


def massage_error(context, tx_err):
    context.bot.send_message(chat_id=ID_ADMIN, text=tx_err)


def wake_up(update, context):
    """Отправка приветствия в Telegram чат. +Кнопка."""

    chat = update.effective_chat
    bot_name = context.bot.first_name

    button = [['загрузить файл']]
    re_mar = ReplyKeyboardMarkup(
        button, one_time_keyboard=True, resize_keyboard=True)
    tx = '{} готов к работе!'.format(bot_name)

    try:
        context.bot.send_message(chat_id=chat.id, text=tx, reply_markup=re_mar)
    except Exception:
        tx_err = 'Ошибка отправки приветственного сообщения'
        logger.error(tx_err)
        massage_error(context, tx_err)
        raise Exception(tx_err)
    finally:
        massage_error(context, 'Кто-то запустил бота :)')


def text_click(update, context):
    """Функция обрабатывает текстовые сообщения."""

    chat = update.effective_chat
    try:
        if update.message.text == 'загрузить файл':
            name = update.message.chat.first_name

            tx = f'{name}, прикрепи файл в формате xlsx и отправь мне :)'
            context.bot.send_message(chat_id=chat.id, text=tx)
        else:
            tx = 'Выбери кнопку "загрузить файл"'
            context.bot.send_message(chat_id=chat.id, text=tx)
    except Exception:
        tx_err = 'Ошибка отправки сообщения'
        logger.error(tx_err)
        massage_error(context, tx_err)
        raise Exception(tx_err)


def reed_file_xlsx(user_name, file_name):
    """Функция преобразует xlsx документ в массив данных."""

    try:
        xls = pd.ExcelFile(f'temp/@{user_name} {file_name}')
        sheetX = xls.parse(0)
        result_arr = []
        name_columns = [i for i in sheetX]
    except Exception:
        raise Exception('Ошибка преобразования xlsx документа')

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
        try:
            to_db = [row[0], row[1], row[2]]
        except IndexError:
            raise IndexError('Проверить данные входного файла ' +
                             'Должно быть три столбца(name, URL, xPath)')
        try:
            curs.execute(
                "INSERT INTO ParsingData VALUES (NULL, ?, ?, ?);", to_db)
        except sqlite3.IntegrityError:
            pass
    logger.info('Данные успешно записаны в БД')
    conn.commit()


def download_file_xlsx(update, context):
    """Функция забирает xlsx документ с сервера."""

    file_name = update.message.document.file_name
    user_name = update.message.chat.username
    file_id = update.message.document.file_id
    try:
        new_file = context.bot.get_file(file_id)
        new_file.download(f'temp/@{user_name} {file_name}')
    except Exception:
        raise Exception('Проверить загрузку файла ексель с сервера')
    else:
        logger.info('Данные с сервера успешно загружены')
    return user_name, file_name


def format_data_list(arr):
    """Функция преобразует данные массива к строке."""

    result = ''
    for line in arr:
        result += '  '.join(line) + '\n\n'
    if not result:
        raise Exception('Ошибка преобразования данных к строке')
    return result


def send_message(update, context, massage):
    """Функция отправки присланных данных в Telegram чат."""

    chat = update.effective_chat
    try:
        for i in massage:
            context.bot.send_message(chat_id=chat.id, text=massage[i])
            time.sleep(3)
    except Exception:
        raise Exception('Ошибка отправки присланных данных')

    picture_random = random.randint(MIN_PICTURE, MAX_PICTURE)
    context.bot.send_photo(
        chat_id=chat.id, photo=open(
            f'pictures/IMG_{picture_random}.jpg', 'rb'))


def main_handler_file_xlsx(update, context):
    """Главная функция, обрабатывающая xlsx документ."""

    try:
        user_name, file_name = download_file_xlsx(update, context)
        array_data = reed_file_xlsx(user_name, file_name)
        write_file_xlsx_database(array_data)
        answer_text = format_data_list(array_data)

        massage = {1: 'Взгляни на обработанные данные:',
                   2: answer_text,
                   3: 'Картинка для настроения :)'}

        send_message(update, context, massage)
    except Exception as err:
        tx_err = 'Ошибка в главном обработчике xlsx документа'
        logger.error(err)
        massage_error(context, tx_err)
        raise Exception(tx_err)


def check_tokens():
    """Проверка доступности переменных окружения."""

    return all([BOT_TOKEN, ID_ADMIN])


def main():
    """Основная логика работы бота."""

    if not check_tokens():
        logger.critical('Ошибка переменных окружения')
        raise Exception(
            'Ошибка переменных окружения, проверить содержание файла .env')

    updater = Updater(token=BOT_TOKEN)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', wake_up)
    dispatcher.add_handler(start_handler)

    message_handler = MessageHandler(Filters.text, text_click)
    dispatcher.add_handler(message_handler)

    xlsx_handler = MessageHandler(
        Filters.document.file_extension("xlsx"), main_handler_file_xlsx)
    dispatcher.add_handler(xlsx_handler)

    updater.start_polling(poll_interval=10)
    updater.idle()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = FileHandler('infra/bot_home.log')
    handler2 = StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s - %(funcName)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    main()
