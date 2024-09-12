import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def convert_crs(geo_df, to_crs='EPSG:32646'):
    # Преобразование CRS для GeoDataFrame
    return geo_df.to_crs(to_crs)


def read_company_data(filepath):
    data = pd.read_csv(filepath, sep="=", engine='python', header=None, encoding='utf-8',
                       names=["name", "address", "revenue",
                              "lat", "lon"])
    return data


def coords_companies(companies):
    # Преобразование координат компаний
    geometry = gpd.points_from_xy(companies['lon'], companies['lat'], crs='EPSG:4326')
    gdf_companies = gpd.GeoDataFrame(companies, geometry=geometry)
    gdf_companies = convert_crs(gdf_companies)

    return gdf_companies


def merge_company_with_region(top_companies, country):
    # Преобразование CRS
    country = convert_crs(country)

    # Определение региона для каждой компании через spatial join
    companies_with_regions = gpd.sjoin(coords_companies(top_companies), country, how='left', predicate='within')

    # Агрегация количества компаний по регионам
    company_counts_by_region = companies_with_regions.groupby('region').size().reset_index(name='company_count')

    # Присоединение данных о плотности компаний к регионам
    country = country.merge(company_counts_by_region, on='region', how='left').fillna({'company_count': 0})

    # Логарифмическая шкала для отображения плотности
    country['log_company_count'] = np.log1p(country['company_count'])

    return country


def revenue_map():
    # Чтение данных о компаниях и регионах
    top_companies = read_company_data('data/locations.csv')
    country = gpd.read_file("data/Russia_regions.geojson")

    # Построение графика
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Построение карты с отображением плотности
    merge_company_with_region(top_companies, country).plot(column='log_company_count', ax=ax, cmap='Blues',
                                                           legend=False)

    # Добавление точек компаний на карту
    ax.scatter(coords_companies(top_companies).geometry.x, coords_companies(top_companies).geometry.y, s=12,
               color="purple", alpha=0.6, marker="*")
    ax.set_title('Плотность компаний по регионам', fontsize=16, weight='bold')

    # Скрытие осей x и y
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)


def revenue_top10_graph():
    # Чтение данных о компаниях и регионах
    top_companies = read_company_data('data/locations.csv')
    country = gpd.read_file("data/Russia_regions.geojson")

    data = merge_company_with_region(top_companies, country)

    # Построение графика
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    top10 = data.sort_values('company_count', ascending=False, ignore_index=True).head(10)

    sns.histplot(ax=ax, data=top10, x='region', weights='company_count', hue='company_count',
                 palette='Blues', legend=False, shrink=0.7)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
    ax.set_title('Топ 10 регионов', fontsize=16, weight='bold')
    ax.set_ylabel("Количество компаний")