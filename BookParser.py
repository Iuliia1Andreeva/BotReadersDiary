from bs4 import BeautifulSoup

from time import sleep

import requests

import pandas as pd

from fake_useragent import UserAgent

url = "https://www.labirint.ru/genres/3000/"

response = requests.get(url, headers={'User-Agent': UserAgent().chrome})
# for key, value in response.request.headers.items():
# print(key+": "+value)

print(response)
soup = BeautifulSoup(response.text, 'html.parser')

types = soup.find_all("a", rel="nofollow")

starting_page = 'https://www.labirint.ru'

list_of_genres = []
list_of_genres_without_href = []
name_of_genres = []
for tipe in types:
    if tipe.text != '' and tipe.get('href')[:5] == "/genr" and tipe.text not in name_of_genres:
        sublist = [tipe.text, tipe.get('href')]
        name_of_genres.append(tipe.text)  # name of table
        list_of_genres.append(sublist)
        list_of_genres_without_href.append(tipe.text)

# name, href, discription, image

list_of_book_hrefs = []
list_of_books_names = []
list_of_books_descriptions = []
list_of_books_images = []
list_of_books_genres = []

about_books = []
for i in range(len(list_of_genres)):
    new_url = starting_page + list_of_genres[i][1]
    print(new_url)
    new_response = requests.get(new_url, headers={'User-Agent': UserAgent().chrome})
    genre = BeautifulSoup(new_response.text, 'html.parser')
    books = genre.find_all("a", class_="cover cover-tooltip")
    for book in books:
        list_of_books_genres.append(list_of_genres[i][0])
        about_books.append([list_of_genres[i][0], book.get('title')])
        list_of_book_hrefs.append(book.get('href'))
        list_of_books_names.append(book.get('title'))
        sleep(1)
        list_of_books_images.append(book.parent.parent.find("img").get("data-src"))
        book_url = starting_page + book.get('href')
        sleep(1)
        print(book_url)
        book_response = requests.get(book_url, headers={'User-Agent': UserAgent().chrome})
        # print(book_response)
        detail = BeautifulSoup(book_response.text, 'html.parser')
        sleep(1)
        detail_ = detail.find(id="fullannotation")
        if detail_ is not None:
            list_of_books_descriptions.append(detail_.p)
        else:
            list_of_books_descriptions.append(None)

boooks_dict = {"list_of_book_names": list_of_books_names, 'list_of_books_descriptions': list_of_books_descriptions,
               "list_of_books_images": list_of_books_images, "list_of_book_hrefs": list_of_book_hrefs,
               "list_of_books_genres": list_of_books_genres}

BookData = pd.DataFrame(boooks_dict, columns=boooks_dict.keys())
BookData.to_csv('BookData.csv')
