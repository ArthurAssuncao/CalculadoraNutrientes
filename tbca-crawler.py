# scrapy runspider tbca-crawler.py -o data.json

import scrapy
import html
import re
import json

def read_codes():
    data = []
    with open('codes.json', 'r', encoding='utf8') as arq:
        data = json.loads(arq.read())[0]['codes']
        data.sort()
    return data

class TBCASpider(scrapy.Spider):
    name = 'tbcaspider'
    url_base = 'http://www.tbca.net.br/base-dados/int_composicao_alimentos.php?cod_produto='
    products = read_codes()
    print(products)
    first_product = products[0]
    start_urls = [f'{url_base}{first_product}']
    actual_index = 0

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def next_product(self):
        new_index = self.actual_index + 1
        return new_index

    def isFinished(self):
        if (self.actual_index == len(self.products)):
            return True
        return False

    def parse(self, response):
        code, name, name_en = ['', '', '']
        for overview in response.css('.bd-content h5#overview'):
            # <h5 id="overview"><strong>Código:</strong> C0001C<br><strong>Descrição:</strong> Abacate, polpa, <i>in natura</i>, <i>Persea americana</i> Mill, &amp;lt&amp;lt Avocado, pulp, raw &amp;gt&amp;gt</h5>
            title = overview.getall()[0]
            title = html.unescape(title)
            title = title.replace('<h5 id="overview">', '').replace('</h5>', '')
            title = title.replace('<strong>Código:</strong> ', '')
            title = title.replace('<br><strong>Descrição:</strong> ', ';')
            title = title.replace('<i>','').replace('</i>', '')
            code, name = title.split(";")
            regex = r'&lt&lt (.*) &gt&gt'
            name_en = re.findall(regex, name)[0]
            name = name.replace(name_en, '')
            last_comma = name.rfind(',')
            name = name[0:last_comma]

        data = {}


        for line in response.css('#tabela1 tbody tr'):
            row_data = line.css('td::text').getall()
            value = -1
            try:
                value = float(row_data[2].replace(',', '.'))
            except ValueError as e:
                value = row_data[2]
            nutrient = {
                'unit': row_data[1],
                'value': value

            }

            data[row_data[0]] = nutrient

        yield { code: {'name': name, 'name_en': name_en, 'nutrients': data} }

        new_index = self.next_product()
        self.actual_index = new_index

        if (not self.isFinished()):
            yield scrapy.Request(
                response.urljoin(f'{self.url_base}{self.products[self.actual_index]}'),
                callback=self.parse
            )
