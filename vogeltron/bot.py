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
from pytz import timezone
from jinja2 import Template

from . import baseball
from . import reddit


def timestamp():
    pacific = timezone('US/Pacific')
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.astimezone(pacific).strftime("%Y-%m-%d %I:%M %p %Z")


def all_stats(league, division, schedule_url):
    path = os.path.join(os.path.dirname(__file__), 'templates/all_stats.md')
    template = Template(open(path).read())

    standings = baseball.current_standings(league, division)
    past, future = baseball.schedule(division, schedule_url)

    return template.render(standings=standings, past=past, future=future,
                           timestamp=timestamp())


def thread_open(gametime, now):
    seconds = (gametime - now).total_seconds()
    return seconds > -600 and seconds <= 25200


def update_standings(current_description, stats):
    return re.sub(r'\[\]\(/all_statsstart\).*\[\]\(/all_statsend\)',
                  '[](/all_statsstart)\n' + stats + '\n[](/all_statsend)',
                  current_description, flags=re.S)


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

    return r.admin(subreddit, payload)


def update_game_thread(r, subreddit, team):
    gametime, espn_id = baseball.next_game(team['links']['schedule'])
    now = datetime.datetime.now(datetime.timezone.utc)

    if not thread_open(gametime, now):
        return

    pass


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
    update_game_thread(r, subreddit, team)
    update_post_game_thread(r, subreddit, team)

    logging.info('Stopping bot')
