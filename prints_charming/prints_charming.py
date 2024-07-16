# prints_charming.py

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import os
import sys
import traceback
import re
import logging
from time import perf_counter



def get_terminal_width():
    terminal_size = os.get_terminal_size()
    return terminal_size.columns


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
    reset = "\033[0m"
    
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
        "kwargs"              : True,
        "conceal"             : True,
    }

    COLOR_MAP: Dict[str, str] = {
        "default" : "\033[0m",
        "white"   : "\033[97m",
        "gray"    : "\033[38;5;248m",
        "dgray"   : "\033[38;5;8m",
        "black"   : "\033[30m",
        "green"   : "\033[32m",
        "vgreen"  : "\033[38;5;46m",
        "lime"    : "\033[38;5;118m",
        "forest"  : "\033[38;5;28m",
        "aqua"    : "\033[38;5;122m",
        "turq"    : "\033[38;5;80m",
        "red"     : "\033[31m",
        "vred"    : "\033[38;5;196m",
        "maroon"  : "\033[38;5;124m",
        "yellow"  : "\033[33m",
        "vyellow" : "\033[38;5;226m",
        "blue"    : "\033[34m",
        "dblue"   : "\033[38;5;21m",
        "vblue"   : "\033[38;5;27m",
        "navy"    : "\033[38;5;17m",
        "sky"     : "\033[38;5;117m",
        "vsky"    : "\033[38;5;39m",
        "magenta" : "\033[35m",
        "vmagenta": "\033[38;5;201m",
        "cyan"    : "\033[36m",
        "vcyan"   : "\033[38;5;51m",
        "orange"  : "\033[38;5;208m",
        "vorange" : "\033[38;5;202m",
        "rorange" : "\033[38;5;203m",
        "pink"    : "\033[38;5;200m",
        "lpink"   : "\033[38;5;218m",
        "purple"  : "\033[38;5;129m",
        "lpurple" : "\033[38;5;147m",
        "indigo"  : "\033[38;5;63m",
        "violet" : "\033[38;5;69m",
        "lav"     : "\033[38;5;183m",
        "brown"   : "\033[38;5;94m",
        "gold"    : "\033[38;5;220m",
        "sand"    : "\033[38;5;215m",
        "copper"  : "\033[38;5;166m"
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
        "default_bg"   : TextStyle(bg_color="black"),
        "white"        : TextStyle(color="white"),
        "gray"         : TextStyle(color="gray"),
        "dgray"        : TextStyle(color="dgray"),
        "black"        : TextStyle(color="black"),
        "green"        : TextStyle(color="green"),
        "vgreen"       : TextStyle(color="vgreen", bold=True),
        "forest"       : TextStyle(color="forest", bold=True),
        "red"          : TextStyle(color="red"),
        "vred"         : TextStyle(color="vred", bold=True),
        "blue"         : TextStyle(color="blue"),
        "dblue"        : TextStyle(color="dblue"),
        "vblue"        : TextStyle(color="vblue"),
        "yellow"       : TextStyle(color="yellow"),
        "vyellow"      : TextStyle(color="vyellow"),
        "magenta"      : TextStyle(color="magenta", bold=True),
        "vmagenta"     : TextStyle(color="vmagenta"),
        "pink"         : TextStyle(color="pink"),
        "purple"       : TextStyle(color="purple"),
        "cyan"         : TextStyle(color="cyan"),
        "vcyan"        : TextStyle(color="vcyan"),
        "orange"       : TextStyle(color="orange"),
        "copper"       : TextStyle(color="copper"),
        "brown"        : TextStyle(color="brown"),
        "sand"         : TextStyle(color="sand"),
        "lav"          : TextStyle(color="lav"),
        "lpurple"      : TextStyle(color="lpurple"),
        "header"       : TextStyle(color="vcyan"),
        "header_text"  : TextStyle(color="purple", bg_color="gray", bold=True, italic=True),
        "header_text2" : TextStyle(color="gray", bg_color="purple", bold=True),
        "header_symbol": TextStyle(color="magenta", bold=True, overlined=True, strikethrough=True),
        "task"         : TextStyle(color="blue", bold=True),
        "path"         : TextStyle(color="blue"),
        "filename"     : TextStyle(color="yellow"),
        "line_info"    : TextStyle(color="yellow", bold=True),
        "line_number"  : TextStyle(color="yellow", bold=True),
        "function_name": TextStyle(color="yellow", italic=True),
        "error_message": TextStyle(color="vred", bg_color="vyellow", bold=True),
        "code"         : TextStyle(color="yellow"),
        "label"        : TextStyle(bold=True, italic=True),
        "conceal"      : TextStyle(conceal=True),
    }



    def __init__(self,
                 config: Optional[Dict[str, Union[bool, str, int]]] = None,
                 color_map: Optional[Dict[str, str]] = None,
                 bg_color_map: Optional[Dict[str, str]] = None,
                 effect_map: Optional[Dict[str, str]] = None,
                 styles: Optional[Dict[str, TextStyle]] = None,
                 colorprinter_variables: Optional[Dict[str, List[str]]] = None,
                 style_conditions: Optional[Any] = None,
                 ) -> None:

        """
        Initialize the ColorPrinter with args to any of these optional parameters.

        :param config: enable or disable various functionalities of this class. Default is the ColorPrinter.CONFIG dictionary above
        :param color_map: supply your own color_map dictionary. Default is the ColorPrinter.COLOR_MAP dictionary above
        :param bg_color_map: supply your own bg_color_map dictionary. Default is computed from color_map dictionary
        :param effect_map: supply your own effect_map dictionary. Default is the ColorPrinter.EFFECT_MAP dictionary above
        :param styles: supply your own styles dictionary. Default is the ColorPrinter.STYLES dictionary above
        :param colorprinter_variables: calls the add_variables_from_dict method with your provided dictionary. See README for more info.
        :param style_conditions: A custom class for implementing dynamic application of styles to text based on conditions.
        """

        if not config:
            config = ColorPrinter.CONFIG.copy()
        self.config = config

        if not color_map:
            color_map = ColorPrinter.COLOR_MAP.copy()
        self.color_map = color_map

        if not bg_color_map:
            bg_color_map = {
                color: self.compute_bg_color_map(code) for color, code in self.color_map.items()
            }
        self.bg_color_map = bg_color_map

        if not effect_map:
            effect_map = ColorPrinter.EFFECT_MAP.copy()
        self.effect_map = effect_map


        if not styles:
            styles = ColorPrinter.STYLES.copy()
        self.styles = styles

        self.style_codes: Dict[str, str] = {
            name: self.create_style_code(style) for name, style in self.styles.items() if self.styles[name].color in self.color_map
        }

        self.reset = ColorPrinter.reset


        self.variable_map: Dict[str, str] = {}
        self.word_map: Dict[str, Dict[str, str]] = {}
        self.phrase_map: Dict[str, Dict[str, str]] = {}
        self.conceal_map: Dict[str, Dict[str, str]] = {}

        if colorprinter_variables:
            self.add_variables_from_dict(colorprinter_variables)

        self.style_conditions = style_conditions
        self.style_conditions_map = {}
        if style_conditions:
            self.style_conditions_map = style_conditions.map


    def replace_and_style_placeholders(self, text: str, kwargs: Dict[str, Any], enable_label_style: bool = True, label_delimiter: str = ':') -> str:
        """Replace placeholders with actual values and apply colors."""
        label_style_code = self.get_style_code('label') if enable_label_style else ''
        lines = text.split('\n')

        # Style labels directly in the text
        if enable_label_style:
            for i, line in enumerate(lines):
                # Handle standalone labels that end with ':'
                if line.strip().endswith(label_delimiter):
                    label, _, rest = line.partition(label_delimiter)
                    lines[i] = f"{label_style_code}{label}{label_delimiter}{self.reset}{rest}"
                # Handle inline labels followed by placeholders
                elif label_delimiter in line:
                    label, delimiter, rest = line.partition(label_delimiter)
                    if '{' in rest:
                        lines[i] = f"{label_style_code}{label}{delimiter}{self.reset}{rest}"

        styled_text = '\n'.join(lines)

        # Replace placeholders with actual values and apply styles
        for key, value in kwargs.items():
            styled_value = str(value)
            if key in self.style_conditions_map:
                style_name = self.style_conditions_map[key](value)
                style_code = self.get_style_code(style_name)
                styled_value = f"{style_code}{styled_value}{self.reset}"
            styled_text = styled_text.replace(f"{{{key}}}", styled_value)

        return styled_text


    def compute_bg_color_map(self, code):
        if '[38' in code:
            bg_code = code.replace('[38', '[48')  # Change to background color for 256-color codes
        elif '[9' in code:
            bg_code = code.replace('[9', '[10')  # Special handling for white, which starts with 9
        else:
            bg_code = code.replace('[3', '[4')  # Basic ANSI colors: convert foreground color to background color

        return bg_code

    def print_bg(self, color_name: str, length: int = 1) -> None:
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


    def return_bg(self, color_name: str, length: int = 10) -> str:

        if length <= 0:
            message = f"Invalid length '{length}'. Length must be positive."
            styled_message = self.apply_style('vred', message)
            raise InvalidLengthError(styled_message, self, self.apply_style)

        bg_color_code = self.bg_color_map.get(color_name)
        if not bg_color_code:
            message = f"Key '{color_name}' not found in the 'self.bg_color_map' dictionary."
            styled_message = self.apply_style('vred', message)
            raise ColorNotFoundError(styled_message, self, self.apply_style, format_specific_exception=True)

        # style the color block
        bg_bar_strip = f"{bg_color_code}{' ' * length}{self.reset}"

        return bg_bar_strip


    def get_bg_bar_strip(self, color_name: str, length: int = 1) -> str:
        bg_color_code = self.bg_color_map.get(color_name)
        bg_bar_strip = f"{bg_color_code}{' ' * length}{self.reset}"

        return bg_bar_strip



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

        if text.isspace():
            style_code = self.bg_color_map.get(
                style_name,
                self.bg_color_map.get(
                    self.styles.get(style_name, 'default_bg').bg_color
                )
            )

        else:
            style_code = self.style_codes[style_name]

        # Append the style code at the beginning of the text and the reset code at the end
        styled_text = f"{style_code}{text}{self.reset}"

        return styled_text


    def get_color_code(self, color_name):
        return self.color_map.get(color_name, self.color_map['default'])

    def apply_color(self, color_name, text):
        color_code = self.color_map[color_name]
        colored_text = f"{color_code}{text}{self.reset}"

        return colored_text


    def get_bg_color_code(self, color_name):
        return self.bg_color_map.get(color_name)


    def apply_bg_color(self, color_name, text):
        bg_color_code = self.bg_color_map.get(color_name)
        bg_color_block = f"{bg_color_code}{text}{self.reset}"

        return bg_color_block


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


    def print_variables(self, vars_and_styles: Union[Dict[str, Tuple[Any, str]], Tuple[List[Any], List[str]]],
                        text: str, text_style: str = None) -> None:

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

        self.print(text, style=text_style, skip_ansi_check=True)


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

    @staticmethod
    def contains_ansi_codes(s: str) -> bool:
        return '\033' in s


    def print(self,
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
              sep: str = ' ',
              end: str = '\n',
              filename: str = None,
              skip_ansi_check: bool = False,
              **kwargs: Any) -> None:

        converted_args = [str(arg) for arg in args] if self.config["args_to_strings"] else args

        # Handle not colored text
        if not self.config["color_text"]:
            output = sep.join(converted_args)
            if filename:
                with open(filename, 'a') as file:
                    file.write(output + end)
            else:
                print(output, end=end)
            return

        # Check for ANSI codes in converted_args
        if not skip_ansi_check and any(self.contains_ansi_codes(arg) for arg in converted_args):
            # Handle ANSI styled text if any ANSI codes are found
            output = sep.join(converted_args)
            if filename:
                with open(filename, 'a') as file:
                    file.write(output + end)
            else:
                print(output, end=end)
            return


        # Handle variable replacement
        if var is not None:
            variable = str(var)
            var_style_code = self.style_codes[vstyle]
            if text is not None:
                text = text.replace('var', f"{var_style_code}{variable}{self.reset}")
                style = tstyle
            else:
                text = f"{var_style_code}{variable}{self.reset}"

        # If text was modified, it takes precedence
        if text is not None:
            converted_args = [text] + converted_args

        text = sep.join(converted_args)

        if self.config["style_words_by_index"] and isinstance(style, dict):
            text = self.style_words_by_index(text, style)

        if self.config["kwargs"] and kwargs:
            text = self.replace_and_style_placeholders(text, kwargs)
            if filename:
                with open(filename, 'a') as file:
                    file.write(text + end)
            else:
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

        # Print or write to file
        if filename:
            with open(filename, 'a') as file:
                file.write(styled_text + end)
        else:
            print(styled_text, end=end)


        return



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




