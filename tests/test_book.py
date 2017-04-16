from unittest import TestCase
from gnucashcategorizer.book import Split


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
        assert False
