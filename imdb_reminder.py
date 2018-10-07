import argparse
import requests
import logging
from bs4 import BeautifulSoup
from lxml import html
from datetime import datetime


parser = argparse.ArgumentParser(description='Send email reminders for TV-Shows.')

parser.add_argument('email', metavar='EMAIL',
                    help='Email to send the reminders to.')
parser.add_argument('shows', metavar='SHOWS',
                    nargs='+', help='Comma seperated Shows.')


def get_show_url(name):
    """Get the url of the show."""
    url = 'https://imdb.com/find?q={}'
    r = requests.get(url.format(name.replace(' ', '+')))
    soup = BeautifulSoup(r.content, 'html.parser')
    return 'https://www.imdb.com{}'.format(soup.find('tr').a['href'])


def get_show_status(url):
    """Get the status of the show."""
    r = requests.get(url)
    doc = html.fromstring(r.content)

    runtime = doc.xpath('//div[@class="subtext"]/a/text()')[-1]
    if runtime[runtime.index('–') + 1:-2].isdigit():
        return 'The show has finished streaming all its episodes.'

    rel = doc.xpath('//div[@class="seasons-and-year-nav"]/div[3]/a[1]/@href')[0]
    latest_season_url = 'https://www.imdb.com{}'.format(rel)

    r = requests.get(latest_season_url)
    doc = html.fromstring(r.content)

    episodes = doc.xpath('//*[@id="episodes_content"]/div/div[2]/div')

    # Check whether the first episode is yet to be aired
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


def main():
    args = parser.parse_args()
    email = args.email
    shows = ' '.join(args.shows).split(',')
    statuses = []
    logging.info('Email: ' + email)
    logging.info('Shows: ' + str(shows))
    for show in shows:
        logging.info('Fetching: ' + show)
        url = get_show_url(show)
        status = get_show_status(url)
        statuses.append(status)

    logging.info('Generating message')
    msg = ""
    for show, status in zip(shows, statuses):
        msg += 'TV Series Name: ' + show.title() + '\n'
        msg += 'Status: ' + status + '\n\n'

    print(msg.strip())


if __name__ == '__main__':
    main()
