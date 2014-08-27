# coding=utf-8
"""
EN: Decoding the phone number for CLI.
RU: Декодирование телефонного номера для АОН (Автоматический определитель номера).
"""

# Algorithm
# RU:
# По запросу АОНа АТС посылает телефонный номер, используя следующие правила:
# — Если цифра повторяется менее 2 раз, то это помеха и она должна быть отброшена
# — Каждая значащая цифра повторяется минимум 2 раза
# — Если в номере идут несколько цифр подряд, то для обозначения «такая же цифра как предыдущая» используется
# идущий 2 или более подряд раз знак #
#
# Например, входящая строка 4434###552222311333661 соответствует номеру 4452136

import argparse

__author__ = 'ipetrash'


def decoding_phone_number(string):
    string += " "
    result = ""
    last = ""
    repeat = 1
    symbol_before_grill = ""

    for s in string:
        if not last:
            last = s
            repeat = 1
            continue

        if s is "#" and last is not "#":  # Если текущий символ # и предыдущий число
            symbol_before_grill = last  # Запомним символ перед #

        if last is s:  # Если встретили повтор
            repeat += 1
        else:  # Если символ не такой же как предыдущий
            if repeat > 1:  # Если символ имеет повторы
                if last is "#" and symbol_before_grill:  # Если последним символов является # и ...
                    result += symbol_before_grill  # Добавим число, перед #, но саму # добавлять не будем
                    symbol_before_grill = ""
                else:
                    result += last
                repeat = 1

        last = s

    return result


def create_parser():
    parser = argparse.ArgumentParser(description="Decoding the phone number for CLI")
    return parser


if __name__ == '__main__':
    create_parser().parse_args()

    string = raw_input("Encoded telephone number = ")
    print("Phone number = " + decoding_phone_number(string))