import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
import spiders.PetrovichSpider as petr

#по умолчанию лога нет, если в нем возникнет необходимость, нужно будет в settings.py раскоммментировать параметр LOG_FILE
configure_logging()
settings = get_project_settings()

#зададим базовые параметры процесса
settings.set(name='FEED_FORMAT', value='json', priority='cmdline')
settings.set(name='FEED_EXPORT_ENCODING', value='utf-8', priority='cmdline')
settings.set(name='USER_AGENT', value='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.90 Safari/537.36 Vivaldi/1.91.867.38',
             priority='cmdline')

process = CrawlerProcess(settings)

#определим функцию для последовательного запуска
#TODO - если понадобится масштабирование, подумать над многопоточностью
def crawl(runner_param):
    runner_param.crawl('leroy_spider')
    runner_param.crawl('agava_spider')
    runner_param.crawl('obi_spider')
    runner_param.crawl('order_spider')
    runner_param.crawl('bau_spider')
    runner_param.crawl('maxi_spider')
    runner_param.start()

crawl(process)
print("FINISH scrapy")

#запрос с сайта петровича отдельно, т.к. он сразу отдает весь json, нет смысла гонять по всем пайплайнам
petr.petrovich()
print("Petrovich over")