#-*- coding: utf-8 -*-

import requests                             #запросы
from bs4 import BeautifulSoup               #обработка контента
from datetime import datetime               #для определении времени работы программы
from time import sleep                      #для слипов
from random import choice                   #для рандома
from random import uniform                  #для рандома с дробной частью
import re                                   #для регулярных выражений
import pymysql                              #для работы с mysql



def get_html(url, useragent=None):
    r = requests.get(url, headers=useragent)                   #гет запрос
    return r.text                                              #возврат страницы в виде текста


def get_all_links(html):                                        #собираем линки на объявы
    soup = BeautifulSoup(html, 'lxml')
    
    ads = soup.find('div', class_='catalog-list').find_all('div', class_='item_table-header')
    links = []
    for ad in ads:
        a = ad.find('a', class_='item-description-title-link').get('href')        
        link = 'https://avito.ru' + a
        links.append(link)
    return links

def get_page_data(html):                                        #сборщик данных с объяв
    soup = BeautifulSoup(html, 'lxml')
    try:
        name = soup.find('h1', class_='title-info-title').text.strip()                                                              #собираем названия
    except:
        name = ''
    try:
        price = soup.find('span', class_='price-value-string js-price-value-string').text.strip().replace('\u20bd','руб.')          #собираем цены
    except:
        price = ''
    try:
        about = soup.find('div', class_='item-description').text.strip()                                                            #собираем текст объяв
    except:
        about = ''
    try:
        user_inf = soup.find('div', class_='seller-info js-seller-info').text.split()                                               #собираем инф о пользователе
        user_info = ' '.join(user_inf)                                                                                              #переводим в строку
    except:
        user_info = ''
    try:
        b = soup.find('div', class_='seller-info-col').find('a').get('href')                                                        #собираем ссылки на профили пользователей
        user_link = 'https://www.avito.ru' + b
    except:
        user_link = ''
    try:
        id = soup.find('div', class_='seller-info-col').find('a').get('href')                                                       #собираем id пользователя с ссылки на профиль
        user_idd = re.findall(r'id=\d\S+\d', id)                                                                                    #выдираем id
        user_id = ', '.join(user_idd)                                                                                               #переводим в строку
    except:
        user_id = ''
    try:
        about_u = soup.find('div', class_='title-info-metadata').text.strip().split()[:6]                                           #выбираем еще инф о размещении объяв
        about2 = ' '.join(about_u)                                                                                                  #переводим в строку
    except:
        about2 = ''
    try:
        fotos = soup.find('ul', class_='gallery-list js-gallery-list').find_all('span', class_='gallery-list-item-link')            #собираем линки на фотки
        s = str(fotos).replace('75x55', '640x480')                                                                                  #из линков на предпросмотр делаем линки на большие фотки
        pics = re.findall(r'//\d\d.img.avito.../640x480/\S+(?:jpg)', s)                                                             #отсеиваем от мусора
        picture = ', '.join(pics)                                                                                                   #переводим в строку
        #print ('picture: ' + picture)
    except:
        picture = ''

    data = [name,price,about,user_info,user_link,user_id,about2,picture]
    
    return data
    

def write_sql(data):
    try:
        conn = pymysql.connect(user="root",passwd="",host="127.0.0.1",port=3306,database="test2",charset='utf8')
    except:
        print('ошибка подключения к mysql, проверить пользователя/пароль')
    try:
        with conn.cursor() as cursor:            
            sql = "INSERT INTO avito(name,price,about,user_info,user_link,user_id,about2,picture) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
            cursor.execute(sql, data)
            conn.commit()
            print('Все успешно записано в БД')
    
    except:
        print('Запись в БД не удалась, проверить кодировки в настройках mysql')

    conn.close()


def main():
    start = datetime.now()                                              #старт таймера

    url = 'https://avito.ru/rossiya/gruzoviki_i_spetstehnika'
    base_url = 'https://avito.ru/rossiya/gruzoviki_i_spetstehnika?'
    page_part = 'p='
    useragents = open('useragents.txt').read().split('\n')

    
    
    for i in range(1, 20):                                               #промежуток страниц, с которых парсятся объявы
        useragent = {'User-Agent': choice(useragents)}
        url_gen = base_url + page_part + str(i)
        print(url_gen)
        all_links = get_all_links( get_html(url_gen) )
        #print (all_links)

        html = get_html(url_gen)
        for link in all_links:
            html = get_html(link)
            get_page_data(html)
            data = get_page_data(html)
            #print(data)
            write_sql(data)
            sleep(uniform(3,5))                                         #пауза с неточным рандомом от и до в секундах между просмотрами каждого объявления
            print (link + ' was parsed')
        sleep(uniform(4,8))                                             #пауза с неточным рандомом от и до в секундах между циклами, можно попробовать убрать.


   
    end = datetime.now()                                                #стоп таймера
    total = end - start                                                 
    print(str(total))                                                   #вывод времени
        



if __name__ == '__main__':
    main()
