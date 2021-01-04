import scrapy
from Leroy.items import Product, ProductLoader
from datetime import date

today = str(date.today())

class OrderSpider(scrapy.spiders.CrawlSpider):
    name = "order_spider"
    start_urls = ["https://order-nn.ru/kmo/catalog/5940/"]
    custom_settings = {'FEED_URI': f'Order_{today}.json'}

    def parse(self, response):
        for link in response.xpath("//div[@class='sections-block-level-1']/*/a/@href").extract():
            if '7286' not in link:
                yield scrapy.Request(response.urljoin(link), callback=self.parse_page)

    def parse_page(self, response):
        for prod in response.xpath("//div[@class='col-md-4 col-sm-4 col-xs-4 item']"):
            loader = ProductLoader(selector=prod)
            loader.add_xpath('name', ".//div/div/div[@class='items-name']/a/text()")
            loader.add_xpath('packing', ".//div/div/div[@class='items-name']/a/text()")
            loader.add_xpath('measure', ".//div/div/div[@class='items-name']/a/text()")
            loader.add_value('client', 'Order')
            loader.add_xpath('article', ".//div/div/div/span[@class='block-code-value']/text()")
            if prod.xpath(".//div/div/div[@class='price']/div[@class='price-old']"):
                loader.add_xpath('price', ".//div/div/div[@class='price']/div[@class='price-old']/text()")
            else:
                loader.add_xpath('price', ".//div/div/div[@class='price']/div[@class='price-current']/text()[position()=1]")
            yield loader.load_item()

        next_page = response.xpath("//ul[@class='pagination']/li/a[descendant::i[@class='fa fa-arrow-right']]/@href")

        if next_page:
            yield scrapy.Request(response.urljoin(next_page.extract_first()), callback=self.parse_page)