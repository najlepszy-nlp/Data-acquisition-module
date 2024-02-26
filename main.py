import time
import csv
import json
import requests
from bs4 import BeautifulSoup
from itertools import chain
import re

SITE_URL = f"https://www.unb.com.bd/api/tag-news?tag_id=54&item="
NUMBER_OF_PAGES = 1


def extract_urls(soup):
    links = soup.find_all('a')
    urls = [link.get('href') for link in links if link.get('href') is not None]
    return urls


def HandleLinkFromList(link):
    link_test = link.replace('"', "")
    page = requests.get(link_test)
    soup = BeautifulSoup(page.content, "html.parser")
    data = soup.find_all('ul',class_='post-meta hidden-xs')
    soup = BeautifulSoup(str(data),"html.parser")
    data = soup.find_all('li',class_='news-section-bar')
    temp_soup = BeautifulSoup(str(data),"html.parser")

    data = temp_soup.find_all('li')
    place = data[0].text #potem
    numberOfDates=0
    DateTab=[]
    for html in data:
        rekord=html.find_all('span',class_='icon qb-clock')
        if len(rekord) > 0:
            DateTab.append(html.text.replace("\n","").replace("'",""))
            numberOfDates+=1
    place =""
    for html in data:
        rekord=html.find_all('span',class_='icon fa fa-map-marker')
        if len(rekord) > 0:
            place = html.text

    htmlText=page.content
    soup = BeautifulSoup(page.content, "html.parser")
    text_temp = soup.find_all('div', class_='text')
    soup = BeautifulSoup(str(text_temp[0]), "html.parser")
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    articleText = ' '.join(soup.stripped_strings)
    print(articleText)
    if len(DateTab) == 1:
        return (DateTab[0],"",place,htmlText,articleText)
    else:
        return (DateTab[0],DateTab[1],place,htmlText,articleText)

if __name__ == '__main__':
    final_links = []
    for index in range(1, NUMBER_OF_PAGES + 1):
        page = requests.get(f"{SITE_URL}{index}")
        json_page = json.loads(page.content)

        while len(json_page["html"]) < 1:
            page = requests.get(f"{SITE_URL}{index}")
            json_page = json.loads(page.content)
        soup = BeautifulSoup(page.content, "html.parser")
        links = extract_urls(soup)
        links = list(set(links))
        links = [w.replace("\\", "") for w in links]
        final_links += links
        print(final_links[0])
    # mamy final_links teraz chcemy przez nie przelecieć
    krotka = HandleLinkFromList(link=final_links[0])

    print(krotka)
    with open('C:/Users/bezi1/OneDrive/Dokumenty/output.csv', 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(('Publish', 'Update','HTML_TEXT','RAW_TEXT'))
        csv_out.writerow(krotka)

    exit()
