
import os
import sys
import textwrap
from datetime import datetime
from typing import Any, Dict, List, Optional, Union






class DynamicFormatter:
    def __init__(self,
                 width: int = 0,
                 alignment: str = 'left',
                 fill_char: str = ' ',
                 precision: Optional[int] = None,
                 number_format: Optional[str] = None,
                 sign: Optional[str] = None,
                 percent: bool = False,
                 scientific: bool = False,
                 datetime_format: Optional[str] = None,
                 pad_char_left: str = '',
                 pad_char_right: str = '',
                 tab_size: int = 4
                 ):

        self.width = width
        self.terminal_width = os.get_terminal_size().columns
        self.alignment = alignment
        self.fill_char = fill_char
        self.precision = precision
        self.number_format = number_format
        self.sign = sign
        self.percent = percent
        self.scientific = scientific
        self.datetime_format = datetime_format
        self.pad_char_left = pad_char_left
        self.pad_char_right = pad_char_right
        self.tab_size = tab_size
        self.styles = {}
        self.buffer = []  # Store formatted strings for later writing


    def _get_alignment(self, align: Optional[str]) -> str:
        """Helper to map alignment string to format specifier."""
        align_map = {
            'left': '<',
            'right': '>',
            'center': '^'
        }
        return align_map.get(align or self.alignment, '<')


    def format(self, value: Any, align: Optional[str] = None, tabs: int = 0, newlines: int = 0) -> str:
        """Formats the value based on the options specified in the constructor."""
        alignment = self._get_alignment(align)
        format_spec = f'{self.fill_char}{alignment}{self.width}'

        if isinstance(value, float) and self.precision is not None:
            format_spec += f'.{self.precision}f'
        if self.percent:
            format_spec += '%'
        elif self.scientific:
            format_spec += 'e'
        elif self.number_format:
            format_spec += self.number_format

        if self.sign:
            format_spec = f'{self.sign}{format_spec}'

        if isinstance(value, datetime) and self.datetime_format:
            formatted_value = value.strftime(self.datetime_format)
        else:
            formatted_value = f'{value:{format_spec}}'

        if self.pad_char_left:
            formatted_value = self.pad_char_left + formatted_value
        if self.pad_char_right:
            formatted_value += self.pad_char_right

        tabs = ' ' * (self.tab_size * tabs)
        new_lines = '\n' * newlines
        return f'{tabs}{formatted_value}{new_lines}'



    def format_multiline(self, value, width=None, alignment='left', tabs=0, newlines=1, break_long_words=False):
        """
        Formats multi-line text with optional indentation and line wrapping.

        Parameters:
        - value: The multi-line string to format.
        - width: Maximum line width for wrapping.
        - alignment: Alignment of the text ('left', 'right', 'center').
        - newline: If True, adds newlines after each wrapped line.
        - tab: Number of tabs to prepend to each line.
        - break_long_words: If True, break long words to respect width.
        """
        lines = value.splitlines()
        formatted_lines = []

        if not width:
            width = self.width
            if width == 0:
                width = self.terminal_width

        # Initialize TextWrapper with options
        wrapper = textwrap.TextWrapper(width=width, break_long_words=break_long_words)

        for line in lines:
            # Use wrapper to split the line at word boundaries (or break long words if set)
            wrapped_lines = wrapper.wrap(line)

            for wrapped_line in wrapped_lines:
                formatted_lines.append(self.format(wrapped_line, tabs=tabs, newlines=newlines))

        return formatted_lines


    def write(self,
              text: Union[str, List[str]],
              start: str = '',
              end: str = '',
              file: str = None,
              sep: str = "\n",
              spacing: Union[int, List[int]] = 0):
        """
        Writes a string or a list of formatted strings to the terminal or a file.

        Parameters:
        - text: Either a single string or a list of strings to write.
        - start: A string to prepend before the entire list of text.
        - end: A string to append after the entire list of text.
        - file: If provided, writes to the specified file. Otherwise, writes to stdout.
        - spacing: Single, double, triple, or more sep (or a pattern) between items in the list. If an int, applies uniformly;
          if a list, applies the pattern cyclically (e.g., [1, 2, 3] for single, double, triple spacing).
        """

        if sep == '\t':
            sep = ' ' * self.tab_size

        def _write(output):
            if file:
                with open(file, 'a') as f:
                    f.write(output)
            else:
                sys.stdout.write(output)

        # If text is a single string, make it a list for uniform processing
        if isinstance(text, str):
            text = [text]

        # Write the start before the list
        if start:
            _write(start)

        # Determine spacing pattern
        if isinstance(spacing, int):
            spacing_pattern = [spacing]
        elif isinstance(spacing, list):
            spacing_pattern = spacing
        else:
            raise ValueError("Spacing must be an int or a list of ints")

        # Write each item in the list, applying the spacing pattern
        for idx, item in enumerate(text):
            _write(item)

            # Apply spacing after each item, but not after the last one
            if idx < len(text) - 1:
                spaces = sep * spacing_pattern[idx % len(spacing_pattern)]
                _write(spaces)

        # Write the end after the entire list
        if end:
            _write(end)


    def conditional_format(self, value, class_instance):
        """
        Apply conditional formatting based on the value's type or properties.

        Example rules:
        - Negative numbers are displayed in red.
        - Positive numbers are displayed in green.
        - Zero is displayed in blue.
        - Strings longer than the width are truncated.
        """


        if isinstance(value, (int, float)):
            if value < 0:
                style = self.styles.get('neg')
                # Example: red for negative numbers
                #formatted_value = f'\033[31m{self.format(value)}\033[0m'  # ANSI escape code for red text
                formatted_value = class_instance.apply_style(style, self.format(value))
            elif value > 0:
                style = self.styles.get('pos')
                # Example: green for positive numbers
                #formatted_value = f'\033[32m{self.format(value)}\033[0m'  # ANSI escape code for green text
                formatted_value = class_instance.apply_style(style, self.format(value))
            else:
                style = self.styles.get('zero')
                # Example: blue for zero
                #formatted_value = f'\033[34m{self.format(value)}\033[0m'  # ANSI escape code for blue text
                formatted_value = class_instance.apply_style(style, self.format(value))

        elif isinstance(value, str) and len(value) > self.width:
            # Truncate long strings
            formatted_value = f'{value[:self.width]}...'
        else:
            formatted_value = self.format(value)

        return formatted_value

    def write_to_buffer(self, value, format_spec=None):
        """
        Adds a formatted token (space, character, word, etc.) to the buffer.

        Parameters:
        - value: The value (character, word, phrase) to format and add to the buffer.
        - format_spec: A custom format specifier for this particular value (optional).
        """
        if format_spec:
            formatted_value = f'{value:{format_spec}}'
        else:
            formatted_value = str(value)

        self.buffer.append(formatted_value)

    def get_formatted_buffer(self, clear_buffer=True):
        """
        Returns the final formatted line or lines after incremental formatting.

        Parameters:
        - clear_buffer: If True, clears the buffer after returning the formatted result.

        Returns:
        - A string representing the final formatted line.
        """
        formatted_line = ''.join(self.buffer)
        if clear_buffer:
            self.buffer.clear()
        return formatted_line

    def format_token_by_token(self, tokens, format_spec=None):
        """
        Formats each token (character, word, or phrase) incrementally and stores it in the buffer.

        Parameters:
        - tokens: A list of tokens (e.g., characters, words, phrases) to format.
        - format_spec: A custom format specifier for all tokens (optional).
        """
        for token in tokens:
            self.write_to_buffer(token, format_spec)


    def reset_buffer(self):
        """Clears the formatting buffer."""
        self.buffer.clear()


    def set_width(self, width):
        """Set the width dynamically."""
        self.width = width

    def set_alignment(self, alignment):
        """Set alignment dynamically ('left', 'right', 'center')."""
        self.alignment = alignment

    def set_fill_char(self, fill_char):
        """Set fill character dynamically."""
        self.fill_char = fill_char

    def set_pad_char_left(self, pad_char_left):
        """Set left-side padding character."""
        self.pad_char_left = pad_char_left

    def set_pad_char_right(self, pad_char_right):
        """Set right-side padding character."""
        self.pad_char_right = pad_char_right

    def set_tab_size(self, tab_size: int):
        """Set the tab size dynamically."""
        self.tab_size = tab_size

    def set_precision(self, precision):
        """Set the precision for float formatting."""
        self.precision = precision

    def set_number_format(self, number_format):
        """Set the number format (e.g., 'n', 'b', 'o', 'x', etc.)."""
        self.number_format = number_format

    def set_sign(self, sign):
        """Set the sign handling for numbers ('+' or '-')."""
        self.sign = sign

    def set_percent(self, percent):
        """Set whether to format as percentage."""
        self.percent = percent

    def set_scientific(self, scientific):
        """Set whether to format as scientific notation."""
        self.scientific = scientific

    def set_datetime_format(self, datetime_format):
        """Set the formatting for datetime objects."""
        self.datetime_format = datetime_format
































