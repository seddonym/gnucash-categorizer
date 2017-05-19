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
        uncategorized_account_names = []
        for match_dict in self._config_dict['matches']:
            uncategorized_account_names.append(self._get_only_key_from_dictionary(match_dict))
        return uncategorized_account_names

    @classmethod
    def _get_only_key_from_dictionary(cls, dictionary):
        """
        Args:
            A dictionary with one entry.
        Returns:
            The key of the entry.
        Raises:
            ValueError if the dictionary does not have exactly one entry.
        """
        number_of_keys = len(dictionary.keys())
        if number_of_keys != 1:
            raise ValueError('_get_only_key_from_dictionary received a dictionary '
                             'with {} keys.'.format(number_of_keys))
        return tuple(dictionary)[0]

    def get_patterns_for_account_name(self, account_name):
        """
        Args:
           account_name - Name of the imbalance account for which to get patterns.
        Returns:
            List of MatchPatterns.
        """
        match_patterns = []
        matches_config = self._get_matches_config_for_account_name(account_name)
        for match_config in matches_config:
            new_account_name = self._get_only_key_from_dictionary(match_config)
            for pattern_text in match_config[new_account_name]:
                match_pattern = MatchPattern(pattern=pattern_text, account_name=new_account_name)
                match_patterns.append(match_pattern)
        return match_patterns

    def _get_matches_config_for_account_name(self, account_name):
        """Args:
            account_name - Name of the imbalance account for which to get the config
                           relating to that particular account.
            Returns:
                List of dictionaries, each in the form, or empty list if none could be found.
                    {'Destination account': ['PATTERN ONE', 'PATTERN TWO']}
        """
        for account_dict in self._config_dict['matches']:
            config_account_name = self._get_only_key_from_dictionary(account_dict)
            if account_name == config_account_name:
                return account_dict[account_name]
        return []
