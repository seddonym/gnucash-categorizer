from unittest import TestCase
from unittest.mock import Mock, patch, call, sentinel
from moneyed import Money, GBP
from datetime import date
from gnucashcategorizer.book import Transaction
from gnucashcategorizer.config import MatchPattern
from gnucashcategorizer.suggester import Suggester, Suggestion


class TestSuggester(TestCase):
    def test_get_suggestions_debit_account(self):
        book = Mock()
        DEBIT_ACCOUNT = 'Assets.Current Account'
        CREDIT_ACCOUNT = 'Expenses.Groceries'
        transaction = Transaction(
            date=date(2017, 3, 1),
            amount=Money(135, GBP),
            description='CASH FROM STORE 1',
            debit_account=DEBIT_ACCOUNT,
            credit_account='Expenses.Uncategorized'
        )
        uncategorized_transactions = [
            transaction,
        ]
        book.get_uncategorized_transactions.return_value = uncategorized_transactions

        config = Mock()
        config.get_patterns_for_account.return_value = [
            MatchPattern('FOO', 'Expenses.Foo'),
            MatchPattern('CASH FROM STORE*', CREDIT_ACCOUNT),
        ]

        suggester = Suggester(book=book,
                              config=config)
        suggestions = suggester.get_suggestions()

        config.get_patterns_for_account.assert_called_once_with(DEBIT_ACCOUNT)
        assert suggestions == [
            Suggestion(
                transaction=transaction,
                credit_account=CREDIT_ACCOUNT)
        ]


class TestSuggestion(TestCase):
    def test_suggestions_are_equal_if_same_data(self):
        transaction = Transaction(
            date=date(2017, 3, 1),
            amount=Money(135, GBP),
            description='Foo',
            debit_account='Bar',
            credit_account='Baz'
        )
        credit_account = 'Foobaz'
        suggestion_a = Suggestion(
            transaction=transaction,
            credit_account=credit_account
        )
        suggestion_b = Suggestion(
            credit_account=credit_account,
            transaction=transaction
        )
        assert suggestion_a == suggestion_b
