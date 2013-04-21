## Standings
| Team | W | L | W/L% | GB |
| ------ | ------ | ----- | ----- | ----- |
{% for t in standings -%}
| {{ t.name }} | {{ t.wins }} | {{ t.losses }} | {{ t.record }} | {{ t.back }} |
{% endfor %}
## Last 5 Games
| Date | vs. | W/L | Score |
| ------ | ------ | ----- | ----- |
{% for g in past -%}
| {{ g.pretty_date }} | {{ g.opponent }} | {{ g.w }} | {{ g.score }} |
{% endfor %}
## Upcoming Games
| Date | Time | Opponent |
| ------ | ------ | ----- |
{% for g in future -%}
| {{ g.pretty_date }} | {{ g.pretty_time }} | {{ g.description }} |
{% endfor %}
Last Updated @ {{ timestamp }}
