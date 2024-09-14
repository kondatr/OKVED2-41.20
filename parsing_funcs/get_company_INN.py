import openpyxl

#
# Получаем список ИНН компаний из отфильтрованного реестра, представленного в xlsx формате
#

# Открываем .xlsx файл
book = openpyxl.open('data/filtered_reestr.xlsx', read_only=True)

# Выбираем первый лист exel файла
sheet = book.active

# Записываем в .txt файл все ИНН
with open('data/INNs.txt', 'w') as file:
    for raw in range(4, 10577):
        INN = str(sheet[raw][5].value)
        file.write(INN + ',' + '\n')