class TableManager:
    def __init__(self, cp: ColorPrinter = None, style_themes: dict = None, conditional_styles: dict = None):
        self.cp = cp if cp else ColorPrinter()
        self.style_themes = style_themes
        self.conditional_styles = conditional_styles
        self.tables = {}

        self.border_char = "-"
        self.col_sep = " | "
        self.title_style = "header_text"


    def generate_table(self,
                       table_data: List[List[Any]],
                       table_name: str = None,
                       show_table_name: bool = False,
                       table_style: str = "default",
                       border_char: str = "-",
                       col_sep: str = " | ",
                       border_style: Optional[str] = None,
                       col_sep_style: Optional[str] = None,
                       header_style: Optional[str] = None,
                       header_column_styles: Optional[Dict[int, str]] = None,
                       col_alignments: Optional[List[str]] = None,
                       column_styles: Optional[Dict[int, str]] = None,
                       cell_style: Optional[str or list] = None,
                       target_text_box: bool = False,
                       conditional_styles: Optional[Dict[str, List[Dict[str, Union[str, int]]]]] = None,
                       double_space: bool = False
                       ) -> str:

        """
        Generates a table with optional styling and alignment as a string.

        :param table_data: A list of lists representing the rows of the table.
        :param col_alignments: A list of strings ('left', 'center', 'right') for column alignments.
        :param cell_style: Style name for the table cells.
        :param header_style: Style name for the header row.
        :param header_column_styles: A dictionary mapping column indices to style names for the header row.
        :param border_style: Style name for the table borders.
        :param column_styles: A dictionary mapping column indices to style names.
        :param conditional_styles: A dictionary defining conditional styles based on cell values.
        :return: A string representing the formatted table.
        """

        styled_col_sep = self.cp.apply_style(col_sep_style, col_sep) if col_sep_style else col_sep

        # 1. Automatic Column Sizing
        max_col_lengths = [0] * len(table_data[0])
        for row in table_data:
            for i, cell in enumerate(row):
                cell_length = len(str(cell))
                max_col_lengths[i] = max(max_col_lengths[i], cell_length)

        # 2. Column Alignment
        table_output = []
        header = table_data[0]

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
                else:
                    aligned_cell = cell_str.ljust(max_length)  # Fallback

                # Apply the style
                if row_idx == 0:
                    # Apply header styles
                    if header_column_styles and i in header_column_styles:
                        aligned_cell = self.cp.apply_style(header_column_styles[i], aligned_cell)
                    elif header_style:
                        aligned_cell = self.cp.apply_style(header_style, aligned_cell)
                else:
                    if header[i] == 'Color Name':
                        aligned_cell = self.cp.apply_color(cell_str, aligned_cell)
                    elif header[i] == 'Foreground Text':
                        color_name = row[0]  # Assuming the first column is the color name
                        aligned_cell = self.cp.apply_color(color_name, aligned_cell)
                    elif header[i] == 'Background Block':
                        color_name = row[0]  # Assuming the first column is the color name
                        aligned_cell = self.cp.return_bg(color_name, length=max_length)

                    # Apply conditional styles if provided
                    elif conditional_styles and header[i] in conditional_styles:
                        for condition in conditional_styles[header[i]]:
                            if condition["type"] == "below" and isinstance(cell, (int, float)) and cell < condition["value"]:
                                aligned_cell = self.cp.apply_style(condition["style"], aligned_cell)
                            elif condition["type"] == "above_or_equal" and isinstance(cell, (int, float)) and cell >= condition["value"]:
                                aligned_cell = self.cp.apply_style(condition["style"], aligned_cell)
                            elif condition["type"] == "equals" and cell_str == condition["value"]:
                                aligned_cell = self.cp.apply_style(condition["style"], aligned_cell)
                            elif condition["type"] == "in_list" and cell_str in condition["value"]:
                                aligned_cell = self.cp.apply_style(condition["style"], aligned_cell)
                            elif condition["type"] == "not_in_list" and cell_str not in condition["value"]:
                                aligned_cell = self.cp.apply_style(condition["style"], aligned_cell)
                    elif column_styles and i in column_styles:
                        # Apply column-specific styles if provided
                        aligned_cell = self.cp.apply_style(column_styles[i], aligned_cell)
                    elif cell_style:
                        if isinstance(cell_style, list):
                            # Apply alternating styles based on the row index
                            style_to_apply = cell_style[0] if row_idx % 2 == 1 else cell_style[1]
                            aligned_cell = self.cp.apply_style(style_to_apply, aligned_cell)
                        else:
                            aligned_cell = self.cp.apply_style(cell_style, aligned_cell)


                # Add aligned and styled cell to the row
                aligned_row.append(aligned_cell)

            # Create a row string and add to table output
            if target_text_box:
                row_str = self.cp.apply_style(col_sep_style, col_sep.lstrip()) + styled_col_sep.join(aligned_row) + self.cp.apply_style(col_sep_style, col_sep.rstrip())
            else:
                row_str = styled_col_sep + styled_col_sep.join(aligned_row) + styled_col_sep
            table_output.append(row_str)

        # 3. Generate Borders and Rows
        table_str = ""
        border_line = ""  # Initialize border_line to ensure it always has a value
        if border_style:
            border_length = sum(max_col_lengths) + len(max_col_lengths) * len(col_sep) + len(col_sep) - 2
            border_line = self.cp.apply_style(border_style, border_char * border_length)
            #print(f' {border_line}')
            if target_text_box:
                table_str += f'{border_line}\n'
            else:
                table_str += f' {border_line}\n'

        if show_table_name and table_name:
            centered_table_name = self.cp.apply_style(self.title_style, table_name.center(border_length))
            table_str += f'{centered_table_name}\n'
            if border_style:
                table_str += f'{border_line}\n'

        for i, row in enumerate(table_output):
            #print(row)
            table_str += row + "\n"
            if i != 0 and double_space:
                table_str += "\n"
            #if double_space:
                #table_str += "\n"
            if i == 0 and (header_style or header_column_styles) and border_style:
                #print(f' {border_line}')
                if target_text_box:
                    table_str += f'{border_line}\n'
                else:
                    table_str += f' {border_line}\n'

        if border_style:
            #print(f' {border_line}')
            if target_text_box:
                table_str += f'{border_line}\n'
            else:
                table_str += f' {border_line}\n'

        return table_str






