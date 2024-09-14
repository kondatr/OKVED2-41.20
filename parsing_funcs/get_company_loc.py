import csv
from xml.etree import ElementTree
import requests
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept': "*/*"
}

session = requests.Session()

ns = {
    'gml': 'http://www.opengis.net/gml',
    'ymaps': 'http://maps.yandex.ru/ymaps/1.x'
}

params = {"apikey": "*******-****-****-****-************", "geocode": "", "lang": "ru_RU"}


def read_company_data(filepath):
    ddata = pd.read_csv(filepath, sep="=", engine='python', header=None, encoding='utf-8',
                        names=["Название", "Адрес", "Выручка",
                               "EBITDA по годам", "Изменение ЧП по годам(%)", "Чистая прибыль по годам"])
    return ddata


df = read_company_data('../data/company_info.csv')

with open("../data/locations.csv", "w", encoding='utf-8') as file:
    file_writer = csv.writer(file, delimiter="=", lineterminator="\r")
    for row in df.iloc():
        params['geocode'] = row['Адрес']
        try:
            res = requests.get("https://geocode-maps.yandex.ru/1.x", params=params)
            res.raise_for_status()  # бросает исключение в случае ошибки запроса
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
        else:
            tree = ElementTree.fromstring(res.content)

            # Поиск элемента <gml:pos> с указанием пространства имен
            pos_elem = tree.find('.//gml:pos', ns)
            if pos_elem is not None:
                pos = pos_elem.text

                # Разделение строки на широту и долготу
                lon, lat = pos.split(" ")
            else:
                lon, lat = 0, 0
                print("Не удалось найти элемент")

        file_writer.writerow([row['Название'], row['Адрес'], row['Выручка'], lat, lon])
