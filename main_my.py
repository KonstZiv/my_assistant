from ntpath import join
from classes_my import AddressBook, Record, Phone, Birthday
from os import name
import sys
from functions import error_handler, deserialize_users, serialize_users, parse, pretty_print, get_handler
import time
import nltk
import pymorphy2
import re
from pathlib import Path
from faker import Faker


# директория может быть выбрана при запуске программы, имя файла - константа.
CONTACTS_FILE = 'contacts.dat'
CONTACTS_DIR = ''


def main():
    # главный цикл работы программы
    if len(sys.argv) < 2:
        path = CONTACTS_DIR
        name = CONTACTS_FILE
        path_file = Path(path) / name
        addressbook = deserialize_users(
            path_file) if Path.exists(path_file) else AddressBook()

    else:
        path = sys.argv[1]
        name = CONTACTS_FILE
        path_file = Path(path) / name
        addressbook = deserialize_users(path_file)

    menu = '''Вы можете:
                1. добавить абонента в адресную книгу
                2. изменить поля в адресной книге для существующего абонента
                3. удалить абонента из адресной книги
                4. искать абонента в адресной книге по любым полям и вхождениям в них
                5. просмотреть все записи в адресной книге 
                6. завершить работу 
            выберите желаемый пункт меню
                      (P.S. или напишите мне простым языком - чего Вы хотите. Постараюсь понять)
                      (P.P.S. если Ваши желания будут выражены простыми предложениями - мне будет легче понять)'''

    while True:
        # addressbook.add_fake_records(40)

        pretty_print(menu)
        input_string = input('>>>  ')
        # убираем разбор строки на слова и поиск команды
        # res_pars = parse(input_string)

        # сейчас input_string  должен содержать только номер команду - действие

        result = get_handler(input_string, addressbook)
        if not result:
            serialize_users(addressbook, path_file)
            print('Пока!')
            break
        pretty_print(result)


if __name__ == '__main__':
    main()
