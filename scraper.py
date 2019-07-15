from bs4 import BeautifulSoup
from datetime import datetime
import os
import requests
import boto3
import send_sms

def get_env(name):
    try: 
        return os.environ[name]
    except KeyError:
        import config
        return config.config[name]

ARTICLE_TABLE = get_env('ARTICLE_TABLE')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(ARTICLE_TABLE)
base_url = 'https://www.thekeyplay.com'

def parse_date(date):
    date_formatted = datetime.strptime(date, '%B %d, %Y, %I:%M %p')
    return datetime.strftime(date_formatted, '%Y-%m-%d %H:%M')


def scrape_articles():
    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    titles = soup.find_all('h2', class_='node__title node-title')
    dates = soup.find_all('span', class_='node-submitted-date')
    authors = soup.find_all('span', class_='node-submitted-name')
    article_urls = soup.find_all('h2', class_='node__title node-title')
    # print(titles)
    articles_scraped = [{
                        'title': titles[i].text, 
                        'date': parse_date(dates[i].text[3:]), 
                        'author': authors[i].text[4:]
                        # 'article_url': 
                        } for i, title in enumerate(titles)]
    return(articles_scraped)


def scan_articles():
    articles_db = table.scan()['Items']
    return(articles_db)


def notification(articles_scraped, articles_db):
    if articles_scraped[0] in articles_db:
        print('No new articles')
    else:
        for article in articles_scraped:
            if article not in articles_db:
                response = table.put_item(Item=article)

                title = article['title']
                author = article['author']
                print('Added to database: "{}"').format(title)

                notification = 'New Article: {}\nBy: {}'.format(title, author)
                send_sms.send_sms(notification)
                print('SMS notification sent')