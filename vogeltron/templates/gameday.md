| {{ home.name}} ({{ home.record }}) | {{ away.name }} ({{ away.record }}) |
| ------ | ------ |
| {{ home.name}} Lineup | {{ away.name }} Lineup |
{% for player1, player2 in players -%}
| {{ player1.name }} {{ player1.position }} | {{ player2.name }} {{ player2.position }} |
{% endfor %}
| UPVOTE FOR VISIBILITY/PRAISE HIM |

Last Updated @ {{ timestamp }}
