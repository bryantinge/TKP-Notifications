from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from utils import get_env, send_sms, parse_date
from operator import itemgetter
import requests

DB_USERNAME = get_env('DB_USERNAME')
DB_PASSWORD = get_env('DB_PASSWORD')
DB_URL = get_env('DB_URL')
DB_PORT = get_env('DB_PORT')
DB_NAME = get_env('DB_NAME')

connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(
    DB_USERNAME, DB_PASSWORD, DB_URL, DB_PORT, DB_NAME)

Base = declarative_base()
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()

base_url = 'https://www.thekeyplay.com'


class Article(Base):
    __tablename__ = 'tkp-articles'
    id = Column(Integer, primary_key=True)
    title = Column(String())
    author = Column(String())
    date = Column(String())


def scrape_articles():
    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    titles = soup.find_all('h2', class_='node__title node-title')
    dates = soup.find_all('span', class_='node-submitted-date')
    authors = soup.find_all('span', class_='node-submitted-name')

    articles_scraped = [{
                        'title': titles[i].text,
                        'author': authors[i].text[4:],
                        'date': parse_date(dates[i].text[3:])
                        } for i, title in enumerate(titles)]

    articles_scraped.reverse()

    return articles_scraped


def query_articles():
    articles_query = [{'id': instance.id,
                       'title': instance.title,
                       'author': instance.author,
                       'date': instance.date}
                      for instance in session.query(Article).order_by(
                      Article.id.desc()).limit(20)]

    return articles_query


def filter_articles(articles_scraped, articles_query):
    id = articles_query[0]['id']

    for article in articles_scraped:
        if article['title'] not in map(itemgetter('title'), articles_query):

            id += 1
            title = article['title']
            author = article['author']
            date = article['date']

            add_article = Article(id=id, title=title, author=author, date=date)

            session.add(add_article)
            session.commit()

            notification = 'New Article: {}\nBy: {}'.format(title, author)
            send_sms(notification)
