import pandas as pd
from collections import defaultdict

def read_places_from_file_to_dict(path):
    frame = pd.read_csv(path)
    frame = frame.loc[frame['country'] == "Bangladesh"]
    frame = frame[['city_ascii', 'admin_name']]
    city_admin_dict = defaultdict(list)
    for city, admin_name in zip(frame['city_ascii'], frame['admin_name']):
        city_admin_dict[city.lower()].append(admin_name)
        if not city.endswith('s'):
            plural_city = city + 's'
            city_admin_dict[plural_city.lower()].append(admin_name)
    result_dict = {key: value[0] for key, value in city_admin_dict.items()}
    return result_dict
#gdyby ktoś (ekhem frontend) potrzebował innych danych to można dopisywać tutaj żeby rozgardiaszu nie robić