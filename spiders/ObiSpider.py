import scrapy
from Leroy.items import Product, ProductLoader
from datetime import date

today = str(date.today())

class ObiSpider(scrapy.spiders.CrawlSpider):
    name = "obi_spider"
    start_urls = ["https://www.obi.ru/vsyo-dlya-doma/lakokrasochnye-materialy/c/296"]
    custom_settings = {'FEED_URI': f'Obi_{today}.json'}

    def parse(self, response):
        for link in response.xpath("//ul[@class='first-level dashed']/li/a/@href").extract():
            #игнорируем нерелевантные ссылки
            if 'malyarnyi-instrument-i-materialy' not in link:
                yield scrapy.Request(response.urljoin(link), callback=self.parse_page)

    def parse_page(self, response):
        prod_large = response.xpath("//li[@class='product large']")
        #вытаскиваем ссылки на страницы продуктов, отдаем в parse_prod
        for prod in prod_large:
            prodpage = prod.xpath(".//a/@href").extract_first()
            yield scrapy.Request(response.urljoin(prodpage), callback=self.parse_prod)
        #проходимся по страницам со 2-ой до последней, рекурсивно вызывая эту ффункцию 
        max_page = int(response.xpath("//a[@class='pagination-bar__link-refs js-pagination-link-refs']/text()").extract()[0][-1])
        if max_page:
            for link in range(2, max_page):
                yield scrapy.Request(response.urljoin("?page=")+str(link), callback=self.parse_page)

    def parse_prod(self, response):
        loader = ProductLoader(selector=response, base=response.url, size_changer = (False,""))
        #если есть скидка, берем оригинальную цену
        if response.xpath("//div[@class='span12 span-mobile12']/span/del[position()=2]/text()"):
            loader.add_xpath('price', "//div[@class='span12 span-mobile12']/span/del[position()=2]/text()")
        else:
            loader.add_xpath('price', "//div[@class='float-right']/span/strong/strong/text()")
        loader.add_xpath('name', "//h1[@class='h2 overview__heading']/text()")
        loader.add_xpath('measure', "//h1[@class='h2 overview__heading']/text()")
        loader.add_xpath('packing', "//h1[@class='h2 overview__heading']/text()")
        loader.add_value('client', 'OBI')
        loader.add_xpath('image', "//img[contains(@class,'ads-slider__image')]/@src[1]")
        loader.add_xpath('article', "//section[@class='collapse in desc']/*/p[contains(@class,'article')]/text()")
        yield loader.load_item()

        #если у продукта есть несколько фасовок, достаем их и передаем на окончательный парсинг в parse_last
        variants = response.xpath("//ul[@class='dropdown-menu']/li/a/@href").extract()
        if variants:
            for link in variants:
                yield scrapy.Request(response.urljoin(link), callback=self.parse_last)

    def parse_last(self, response):
        loader = ProductLoader(selector=response, base=response.url, size_changer = (False, ""))
        if response.xpath("//div[@class='span12 span-mobile12']/span/del[position()=2]/text()"):
            loader.add_xpath('price', "//div[@class='span12 span-mobile12']/span/del[position()=2]/text()")
        else:
            loader.add_xpath('price', "//div[@class='float-right']/span/strong/strong/text()")
        loader.add_xpath('name', "//h1[@class='h2 overview__heading']/text()")
        loader.add_xpath('measure', "//h1[@class='h2 overview__heading']/text()")
        loader.add_xpath('packing', "//h1[@class='h2 overview__heading']/text()")
        loader.add_value('client', 'OBI')
        loader.add_xpath('image', "//img[contains(@class,'ads-slider__image')]/@src[1]")
        loader.add_xpath('article', "//section[@class='collapse in desc']/*/p[contains(@class,'article')]/text()")
        yield loader.load_item()