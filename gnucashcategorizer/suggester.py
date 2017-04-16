from datetime import date
from moneyed import Money, GBP
from .book import Transaction


class Suggestion:
    def __init__(self, transaction, debit_account=None, credit_account=None):
        self.transaction = transaction
        self.debit_account = debit_account
        self.credit_account = credit_account

    @property
    def date(self):
        return self.transaction.date

    @property
    def description(self):
        return self.transaction.description

    @property
    def amount(self):
        return self.transaction.amount

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        # Hash is useful for establishing two suggestions as being equal with the same data
        hashable = (self.transaction, self.debit_account, self.credit_account)
        return hash(hashable)

    def __repr__(self):
        return "{cls}({transaction}, credit_account='{credit_account}')".format(
                                                                cls=self.__class__.__name__,
                                                                transaction=self.transaction,
                                                                credit_account=self.credit_account)

class Suggester:
    """Provides a list of Suggestions for unmatched transactions.

    Args:
        config: Config object.
        book: Book object.
    """
    def __init__(self, config, book):
        self._config = config
        self._book = book

    def get_suggestions(self):
        """Gets a list of suggestions to apply to the book.

        Returns:

            A list of Suggestion objects.
        """
        transactions = self._book.get_uncategorized_transactions()
        suggestions = []

        for transaction in transactions:
            patterns = self._config.get_patterns_for_account(transaction.debit_account)
            for pattern in patterns:
                if pattern.is_match(transaction.description):
                    suggestion = Suggestion(
                        transaction=transaction,
                        credit_account=pattern.account
                    )
                    suggestions.append(suggestion)
                    break
        return suggestions

