import csv
import json
import requests
from bs4 import BeautifulSoup
from lxml import etree
from io import StringIO
import CitiesListProcessing as clp
from datetime import datetime, timedelta
import cars_words as cars

SITE_URL = "https://www.unb.com.bd/api/tag-news?tag_id=54&item="
NUMBER_OF_PAGES = 118
date_list = []


def get_json_data(url):
    response = requests.get(url)
    return json.loads(response.content)


def extract_urls(json_data):
    soup = BeautifulSoup(json_data["html"], "html.parser")
    links = soup.find_all('a')
    urls = set(link.get('href').replace("\\", "") for link in links if link.get('href'))
    return urls


def check_link_for_city(link, citiesDict):
    noPrefixLink = link.replace("https://www.unb.com.bd/category/Bangladesh/", "")
    index = noPrefixLink.find("/")
    readyToParseLink = noPrefixLink[:index]
    wordsList = readyToParseLink.split("-")
    for word in wordsList:

        # check if word is in districts to cities dict
        if word.lower() in citiesDict.keys():
            return citiesDict[word].lower()

        # check if word is in ciries dict
        if word.lower() in cities:
            return word

        if word.lower() in district_to_region.keys():
            return district_to_region[word.lower()]

    # if above steeps fail return empty string
    return ""


def check_text_for_city(articleText: str):
    cityName = articleText.split(",")[0]
    if cityName.lower() in cities:
        return cityName
    if cityName.lower() in district_to_region.keys():
        return district_to_region[cityName.lower()]
    return ""


def process_link(link, citiesDict):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")

    date_data = soup.find_all('ul', class_='post-meta hidden-xs')
    date_data = BeautifulSoup(str(date_data), "html.parser").find_all('li', class_='news-section-bar')
    dates = [item.text.replace("\n", "").replace("'", "") for item in date_data if 'qb-clock' in str(item)]
    # if dates are not provided take the oldest one
    if len(dates) == 0:
        min_date = min(date_list)
        dates[0] = min_date.strftime('%B %d, %Y')

    # make dates into correct format Month day, year
    for i in range(len(dates)):
        date = dates[i]
        date = date.replace("Publish- ", "").replace("Update- ", "")
        date_table = date.split(",")
        dates[i] = f"{date_table[0]},{date_table[1]}"

    # if no update date provided make it have a publish date instead
    if len(dates) == 1:
        dates.append(dates[0])

    # handle the oldest date mechanism

    if len(dates) > 0:
        # convert our date to datetime format
        date = dates[0]
        date_datatime = datetime.strptime(date, '%B %d, %Y')

        # append to our list
        date_list.append(date_datatime)

    htmlText = response.content.decode('utf-8').replace('\n', ' ').replace(';', '')
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(htmlText), parser)
    for s in tree.xpath('//script'):
        s.getparent().remove(s)
    htmlText = str(etree.tostring(tree.getroot(), pretty_print=True))
    article_soup = BeautifulSoup(htmlText, "html.parser")
    text_div = article_soup.find('div', class_='text')
    if text_div:
        for tag in text_div(['style', 'script', 'a']):
            tag.decompose()
        articleText = ' '.join(text_div.stripped_strings).replace(';', '').replace('&nbsp', '').replace('\\', '')
    else:
        articleText = ""
    if [item.text for item in date_data if 'fa-map-marker' in str(item)]:
        place = [item.text for item in date_data if 'fa-map-marker' in str(item)][0] if date_data else ""
    else:
        place = check_link_for_city(link, citiesDict)
        if place == "":
            place = check_text_for_city(articleText)
        if place == "":
            print(link)
            place = "Sosnowiec"
    if check_text_for_car(articleText):
        return (dates[0], dates[1] if len(dates) > 1 else "", place, htmlText, articleText, link)
    else:
        return False


def check_text_for_car(articleText):
    tab = articleText.split()
    for word in tab:
        if word.lower() in cars.CAR_RELATED_WORDS:
            return True
    return False


def save_to_csv(data, filepath):
    with open(filepath, 'w', newline='', encoding='utf-8') as out:
        csv_out = csv.writer(out, delimiter=';')
        csv_out.writerow(('Publish', 'Update', 'Place', 'HTML_TEXT', 'RAW_TEXT', 'Url'))
        for row in data:
            csv_out.writerow(row)


if __name__ == '__main__':
    all_data = []
    district_to_region = clp.get_data_from_wikipedia_table("wikipedia_table_districts.txt.txt")
    temp = clp.read_places_from_file_to_dict("./worldcities.csv")
    citiesDict = temp[0]
    cities = temp[1].tolist()
    cities = list(map(lambda city: city.lower(), cities))
    links_used = []
    for index in range(1, NUMBER_OF_PAGES + 1):
        json_data = get_json_data(f"{SITE_URL}{index}")
        urls = extract_urls(json_data)
        for link in urls:
            if not "Bangladesh" in link:
                continue
            if link in links_used:
                continue
            links_used.append(link)
            link_data = process_link(link, citiesDict)
            print(link)
            if link_data != False:
                all_data.append(link_data)

        # get oldest date, subtract one day append it to the list
        # this is done for articles without date
        # so we can substitute the publish date for them
        min_date = min(date_list)
        one_day = timedelta(days=1)
        new_oldest_date = min_date - one_day
        date_list.append(new_oldest_date)

    save_to_csv(all_data, './abc.txt')
