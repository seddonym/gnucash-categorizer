from argparse import ArgumentParser
from moneyed import GBP
from moneyed.localization import (format_money, _format as set_money_format,
                                  _sign as set_currency_sign)
from .config import Config
from .book import Book
from gnucashcategorizer.suggester import Suggester
from decimal import ROUND_HALF_UP
from termcolor import colored, cprint


set_money_format('en_GB', group_size=3, group_separator=",", decimal_point=".",
                 positive_sign="", trailing_positive_sign="",
                 negative_sign="-", trailing_negative_sign="",
                 rounding_method=ROUND_HALF_UP)
set_currency_sign('en_GB', GBP, prefix='£')


class CommandOptions:
    """The options supplied by the user for running the categorizer.

    Args:
        config_filename: The filename and path to the config yaml file (string).
        book_filename: The filename and path to the Gnucash accounts file (string).
    """
    def __init__(self, config_filename, book_filename):
        self._config_filename = config_filename
        self._book_filename = book_filename

    def get_config(self):
        """Gets the Config object from the config filename.

        Returns:
            Config object.
        """
        return Config(filename=self._config_filename)

    def get_book(self):
        """Gets the Book object from the book filename.

        Returns:
            Book object.
        """
        return Book(filename=self._book_filename)


class CommandHandler:
    """Handles the user flow and display.

    Usage:

        CommandHandler().run()
    """
    MESSAGE_INFO = 'IN'
    MESSAGE_SUCCESS = 'SU'
    MESSAGE_WARNING = 'WA'
    MESSAGE_ERROR = 'ER'

    MESSAGE_STYLE_MAP = {
        MESSAGE_SUCCESS: 'green',
        MESSAGE_WARNING: 'yellow',
        MESSAGE_ERROR: 'red',
    }
    COLUMN_WIDTH = 35

    def run(self):
        """Main runner for the program.
        """
        options = self._parse_options_from_command_line()
        suggestions = self._get_and_preview_suggestions(options)
        if self._user_accepts_suggestions():
            self._save_suggestions(suggestions)
        else:
            self._print_message('Aborted.', self.MESSAGE_WARNING)

    def _parse_options_from_command_line(self):
        """Gets the config and book filenames from the command line.

        Returns:
            CommandOptions instance.
        """
        parser = ArgumentParser()
        parser.add_argument(
            "config",
            help="The name of the .yml file that contains the matching configuration.")
        parser.add_argument(
            "accounts",
            help="The name of the GnuCash file that contains the accounts.")

        args = parser.parse_args()

        return CommandOptions(config_filename=args.config, book_filename=args.accounts)

    def _get_and_preview_suggestions(self, options):
        """Gets and previews the suggested changes to make to the transactions.

        Args:
            options: CommandOptions object.

        Returns:
            suggestions: List of Suggestions.
        """
        suggestions = self._get_suggestions(options)
        self._render_suggestions(suggestions)
        return suggestions

    def _get_suggestions(self, options):
        """Gets the suggested changes to make to the transactions.

        Args:
            options: CommandOptions object.

        Returns:
            List of Suggestions.
        """
        return self._get_suggester(options).get_suggestions()

    def _get_suggester(self, options):
        """Gets a Suggester object to use to get the suggestions.

        Args:
            options: CommandOptions object.

        Returns:
            Suggester object.
        """
        return Suggester(config=options.get_config(),
                         book=options.get_book())

    def _render_suggestions(self, suggestions):
        """Outputs the suggestions for the user to review.

        Args:
            suggestions: List of suggestions.
        """
        self._print_message('\nSuggestions for uncategorized transactions:\n')
        headings = ['Date', 'Description', 'Amount', 'Old account', 'New account']
        self._print_message(self._format_cells(headings))
        self._print_horizontal_line(cell_count=len(headings))
        for suggestion in suggestions:
            parts = [str(part) for part in (
                suggestion.date.strftime('%d/%m/%Y'),
                suggestion.description,
                format_money(suggestion.amount, locale='en_GB'),
                suggestion.old_account,
                suggestion.new_account,
            )]
            self._print_message(self._format_cells(parts))

    def _format_cells(self, cells):
        """Args:
            A list of strings.
        Returns:
            A string with the strings evenly spaced into columns.
        """
        cell_format = '{: <%d}' % self.COLUMN_WIDTH
        format_string = ' '.join([cell_format * len(cells)])
        return format_string.format(*cells)

    def _print_horizontal_line(self, cell_count):
        """Prints a horizontal line to span the number of cells provided.
        Args:
            How many cells.
        """
        LINE_CHARACTER = '-'
        self._print_message(LINE_CHARACTER * self.COLUMN_WIDTH * cell_count)

    def _save_suggestions(self, suggestions):
        """Saves the list of suggestions to the accounts book.

        Args:
            suggestions: List of suggestions.
        """
        for suggestion in suggestions:
            suggestion.save()
        self._print_message('Saved.', self.MESSAGE_SUCCESS)

    def _user_accepts_suggestions(self):
        """Asks the user whether or not they accept the suggestions.

        Returns:
            Whether they accept the suggestions (boolean).
        """
        YES, NO = 'y', 'n'
        print()
        while True:
            user_input = input('Save these suggestions to the accounts file? (y/n): ').lower()
            if user_input in [YES, NO]:
                break
            else:
                self._print_message('Please enter {} or {}.'.format(YES, NO),
                                    self.MESSAGE_WARNING)

        return user_input == YES

    def _print_message(self, message, style=MESSAGE_INFO):
        """Outputs the given message to the user.

        Args:
            message: Message to output (string).
            style: MESSAGE_INFO, MESSAGE_SUCCESS,
                   MESSAGE_WARNING or MESSAGE_ERROR.
        """

        try:
            color = self.MESSAGE_STYLE_MAP[style]
            cmessage = colored(message, color)
        except KeyError:
            cmessage = message
        cprint(cmessage)
