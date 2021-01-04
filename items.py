# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import sys
import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Compose, Join
from urllib.parse import urljoin 

pattern_mes_num = re.compile(r"(?<!\d)\d{1,3}(\,\d{1,3})?\s?(л|кг|г|мл){1}(?![a-я])")   #извлекает цифру + ЕИ
pattern_mes = re.compile(r"[а-я]+") #извлекает ЕИ
pattern_num = re.compile(r"\d{1,3}(\,\d{1,3})?") #извлекает фасовку
pattern_price = re.compile(r"\d{1,5}(\,\d{1,3})?") #извлекает цену
pattern_article = re.compile(r"\d+") #извлекает артикул, нас интересуют только цифры
pattern_img = re.compile(r"\d+x\d+") #извлекает ссылку на изображение

def stripper(x):
    """несмотря на двусмысленное название, задача этой функции - получить цену в цифрах, очищенную от букв, точек и прочих символов.
    Args:
        x (str): неочищенная строка, полученная пауком непосредственно с сайта.
    Returns:
        float: цена продукта в десятичном выражении
    """
    res = "".join(x.split())
    try:
        price = pattern_price.search(res).group(0)
    except AttributeError:
        return None
    else:
        return float(price.replace(",","."))

def articler(x):
    """Возвращает цифровой код артикула
    Args:
        x (str): неочищенная строка, полученная пауком непосредственно с сайта.
    Returns:
        str: код артикула, состоящий только из цифр
    """
    try:
        res=pattern_article.search(x).group(0)
    except AttributeError:
        return None
    else:
        return res

def namer(x):
    """Возвращает имя продукта
    Args:
        x (str): неочищенная строка, полученная пауком непосредственно с сайта.
    Returns:
        str: очищенное имя продукта
    """
    return x.replace('\n','').replace('.',',').strip()

def measurer(x):
    """
    Извлекает из названия продукта и возвращает массив из двух значений - единица измерения и фасовка.
    Args:
        x (str): неочищенная строка, полученная пауком непосредственно с сайта.
    Returns:
        list: [единица измерения, фасовка]
    """
    try:
        mes_num = pattern_mes_num.search(x).group(0)
    except AttributeError:
        return None
    else:
        mes = pattern_mes.search(mes_num).group(0) # extract packing (measure)
        pack = pattern_num.search(mes_num).group(0) #extract packing (number)
        if mes == 'г':   #converting measures
            mes = 'кг'
            pack = float(pack.replace(',','.'))/1000
        elif mes == 'мл':
            mes='л'
            pack = float(pack.replace(',','.'))/1000
    return [mes,pack]

def imager(link, loader_context):
    """[summary]
    Args:
        link (str): URL с изображением продукта
        loader_context (dict): scrapy loader_context (https://docs.scrapy.org/en/latest/topics/loaders.html) в данном случае имеющий следующую структуру:
         {base: str, size_changer: (bool, str)}, где под base хранится ссылка на картинку, извлеченная пауком,
          а в кортеже под size_changer - ответ на вопрос "нужно ли получить ссылку на картинку другого размера" и если да, то какой должен быть размер
    Returns:
        str: ссылка на изображение продукта
    """
    try:
        res = urljoin(loader_context['base'], link)
    except AttributeError:
        return None
    else:
        size_changer = loader_context['size_changer']
        if size_changer[0]==True:
                to_change = pattern_img.search(res).group(0)
                res = res.replace(to_change, size_changer[1])
        return res





class Product(scrapy.Item):
    """Класс, содержащий все собираемые сведения о продукте: цена, имя, магазин, артикул, изображение, фасовка и ЕИ.
    Каждый атрибут перед присвоением проходит ETL-этап. Подробнее о самой концепции в рамках scrapy: https://docs.scrapy.org/en/latest/topics/loaders.html#declaring-input-and-output-processors
    """
    price = scrapy.Field(input_processor=MapCompose(stripper),
                         output_processor=TakeFirst())
    name = scrapy.Field(input_processor=MapCompose(namer),
                        output_processor=TakeFirst())
    client = scrapy.Field(output_processor=TakeFirst())
    article = scrapy.Field(input_processor = MapCompose(articler),
                           output_processor = TakeFirst())
    image = scrapy.Field(input_processor = MapCompose(imager),
                         output_processor = TakeFirst())
    packing = scrapy.Field(input_processor = MapCompose(namer, measurer),
                           output_processor = lambda x: x[1])
    measure = scrapy.Field(input_processor = MapCompose(namer, measurer),
                           output_processor = TakeFirst()) 

class ProductLoader(ItemLoader):
    default_item_class = Product #просто чтобы каждый раз внутри пауков не инциализировать продукт


