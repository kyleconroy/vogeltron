**NL East Standings**

|        | W | L | PCT | GB | STRK |
| :---: |:---: | :---: | :---: | :---: | :---: |
{% for t in standings -%}
| [](/{{ t.team_abbr }}) | {{ t.wins }} | {{ t.losses }} | {{ t.record }} | {{ t.back }} | {{ t.streak }} |
{% endfor %}