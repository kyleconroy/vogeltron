import requests
from collections import namedtuple
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
STATS_URL = "http://espn.go.com/mlb/standings"
Standing = namedtuple('Standing', 'name, wins, losses, ratio, games_back')


def current_standings(league, division):
    """Return the current standings for the given league and division

    :returns: List of Standings
    """
    standings = {
        'NATIONAL': {
            'EAST': [],
            'WEST': [],
            'CENTRAL': [],
        },
        'AMERICAN': {
            'EAST': [],
            'WEST': [],
            'CENTRAL': [],
        },
    }

    resp = requests.get(STATS_URL, headers={'User-Agent': USER_AGENT})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content)

    table = soup.find("table", class_="tablehead")

    active_league = None
    active_division = None

    for tr in table.find_all("tr"):
        if 'stathead' in tr['class']:  # League Row
            active_league = tr.text.strip().upper().replace(" LEAGUE", "")
            continue

        if 'colhead' in tr['class']:  # Division Row
            active_division = tr.find('td').text.strip().upper()
            continue

        current = standings[active_league][active_division]

        d = tr.find_all('td')
        current.append(Standing(
            d[0].text,
            int(d[1].text),
            int(d[2].text),
            float(d[3].text),
            0.0 if d[4].text == "-" else float(d[4].text)
        ))

    return standings[league][division]
