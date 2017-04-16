from unittest import TestCase
from gnucashcategorizer.config import MatchPattern


# Use a real file for the config
# CONFIG_FILENAME = os.path.join(
#    os.path.dirname(__file__), 'files', 'config.yaml'
# )

class TestMatchPattern(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.match_pattern = MatchPattern(pattern='CASH * FOO', account='Bar')

    def test_is_match_returns_true_if_exact(self):
        assert self.match_pattern.is_match('CASH * FOO')

    def test_is_match_returns_true_with_wildcard(self):
        assert self.match_pattern.is_match('CASH store FOO')

    def test_is_match_is_case_sensitive(self):
        assert not self.match_pattern.is_match('cash store FOO')

    def test_is_match_returns_false_if_not_match(self):
        assert not self.match_pattern.is_match('CASH something')
