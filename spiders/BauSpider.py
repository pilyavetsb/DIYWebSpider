import scrapy
from Leroy.items import Product, ProductLoader
from datetime import date

today = str(date.today())


class BauSpider(scrapy.spiders.CrawlSpider):
    name = "bau_spider"
    start_urls = ["https://baucenter.ru/oboi_dekor_kraski/"]
    custom_settings = {'FEED_URI': f'Bau_{today}.json'}

    def parse(self, response):
        #у бауцентра каталоги разной глубины в зависимости от категории, потому проверяем, попали ли мы на страницу с продуктами или на страницу с подкатегориями
        if response.xpath("//a[@class='categories_row_item']/@href"):
            for link in response.xpath("//a[@class='categories_row_item']/@href").extract():
                #игнорируем не-ЛКМ категории
                if not any(i in link for i in ['oboi', 'karnizy_rolety_i_zhalyuzi', 'shtory_i_aksessuary_dlya_shtor_podushki_tekstil',
                                               'ramki_kartiny_chasy', 'dekorativnye_plenki','plintus_potolochnyy_i_nastennyy_dekorativnye_balki',
                                               'potolochnaya_plitka', 'sredstva_dlya_pokleyki']):
                    yield scrapy.Request(response.urljoin(link), callback=self.parse)
        else:
            #если попали на продуктовую страницу, вызываем соответствующий метод
            self.parse_page(response)

    def parse_page(self, response):
        for prod in response.xpath("//div[@class='catalog_item with-tooltip']"):
            loader = ProductLoader(selector=prod, base = response.url, size_changer = (False,""))
            loader.add_xpath('name', ".//@data-name")
            loader.add_xpath('packing', ".//@data-name")
            loader.add_xpath('measure', ".//@data-name")
            loader.add_xpath('price', ".//@data-price")
            loader.add_value('client', 'Baucentr')
            loader.add_xpath('article', ".//div/div/p[@class='catalog_item_info']/text()[contains(.,'35')]")
            loader.add_xpath('image', ".//img[@class='catalog_item_image']/@src")
            yield loader.load_item()
        link = response.xpath("//a[@class='pagination_button pagination_button--next']/@href").extract_first()
        yield scrapy.Request(response.urljoin(link), callback=self.parse_page)