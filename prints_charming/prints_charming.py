# prints_charming.py

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import sys
import traceback
import re



def get_all_subclass_names(cls, trailing_char=None):
    subclasses = set(cls.__subclasses__())
    result = {subclass.__name__ + (trailing_char or '') for subclass in subclasses}
    for subclass in subclasses.copy():
        result.update(get_all_subclass_names(subclass, trailing_char))
    return result


@dataclass
class TextStyle:

    """
    A class to manage text styles including color, background color, and various text effects.
    """

    color: Optional[str] = 'default'
    bg_color: Optional[str] = None
    bold: bool = False
    italic: bool = False
    underlined: bool = False
    overlined: bool = False
    strikethrough: bool = False
    reversed: bool = False
    blink: bool = False
    conceal: bool = False

    def update(self, attributes):
        for attr, value in attributes.items():
            if hasattr(self, attr):
                setattr(self, attr, value)


class ColorPrinter:
    
    """
    This module provides a ColorPrinter class for handling colored text printing tasks.
    It also includes TextStyle, a dataclass for managing text styles. In the COLOR_MAP "v" before a color stands for "vibrant".

    Note: This module is developed and tested on Linux and is intended for use in Linux terminals.

    """
    
    CONFIG: Dict[str, bool] = {
        "color_text"          : True,
        "args_to_strings"     : True,
        "style_names"         : True,
        "style_words_by_index": True,
        "kwargs"              : False,
        "conceal"             : True,
        "width"               : 80,
    }

    COLOR_MAP: Dict[str, str] = {
        "default" : "\033[0m",
        "white"   : "\033[97m",
        "black"   : "\033[30m",
        "green"   : "\033[32m",
        "vgreen"  : "\033[38;5;46m",
        "red"     : "\033[31m",
        "vred"    : "\033[38;5;196m",
        "blue"    : "\033[34m",
        "vblue"   : "\033[38;5;21m",
        "yellow"  : "\033[33m",
        "vyellow" : "\033[38;5;226m",
        "magenta" : "\033[35m",
        "vmagenta": "\033[38;5;201m",
        "cyan"    : "\033[36m",
        "vcyan"   : "\033[38;5;51m",
        "orange"  : "\033[38;5;208m",
        "gray"    : "\033[38;5;252m",
        "pink"    : "\033[38;5;200m",
        "purple"  : "\033[38;5;129m",
    }

    EFFECT_MAP: Dict[str, str] = {
        "bold"         : "\033[1m",
        "italic"       : "\033[3m",
        "underlined"   : "\033[4m",
        "overlined"    : "\033[53m",
        "strikethrough": "\033[9m",
        "blink"        : "\033[5m",
        "conceal"      : "\033[8m",
        "reversed"     : "\033[7m",
    }

    STYLES: Dict[str, TextStyle] = {
        "default"      : TextStyle(),
        "green"        : TextStyle(color="green", underlined=True),
        "vgreen"       : TextStyle(color="vgreen"),
        "red"          : TextStyle(color="red"),
        "vred"         : TextStyle(color="vred", bold=True),
        "blue"         : TextStyle(color="blue"),
        "yellow"       : TextStyle(color="yellow"),
        "vyellow"      : TextStyle(color="vyellow"),
        "magenta"      : TextStyle(color="magenta", bold=True),
        "vmagenta"     : TextStyle(color="vmagenta"),
        "pink"         : TextStyle(color="pink"),
        "purple"       : TextStyle(color="purple"),
        "cyan"         : TextStyle(color="cyan"),
        "vcyan"        : TextStyle(color="vcyan"),
        "orange"       : TextStyle(color="orange"),
        "gray"         : TextStyle(color="gray"),
        "header_text"  : TextStyle(color="white", bg_color="purple", bold=True),
        "header_symbol": TextStyle(color="magenta", bold=True, overlined=True, strikethrough=True),
        "task"         : TextStyle(color="blue", bold=True),
        "conceal"      : TextStyle(conceal=True),
    }


    def __init__(
            self,
            config: Dict[str, Union[bool, str, int]] = None,
            color_map: Dict[str, str] = None,
            bg_color_map: Dict[str, str] = None,
            effect_map: Dict[str, str] = None,
            styles: Dict[str, TextStyle] = None,
            reset_color: str = None,
            colorprinter_variables: Dict[str, List[str]] = None
    ) -> None:

        """
        Initialize the ColorPrinter with args to any of these optional parameters.

        :param config: enable or disable various functionalities of this class. Default is the ColorPrinter.CONFIG dictionary above
        :param color_map: supply your own color_map dictionary. Default is the ColorPrinter.COLOR_MAP dictionary above
        :param bg_color_map: supply your own bg_color_map dictionary. Default is computed from color_map dictionary
        :param effect_map: supply your own effect_map dictionary. Default is the ColorPrinter.EFFECT_MAP dictionary above
        :param styles: supply your own styles dictionary. Default is the ColorPrinter.STYLES dictionary above
        :param reset_color: supply your own from the color_map dictionary. Default is 'default' from the color_map dictionary
        :param colorprinter_variables: calls the add_variables_from_dict method with your provided dictionary. See README for more info.
        """

        if not config:
            config = ColorPrinter.CONFIG
        self.config = config

        if not color_map:
            color_map = ColorPrinter.COLOR_MAP
        self.color_map = color_map

        if not bg_color_map:
            bg_color_map = {
                color: self.compute_bg_color_map(code) for color, code in self.color_map.items()
            }
        self.bg_color_map = bg_color_map

        if not effect_map:
            effect_map = ColorPrinter.EFFECT_MAP
        self.effect_map = effect_map

        if not styles:
            styles = ColorPrinter.STYLES
        self.styles = styles

        self.style_codes: Dict[str, str] = {
            name: self.create_style_code(style) for name, style in self.styles.items() if self.styles[name].color in self.color_map
        }

        #  Set the printer reset code to the default value in self.color_map or user supplied value
        if not reset_color:
            reset_color = self.color_map['default']
        self.reset = reset_color

        self.variable_map: Dict[str, str] = {}
        self.word_map: Dict[str, Dict[str, str]] = {}
        self.phrase_map: Dict[str, Dict[str, str]] = {}
        self.conceal_map: Dict[str, Dict[str, str]] = {}

        if colorprinter_variables:
            self.add_variables_from_dict(colorprinter_variables)



    def compute_bg_color_map(self, code):
        if '[38' in code:
            bg_code = code.replace('[38', '[48')  # Change to background color for 256-color codes
        elif '[9' in code:
            bg_code = code.replace('[9', '[10')  # Special handling for white, which starts with 9
        else:
            bg_code = code.replace('[3', '[4')  # Basic ANSI colors: convert foreground color to background color

        return bg_code

    def print_bg(self, color_name: str, length: int = 10) -> None:
        """
        Prints a "block" of background color.

        :param color_name: The name of the color as per self.color_map.
        :param length: The length of the color block in terms of spaces.
        :raises ColorNotFoundError: If the background color is not found in the background color map.
        :raises InvalidLengthError: If the length is not valid.
        """

        if length <= 0:
            message = f"Invalid length '{length}'. Length must be positive."
            styled_message = self.apply_style('vred', message)
            raise InvalidLengthError(styled_message, self, self.apply_style)

        bg_color_code = self.bg_color_map.get(color_name)
        if not bg_color_code:
            message = f"Key '{color_name}' not found in the 'self.bg_color_map' dictionary."
            styled_message = self.apply_style('vred', message)
            raise ColorNotFoundError(styled_message, self, self.apply_style, format_specific_exception=True)

        # Print the color block
        print(f"{bg_color_code}{' ' * length}{self.reset}")



    def create_style_code(self, style: Union[TextStyle, Dict[str, Any]]):
        style_codes = []

        if isinstance(style, TextStyle):
            # Add foreground color
            if style.color and style.color in self.color_map:
                style_codes.append(self.color_map[style.color])

            # Add background color if provided
            if style.bg_color and style.bg_color in self.bg_color_map:
                style_codes.append(self.bg_color_map[style.bg_color])

            # Loop through other attributes
            for attr, ansi_code in self.effect_map.items():
                if getattr(style, attr, False):
                    style_codes.append(ansi_code)

        elif isinstance(style, Dict):
            # Add foreground color
            if "color" in style and style["color"] in self.color_map:
                style_codes.append(self.color_map[style["color"]])

            # Add background color if provided
            if "bg_color" in style and style["bg_color"] in self.bg_color_map:
                style_codes.append(self.bg_color_map[style["bg_color"]])

            # Loop through other effects
            for effect, ansi_code in self.effect_map.items():
                if effect in style and style[effect]:
                    style_codes.append(ansi_code)

        return "".join(style_codes)

    def add_style(self, name: str, style: TextStyle):
        self.styles[name] = style
        if self.styles[name].color in self.color_map:
            style_code = self.create_style_code(self.styles[name])
            self.style_codes[name] = style_code

    def get_style_code(self, style_name):
        return self.style_codes.get(style_name, self.style_codes['default'])

    def apply_style(self, style_name, text):

        style_code = self.style_codes[style_name]

        # Append the style code at the beginning of the text and the reset code at the end
        styled_text = f"{style_code}{text}{self.reset}"

        return "".join(styled_text)


    def add_variable(self, variable: str, style_name: str) -> None:

        """
        Adds a variable with a specific style.
    
        :param variable: The variable to be styled.
        :param style_name: The name of the style to apply.
        """

        variable = str(variable)
        if style_name in self.styles:
            styled_string = f"{self.style_codes[style_name]}{variable}{self.reset}"
            if style_name == 'conceal':
                self.conceal_map[variable] = {
                    "style": style_name,
                    "styled": styled_string
                }
            contains_inner_space = ' ' in variable.strip()
            if contains_inner_space:
                self.phrase_map[variable] = {
                    "style" : style_name,
                    "styled": styled_string
                }
            else:
                self.word_map[variable] = {
                    "style" : style_name,
                    "styled": styled_string
                }
        else:
            print(f"Style {style_name} not found in styles dictionary.")

    def add_variables(self, variables: List[str], style_name: str) -> None:
        if style_name in self.styles:
            style_code = self.style_codes[style_name]
            for variable in variables:
                self.add_variable(variable, style_name)

    def add_variables_from_dict(self, style_variables_dict: Dict[str, List[str]]) -> None:
        for style_name, variables in style_variables_dict.items():
            if style_name in self.styles:
                self.add_variables(variables, style_name)
            else:
                print(f"Style {style_name} not found in styles dictionary.")

    def remove_variable(self, variable: str) -> None:
        if variable in self.word_map:
            del self.word_map[variable]
        if variable in self.phrase_map:
            del self.phrase_map[variable]
        elif variable in self.conceal_map[variable]:
            del self.conceal_map[variable]


    def conceal_text(self, text_to_conceal, replace=False):
        if replace:
            style_code = self.style_codes['vyellow']
            concealed_text = f"{style_code}***concealed_api_key***{self.reset}"
        else:
            style_code = self.style_codes['conceal']
            concealed_text = f"{style_code}{text_to_conceal}{self.reset}"

        return concealed_text


    def print_variables(
            self,
            vars_and_styles: Union[Dict[str, Tuple[Any, str]], Tuple[List[Any], List[str]]],
            text: str,
            text_style: str = None
    ) -> None:

        if isinstance(vars_and_styles, dict):  # Approach 1: Using Dictionary
            for placeholder, (variable, var_style) in vars_and_styles.items():
                styled_var_code = self.style_codes[var_style]
                sub = f"{styled_var_code}{str(variable)}{self.reset}"
                text = text.replace(f"{{{placeholder}}}", sub)

        elif isinstance(vars_and_styles, tuple) and len(vars_and_styles) == 2:  # Approach 2: Using Lists
            variables, styles = vars_and_styles
            for i, (variable, var_style) in enumerate(zip(variables, styles)):
                styled_var_code = self.style_codes[var_style]
                sub = f"{styled_var_code}{str(variable)}{self.reset}"
                text = text.replace(f"var{i + 1}", sub)

        self.print(text, style=text_style)


    def apply_kwargs_placeholders(self, text: str, kwargs: Dict[str, Any]) -> str:
        # Replace placeholders with actual values and apply colors
        for key, value in kwargs.items():
            # colored_value = f"\033[1;{self.color_map[self.variable_map[key]]}{value}\033[0m"
            styled_value = str(value)
            if key in self.variable_map:
                # colored_value = f"\033[1;{self.color_map[self.variable_map[key]]}{str(value)}\033[0m"  # use str() here
                style_name = self.variable_map[key]
                style_code = self.style_codes[style_name]
                styled_value = f"{style_code}{styled_value}{self.reset}"  # colored_value = f"\033[1;{self.color_map[self.variable_map[key]]}{value}\033[0m"
                styled_value_ascii = f"{style_code}{styled_value}{self.reset}"

            text = text.replace(f"{{{key}}}", styled_value)

        return text


    def style_words_by_index(self, text: str, style_mapping: Dict[Union[int, Tuple[int, int]], str]) -> str:
        words = text.split()
        for i, word in enumerate(words, start=1):  # Start indexing from 1
            for key in style_mapping:
                style_name = style_mapping[key]
                style_code = self.style_codes[style_name]
                if isinstance(key, tuple):
                    start, end = key
                    if start <= i <= end and style_name in self.styles:  # Inclusive end
                        words[i - 1] = f"{style_code}{word}{self.reset}"
                elif isinstance(key, int):
                    if key == i and style_name in self.styles:
                        words[i - 1] = f"{style_code}{word}{self.reset}"
        return " ".join(words)


    def print(
            self,
            *args: Any,
            text: str = None,
            var: Any = None,
            tstyle: str = None,
            vstyle: str = None,
            style: Union[None, str, Dict[Union[int, Tuple[int, int]], str]] = None,
            color: str = None,
            bg_color: str = None,
            bold: bool = False,
            italic: bool = False,
            overlined: bool = False,
            underlined: bool = False,
            strikethrough: bool = False,
            reversed: bool = False,
            blink: bool = False,
            conceal: bool = False,
            header: bool = False,
            sep: str = ' ',
            end: str = '\n',
            **kwargs: Any
    ) -> None:

        # Handle variable replacement
        if var is not None:
            variable = str(var)
            var_style_code = self.style_codes[vstyle]
            if text != None:
                text = text.replace('var', f"{var_style_code}{variable}{self.reset}")
                style = tstyle
            else:
                text = f"{var_style_code}{variable}{self.reset}"

        converted_args = [str(arg) for arg in args] if self.config["args_to_strings"] else args

        # If text was modified, it takes precedence
        if text is not None:
            converted_args = [text] + converted_args

        text = sep.join(converted_args)

        if not self.config["color_text"]:
            print(sep.join(args), end=end)

            return

        if self.config["style_words_by_index"] and isinstance(style, dict):
            text = self.style_words_by_index(text, style)

        if self.config["kwargs"] and kwargs:
            text = self.apply_kwargs_placeholders(text, kwargs)
            print(text, end=end)

            return

        if any([color, bg_color, bold, italic, underlined, overlined, strikethrough, reversed, blink, conceal]):

            # Apply the effective style to text which is not already styled
            # Create an empty dict
            effective_style = {}

            updated_style = {k: v for k, v in {
                'color'        : color,
                'bg_color'     : bg_color,
                'bold'         : bold,
                'italic'       : italic,
                'underlined'   : underlined,
                'overlined'    : overlined,
                'strikethrough': strikethrough,
                'reversed'     : reversed,
                'blink'        : blink,
                'conceal'      : conceal
            }.items() if v is not None}

            effective_style.update(updated_style)

            effective_style_code = self.create_style_code(effective_style)

        else:
            if style and isinstance(style, str):
                effective_style_code = self.style_codes[style]
            else:
                effective_style_code = self.style_codes['default']

        # Count leading and trailing spaces
        leading_spaces = len(text) - len(text.lstrip())
        trailing_spaces = len(text) - len(text.rstrip())

        # Convert the text to a list of words and spaces
        words = text.split()

        # Initialize the list to keep track of which indexes are used by phrases and which are not
        indexes_used_by_phrases = set()

        # Initialize list to hold the final styled words
        styled_words = [None] * len(words)

        # Step 1: Handle phrases
        for phrase, details in self.phrase_map.items():
            # Check if the phrase exists in the text
            if phrase in text:
                # Extract the styled phrase
                styled_phrase = details.get('styled', phrase)

                # Split the styled_phrase into words
                styled_phrase_words = styled_phrase.split()

                # Find the starting index of this phrase in the list of words
                for i in range(len(words) - len(styled_phrase_words) + 1):
                    if words[i:i + len(styled_phrase_words)] == phrase.split():
                        # Update the indexes_used_by_phrases set
                        indexes_used_by_phrases.update(list(range(i, i + len(styled_phrase_words))))
                        # Update the styled_words list
                        for j, styled_word in enumerate(styled_phrase_words):
                            styled_words[i + j] = styled_word

        # Step 2: Handle individual words
        for i, word in enumerate(words):
            # Skip the index if it's used by a phrase
            if i in indexes_used_by_phrases:
                continue

            # Check if the word is in the word_map
            if word in self.word_map:
                styled_word = self.word_map.get(word, {}).get('styled', word)
            else:
                styled_word = f"{effective_style_code}{word}{self.reset}"

            # Update the styled_words list
            styled_words[i] = styled_word

        # Step 3: Handle default styling for remaining words
        for i, styled_word in enumerate(styled_words):
            if styled_word is None:
                styled_words[i] = f"{effective_style_code}{words[i]}{self.reset}"

        # Step 4: Join the styled_words to form the final styled text
        styled_text = ' '.join(filter(None, styled_words))

        # Add back the leading and trailing spaces
        styled_text = ' ' * leading_spaces + styled_text + ' ' * trailing_spaces

        print(styled_text, end=end)

        return


    def print_table(
            self,
            table_data: List[List[Any]],
            table_style: str = "default",
            border_style: Optional[str] = None,
            header_style: Optional[str] = None,
            col_alignments: Optional[List[str]] = None,
            column_styles: Optional[Dict[str, str]] = None,
            cell_style: Optional[str] = None
    ) -> None:

        """
        Prints a table with optional styling and alignment.

        :param table_data: A list of lists representing the rows of the table.
        :param col_alignments: A list of strings ('left', 'center', 'right') for column alignments.
        :param cell_style: Style name for the table cells.
        :param header_style: Style name for the header row.
        :param border_style: Style name for the table borders.
        """

        # 1. Automatic Column Sizing
        max_col_lengths = [0] * len(table_data[0])
        for row in table_data:
            for i, cell in enumerate(row):
                cell_length = len(str(cell))
                max_col_lengths[i] = max(max_col_lengths[i], cell_length)

        # 2. Column Alignment
        table_output = []
        for row_idx, row in enumerate(table_data):
            aligned_row = []
            for i, cell in enumerate(row):
                cell_str = str(cell)
                max_length = max_col_lengths[i]

                # Determine the alignment for this cell
                alignment = 'left'  # Default
                if col_alignments and i < len(col_alignments):
                    alignment = col_alignments[i]
                elif isinstance(cell, (int, float)):
                    alignment = 'right'

                # Apply the alignment
                if alignment == 'left':
                    aligned_cell = cell_str.ljust(max_length)
                elif alignment == 'center':
                    aligned_cell = cell_str.center(max_length)
                elif alignment == 'right':
                    aligned_cell = cell_str.rjust(max_length)

                # Apply the style
                if row_idx == 0 and header_style:
                    aligned_cell = self.apply_style(header_style, aligned_cell)
                elif cell_style:
                    aligned_cell = self.apply_style(cell_style, aligned_cell)

                # Add aligned and styled cell to the row
                aligned_row.append(aligned_cell)

            # Create a row string and add to table output
            row_str = " | ".join(aligned_row)
            table_output.append(row_str)

        # 3. Print Borders and Rows
        if border_style:
            border_line = self.apply_style(border_style, "-" * (sum(max_col_lengths) + len(max_col_lengths) * 3 - 1))
            print(border_line)

        for i, row in enumerate(table_output):
            print(row)
            if i == 0 and header_style and border_style:
                print(border_line)

        if border_style:
            print(border_line)


    def ugly_print_map(self, d: Dict, style_name: str, indent: int = 2, is_last_item: bool = True):
        style_code = self.style_codes[style_name]
        value_style = self.style_codes.get('default', self.style_codes['default'])

        print(' ' * indent + '{')

        total_items = len(d)
        current_item = 0

        for key, value in d.items():
            current_item += 1
            indented_key = ' ' * (indent + 4) + style_code + repr(key) +  self.reset
            indented_value = value_style + repr(value) + self.reset

            if isinstance(value, dict):
                print(f"{indented_key}: ", end="")
                self.ugly_print_map(value, style_name, indent + 4, current_item == total_items)
            else:
                separator = "," if current_item < total_items else ""
                sep2 = "\n"
                print(f"{indented_key}{style_code}{value}{self.reset}{separator}{sep2}")

        closing_brace = ' ' * indent + '}'
        if is_last_item:
            print(closing_brace)
        else:
            print(f"{closing_brace},")


