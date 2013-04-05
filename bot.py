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

SUBREDDIT = os.environ.get("SUBREDDIT", "SFGiants")
LEAGUE = os.environ.get("MLB_LEAGUE", "NL")
DIVISION = os.environ.get("MLB_DIVISION", "WEST")


if __name__ == "__main__":
    logging.info('Starting bot')

    assert "REDDIT_USERNAME" in os.environ, "REDDIT_USERNAME envvar required"
    assert "REDDIT_PASSWORD" in os.environ, "REDDIT_PASSWORD envvar required"

    # Initiate a reddit session
    r = reddit.Client(os.environ["REDDIT_USERNAME"],
                      os.environ["REDDIT_PASSWORD"],
                      SUBREDDIT)

    logging.info('Stopping bot')
