import yaml
from fnmatch import fnmatch


class MatchPattern:
    """A pattern of text to match to a transaction's description,
    and the resulting account that the transaction should be pointed to.

    Args:
        pattern: text to match to a description (string).
        account_name: full name of account to point the transaction to (string).
    """
    def __init__(self, pattern, account_name):
        self.pattern = pattern
        self.account_name = account_name

    def is_match(self, description):
        """Returns whether or not a description matches the pattern.

        Args:
            description: a description from a transaction to be tested against the pattern (string).

        Returns:
            Whether the supplied description matches the pattern.
        """
        return fnmatch(description, self.pattern)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        hashable = (self.pattern, self.account_name)
        return hash(hashable)

    def __repr__(self):
        return "{cls}(pattern='{pattern}', account_name='{account_name}')".format(cls=self.__class__.__name__,
                                                                                  pattern=self.pattern,
                                                                                  account_name=self.account_name)

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
        return self._config_dict['uncategorized_accounts']

    def get_patterns(self):
        """
        Returns:
            List of MatchPatterns.
        """
        match_patterns = []
        for match_dict in self._config_dict['matches']:
            assert len(match_dict.keys()) == 1, "Unexpected format."
            account_name = list(match_dict.keys())[0]
            for match in match_dict[account_name]:
                match_pattern = MatchPattern(pattern=match, account_name=account_name)
                match_patterns.append(match_pattern)
        return match_patterns
