import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import LandesbankItem

pattern = r'(\r)?(\n)?(\t)?(\xa0)?'



class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://www.hyponoe.at/ueber-uns/presse']

    def parse(self, response):
        links = response.xpath('//h3[@class="h5 m-0"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="next page-item"]/a[@class="page-link"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(LandesbankItem())
        item.default_output_processor = TakeFirst()
        date = response.xpath('//span[@class="date-published"]//text()').get().strip()
        title = response.xpath('//h1//text()').get()
        content = response.xpath('//div[@property="articleBody"]//text()[not(ancestor::figcaption)]').getall()
        content = re.sub(pattern, "" ,' '.join([text.strip() for text in content if text.strip()]))

        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        return item.load_item()
