##Standings
##Last 5
##Next 5 Games
------------

| Team | W | L | W/L% | GB |
| ------ | ------ | ----- | ----- | ----- |
{% for t in standings -%}
| {{ t.name }} | {{ t.wins }} | {{ t.losses }} | {{ t.ratio }} | {% if t.games_back < 0.5 %}--{%else%} {{ t.games_back }}{% endif %} |
{% endfor %}
| Date | vs. | W/L | Score |
| ------ | ------ | ----- | 
{% for g in previous -%}
| {{ g.datetime }} | {{ g.opponent }} | {{ g.win }} | {{ g.score }} |
{% endfor %}
| Date | Time | Opponent |    
| ------ | ------ | ----- | 
{% for g in future -%}
| {{ g.datetime }} | {{ g.datetime }} | {{ t.opponent }} |
{% endfor %}
Last Updated @ {{ timestamp }}
