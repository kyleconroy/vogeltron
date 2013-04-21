import argparse
import json
import multiprocessing
import os
import requests
import subprocess

REPO_URL = 'https://github.com/kyleconroy/vogeltron.git'

from . import heroku


def app_name(subreddit):
    return 'vogeltron-' + subreddit.lower()


def app_config(section):
    return {
        'VOGELTRON_SUBREDDIT': section['name'],
        'VOGELTRON_USERNAME': section['username'],
        'VOGELTRON_PASSWORD': section['password'],
        'VOGELTRON_TEAM': section['team'],
        'VOGELTRON_SENTRY_DSN': section['raven'],
    }


# 491 cochise
def deploy_bot(section):
    try:
        os.mkdir('repos')
    except OSError:
        pass

    # Heroku
    subreddit = section['name']
    botname = app_name(section['name'])
    client = heroku.Client(section['heroku'])

    if not client.get_app(botname):
        client.create_app(botname)

    new_config = app_config(section)
    current_config = client.get_config(botname)

    if new_config != current_config:
        current_config.update(new_config)
        client.set_config(botname, current_config)

    # Scale the dyno
    client.install_addon(botname, 'scheduler')

    # Config the scheduler

    # Git
    repo = os.path.join('repos', subreddit)

    if not os.path.exists(repo):
        subprocess.check_output(['git', 'clone', REPO_URL, repo], 
                                stderr=subprocess.STDOUT)

    os.chdir(repo)
    
    subprocess.check_output(['git', 'pull', 'origin', 'master'],
                            stderr=subprocess.STDOUT)

    remotes = subprocess.check_output(['git', 'remote', 'show'])

    if 'heroku' not in str(remotes):
        subprocess.check_output(['git', 'remote', 'add', 'heroku',
                                'git@heroku.com:' + botname + '.git'])

    subprocess.check_output(['git', 'push', 'heroku', 'master'])


def main():
    description = 'Deploy the latest version of Vogeltron'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('config', type=argparse.FileType('r'),
                        help='Path to a config file')
    args = parser.parse_args()
    
    config = json.load(args.config)

    for subreddit in config['subreddits']:
        subreddit['heroku'] = config['heroku']
        subreddit['raven'] = config['raven']

    p = multiprocessing.Pool(5)
    p.map(deploy_bot, config['subreddits'])


if __name__ == "__main__":
    main()