class ColorPrinterError(Exception):
    """Base class for exceptions in this module."""

    def __init__(
            self,
            message: str,
            cp: 'ColorPrinter',
            apply_style: Callable[[str, str], str],
            tb_style_name: str = 'default',
            format_specific_exception: bool = False
    ) -> None:

        super().__init__(message)
        self.message = message
        self.cp = cp
        self.apply_style = apply_style
        self.tb_style_name = tb_style_name
        self.format_specific_exception = format_specific_exception

    def __str__(self):
        return self.message

    def format_traceback(self, tb):
        return self.apply_style(self.tb_style_name, tb)

    def print_error(self):
        print(self.message)
        print()

    def stylize_traceback(self, tb_lines):

        styled_lines = []
        file_line_regex = re.compile(r'(File ")(.*?)(/[^/]+)(", line )(\d+)(, )(in )(.*)')
        subclass_names_with_colon = list(get_all_subclass_names(ColorPrinterError, trailing_char=':'))

        for line in tb_lines:
            leading_whitespace = re.match(r"^\s*", line).group()
            if line.startswith("Traceback"):
                styled_line = self.apply_style('header', line)
                styled_lines.append(' ')
                styled_lines.append(styled_line)
                styled_lines.append(' ')
            elif line.strip().startswith("File"):
                match = file_line_regex.search(line)
                if match:
                    section1 = match.group(1) + match.group(2)  # File path excluding last part
                    section2 = match.group(3)  # Last part of the path (filename)
                    section3 = match.group(4)  # ", line "
                    section4 = match.group(5)  # Line number
                    section5 = match.group(6)  # ", "
                    section6 = match.group(7)  # in
                    section7 = match.group(8)  # Function name

                    # Apply styles to each section
                    styled_section1 = self.apply_style('path', section1)
                    styled_section2 = self.apply_style('filename', section2)
                    styled_section3 = self.apply_style('line_info', section3)
                    styled_section4 = self.apply_style('line_number', section4)
                    styled_section5 = self.apply_style('path', section5)
                    styled_section6 = self.apply_style('path', section6)
                    styled_section7 = self.apply_style('function_name', section7)

                    # Combine the styled sections
                    styled_line = f"{styled_section1}{styled_section2}{styled_section3}{styled_section4}{styled_section5}{styled_section6}{styled_section7}"
                    styled_lines.append(f"{leading_whitespace}{styled_line}")
                else:
                    # If regex matching fails, style the whole line as fallback
                    styled_line = self.apply_style('blue', line)
                    styled_lines.append(f"{leading_whitespace}{styled_line}")

            elif line.strip().startswith("raise") or line.strip().startswith("ValueError"):
                styled_line = self.apply_style('red', line)
                styled_lines.append(' ')
                styled_lines.append(styled_line)
                styled_lines.append(' ')

            else:
                for name in subclass_names_with_colon:
                    if name in line:
                        start_index = line.find(name)
                        before_name = line[:start_index]
                        subclass_name = line[start_index:start_index + len(name)]
                        after_name = line[start_index + len(name):]

                        # Apply styles
                        styled_before_name = self.apply_style('gray', before_name)
                        styled_subclass_name = self.apply_style('vyellow', subclass_name)
                        styled_after_name = self.apply_style('default', after_name)

                        # Combine the styled parts
                        styled_line = f"{styled_before_name}{styled_subclass_name}{styled_after_name}"
                        styled_lines.append(' ')
                        styled_lines.append(f"{leading_whitespace}{styled_line}")
                        styled_lines.append(' ')
                        break

                else:
                    styled_line = self.apply_style('default', line)
                    styled_lines.append(styled_line)
                    styled_lines.append(' ')

        return styled_lines


    def handle_exception(self):
        self.print_error()

        if self.format_specific_exception:
            tb = ''.join(traceback.format_exception(None, self, self.__traceback__))
        else:
            tb = traceback.format_exc()

        tb_lines = tb.split('\n')

        # Stylize the traceback
        styled_tb_lines = self.stylize_traceback(tb_lines)

        # Print the stylized traceback
        for line in styled_tb_lines:
            print(line, file=sys.stderr)

        print()


class ColorNotFoundError(ColorPrinterError):
    """Exception raised when a color is not found in the color map."""
    pass


class InvalidLengthError(ColorPrinterError):
    """Exception raised when an invalid length is provided."""
    pass


class UnsupportedEffectError(ColorPrinterError):
    """Exception raised when an unsupported effect is requested."""
    pass


# Define the global exception hook
def custom_excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, ColorPrinterError):
        exc_value.handle_exception()
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


# Set the custom exception hook
sys.excepthook = custom_excepthook




