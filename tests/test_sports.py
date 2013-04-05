import mock
import baseball
from nose.tools import assert_equals


@mock.patch('requests.get')
def test_standings(_get):
    _get().content = open('tests/fixtures/summary.shtml').read()
    standings = baseball.current_standings('NL', 'WEST')
    assert_equals(standings, [
        baseball.Standing('Arizona Diamondbacks', 'ARI', 2, 1, .667, 0.0),
        baseball.Standing('Colorado Rockies', 'COL', 2, 1, .667, 0.0),
        baseball.Standing('San Francisco Giants', 'SFG', 2, 1, .667, 0.0),
        baseball.Standing('Los Angeles Dodgers', 'LAD', 1, 2, .333, 1.0),
        baseball.Standing('San Diego Padres', 'SDP', 1, 2, .333, 1.0),
    ])
