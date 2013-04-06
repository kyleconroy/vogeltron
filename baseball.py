import requests
import datetime
import pytz
from collections import namedtuple
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
STATS_URL = "http://espn.go.com/mlb/standings"
SCHEDULE_URL = ("http://espn.go.com/mlb/team/schedule/"
                "_/name/sf/san-francisco-giants")

Standing = namedtuple('Standing', 'name, wins, losses, ratio, games_back')


class Game(object):

    def __init__(self, opponent, datetime, home, win, score):
        self.opponent = opponent
        self.datetime = datetime
        self.home = home
        self.win = win
        self.score = score

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def date(self):
        return "{} {}".format(self.datetime.strftime("%B"),
                              int(self.datetime.strftime("%d")))

    @property
    def time(self):
        return self.datetime.strftime("%I:%M%p")

    @property
    def w(self):
        return "W" if self.win else "L"

    @property
    def description(self):
        return "{} {}".format("vs" if self.home else "at", self.opponent)


def parse_gametime(date, time):
    today = datetime.date.today()
    timestamp = "{} {} {}".format(date, time, today.year)
    gametime = datetime.datetime.strptime(timestamp, "%a, %b %d %I:%M %p %Y")
    eastern = pytz.timezone('US/Eastern')
    return eastern.localize(gametime).astimezone(pytz.utc)


def giants_schedule():
    resp = requests.get(SCHEDULE_URL, headers={'User-Agent': USER_AGENT})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content)
    table = soup.find("table", class_="tablehead")

    past = []
    future = []
    pacific = pytz.timezone('US/Pacific')

    for tr in table.find_all("tr"):
        if 'stathead' in tr['class'] or 'colhead' in tr['class']:  # League Row
            continue

        d = tr.find_all('td')

        status, _, team_name = d[1].find_all('li')

        # Game currently in progress, ignore
        if len(d[2].find_all('li')) == 1:
            continue

        try:
            win_node, score_node = d[2].find_all('li')
            win = win_node.text.strip().upper() == 'W'
            score = score_node.text.strip().upper()
            clock = "04:05 PM"
        except ValueError:
            clock = d[2].text.strip()
            win = None
            score = "0-0"

        gametime = parse_gametime(d[0].text, clock)

        home = status.text.strip().upper() == "VS"
        opponent = team_name.text.strip()

        game = Game(opponent, gametime.astimezone(pacific), home, win, score)

        if win is None:
            future.append(game)
        else:
            past.append(game)

    return past[-5:], future[:5]


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
            d[0].text,  # Team name
            int(d[1].text),  # Wins
            int(d[2].text),  # Losses
            float(d[3].text),  # Win Percentage
            0.0 if d[4].text == "-" else float(d[4].text)  # Games back
        ))

    return standings[league][division]
