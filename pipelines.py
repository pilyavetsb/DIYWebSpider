# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem 

class NamePricePipeline(object):
    """
    Пайплайн. задача которого не пропустить в конечный файл объекты без имени, цены или артикула
    """
    def process_item(self, item, spider):
        """Проверяет, есть ли у айтема имя, цена и артикул. Если нет хотя бы одного, айтем не попадает в финальную базу.
        Args:
            item (scrapy.Item): вытащенный пауком айтем
            spider (scrapy.Spider): сам паук
        Raises:
            DropItem: айтем не попадает в следующий пайплайн и не попадает в финальную базу
        Returns:
            Item: айтем с минимально необходимым набором атрибутов
        """
        if item.get('name') and item.get('price') and item.get('article'):
            return item
        else:
            raise DropItem(f"Missing name or price in {item}")

class ExcluderPipeline(object):
    """Исключает айтемы, не относящиеся к ЛКМ
    """
    def process_item(self, item, spider):
        """Исключает айтемы, не относящиеся к ЛКМ
        Args:
            item (scrapy.Item): вытащенный пауком айтем
            spider (scrapy.Spider): сам паук
        Raises:
            DropItem: айтем не попадает в следующий пайплайн и не попадает в финальную базу
        Returns:
            Item: айтем с минимально необходимым набором атрибутов, относящийся к ЛКМ
        """
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
        if any(substr in item.get('name').lower() for substr in excluder):
            raise DropItem("Не ЛКМ, а шляпа какая-то")
        else:
            return item


class DuplicatePipeline(object):
    """[summary]
    Удаляет полные дубликаты
    """
    def __init__(self):
        self.items_seen = set()

    def process_item(self, item, spider):
        if item['article'] in self.items_seen:
            raise DropItem("Дубликат")
        else:
            self.items_seen.add(item['article'])
            return item
        
