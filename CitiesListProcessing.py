import pandas as pd
from collections import defaultdict
from bs4 import BeautifulSoup

def read_places_from_file_to_dict(path):
    frame = pd.read_csv(path)
    frame = frame.loc[frame['country'] == "Bangladesh"]
    frame = frame[['city_ascii', 'admin_name']]
    city_admin_dict = defaultdict(list)
    for city, admin_name in zip( frame['admin_name'],frame['city_ascii']):
        city_admin_dict[city.lower()].append(admin_name)
        if not city.endswith('s'):
            plural_city = city + 's'
            city_admin_dict[plural_city.lower()].append(admin_name)
    result_dict = {key: value[0] for key, value in city_admin_dict.items()}
    return (result_dict,frame['city_ascii'])

def get_data_from_wikipedia_table(path):
    # Parse the HTML content
    stream = open(path,"r")
    html_content = stream.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract column headers
    columns = [th.get_text().strip() for th in soup.find_all('th')]

    # Extract data rows
    data = []
    for row in soup.find_all('tr')[1:]:
        row_data = [td.get_text().strip() for td in row.find_all('td')]
        data.append(row_data)
    df = pd.DataFrame(data)

    # since data is weirdly structured we have to add cities labels 
    new_division = 'Barisal'
    for index, row in df.iterrows():
        if df.iat[index, 1] is None:
            continue
        if df.iat[index, 1].isnumeric():
            df.iat[index, 1] = new_division
        else:
            new_division = row.iloc[1]

    # Delete rows where second column is none
    df = df.dropna(subset=[df.columns[1]])
    df[df.columns[0]] = df[df.columns[0]].str.lower()
    df[df.columns[1]] = df[df.columns[1]].str.lower()
    #return dictionary made from first two columns
    df.set_index(df.columns[0], inplace=True)
    result_dict = df[df.columns[0]].to_dict()
    return result_dict


#gdyby ktoś (ekhem frontend) potrzebował innych danych to można dopisywać tutaj żeby rozgardiaszu nie robić