from unittest import TestCase
from unittest.mock import Mock, patch, sentinel, call
from gnucashcategorizer.book import Book, Split


class TestAccount(TestCase):
    def test_splits(self):
        assert False


class TestSplit(TestCase):
    def test_split(self):
        kwargs = dict(
            guid='foo',
        )
        split = Split(**kwargs)

        for name, value in kwargs.items():
            assert getattr(split, name) == value

    def test_description(self):
        assert False


class TestBook(TestCase):
    def test_get_account(self):
        assert False

    def test_get_accounts(self):
        assert False

    def test_get_splits_from_accounts(self):
        splits_chunks = [
            [sentinel.split_1],
            [sentinel.split_2, sentinel.split_3],
        ]
        accounts = [sentinel.account_1, sentinel.account_2]
        with patch.object(Book, '_load_from_file'):
            book = Book(filename='baz')

        with patch.object(book, '_get_splits_from_account', side_effect=splits_chunks) as mock_get_splits:
            result = book.get_splits_from_accounts(accounts)

        mock_get_splits.assert_has_calls([
            call(sentinel.account_1),
            call(sentinel.account_2),
        ])
        assert result == [
            sentinel.split_1,
            sentinel.split_2,
            sentinel.split_3,
        ]
