from vogeltron import filters
from nose.tools import assert_equals


def test_nationals_team_abbr():
    assert_equals(filters.nationals_team_abbr('NYM'), 'NYM1')
    assert_equals(filters.nationals_team_abbr('ATL'), 'ATL1')
    assert_equals(filters.nationals_team_abbr('WSH'), 'WAS1')
    assert_equals(filters.nationals_team_abbr('FOO'), 'FOO')
