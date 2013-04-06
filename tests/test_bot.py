import bot
import mock
from baseball import Standing
from nose.tools import assert_equals


sidebar = """
##Standings
------------

| Team | W | L | W/L% | GB |
| ------ | ------ | ----- | ----- | ----- |
| San Francisco | 3 | 1 | 0.75 | -- |
| San Francisco | 3 | 1 | 0.75 | -- |

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
def test_all_stats(_standings, _timestamp):
    _timestamp.return_value = "2013-04-06 12:31 AM"
    _standings.return_value = [
        Standing('San Francisco', 3, 1, .75, 0.0),
        Standing('San Francisco', 3, 1, .75, 0.0),
    ]

    assert_equals(sidebar.strip(), bot.all_stats())


def test_timestamp():
    assert ('PST' in bot.timestamp() or 'PDT' in bot.timestamp())
