# formatter.py

import sys
import os
import textwrap
import re
from datetime import datetime
from typing import Any, Optional, List, Union




class ANSITextWrapper(textwrap.TextWrapper):

    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _strip_ansi(self, text):
        """Remove ANSI escape sequences from text."""
        return self.__class__.ansi_escape.sub('', text)

    def _wrap_chunks(self, chunks):
        """Wrap text while ignoring ANSI escape sequences."""
        lines = []
        line = []
        current_length = 0

        for chunk in chunks:
            # Calculate chunk length without ANSI codes
            chunk_length = len(self._strip_ansi(chunk))
            if current_length + chunk_length <= self.width:
                line.append(chunk)
                current_length += chunk_length
            else:
                # If the line is not empty, add it to lines and reset
                if line:
                    lines.append(''.join(line))
                    line = []
                    current_length = 0
                # Handle long chunks that may exceed the line width
                if chunk_length > self.width:
                    lines.append(chunk)
                else:
                    line.append(chunk)
                    current_length += chunk_length

        # Add any remaining line to lines
        if line:
            lines.append(''.join(line))

        return lines

    def wrap(self, text):
        # Split text into chunks, preserving ANSI sequences
        chunks = self._split_text_preserve_ansi(text)
        return self._wrap_chunks(chunks)

    @staticmethod
    def _split_text_preserve_ansi(text):
        """Split text into chunks, keeping ANSI sequences intact."""
        words = re.split(r'(\s+)', text)  # Split on whitespace but preserve it
        return words

    def fill(self, text):
        return '\n'.join(self.wrap(text))



