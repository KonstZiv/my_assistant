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

    menu = '''You can :
                1. add abonent to addressbook
                2. change abonent's record in addressbook
                3. delete abonent from addressbook
                4. seek abonent or phone
                5. show all 
                6. end 
            Choose menu item number'''

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
            print('Good bye!')
            break
        print(result)


if __name__ == '__main__':
    main()
