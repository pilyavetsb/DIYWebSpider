import scrapy
from Leroy.items import Product, ProductLoader
from datetime import date

today = str(date.today())

class AgavaSpider(scrapy.spiders.CrawlSpider):
    name = "agava_spider"
    start_urls = ["https://kazan.megastroy.com/catalog/lakokrasochnye-materialy"]
    custom_settings = {'FEED_URI': f'Agava_{today}.json'}


    def parse(self, response):
        for link in response.xpath("//a[@class='full-size-link']/@href").extract():
            #игнорируем нерелевантные подкатегории
            if not any(i in link for i in ['zhidkie-gvozdi', 'klei-kleykie-lenty', 'germetiki', 'smyvki', 'trafarety', 'peny-montazhnye']):
                yield scrapy.Request(response.urljoin(link), callback=self.parse_page)

    def parse_page(self, response):
        for prod in response.xpath("//div[@class='col-lg-3 col-sm-4']"):
            loader = ProductLoader(selector=prod)
            loader.add_xpath('name', ".//*/div/a[@class='title']/text()")
            #если есть скидка, берем цену до скидки, в противном случае - просто цену
            if prod.xpath(".//*/*/div[@class='striked-price']"):
                loader.add_xpath('price', ".//*/*/div[@class='striked-price']/b/text()")
            else:
                loader.add_xpath('price', ".//*/div/div[@class='price']/b/text()")
            loader.add_value('client', 'Agava')
            loader.add_xpath('packing', ".//*/div/a[@class='title']/text()")
            loader.add_xpath('measure', ".//*/div/a[@class='title']/text()")
            loader.add_xpath('article', ".//div/div[@class='wrap']/div[@class='code']/text()")
            yield loader.load_item()

        #достаем номер последней страницы
        maxim = int(response.xpath("(//ul[@class='pagination']/li)[last()]/a/text()").extract_first()) - 1

        #проходимся по всем страницам, конструируем ссылку с номером
        for i in range(1, maxim):
            if "?page" not in response.url:
                yield scrapy.Request(response.url+"?page=1", callback=self.parse_page)

            elif "?page="+str(maxim) not in response.url:
                for link in range(2,maxim):
                    yield scrapy.Request(response.url.split("?")[0]+"?page="+str(i), callback=self.parse_page)