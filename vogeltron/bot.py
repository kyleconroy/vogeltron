"""
Author: RogueDarkJedi and Derferman
Desc: Updates a sidebar for a subreddit with the
newest Baseball data!
Usage: In the sidebar description, add the tags [](/statsstart) and
[](/statsend) where you want the table to go.
"""

import os
import logging
import datetime
import re
import raven
from jinja2 import Template

from . import baseball
from . import reddit


def _load_template(filename):
    subreddit = os.environ.get('VOGELTRON_TEAM', 'default').lower()

    subreddit_path = os.path.join(os.path.dirname(__file__), 'templates',
                                  subreddit, filename)
    default_path = os.path.join(os.path.dirname(__file__), 'templates',
                                'default', filename)

    if os.path.exists(subreddit_path):
        return Template(open(subreddit_path).read())
    else:
        return Template(open(default_path).read())


def timestamp(team_zone):
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.astimezone(team_zone).strftime("%Y-%m-%d %I:%M %p %Z")


def post_url_prefix(title):
    return title.split(':')[0].replace(' ', '_').replace('/', '').lower()


def post_game_url_prefix(title):
    return title.split('--', 1)[0].strip().lower()\
        .replace(':', '').replace(' ', '_').replace('/', '')


def all_stats(league, division, schedule_url):
    template = _load_template('all_stats.md')

    standings = baseball.current_standings(league, division)
    past, future = baseball.schedule(division, schedule_url)
    ts = timestamp(baseball.division_timezone(division))

    return template.render(standings=standings, past=past, future=future,
                           timestamp=ts)


def thread_open(gametime, now):
    if not gametime.date() == now.date():
        return False

    return now.hour >= 8


def update_standings(current_description, stats):
    amps = re.sub(r'&(amp;)+', '&', current_description)
    return re.sub(r'\[\]\(/all_statsstart\).*\[\]\(/all_statsend\)',
                  '[](/all_statsstart)\n' + stats + '\n[](/all_statsend)',
                  amps, flags=re.S)


def gamethread_post(espn_id, team_zone):
    game = baseball.game_info(espn_id)
    start = game.start_time.astimezone(team_zone)

    title = "Gameday Thread {}: {} ({}) at {} ({}) ({})".format(
        start.strftime("%-m/%-d/%y"),
        game.teams[0].name,
        game.teams[0].pitcher.name if game.teams[1].pitcher else 'TBA',
        game.teams[1].name,
        game.teams[1].pitcher.name if game.teams[1].pitcher else 'TBA',
        start.strftime("%-I:%M%p"))

    template = _load_template('gameday.md')

    home, away = game.teams
    players = zip(home.lineup, away.lineup)

    post = template.render(home=home, away=away, players=players,
                           timestamp=timestamp(team_zone),
                           weather=game.weather)

    return title, post


def update_sidebar(r, subreddit, team):
    about = r.settings(subreddit)
    stats = all_stats(team['league'], team['division'],
                      team['links']['schedule'])

    payload = {
        'description': update_standings(about['description'], stats),
        'link_type': 'any',
        'sr': about['subreddit_id'],
        'title': about['title'],
        'type': about['subreddit_type'],
        'wikimode': about['wikimode'],
    }

    r.admin(subreddit, payload)


def find_post(r, prefix):
    for post in r.submitted(r.username):
        if prefix in post['data']['url']:
            return post['data']['name']
    return None


def update_game_thread(r, subreddit, team):
    gametime, espn_id = baseball.next_game(team['links']['schedule'])

    if espn_id is None:
        logging.info("No game_id yet, can't make thread")
        return

    teamzone = baseball.division_timezone(team['division'])
    now = datetime.datetime.now(teamzone)

    if not thread_open(gametime.astimezone(teamzone), now):
        logging.info("Not time yet for game #{}".format(espn_id))
        return

    title, post = gamethread_post(espn_id, teamzone)

    post_id = find_post(r, post_url_prefix(title))

    if not post_id:
        logging.info("Creating game #{} thread".format(espn_id))
        r.submit(subreddit, title, post)
    else:
        logging.info("Editing game #{} thread".format(espn_id))
        r.edit(post_id, post)


def postgame_thread_post(game, name, team_zone):
    fmt = ("POSTGAME THREAD {} -- {} vs {} -- Join the Giants game / baseball "
           "discussion and social thread!")

    start = game.datetime.astimezone(team_zone)

    title = fmt.format(start.strftime("%-m/%-d"), name, game.opponent)

    template = _load_template('postgame.md')

    post = template.render()

    return title, post


def update_post_game_thread(r, subreddit, team):
    past, _ = baseball.schedule(team['division'],
                                team['links']['schedule'])
    game = past[-1]

    teamzone = baseball.division_timezone(team['division'])
    title, post = postgame_thread_post(game, team['name'], teamzone)

    post_id = find_post(r, post_game_url_prefix(title))

    if not post_id:
        logging.info("Creating postgame thread")
        r.submit(subreddit, title, post)


def enabled(key):
    return os.environ.get(key, '').lower() != 'false'


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting bot')

    sentry = raven.Client(os.environ.get('VOGELTRON_SENTRY_DSN', ''))

    try:

        r = reddit.Client(os.environ['VOGELTRON_USERNAME'],
                          os.environ['VOGELTRON_PASSWORD'])

        team = baseball.team_info(os.environ['VOGELTRON_TEAM'])
        subreddit = os.environ['VOGELTRON_SUBREDDIT']

        if enabled('VOGELTRON_SIDEBAR'):
            update_sidebar(r, subreddit, team)

        if enabled('VOGELTRON_GAMEDAY_THREAD'):
            update_game_thread(r, subreddit, team)

        if enabled('VOGELTRON_POSTGAME_THREAD'):
            update_post_game_thread(r, subreddit, team)

        logging.info('Stopping bot')

    except:
        sentry.captureException()
