import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def read_company_data(filepath):
    data = pd.read_csv(filepath, sep="=", engine='python', header=None, encoding='utf-8',
                       names=["Название", "Адрес", "Выручка",
                              "EBITDA по годам", "Изменение ЧП по годам(%)", "Чистая прибыль по годам"])
    return data

def get_totals():
    EBITDA_by_years = pd.DataFrame([row['EBITDA по годам'][1:-1].split(',')
                                    for row in read_company_data('data/company_info.csv').iloc],
                                   columns=[f'EBITDA за {2023 - i} год' for i in range(5)])

    totals = pd.DataFrame({
        'average': [],
        'median': [],
        'year': []
    })

    for i in range(5):
        EBITDA_by_years[f'EBITDA за {2019 + i} год'] = pd.to_numeric(EBITDA_by_years[f'EBITDA за {2019 + i} год'],
                                                                     errors='coerce')
        av_EBITDA = EBITDA_by_years[f'EBITDA за {2019 + i} год'][
            EBITDA_by_years[f'EBITDA за {2019 + i} год'].notnull()].mean()
        median_EBITDA = EBITDA_by_years[f'EBITDA за {2019 + i} год'][
            EBITDA_by_years[f'EBITDA за {2019 + i} год'].notnull()].median()

        totals = pd.concat([totals, pd.DataFrame({'average': [av_EBITDA],
                                                  'median': [median_EBITDA],
                                                  'year': [str(2019 + i) + 'г.']
                                                  })],
                           ignore_index=True)
    return totals


def EBITDA_graph():
    totals = get_totals()
    fig, ax = plt.subplots(1)

    ax.set_xlabel('Год')
    ax.set_ylabel('тыс. руб.')
    ax.set_title('EBITDA по годам', fontsize=16, weight='bold')
    ax.grid(True)
    sns.lineplot(data=totals, x='year', y='average')
    sns.scatterplot(data=totals, x='year', y='average', markers='o', s=100, label="Средняя")

    sns.lineplot(data=totals, x='year', y='median')
    sns.scatterplot(data=totals, x='year', y='median', markers='o', s=100, label="Медианная")
