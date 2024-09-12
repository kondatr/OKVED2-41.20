import requests

#
# Парсим id компаний с информационного ресурса "bo.nalog.ru" для получения дальнейшей информации о компаниях
#

# Считываем ИНН компаний в лист
with open('../data/INNs.txt', 'r') as file:
    inns = [inn[:-2] for inn in file.readlines()]

# Открываем "сессию"
session = requests.Session()

# Задаем заголовки (свой user-agent из браузера), чтобы сайт не запрещал доступ
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36'}

# С помощью ранее полученных ИНН отправляем запросы серверу сайта и "выцепляем" с ответа id компаний
# Записываем id в .txt файл
with open('../data/ids.txt', 'w') as file:
    for inn in inns:
        res = session.get(f"https://bo.nalog.ru/advanced-search/organizations/search?query={inn}&page=0",
                          headers=headers).json()
        if len(res["content"]) == 0:
            continue
        org_id = res["content"][0]["id"]
        file.write(str(org_id) + ',' + '\n')