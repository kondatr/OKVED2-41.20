import requests
import csv

#
# Получаем финансовые показатели компаний
#

def reduce_extend_len(llist, target_len):
    return llist[:target_len] + ["nan"]*(target_len - len(llist))

# Считываем id компаний в лист
with open('../data/ids.txt', 'r') as file:
    ids = [idd[:-2] for idd in file.readlines()]

# Открываем сессию
session = requests.Session()

# Задаем заголовки (свой user-agent из браузера), чтобы сайт не запрещал доступ
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept': "*/*"
}

# С помощью ранее полученных id отправляем запросы серверу сайта и получаем EBITDA по годам, процент роста прибыли по
# годам, выручку, название и адресс компаний Записываем полученные финансовые показатели в .txt файл

with open("../data/company_info.csv", "w", encoding='utf-8') as file:
    file_writer = csv.writer(file, delimiter="=", lineterminator="\r")

    for idd in ids:
        try:
            res = session.get(
                f"https://bo.nalog.ru/nbo/organizations/{idd}/bfo/", headers=headers).json()
        except:
            continue

        EBITDA_years = []  # EBITDA по годам
        perc_of_growth_years = []  # Процент роста прибыли по годам
        net_profit_years = []   # Чистая прибыль по годам
        revenue_years = []  # Выручка по годам

        if res[0].get('correction').get('financialResult') is None:
            continue

        for i in range(0, len(res)):
            finance_res = res[i].get('correction').get('financialResult')

            if finance_res is None:
                EBITDA_years.append("nan")
                perc_of_growth_years.append("nan")
                continue

            cost = finance_res.get('current2120')  # Себестоимость
            income_tax = finance_res.get('current2410')  # Налог на прибыль
            interest_to_pay = finance_res.get('current2330')  # Проценты к уплате
            rev = finance_res.get('current2110')  # Выручка

            if all([cost, income_tax, rev, interest_to_pay]):
                EBITDA_years.append(
                    rev - cost + income_tax + interest_to_pay)
            else:
                EBITDA_years.append("nan")

            net_profit = finance_res.get('current2400')
            net_profit_2023 = res[0].get('correction'). \
                get('financialResult').get('current2400')  # Чистая прибыль за 2023

            if net_profit_2023 and net_profit:
                perc_of_growth = round((net_profit_2023 - net_profit) / abs(net_profit) * 100)
            else:
                perc_of_growth = "nan"
            perc_of_growth_years.append(perc_of_growth)

            if net_profit:
                net_profit_years.append(net_profit)
            else:
                net_profit_years.append("nan")

            if rev:
                revenue_years.append(rev)
            else:
                revenue_years.append("nan")

        # Сбор данных о компании
        name = res[0].get('organizationInfo').get('fullName')  # Название компании
        address = res[0].get('organizationInfo').get('address')  # Адрес компании

        file_writer.writerow([name, address, str(reduce_extend_len(revenue_years, 5)), str(reduce_extend_len(EBITDA_years, 5)),
                              str(reduce_extend_len(perc_of_growth_years, 5)[1:]), net_profit_years])
