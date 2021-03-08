# -*- coding: utf-8 -*-
import scrapy

from .. import items


class WsjCrawlerSpider(scrapy.Spider):
    name = 'wsj_crawler'
    site_id = 4
    allowed_domains = ['wsj.com']
    start_urls = ['https://www.wsj.com' + url.strip() for url in open('wsj_cats.txt').readlines()]

    def parse(self, response):
        urls = response.xpath('//a/@href').re('\/articles\/[\w+-]+\d+')
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_article_title)

    def parse_article_title(self, response):
        title = response.xpath('//h1//text()').extract_first().strip()
        yield items.TitleCrawlerItem(url=response.url, title=title, site_id=self.site_id)
