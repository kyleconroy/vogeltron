##Standings
##Last 5
##Next 5 Games
------------

| Team | W | L | W/L% | GB |
| ------ | ------ | ----- | ----- | ----- |
{% for t in standings -%}
| {{ t.name }} | {{ t.wins }} | {{ t.losses }} | {{ ('%.3f' % t.ratio).lstrip('0') }} | {% if t.games_back < 0.5 %}--{%else%} {{ t.games_back }}{% endif %} |
{% endfor %}
| Date | vs. | W/L | Score |
| ------ | ------ | ----- | ----- |
{% for g in past -%}
| {{ g.pretty_date }} | {{ g.opponent }} | {{ g.w }} | {{ g.score }} |
{% endfor %}
| Date | Time | Opponent |
| ------ | ------ | ----- |
{% for g in future -%}
| {{ g.pretty_date }} | {{ g.pretty_time }} | {{ g.description }} |
{% endfor %}
Last Updated @ {{ timestamp }}
