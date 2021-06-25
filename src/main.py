#!/bin/env python
import getopt
import questionary

from search import SearchMangaInUa
from kaomoji import check_search_results, check_volumes, check_downloaded
from config import usage, HEADERS, SITE_URL, logs

'''
TODO:
    - Proper INFO logs for old pages
    - Download chapters if no volumes are available (critical)
    - Download multiple titles
'''


def manga_choice(search_results):
    return questionary.select("Оберіть бажаний тайтл.", choices=search_results).ask()


def main(argv, QUERY=None, download=False, outputpath=''):
    try:
        opts, args = getopt.getopt(
            argv, "hvdo:s:", ["help", "verbose", "download-all", "output=", "search="])
    except getopt.GetoptError:
        print(f"{usage()}")
        exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(f"{usage()}")
            exit(0)
        elif opt in ("-D", "--debug"):
            print("LOGS ARE TRUE")
            logs(True)
        elif opt in ("-o", "--output"):
            outputpath = arg
        elif opt in ("-s", "--search"):
            QUERY = arg
        elif opt in ("-d", "--download-all"):
            download = True

    search = SearchMangaInUa(SITE_URL, HEADERS)

    if download:
        if not QUERY:
            QUERY = questionary.text("Введіть назву манґи: ").ask()
        search_results = search.get_search_results(QUERY)
        check_search_results(search_results)
        selected_manga = manga_choice(search_results)

        if type(selected_manga) == list:
            for i in selected_manga:
                manga_volumes = search.get_all_volumes(i)
                check_volumes(manga_volumes)

                downloaded = search.download_all_volumes(manga_volumes)
                check_downloaded(downloaded)
        else:
            selected_manga = dict(
                {selected_manga: search_results[selected_manga]})
            manga_volumes = search.get_all_volumes(selected_manga)
            check_volumes(manga_volumes)

            downloaded = search.download_all_volumes(manga_volumes, outputpath)
            check_downloaded(downloaded)
    elif not download:
        if not QUERY:
            QUERY = questionary.text("Введіть назву манґи: ").ask()
        search_results = search.get_search_results(QUERY)
        check_search_results(search_results)
        for i in search_results:
            questionary.print(
                f"{i}: {search_results[i]}", style="fg:ansiblue")
