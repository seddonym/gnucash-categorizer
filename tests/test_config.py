from unittest import TestCase
from unittest.mock import sentinel, patch
import os
from gnucashcategorizer.config import MatchPattern, Config


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

    def test_match_patterns_are_equal_if_same_data(self):
        account = 'Foo'
        pattern = 'BAR *'
        match_pattern_a = MatchPattern(pattern, account)
        match_pattern_b = MatchPattern(pattern, account)
        assert match_pattern_a == match_pattern_b

    def test_str(self):
        match_pattern = MatchPattern(pattern='BAZ *', account='Foo:Bar')
        assert str(match_pattern) == "MatchPattern(pattern='BAZ *', account='Foo:Bar')"


class TestConfig(TestCase):
    def test_init(self):
        with patch.object(Config, '_load_from_file') as mock_load:
            Config(sentinel.filename)

            mock_load.assert_called_once_with(sentinel.filename)

    def test_load_from_file(self):
        # Not a unit test this one, actually loads the config from a sample file
        filename = os.path.join(os.path.dirname(__file__), 'sample_config.yaml')
        config = Config(filename)
        assert config._config_dict == {
            'unresolved_accounts': [
                'Imbalance-GBP',
                'Assets:Current Assets:Checking Account:Unresolved',
            ],
            'matches': [
                {'Expenses:Groceries': ['CASH *', 'STORE ?']},
                {'Income:Salary': ['MYEMPLOYER']}
            ],
        }

    def test_get_unresolved_account_names(self):
        with patch.object(Config, '_load_from_file'):
            config = Config(sentinel.filename)
            config._config_dict = {
                'unresolved_accounts': sentinel.account_names,
            }
            assert config.get_unresolved_account_names() == sentinel.account_names

    def test_get_patterns(self):
        with patch.object(Config, '_load_from_file'):
            config = Config(sentinel.filename)
            config._config_dict = {
                'matches': [
                    {'Foo:Bar': ['FOOBAZ', 'FOOBAR ?']},
                    {'Baz': ['baz baz *']}
                ],
            }
            expected_patterns = [
                MatchPattern(pattern='FOOBAZ', account='Foo:Bar'),
                MatchPattern(pattern='FOOBAR ?', account='Foo:Bar'),
                MatchPattern(pattern='baz baz *', account='Baz'),
            ]

            assert config.get_patterns() == expected_patterns
