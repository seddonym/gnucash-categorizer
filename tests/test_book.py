from unittest import TestCase
from datetime import date
from moneyed import Money, GBP
from gnucashcategorizer.book import Transaction


class TestTransaction(TestCase):
    def test_transaction(self):
        kwargs = dict(
            date=date(2017, 3, 1),
            debit_account='Assets.Foo',
            credit_account='Expenses.Bar',
            description='Foo description',
            amount=Money(531.55, GBP)
        )
        transaction = Transaction(**kwargs)

        for name, value in kwargs.items():
            assert getattr(transaction, name) == value
