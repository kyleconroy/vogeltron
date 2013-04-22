**NL East Standings**

|        | W | L | PCT | GB | STRK |
| :---: |:---: | :---: | :---: | :---: | :---: |
{% for t in standings -%}
| [](/{{ t.team_abbr }}{% if t.team_abbr in ['NYM', 'WAS', 'ATL']%}1{%endif%}) | {{ t.wins }} | {{ t.losses }} | {{ t.record }} | {{ t.back }} | {{ t.streak }} |
{% endfor %}
Last Updated @ {{ timestamp }}
