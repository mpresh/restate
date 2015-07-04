import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

class HackerNewsItem(scrapy.Item):
    title = scrapy.Field()
    comment = scrapy.Field()
    link = scrapy.Field()

class HackerNewsSpider(CrawlSpider):
    name = 'hackernews'
    allowed_domains = ['news.ycombinator.com']
    start_urls = [
        'https://news.ycombinator.com/'
    ]
    rules = (
        # Follow any item link and call parse_item.
        Rule(LinkExtractor(allow=('item.*', )), callback='parse_item'),
    )

    def parse_item(self, response):
        item = HackerNewsItem()
        item['link'] = response.url
        return item
