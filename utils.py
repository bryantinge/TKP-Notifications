from twilio.rest import Client
from datetime import datetime
import os


def get_env(name):
    try:
        return os.environ[name]
    except KeyError:
        import config
        return config.config[name]


def parse_date(date):
    date_formatted = datetime.strptime(date, '%B %d, %Y, %I:%M %p')
    return datetime.strftime(date_formatted, '%Y-%m-%d %H:%M')


def send_sms(sms_body):
    ACCOUNT_SID = get_env('ACCOUNT_SID')
    AUTH_TOKEN = get_env('AUTH_TOKEN')
    SENDING_NUMBER = get_env('SENDING_NUMBER')
    RECEIVING_NUMBER = get_env('RECEIVING_NUMBER')

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages \
                    .create(body=sms_body,
                            from_=SENDING_NUMBER,
                            to=RECEIVING_NUMBER)
