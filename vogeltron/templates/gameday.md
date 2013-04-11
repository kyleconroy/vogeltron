| {{ home.name}} ({{ home.record }}) | {{ away.name }} ({{ away.record }}) |
| ------ | ------ |
{% if home.pitcher and away.pitcher %}| *{{ home.pitcher.name }}*: {{ home.pitcher.record }} {{ '%0.2f' % home.pitcher.era }} ERA | *{{ away.pitcher.name }}*: {{ away.pitcher.record }} {{ '%0.2f' % away.pitcher.era }} ERA |{% endif %}
| *{{ home.name}} Lineup* | *{{ away.name }} Lineup* |
{% for player1, player2 in players -%}
| {{ player1.name }} {{ player1.position }} | {{ player2.name }} {{ player2.position }} |
{% endfor %}
| UPVOTE FOR VISIBILITY/PRAISE HIM |

Last Updated @ {{ timestamp }}
