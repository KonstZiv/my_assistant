import pickle
from prettytable import PrettyTable
from termcolor2 import colored
from classes_my import AddressBook, Record, Phone, Birthday
import nltk
import re
import pymorphy2


def pretty_table(addressbook, N=10):
    # выводит на экран всю адресную книгу блоками по N записей. Основная обработка
    # реализована как метод класса addressbook, что позволяет использовать аналогичный
    # вывод для результатов поиска по запросам, так как функции поиска возвращают
    # объект типа addressbook с результатами
    n = int(N)
    pretty_print(f'всего к выводу {len(addressbook)} записей: ')
    for block in addressbook.out_iterator(n):
        print(pretty(block))
        usr_choice = input(colored(
            'Нажмите "Enter", или введите "q", что бы закончить просмотр.\n', 'yellow'))
        if usr_choice:
            '''Если пользователь вводит любой символ, его перебрасывает на основное меню.'''
            break
        continue

    return colored('Вывод окончен!', 'yellow')


def pretty(block):
    '''
        Данная функция создана исключительно для обработки функции show_all,
        1. Принимает блок
        2. Парсит его
        3. Добавляет обработанную инфу в таблицу
        4. Возвращает таблицу
        '''
    # from prettytable import ORGMODE
    # vertical_char=chr(9553), horizontal_char=chr(9552), junction_char=chr(9580)
    # vertical_char=chr(9475), horizontal_char=chr(9473), junction_char=chr(9547)
    #  vertical_char="⁝", horizontal_char="᠃", junction_char="྿"
    # ஃ ৹ ∘"܀" "܅" ྿ ፠ ᎒ ። ᠃

    table = PrettyTable(
        ['Name', 'Birthday', 'Number(s)'], vertical_char="⁝", horizontal_char="᠃", junction_char="྿")
    # table.set_style(ORGMODE)
    nx = str(block).split('\n')
    for j in range(len(nx) - 1):
        xr = nx[j].split('SP')
        a = str(xr.pop(2)).replace(
            '[', '').replace(']', '').replace(',', '\n')
        xr.append(a)
        table.add_row(xr)
    return colored(table, 'green')


def pretty_input(text):
    # функция для Ярослава
    # print(chr(3196)*80)
    print(colored(text, color='green'))
    user_input = input('>>> ')
    print(colored(chr(3196) * 80, color='green'))
    return user_input


def pretty_print(text):
    # функция для Ярослава
    print(colored(text, color='green'))
    print(chr(3196)*80)


def deserialize_users(path):
    """using the path "path" reads the file with contacts"""

    with open(path, "rb") as fh:
        addressbook = pickle.load(fh)

    return addressbook


def serialize_users(addressbook, path):
    """saves a file with contacts on the path (object pathlib.Path) to disk"""

    with open(path, "wb") as fh:
        pickle.dump(addressbook, fh)


def error_handler(func):
    # сюда вынесена обработка всех возникающих ошибок в ходе работы программы - как типов и
    # форматов, так и логические (дата рождения в будущем, попытка удалить несуществующий параметр и т.д.)
    def inner(*args):
        try:
            result = func(*args)
            return result
        except Exception as message:
            return message.args[0]

    return inner


def parse(input_string):  # --> ('key word', parameter)
    # извлекает команду и параметры из строки, возвращает в виде списка с
    # одним элементом - кортеж из двух элементов: команды и параметры

    def parse_phone(src):
        # функция принимает строку в качестве аргумента и ищет в ней номер телефона (справа)
        # Возвращает кортеж из двух аргументов - все, вплоть до номера телефона (без
        # пробелов слева и справа) и номера телефона. Если номер телефона не найден,
        # вместо него возвращается пустая строка.

        import re
        phone_regex = re.compile(r'[+]?[\d\-\(\)]{5,18}\s?$')
        match = phone_regex.search(src)
        if match is None:
            result = (src.strip(), '')
        else:
            result = (src[:match.start()].strip(), match.group())
        return result

    def parse_word(word):
        # фабричная функция. Производит функции синтаксического анализатора для
        # отдельных команд. Возвращает кортеж из команды, строку после команды
        # и номер телефона. Если номер телефона отсутствует, вместо него
        # возвращается пустая строка.

        l = len(word)

        def result(src):
            if src.casefold().startswith(word.casefold()):
                return word, *parse_phone(src[l:].lstrip())

        return result

    parse_scoup = [
        parse_word('hello'),
        parse_word('add'),
        # parse_word('change'),
        parse_word('phone'),
        parse_word('show all'),
        parse_word('exit'),
        parse_word('close'),
        parse_word('good bye'),
        parse_word('.'),
        parse_word('help'),
        parse_word('search'),
        parse_word('other phone'),
        parse_word('bd add')
    ]
    res_pars = [i(input_string) for i in parse_scoup if i(
        input_string)] or [('unrecognize', '', '')]

    return res_pars[0]


