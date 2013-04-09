import mock
import datetime
from vogeltron import bot
from vogeltron.baseball import Standing, Game
from nose.tools import assert_equals


sidebar = """
##Standings
##Last 5
##Next 5 Games
------------

| Team | W | L | W/L% | GB |
| ------ | ------ | ----- | ----- | ----- |
| San Francisco | 3 | 1 | 0.75 | -- |
| San Francisco | 3 | 1 | 0.75 | -- |

| Date | vs. | W/L | Score |
| ------ | ------ | ----- | ----- |
| January 1 | LA Dodgers | W | 1-1 |

| Date | Time | Opponent |
| ------ | ------ | ----- |
| January 2 | 12:00AM | vs LA Dodgers |

Last Updated @ 2013-04-06 12:31 AM
"""

markdown = """
[](/all_statsstart)
foo
[](/all_statsend)
"""

exp_markdown = """
[](/all_statsstart)
bar
[](/all_statsend)
"""


def test_update_description_amps():
    assert_equals("&", bot.update_standings("&amp;amp;amp;", 'bar').strip())


def test_update_description():
    assert_equals(exp_markdown.strip(),
                  bot.update_standings(markdown, 'bar').strip())


@mock.patch('vogeltron.bot.timestamp')
@mock.patch('vogeltron.baseball.current_standings')
@mock.patch('vogeltron.baseball.schedule')
def test_all_stats(_schedule, _standings, _timestamp):
    _timestamp.return_value = "2013-04-06 12:31 AM"
    _schedule.return_value = (
        [Game('LA Dodgers', datetime.datetime(2013, 1, 1), True, True, "1-1")],
        [Game('LA Dodgers', datetime.datetime(2013, 1, 2), True, None, "0-0")],
    )
    _standings.return_value = [
        Standing('San Francisco', 3, 1, .75, 0.0),
        Standing('San Francisco', 3, 1, .75, 0.0),
    ]

    assert_equals(sidebar.strip(), bot.all_stats('NATIONAL', 'WEST', 'foo'))


def check_thread(start, end, opened):
    assert_equals(bot.thread_open(start, end), opened)


def test_thread_window():
    dt1 = datetime.datetime(2013, 4, 16, 12)
    dt2 = datetime.datetime(2013, 4, 16, 16)
    dt3 = datetime.datetime(2013, 4, 16, 15)
    dt4 = datetime.datetime(2013, 4, 16, 20)

    yield check_thread, dt2, dt1, True
    yield check_thread, dt2, dt2, True
    yield check_thread, dt2, dt3, True
    yield check_thread, dt1, dt2, False
    yield check_thread, dt1, dt4, False
    yield check_thread, dt4, dt1, False


def test_timestamp():
    assert ('PST' in bot.timestamp() or 'PDT' in bot.timestamp())
