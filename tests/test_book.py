from unittest import TestCase
from unittest.mock import Mock, patch, sentinel, call
from gnucashcategorizer.book import Book, Split, Account
import piecash


class TestAccount(TestCase):
    def test_splits(self):
        piecash_account = Mock(splits=[sentinel.piecash_split_1, sentinel.piecash_split_2])
        splits = [sentinel.split_1, sentinel.split_2]
        account = Account(piecash_account=piecash_account)
        with patch('gnucashcategorizer.book.Split', side_effect=splits) as mock_account_cls:
            assert account.splits == splits

        mock_account_cls.assert_has_calls([
            call(sentinel.piecash_split_1),
            call(sentinel.piecash_split_2),
        ])


class TestSplit(TestCase):
    def test_init(self):
        split = Split(piecash_split=sentinel.piecash_split)
        assert split._piecash_split == sentinel.piecash_split

    def test_description(self):
        piecash_split = Mock()
        split = Split(piecash_split=piecash_split)
        assert split.description == piecash_split.transaction.description

    def test_date(self):
        piecash_split = Mock()
        split = Split(piecash_split=piecash_split)
        assert split.date == piecash_split.transaction.date

    def test_amount(self):
        piecash_split = Mock()
        split = Split(piecash_split=piecash_split)
        assert split.amount == piecash_split.amount

    def test_update_account(self):
        piecash_split = Mock()
        new_account = Mock()
        split = Split(piecash_split=piecash_split)

        split.update_account(new_account)

        assert split._piecash_split.account == new_account._piecash_account
        # TODO - this may not be correct
        split._piecash_split.book.save.assert_called_once_with()


class TestBook(TestCase):
    def test_init(self):
        with patch('gnucashcategorizer.book.piecash.open_book', return_value=sentinel.piecash_book) as mock_open:
            book = Book(filename=sentinel.filename)

        assert book._piecash_book == sentinel.piecash_book
        mock_open.assert_called_once_with(sentinel.filename, readonly=False)

    def test_get_account(self):
        with patch.object(Book, '_load_from_file'):
            book = Book(filename='baz')

        with patch.object(Book, '_get_piecash_account_from_name',
                          return_value=sentinel.piecash_account) as mock_get_piecash:
            with patch('gnucashcategorizer.book.Account', return_value=sentinel.account) as mock_account_cls:
                result = book._get_account(sentinel.name)

        assert result == sentinel.account
        mock_get_piecash.assert_called_once_with(sentinel.name)
        mock_account_cls.assert_called_once_with(sentinel.piecash_account)

    def test_get_piecash_account_from_name(self):
        name = 'Foo:Bar:Foo Bar:Baz'

        with patch.object(Book, '_load_from_file'):
            book = Book(filename='baz')

        piecash_book = Mock()
        piecash_book.get.side_effect = [
            sentinel.account_1,
            sentinel.account_2,
            sentinel.account_3,
            sentinel.account_4,
        ]
        book._piecash_book = piecash_book

        result = book._get_piecash_account_from_name(name)

        assert result == sentinel.account_4
        piecash_book.get.assert_has_calls([
            call(piecash.Account, name='Foo', parent=piecash_book.root_account),
            call(piecash.Account, name='Bar', parent=sentinel.account_1),
            call(piecash.Account, name='Foo Bar', parent=sentinel.account_2),
            call(piecash.Account, name='Baz', parent=sentinel.account_3),
        ])

    def test_get_accounts(self):
        with patch.object(Book, '_load_from_file'):
            book = Book(filename='baz')
        account_names = [sentinel.account_name1, sentinel.account_name2]
        accounts = [sentinel.account1, sentinel.account2]

        with patch.object(Book, '_get_account', side_effect=accounts) as mock_get_account:
            result = book.get_accounts(account_names)

        assert result == accounts
        mock_get_account.assert_has_calls([
            call(sentinel.account_name1),
            call(sentinel.account_name2),
        ])

    def test_get_splits_from_accounts(self):
        account_1 = Mock(splits=[sentinel.split_1])
        account_2 = Mock(splits=[sentinel.split_2, sentinel.split_3])
        accounts = [account_1, account_2]
        with patch.object(Book, '_load_from_file'):
            book = Book(filename='baz')

        result = book.get_splits_from_accounts(accounts)

        assert result == [
            sentinel.split_1,
            sentinel.split_2,
            sentinel.split_3,
        ]
