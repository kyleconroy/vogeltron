import bot
import mock
import datetime
from baseball import Standing, Game
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


@mock.patch('bot.all_stats')
def test_update_description(_stats):
    _stats.return_value = "bar"
    assert_equals(exp_markdown.strip(), bot.update_standings(markdown).strip())


@mock.patch('bot.timestamp')
@mock.patch('baseball.current_standings')
@mock.patch('baseball.giants_schedule')
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

    assert_equals(sidebar.strip(), bot.all_stats())


def test_timestamp():
    assert ('PST' in bot.timestamp() or 'PDT' in bot.timestamp())
