import argparse
import configparser
import logging
import requests
import smtplib
import sys
from datetime import datetime
from lxml import html


config = configparser.ConfigParser()
config.read('config.ini')
try:
    SENDER_EMAIL = config['email']['id']
    SENDER_PASSWORD = config['email']['password']
    SMTP_HOST = config['smtp']['host']
    SMTP_PORT = config['smtp']['port']
except KeyError as e:
    logging.error('config.ini set incorrectly')
    sys.exit()

# Set logging config
logging.basicConfig(filename='imdb_reminder.log', level=logging.DEBUG)

# Set argparse config
parser = argparse.ArgumentParser(description='Send email reminders for TV-Shows')
parser.add_argument('email', metavar='EMAIL',
                    help='Email to send the reminders to.')
parser.add_argument('shows', metavar='SHOWS',
                    nargs='+', help='Comma seperated Shows.')
args = parser.parse_args()


def get_show_url(name):
    """Get the url of the show.

    Args:
        name (str): The name of the show.

    Returns:
        str: The imdb url of the show.

    """
    url = 'https://imdb.com/find?q={}'
    r = requests.get(url.format(name.replace(' ', '+')))
    doc = html.fromstring(r.content)

    # Extract url from the first search result
    rel = doc.xpath('//td[@class="result_text"]/a/@href')[0]

    return 'https://www.imdb.com{}'.format(rel)


def get_show_status(url):
    """Get the status of the show.

    Args:
        url (str): imdb url of a show.

    Returns:
        str: Status of the show.

    """
    r = requests.get(url)
    doc = html.fromstring(r.content)

    # Extract runtime from the show page.
    # If runtime is not a single year the show has finished streaming.
    runtime = doc.xpath('//div[@class="subtext"]/a/text()')[-1]
    if runtime[runtime.index('–') + 1:-2].isdigit():
        return 'The show has finished streaming all its episodes.'

    # Get the latest season of the show.
    rel = doc.xpath('//div[@class="seasons-and-year-nav"]/div[3]/a[1]/@href')[0]
    latest_season_url = 'https://www.imdb.com{}'.format(rel)

    r = requests.get(latest_season_url)
    doc = html.fromstring(r.content)

    # Extract episode listing of the latest season.
    episodes = doc.xpath('//*[@id="episodes_content"]/div/div[2]/div')

    # Check whether the first episode is yet to be aired.
    # If true return the season air year.
    first_epi = episodes[0]
    if first_epi.xpath('*//span[contains(@class,"add-image-container")]'):
        airdate = first_epi.xpath('*//div[@class="airdate"]/text()')[0].strip()
        return 'The next season begins in {}'.format(airdate)

    # Check other episodes yet to be aired
    for episode in episodes[1:]:
        if episode.xpath('*//span[contains(@class,"add-image-container")]'):
            date = episode.xpath('*//div[@class="airdate"]/text()')[0].strip()
            airdate = datetime.strptime(date, '%d %b. %Y')
            return 'Next episode airs on {}'.format(airdate.strftime('%Y-%m-%d'))


def send_email(msg):
    """Send email.

    Args:
        msg (str): The message to sent in the email.

    """
    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    smtp.starttls()
    smtp.login(SENDER_EMAIL, SENDER_PASSWORD)

    mail_msg = 'From: {}\nTo: {}\nSubject: TV-Show Reminder\n\n{}'
    mail_msg = mail_msg.format(SENDER_EMAIL, args.email, msg)

    smtp.sendmail(SENDER_EMAIL, args.email, mail_msg)


def main():
    """Driver function of the script."""
    email = args.email
    shows = ' '.join(args.shows).split(',')
    statuses = []

    logging.info('Email: %s', email)
    logging.info('Shows: %s', str(shows))

    print('Fetching show details...')
    for show in shows:
        logging.info('Fetching: %s', show)
        url = get_show_url(show)
        status = get_show_status(url)
        statuses.append(status)

    logging.info('Generating message')
    msg = ""
    for show, status in zip(shows, statuses):
        msg += 'TV Series Name: {}\n'.format(show.title())
        msg += 'Status: {}\n\n'.format(status)

    print('Sending mail...')
    logging.info('Sending mail')
    send_email(msg)
    print('Email sent!')


if __name__ == '__main__':
    main()
