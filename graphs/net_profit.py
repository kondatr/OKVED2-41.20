import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import seaborn as sns
import pandas as pd


def read_company_data(filepath):
    data = pd.read_csv(filepath, sep="=", engine='python', header=None, encoding='utf-8',
                       names=["Название", "Адрес", "Выручка",
                              "EBITDA по годам", "Изменение ЧП по годам(%)", "Чистая прибыль по годам"])
    return data


def get_formal_data(i):
    profit_by_years = pd.DataFrame([row['Изменение ЧП по годам(%)'][1:-1].split(',')
                                    for row in read_company_data('data/company_info.csv').iloc],
                                   columns=[f'Изменение ЧП спустя {i + 1} год(а)' for i in range(4)])
    profit_by_years[f'Изменение ЧП спустя {i + 1} год(а)'] = \
        pd.to_numeric(profit_by_years[f'Изменение ЧП спустя {i + 1} год(а)'],
                      errors='coerce')

    # Сортируем данные для оси x
    counter = Counter(profit_by_years[f'Изменение ЧП спустя {i + 1} год(а)']
                      [profit_by_years[f'Изменение ЧП спустя {i + 1} год(а)'].notnull()])

    percents = [int(x) if x is not None else 0 for x in sorted(counter.keys())]
    n_companies = [int(x) if x is not None else 0 for x in [counter[p] for p in percents]]

    ddata = {
        'x': percents,
        'y': n_companies,
        'x*y': [p * n for p, n in zip(percents, n_companies)]
    }

    df = pd.DataFrame(ddata)
    full_x = range(-5000, 5001)
    df_full = pd.DataFrame({'x': full_x}).merge(df, how='left', on='x').fillna(0)

    count_pos = sum(df[df['x'] >= 0]['y'])
    count_neg = sum(df[df['x'] < 0]['y'])

    totals = pd.DataFrame({
        'Сумма': [abs(sum(df[df['x'] < 0]['x'] * df[df['x'] < 0]['y'])),
                  sum(df[df['x'] >= 0]['x'] * df[df['x'] >= 0]['y'])],
        'Знак': ['Падение', 'Рост'],
        'Количество': [count_neg, count_pos]
    })
    return df, df_full, totals


def growth_years_graph():
    # Настройка фигуры (4 строки, 1 столбец)
    fig, axs = plt.subplots(4, 1, figsize=(16, 20))

    for i, ax in enumerate(axs):
        df, df_full, totals = get_formal_data(i)
        # Убираем оси у "контейнера" ax
        ax.axis('off')

        # Большой график
        ax_main = fig.add_subplot(plt.GridSpec(4, 4)[i, 0:3])
        ax_main.fill_between(df_full[df_full['x'] >= 0]['x'], 0, df_full[df_full['x'] >= 0]['y'],
                             color=sns.color_palette()[0])
        ax_main.fill_between(df_full[df_full['x'] < 0]['x'], 0, df_full[df_full['x'] < 0]['y'],
                             color=sns.color_palette()[3])
        ax_main.set_xlim(-5000, 5000)
        ax_main.set_ylim(0, 40)
        ax_main.set_ylabel('Количество компаний')
        ax_main.set_xlabel('Изменение чистой прибыли(%)')
        ax_main.set_xticks(np.arange(-5000, 5001, 1000))

        ax_main.text(x=-3000, y=30, s=str(totals['Количество'][0])+" компаний", color='red',
                 horizontalalignment='left', verticalalignment='top')
        ax_main.text(x=3000, y=30, s=str(totals['Количество'][1])+" компаний", color='blue',
                 horizontalalignment='right', verticalalignment='top')
        # Маленький график
        ax_inset = fig.add_subplot(plt.GridSpec(4, 4)[i, 3])
        sns.histplot(data=totals, x='Знак', hue='Знак', weights='Количество',
                     ax=ax_inset, legend=False, palette={'Падение': 'red', 'Рост': 'blue'})
        ax_inset.set_xlabel(' ')
        ax_inset.set_ylabel('Количество компаний')
        ax_inset.set_yticks([])
        ax_inset.grid()

        # Добавляем заголовок над графиками
        ax.set_title(f'Изменение чистой прибыли спустя {i + 1} год(а)', fontsize=16, weight='bold')
        plt.subplots_adjust(hspace=0.6)


def net_profit_graph():
    profit_by_years = pd.DataFrame([row['Чистая прибыль по годам'][1:-1].split(',')
                                    for row in read_company_data('data/company_info.csv').iloc],
                                   columns=[f'Чистая прибыль за {2023 - i} год' for i in range(5)])

    data = pd.DataFrame()
    for i in range(5):
        profit_by_years[f'Чистая прибыль за {i + 2019} год'] = pd.to_numeric(
            profit_by_years[f'Чистая прибыль за {i + 2019} год'], errors='coerce')

        av_profit = profit_by_years[f'Чистая прибыль за {i + 2019} год'][
            profit_by_years[f'Чистая прибыль за {i + 2019} год'].notnull()].mean()
        median_profit = profit_by_years[f'Чистая прибыль за {i + 2019} год'][
            profit_by_years[f'Чистая прибыль за {i + 2019} год'].notnull()].median()

        count = profit_by_years[f'Чистая прибыль за {i + 2019} год'][
            profit_by_years[f'Чистая прибыль за {i + 2019} год'].notnull()].count()

        data = pd.concat([data, pd.DataFrame({'average': [av_profit],
                                              'median': [median_profit],
                                              'count': [count],
                                              'year': [str(i + 2019) + 'г.']
                                              })],
                         ignore_index=True)

    fig, ax = plt.subplots(1)

    ax.set_xlabel(' ')
    ax.set_ylabel('тыс. руб.')
    ax.set_title('Чистая прибыль', fontsize=16, weight='bold')
    ax.grid(True)
    sns.lineplot(data=data, x='year', y='average', color='orange',)
    sns.scatterplot(data=data, x='year', y='average', markers='o', s=100, label="Средняя", color='orange')
    sns.histplot(data=data, x='year', weights='average', color='orange', alpha=0.5)

    sns.lineplot(data=data, x='year', y='median', color='green')
    sns.scatterplot(data=data, x='year', y='median', markers='o', s=100, label="Медианная", color='green')
    sns.histplot(data=data, x='year', weights='median', color='green', alpha=0.5)


def net_profit_change_graph():
    fig, ax = plt.subplots(1, figsize=(10, 7))
    y = []
    x = ['Спустя 1 год', 'Спустя 2 года', 'Спустя 3 года', 'Спустя 4 года']
    for i in range(4):
        _, _, totals = get_formal_data(i)
        y.append(totals['Количество'][1]-totals['Количество'][0])

    bar = sns.barplot(x=y, y=x, hue=x, legend=False)
    for index, value in enumerate(y):
        bar.text(value + 0.1, index, value, va='center')

    ax.set_xlabel(' ')
    ax.set_ylabel(' ')
    ax.set_title('Разница между количеством компаний (рост - падение)', fontsize=16, weight='bold')