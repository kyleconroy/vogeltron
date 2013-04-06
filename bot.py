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

SUBREDDIT = os.environ.get("SUBREDDIT", "SFGiants")
LEAGUE = os.environ.get("MLB_LEAGUE", "NATIONAL")
DIVISION = os.environ.get("MLB_DIVISION", "WEST")


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


def update_sidebar():
    r = reddit.Client(os.environ["REDDIT_USERNAME"],
                      os.environ["REDDIT_PASSWORD"])

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


if __name__ == "__main__":
    logger.info('Starting bot')

    assert "REDDIT_USERNAME" in os.environ, "REDDIT_USERNAME required"
    assert "REDDIT_PASSWORD" in os.environ, "REDDIT_PASSWORD required"

    update_sidebar()

    logger.info('Stopping bot')
