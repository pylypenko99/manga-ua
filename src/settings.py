import sys
import logging
import json
import questionary

SITE_URL = "https://manga.in.ua/mangas/"
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.7113.93 Safari/537.36'}


def logs(debug=False):
    if debug:
        logging.basicConfig(level=logging.DEBUG, datefmt='%H:%M:%S',
                            format='%(levelname)s %(asctime)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, datefmt='%H:%M:%S',
                            format='%(levelname)s %(asctime)s: %(message)s')


'''
Reference:
logging.debug('debug')
logging.info('using %s file', w)
status = "based"
logging.warning(f'warning! user is {status}!')
logging.error('error')
ligging.exception('exception')
logging.critical('critical')
'''

logs()


def usage():
    usage = f"""
    Використання:
        {sys.argv[0]} (опція) (аргумент) (опція) (...)

        Опції:
            -h, --help          Допомога(це повідомлення).
                                Не потребує аргументів.

            -v, --verbose       Відображати додаткову інформацію.
                                Не потребує аргументів.

            -o, --output=       Зазначити директорію в яку слід завантажувати манґу.

            -s, --search=       Пошук на сайті без завантаження,
                                без цієї опції програма окремо попросить вас ввести запит.

            -d, --download-all  Завантажити всі томи знайденої манґи.
                                Не потребує аргументів.

            -w, --delay=        Перерва між кожним завантаженням,
                                для того аби не перевантажувати пропускну здатність серверів.

            -f, --default_dir=  Встановити шлях до директорії для завантаження за замовчуванням.
    """
    return usage


def default_path(set_path=None, get_path=False):
    if get_path:
        try:
            with open("config.json", "r") as config_file:
                path = json.load(config_file)
                return path['default_path']
        except OSError as error:
            logging.error(f"{error}")
            return ''
    if set_path:
        try:
            with open("config.json", "w") as config_file:
                json.dump({'default_path': set_path}, config_file, indent=True)
            questionary.print(
                f"Шлях за замовчуванням встановлено: {set_path}", style="italic")
        except OSError as error:
            logging.error(f"{error}")
            exit(1)
