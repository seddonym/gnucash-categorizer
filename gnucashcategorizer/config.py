import yaml
from fnmatch import fnmatch


class MatchPattern:
    """A pattern of text to match to a transaction's description,
    and the resulting account that the transaction should be pointed to.

    Args:
        pattern: text to match to a description (string).
        account: account to point the transaction to (string).
    """
    def __init__(self, pattern, account):
        self.pattern = pattern
        self.account = account

    def is_match(self, description):
        """Returns whether or not a description matches the pattern.

        Args:
            description: a description from a transaction to be tested against the pattern (string).

        Returns:
            Whether the supplied description matches the pattern.
        """
        return fnmatch(description, self.pattern)


class Config:
    """Reads and stores configuration from a YAML file.
    """
    def __init__(self, filename):
        self._load_from_file(filename)

    def _load_from_file(self, filename):
        """Parses the supplied yaml filename.
        """
        with open(filename) as config_file:
            yaml_string = config_file.read()
            self._config_dict = yaml.load(yaml_string)

    def get_uncategorized_account_names(self):
        """
        Returns:
            List of account names (strings).
        """
        return []
