import mock
from datetime import datetime, timezone
import pytz
from nose.tools import assert_equals, assert_raises
from vogeltron import baseball
from bs4 import BeautifulSoup

YEAR = datetime.today().year


def date_for_month(month, day, hour, minute):
    timez = pytz.timezone('US/Pacific')
    return timez.localize(datetime(YEAR, month, day, hour, minute))


def april(day, hour, minute):
    return date_for_month(4, day, hour, minute)


def june(day, hour, minute):
    return date_for_month(6, day, hour, minute)


game = baseball.Result('LA Dodgers', april(1, 20, 5), False, False, '4-0')


def test_game_date():
    assert_equals(game.pretty_date, 'April 1')


def test_game_time():
    assert_equals(game.pretty_time, '08:05PM')


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
        baseball.Result('LA Dodgers', april(1, 13, 5), False, False, '4-0'),
        baseball.Result('LA Dodgers', april(2, 13, 5), False, True, '3-0'),
        baseball.Result('LA Dodgers', april(3, 13, 5), False, True, '5-3'),
        baseball.Result('St. Louis', april(5, 13, 5), True, True, '1-0'),
    ])


@mock.patch('requests.get')
def test_no_next_game(_get):
    _get().content = open('tests/fixtures/schedule_current_game.html').read()
    game_time, game_id = baseball.next_game('http://example.com')
    assert_equals(game_id, '330406126')


@mock.patch('requests.get')
def test_next_game_against_bluejays(_get):
    _get().content = \
        open('tests/fixtures/bluejays_with_double_header.html').read()
    game_time, game_id = baseball.next_game('http://example.com')

    assert game_time is not None
    assert_equals('330604126', game_id)


@mock.patch('requests.get')
def test_next_game(_get):
    _get().content = open('tests/fixtures/schedule.html').read()
    game_time, game_id = baseball.next_game('http://example.com')
    assert_equals(game_id, '330406126')
    assert_equals(game_time, april(6, 13, 5))


@mock.patch('requests.get')
def test_upcoming(_get):
    _get().content = open('tests/fixtures/schedule.html').read()
    _, upcoming = baseball.schedule('WEST', 'http://example.com')
    assert_equals(upcoming, [
        baseball.Result('St. Louis', april(6, 13, 5), True, None, '0-0'),
        baseball.Result('St. Louis', april(7, 13, 5), True, None, '0-0'),
        baseball.Result('Colorado', april(8, 19, 15), True, None, '0-0'),
        baseball.Result('Colorado', april(9, 19, 15), True, None, '0-0'),
        baseball.Result('Colorado', april(10, 12, 45), True, None, '0-0'),
    ])


@mock.patch('requests.get')
def test_upcoming_with_skipped(_get):
    webpage = open('tests/fixtures/bluejays_with_double_header.html').read()
    _get().content = webpage
    _, upcoming = baseball.schedule('WEST', 'http://example.com')

    print(upcoming[0].opponent)

    assert_equals(upcoming, [
        baseball.Result('Toronto', june(4, 19, 15), True, None, '0-0'),
        baseball.Result('Toronto', june(5, 12, 45), True, None, '0-0'),
        baseball.Result('Arizona', june(7, 18, 40), False, None, '0-0'),
        baseball.Result('Arizona', june(8, 19, 10), False, None, '0-0'),
        baseball.Result('Arizona', june(9, 13, 10), False, None, '0-0'),
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


def test_parse_gametime_tba():
    gt = baseball.parse_gametime("Mon, Apr 1", "TBA")
    assert_equals(pytz.utc.localize(datetime(YEAR, 4, 1, 20, 5)), gt)


def test_parse_gametime_postponed():
    gt = baseball.parse_gametime("Mon, Apr 1", "POSTPONED")
    assert_equals(pytz.utc.localize(datetime(YEAR, 4, 1, 20, 5)), gt)


def test_parse_gametime():
    gt = baseball.parse_gametime("Mon, Apr 1", "4:05 PM")
    assert_equals(pytz.utc.localize(datetime(YEAR, 4, 1, 20, 5)), gt)


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
