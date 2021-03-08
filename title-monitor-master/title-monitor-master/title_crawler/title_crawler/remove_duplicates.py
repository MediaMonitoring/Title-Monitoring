import diff_match_patch as dmp_module
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

dmp = dmp_module.diff_match_patch()

import spacy

nlp = spacy.load('en_core_web_lg')

from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer(language='english')

from fixer_evaluation import get_diff_log

DeclarativeBase = declarative_base()

from pipelines import News_Title


class DatabaseHandler(object):
    """
    The db handler class for processing the crawled db,
    and turn it into a training set..
    """

    def __init__(self):
        self.database = {
            'drivername': 'postgresql',
            'host': 'title-monitoring-db.cafklgqz4nvf.us-east-2.rds.amazonaws.com',
            'port': '5432',
            'username': 'root',
            'password': '%xjlpBF934^5mw',
            'database': 'monitoringdb'
        }
        self.sessions = {}
        self.engine = self.create_engine()
        self.create_tables(self.engine)
        self.session = self.create_session(self.engine)

    def create_engine(self):
        engine = create_engine(URL(**self.database), poolclass=StaticPool, echo=True,
                               )  # connect_args={'check_same_thread': True},
        return engine

    def create_tables(self, engine):
        DeclarativeBase.metadata.create_all(engine, checkfirst=True)

    def create_session(self, engine):
        session = sessionmaker(bind=engine)()
        return session

    def find_distinct(self):
        n_urls = []
        # for n_url in self.session.query(News_Title.title_url).filter(cast(News_Title.title_timestamp, DATE)==date.today()).distinct():
        for n_url in self.session.query(News_Title.title_url).filter(News_Title.site_id == 4).order_by(
                # for n_url in self.session.query(News_Title.title_url).filter(News_Title.title_url == 'https://www.bbc.com/news/business-49027889').order_by(
                News_Title.title_timestamp).distinct():
            n_urls.append(n_url[0])
        return n_urls

    def remove_dups(self, urls):
        for url in urls:
            n_titles = self.session.query(News_Title).filter_by(title_url=url).all()
            if len(n_titles) == 1:
                continue
            c_title = n_titles.pop()
            to_delete = []

            for title in n_titles:
                # diff = dmp.diff_main(title.title_text, c_title.title_text)
                try:
                    diff = get_diff_log(title.title_text, c_title.title_text)
                except ValueError:
                    continue
                # diff = [d for d in diff if d[1]]
                if len(diff) < 3:
                    to_delete.append(title)
                    with open("dedup_results.txt", "a") as ffile:
                        try:
                            ffile.writelines(
                                [c_title.title_text, '\n', title.title_text, '\n', "==" * 50, '\n'])
                        except:
                            pass

            for title in to_delete:
                self.session.query(News_Title).filter_by(title_id=title.title_id).delete()
                # print("Savage el Savage Savage el Savage Savage el Savage Savage el Savage ")
                self.session.commit()

    def get_lemmas(self, title):

        if not title: return

        doc = nlp(title)

        return [stemmer.stem(token.text) for token in doc]

    def remove_rewording(self, urls):
        for url in urls:
            n_titles = self.session.query(News_Title).filter_by(title_url=url).all()
            if len(n_titles) == 1:
                continue
            c_title = n_titles.pop()
            c_title_lemmas = self.get_lemmas(c_title.title_text)
            to_delete = []

            for title in n_titles:

                try:
                    title_lemmas = self.get_lemmas(title.title_text)
                except ValueError:
                    continue
                except TypeError:
                    continue

                def compare_bitwise(x, y):
                    set_x = frozenset(x)
                    set_y = frozenset(y)
                    diff_x = set_x - set_y
                    diff_y = set_y - set_x

                    sum_diff = len(diff_x) + len(diff_y)
                    if sum_diff <= 3 or sum_diff / (len(set_x) + len(set_y)) <= .1:
                        return True
                    # return set_x & set_y

                    # ffile.write()
                    # ffile.write(c_title.title_text)
                    # ffile.write(c_title.title_text)

                if not c_title_lemmas or not title_lemmas:
                    continue
                if compare_bitwise(c_title_lemmas, title_lemmas):
                    to_delete.append(title)
                    print("BINGO")
                    with open("reword_results.txt", "a") as ffile:
                        try:
                            ffile.writelines(
                                [c_title.title_text, '\n', title.title_text, '\n', "==" * 50, '\n'])
                        except:
                            pass

            for title in to_delete:
                self.session.query(News_Title).filter_by(title_id=title.title_id).delete()
                # print("Savage el Savage Savage el Savage Savage el Savage Savage el Savage ")
                self.session.commit()

    def remove_rewording_full(self, urls):
        for url in urls:
            n_titles = self.session.query(News_Title).filter_by(title_url=url).all()
            if len(n_titles) == 1:
                continue
            # c_title = n_titles.pop()

            to_delete = []

            for i in range(len(n_titles)):
                try:
                    title = n_titles[i]
                    title_lemmas = self.get_lemmas(title.title_text)
                except ValueError:
                    continue
                except TypeError:
                    continue

                for j in range(i + 1, len(n_titles)):

                    try:
                        c_title = n_titles[j]
                        c_title_lemmas = self.get_lemmas(c_title.title_text)

                    except ValueError:
                        continue
                    except TypeError:
                        continue

                    def compare_bitwise(x, y):
                        set_x = frozenset(x)
                        set_y = frozenset(y)
                        diff_x = set_x - set_y
                        diff_y = set_y - set_x

                        sum_diff = len(diff_x) + len(diff_y)
                        if sum_diff <= 3 or sum_diff / (len(set_x) + len(set_y)) <= .1:
                            return True

                    # return set_x & set_y

                    # ffile.write()
                    # ffile.write(c_title.title_text)
                    # ffile.write(c_title.title_text)
                    if not c_title_lemmas or not title_lemmas:
                        continue
                    if compare_bitwise(c_title_lemmas, title_lemmas):
                        to_delete.append(title)
                        print("BINGO")
                        with open("reword_results.txt", "a") as ffile:
                            try:
                                ffile.writelines(
                                    [c_title.title_text, '\n', title.title_text, '\n', "==" * 50, '\n'])
                            except:
                                pass

            for title in to_delete:
                self.session.query(News_Title).filter_by(title_id=title.title_id).delete()
                # print("Savage el Savage Savage el Savage Savage el Savage Savage el Savage ")
                self.session.commit()


def main():
    db_handler = DatabaseHandler()
    # 1. find all referer urls, save them in referer table for ease of processing
    urls = db_handler.find_distinct()
    # db_handler.remove_dups(urls)
    # db_handler.remove_rewording(urls)
    db_handler.remove_rewording_full(urls)
    # 2. add content_text column to the pages table
    # db_handler.add_column()
    # # 3. use the boiler removal function to get the content text
    # db_handler.update_content_text(remover_boiler_code)
    # # 4. construct the url pairs
    # fill_url_pairs(db_handler)
    # # 5. update the similarity scores with structural and semantic similarity functions
    # db_handler.update_sim_score(similarity, get_cosine_sim, )


if __name__ == '__main__':
    main()
