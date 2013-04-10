import mock
from datetime import datetime, timezone, date
import pytz
from nose.tools import assert_equals, assert_raises
from vogeltron import baseball


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
    assert_equals(standings, [
        baseball.Standing('San Francisco', 3, 1, .75, 0.0),
        baseball.Standing('Colorado', 3, 1, .75, 0.0),
        baseball.Standing('Arizona', 2, 1, .667, 0.5),
        baseball.Standing('LA Dodgers', 1, 2, .333, 1.5),
        baseball.Standing('San Diego', 1, 3, .250, 2.0),
    ])


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


@mock.patch('requests.get')
def test_boxscore_early(_get):
    _get().content = open('tests/fixtures/boxscore_early.html').read()
    game = baseball.game_info('345')
    a, b = game.teams

    assert_equals(len(a.lineup), 9)
    assert_equals(len(b.lineup), 9)
    assert_equals(game.start_time,
                  datetime(2013, 4, 10, 2, 15, tzinfo=timezone.utc))


@mock.patch('requests.get')
def test_boxscore(_get):
    _get().content = open('tests/fixtures/boxscore.html').read()
    game = baseball.game_info('345')
    rockies, giants = game.teams

    assert_equals(len(giants.lineup), 9)
    assert_equals(len(rockies.lineup), 9)

    assert_equals(giants.name, 'San Francisco Giants')
    assert_equals(giants.record, '4-3')

    assert_equals(rockies.name, 'Colorado Rockies')
    assert_equals(rockies.record, '5-2')

    assert_equals(game.start_time,
                  datetime(2013, 4, 9, 2, 15, tzinfo=timezone.utc))
