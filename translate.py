import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

load_dotenv()

YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'


def get_client_text(word):
    word_txt = word.get('text')
    word_gen = word.get('gen')
    word_anm = word.get('anm')
    word_tr = word.get('tr')
    words_list = []
    for words in word_tr:
        if words.get("mean") and words.get("gen"):
            words_list.append(
                f'\n{words.get("text")}, род: {words.get("gen")}, '
                f'значение:'
            )
            for mean in words.get("mean"):
                words_list.append(
                    f'{mean.get("text")},'
                )
        elif words.get("mean"):
            words_list.append(
                f'\n{words.get("text")}, '
                f'значение:'
            )
            for mean in words.get("mean"):
                words_list.append(
                    f'{mean.get("text")},'
                )
        elif words.get("gen"):
            words_list.append(
                f'\n{words.get("text")}, род: {words.get("gen")},'
            )
        else:
            words_list.append(
                f'\n{words.get("text")}'
            )
    return (
        f'{word_txt}, род: {word_gen}, предмет: {word_anm}\n'
        f'Найдено {len(word_tr)} перевода:\n'
        f'{",".join(words_list)}'
        f'\n\nРеализовано с помощью сервиса «API «Яндекс.Словарь» '
        f'http://api.yandex.ru/dictionary'
    )


def get_translate_queryset(text):
    data = text.split()
    params = {
        'key': f'{YANDEX_TOKEN}',
        'lang': f'{data[1]}',
        'text': f'{data[0]}',
    }
    try:
        return requests.post(URL, params=params).json().get('def')[0]
    except requests.RequestException as error:
        return logging.error(error, exc_info=True)


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def send_hi(bot, update):
    return update.message.reply_text(
        f'Здравствуйте, {update.message.chat.first_name}\n'
        f'Чтобы начать пользоваться словарём, просто введите любое слово '
        f'и укажите язык перевода (напр. "Словарь ru-de") '
        f'\nВарианты языков: en - английский; ru - русский; uk - украинский; '
        f'tr - турецкий; de - немецкий. '
        f'\n\nРеализовано с помощью сервиса «API «Яндекс.Словарь» '
        f'http://api.yandex.ru/dictionary'
    )


def get_message(bot, update):
    text = update.message.text
    try:
        queryset = get_translate_queryset(text)
        update.message.reply_text(get_client_text(queryset))
        logging.info('Сообщение отправлено')
    except Exception as e:
        logging.error(f'Бот столкнулся с ошибкой: {e}')
        update.message.reply_text('Бот столкнулся с ошибкой')
        time.sleep(5)


def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Запуск бота-ассистента')
    dispatcher.add_handler(
        CommandHandler('start', send_hi)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.text, get_message)
    )
    updater.start_polling(poll_interval=6.0)
    updater.idle()


if __name__ == '__main__':
    main()
