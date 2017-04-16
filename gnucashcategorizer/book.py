import piecash


class Account:
    def __init__(self, full_name):
        self.full_name = full_name


class Split:
    """Each Split is linked to an Account and gives the increase/decrease to the account.
    """
    def __init__(self, guid):
        self.guid = guid


class Transaction:
    """Represents movement of money between accounts.
     The transaction is modelled through a set of Splits (2 or more).
     The sum of the splits should be balanced for a single transaction.
    """
    def __init__(self, date, description, amount, splits):
        self.date = date
        self.description = description
        self.amount = amount
        self.splits = splits


class Book:
    """The entire account GnuCash book.
    """
    def __init__(self, filename):
        self._load_from_file(filename)

    def _load_from_file(self, filename):
        """Opens and initializes the Gnucash file.
        """
        self._piecash_book = piecash.open_book(filename, readonly=False)

    def get_accounts(self, account_names):
        for name in account_names:
            return self._get_account(name)

    def _get_account(self, fullname):
        """Gets an Account by colon-separated fullname.
        Args:
            fullname: the name of the account, e.g. 'Equity:Opening Balances'
        Returns:
            piecash.Account object.
        """
        ACCOUNT_SEPERATOR = ':'
        parts = fullname.split(ACCOUNT_SEPERATOR)
        # Walk down the accounts, getting from the previous parent
        account = self._piecash_book.root_account
        for part in parts:
            account = self._piecash_book.get(piecash.Account, name=part, parent=account)
        return account

    def get_splits_from_account_names(self, account_names):
        """Gets any splits that are assigned to any of the supplied list of account names.
        """
        splits = []
        for account_name in account_names:
            account = self._get_account(account_name)
            splits.extend(account.splits)
        return splits
