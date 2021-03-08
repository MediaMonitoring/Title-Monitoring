from scrapy.spiders import SitemapSpider


class MySpider(SitemapSpider):
    name = 'bbc_sm_crawler'
    sitemap_urls = ['https://www.bbc.com/sitemaps/https-sitemap-com-news-1.xml']

    # sitemap_rules = [
    #     ('/url/', 'parse_news'),
    # ]
    # sitemap_follow = ['/sitemap_shops']

    def parse(self, response):
        print(response)
        pass  # ... scrape shop here ...
