import scrapy
from Leroy.items import Product, ProductLoader
from datetime import date

today = str(date.today())

class Maxispider(scrapy.spiders.CrawlSpider):
    name = "maxi_spider"
    start_urls = ["https://www.maxidom.ru/catalog/kraska-i-maljarnyjj-instrument/"]
    custom_settings = {'FEED_URI': f'Maxidom_{today}.json', 'CONCURRENT_REQUESTS_PER_DOMAIN': 12}
    

    def parse(self, response):
        for link in response.xpath("//figure[@class='category category-first']/a[position()=2]/@href").extract():
            if not any(i in link for i in ['maljarno-shtukaturnyjj-instrument','pasty-kolerovochnye']):
                yield scrapy.Request(response.urljoin(link), callback=self.parse_page)

    def parse_page(self, response):
        for prod in response.xpath("//article[@class='item-list group']"):
            loader = ProductLoader(selector=prod)
            loader.add_xpath('name', ".//div[@class='caption-list']/a/text()")
            loader.add_xpath('packing', ".//div[@class='caption-list']/a/text()")
            loader.add_xpath('measure', ".//div[@class='caption-list']/a/text()")
            loader.add_xpath('price', ".//*/*/span[@class='price-list']/span/@data-repid_price")
            loader.add_value('client', 'MAXIDOM')
            loader.add_xpath('article', ".//div[@class='caption-list']/div[@class='small-top']/small[position()=2]/text()")
            yield loader.load_item()

        #до тех пор, пока на странице есть указатель на следующую, рекурсивно вызываем parse_page, чтобы получить данные со всех страниц
        next_page = response.xpath("//a[@id='navigation_3_next_page']/@href").extract_first()

        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse_page)
