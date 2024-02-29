import csv
import json
import requests
from bs4 import BeautifulSoup
from lxml import etree
from io import StringIO
import CitiesListProcessing as clp


SITE_URL = "https://www.unb.com.bd/api/tag-news?tag_id=54&item="
NUMBER_OF_PAGES = 118


def get_json_data(url):
    response = requests.get(url)
    return json.loads(response.content)


def extract_urls(json_data):
    soup = BeautifulSoup(json_data["html"], "html.parser")
    links = soup.find_all('a')
    urls = set(link.get('href').replace("\\", "") for link in links if link.get('href'))
    return urls

def check_link_for_city(link,citiesDict):
    noPrefixLink = link.replace("https://www.unb.com.bd/category/Bangladesh/","")
    index = noPrefixLink.find("/")
    readyToParseLink = noPrefixLink[:index]
    wordsList = readyToParseLink.split("-")
    for word in wordsList:
        if word.lower() in citiesDict.keys():
            return citiesDict[word].lower()
    return ""


def process_link(link,citiesDict):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")

    date_data = soup.find_all('ul', class_='post-meta hidden-xs')
    date_data = BeautifulSoup(str(date_data), "html.parser").find_all('li', class_='news-section-bar')
    dates = [item.text.replace("\n", "").replace("'", "") for item in date_data if 'qb-clock' in str(item)]
    if [item.text for item in date_data if 'fa-map-marker' in str(item)]:
        place = [item.text for item in date_data if 'fa-map-marker' in str(item)][0] if date_data else ""
    else:
        place = check_link_for_city(link,citiesDict)
        if place == "":
            print(link)
            place = "Sosnowiec"
    htmlText = response.content.decode('utf-8').replace('\n', ' ').replace(';','')
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(htmlText), parser)
    for s in tree.xpath('//script'):
        s.getparent().remove(s)
    htmlText = str(etree.tostring(tree.getroot(), pretty_print=True))
    article_soup = BeautifulSoup(htmlText, "html.parser")
    text_div = article_soup.find('div', class_='text')
    if text_div:
        for tag in text_div(['style', 'script']):
            tag.decompose()
        articleText = ' '.join(text_div.stripped_strings).replace(';','')
    else:
        articleText = ""

    return (dates[0], dates[1] if len(dates) > 1 else "", place, htmlText, articleText)


def save_to_csv(data, filepath):
    with open(filepath, 'w', newline='', encoding='utf-8') as out:
        csv_out = csv.writer(out, delimiter=';')
        csv_out.writerow(('Publish', 'Update', 'Place', 'HTML_TEXT', 'RAW_TEXT'))
        for row in data:
            csv_out.writerow(row)


if __name__ == '__main__':
    all_data = []
    citiesDict = clp.read_places_from_file_to_dict("./worldcities.csv")
    for index in range(1, NUMBER_OF_PAGES + 1):
        json_data = get_json_data(f"{SITE_URL}{index}")
        urls = extract_urls(json_data)
        for link in urls:
            if not "Bangladesh" in link:
                continue
            link_data = process_link(link,citiesDict)
            all_data.append(link_data)
    save_to_csv(all_data, './abc.txt')