class FormattedTextBox:
    def __init__(self, cp=None, horiz_width=None, horiz_char=' ', vert_width=None, vert_padding=0, vert_char='|'):
        self.cp = cp if cp else ColorPrinter()
        self.terminal_width = get_terminal_width()
        self.horiz_width = horiz_width if horiz_width else self.terminal_width
        self.horiz_char = horiz_char
        self.horiz_border = self.horiz_width * horiz_char
        self.vert_width = vert_width
        self.vert_padding = vert_padding * ' '
        self.vert_char = horiz_char if vert_width and not vert_char else vert_char
        self.vert_border = '' if not vert_width else vert_width * self.vert_char


    def align_text(self, text, available_width, align='center'):

        if align == 'left':
            return text.ljust(available_width)
        elif align == 'right':
            return text.rjust(available_width)
        elif align == 'center':
            return text.center(available_width)
        else:
            raise ValueError("Invalid alignment. Choose from 'left', 'right', or 'center'.")



    def align_strings(self, strings, available_width=None, styles=None, alignments=None):
        if len(strings) not in [2, 3]:
            raise ValueError("The list must contain exactly two or three strings.")

        if not available_width:
            available_width = self.get_available_width()

        if len(strings) == 3:
            part_width = available_width // 3
            remainder = available_width % 3

            if remainder != 0:
                left_right_width = (available_width - (part_width + remainder)) // 2
                center_width = part_width + remainder
            else:
                left_right_width = part_width
                center_width = part_width

            # Check if any string is too long
            for i, string in enumerate(strings):
                if i == 1:  # Center part
                    max_width = center_width
                else:  # Left and right parts
                    max_width = left_right_width

                if len(string) > max_width:
                    raise ValueError(f"String at index {i} ('{string}') is too long. "
                                     f"Section width: {max_width}, String length: {len(string)}")

            if not styles:
                styles = ['default', 'default', 'default']
            if isinstance(styles, str):
                styles = [styles, styles, styles]

            if not alignments:
                alignments = ['center', 'center', 'center']
            if isinstance(alignments, str):
                alignments = [alignments, alignments, alignments]

            left_aligned = self.cp.apply_style(styles[0], self.align_text(strings[0], left_right_width, alignments[0]))
            center_aligned = self.cp.apply_style(styles[1], self.align_text(strings[1], center_width, alignments[1]))
            right_aligned = self.cp.apply_style(styles[2], self.align_text(strings[2], left_right_width, alignments[2]))

            # Concatenate the aligned strings
            return left_aligned + center_aligned + right_aligned


        elif len(strings) == 2:
            # Determine the width for each section
            part_width = available_width // 2

            # Check if any string is too long
            for i, string in enumerate(strings):
                if len(string) > part_width:
                    raise ValueError(f"String at index {i} ('{string}') is too long. "
                                     f"Section width: {part_width}, String length: {len(string)}")

            if not styles:
                styles = ['default', 'default']
            if isinstance(styles, str):
                styles = [styles, styles]

            if not alignments:
                alignments = ['center', 'center']
            if isinstance(alignments, str):
                alignments = [alignments, alignments]

            left_aligned = self.cp.apply_style(styles[0], self.align_text(strings[0], part_width, alignments[0]))
            right_aligned = self.cp.apply_style(styles[1], self.align_text(strings[1], part_width, alignments[1]))

            # Concatenate the aligned strings
            return left_aligned + right_aligned


    def split_text_to_lines(self, text, available_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= available_width:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines


    def get_available_width(self):
        return self.horiz_width - (2 * self.vert_width) - 2 if self.vert_border else self.horiz_width - (len(self.vert_padding) * 2)

    def strip_ansi_escape_sequences(self, text):
        ansi_escape = re.compile(r'\x1b\[([0-9]+)(;[0-9]+)*m')
        return ansi_escape.sub('', text)

    def print_simple_border_boxed_text(self, title, subtitle='', align='center'):
        available_width = self.get_available_width()

        title_aligned_text = self.cp.apply_style('vgreen', self.align_text(title, available_width, align))

        if subtitle:
            subtitle_aligned_text = self.cp.apply_style('white', self.align_text(subtitle, available_width, align))
        else:
            subtitle_aligned_text = ''

        horiz_border_top = self.cp.apply_style('purple', self.horiz_border)
        horiz_border_bottom = self.cp.apply_style('orange', self.horiz_border)

        title_vert_border_left = self.cp.apply_style('orange', self.vert_border) + self.vert_padding
        title_vert_border_right = self.vert_padding + self.cp.apply_style('purple', self.vert_border)

        subtitle_vert_border_left = self.cp.apply_style('orange', self.vert_border) + self.vert_padding
        subtitle_vert_border_right = self.vert_padding + self.cp.apply_style('purple', self.vert_border)

        formatted_title_line = f"{title_vert_border_left}{title_aligned_text}{title_vert_border_right}"
        if subtitle:
            formatted_subtitle_line = f"{subtitle_vert_border_left}{subtitle_aligned_text}{subtitle_vert_border_right}"

        print(horiz_border_top)
        print(formatted_title_line)
        if subtitle:
            print(formatted_subtitle_line)
        print(horiz_border_bottom)
        print()




    def build_border_box(self, horiz_border_top=True, horiz_border_top_style=None,
                         horiz_border_bottom=True, horiz_border_bottom_style=None,
                         vert_border_left=True, vert_border_left_style=None,
                         vert_border_right=True, vert_border_right_style=None):

        if horiz_border_top:
            horiz_border_top = self.horiz_border if not horiz_border_top_style else self.cp.apply_style(horiz_border_top_style, self.horiz_border)
        else:
            horiz_border_top = None

        if horiz_border_bottom:
            horiz_border_bottom = self.horiz_border if not horiz_border_bottom_style else self.cp.apply_style(horiz_border_bottom_style, self.horiz_border)
        else:
            horiz_border_bottom = None

        if self.vert_char == ' ':
            if vert_border_left:
                vert_border_left = self.vert_border + self.vert_padding if not vert_border_left_style else self.cp.apply_bg_color(vert_border_left_style, self.vert_border) + self.vert_padding
            else:
                vert_border_left = self.vert_padding

            if vert_border_right:
                vert_border_right = self.vert_padding + self.vert_border if not vert_border_right_style else self.vert_padding + self.cp.apply_bg_color(vert_border_right_style, self.vert_border)
            else:
                vert_border_right = self.vert_padding

        else:
            if vert_border_left:
                vert_border_left = self.vert_border + self.vert_padding if not vert_border_left_style else self.cp.apply_style(vert_border_left_style, self.vert_border) + self.vert_padding
            else:
                vert_border_left = self.vert_padding

            if vert_border_right:
                vert_border_right = self.vert_padding + self.vert_border if not vert_border_right_style else self.vert_padding + self.cp.apply_style(vert_border_right_style, self.vert_border)
            else:
                vert_border_right = self.vert_padding



        return horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom



    def print_border_boxed_text(self, text, text_style=None, text_align='center', subtext='', subtext_style=None, subtext_align='center', horiz_border_top=True, horiz_border_top_style=None, horiz_border_bottom=True, horiz_border_bottom_style=None, text_vert_border_l_style=None, text_vert_border_r_style=None, subtext_vert_border_l_style=None, subtext_vert_border_r_style=None, first_line_blank=False):

        if not text_style:
            text_style = 'default'
        if not subtext_style:
            subtext_style = 'default'

        available_width = self.get_available_width()
        text_lines = self.split_text_to_lines(text, available_width)
        subtext_lines = self.split_text_to_lines(subtext, available_width) if subtext else []

        if horiz_border_top:
            horiz_border_top = self.horiz_border if not horiz_border_top_style else self.cp.apply_style(horiz_border_top_style, self.horiz_border)
            print(horiz_border_top)

        if first_line_blank:
            blank_text = ' '
            blank_aligned_text = self.align_text(blank_text, available_width, text_align)
            if self.vert_border:
                blank_text_vert_border_left = self.vert_border + self.vert_padding if not text_vert_border_l_style else self.cp.apply_style(text_vert_border_l_style, self.vert_border) + self.vert_padding
                blank_text_vert_border_right = self.vert_padding + self.vert_border + self.vert_padding if not text_vert_border_r_style else self.vert_padding + self.cp.apply_style(text_vert_border_r_style, self.vert_border)
                print(f"{blank_text_vert_border_left}{blank_aligned_text}{blank_text_vert_border_right}")
            else:
                print(f"{self.vert_padding}{blank_aligned_text}{self.vert_padding}")


        for line in text_lines:
            aligned_text = self.cp.apply_style(text_style, self.align_text(line, available_width, text_align))
            if self.vert_border:
                text_vert_border_left = self.vert_border + self.vert_padding if not text_vert_border_l_style else self.cp.apply_style(text_vert_border_l_style, self.vert_border) + self.vert_padding
                text_vert_border_right = self.vert_padding + self.vert_border + self.vert_padding if not text_vert_border_r_style else self.vert_padding + self.cp.apply_style(text_vert_border_r_style, self.vert_border)
                print(f"{text_vert_border_left}{aligned_text}{text_vert_border_right}")
            else:
                txt_vert_border_left = self.vert_padding
                txt_vert_border_right = self.vert_padding
                print(f"{self.vert_padding}{aligned_text}{self.vert_padding}")

        for line in subtext_lines:
            aligned_subtext = self.cp.apply_style(subtext_style, self.align_text(line, available_width, subtext_align))
            if self.vert_border:
                subtext_vert_border_left = self.vert_border + self.vert_padding if not subtext_vert_border_l_style else self.cp.apply_style(subtext_vert_border_l_style, self.vert_border) + self.vert_padding
                subtext_vert_border_right = self.vert_padding + self.vert_border if not subtext_vert_border_r_style else self.vert_padding + self.cp.apply_style(subtext_vert_border_r_style, self.vert_border)
                print(f"{subtext_vert_border_left}{aligned_subtext}{subtext_vert_border_right}")
            else:
                print(f"{self.vert_padding}{aligned_subtext}{self.vert_padding}")

        if horiz_border_bottom:
            horiz_border_bottom = self.horiz_border if not horiz_border_bottom_style else self.cp.apply_style(horiz_border_bottom_style, self.horiz_border)
            print(horiz_border_bottom)



    def print_border_boxed_text2(self, texts, text_styles=None, alignments=None,
                                 horiz_border_top=True, horiz_border_bottom=True,
                                 horiz_border_top_style=None, horiz_border_bottom_style=None,
                                 vert_border_l_style=None, vert_border_r_style=None,  vert_borders=True):

        # Set default values for parameters if not provided
        if not text_styles:
            text_styles = ['default'] * len(texts)
        if isinstance(text_styles, str):
            text_styles = [text_styles] * len(texts)

        if not alignments:
            alignments = ['center'] * len(texts)
        if isinstance(alignments, str):
            alignments = [alignments] * len(texts)

        available_width = self.get_available_width()
        lines_list = [self.split_text_to_lines(text, available_width) for text in texts]


        horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom = self.build_border_box(
            horiz_border_top=horiz_border_top,
            horiz_border_top_style=horiz_border_top_style,
            horiz_border_bottom=horiz_border_bottom,
            horiz_border_bottom_style=horiz_border_bottom_style,
            vert_border_left=vert_borders,
            vert_border_left_style=vert_border_l_style,
            vert_border_right=vert_borders,
            vert_border_right_style=vert_border_r_style
        )

        if horiz_border_top:
            print(horiz_border_top)

        for lines, text_style, text_align in zip(lines_list, text_styles, alignments):
            for line in lines:
                if line == 'invisible_text' or line == '':
                    line = ' '
                    aligned_text = self.align_text(line, available_width, text_align)
                else:
                    aligned_text = self.cp.apply_style(text_style, self.align_text(line, available_width, text_align))

                print(f"{vert_border_left}{aligned_text}{vert_border_right}")


        if horiz_border_bottom:
            print(horiz_border_bottom)



    def construct_text(self, vert_border_left, vert_border_right, aligned_text):
        # Define a dictionary mapping conditions to their corresponding text constructions
        construction_map = {
            (True, True): lambda: f"{vert_border_left}{aligned_text}{vert_border_right}",
            (True, False): lambda: f"{vert_border_left}{aligned_text}",
            (False, True): lambda: f"{aligned_text}{vert_border_right}",
            (False, False): lambda: aligned_text
        }

        # Determine the key based on the presence of the borders
        key = (bool(vert_border_left), bool(vert_border_right))

        # Construct and return the text based on the mapped lambda function
        return construction_map[key]()


    def print_border_boxed_text3(self, texts, text_styles=None, alignments=None,
                                 horiz_border_top=None, horiz_border_bottom=None,
                                 vert_border_left=None, vert_border_right=None,
                                 default_alignment='center'):

        # Set default values for parameters if not provided
        if not text_styles:
            text_styles = ['default'] * len(texts)
        if isinstance(text_styles, str):
            text_styles = [text_styles] * len(texts)

        if not alignments:
            alignments = [default_alignment] * len(texts)
        if isinstance(alignments, str):
            alignments = [alignments] * len(texts)

        available_width = self.get_available_width()
        lines_list = [self.split_text_to_lines(text, available_width) for text in texts]

        if horiz_border_top:
            print(horiz_border_top)

        for lines, text_style, text_align in zip(lines_list, text_styles, alignments):
            for line in lines:
                if line == 'invisible_text' or line == '':
                    line = ' '
                    aligned_text = self.align_text(line, available_width, text_align)
                else:
                    aligned_text = self.cp.apply_style(text_style, self.align_text(line, available_width, text_align))

                final_text = self.construct_text(vert_border_left, vert_border_right, aligned_text)

                print(final_text)

        if horiz_border_bottom:
            print(horiz_border_bottom)

    def print_border_boxed_text4(self, texts, text_styles=None, text_alignments=None,
                                 horiz_border_top=None, horiz_border_bottom=None,
                                 vert_border_left=None, vert_border_right=None,
                                 default_text_alignment='center',
                                 table_strs=None, table_strs_alignments=None,
                                 table_strs_horiz_border_top=False,
                                 table_strs_horiz_border_bottom=False,
                                 table_strs_vert_border_left=False,
                                 table_strs_vert_border_right=False,
                                 default_table_alignment='center'):

        # Set default values for parameters if not provided
        if not text_styles:
            text_styles = ['default'] * len(texts)
        if isinstance(text_styles, str):
            text_styles = [text_styles] * len(texts)

        if not text_alignments:
            text_alignments = [default_text_alignment] * len(texts)
        if isinstance(text_alignments, str):
            text_alignments = [text_alignments] * len(texts)

        available_width = self.get_available_width()
        lines_list = [self.split_text_to_lines(text, available_width) for text in texts]

        if horiz_border_top:
            print(horiz_border_top)

        for lines, text_style, text_align in zip(lines_list, text_styles, text_alignments):
            for line in lines:
                if line == 'invisible_text' or line == '':
                    line = ' '
                    aligned_text = self.align_text(line, available_width, text_align)
                else:
                    aligned_text = self.cp.apply_style(text_style, self.align_text(line, available_width, text_align))

                final_text = self.construct_text(vert_border_left, vert_border_right, aligned_text)

                print(final_text)

        if horiz_border_bottom:
            print(horiz_border_bottom)
            blank_text = ' '
            print(blank_text.center(self.horiz_width))




        if table_strs:
            if table_strs_horiz_border_top and isinstance(table_strs_horiz_border_top, bool):
                table_strs_horiz_border_top = horiz_border_top
            if table_strs_horiz_border_bottom and isinstance(table_strs_horiz_border_bottom, bool):
                table_strs_horiz_border_bottom = horiz_border_bottom
            if table_strs_vert_border_left and isinstance(table_strs_vert_border_left, bool):
                table_strs_vert_border_left = vert_border_left
            if table_strs_vert_border_right and isinstance(table_strs_vert_border_right, bool):
                table_strs_vert_border_right = vert_border_right


            if not table_strs_alignments:
                table_strs_alignments = [default_table_alignment] * len(table_strs)
            if isinstance(table_strs_alignments, str):
                table_strs_alignments = [table_strs_alignments] * len(table_strs)

            if len(table_strs) > 1:

                self.print_border_boxed_tables(table_strs,
                                               horiz_border_top=table_strs_horiz_border_top,
                                               vert_border_left=table_strs_vert_border_left,
                                               vert_border_right=table_strs_vert_border_right,
                                               horiz_border_bottom=table_strs_horiz_border_bottom,
                                               alignments=table_strs_alignments)
            else:
                table_str = table_strs[0]
                table_str_alignment = table_strs_alignments[0]
                self.print_border_boxed_table(table_str,
                                              table_strs_horiz_border_top,
                                              table_strs_vert_border_left,
                                              table_strs_vert_border_right,
                                              table_strs_horiz_border_bottom,
                                              text_align=table_str_alignment)

        if horiz_border_bottom:
            print(horiz_border_bottom)




    def print_border_boxed_table(self,
                                 table_str,
                                 horiz_border_top,
                                 vert_border_left,
                                 vert_border_right,
                                 horiz_border_bottom,
                                 table_style=None,
                                 text_style=None,
                                 text_align='center'):

        available_width = self.get_available_width()
        table_lines = table_str.split("\n")

        if horiz_border_top:
            print(horiz_border_top)
            blank_line = ' '.center(available_width)
            print(f'{vert_border_left}{blank_line}{vert_border_right}')

        for line in table_lines:
            stripped_line = self.strip_ansi_escape_sequences(line)
            padding_needed = available_width - len(stripped_line)
            if text_align == 'center':
                leading_spaces = padding_needed // 2
                trailing_spaces = padding_needed - leading_spaces
                aligned_text = ' ' * leading_spaces + line + ' ' * trailing_spaces
            elif text_align == 'left':
                aligned_text = line + ' ' * padding_needed
            else:
                aligned_text = padding_needed * ' ' + line


            final_text = self.construct_text(vert_border_left, vert_border_right, aligned_text)

            print(final_text)

            #print(f"{vert_border_left}{aligned_text}{vert_border_right}")
            #aligned_text = self.align_text(line, available_width, text_align)
            #print(f"{vert_border_left}{aligned_text}{vert_border_right}")

        if horiz_border_bottom:
            print(horiz_border_bottom)




    def print_border_boxed_tables(self,
                                  table_strs,
                                  horiz_border_top,
                                  vert_border_left,
                                  vert_border_right,
                                  horiz_border_bottom,
                                  table_padding=4,
                                  table_style=None,
                                  text_style=None,
                                  text_align='center',
                                  alignments=None):
        available_width = self.get_available_width()
        table_lines_list = [table_str.split("\n") for table_str in table_strs]

        blank_line = None

        max_lines = max(len(table_lines) for table_lines in table_lines_list)
        for table_lines in table_lines_list:
            table_lines += [''] * (max_lines - len(table_lines))

        if horiz_border_top:
            print(horiz_border_top)
            blank_line = ' '.center(available_width)
            print(f'{vert_border_left}{blank_line}{vert_border_right}')

        current_width = 0
        row_buffer = []

        for line_index in range(max_lines):
            row = ""
            row_length = 0
            for table_index, table_lines in enumerate(table_lines_list):
                line = table_lines[line_index]
                stripped_line = self.strip_ansi_escape_sequences(line)
                line_length = len(stripped_line)
                if current_width + line_length > available_width:
                    row_buffer.append(row.rstrip())
                    row = ""
                    current_width = 0
                if row:
                    row += " " * table_padding
                    row_length += table_padding
                row += line
                row_length += line_length
                current_width += line_length + table_padding

            if row:
                row_buffer.append(row.rstrip())
                current_width = 0

        for row in row_buffer:

            row_length = len(self.strip_ansi_escape_sequences(row))
            leading_spaces = (available_width - row_length) // 2
            if (available_width - row_length) % 2 != 0:
                leading_spaces += 1  # Adjust if the remaining space is odd
            #print(leading_spaces)
            #padding_needed = available_width - len(self.strip_ansi_escape_sequences(row))
            #aligned_text = row + ' ' * padding_needed
            aligned_text = ' ' * leading_spaces + row
            padding_needed = available_width - len(self.strip_ansi_escape_sequences(aligned_text))

            print(f"{vert_border_left}{aligned_text + ' ' * padding_needed}{vert_border_right}")



        if horiz_border_bottom:
            if not blank_line:
                blank_line = ' '.center(available_width) if vert_border_left and vert_border_right else ' '.center(self.horiz_width)
            print(f'{vert_border_left}{blank_line}{vert_border_right}')
            print(horiz_border_bottom)



    def print_border_boxed_tables2(self,
                                  table_strs,
                                  horiz_border_top,
                                  vert_border_left,
                                  vert_border_right,
                                  horiz_border_bottom,
                                  table_alignments=None,
                                  table_style=None,
                                  text_style=None):
        available_width = self.get_available_width()
        num_tables = len(table_strs)
        section_width = (available_width - (num_tables - 1)) // num_tables

        table_lines_list = [table_str.split("\n") for table_str in table_strs]
        max_lines = max(len(table_lines) for table_lines in table_lines_list)
        for table_lines in table_lines_list:
            table_lines += [''] * (max_lines - len(table_lines))

        if horiz_border_top:
            print(horiz_border_top)
            blank_line = ' '.center(available_width)
            print(f'{vert_border_left}{blank_line}{vert_border_right}')

        for line_index in range(max_lines):
            row = ""
            for table_index, table_lines in enumerate(table_lines_list):
                line = table_lines[line_index]
                stripped_line = self.strip_ansi_escape_sequences(line)
                padding_needed = section_width - len(stripped_line)
                if table_alignments and table_index < len(table_alignments):
                    text_align = table_alignments[table_index]
                else:
                    text_align = 'left'
                if text_align == 'center':
                    leading_spaces = padding_needed // 2
                    trailing_spaces = padding_needed - leading_spaces
                    aligned_line = ' ' * leading_spaces + line + ' ' * trailing_spaces
                elif text_align == 'left':
                    aligned_line = line + ' ' * padding_needed
                else:  # right align
                    aligned_line = ' ' * padding_needed + line
                if table_index > 0:
                    row += " "  # Padding between tables
                row += aligned_line
            row_length = len(self.strip_ansi_escape_sequences(row))
            padding_needed = available_width - row_length
            print(f"{vert_border_left}{row + ' ' * padding_needed}{vert_border_right}")

        if horiz_border_bottom:
            print(horiz_border_bottom)


    def print_border_boxed_tables4(self,
                                  table_strs,
                                  horiz_border_top,
                                  vert_border_left,
                                  vert_border_right,
                                  horiz_border_bottom,
                                  table_alignments=None,
                                  table_padding=4,
                                  table_style=None,
                                  text_style=None):
        available_width = self.get_available_width()
        num_tables = len(table_strs)
        section_width = (available_width - (num_tables - 1) * table_padding) // num_tables

        table_lines_list = [table_str.split("\n") for table_str in table_strs]
        max_lines = max(len(table_lines) for table_lines in table_lines_list)
        for table_lines in table_lines_list:
            table_lines += [''] * (max_lines - len(table_lines))

        for line_index in range(max_lines):
            row_parts = []
            for table_index, table_lines in enumerate(table_lines_list):
                line = table_lines[line_index]
                stripped_line = self.strip_ansi_escape_sequences(line)
                if table_alignments and table_index < len(table_alignments):
                    text_align = table_alignments[table_index]
                else:
                    text_align = 'left'

                aligned_line = self.align_text(line, section_width, text_align)
                row_parts.append(aligned_line)

            row = (' ' * table_padding).join(row_parts)
            row_length = len(self.strip_ansi_escape_sequences(row))
            padding_needed = available_width - row_length
            print(f"{vert_border_left}{row.ljust(available_width)}{vert_border_right}")







class ColorPrinterError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self,
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


def custom_excepthook_with_logging(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, ColorPrinterError):
        exc_value.handle_exception()
    else:
        logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

def set_custom_excepthook():
    sys.excepthook = custom_excepthook


def set_custom_excepthook_with_logging():
    sys.excepthook = custom_excepthook_with_logging







