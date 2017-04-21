from unittest import TestCase
from unittest.mock import Mock, patch, call, sentinel
import sys
from moneyed import Money, GBP
from datetime import date
from gnucashcategorizer.commandhandler import CommandHandler, CommandOptions


class TestCommandOptions(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.options = CommandOptions(config_filename=sentinel.config_filename,
                                     book_filename=sentinel.book_filename)

    def test_get_config(self):
        with patch('gnucashcategorizer.commandhandler.Config', return_value=sentinel.config) as mock_config_cls:
            assert self.options.get_config() == sentinel.config
            mock_config_cls.assert_called_once_with(filename=sentinel.config_filename)

    def test_get_book(self):
        with patch('gnucashcategorizer.commandhandler.Book', return_value=sentinel.book) as mock_book_cls:
            assert self.options.get_book() == sentinel.book
            mock_book_cls.assert_called_once_with(filename=sentinel.book_filename)


class TestCommandHandler(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.command_handler = CommandHandler()

    def test_run_user_accepts(self):
        with patch.object(self.command_handler, '_parse_options_from_command_line') as mock_parse:
            with patch.object(self.command_handler, '_get_and_preview_suggestions') as mock_preview:
                with patch.object(self.command_handler, '_user_accepts_suggestions', return_value=True):
                    with patch.object(self.command_handler, '_save_suggestions') as mock_save:
                        with patch.object(self.command_handler, '_print_message'):
                            mock_parse.return_value = sentinel.options
                            mock_preview.return_value = sentinel.suggestions

                            self.command_handler.run()

                            mock_preview.assert_called_once_with(sentinel.options)
                            mock_save.assert_called_once_with(sentinel.suggestions)

    def test_run_user_does_not_accept(self):
        # TODO make this test and the one above more DRY.
        with patch.object(self.command_handler, '_parse_options_from_command_line') as mock_parse:
            with patch.object(self.command_handler, '_get_and_preview_suggestions') as mock_preview:
                with patch.object(self.command_handler, '_user_accepts_suggestions', return_value=False):
                    with patch.object(self.command_handler, '_save_suggestions') as mock_save:
                        with patch.object(self.command_handler, '_print_message') as mock_print:
                            mock_parse.return_value = sentinel.options
                            mock_preview.return_value = sentinel.suggestions

                            self.command_handler.run()

                            mock_preview.assert_called_once_with(sentinel.options)
                            assert not mock_save.called
                            mock_print.assert_called_once_with('Aborted.',
                                                               self.command_handler.MESSAGE_WARNING)

    def test_parse_options_from_command_line(self):
        CONFIG_FILENAME = 'path/to/config.yaml'
        BOOK_FILENAME = 'path/to/foo_book_filename.gnucash'
        # Spoof passing command line arguments in
        sys.argv.extend([CONFIG_FILENAME, BOOK_FILENAME])

        with patch('gnucashcategorizer.commandhandler.CommandOptions',
                   return_value=sentinel.options) as mock_options_cls:
            options = self.command_handler._parse_options_from_command_line()

            assert options == sentinel.options
            mock_options_cls.assert_called_once_with(config_filename=CONFIG_FILENAME,
                                                     book_filename=BOOK_FILENAME)

    def test_get_suggestions(self):
        suggester = Mock()
        with patch.object(self.command_handler, '_get_suggester', return_value=suggester) as mock_get_suggester:
            suggestions = self.command_handler._get_suggestions(sentinel.options)

            assert suggestions == suggester.get_suggestions()
            mock_get_suggester.assert_called_once_with(sentinel.options)

    def test_get_and_preview_suggestions(self):
        with patch.object(self.command_handler, '_get_suggestions',
                          return_value=sentinel.suggestions) as mock_get_suggestions:
            with patch.object(self.command_handler, '_render_suggestions') as mock_render_suggestions:
                suggestions = self.command_handler._get_and_preview_suggestions(sentinel.options)

        assert suggestions == sentinel.suggestions
        mock_get_suggestions.assert_called_once_with(sentinel.options)
        mock_render_suggestions.assert_called_once_with(sentinel.suggestions)

    def test_render_suggestions(self):
        suggestions = [
            Mock(date=date(2017, 3, 19),
                 description='CASH 19 MAR',
                 amount=Money(30, GBP),
                 new_account='Expenses:Groceries'),
            Mock(date=date(2017, 3, 21),
                 description='Monthly Salary',
                 amount=Money(1500, GBP),
                 new_account='Income:Salary'),
        ]
        with patch.object(self.command_handler, '_print_message') as mock_print:
            with patch.object(self.command_handler, '_format_cells') as mock_format_cells:
                mock_format_cells.side_effect = [
                    sentinel.table_headings_string,
                    sentinel.table_data_string_1,
                    sentinel.table_data_string_2,
                ]
                with patch.object(self.command_handler, '_print_horizontal_line') as mock_print_hr:
                    self.command_handler._render_suggestions(suggestions)

        mock_format_cells.assert_has_calls([
            call(['Date', 'Description', 'Amount', 'Account']),
            call(['19/03/2017', 'CASH 19 MAR', '£30.00', 'Expenses:Groceries']),
            call(['21/03/2017', 'Monthly Salary', '£1,500.00', 'Income:Salary']),
        ])
        mock_print_hr.assert_called_once_with(cell_count=4)
        mock_print.assert_has_calls([
            call('\nSuggestions for uncategorized transactions:\n'),
            call(sentinel.table_headings_string),
            call(sentinel.table_data_string_1),
            call(sentinel.table_data_string_2),
        ])

    def test_format_cells(self):
        assert False

    def test_print_horizontal_line(self):
        assert False

    def test_save_suggestions(self):
        suggestions = [
            Mock(),
            Mock(),
        ]
        with patch.object(self.command_handler, '_print_message') as mock_print:
            self.command_handler._save_suggestions(suggestions)

            suggestions[0].save.assert_called_once_with()
            suggestions[1].save.assert_called_once_with()
            mock_print.assert_called_once_with('Saved.',
                                               self.command_handler.MESSAGE_SUCCESS)

    def test_get_suggester(self):
        options = Mock()

        with patch('gnucashcategorizer.commandhandler.Suggester') as mock_suggester_cls:
            suggester = self.command_handler._get_suggester(options)

        assert suggester == mock_suggester_cls.return_value
        mock_suggester_cls.assert_called_once_with(config=options.get_config(), book=options.get_book())

    def test_user_accepts_suggestions_returns_true_when_they_enter_yes(self):
        YES = 'y'
        with patch('builtins.input', side_effect=YES) as mock_input:
            result = self.command_handler._user_accepts_suggestions()

            mock_input.assert_called_once_with('Save these suggestions to the accounts file? (y/n): ')
            assert result is True

    def test_user_accepts_suggestions_returns_false_when_they_enter_no(self):
        NO = 'n'
        with patch('builtins.input', side_effect=NO) as mock_input:
            result = self.command_handler._user_accepts_suggestions()

            mock_input.assert_called_once_with('Save these suggestions to the accounts file? (y/n): ')
            assert result is False

    def test_user_clarifies_input_when_they_enter_invalid_answer(self):
        INVALID = 'f'
        YES = 'y'
        with patch('builtins.input', side_effect=[INVALID, YES]) as mock_input:
            with patch.object(self.command_handler, '_print_message') as mock_print:
                result = self.command_handler._user_accepts_suggestions()

                mock_input.assert_has_calls([
                    call('Save these suggestions to the accounts file? (y/n): '),
                    call('Save these suggestions to the accounts file? (y/n): '),
                ])
                mock_print.assert_called_once_with('Please enter y or n.',
                                                   self.command_handler.MESSAGE_WARNING)
                assert result is True

    def assert_print_message_is_colored(self, style=None, expected_color=None):
        """Given a message style, assert that _print_message applies the correct colour.
        Args:
            style: A message style, e.g. CommandHandler.MESSAGE_SUCCESS.  If None
                   is supplied, _print_message will be called with no style argument.
            expected_color: A string, the expected color to be applied, e.g. 'green'.
                            If None is supplied, no color is expected.
        """
        kwargs = dict(style=style) if style else dict()
        
        with patch('gnucashcategorizer.commandhandler.cprint') as mock_cprint:
            with patch('gnucashcategorizer.commandhandler.colored') as mock_colored:
                self.command_handler._print_message('Foo.', **kwargs)
                
        if expected_color:
            mock_colored.assert_called_once_with('Foo.', expected_color)
            mock_cprint.assert_called_once_with(mock_colored.return_value)
        else:
            mock_cprint.assert_called_once_with('Foo.')
        
        
    def test_print_message_default(self):
        self.assert_print_message_is_colored(style=None, expected_color=None)
    
    def test_print_message_info(self):
        self.assert_print_message_is_colored(style=self.command_handler.MESSAGE_INFO,
                                             expected_color=None)

    def test_print_message_success(self):
        self.assert_print_message_is_colored(style=self.command_handler.MESSAGE_SUCCESS,
                                             expected_color='green')

    def test_print_message_warning(self):
        self.assert_print_message_is_colored(style=self.command_handler.MESSAGE_WARNING,
                                             expected_color='yellow')

    def test_print_message_error(self):
        self.assert_print_message_is_colored(style=self.command_handler.MESSAGE_ERROR,
                                             expected_color='red')
