"""
Author: RogueDarkJedi and Derferman
Desc: Updates a sidebar for a subreddit with the
newest Baseball data!
Usage: In the sidebar description, add the tags [](/statsstart) and
[](/statsend) where you want the table to go.
"""
import os
import logging
import reddit
import baseball
import datetime
import re
from pytz import timezone
from jinja2 import Template

logger = logging.getLogger('sfgiants')

SUBREDDIT = os.environ.get("VOGELTRON_SUBREDDIT", "SFGiants")
LEAGUE = os.environ.get("VOGELTRON_LEAGUE", "NATIONAL")
DIVISION = os.environ.get("VOGELTRON_DIVISION", "WEST")


def timestamp():
    pacific = timezone('US/Pacific')
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.astimezone(pacific).strftime("%Y-%m-%d %I:%M %p %Z")


def all_stats():
    standings = baseball.current_standings(LEAGUE, DIVISION)
    past, future = baseball.giants_schedule()
    template = Template(open('templates/all_stats.md').read())
    return template.render(standings=standings, past=past, future=future,
                           timestamp=timestamp())


def update_standings(current_description):
    stats = all_stats()
    return re.sub(r'\[\]\(/all_statsstart\).*\[\]\(/all_statsend\)',
                  '[](/all_statsstart)\n' + stats + '\n[](/all_statsend)',
                  current_description, flags=re.S)


def update_sidebar(r):
    about = r.settings(SUBREDDIT)

    payload = {
        'description': update_standings(about['description']),
        'link_type': 'any',
        'sr': about['subreddit_id'],
        'title': about['title'],
        'type': about['subreddit_type'],
        'wikimode': about['wikimode'],
    }

    return r.admin(SUBREDDIT, payload)


def thread_open(gametime, now):
    return abs((gametime - now).total_seconds()) <= 14400


def update_game_thread(r):
    gametime, espn_id = baseball.next_game()

    if not thread_open(gametime - datetime.datetime.utcnow()):
        return

    pass


def update_post_game_thread(r):
    pass


if __name__ == "__main__":
    # Setup logging
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    logger.info('Starting bot')

    assert "VOGELTRON_USERNAME" in os.environ, "VOGELTRON_USERNAME required"
    assert "VOGELTRON_PASSWORD" in os.environ, "VOGELTRON_PASSWORD required"

    r = reddit.Client(os.environ["VOGELTRON_USERNAME"],
                      os.environ["VOGELTRON_PASSWORD"])

    update_sidebar(r)
    update_game_thread(r)
    update_post_game_thread(r)

    logger.info('Stopping bot')
