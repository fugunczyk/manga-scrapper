from bs4 import BeautifulSoup
import requests
from io import BytesIO
import PIL
from PIL import Image
import os
import difflib

HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.11 (KHTML, like Gecko) '
                      'Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
}
CWD = os.getcwd()
URL_CONST = 'http://www.mangareader.net/'
title_list = []
title_links = []
first_run = True

def find_titles():
    url = "{0}alphabetical".format(URL_CONST)
    source = requests.get(url, headers=HEADER).text
    soup = BeautifulSoup(source, "lxml")
    series_ul = soup.findAll('ul', {"class": "series_alpha"})
    for ul in series_ul:
        series_li = ul.findAll('li')
        for li in series_li:
            link = li.findAll('a')
            for text in link:
                title_list.append(text.text)
                title_links.append(text['href'])

def page_counter(title, chapter_num):
    url = "{0}{1}/{2}".format(URL_CONST,title,chapter_num)
    source = requests.get(url, headers=HEADER).text
    soup = BeautifulSoup(source, "lxml")
    try:
        pages_menu = soup.find('select', {"id": "pageMenu"})
        pages_option = pages_menu.findAll("option")
        if os.path.isdir("{0}/{1}/{2}".format(CWD,title,chapter_num)):
            pass
        else:
            os.makedirs("{0}/{1}/{2}".format(CWD,title,chapter_num))
        print("Chapter #{0} has been found, downloading".format(chapter_num))
        scrap_images(title,chapter_num,len(pages_option))
    except:
        print("Page or chapter not found")

def scrap_images(title,chapter_num,num_of_pages):
    PATH = "{0}/{1}/{2}".format(CWD,title,chapter_num)
    for page_number in range(1,num_of_pages+1):
        url = "{0}{1}/{2}/{3}".format(URL_CONST,title,chapter_num,page_number)
        source = requests.get(url, headers=HEADER).text
        soup = BeautifulSoup(source, "lxml")
        try:
            page_div = soup.find('div', {"id": "imgholder"})
            page_img = page_div.findAll("img")
            for img in page_img:
                img_url = img["src"]
                response = requests.get(img_url)
                page = Image.open(BytesIO(response.content))
                if os.path.isfile("{0}/{1}".format(PATH,img_url.split("/")[-1])):
                    print("file omitted")
                    pass
                else:
                    page.save("{0}/{1}".format(PATH,img_url.split("/")[-1]))
                    print("Image #{0} out of {1}".format(page_number,num_of_pages))
        except:
            print("Image not found")

def single_chapter(title, chapter):
    dictionary = dict(zip(title_list, title_links))
    close_call = difflib.get_close_matches(title, title_list,  n=1)
    if close_call:
        page_counter(dictionary[close_call[0]][1:], chapter)
    else:
        print("Title not found")
    main_menu()

def bulk(title):
    dictionary = dict(zip(title_list, title_links))
    close_call = difflib.get_close_matches(title, title_list,  n=1)
    if close_call:
        url = '{0}{1}'.format(URL_CONST,dictionary[close_call[0]][1:])
        source = requests.get(url, headers=HEADER).text
        soup = BeautifulSoup(source, "lxml")
        main_table = soup.find('table', {"id": "listing"})
        table_tr = main_table.findAll('tr')
        for x in range(1,len(table_tr)):
            page_counter(dictionary[close_call[0]][1:], x)
    else:
        print("Title not found")
    main_menu()

def latest(title):
    dictionary = dict(zip(title_list, title_links))
    close_call = difflib.get_close_matches(title, title_list,  n=1)
    if close_call:
        url = '{0}{1}'.format(URL_CONST,dictionary[close_call[0]][1:])
        source = requests.get(url, headers=HEADER).text
        soup = BeautifulSoup(source, "lxml")
        main_table = soup.find('table', {"id": "listing"})
        table_tr = main_table.findAll('tr')
        page_counter(dictionary[close_call[0]][1:], len(table_tr)-1)
    else:
        print("Title not found")
    main_menu()

def favorites_latest():
    if os.path.isfile("favorites.txt"):
        with open("favorites.txt", "r") as f:
            titles = f.readlines()
        for title in titles:
            latest(title)
    else:
        print("favorites.txt file not found")

def main_menu():
    global first_run
    if first_run:
        print("/"*38)
        print("/ Manga scrapper for mangareader.net /")
        print("/"*38,"\n")
        first_run = False
    print("1. Single chapter download")
    print("2. Whole series bulk download")
    print("3. Latest chapter of given title download")
    print("4. Favorites latest chapters download")
    print("5. Exit")
    while True:
        try:
            selection = int(input("Enter choice: "))
            if selection == 1:
                query = input("Enter manga title and chapter number to download:")
                title = query[0:-1]
                chapter = query[-1:]
                single_chapter(title,chapter)
            elif selection == 2:
                query = input("Enter manga title download whole series:")
                bulk(query)
            elif selection == 3:
                query = input("Enter manga title to download latest chapter:")
                latest(query)
            elif selection == 4:
                favorites_latest()
            elif selection == 5:
                break
            else:
                print("Invalid choice. Enter 1-5")
        except ValueError:
            print("Invalid choice. Enter 1-5")

if __name__ == "__main__":
    find_titles()
    main_menu()
