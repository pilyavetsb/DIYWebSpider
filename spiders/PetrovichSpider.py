from lxml import html
from urllib.request import urlopen, Request
import codecs, json
import unicodedata
from datetime import date
import sys
import re

def petrovich():
    today = str(date.today())
    start = "https://petrovich.ru/catalog/1459/"
    request = Request(start)
    request.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1')
    connect = urlopen(request)
    dom = html.fromstring(connect.read())
    res = list()

    #TODO - переписать на aiohttp
    #получаем список категорий, проходимся по нему и достаем из скриптов json с продуктами
    for link in (dom.xpath("//ul[@class='categories_list']/li[@class = 'categories_list_item small_category']/a/@href")):
        print(link)
        full = "http://petrovich.ru/"+link[1:]
        req = Request(full)
        req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1')
        page = urlopen(req)
        dom1=html.fromstring(page.read())
        lal = dom1.xpath("//*")
        test = dom1.xpath("//script[contains(., '_listDATA')]/text()")

        #чистим строковое представление json так, чтобы это был настоящий json, храним как массив словарей
        spacestrip = " ".join(str(test).split()).replace("amp;", "amp").split(";")[1]
        spacestrip = spacestrip.replace("\\", "")[13:-2].replace("'", "\"")
        spacestrip = spacestrip.split("},{")
        spacestrip = ["{" + i + "}" for i in spacestrip]
        spacestrip = [i.replace("}}", "}").replace("{{", "{") for i in spacestrip]
        spacestrip = [unicodedata.normalize('NFKD', i) for i in spacestrip]

        res.extend(spacestrip)

    res.remove('{"ID" : "4295412692","name" : "Штукатурка текстурная Kapral ST-80 &qu}')
    res.remove('{"ID" : "2952651900","name" : "Краска в/д фактурная Alpina Expert &qu}')
    res=[eval(i) for i in res]
    #this is is the simplest way to create dictionary from a list of dictionary string representations
    res=[{'name':i['name'], 'price':i['priceG'], 'client':'Petrovich', 'article':i['ID']} for i in res]

    def process_item(item):
        #эмулируем пайплайны, выкидывая не ЛКМ
        excluder = ["шпатель", "щетка", "щётка", "щетина", "губка", "валик", "кисть", "брусок", "герметик",
            "бензин", "обезжириватель", "трафарет", "воск", "карандаш", "смывка","шпателей", "клей",
            "трафарет", "мешок", "варежка", "терка", "набор", "салфетки", "черенок", "стеклоочиститель",
            "штор", "подушка", "метла", "ароматизатор", "очиститель", "аппликация", "вышивка", "картины",
            "полироль", "картина", "ваза", "жидкие обои", "добавка", "бюгель", "пистолет", "лента", "крепление",
            "отбеливатель", "скребок", "ручка", "плед", "карниз", "пленка", "жалюзи", "штанга", "держатель",
            "чистящее", "совок", "швабр", "тряпка", "салфетка", "кювет", "плёнка", "уплотнитель", "штрих",
            "маркер", "бленда", "планка", "шина", "кольца", "шампунь", "омыватель", "клипс", "удалитель",
             "очиститель", "диск", "битум", "колорант", "флуорес", "флюорес", "fluores", "эркер", "серебрянка",
             "краситель", "штукатурка", "для удаления", "штамп", "кельма", "паста", "крючок", "карниз", "ксилол",
             "скипидар", "шины", "пена", "фартук", "насадка", "комбинезон", "водосгон", "серпянка", "стержень", "макловица",
             "перчатки", "полотно", "отжим", "наждак", "керосин", "кювета", "ведро для краски"]
        for c,i in enumerate(item):
            if any(substr in item.get('name').lower() for substr in excluder):
                del res[c]
    process_item(res)


    pattern_mes_num = re.compile(r"(?<!\d)\d{1,3}(\,\d{1,3})?\s?(л|кг|г|мл){1}(?![a-я])")   #извлекает цифру + ЕИ
    pattern_mes = re.compile(r"[а-я]+") #извлекает ЕИ
    pattern_num = re.compile(r"\d{1,3}(\,\d{1,3})?")

    def measurer(x):
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

    for i in res:
        i['measure'] = measurer(i['name'][0])
        i['packing'] = measurer(i['name'][1])

    #скидываем все в файл
    with open(f'Petr_{today}.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(res, ensure_ascii=False, sort_keys=True))
