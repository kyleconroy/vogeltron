import json
from vogeltron import baseball

with open('vogeltron/teams.json', 'w') as f:
    json.dump(baseball.teams(), f)

