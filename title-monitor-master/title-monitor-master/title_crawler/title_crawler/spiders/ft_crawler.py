# -*- coding: utf-8 -*-
import scrapy

from .. import items


class FtCrawlerSpider(scrapy.Spider):
    name = 'ft_crawler'
    site_id = 3
    allowed_domains = ['ft.com']
    start_urls = ['https://www.ft.com' + url.strip() for url in open('ft_cats.txt').readlines()]

    def parse(self, response):
        urls = response.xpath('//a[@data-trackable="heading-link"]')
        for url in urls:
            url_href = response.urljoin(url.xpath("./@href").extract_first())
            title = url.xpath(".//text()").extract_first()
            yield items.TitleCrawlerItem(url=url_href, title=title, site_id=self.site_id)

    # def parse_article_title(self, response):
    #     title = response.xpath('//blockquote//text()').extract_first().strip()
    #     yield items.TitleCrawlerItem(url=response.url, title=title, site_id=self.site_id)
