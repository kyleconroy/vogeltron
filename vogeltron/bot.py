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
from jinja2 import Template

from . import baseball
from . import reddit


def timestamp(team_zone):
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.astimezone(team_zone).strftime("%Y-%m-%d %I:%M %p %Z")


def post_url_prefix(title):
    return title.split(':')[0].replace(' ', '_').replace('/', '').lower()


def all_stats(league, division, schedule_url):
    path = os.path.join(os.path.dirname(__file__), 'templates/all_stats.md')
    template = Template(open(path).read())

    standings = baseball.current_standings(league, division)
    past, future = baseball.schedule(division, schedule_url)
    ts = timestamp(baseball.division_timezone(division))

    return template.render(standings=standings, past=past, future=future,
                           timestamp=ts)


def thread_open(gametime, now):
    seconds = (gametime - now).total_seconds()
    return seconds > -600 and seconds <= 25200


def update_standings(current_description, stats):
    amps = re.sub(r'&(amp;)+', '&', current_description)
    return re.sub(r'\[\]\(/all_statsstart\).*\[\]\(/all_statsend\)',
                  '[](/all_statsstart)\n' + stats + '\n[](/all_statsend)',
                  amps, flags=re.S)


def gamethread_post(espn_id, team_zone):
    game = baseball.game_info(espn_id)
    start = game.start_time.astimezone(team_zone)

    title = "Gameday Thread {}: {} at {} ({})".format(
        start.strftime("%-m/%-d/%y"),
        game.teams[0].name,
        game.teams[1].name,
        start.strftime("%-I:%M%p"))

    path = os.path.join(os.path.dirname(__file__), 'templates/gameday.md')
    template = Template(open(path).read())

    home, away = game.teams
    players = zip(home.lineup, away.lineup)

    post = template.render(home=home, away=away, players=players,
                           timestamp=timestamp(team_zone))

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
    now = datetime.datetime.now(datetime.timezone.utc)

    if espn_id is None:
        logging.info("No game_id yet, can't make thread")
        return

    if not thread_open(gametime, now):
        logging.info("Not time yet for game #{}".format(espn_id))
        return

    teamzone = baseball.division_timezone(team['division'])
    title, post = gamethread_post(espn_id, teamzone)

    post_id = find_post(r, post_url_prefix(title))

    if not post_id:
        logging.info("Creating game #{} thread".format(espn_id))
        r.submit(subreddit, title, post)
    else:
        logging.info("Editing game #{} thread".format(espn_id))
        r.edit(post_id, post)


def update_post_game_thread(r, subreddit, team):
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting bot')

    r = reddit.Client(os.environ['VOGELTRON_USERNAME'],
                      os.environ['VOGELTRON_PASSWORD'])

    team = baseball.team_info(os.environ['VOGELTRON_TEAM'])
    subreddit = os.environ['VOGELTRON_SUBREDDIT']

    update_sidebar(r, subreddit, team)

    if not os.environ.get('VOGELTRON_GAMEDAY_THREAD', '').lower() == 'false':
        update_game_thread(r, subreddit, team)

    update_post_game_thread(r, subreddit, team)

    logging.info('Stopping bot')
