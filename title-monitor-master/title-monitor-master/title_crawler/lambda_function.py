import imp
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

sys.modules["sqlite"] = imp.new_module("sqlite")
sys.modules["sqlite3.dbapi2"] = imp.new_module("sqlite.dbapi2")

def handler(event, context):
    process = CrawlerProcess(get_project_settings())
    process.crawl("bbc_crawler")
    process.start()


def ny_handler(event, context):
    process = CrawlerProcess(get_project_settings())
    process.crawl("nytimes_crawler")
    process.start()

def ft_handler(event, context):
    process = CrawlerProcess(get_project_settings())
    process.crawl("ft_crawler")
    process.start()



def wsj_handler(event, context):
    process = CrawlerProcess(get_project_settings())
    process.crawl("wsj_crawler")
    process.start()


