# http://www.tbca.net.br/base-dados/composicao_alimentos.php?pagina=53

# scrapy runspider tbca-codes-crawler.py -o codes.json

import scrapy
import html
import re
from scrapy import signals
from pydispatch import dispatcher

class TBCACodesSpider(scrapy.Spider):
    name = 'tbcacodesspider'
    url_base = 'http://www.tbca.net.br/base-dados/composicao_alimentos.php?pagina='
    start_urls = [f'{url_base}1']
    page = 1
    MAX = 53
    data = []

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def next_page(self):
        if (self.page < self.MAX):
            self.page = self.page + 1
            return True
        return False


    def parse(self, response):

        for code in response.css('.table tbody tr td:first-child a::text'):
            self.data.append(code.getall()[0])

        if (self.page == self.MAX):
            yield { 'codes': self.data }
        if (self.next_page()):
            yield scrapy.Request(
                response.urljoin(f'{self.url_base}{self.page}'),
                callback=self.parse
            )

    def spider_closed(self, spider):
        print('TBCA Codes Spider Finished')

