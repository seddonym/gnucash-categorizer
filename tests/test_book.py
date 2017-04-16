from unittest import TestCase
from unittest.mock import Mock, patch, sentinel, call
from gnucashcategorizer.book import Book, Split


class TestSplit(TestCase):
    def test_split(self):
        kwargs = dict(
            guid='foo',
        )
        split = Split(**kwargs)

        for name, value in kwargs.items():
            assert getattr(split, name) == value


class TestBook(TestCase):
    def test_get_splits_from_account_names(self):
        with patch.object(Book, '_load_from_file'):
            book = Book(filename='baz')
        account_names = ['Foo', 'Bar']
        account_1 = Mock(splits=[sentinel.split_1])
        account_2 = Mock(splits=[sentinel.split_2, sentinel.split_3])
        accounts = [
            account_1,
            account_2,
        ]
        with patch.object(book, '_get_account', side_effect=accounts) as mock_get_account:
            splits = book.get_splits_from_account_names(account_names)

        mock_get_account.assert_has_calls([
            call('Foo'),
            call('Bar'),
        ])
        assert splits == [
            sentinel.split_1,
            sentinel.split_2,
            sentinel.split_3,
        ]
