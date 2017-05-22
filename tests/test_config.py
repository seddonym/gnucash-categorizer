from unittest import TestCase
from unittest.mock import sentinel, patch
import os
from gnucashcategorizer.config import MatchPattern, Config


class TestMatchPattern(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.match_pattern = MatchPattern(pattern='CASH * FOO', account_name='foo')

    def test_is_match_returns_true_if_exact(self):
        assert self.match_pattern.is_match('CASH * FOO')

    def test_is_match_returns_true_with_wildcard(self):
        assert self.match_pattern.is_match('CASH store FOO')

    def test_is_match_is_case_sensitive(self):
        assert not self.match_pattern.is_match('cash store FOO')

    def test_is_match_returns_false_if_not_match(self):
        assert not self.match_pattern.is_match('CASH something')

    def test_match_patterns_are_equal_if_same_data(self):
        account_name = 'Foo:Bar'
        pattern = 'BAR *'
        match_pattern_a = MatchPattern(pattern, account_name)
        match_pattern_b = MatchPattern(pattern, account_name)
        assert match_pattern_a == match_pattern_b

    def test_str(self):
        match_pattern = MatchPattern(pattern='BAZ *', account_name='Foo:Bar')
        assert str(match_pattern) == "MatchPattern(pattern='BAZ *', account_name='Foo:Bar')"


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
            'matches': [
                {'Assets:Current Assets:Checking Account:Uncategorized': [
                    {'Expenses:Groceries': ['CASH *', 'STORE ?']},
                    {'Income:Salary': ['MYEMPLOYER']},
                ]},
                {'Imbalance-GBP': [
                    {'Expenses:Social': ['CASH *']},
                ]}
            ],
        }

    def test_get_uncategorized_account_names(self):
        with patch.object(Config, '_load_from_file'):
            config = Config(sentinel.filename)
            config._config_dict = {
                'matches': [
                    {sentinel.foo_account: []},
                    {sentinel.bar_account: []}
                ],
            }
            assert config.get_uncategorized_account_names() == [sentinel.foo_account, sentinel.bar_account]

    def assert_get_patterns_for_account_name_returns_patterns(self, account_name, matches, patterns):
        with patch.object(Config, '_load_from_file'):
            config = Config(sentinel.filename)
            config._config_dict = {
                'matches': matches,
            }

        assert config.get_patterns_for_account_name(account_name) == patterns

    def test_get_patterns_for_account_name(self):
        matches = [
            {'Another Account': [
                {'Foo:Bar': ['WRONG']},
            ]},
            {'Imbalance Account': [
                {'Foo:Bar': ['FOOBAZ', 'FOOBAR ?']},
                {'Baz': ['baz baz *']}
            ]},
        ]
        expected_patterns = [
            MatchPattern(pattern='FOOBAZ', account_name='Foo:Bar'),
            MatchPattern(pattern='FOOBAR ?', account_name='Foo:Bar'),
            MatchPattern(pattern='baz baz *', account_name='Baz'),
        ]
        self.assert_get_patterns_for_account_name_returns_patterns('Imbalance Account', matches, expected_patterns)

    def test_get_patterns_for_account_name_returns_empty_list_for_account_not_in_config(self):
        matches = [
            {'Another Account': [
                {'Foo:Bar': ['WRONG']},
            ]},
            {'Imbalance Account': [
                {'Foo:Bar': ['FOOBAZ', 'FOOBAR ?']},
                {'Baz': ['baz baz *']}
            ]},
        ]
        self.assert_get_patterns_for_account_name_returns_patterns('Unlisted account', matches, [])

    def assert_get_only_key_from_dictionary_raises_value_error(self, dictionary):
        try:
            Config._get_only_key_from_dictionary(dictionary)
        except ValueError as e:
            assert str(e) == '_get_only_key_from_dictionary received a ' \
                'dictionary with {} keys.'.format(len(dictionary))
        else:
            assert False, '_get_only_key_from_dictionary did not raise ValueError.'

    def test_get_only_key_from_empty_dictionary(self):
        self.assert_get_only_key_from_dictionary_raises_value_error({})

    def test_get_only_key_from_dictionary_with_multiple_keys(self):
        self.assert_get_only_key_from_dictionary_raises_value_error({'foo': 1, 'bar': 2, 'baz': 3})

    def test_get_only_key_from_dictionary_with_one_key(self):
        result = Config._get_only_key_from_dictionary({'foo': 1})
        assert result == 'foo'
