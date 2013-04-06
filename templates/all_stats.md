##Standings
------------

| Team | W | L | W/L% | GB |
| ------ | ------ | ----- | ----- | ----- |
{% for t in standings -%}
| {{ t.name }} | {{ t.wins }} | {{ t.losses }} | {{ t.ratio }} | {% if t.games_back < 0.5 %}--{%else%} {{ t.games_back }}{% endif %} |
{% endfor %}
Last Updated @ {{ timestamp }}
