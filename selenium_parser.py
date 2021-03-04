import csv

from collections import OrderedDict
from icecream import ic
from selenium import webdriver

from private_settings import MARKET_URL


def csv_writer(list):
    """Запись названия нот и ID  в CSV файл """
    ordered_fieldnames = OrderedDict([('sheets_name', None), ('sheets_id', None), ('sheets_file', None)])
    for product in list:
        ic(product)
        with open('databases/sheets_info.csv', "a", newline='', encoding='utf-8') as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=ordered_fieldnames)
            writer.writerow(product)

def main():
    """Получение названия нот и уникального ID из маркета ВК"""
    driver = webdriver.Chrome()
    driver.get(MARKET_URL)
    title_market= driver.find_elements_by_class_name('market_row')
    all_products = []
    for market in title_market:
        market_row_name = market.find_element_by_class_name('market_row_name')
        data = market_row_name.find_element_by_tag_name('a')
        sheet_name = data.text
        sheet_id = data.get_attribute('onclick')[-16:-9]
        all_products.append({'sheets_name':sheet_name, 'sheets_id':sheet_id, 'sheets_file': None})
    ic(all_products)

    csv_writer(list=all_products)

if __name__ == '__main__':
   main()

