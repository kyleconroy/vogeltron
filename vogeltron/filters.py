def nationals_team_abbr(value):
    if value == 'WSH':
        return 'WAS1'
    if value == 'ATL' or value == 'NYM':
        return value + '1'
    return value
