import requests
import os
import time
from bs4 import BeautifulSoup as bs
from config import logging

# Another example:
# https://manga.in.ua/index.php?story={attack+on+titan}&do=search&subaction=search


def index_0(d):
    return next(iter(d))


class SearchMangaInUa:
    def __init__(self, url, headers):
        self.headers = headers
        self.url = url
        self.results = dict()
        self.query = ""
        self.volume_title = ""
        self.volumes = dict()

    def get_search_results(self, query):
        self.query = query
        r = requests.post(self.url, data={
            'do': 'search', 'subaction': 'search', 'titleonly': '3', 'story': self.query}, headers=self.headers)
        soup = bs(r.text, features="lxml")

        for result in soup.find_all('h3', class_='card__title'):
            result_title = result.find('a').get('title')
            result_url = result.find('a').get('href')
            self.results.update({result_title: result_url})
        if not self.results:
            return None
        else:
            return self.results

    def get_all_volumes(self, results):
        self.results = results

        def check_for_chapters(soup):
            chapter_list = list()
            count = soup.find_all('div', class_='icon_wrapper fleft small')
            for chapter in count:
                chapter_url = chapter.find('a').get('href')
                chapter_list.append(chapter_url)
            if chapter_list != 0:
                return chapter_list
            else:
                return None

        def get_all_chapters(chapters):
            reversed_chapter_list = chapters[::-1]
            for item in reversed_chapter_list:
                self.volumes.update(
                    {volume_title + "_" + str(reversed_chapter_list.index(item) + 1): [item]})

        def get_all_volumes_alt(soup):
            self.volumes = {}
            self.volume_title = index_0(results)
            count = soup.find_all(
                'div', class_='customajaxpagination_wrapper')
            for volume in count:
                chapter_url = volume.find('a').get('href')
                chapter_title = ''.join(volume.find('a').contents)

                r = requests.get(chapter_url, headers=self.headers)
                soup = bs(r.text, features="lxml")

                pages = soup.find('div', class_='comics')
                image_tags = pages.find_all('img')
                image_paths = (list(tag['data-src']
                                    for tag in image_tags))
                image_links = [
                    f'https://manga.in.ua{path}' for path in image_paths]
                logging.info(
                    f"Знайдено {len(image_links)} сторінок в {chapter_title.strip()}.")
                self.volumes.update({chapter_title: image_links})

        try:
            volume_list = list()
            volume_url = results[index_0(results)]
            volume_title = ''.join([
                key for (key, value) in results.items() if value == volume_url])
            self.volume_title = volume_title

            r = requests.get(volume_url, headers=self.headers)
            soup = bs(r.text, features="lxml")
            count = soup.find_all(
                'div', class_='icon_wrapper fright small')
            for volume in count:
                volume_url = volume.find('a').get('href')
                volume_list.append(volume_url)

            if len(volume_list) == 0:
                try_chapters = check_for_chapters(soup)
                if not try_chapters:
                    pass
                else:
                    # pages without download whole volumes button (one on the right) and only chapters
                    get_all_chapters(try_chapters)
                    return self.volumes

            elif len(volume_list) != 0:
                logging.info(f"Знайдено {len(volume_list)} томів.")
                reversed_volume_list = volume_list[::-1]
                for item in reversed_volume_list:
                    self.volumes.update(
                        {volume_title + "_" + str(reversed_volume_list.index(item) + 1): [item]})

            # alt pages with no download buttons
            if not self.volumes:
                get_all_volumes_alt(soup)
            return self.volumes
        except TypeError as error:
            logging.info(f"{error}")
            return None

    def download_all_volumes(self, delay, volumes=None, desired_path=''):
        def mkdir(path):
            try:
                os.mkdir(path)
            except OSError as error:
                logging.info(f"Директорія '{path}' вже існує...\n{error}")

        def sleep(delay, download_list, current_item):
            last_item = list(download_list)[-1]
            if current_item != last_item:
                time.sleep(delay)

        def write(download_request, download_title):
            with open(download_title, "wb") as download:
                download.write(download_request.content)
                logging.info(
                    f"Завантажено '{download_title}'.")

        def download(path, volumes):
            for i in volumes:
                download_title = path + "/" + \
                    i.replace(" / ", "_") + ".zip"
                logging.info(f"Завантажуємо '{download_title}'...")
                if os.path.isfile(download_title):
                    logging.info(f"'{download_title}' вже існує.")
                    pass
                else:
                    download_request = requests.get(
                        volumes[i][0], headers=self.headers)
                    write(download_request, download_title)
                sleep(delay, download_list=volumes, current_item=volumes)

        def download_alt(path, volumes):
            for i in volumes:
                download_path = path + "/" + \
                    i.replace(" / ", "_").replace("/", "\\").strip()
                mkdir(download_path)
                count = 1  # workaround i'm not proud of.
                for chapter in volumes[i]:
                    download_title = download_path + \
                        "/" + str(count) + ".png"
                    if os.path.isfile(download_title):
                        logging.info(f"'{download_title}' вже існує.")
                        pass
                    else:
                        download_request = requests.get(
                            chapter, headers=self.headers)
                        write(download_request, download_title)
                        count += 1
                    sleep(
                        delay, download_list=volumes[i], current_item=chapter)
                count = 1

        if desired_path == '':
            path = self.volume_title.replace(" / ", "_")
        elif desired_path.endswith('/'):
            path = desired_path + \
                self.volume_title.replace(" / ", "_")
        else:
            path = desired_path + '/' + \
                self.volume_title.replace(" / ", "_")
        path = path.replace("/", "\\").strip()

        if not volumes:
            logging.critical('Critical. No volumes argument provided!')
            exit(1)

        vol_index_0 = index_0(volumes)
        if len(volumes[vol_index_0]) == 1:
            mkdir(path)
            try:
                download(path, volumes)
                return True
            except TypeError as error:
                logging.error(f"{error}")
                return False

        elif len(volumes[vol_index_0]) > 1:
            mkdir(path)
            try:
                download_alt(path, volumes)
                return True
            except TypeError as error:
                logging.error(f"{error}")
                return False

    def print_params(self):
        print("=" * 50)
        print(f"""
                {self.headers=}
                {self.url=}
                {self.query=}
                {self.results=}
                {self.volume_title=}
                """)
