import piecash
from moneyed import Money, GBP
from builtins import NotImplementedError


class Book:
    """Adapter for the entire account GnuCash book.
    """
    # The character used to separate account names when specifying the full account name
    ACCOUNT_NAME_SEPARATOR = ':'

    def __init__(self, filename):
        self._load_from_file(filename)

    def _load_from_file(self, filename):
        """Opens and initializes the Gnucash file.
        """
        self._piecash_book = piecash.open_book(filename, readonly=False)

    def get_accounts(self, account_names):
        """Args:
            account_names: list of account names, e.g. 'Equity:Opening Balances'
        Returns:
            Account object.
        """
        accounts = []
        for name in account_names:
            accounts.append(self.get_account(name))
        return accounts

    def get_account(self, name):
        """Gets an Account by colon-separated name.
        Args:
            name: the name of the account, e.g. 'Equity:Opening Balances'
        Returns:
            Account object.
        """
        piecash_account = self._get_piecash_account_from_name(name)
        return Account(piecash_account)

    def _get_piecash_account_from_name(self, name):
        """Args:
            name: the name of the account, e.g. 'Equity:Opening Balances'
        Returns:
            piecash.Account object.
        """
        parts = name.split(self.ACCOUNT_NAME_SEPARATOR)
        # Walk down the accounts, getting from the previous parent
        piecash_account = self._piecash_book.root_account
        for part in parts:
            piecash_account = self._piecash_book.get(piecash.Account,
                                                     name=part,
                                                     parent=piecash_account)
        return piecash_account

    def get_splits_from_accounts(self, accounts):
        """Gets any splits that are assigned to any of the supplied list of accounts.

        Args:
            accounts: List of Account objects.

        Returns:
            List of Split objects.
        """
        splits = []
        for account in accounts:
            splits.extend(account.splits)
        return splits


class Account:
    def __init__(self, piecash_account):
        self._piecash_account = piecash_account

    @property
    def splits(self):
        """Gets any splits that are assigned to the supplied account.

        Returns:
            List of Split objects.
        """
        splits = []
        for piecash_split in self._piecash_account.splits:
            split = Split(piecash_split)
            splits.append(split)
        return splits

    @property
    def name(self):
        """Returns:
            The full name of the account.
        """
        return self._piecash_account.fullname

    def __str__(self):
        return self.name


class OppositeAccountNotDetermined(Exception):
    """A single opposite account could not be determined, as might
    be the case when more than two splits are grouped together into a single entry.
    """
    pass


class Split:
    """Each Split is linked to an Account and gives the increase/decrease to the account.
    """
    def __init__(self, piecash_split):
        self._piecash_split = piecash_split

    @property
    def date(self):
        return self._piecash_split.transaction.post_date

    @property
    def description(self):
        return self._piecash_split.transaction.description

    @property
    def amount(self):
        # TODO - check currency
        return Money(self._piecash_split.value, GBP)

    def get_opposite_account(self):
        """Returns:
            The Account that is the corresponding credit/debit of this one.
        Raises:
            OppositeAccountNotDetermined - not all splits will have a single opposite account.
        """
        raise NotImplementedError

    def update_account(self, account):
        """Saves the split with the new account.
        Args:
            account: Account object.
        """
        # TODO - should not use a private property
        self._piecash_split.account = account._piecash_account
        self._piecash_split.book.save()