@error_handler
def get_handler(res_pars, addressbook):
    # получив результаты работы парсера функция управляет передачей параметров
    # и вызовм соотвествующего обработчика команды

    def help_f(*args):
        return '''формат команд:
        - add - формат: add name phone_number - добавляет новый контакт
        - other phone - формат: other phone name phone_number - добавляет дополнительный телефон в существующую запись
        - show all - формат: show all [N] - показывает всю адресную книгу. N - необязательный параметр - количество одновременно выводимых записей
        - exit/./close/goog bye - формат: exit - остановка работы с программой. Важно! чтобы сохранить все изменения и введенные данные - используйте эту команду
        - phone - формат: phone name - поиск телефона по имени. Можно ввести неполной имя либо его часть - программа выведет все совпадения
        - hello - формат: hello - просто Ваше привествие программе. Доброе слово - оно и для кода приятно)
        - bd add - формат: bd add name dd-mm-YYYY - ввод либо перезапись ранее введенной даты рождения. Соблюдайте формат ввода даты.
        - search - формат: search pattern - поиск совпадений по полям имени и телефонов. Будут выведены все записи в которых есть совпадения'''

    def hello_f(*args):
        return 'How can I help you?'

    def exit_f(*args):
        return None

    def add_f(addressbook):
        #  сначала создает запись с именем
        #  потом последовательно вызывает функции
        # для заполнения телефона, д/р, заметки, и т.д.
        name = pretty_input('Введите имя ')
        record = Record(name)
        addressbook.add_record(record)

        add_phone(record)
        change_bd(record)
        change_adr(record)
        change_eml(record)
        add_note(record)

        pretty_print(f'в адресную книгу внесена запись: \n{record}')
        return True

    @error_handler
    def add_note(record):
        pass

    @error_handler
    def change_note(record):
        pass

    @error_handler
    def change_eml(record):
        pass

    @error_handler
    def change_adr(record):
        pass

    def change_name(record):
        name = pretty_input('Введите новое имя ')
        addressbook.del_record(name)
        record.change_name(name)
        addressbook(record)

    @error_handler
    def change_bd(record):
        birthday_str = pretty_input(
            'введите день рождения в формате дд-мм-гггг ("ввод" - пропустить): ')
        if birthday_str:
            result = record.add_birthday(birthday_str)
            if isinstance(result, Exception):
                return result
            return f'в запись добавлен день рождения: \n {record}'
        else:
            return 'абоненту день рождения не добавлен'

    @error_handler
    def add_phone(record):
        # позволяет добавить в запись дополнительный телефон
        phone = pretty_input('Entry phone number ')
        result = record.add_phone(phone)

        if isinstance(result, Exception):
            return result
        return f'в запись добавлен новый телефон: \n {record}'

    @error_handler
    def change_phone(record):

        pretty_print(record)
        old_phone = pretty_input(
            'What number you want to change (enter item number) ')

        new_phone = pretty_input('Entry new phone number ')
        result = record.change_phone(old_phone, new_phone)
        if isinstance(result, Exception):
            return result
        return f'в запись добавлен новый телефон: \n {record}'

    def change_f(addressbook):

        name = pretty_input('Введите имя ')
        record = addressbook[name]
        pretty_print(record)
        pretty_print(menu_change)
        item_number = input('>>>  ')
        return func_change[item_number](record)

    def search(addressbook):
        user_input = pretty_input('What are you looking for?  ')
        # осуществляет поиск введенной строки во всех текстовых полях адресной книги
        result = addressbook.search(user_input)

        if not result:
            raise Exception('По данному запросу ничего не найдено')

        return pretty_table(result, N=10)

    def delete_f(addressbook):
        name = pretty_input('Введите имя ')
        result = addressbook.del_record(name)
        return result

    def show_all_f(addressbook, N=10):
        return pretty_table(addressbook, N)

    def unrecognize_f(res_pars, addressbook):
        print(f'вызвана функция unrecognize. Строка:  {res_pars}')
        COMMANDS = {'add': ['добавить', 'приплюсовать', 'нарастить', 'расширить', 'присовокупить', 'доложить', 'подбросить',
                    'прирастить', 'прибавить', 'приобщить', 'причислить', 'дополнить', 'додать', 'надбавить', 'увеличить', 'привнести',
                            'подбавить', 'присоединить', 'подбавить', 'внести', 'добавляй'],
                    'change': ['изменить', 'модифицировать', 'реконструировать', 'поменять', 'трансформировать', 'преобразовать',
                               'преобразить', 'переделать', 'видоизменить', 'обновить', 'переменить', 'сменить', 'изменить', 'менять', 'заменить'],
                    'remove': ['удалить', 'изьять', 'вытереть', 'выкинуть', 'вытереть', 'стререть', 'очистить', 'убрать', 'исключить',
                               'ликвидировать', 'удаляй', 'вытирай'],
                    'search': ['найти', 'выбрать', 'подобрать', 'показать', 'вывести', 'отобразить', 'искать', 'найди', 'ищи']}

        OBJECTS = {'record': ['имя', 'запись', 'человек', ],
                   'phone': ['телефон', 'номер'],
                   'birthday': ['день', 'дата', 'роды'],
                   'note': ['заметка', 'текст', 'тэг', 'примечание', 'описание', 'напоминание'],
                   'email': ['почта', 'мыло', 'email', 'e-mail', 'emails', 'e-mails', 'электронка'],
                   'adress': ['адрес', 'город', 'улица', 'ул.', 'проспект', 'поселок', 'село', 'деревня', 'бульвар', 'дом', 'квартира',
                              'кв.', 'площадь', 'пос.', 'набережная']}

        def find_email(raw_text):
            regex = re.compile('[^ @]*@[^ ]*')
            result = regex.findall(raw_text)
            return result if result else None

        def pre_processing_str(raw_str):
            # Эта функция считает, что входящий текст - ОДНО предложение. \
            # осуществляет предварительную обработку строки - \
            # из предложения удаляет стоп-слова, \
            # предложение разбивает на слова и возвращает список слов без стоп-слов

            # получаем список слов
            text_words_list = (nltk.word_tokenize(raw_str))
            # читаем из библиотеки и дополняем список стоп-слов
            stop_words = nltk.corpus.stopwords.words('russian')
            stop_words.extend(['что', 'это', 'так', 'вот', 'быть',
                               'как', 'в', '—', '–', 'к', 'на', '...'])
            # удаляем из списка слов стоп-слова
            prepare_text_words_list = [
                i for i in text_words_list if (i not in stop_words)]
            return prepare_text_words_list

        def find_predictors(prepare_text_word_list, commands_scoup=COMMANDS, objects_scoup=OBJECTS):
            # получает на вход предварительно обработанный список слов из введенной строки, \
            # словарь возможных значений команд и словарь созможных значений объектов (то, над \
            # чем могут совершаться команды). Возвращает словарь, в котором ключами являются \
            # строки - соотвествующие предикторам, а значениями списки (для объектов которые могут \
            # имень несколько значений - телефоны, e-mail, команды или типы объектов), \
            # и одиночное значение (строка) для имени

            morph_ru = pymorphy2.MorphAnalyzer()

            predictors_dict = {
                'name': None,
                'commands': [],
                'objects': [],
                'phones': [],
                'emails': []
            }

            def find_commands(word_of_morph_res, commands_scoup=COMMANDS):
                # из результатов морфлогического разбора отдельных слов выбираю ТОЛЬКО глаголы\
                # и сравниваю их нормальную форму с перечнем возможных команд. При совпадении\
                # возвращаю наименование команды как строку, иначе - None
                if word_of_morph_res.tag.POS == 'VERB' or word_of_morph_res.tag.POS == 'INFN':
                    for key, value in commands_scoup.items():
                        for word in value:
                            if word_of_morph_res.normal_form == word:
                                return key

            def find_objekts(word_of_morph_res, objects_scoup=OBJECTS):
                # из результатов морфлогического разбора отдельных слов выбираю ТОЛЬКО существительные\
                # и сравниваю их нормальную форму с перечнем возможных названий объектов. При совпадении\
                # возвращаю наименование объекта как строку, иначе - None
                res = None
                if word_of_morph_res.tag.POS == 'NOUN':
                    for key, value in objects_scoup.items():
                        res = key if [x for x in value if x ==
                                      word_of_morph_res.normal_form] else None
                        if res:
                            break
                return res

            def find_name(morph_ru_result):
                # из результатов морфлогического разбора отдельных слов выбираю ТОЛЬКО с признаком,\
                # одушевленности и формирую из них одну строку. Если не найдено ничего - None
                res = []
                for word in morph_ru_result:
                    #print(f'{word[0].normal_form}    {word[0].tag.animacy}')
                    if word.tag.animacy == 'anim':
                        res.append(word.normal_form)
                return ' '.join(res) if res else None

            def find_phone(raw_text):
                regex = re.compile('\+?[0-9-xX()\[\]]{5,25}')
                result = regex.search(raw_text)
                return result.group() if result else None

            # проводим морфологический разбор слов в списке переданных подготовленных слов,\
            #  выбираем только наиболее вероятные знаяения для слов (выбор єлемента с индексом 0)
            morph_ru_result = [morph_ru.parse(word)[0]
                               for word in prepare_text_word_list]

            for word in morph_ru_result:
                command = find_commands(word, commands_scoup=COMMANDS)
                if command:
                    predictors_dict['commands'].append(command)

                object_for = find_objekts(word, objects_scoup=OBJECTS)
                if object_for:
                    predictors_dict['objects'].append(object_for)

                phone = find_phone(word.word)
                if phone:
                    predictors_dict['phones'].append(phone)

            predictors_dict['name'] = find_name(morph_ru_result)

            return predictors_dict

        def hendler_raw(predictors_dict, address_book):
            # получает на вход словарь с набором выявленных предикторов \
            # и на основе их анализа предлагает действия для их обработки
            # возвращает строку с рапортом о совершенных действиях или None\
            #  если никакие действия совершены быть не могут

            if 'search' in predictors_dict['commands']:
                pattern = pretty_input(
                    'распознана команда ПОИСК. \nЧто ищем, брат? Не разобрал, повтори, будь добр... : ')
                result = address_book.search(pattern)
                pretty_table(result)
                return 'поиск выполнен'

            if not predictors_dict['commands']:
                return 'ввод не распознан. Получить помощь можно используя команду help'

            if predictors_dict['name']:

                if not predictors_dict['name'] in address_book:
                    if not 'add' in predictors_dict['commands']:
                        # для несуществующей записи выбрана команда (не add). Действие не может быть завершено
                        pretty_print(
                            f"Распознана команда {'/'.join(predictors_dict['commands'])}, но записи с именем {predictors_dict['name']} не существует. \n Команда не может быть выполнена. Попробуйте еще раз")
                        return 'невозможно применить введенную команду к несуществующей записи'
                    # предложить создать новую запись с параметрами из словаря.
                    record_temp = gen_record(predictors_dict)
                    pretty_print(
                        'С введенными параметрами может быть создана новая запись: ')
                    pretty_table(AddressBook(record_temp))
                    while True:
                        enter = pretty_input(
                            'внести запись в адресную книгу? ("y" - да, "n" - нет)')
                        if enter == 'y':
                            address_book.add_record(record_temp)
                            # вызвать функцию для построчного ввода чего-то
                            return f'запись {predictors_dict["name"]} внесена в адресную унигу'
                        elif enter == 'n':
                            break
                    return f'запись {predictors_dict["name"]} не сохранена'

                # отобразить текущую запись
                pretty_print(
                    f'Текущее содержание записи {predictors_dict["name"]}: ')
                pretty_table(AddressBook(
                    address_book[predictors_dict["name"]]))
                # проверить наличие поля phone и номера телефона
                if ('phone' in predictors_dict['objects']) and predictors_dict['phones']:
                    command = predictors_dict['commands'][0]
                    if command == 'add':
                        for phone in predictors_dict['phones']:
                            # вызвать функцию добавления телефона phone в запись predictors_dict["name"]
                            address_book[predictors_dict["name"]
                                         ].add_phone(phone)

                        # return f'мы должны тут добавить телефон {phone} в запись {predictors_dict["name"]}'
                    if command == 'remove':
                        for phone in predictors_dict['phones']:
                            # вызвать функцию удаления телефона phone из записи predictors_dict["name"]
                            address_book[predictors_dict["name"]
                                         ].del_phone(phone)
                            pass
                        # return f'мы должны тут удалить телефон {phone} из записи {predictors_dict["name"]}'
                    if command == 'change':
                        # return 'при необходимости заменить телефон в какой-либо записи воспользуйтесь \nцифровым ваантом меню или сначала добавьте новый номер телефона, а потом \nудалмите старый. При свободном вводе я могу перепутать телефоны \n- что приведет к потере важной информации. Извините.'
                        # проверить наличие поля email и значений email
                        pass
                if ('email' in predictors_dict['objects']) and predictors_dict['emails']:
                    command = predictors_dict['commands'][0]
                    if command == 'add':
                        for email in predictors_dict['emails']:
                            # вызвать функцию добавления email в запись predictors_dict["name"]
                            pass
                        # return f'мы должны тут добавить email {email} в запись {predictors_dict["name"]}'
                    if command == 'remove':
                        for email in predictors_dict['emails']:
                            # вызвать функцию удаления телефона phone из записи predictors_dict["name"]
                            pass
                        return f'мы должны тут удалить email {email} из записи {predictors_dict["name"]}'
                    if command == 'change':
                        # return 'при необходимости заменить email в какой-либо записи воспользуйтесь \nцифровым ваантом меню или сначала добавьте новый email, а потом \nудалмите старый. При свободном вводе я могу перепутать email \n- что приведет к потере важной информации. Извините.'
                        # значения телефонов найдены, но слово "телефон" не встречается в строке
                        pass
                if predictors_dict['phones'] and (not ('phone' in predictors_dict['objects'])):
                    command = predictors_dict['commands'][0]
                    if command == 'add':
                        for phone in predictors_dict['phones']:
                            # вызвать функцию добавления телефона phone в запись predictors_dict["name"]
                            address_book[predictors_dict["name"]
                                         ].add_phone(phone)
                            print('перед сохранием - уточнить')
                        # return f'мы должны тут добавить телефон {phone} в запись {predictors_dict["name"]}'
                    if command == 'remove':
                        for phone in predictors_dict['phones']:
                            # вызвать функцию удаления телефона phone из записи predictors_dict["name"]
                            address_book[predictors_dict["name"]
                                         ].del_phone(phone)
                            print('перед сохранием - уточнить')
                        # return f'мы должны тут удалить телефон {phone} из записи {predictors_dict["name"]}'
                    if command == 'change':
                        # return 'при необходимости заменить телефон в какой-либо записи воспользуйтесь \nцифровым ваантом меню или сначала добавьте новый номер телефона, а потом \nудалмите старый. При свободном вводе я могу перепутать телефоны \n- что приведет к потере важной информации. Извините.'
                        pass
                if (not ('email' in predictors_dict['objects'])) and predictors_dict['emails']:
                    command = predictors_dict['commands'][0]
                    if command == 'add':
                        for email in predictors_dict['emails']:
                            # вызвать функцию добавления email в запись predictors_dict["name"]
                            print('перед сохранием - уточнить')
                        # return f'мы должны тут добавить email {email} в запись {predictors_dict["name"]}'
                    if command == 'remove':
                        for email in predictors_dict['emails']:
                            # вызвать функцию удаления телефона phone из записи predictors_dict["name"]
                            print('перед сохранием - уточнить')
                        # return f'мы должны тут удалить email {email} из записи {predictors_dict["name"]}'
                    if command == 'change':
                        pass
                        # return 'при необходимости заменить email в какой-либо записи воспользуйтесь \nцифровым ваантом меню или сначала добавьте новый email, а потом \nудалмите старый. При свободном вводе я могу перепутать email \n- что приведет к потере важной информации. Извините.'
                # слово телефон (email) встречается в строке, но значения нет
                if (not predictors_dict['phones']) and ('phone' in predictors_dict['objects']):
                    command = predictors_dict['commands'][0]
                    if command == 'add':
                        for phone in predictors_dict['phones']:
                            add_phone(address_book[predictors_dict['name']])
                            # запросить телефон для добавления
                            # вызвать функцию добавления телефона phone в запись predictors_dict["name"]

                        # return f'мы должны тут запросить телефон и добавить его в запись {predictors_dict["name"]}'
                    if command == 'remove':
                        for phone in predictors_dict['phones']:
                            # запросить телефон для удаления
                            # вызвать функцию удаления телефона phone из записи predictors_dict["name"]
                            pass
                        # return f'мы должны запросить номер телефона и удалить его из записи {predictors_dict["name"]}'
                    if command == 'change':
                        pass
                        # return 'при необходимости заменить телефон в какой-либо записи воспользуйтесь \nцифровым ваантом меню или сначала добавьте новый номер телефона, а потом \nудалмите старый. При свободном вводе я могу перепутать телефоны \n- что приведет к потере важной информации. Извините.'
                if ('email' in predictors_dict['objects']) and (not predictors_dict['emails']):
                    command = predictors_dict['commands'][0]
                    if command == 'add':
                        for email in predictors_dict['emails']:
                            # запросить email
                            # вызвать функцию добавления email в запись predictors_dict["name"]
                            pass
                        # return f'мы должны тут запросить email и добавить его в запись {predictors_dict["name"]}'
                    if command == 'remove':
                        for email in predictors_dict['emails']:
                            # запросить email
                            # вызвать функцию удаления телефона phone из записи predictors_dict["name"]
                            pass
                        # return f'мы должны тут запросить email и удалить его из записи {predictors_dict["name"]}'
                    if command == 'change':
                        pass
                        # return 'при необходимости заменить email в какой-либо записи воспользуйтесь \nцифровым ваантом меню или сначала добавьте новый email, а потом \nудалмите старый. При свободном вводе я могу перепутать email \n- что приведет к потере важной информации. Извините.'
            return f'обработка записи {predictors_dict["name"]} завершена'

        def gen_record(predictors_dict):
            # получает словарь выделенных из текста параметров и создает объект типа Record с этими параметрами
            record = Record(predictors_dict['name'])
            for elem in predictors_dict['phones']:
                record.add_phone(elem)
            # for elem in predictors_dict['emails']:
            #    record.add_email(elem)
            return record

        prepare_text_words_list = pre_processing_str(res_pars)
        print(prepare_text_words_list)  # отладочный вывод

        # получаем словарь выявленных предикторов - подробнее в описании функции
        predictors_dict = find_predictors(prepare_text_words_list)

        # для словаря предикторов ищим в исходной стпроке e-mail (это костыль - все\
        #  это должно делаться функцией find_predictors(), но так проще сейчас)
        email = find_email(res_pars)
        if email:
            predictors_dict['emails'].extend(email)

        print(predictors_dict)  # отладочный вывод

        return hendler_raw(predictors_dict, addressbook)

    menu_change = '''
    What you want to change:    1. name
                                2. change phone
                                3. add phone
                                4. change birthday
                                5. change e-mail
                                6. change address
                                7. change note
                                8. add note
    '''

    func_change = {'1': change_name,
                   '2': change_phone,
                   '3': add_phone,
                   '4': change_bd,
                   '5': change_eml,
                   '6': change_adr,
                   '7': change_note,
                   '8': add_note}

    HANDLING = {
        '1': add_f,
        '2': change_f,
        '3': delete_f,
        '4': search,
        '5': show_all_f,
        '6': exit_f,
        'hello': hello_f,
        'exit': exit_f,
        '.': exit_f,
        'good bye': exit_f,
        'close': exit_f,
        'add': add_f,
        'show all': show_all_f,
        'phone': search,
        'search': search,
        'change': change_f,
        'unrecognize': unrecognize_f,
        'help': help_f,
        'other phone': add_phone,
        'bd add': change_bd
    }

    return HANDLING.get(res_pars)(addressbook) if HANDLING.get(res_pars) else unrecognize_f(res_pars, addressbook)
