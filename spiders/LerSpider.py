import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from Leroy.items import Product, ProductLoader
from datetime import date

today = str(date.today())


#пока не удаляю закоменченый код, потому что Леруа нон-стоп что-то меняет на своем сайте, весьма вероятно, что опять придется к селениуму откатиться

class LeroySpider(scrapy.spiders.CrawlSpider):
    name = "leroy_spider"
    start_urls = ["https://leroymerlin.ru/catalogue/kraski/?REGION_ID=34&PREV_REGION_ID=506"]

    #def __init__(self, *args, **kwargs):
        #super(LeroySpider, self).__init__(*args, **kwargs)
        #opt = Options()
        #opt.add_argument("--headless")
        #opt.add_argument("--window-size=1920x1080")
        #opt.add_argument("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.90 Safari/537.36 Vivaldi/1.91.867.38")
        # profile.set_preference("geo.wifi.uri", "https://location.services.mozilla.com/v1/geolocate?key=%MOZILLA_API_KEY%")
        #self.browser = webdriver.Chrome("F:\ScrapingRefactoring\Leroy\Leroy\chromedriver.exe", chrome_options=opt)

    custom_settings = {'CONCURRENT_REQUESTS_PER_DOMAIN': 16, 'FEED_URI': f'Leroy_{today}.json'}

    def parse(self, response):
        for link in response.xpath("//div[@class='items']/ul/li/a/@href").getall()[0:31]:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_subcat)

    def parse_subcat(self, response):
        # self.browser.get(response.url)
        # wait = WebDriverWait(self.browser, 10)
        # elem = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[@class='paginator-button next-paginator-button']" )))
        # all_viewer = self.browser.find_element_by_xpath("//select[@id='per-page1']")
        # selectron = Select(elem)
        # selectron.select_by_value("all")
        # elem.click()

        #source = self.browser.page_source
        sel = Selector(response)

        for prod in sel.xpath("//div[@class='ui-product-card']"):
            loader = ProductLoader(selector=prod, base=response.url, size_changer = (False,"800x800"))
            loader.add_xpath('name', ".//div/div[@class='product-name']/a/text()")
            loader.add_xpath('measure', ".//div/div[@class='product-name']/a/text()")
            loader.add_xpath('packing', ".//div/div[@class='product-name']/a/text()")
            loader.add_xpath('price', ".//div/descendant::span[@class='main-value-part']/@content")
            loader.add_value('client', 'Leroy')
            loader.add_xpath('article', ".//descendant::span[@class='madein__text'][2]/text()")
            #loader.add_xpath('image', ".//div/picture/source[1]/@srcset")  
            yield loader.load_item()
        #достаем последнюю страницу и проходимся циклом по всем страницам
        max_page=response.xpath("//a[@class='paginator-item ']/text()").getall()[1].strip()
        max_page = int(max_page)
        for i in range(2,max_page):
            yield scrapy.Request(response.url.split("?")[0]+"?page="+str(i), callback=self.parse_subcat)

