import piecash
from _datetime import date
from IPython.core.release import description
from sqlalchemy.orm.persistence import save_obj


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
            accounts.append(self._get_account(name))
        return accounts

    def _get_account(self, fullname):
        """Gets an Account by colon-separated fullname.
        Args:
            fullname: the name of the account, e.g. 'Equity:Opening Balances'
        Returns:
            Account object.
        """
        # TODO rename fullname to name
        piecash_account = self._get_piecash_account_from_name(fullname)
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
        for piecash_split in self._piecash_accounts.splits:
            split = Split(piecash_split)
            splits.append(split)
        return splits


class Split:
    """Each Split is linked to an Account and gives the increase/decrease to the account.
    """
    def __init__(self, piecash_split):
        self._piecash_split = piecash_split

    @property
    def date(self):
        return self._piecash_split.transaction.date

    @property
    def description(self):
        return self._piecash_split.transaction.description

    @property
    def amount(self):
        return self._piecash_split.amount

    def update_account(self, account):
        """Saves the split with the new account.
        Args:
            account: Account object.
        """
        raise NotImplemented
