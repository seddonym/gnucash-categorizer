from unittest import TestCase
from unittest.mock import Mock, patch, sentinel, call
from gnucashcategorizer.book import Account, Split
from gnucashcategorizer.suggester import Suggester, Suggestion


class TestSuggester(TestCase):
    def test_get_suggestions(self):
        accounts = [
            Mock(splits=[sentinel.split_1]),
            Mock(splits=[sentinel.split_2, sentinel.split_3]),
        ]
        suggestions = [
            sentinel.suggestion_1,
            sentinel.suggestion_2,
            sentinel.suggestion_3,
        ]
        suggester = Suggester(book=Mock(), config=Mock())
        with patch.object(suggester, '_get_uncategorized_accounts', return_value=accounts):
            with patch.object(suggester, '_get_suggestion_for_split',
                              side_effect=suggestions) as mock_get_suggestion:
                result = suggester.get_suggestions()

        assert result == suggestions
        mock_get_suggestion.assert_has_calls([
            call(sentinel.split_1),
            call(sentinel.split_2),
            call(sentinel.split_3),
        ])


class TestSuggestion(TestCase):
    def test_str(self):
        split = Mock()
        split.__str__ = Mock(return_value='foo split')
        account = Mock()
        account.__str__ = Mock(return_value='bar account')

        suggestion = Suggestion(
            split=split,
            new_account=account
        )
        assert repr(suggestion) == "Suggestion(foo split, bar account)"

    def test_suggestions_are_equal_if_same_data(self):
        split = Split(guid='foo')
        account = Account(full_name='bar')
        suggestion_a = Suggestion(
            split=split,
            new_account=account
        )
        suggestion_b = Suggestion(
            split=split,
            new_account=account
        )
        assert suggestion_a == suggestion_b
