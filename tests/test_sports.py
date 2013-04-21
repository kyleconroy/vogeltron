import mock
from datetime import datetime, timezone, date
import pytz
from nose.tools import assert_equals, assert_raises
from vogeltron import baseball
from bs4 import BeautifulSoup


def april(day, hour, minute):
    year = date.today().year
    return pytz.utc.localize(datetime(year, 4, day, hour, minute))

game = baseball.Game('LA Dodgers', april(1, 20, 5), False, False, '4-0')


def test_game_date():
    assert_equals(game.date, 'April 1')


def test_game_time():
    assert_equals(game.time, '08:05PM')


def test_game_description():
    assert_equals(game.description, 'at LA Dodgers')


@mock.patch('requests.get')
def test_all_teams(_get):
    _get().content = open('tests/fixtures/teams.html').read()
    teams = baseball.teams()
    assert_equals(len(teams), 30)


@mock.patch('requests.get')
def test_first_teams(_get):
    _get().content = open('tests/fixtures/teams.html').read()
    team = baseball.teams()[0]

    assert_equals(team['name'], 'Baltimore Orioles')
    assert_equals(team['league'], 'AMERICAN')
    assert_equals(team['division'], 'EAST')
    assert_equals(team['links']['schedule'],
                  'http://espn.go.com/mlb/teams/schedule?team=bal')


@mock.patch('requests.get')
def test_results(_get):
    _get().content = open('tests/fixtures/schedule.html').read()
    results, _ = baseball.schedule('WEST', 'http://example.com')
    assert_equals(results, [
        baseball.Game('LA Dodgers', april(1, 20, 5), False, False, '4-0'),
        baseball.Game('LA Dodgers', april(2, 20, 5), False, True, '3-0'),
        baseball.Game('LA Dodgers', april(3, 20, 5), False, True, '5-3'),
        baseball.Game('St. Louis', april(5, 20, 5), True, True, '1-0'),
    ])


@mock.patch('requests.get')
def test_no_next_game(_get):
    _get().content = open('tests/fixtures/schedule_current_game.html').read()
    game_time, game_id = baseball.next_game('http://example.com')
    assert_equals(game_id, '330406126')


@mock.patch('requests.get')
def test_next_game(_get):
    _get().content = open('tests/fixtures/schedule.html').read()
    game_time, game_id = baseball.next_game('http://example.com')
    assert_equals(game_id, '330406126')
    assert_equals(game_time, april(6, 20, 5))


@mock.patch('requests.get')
def test_upcoming(_get):
    _get().content = open('tests/fixtures/schedule.html').read()
    _, upcoming = baseball.schedule('WEST', 'http://example.com')
    assert_equals(upcoming, [
        baseball.Game('St. Louis', april(6, 20, 5), True, None, '0-0'),
        baseball.Game('St. Louis', april(7, 20, 5), True, None, '0-0'),
        baseball.Game('Colorado', april(9, 2, 15), True, None, '0-0'),
        baseball.Game('Colorado', april(10, 2, 15), True, None, '0-0'),
        baseball.Game('Colorado', april(10, 19, 45), True, None, '0-0'),
    ])


@mock.patch('requests.get')
def test_standings(_get):
    _get().content = open('tests/fixtures/standings.html').read()
    standings = baseball.current_standings('NATIONAL', 'WEST')

    examples = [
        baseball.Standing('San Francisco', 'SF', 3, 1, .75, 0.0, 'Won 3'),
        baseball.Standing('Colorado', 'COL', 3, 1, .75, 0.0, 'Won 3'),
        baseball.Standing('Arizona', 'ARI', 2, 1, .667, 0.5, 'Won 1'),
        baseball.Standing('LA Dodgers', 'LAD', 1, 2, .333, 1.5, 'Lost 2'),
        baseball.Standing('San Diego', 'SD', 1, 3, .250, 2.0, 'Lost 1'),
    ]

    assert_equals(standings, examples)


def test_parse_gametime():
    gt = baseball.parse_gametime("Mon, Apr 1", "4:05 PM")
    assert_equals(pytz.utc.localize(datetime(2013, 4, 1, 20, 5)), gt)


def test_no_team_info():
    with assert_raises(Exception):
        baseball.team_info('Giantssjk')


def test_team_info():
    team = baseball.team_info('Giants')
    assert_equals(team['name'], 'San Francisco Giants')


def test_normalize():
    assert_equals(baseball.normalize('Giants'), 'GIANTS')
    assert_equals(baseball.normalize('Francisco Giants'), 'FRANCISCOGIANTS')
    assert_equals(baseball.normalize('Red-Sox'), 'REDSOX')


def test_preview_weather():
    soup = BeautifulSoup(open('tests/fixtures/preview_during.html'))
    assert_equals(baseball.parse_weather(soup), '40° Broken Clouds')


def test_preview_gametime():
    soup = BeautifulSoup(open('tests/fixtures/preview_during.html'))
    assert_equals(baseball.parse_game_time(soup),
                  datetime(2013, 4, 13, 17, 5, tzinfo=timezone.utc))


def test_preview_teamname():
    soup = BeautifulSoup(open('tests/fixtures/preview_during.html'))
    name, record = baseball.parse_team_info(soup, 0)
    assert_equals(name, "Giants")
    assert_equals(record, "7-4")


def test_preview_pitcher():
    soup = BeautifulSoup(open('tests/fixtures/preview_during.html'))
    pitcher = baseball.parse_starting_pitcher(soup, 0)

    assert_equals(pitcher.name, "Bumgarner")
    assert_equals(pitcher.era, 0.96)
    assert_equals(pitcher.record, '2-0')


def test_preview_lineup():
    soup = BeautifulSoup(open('tests/fixtures/preview_during.html'))
    lineup = baseball.parse_starting_lineup(soup, 0)
    blanco = lineup[0]

    assert_equals(len(lineup), 9)
    assert_equals(blanco.name, 'Blanco')
    assert_equals(blanco.position, 'CF')
