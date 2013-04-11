import requests
import datetime
import pytz
import re
import json
import os
import collections
from urllib import parse
from collections import namedtuple
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
STANDINGS_URL = "http://espn.go.com/mlb/standings"
TEAMS_URL = "http://espn.go.com/mlb/teams"
BOXSCORE_URL = "http://espn.go.com/mlb/boxscore?gameId={}"


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
    timestamp = "{} {} {}".format(date.strip(), time.strip(), today.year)
    gametime = datetime.datetime.strptime(timestamp, "%a, %b %d %I:%M %p %Y")
    eastern = pytz.timezone('US/Eastern')
    return eastern.localize(gametime).astimezone(pytz.utc)


def make_soup(url):
    resp = requests.get(url, headers={'User-Agent': USER_AGENT})
    resp.raise_for_status()
    return BeautifulSoup(resp.content)


def division_timezone(division):
    """For a given division, return the correct timezone"""
    if division == 'EAST':
        return pytz.timezone('US/Eastern')
    elif division == 'CENTRAL':
        return pytz.timezone('US/Central')
    else:
        return pytz.timezone('US/Pacific')


def normalize(name):
    return name.upper().replace(" ", "").replace("-", "")


Player = collections.namedtuple('Player', 'name, position')
Team = collections.namedtuple('Team', 'name, record, lineup')
Boxscore = collections.namedtuple('Boxscore', 'teams, start_time')


def game_info(espn_id):
    soup = make_soup(BOXSCORE_URL.format(espn_id))
    boxes = soup.find_all('table', class_='mlb-box')

    teams = []

    for info_box in soup.find_all('div', class_='team-info'):
        team_name = info_box.find('h3').find('a').text
        record = info_box.find('p').text.replace('(', '').split(',')[0]
        teams.append(Team(team_name, record, []))

    for i, databox in enumerate(boxes):
        if len(databox.find_all('thead')) > 2:
            continue

        team_name = databox.find('thead').find_all('tr')[0].text
        player_type = databox.find('thead').find_all('tr')[1].text

        if 'pitchers' in player_type.lower():
            continue

        players = databox.find_all('tbody')[0]

        team = [t for t in teams if team_name.endswith(t.name)].pop()

        for player in players:
            name = player.find('td')

            if name.find('div'):  # Not starting
                continue

            full_name, position = name.text.rsplit(' ', 1)
            _, last_name = full_name.split(' ', 1)

            team.lineup.append(Player(last_name, position))

    timestamp = soup.find('div', class_='game-time-location').find('p').text
    gametime = datetime.datetime.strptime(timestamp.replace("ET", ""),
                                          "%I:%M %p , %B %d, %Y")
    eastern = pytz.timezone('US/Eastern')

    return Boxscore(teams, eastern.localize(gametime).astimezone(pytz.utc))


def team_info(name):
    path = os.path.join(os.path.dirname(__file__), 'teams.json')
    teams = json.load(open(path))

    for team in teams:
        if normalize(team['name']).endswith(normalize(name)):
            return team

    raise Exception("No team found for {}".format(name))


def teams():
    soup = make_soup(TEAMS_URL)
    divisions = soup.find_all("div", class_="mod-open-list")

    teams = []

    for div in divisions:
        league, division = div.find('div', class_='stathead').text.split(' ')

        for li in div.find_all('li'):
            menu = li.find_all('span')[-1]

            links = {}

            for a in menu.find_all('a'):
                links[a.text.lower()] = 'http://espn.go.com' + a['href']

            team = {
                'league': 'NATIONAL' if league == 'NL' else 'AMERICAN',
                'division': division.upper(),
                'name': li.find('h5').text,
                'links': links,
            }

            teams.append(team)

    return teams


def next_game(schedule_url):
    soup = make_soup(schedule_url)
    table = soup.find("table", class_="tablehead")

    for tr in table.find_all("tr"):
        if 'stathead' in tr['class'] or 'colhead' in tr['class']:  # League Row
            continue

        d = tr.find_all('td')

        if len(d[2].find_all('li')) > 1:
            continue

        preview_link = d[2].find('a')

        if not preview_link:
            return parse_gametime(d[0].text, d[2].text), None

        if 'gamecast' in preview_link.get('onclick', []):
            match = re.search('gamecast(\d+)', preview_link['onclick'])
            now = datetime.datetime.now(datetime.timezone.utc)
            return now, match.group(1)
        else:
            parts = parse.urlparse(preview_link['href'])
            query = parse.parse_qs(parts.query)
            return parse_gametime(d[0].text, d[2].text), query['id'].pop()

    return None, None  # Game currently in progress


def schedule(division, schedule_url):
    soup = make_soup(schedule_url)
    table = soup.find("table", class_="tablehead")

    past = []
    future = []

    for tr in table.find_all("tr"):
        if 'stathead' in tr['class'] or 'colhead' in tr['class']:  # League Row
            continue

        d = tr.find_all('td')

        status, _, team_name = d[1].find_all('li')
        team_zone = division_timezone(division)

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

        game = Game(opponent, gametime.astimezone(team_zone), home, win, score)

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

    soup = make_soup(STANDINGS_URL)

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
