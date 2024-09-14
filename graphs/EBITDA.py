import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

def read_company_data(filepath):
    data = pd.read_csv(filepath, sep="=", engine='python', header=None, encoding='utf-8',
                       names=["Название", "Адрес", "Выручка по годам",
                              "EBITDA по годам", "Изменение ЧП по годам(%)", "Чистая прибыль по годам"])
    return data

def get_totals():
    EBITDA_by_years = pd.DataFrame([row['EBITDA по годам'][1:-1].split(',')
                                    for row in read_company_data('data/company_info.csv').iloc],
                                   columns=[f'EBITDA за {2023 - i} год' for i in range(5)])
    revenue_by_years = pd.DataFrame([row['Выручка по годам'][1:-1].split(',')
                                    for row in read_company_data('data/company_info.csv').iloc],
                                   columns=[f'Выручка за {2023 - i} год' for i in range(5)])
    totals = pd.DataFrame()

    for i in range(5):
        EBITDA_by_years[f'EBITDA за {2019 + i} год'] = pd.to_numeric(EBITDA_by_years[f'EBITDA за {2019 + i} год'],
                                                                     errors='coerce')

        revenue_by_years[f'Выручка за {2023 - i} год'] = pd.to_numeric(revenue_by_years[f'Выручка за {2023 - i} год'],
                                                                     errors='coerce')

        revenue = sum(revenue_by_years[f'Выручка за {2023 - i} год'][
            revenue_by_years[f'Выручка за {2023 - i} год'].notnull()]) / 1_000_000

        sum_EBITDA = sum(EBITDA_by_years[f'EBITDA за {2019 + i} год'][
            EBITDA_by_years[f'EBITDA за {2019 + i} год'].notnull()]) / 1_000_000
        av_EBITDA = EBITDA_by_years[f'EBITDA за {2019 + i} год'][
            EBITDA_by_years[f'EBITDA за {2019 + i} год'].notnull()].mean() / 1_000
        median_EBITDA = EBITDA_by_years[f'EBITDA за {2019 + i} год'][
            EBITDA_by_years[f'EBITDA за {2019 + i} год'].notnull()].median() / 1_000
        count = EBITDA_by_years[f'EBITDA за {2019 + i} год'][
            EBITDA_by_years[f'EBITDA за {2019 + i} год'].notnull()].count()

        totals = pd.concat([totals, pd.DataFrame({'sum': [sum_EBITDA],
                                                  'average': [av_EBITDA],
                                                  'median': [median_EBITDA],
                                                  'revenue': [revenue],
                                                  'count': [count],
                                                  'year': [str(2019 + i) + 'г.']
                                                  })],
                           ignore_index=True)
    return totals


def av_med_EBITDA_graph():
    totals = get_totals()
    fig, ax = plt.subplots(1)
    ax.set_xlabel(' ')
    ax.set_ylabel('млн. руб.')
    ax.set_title('Динамика изменения EBITDA', fontsize=16, weight='bold')
    ax.grid(True)

    sns.lineplot(data=totals, x='year', y='average', color='orange')
    sns.scatterplot(data=totals, x='year', y='average', markers='o', s=100, label="Средняя", color='orange')
    sns.histplot(data=totals, x='year', weights='average', alpha=0.5, color='orange')

    sns.lineplot(data=totals, x='year', y='median', color='green')
    sns.scatterplot(data=totals, x='year', y='median', markers='o', s=100, label="Медианная", color='green')
    sns.histplot(data=totals, x='year', weights='median', color='green', alpha=0.5)

def EBITDA_graph():
    totals = get_totals()

    fig, ax1 = plt.subplots(1)

    ax1.set_xlabel(' ')
    ax1.set_ylabel(' ')
    ax1.set_title('Динамика изменения EBITDA отрасли', fontsize=16, weight='bold')
    ax1.tick_params(axis='y', labelcolor='orange')
    ax1.set_ylim(0, 300)
    ax1.grid(True)

    sns.lineplot(data=totals, x='year', y='sum', color='orange')
    sns.scatterplot(data=totals, x='year', y='sum', markers='o', s=100, color='orange')
    sns.histplot(data=totals, x='year', weights='sum', alpha=0.5, color='orange', label="EBITDA, млрд. руб.")
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.set_ylabel(' ')
    ax2.set_yticks(np.arange(1, 16, 2))
    ax2.set_ylim(0, 16)
    ax2.tick_params(axis='y', labelcolor='red')

    percentage = totals['sum'] / totals['revenue'] * 100
    sns.lineplot(ax=ax2, data=totals, x='year', y=percentage, color='red', label="Рентабельность EBITDA, %")
    sns.scatterplot(ax=ax2, data=totals, x='year', y=percentage, color='red', s=10)

    for i in range(len(totals)):
        ax2.text(totals['year'][i], percentage[i] + 1, f'{percentage[i]:.2f}%', color='red', ha='center',
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

    ax2.legend(loc='upper right')
