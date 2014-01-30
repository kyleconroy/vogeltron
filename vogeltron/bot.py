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
import jinja2

from . import baseball
from . import reddit
from . import filters


loader = jinja2.PackageLoader('vogeltron', 'templates')
env = jinja2.Environment(loader=loader)
env.filters['nationals_team_abbr'] = filters.nationals_team_abbr


def _load_template(filename):
    subreddit = os.environ.get('VOGELTRON_TEAM', 'default').lower()
    try:
        return env.get_template(os.path.join(subreddit, filename))
    except jinja2.TemplateNotFound:
        return env.get_template(os.path.join('default', filename))


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
    start = game.datetime.astimezone(team_zone)

    title_template = _load_template('gameday_title.txt')
    post_template = _load_template('gameday.md')

    #  start.strftime("%-m/%-d/%y"),
    #  start.strftime("%-I:%M%p"))

    home, away = game.teams
    players = zip(home.lineup, away.lineup)

    post = post_template.render(home=home, away=away, players=players,
                                timestamp=timestamp(team_zone),
                                weather=game.weather)

    title = title_template.render(home=home, away=away, start=start)

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
        post_id = find_post(r, post_url_prefix(title))
        r.sticky(post_id)
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

        post_id = find_post(r, post_game_url_prefix(title))
        r.sticky(post_id)


def enabled(key):
    return os.environ.get(key, '').lower() != 'false'


def update(settings):
    r = reddit.Client(settings['username'], settings['password'])

    team = baseball.team_info(settings['team'])
    subreddit = settings['subreddit']

    logging.info('Starting update for /r/' + subreddit)

    if settings.get('sidebar'):
        update_sidebar(r, subreddit, team)

    if settings.get('postgame_thread'):
        update_post_game_thread(r, subreddit, team)

    if settings.get('gameday_thread'):
        update_game_thread(r, subreddit, team)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    sentry = raven.Client(os.environ.get('SENTRY_DSN', ''))

    reddits = [{
        'username': 'vogeltron',
        'password': os.environ['VOGELTRON_PASSWORD'],
        'team': 'Nationals',
        'subreddit': 'nationals',
        'sidebar': True,
    }, {
        'username': 'sfgbot',
        'password': os.environ['SFGBOT_PASSWORD'],
        'team': 'Giants',
        'subreddit': 'sfgiants',
        'sidebar': True,
        'postgame_thread': True,
        'gameday_thread': True,
    }]

    for subreddit in reddits:
        try:
            update(subreddit)
        except Exception as e:
            sentry.captureException()
            raise e
