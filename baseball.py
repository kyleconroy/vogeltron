import requests
import datetime
from collections import namedtuple
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
STATS_URL = "http://www.baseball-reference.com/leagues/{}/{}.shtml"
Standing = namedtuple('Standing',
                      'name, abbr, wins, losses, ratio, games_back')


def current_standings(league, division):
    """Return the current standings for the given league and division

    :returns: List of Standings
    """
    url = STATS_URL.format(league, datetime.date.today().year)

    resp = requests.get(url, headers={'User-Agent': USER_AGENT})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content)
    region_id = "standings_{}".format(division[0].upper())

    table = soup.find(id=region_id)

    standings = []

    for tr in table.find('tbody').find_all('tr'):
        link, abbr, wins, losses, ratio, games_back = tr.find_all('td')
        s = Standing(
            link.find('a')['title'],
            abbr.text.upper(),
            int(wins.text),
            int(losses.text),
            float(ratio.text),
            0.0 if games_back.text == "--" else float(games_back.text),
        )
        standings.append(s)

    return standings
