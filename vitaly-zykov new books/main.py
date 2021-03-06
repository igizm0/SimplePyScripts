#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


"""
Скрипт для уведомления о появлении новых книг Зыкова.

"""


# TODO: костыль для винды, для исправления проблем с исключениями
# при выводе юникодных символов в консоль винды
# Возможно, не только для винды, но и для любой платформы стоит использовать
# эту настройку -- мало какие проблемы могут встретиться
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter(sys.stdout.encoding)(sys.stdout.detach(), 'backslashreplace')
    sys.stderr = codecs.getwriter(sys.stderr.encoding)(sys.stderr.detach(), 'backslashreplace')


def wait(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    from datetime import timedelta, datetime
    today = datetime.today()
    timeout_date = today + timedelta(
        days=days, seconds=seconds, microseconds=microseconds,
        milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks
    )

    while today <= timeout_date:
        def str_timedelta(td):
            # Remove ms
            td = str(td)
            if '.' in td:
                td = td[:td.index('.')]

            return td

        left = timeout_date - today
        left = str_timedelta(left)

        print('\r' * 100, end='')
        print('До следующего запуска осталось {}'.format(left), end='')

        import sys
        sys.stdout.flush()

        # Delay 1 seconds
        import time
        time.sleep(1)

        today = datetime.today()

    print('\r' * 100, end='')
    print('\n')


from config import *


def get_logger(name, file='log.txt', encoding='utf8'):
    import sys
    import logging

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s')

    fh = logging.FileHandler(file, encoding=encoding)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)

    return log


log = get_logger('vitaly-zykov new books')


def send_sms(api_id: str, to: str, text: str):
    log.debug('Отправка sms: "%s"', text)

    # Отправляю смс на номер
    url = 'https://sms.ru/sms/send?api_id={api_id}&to={to}&text={text}'.format(
        api_id=api_id,
        to=to,
        text=text
    )
    log.debug(repr(url))

    while True:
        try:
            import requests
            rs = requests.get(url)
            log.debug(repr(rs.text))

            break

        except:
            log.exception("При отправке sms произошла ошибка:")
            log.debug('Через 5 минут попробую снова...')

            # Wait 5 minutes before next attempt
            import time
            time.sleep(5 * 60)


def get_books():
    import requests
    rs = requests.get('http://vitaly-zykov.ru/knigi')

    from bs4 import BeautifulSoup
    root = BeautifulSoup(rs.content, 'lxml')

    return [x.text.strip().replace('"', '') for x in root.select('.book_tpl > h3')]


FILE_NAME_CURRENT_BOOKS = 'books'


if __name__ == '__main__':
    # NOTE: С этим флагом нужно быть осторожным при первом запуске, когда список книг пустой
    notified_by_sms = True

    # Загрузка текущих книг
    import ast
    current_books = ast.literal_eval(open(FILE_NAME_CURRENT_BOOKS, encoding='utf-8').read())
    log.debug('Current books: %s', current_books)

    while True:
        try:
            log.debug('get books')

            books = get_books()
            log.debug('books: %s', books)

            new_books = set(books) - set(current_books)
            if new_books:
                current_books = books
                open(FILE_NAME_CURRENT_BOOKS, mode='w', encoding='utf-8').write(str(current_books))

                for book in new_books:
                    text = 'Появилась новая книга Зыкова: "{}"'.format(book)
                    log.debug(text)

                    if notified_by_sms:
                        send_sms(API_ID, TO, text)

            else:
                log.debug('Новых книг нет')

            wait(weeks=1)

        except:
            log.exception('Ошибка:')
            log.debug('Через 5 минут попробую снова...')

            # Wait 5 minutes before next attempt
            import time
            time.sleep(5 * 60)
