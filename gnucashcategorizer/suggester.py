class NoSuggestion(Exception):
    """Exception raised when no suggestion could be made.
    """
    def __init__(self, split):
        self._split = split


class Suggestion:
    def __init__(self, split, new_account):
        self.split = split
        self.new_account = new_account

    @property
    def date(self):
        return self.split.date

    @property
    def description(self):
        return self.split.description

    @property
    def amount(self):
        return self.split.amount

    def save(self):
        """Saves the suggestion to the Gnucash book.
        """
        self.split.update_account(self.new_account)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        # Hash is useful for establishing two suggestions as being equal with the same data
        hashable = (self.split, self.new_account)
        return hash(hashable)

    def __repr__(self):
        return "{cls}({split}, {new_account})".format(cls=self.__class__.__name__,
                                                      split=self.split,
                                                      new_account=self.new_account)


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
        suggestions = []

        splits = self._get_uncategorized_splits()
        for split in splits:
            suggestions.append(self._get_suggestion_for_split(split))

        return suggestions

    def _get_uncategorized_splits(self):
        """Returns:
            List of all splits from uncategorized accounts.
        """
        accounts = self._get_uncategorized_accounts()
        return self._book.get_splits_from_accounts(accounts)

    def _get_uncategorized_accounts(self):
        account_names = self._config.get_uncategorized_account_names()
        return self._book.get_accounts(account_names)

    def _get_suggestion_for_split(self, split):
        """
        Args:
            split: Split to get a suggestion for.

        Returns:
            Suggestion object.

        Raises:
            NoSuggestion.
        """
        # TODO - this is not very efficient as we keep recalculating the patterns
        # for the same accounts, if there are many splits for the same account (which is likely).
        patterns = self._config.get_patterns_for_account_name(split.account.name)
        for pattern in patterns:
            if pattern.is_match(split.description):
                account = self._book.get_account(pattern.account_name)
                return Suggestion(split, new_account=account)
        raise NoSuggestion(split)
