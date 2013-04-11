import mock
import pytz
from vogeltron import bot
from vogeltron.baseball import Standing, Game, Boxscore, Team, Player, Pitcher
from nose.tools import assert_equals
from datetime import datetime, timezone


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
        [Game('LA Dodgers', datetime(2013, 1, 1), True, True, "1-1")],
        [Game('LA Dodgers', datetime(2013, 1, 2), True, None, "0-0")],
    )
    _standings.return_value = [
        Standing('San Francisco', 3, 1, .75, 0.0),
        Standing('San Francisco', 3, 1, .75, 0.0),
    ]

    assert_equals(sidebar.strip(), bot.all_stats('NATIONAL', 'WEST', 'foo'))


def check_thread(start, end, opened):
    assert_equals(bot.thread_open(start, end), opened)


def test_thread_window():
    dt1 = datetime(2013, 4, 16, 12)
    dt2 = datetime(2013, 4, 16, 16)
    dt3 = datetime(2013, 4, 16, 15)
    dt4 = datetime(2013, 4, 16, 20)

    yield check_thread, dt2, dt1, True
    yield check_thread, dt2, dt2, True
    yield check_thread, dt2, dt3, True
    yield check_thread, dt1, dt2, False
    yield check_thread, dt1, dt4, False
    yield check_thread, dt4, dt1, False


def test_timestamp():
    zone = pytz.timezone('US/Pacific')

    assert ('PST' in bot.timestamp(zone) or
            'PDT' in bot.timestamp(zone))

teams = [
    Team('Rockies', '5-1', [Player('Foo', 'P')],
         Pitcher('Francis', '1-0', 1.5)),
    Team('Giants', '4-2', [Player('Bar', 'P')],
         Pitcher('Zito', '1-0', 0.0)),
]

game = Boxscore(teams, datetime(2013, 4, 10, 2, 15, tzinfo=timezone.utc))


@mock.patch('vogeltron.baseball.game_info')
def test_gameday_title(_game_info):
    _game_info.return_value = game

    title, _ = bot.gamethread_post('foo', pytz.timezone('US/Pacific'))

    assert_equals(title, ("Gameday Thread 4/9/13: Rockies "
                          "at Giants (7:15PM)"))


def test_reddit_url():
    title = "Gameday Thread 4/9/13: Rockies at Giants (7:15PM)"
    assert_equals(bot.post_url_prefix(title), "gameday_thread_4913")


exp_post = """
| Rockies (5-1) | Giants (4-2) |
| ------ | ------ |
| **Francis**: 1-0 1.50 ERA | **Zito**: 1-0 0.00 ERA |
| **Rockies Lineup** | **Giants Lineup** |
| Foo P | Bar P |

| UPVOTE FOR VISIBILITY/PRAISE HIM |
| ------ |

Last Updated @ foo
"""


exp_post_no_pitchers = """
| Rockies (5-1) | Giants (4-2) |
| ------ | ------ |
| **Rockies Lineup** | **Giants Lineup** |
| Foo P | Bar P |

| UPVOTE FOR VISIBILITY/PRAISE HIM |
| ------ |

Last Updated @ foo
"""


@mock.patch('vogeltron.bot.timestamp')
@mock.patch('vogeltron.baseball.game_info')
def test_gameday_post_no_pitchers(_game_info, _timestamp):
    teams = [
        Team('Rockies', '5-1', [Player('Foo', 'P')], None),
        Team('Giants', '4-2', [Player('Bar', 'P')], None),
    ]

    g = Boxscore(teams,
                 datetime(2013, 4, 10, 2, 15, tzinfo=timezone.utc))

    _timestamp.return_value = 'foo'
    _game_info.return_value = g

    _, post = bot.gamethread_post('foo', pytz.timezone('US/Pacific'))

    assert_equals(exp_post_no_pitchers.strip(), post)
