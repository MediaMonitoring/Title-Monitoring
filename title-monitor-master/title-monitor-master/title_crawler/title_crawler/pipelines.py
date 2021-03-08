# -*- coding: utf-8 -*-
import datetime
import logging

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

logger = logging.getLogger(__name__)
DeclarativeBase = declarative_base()


class News_Title(DeclarativeBase):
    """
    The pages table sqlalchemy class to be used by the sqlite pipeline..
    """
    __tablename__ = "news_titles"

    title_id = Column(Integer, primary_key=True)
    site_id = Column('site_id', Integer)
    title_url = Column('title_url', String)
    title_text = Column('title_text', String)
    title_timestamp = Column('title_timestamp', DateTime)

    def __repr__(self):
        return "<Title({},{})>".format(self.title_url, self.title_text)

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


class TitleCrawlerPipeline(object):
    def __init__(self, settings):
        self.database = settings.get('DATABASE')
        self.sessions = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings)
        return pipeline

    def create_engine(self):
        engine = create_engine(URL(**self.database), poolclass=StaticPool, echo=False,
                               )  # connect_args={'check_same_thread': False},
        return engine

    def create_session(self, engine):
        session = sessionmaker(bind=engine)()
        return session

    def open_spider(self, spider):
        engine = self.create_engine()
        session = self.create_session(engine)
        self.sessions[spider] = session

    def close_spider(self, spider):
        session = self.sessions.pop(spider)
        session.close()

    def process_item(self, item, spider):
        session = self.sessions[spider]

        link_exists = session.query(News_Title).filter(and_(News_Title.title_url.__eq__(item['url']),
                                                            News_Title.title_text.__eq__(
                                                                item['title']))).first() is not None

        if link_exists:
            logger.info('Item {} is in db'.format(item))
            return item
        news_title = News_Title({'site_id': item['site_id'], 'title_url': item['url'], 'title_text': item['title'],
                                 'title_timestamp': str(datetime.datetime.now())})
        try:

            session.add(news_title)
            session.commit()
            logger.info('Item {} stored in db'.format(news_title))
        except:
            logger.info('Failed to add {} to db'.format(news_title))
            session.rollback()
            raise
        return item
