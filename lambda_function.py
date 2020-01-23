from scraper import scrape_articles, query_articles, filter_articles


def lambda_handler(event, context):
    articles_scraped = scrape_articles()
    articles_query = query_articles()
    filter_articles(articles_scraped, articles_query)
    return {'status': 200, 'body': 'Lambda Executed'}


lambda_handler(0, 0)
