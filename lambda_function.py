import scraper

def lambda_handler(event, context):
    articles_scraped = scraper.scrape_articles()
    articles_db = scraper.scan_articles()
    scraper.notification(articles_scraped, articles_db)
    return { 'status' : 200, 'body' : 'Lambda Executed' }

lambda_handler(0,0)