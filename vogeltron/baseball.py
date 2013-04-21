import requests
import datetime
import pytz
import re
import json
import os
import collections
import logging
from urllib import parse
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
STANDINGS_URL = "http://espn.go.com/mlb/standings"
TEAMS_URL = "http://espn.go.com/mlb/teams"
PREVIEW_URL = "http://espn.go.com/mlb/preview?gameId={}"


class Standing(object):

    def __init__(self, name, abbr, wins, losses, ratio, games_back, streak):
        self.team_abbr = abbr
        self.name = name
        self.wins = wins
        self.losses = losses
        self.ratio = ratio
        self.games_back = games_back

        result, length = streak.split(' ')
        self.streak = "{}{}".format(result[0], length).upper()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def record(self):
        return "{0:0.3f}".format(self.ratio).lstrip('0')

    @property
    def back(self):
        if self.games_back < 0.5:
            return "--"
        return self.games_back


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
Boxscore = collections.namedtuple('Boxscore', 'teams, start_time, weather')


class Pitcher(object):

    def __init__(self, name, record, era):
        self.name = name
        self.record = record
        self.era = era

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        if self.record is None or self.era is None:
            return "**{}**".format(self.name)
        fmt = "**{}**: {} {:0.2f} ERA"
        return fmt.format(self.name, self.record, self.era)


class Team(object):

    def __init__(self, name, record, lineup, pitcher):
        self.name = name
        self.record = record
        self.lineup = lineup
        self.pitcher = pitcher

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def parse_weather(soup):
    """Return the weather"""
    return soup.find('p', class_='weather').text.replace('°', '° ')


def parse_team(soup, index):
    """Return the teams playing"""
    name, record = parse_team_info(soup, index)
    return Team(name, record, parse_starting_lineup(soup, index),
                parse_starting_pitcher(soup, index))


def _find_info_table(soup, headline):
    for div in soup.find_all('div', class_='mod-open-gamepack'):
        header = div.find('h4')

        if header is None:
            continue

        if header.text.lower().strip() == headline.lower().strip():
            return div.find('table')

    return None


def parse_starting_pitcher(soup, index):
    """Return the starting home and away pitchers"""
    table = _find_info_table(soup, 'Pitching Matchup')

    if table is None:
        logging.error("Can't find starting pitchers")
        return None

    tds = table.find_all('td')

    if len(tds) != 4:
        logging.error("Not enough table cells in pitching info")
        return None

    info = tds[index * 2 + 1].text.replace("\n", " ")
    m = re.search('(.*)\. (.*) (.*), (.*) ERA', info)

    if m is None:
        logging.error("Can't match the pitching info")
        return None

    return Pitcher(m.group(2), m.group(3), float(m.group(4)))


def parse_starting_lineup(soup, index):
    """Return the starting home and away lineup"""
    table = _find_info_table(soup, 'Gameday Lineups')

    if table is None:
        logging.error("Can't find starting lineup")
        return []

    players = []

    for row in table.find_all('tr'):
        cells = row.find_all('td')

        if not cells:  # Headers
            continue

        text = row.find_all('td')[index + 1].text

        _, namepos = text.split('. ', 1)
        name, position = namepos.split(', ', 1)

        players.append(Player(name, position))

    return players


def parse_team_info(soup, index):
    info_box = soup.find_all('div', class_='team-info')[index]
    team_name = info_box.find('h3').find('a').text
    record = info_box.find('p').text.replace('(', '').split(',')[0]
    return team_name, record


def parse_game_time(soup):
    """Return the start time in UTC"""
    timestamp = soup.find('div', class_='game-time-location').find('p').text
    gametime = datetime.datetime.strptime(timestamp.replace("ET", ""),
                                          "%I:%M %p , %B %d, %Y")
    eastern = pytz.timezone('US/Eastern')
    return eastern.localize(gametime).astimezone(pytz.utc)


def game_info(espn_id):
    soup = make_soup(PREVIEW_URL.format(espn_id))

    return Boxscore([parse_team(soup, 0), parse_team(soup, 1)],
                    parse_game_time(soup), parse_weather(soup))


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
        link = d[0].find('a')
        uri = link['href'].replace('http://espn.go.com/mlb/team/_/name/', '')

        current.append(Standing(
            d[0].text,  # Team name
            uri[:3].upper().replace('/', ''),
            int(d[1].text),  # Wins
            int(d[2].text),  # Losses
            float(d[3].text),  # Win Percentage
            0.0 if d[4].text == "-" else float(d[4].text),  # Games back
            d[10].text.replace('  ', ' ').strip()  # Streak
        ))

    return standings[league][division]