class Formatter:
    def __init__(self,
                 width: int = 0,
                 precision: Optional[int] = 2,
                 fill_char: str = ' ',
                 alignment: str = 'left',
                 pad_char_left: str = '',
                 pad_char_center: str = ' ',
                 pad_char_right: str = '',
                 tab_size: int = 4,
                 datetime_format: Optional[str] = None,
                 ):

        self.width = width
        self.alignment = alignment
        self.fill_char = fill_char
        self.precision = precision
        self.pad_char_left = pad_char_left
        self.pad_char_center = pad_char_center
        self.pad_char_right = pad_char_right
        self.tab_size = tab_size
        self.datetime_format = datetime_format
        self.styles = {}
        self.buffer = []  # Store formatted strings for later writing
        self.terminal_width = self.get_terminal_width()


    @staticmethod
    def get_terminal_width():
        terminal_size = os.get_terminal_size()
        return terminal_size.columns

    # Setter methods from DynamicFormatter
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

    def set_datetime_format(self, datetime_format):
        """Set the formatting for datetime objects."""
        self.datetime_format = datetime_format

    # Format Numbers
    def format_float(self, number, precision=None):
        """Format a floating-point number with specified decimal places or default precision."""
        if not isinstance(number, (int, float)):
            raise ValueError("Input must be a numeric type")
        precision = precision or self.precision
        return f'{number:.{precision}f}'

    def format_percentage(self, ratio, precision=None):
        """Format a number as a percentage with specified or default precision."""
        precision = precision or self.precision
        return f'{ratio:.{precision}%}'

    def format_scientific(self, number, precision=None, upper=False):
        """Format a number in scientific notation with default precision."""
        precision = precision or self.precision
        return f'{number:.{precision}{("E" if upper else "e")}}'

    @staticmethod
    def format_with_commas(number):
        """Format a number with commas as the thousands separator."""
        return f'{number:,}'

    @staticmethod
    def format_binary(number):
        """Format a number as binary."""
        return f'{number:b}'

    @staticmethod
    def format_octal(number):
        """Format a number as octal."""
        return f'{number:o}'

    @staticmethod
    def format_hex_lower(number):
        """Format a number as hexadecimal (lowercase)."""
        return f'{number:x}'

    @staticmethod
    def format_hex_upper(number):
        """Format a number as hexadecimal (uppercase)."""
        return f'{number:X}'

    @staticmethod
    def show_sign_for_positive(number):
        """Always show the sign for both positive and negative numbers."""
        return f'{number:+}'

    @staticmethod
    def space_for_positive(number):
        """Show a space for positive numbers, minus for negative numbers."""
        return f'{number: }'

    def pad_numbers_with_zeros(self, number, width=None):
        """Pad numbers with leading zeros."""
        width = width or self.width
        return f'{number:0{width}}'

    def dynamic_width_and_precision(self, number, width=None, precision=None):
        """Dynamically set width and precision, using defaults if not provided."""
        width = width or self.width
        precision = precision or self.precision
        return f'{number:{width}.{precision}f}'

    def format_currency(self, amount, precision=None):
        """Format a number as currency with default precision."""
        precision = precision or self.precision
        return f'${amount:,.{precision}f}'


    def format_datetime(self, value: datetime) -> str:
        return value.strftime(self.datetime_format) if self.datetime_format else str(value)


    def _get_alignment(self, align: Optional[str]) -> str:
        """Helper to map alignment string to format specifier."""
        align_map = {
            'left': '<',
            'right': '>',
            'center': '^'
        }
        return align_map.get(align or self.alignment, '<')

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Remove ANSI escape sequences from text."""
        return ANSITextWrapper.ansi_escape.sub('', text)

    def format(self, text, width=None, align: Optional[str] = None, tabs: int = 0, newlines: int = 0, skip_format=False) -> Union[str, bool]:
        """Formats the value based on the options specified in the constructor."""
        width = width or self.width

        # Strip ANSI sequences before checking the width
        visible_text_length = len(self._strip_ansi(text))

        # Check if the formatted text exceeds the width for multiline formatting
        if isinstance(text, str):
            if visible_text_length > width:
                return self.format_multiline(text, width=width, align=align, tabs=tabs, newlines=newlines)
            else:
                if skip_format:
                    return False

        alignment = self._get_alignment(align)
        formatted_value = f'{text:{self.fill_char}{alignment}{width}}'

        if self.pad_char_left:
            formatted_value = self.pad_char_left + formatted_value
        if self.pad_char_right:
            formatted_value += self.pad_char_right

        tabs_str = ' ' * (self.tab_size * tabs)
        new_lines = '\n' * newlines
        return f'{tabs_str}{formatted_value}{new_lines}'

    def format_multiline(self, text, width=None, align='left', tabs=0, newlines=0, break_long_words=False, padding_char=''):
        """
        Formats multi-line text with optional line wrapping, alignment, padding, and indentation.

        Parameters:
        - text (str): The multi-line string to format.
        - width (int, optional): The width for each line. Defaults to self.width or self.terminal_width.
        - align (str, optional): Alignment ('left', 'right', 'center') for the text. Defaults to 'left'.
        - tabs (int, optional): Number of tabs to indent each line. Defaults to 0.
        - newlines (int, optional): Number of newlines between formatted lines. Defaults to 1.
        - break_long_words (bool, optional): Whether to break long words. Defaults to False.
        - padding_char (str, optional): Character to use for padding. Defaults to a space.
        """

        # Set width
        width = width or self.width or self.terminal_width

        # Map alignment string to format specifiers
        align_spec = {'left': '<', 'right': '>', 'center': '^'}.get(align, '<')

        # Apply indentation and line spacing
        tabs_str = ' ' * (self.tab_size * tabs)
        newline_str = '\n' * newlines if newlines > 0 else '\n'

        # Initialize TextWrapper with word-breaking options
        wrapper = ANSITextWrapper(width=width, replace_whitespace=False, drop_whitespace=False, break_long_words=break_long_words, break_on_hyphens=False)

        formatted_lines = []

        # Check if text contains newline characters
        if '\n' not in text:
            # No newline characters, use fill to wrap the entire text as a single paragraph
            wrapped_text = wrapper.fill(text)
            formatted_lines.append(f'{wrapped_text:{padding_char}{align_spec}{width}}')
        else:
            # Newline characters present, process line-by-line
            for line in text.splitlines():
                for wrapped_line in wrapper.wrap(line):
                    formatted_lines.append(f'{wrapped_line:{padding_char}{align_spec}{width}}')

        return f'{tabs_str}{newline_str.join(formatted_lines)}'


    def write(self,
              text: Union[str, List[str]],
              start: str = '',
              end: str = '',
              file: str = None,
              sep: str = "\n",
              spacing: Union[int, List[int]] = 0):
        """
        Writes a string or a list of formatted strings to the terminal or a file.
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
        """
        if isinstance(value, (int, float)):
            if value < 0:
                style = self.styles.get('neg')
                formatted_value = class_instance.apply_style(style, self.format(value))
            elif value > 0:
                style = self.styles.get('pos')
                formatted_value = class_instance.apply_style(style, self.format(value))
            else:
                style = self.styles.get('zero')
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
        """
        if format_spec:
            formatted_value = f'{value:{format_spec}}'
        else:
            formatted_value = str(value)

        self.buffer.append(formatted_value)

    def get_formatted_buffer(self, clear_buffer=True):
        """
        Returns the final formatted line or lines after incremental formatting.
        """
        formatted_line = ''.join(self.buffer)
        if clear_buffer:
            self.buffer.clear()
        return formatted_line

    def format_token_by_token(self, tokens, format_spec=None):
        """
        Formats each token (character, word, or phrase) incrementally and stores it in the buffer.
        """
        for token in tokens:
            self.write_to_buffer(token, format_spec)

    def reset_buffer(self):
        """Clears the formatting buffer."""
        self.buffer.clear()

    # Text alignment and padding methods
    def left_align(self, text, width=None):
        """Left-align the text using the default width or a custom one."""
        width = width or self.width
        return f'{text:<{width}}'

    def right_align(self, text, width=None):
        """Right-align the text using the default width or a custom one."""
        width = width or self.width
        return f'{text:>{width}}'

    def center_align(self, text, width=None):
        """Center-align the text using the default width or a custom one."""
        width = width or self.width
        return f'{text:^{width}}'

    def pad_with_char_left(self, text, width=None, pad_char=None):
        """Pad the text (left-aligned) using a custom or default padding character and width."""
        width = width or self.width
        pad_char = pad_char or self.pad_char_left
        return f'{text:{pad_char}<{width}}'

    def pad_with_char_right(self, text, width=None, pad_char=None):
        """Pad the text (right-aligned) using a custom or default padding character and width."""
        width = width or self.width
        pad_char = pad_char or self.pad_char_right
        return f'{text:{pad_char}>{width}}'

    def pad_with_char_center(self, text, width=None, pad_char=None):
        """Pad the text (center-aligned) using a custom or default padding character and width."""
        width = width or self.width
        pad_char = pad_char or self.pad_char_center
        return f'{text:{pad_char}^{width}}'

    def truncate_string(self, text, length=None):
        """Truncate the string to a specified length or default width."""
        length = length or self.width
        return f'{text:.{length}}'

    # Object formatting methods
    @staticmethod
    def use_str_method(obj):
        """Format using str() of the object."""
        return f'{obj!s}'

    @staticmethod
    def use_repr_method(obj):
        """Format using repr() of the object."""
        return f'{obj!r}'

    @staticmethod
    def use_ascii_method(obj):
        """Format using ascii() of the object."""
        return f'{obj!a}'

    # Dict formatting methods
    def format_dict_as_code(self, dict_name, dictionary, indent=0):
        """
        Format a dictionary to print as it would appear in Python code, including handling nested dictionaries.
        """
        indent_str = "    " * indent  # Adjust indentation based on the depth
        formatted_lines = [f"{indent_str}{dict_name} = {{" if indent == 0 else f"{indent_str}{{"]

        for key, value in dictionary.items():
            if isinstance(value, dict):
                # If the value is a nested dictionary, recursively format it with increased indentation
                formatted_lines.append(f'{indent_str}    "{key}": ' + self.format_dict_as_code("", value, indent + 1))
            else:
                # Otherwise, format the key-value pair normally
                formatted_lines.append(f'{indent_str}    "{key}": "{value}",')

        # Close the dictionary definition
        formatted_lines.append(f"{indent_str}}}")

        # Join all formatted lines into a single string
        return "\n".join(formatted_lines)


    @staticmethod
    def format_dict_with_colors(self, dictionary, key_width=None):
        """
        Format a dictionary, applying ANSI color codes to the keys based on the dictionary's values.
        """
        key_width = key_width or max(len(key) for key in dictionary.keys()) + 2  # Adjust width for padding
        formatted_lines = []

        for key, color_code in dictionary.items():
            reset_code = "\033[0m"
            # Apply the color to the key
            formatted_lines.append(f'{color_code}{key:<{key_width}}{reset_code}=> {color_code}{color_code}{reset_code}')

        # Join all formatted lines into a single string
        return "\n".join(formatted_lines)






