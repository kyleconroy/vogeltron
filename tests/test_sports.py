import mock
import baseball
from nose.tools import assert_equals


@mock.patch('requests.get')
def test_standings(_get):
    _get().content = open('tests/fixtures/standings.html').read()
    standings = baseball.current_standings('NATIONAL', 'WEST')
    assert_equals(standings, [
        baseball.Standing('San Francisco', 3, 1, .75, 0.0),
        baseball.Standing('Colorado', 3, 1, .75, 0.0),
        baseball.Standing('Arizona', 2, 1, .667, 0.5),
        baseball.Standing('LA Dodgers', 1, 2, .333, 1.5),
        baseball.Standing('San Diego', 1, 3, .250, 2.0),
    ])
