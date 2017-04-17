from unittest import TestCase
from unittest.mock import Mock, patch, sentinel, call
from gnucashcategorizer.suggester import Suggester, Suggestion, NoSuggestion


class TestSuggester(TestCase):
    def test_get_suggestions(self):
        splits = [
            sentinel.split_1, sentinel.split_2, sentinel.split_3
        ]
        suggestions = [
            sentinel.suggestion_1,
            sentinel.suggestion_2,
            sentinel.suggestion_3,
        ]
        suggester = Suggester(book=Mock(), config=Mock())
        with patch.object(suggester, '_get_uncategorized_splits', return_value=splits):
            with patch.object(suggester, '_get_suggestion_for_split',
                              side_effect=suggestions) as mock_get_suggestion:
                result = suggester.get_suggestions()

        assert result == suggestions
        mock_get_suggestion.assert_has_calls([
            call(sentinel.split_1),
            call(sentinel.split_2),
            call(sentinel.split_3),
        ])

    def test_get_uncategorized_splits(self):
        book = Mock()
        book.get_splits_from_accounts.return_value = sentinel.splits
        suggester = Suggester(book=book, config=Mock())

        with patch.object(suggester, '_get_uncategorized_accounts', return_value=sentinel.accounts):
            result = suggester._get_uncategorized_splits()

        assert result == sentinel.splits
        book.get_splits_from_accounts.assert_called_once_with(sentinel.accounts)

    def test_get_uncategorized_accounts(self):
        book = Mock()
        book.get_accounts.return_value = sentinel.accounts
        config = Mock()
        config.get_uncategorized_account_names.return_value = ['Foo', 'Bar']
        suggester = Suggester(book=book, config=config)

        result = suggester._get_uncategorized_accounts()
        assert result == sentinel.accounts

    def test_get_suggestion_for_split_second_pattern_matches(self):
        config = Mock()
        pattern_1 = Mock()
        pattern_1.is_match.return_value = False
        pattern_2 = Mock()
        pattern_2.is_match.return_value = True
        config.get_patterns.return_value = [pattern_1, pattern_2]
        split = Mock()

        suggester = Suggester(book=Mock(), config=config)
        result = suggester._get_suggestion_for_split(split)

        assert result == Suggestion(split, new_account=pattern_2.account)
        pattern_2.is_match.assert_called_once_with(split.description)

    def test_get_suggestion_for_split_raises_no_suggestion_found_if_no_match(self):
        config = Mock()
        pattern_1 = Mock()
        pattern_1.is_match.return_value = False
        pattern_2 = Mock()
        pattern_2.is_match.return_value = False
        config.get_patterns.return_value = [pattern_1, pattern_2]

        suggester = Suggester(book=Mock(), config=config)
        try:
            suggester._get_suggestion_for_split(Mock())
        except NoSuggestion:
            assert True
        else:
            assert False

    def test_save(self):
        split = Mock()
        new_account = Mock()
        suggestion = Suggestion(split=split, new_account=new_account)

        suggestion.save()

        split.update_account.assert_called_once_with(new_account)


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
        split = Mock()
        account = Mock()
        suggestion_a = Suggestion(
            split=split,
            new_account=account
        )
        suggestion_b = Suggestion(
            split=split,
            new_account=account
        )
        assert suggestion_a == suggestion_b

    def test_date(self):
        suggestion = Suggestion(split=Mock(date=sentinel.date),
                                new_account=Mock())
        assert suggestion.date == sentinel.date

    def test_description(self):
        suggestion = Suggestion(split=Mock(description=sentinel.description),
                                new_account=Mock())
        assert suggestion.description == sentinel.description

    def test_amount(self):
        suggestion = Suggestion(split=Mock(amount=sentinel.amount),
                                new_account=Mock())
        assert suggestion.amount == sentinel.amount
