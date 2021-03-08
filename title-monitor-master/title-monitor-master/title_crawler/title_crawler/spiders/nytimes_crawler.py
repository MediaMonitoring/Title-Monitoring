# -*- coding: utf-8 -*-
import scrapy

from .. import items


class NytCrawlerSpider(scrapy.Spider):
    name = 'nytimes_crawler'
    site_id = 2
    allowed_domains = ['nytimes.com']
    start_urls = ['https://www.nytimes.com' + url.strip() for url in open('nytimes_cats.txt').readlines()]

    def parse(self, response):
        urls = response.xpath('//a/@href').re('/\d{4}/\d{2}/\d{2}.*')
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_article_title)

    def parse_article_title(self, response):
        title = response.xpath('//h1//text()').extract_first().strip()
        yield items.TitleCrawlerItem(url=response.url, title=title, site_id=self.site_id)
