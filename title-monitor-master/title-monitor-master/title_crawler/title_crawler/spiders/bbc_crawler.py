# -*- coding: utf-8 -*-
import scrapy

from .. import items


class BbcCrawlerSpider(scrapy.Spider):
    name = 'bbc_crawler'
    allowed_domains = ['bbc.com']
    start_urls = ['https://www.bbc.com' + url.strip() for url in open('bbc_news_cats.txt').readlines()]

    def parse(self, response):
        urls = response.xpath('//a/@href').re('\/news\/[\w+-]+\d+')
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_article_title)
        # print(len(urls))
        # for url in urls:
        #     url_href = url.xpath('./@href').re('\/news\/[\w+-]+\d+')
        #     if url_href:
        #         print(url.xpath('./text()').extract_first(),)
        # main_urls = response.xpath('//div[@class="orb-footer-primary-links"]//a/@href').extract()

    def parse_article_title(self, response):
        title = response.xpath('//h1//text()').extract_first()
        yield items.TitleCrawlerItem(url=response.url, title=title)
        # for url in urls:
        #     print(url)
