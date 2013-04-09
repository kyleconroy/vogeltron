import json
import baseball

with open('teams.json', 'w') as f:
    json.dump(baseball.teams(), f)

