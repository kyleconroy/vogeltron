| {{ home.name}} ({{ home.record }}) | {{ away.name }} ({{ away.record }}) |
| ------ | ------ |{% if home.pitcher and away.pitcher %}
| {{ home.pitcher }} | {{ away.pitcher }} |{% endif %}
| **{{ home.name}} Lineup** | **{{ away.name }} Lineup** |
{% for player1, player2 in players -%}
| {{ player1.name }} {{ player1.position }} | {{ player2.name }} {{ player2.position }} |
{% endfor %}
| {{ weather }} |
| ------ |

| UPVOTE FOR VISIBILITY/PRAISE HIM |
| ------ |

Last Updated @ {{ timestamp }}
