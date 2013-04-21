import json

from . import baseball

if __name__ == "__main__":
    with open('vogeltron/teams.json', 'w') as f:
        json.dump(baseball.teams(), f)
