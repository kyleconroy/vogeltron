import mock
import baseball
import datetime
import pytz
from nose.tools import assert_equals


def april(day, hour, minute):
    year = datetime.date.today().year
    return pytz.utc.localize(datetime.datetime(year, 4, day, hour, minute))

game = baseball.Game('LA Dodgers', april(1, 20, 5), False, False, '4-0')


def test_game_date():
    assert_equals(game.date, 'April 1')


def test_game_time():
    assert_equals(game.time, '08:05PM')


@mock.patch('requests.get')
def test_results(_get):
    _get().content = open('tests/fixtures/stats.html').read()
    results, _ = baseball.giants_schedule()
    assert_equals(results, [
        baseball.Game('LA Dodgers', april(1, 20, 5), False, False, '4-0'),
        baseball.Game('LA Dodgers', april(2, 20, 5), False, True, '3-0'),
        baseball.Game('LA Dodgers', april(3, 20, 5), False, True, '5-3'),
        baseball.Game('St. Louis', april(5, 20, 5), True, True, '1-0'),
    ])


@mock.patch('requests.get')
def test_upcoming(_get):
    _get().content = open('tests/fixtures/stats.html').read()
    _, upcoming = baseball.giants_schedule()
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
    assert_equals(pytz.utc.localize(datetime.datetime(2013, 4, 1, 20, 5)), gt)
