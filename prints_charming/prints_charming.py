# prints_charming.py

import time
import os
import sys
import copy
import traceback
import re
import logging
import inspect
import ctypes
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from .logging_utils import logger



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
    reverse: bool = False
    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    overline: bool = False
    strikethru: bool = False
    conceal: bool = False
    blink: bool = False


    def update(self, attributes):
        for attr, value in attributes.items():
            if hasattr(self, attr):
                setattr(self, attr, value)



class PrintsCharmingLogHandler(logging.Handler):
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, pc: 'PrintsCharming' = None, styles: Dict[str, TextStyle] = None, timestamp_style: str = 'timestamp',
                 level_styles: Optional[Dict[str, str]] = None):
        super().__init__()
        self.pc = pc or PrintsCharming(styles=styles)
        self.timestamp_style = timestamp_style
        self.level_styles = level_styles or {
            'DEBUG': 'debug',
            'INFO': 'info',
            'WARNING': 'warning',
            'ERROR': 'error',
            'CRITICAL': 'critical'
        }
        self.pc.log_level_styles = self.level_styles

    def emit(self, record: logging.LogRecord):
        try:
            # Format the message using a custom method
            formatted_message = self.format_message(record.msg, record.args)

            # Pass the formatted message to the handle_log_event method
            self.handle_log_event(formatted_message, log_level=record.levelname)

        except Exception as e:
            self.handleError(record)
            print(f"Unexpected error during logging: {e}")

    def format_message(self, message: str, args):

        if args:
            try:
                message = message.format(*args)
            except (IndexError, KeyError, ValueError) as e:
                self.pc.logger.error(f"Error formatting log message: {e}")
                return message

        return message

    def handle_log_event(self, text: str, log_level: str):
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)

        log_level_style = self.level_styles.get(log_level, 'default')

        # Get styled components
        styled_log_level_prefix = self.pc.apply_logging_style(log_level_style, f"LOG[{log_level}]")
        styled_timestamp = self.pc.apply_logging_style(self.timestamp_style, timestamp)
        styled_level = self.pc.apply_logging_style(log_level_style, log_level)
        styled_text = self.pc.apply_logging_style(log_level_style, text)

        # Create the final styled message
        log_message = f"{styled_log_level_prefix} {styled_timestamp} {styled_level} - {styled_text}"

        print(log_message)




class PrintsCharming:
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
    RESET = "\033[0m"
    
    """
    This module provides a PrintsCharming class for handling colored text printing tasks.
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
        "internal_logging"    : False,
        "log_level"           : 'DEBUG',  # Default to DEBUG level
    }


    COLOR_MAP: Dict[str, str] = {
        "default": "\033[0m",
        "dfff": "\033[38;5;147m",
        "black": "\033[38;5;0m",
        "red": "\033[38;5;1m",
        "vred": "\033[38;5;196m",
        "green": "\033[38;5;34m",
        "vgreen": "\033[38;5;46m",
        "blue": "\033[38;5;4m",
        "vblue": "\033[38;5;27m",
        "sky": "\033[38;5;117m",
        "vsky": "\033[38;5;39m",
        "lmagenta": "\033[38;5;205m",
        "magenta": "\033[38;5;5m",
        "vmagenta": "\033[38;5;198m",
        "lav": "\033[38;5;183m",
        "lpurple": "\033[38;5;135m",
        "purple": "\033[38;5;129m",
        "dpurple": "\033[38;5;93m",
        "lplum": "\033[38;5;177m",
        "plum": "\033[38;5;128m",
        "vplum": "\033[38;5;201m",
        "lpink": "\033[38;5;218m",
        "pink": "\033[38;5;206m",
        "vpink": "\033[38;5;199m",
        "cyan": "\033[38;5;6m",
        "vcyan": "\033[38;5;51m",
        "orange": "\033[38;5;208m",
        "vorange": "\033[38;5;202m",
        "copper": "\033[38;5;166m",
        "yellow": "\033[38;5;3m",
        "vyellow": "\033[38;5;226m",
        "gold": "\033[38;5;220m",
        "brass": "\033[38;5;178m",
        "bronze": "\033[38;5;136m",
        "brown": "\033[38;5;94m",
        "sand": "\033[38;5;215m",
        "lbrown": "\033[38;5;138m",
        "silver": "\033[38;5;12m",
        "dsilver": "\033[38;5;10m",
        "gray": "\033[38;5;248m",
        "dgray": "\033[38;5;8m",
        "plat": "\033[38;5;252m",
        "white": "\033[38;5;15m",
        "vwhite": "\033[38;5;231m"
    }

    EFFECT_MAP: Dict[str, str] = {
        "reverse"      : "\033[7m",
        "bold"         : "\033[1m",
        "dim"          : "\033[2m",
        "italic"       : "\033[3m",
        "underline"    : "\033[4m",
        "overline"     : "\033[53m",
        "strikethru"   : "\033[9m",
        "conceal"      : "\033[8m",
        "blink"        : "\033[5m",

    }

    CONTROL_MAP: Dict[str, str] = {
        "clear_line": "\033[2K",
        "clear_screen": "\033[2J",
        "move_cursor_up": "\033[{n}A",
        "move_cursor_down": "\033[{n}B",
        "move_cursor_right": "\033[{n}C",
        "move_cursor_left": "\033[{n}D",
        "save_cursor_position": "\033[s",
        "restore_cursor_position": "\033[u",
    }

    STYLES: Dict[str, TextStyle] = {
        "default"      : TextStyle(),
        "top_level_label": TextStyle(bold=True, italic=True),
        "sub_level_label": TextStyle(color='sky'),
        "numbers"      : TextStyle(color="yellow"),
        'main_bullets' : TextStyle(color="purple"),
        "sub_bullets"  : TextStyle(color="pink"),
        "sub_proj"     : TextStyle(color="cyan"),
        "sub_bullet_title": TextStyle(color="orange"),
        "sub_bullet_sentence": TextStyle(color="vblue"),
        "default_bg"   : TextStyle(bg_color="black"),
        "white"        : TextStyle(color="white"),
        "gray"         : TextStyle(color="gray"),
        "dgray"        : TextStyle(color="dgray"),
        "black"        : TextStyle(color="black"),
        "green"        : TextStyle(color="green", bold=True),
        "vgreen"       : TextStyle(color="vgreen", bold=True),
        "log_true"     : TextStyle(color='vgreen'),
        "bg_color_green": TextStyle(color="white", bg_color='green'),
        "red"          : TextStyle(color="red"),
        "vred"         : TextStyle(color="vred", bold=True),
        "blue"         : TextStyle(color="blue"),
        "vblue"        : TextStyle(color="vblue"),
        "sky"          : TextStyle(color="sky"),
        "vsky"         : TextStyle(color="vsky"),
        "yellow"       : TextStyle(color="yellow"),
        "vyellow"      : TextStyle(color="vyellow"),
        "brass"        : TextStyle(color="brass"),
        "bronze"       : TextStyle(color="bronze"),
        "lbrown"       : TextStyle(color="lbrown"),
        "vorange"      : TextStyle(color="vorange"),
        "lplum"        : TextStyle(color="lplum"),
        "plum"         : TextStyle(color="plum"),
        "vplum"        : TextStyle(color="vplum"),
        "lmagenta"     : TextStyle(color="lmagenta"),
        "magenta"      : TextStyle(color="magenta", bold=True),
        "vmagenta"     : TextStyle(color="vmagenta"),
        "lpink"        : TextStyle(color="lpink"),
        "pink"         : TextStyle(color="pink",),
        "vpink"        : TextStyle(color="vpink"),
        "purple"       : TextStyle(color="purple"),
        "dpurple"      : TextStyle(color="dpurple"),
        "gold"         : TextStyle(color="gold"),
        "cyan"         : TextStyle(color="cyan"),
        "vcyan"        : TextStyle(color="vcyan"),
        "orange"       : TextStyle(color="orange"),
        "orangewhite"  : TextStyle(color="green", bg_color='dgray', underline=True),
        "copper"       : TextStyle(color="copper"),
        "brown"        : TextStyle(color="brown"),
        "sand"         : TextStyle(color="sand"),
        "lav"          : TextStyle(color="lav"),
        "lpurple"      : TextStyle(color="lpurple"),
        "plat"         : TextStyle(color="plat"),
        "silver"       : TextStyle(color="dfff", bg_color="dsilver"),
        "dfff"        : TextStyle(color="dfff", bg_color="purple", reverse=True),
        "vwhite"       : TextStyle(color="vwhite"),
        "header"       : TextStyle(color="vcyan"),
        "header_text"  : TextStyle(color="purple", bg_color="gray", bold=True, italic=True),
        "header_text2" : TextStyle(color="gray", bg_color="purple", bold=True),
        "task"         : TextStyle(color="blue", bold=True),
        "path"         : TextStyle(color="blue"),
        "filename"     : TextStyle(color="yellow"),
        "line_info"    : TextStyle(color="yellow", bold=True),
        "line_number"  : TextStyle(color="orange", bold=True),
        "function_name": TextStyle(color="yellow", italic=True),
        "error_message": TextStyle(color="vred", bold=True, dim=True),
        "code"         : TextStyle(color="yellow"),
        "dict_key": TextStyle(color="sky"),
        "dict_value": TextStyle(color="white"),
        "true": TextStyle(color="vgreen"),
        "false": TextStyle(color="vred"),
        'none': TextStyle(color="lpurple"),
        "int": TextStyle(color="cyan"),
        "float": TextStyle(color="vcyan"),
        "other": TextStyle(color="lav"),
        "conceal": TextStyle(conceal=True),
    }

    LOGGING_STYLES: Dict[str, TextStyle] = {
        "default": TextStyle(),
        "timestamp": TextStyle(color="white"),
        "class_name": TextStyle(color="dfff"),
        "method_name": TextStyle(color="lpurple"),
        "line_number": TextStyle(color="lav"),
        "debug": TextStyle(color="blue"),
        "info": TextStyle(color="green"),
        "warning": TextStyle(color="yellow"),
        "error": TextStyle(color="red"),
        "critical": TextStyle(color="vred"),
        "dict_key": TextStyle(color="sky"),
        "dict_value": TextStyle(color="white"),
        "true": TextStyle(color="vgreen"),
        "false": TextStyle(color="vred"),
        'none': TextStyle(color="lpurple"),
        "int": TextStyle(color="cyan"),
        "float": TextStyle(color="vcyan"),
        "other": TextStyle(color="lav"),
    }



    @classmethod
    def clear_line(cls, use_carriage_return: bool = True):
        if use_carriage_return:
            print("\r" + cls.CONTROL_MAP["clear_line"], end='')
        else:
            print(cls.CONTROL_MAP["clear_line"], end='')



    def __init__(self,
                 config: Optional[Dict[str, Union[bool, str, int]]] = None,
                 color_map: Optional[Dict[str, str]] = None,
                 bg_color_map: Optional[Dict[str, str]] = None,
                 effect_map: Optional[Dict[str, str]] = None,
                 styles: Optional[Dict[str, TextStyle]] = None,
                 printscharming_variables: Optional[Dict[str, List[str]]] = None,
                 style_conditions: Optional[Any] = None,
                 logging_styles: Optional[Dict[str, TextStyle]] = None,
                 autoconf_win: bool = False
                 ) -> None:

        """
        Initialize PrintsCharming with args to any of these optional parameters.

        :param config: enable or disable various functionalities of this class. Default is the PrintsCharming.CONFIG dictionary above
        :param color_map: supply your own color_map dictionary. Default is the PrintsCharming.COLOR_MAP dictionary above
        :param bg_color_map: supply your own bg_color_map dictionary. Default is computed from color_map dictionary
        :param effect_map: supply your own effect_map dictionary. Default is the PrintsCharming.EFFECT_MAP dictionary above
        :param styles: supply your own styles dictionary. Default is the PrintsCharming.STYLES dictionary above
        :param printscharming_variables: calls the add_variables_from_dict method with your provided dictionary. See README for more info.
        :param style_conditions: A custom class for implementing dynamic application of styles to text based on conditions.
        :param logging_styles: A separate dict for logging_styles.
        :param autoconf_win: If your using legacy windows cmd prompt and not getting colored/styled text then change this to True to make things work.
        """

        self.config = {**PrintsCharming.CONFIG, **(config or {})}

        self.color_map = color_map or PrintsCharming.COLOR_MAP.copy()
        self.color_map.setdefault('default', PrintsCharming.RESET)

        self.bg_color_map = bg_color_map or {
                color: self.compute_bg_color_map(code) for color, code in self.color_map.items()
            }

        self.effect_map = effect_map or PrintsCharming.EFFECT_MAP.copy()

        self.styles = styles or PrintsCharming.STYLES.copy()

        self.style_codes: Dict[str, str] = {
            name: self.create_style_code(style) for name, style in self.styles.items() if self.styles[name].color in self.color_map
        }

        self.logging_styles = logging_styles or PrintsCharming.LOGGING_STYLES.copy()

        self.logging_style_codes: Dict[str, str] = {
            name: self.create_style_code(style) for name, style in self.logging_styles.items() if self.logging_styles[name].color in self.color_map
        }

        self.reset = PrintsCharming.RESET


        self.variable_map: Dict[str, str] = {}
        self.word_map: Dict[str, Dict[str, str]] = {}
        self.phrase_map: Dict[str, Dict[str, str]] = {}
        self.conceal_map: Dict[str, Dict[str, str]] = {}
        self.substring_map = {}

        if printscharming_variables:
            self.add_variables_from_dict(printscharming_variables)

        self.style_conditions = style_conditions
        self.style_conditions_map = {}
        if style_conditions:
            self.style_conditions_map = style_conditions.map

        self.style_cache = {}

        if sys.platform == 'win32':
            if autoconf_win:
                self.enable_win_console_ansi_handling()
            else:
                self.win_utils = WinUtils

        # Setup logging
        self.logger = None
        self.setup_logging(self.config["internal_logging"], self.config["log_level"])





    @staticmethod
    def enable_win_console_ansi_handling():
        try:
            k32 = ctypes.windll.kernel32
            handle = k32.GetStdHandle(-11)
            ENABLE_PROCESSED_OUTPUT = 0x0001
            ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            mode = ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            if not k32.SetConsoleMode(handle, mode):
                logging.error("Failed to set console mode")
                return False
            logging.info(f"Console mode set to {mode}")
            return True
        except Exception as e:
            logging.error(f"Error enabling ANSI handling: {e}")
            return False



    def setup_logging(self, internal_logging: bool, log_level: str, log_format: str = '%(message)s'):
        self.logger = logger
        self.logger.propagate = False  # Prevent propagation to root logger
        if internal_logging:
            self.logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))
            if not self.logger.hasHandlers():
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter(log_format))
                self.logger.addHandler(console_handler)
                self.logger.disabled = False

            logging_enabled_init_message = f"Internal Logging Enabled:\n{self.print_dict(self.config)}"
            self.debug(logging_enabled_init_message)

        else:
            self.logger.disabled = True



    def update_logging(self, log_format: str = '%(message)s'):
        self.logger.handlers = []  # Clear existing handlers
        self.setup_logging(self.config["internal_logging"], self.config["log_level"], log_format)



    def log(self, level: str, message: str, *args, **kwargs) -> None:
        if not self.config['internal_logging']:
            return

        level = getattr(logging, level, None)

        if args:
            try:
                message = message.format(*args)
            except (IndexError, KeyError, ValueError) as e:
                self.logger.error(f"Error formatting log message: {e}")
                return

        if kwargs:
            message = message.format(**kwargs)

        timestamp = time.time()
        formatted_timestamp = datetime.fromtimestamp(timestamp).strftime(self.TIMESTAMP_FORMAT)

        timestamp_style = 'timestamp'

        level_styles = {
            10: 'debug',
            20: 'info',
            30: 'warning',
            40: 'error',
            50: 'critical',
        }

        log_level_style = level_styles.get(level, 'default')

        styled_log_level_prefix = self.apply_logging_style(log_level_style, f"LOG[{logging.getLevelName(level)}]")
        styled_timestamp = self.apply_logging_style(timestamp_style, formatted_timestamp)
        styled_level = self.apply_logging_style(log_level_style, logging.getLevelName(level))
        styled_text = self.apply_logging_style(log_level_style, message)

        log_message = f"{styled_log_level_prefix} {styled_timestamp} {styled_level} - {styled_text}"
        self.logger.log(level, log_message)


    def debug(self, message: str, *args, **kwargs) -> None:
        # Get the current stack frame
        current_frame = inspect.currentframe()
        # Get the caller frame
        caller_frame = current_frame.f_back
        # Extract the relevant information
        class_name = self.apply_logging_style('class_name', self.__class__.__name__)
        method_name = self.apply_logging_style('method_name', caller_frame.f_code.co_name)
        line_number = self.apply_logging_style('line_number', caller_frame.f_lineno)

        # Include the extracted information in the log message
        message = f"{class_name}.{method_name}:{line_number} - {message}"

        self.log('DEBUG', message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self.log('INFO', message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self.log('WARNING', message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self.log('ERROR', message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        self.log('CRITICAL', message, *args, **kwargs)


    def print_dict(self, d, indent=4):
        def pprint_dict(d, level=0):
            result = ""
            for key, value in d.items():
                result += " " * (level * indent) + self.apply_style('dict_key', f"{key}: ")
                if isinstance(value, dict):
                    result += "{\n" + pprint_dict(value, level + 1) + " " * (level * indent) + "}\n"
                elif isinstance(value, bool):
                    bool_style = 'true' if value else 'false'
                    result += self.apply_style(bool_style, str(value)) + "\n"
                elif value is None:
                    result += self.apply_style('none', str(value)) + "\n"
                elif isinstance(value, int):
                    result += self.apply_style('int', str(value)) + "\n"
                elif isinstance(value, float):
                    result += self.apply_style('float', str(value)) + "\n"
                elif isinstance(value, str) and value.isupper() and value.lower() in ['debug', 'info', 'warning', 'error', 'critical']:
                    result += self.apply_logging_style(value.lower(), str(value)) + "\n"

                else:
                    result += f"{value}\n"

            return result

        return "{\n" + pprint_dict(d) + "}"


    def escape_ansi_codes(self, ansi_string):
        self.debug("Escaping ANSI codes in string: {}", ansi_string)
        escaped_ansi_string = ansi_string.replace("\033", "\\033")
        #self.debug("Escaped ANSI codes in string: {}", escaped_ansi_string)
        return escaped_ansi_string


    def replace_and_style_placeholders(self,
                                       text: str,
                                       kwargs: Dict[str, Any],
                                       enable_label_style: bool = True,
                                       top_level_label: str = 'top_level_label',
                                       sub_level_label: str = 'sub_level_label',
                                       label_delimiter: str = ':',
                                       style_function: Callable[[str, Dict[str, Any]], str] = None,
                                       **style_kwargs) -> str:

        """Replace placeholders with actual values and apply colors."""
        self.debug("Replacing and styling placeholders in text: {} with kwargs: {}", text, kwargs)
        top_level_label_style_code = self.get_style_code(top_level_label) if enable_label_style else ''
        sub_level_label_style_code = self.get_style_code(sub_level_label) if enable_label_style else ''
        lines = text.split('\n')

        # Style labels directly in the text
        if enable_label_style:
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                # Handle standalone labels that end with ':'
                if stripped_line.endswith(label_delimiter):
                    label, _, rest = line.partition(label_delimiter)
                    lines[i] = f"{sub_level_label_style_code}{label}{label_delimiter}{self.reset}{rest}"
                # Handle inline labels followed by placeholders
                elif label_delimiter in line:
                    label, delimiter, rest = line.partition(label_delimiter)
                    if '{' in rest:
                        lines[i] = f"{top_level_label_style_code}{label}{delimiter}{self.reset}{rest}"

        styled_text = '\n'.join(lines)

        # Replace placeholders with actual values and apply styles
        for key, value in kwargs.items():
            styled_value = str(value)
            if key in self.style_conditions_map:
                style_name = self.style_conditions_map[key](value)
                style_code = self.get_style_code(style_name)
                styled_value = f"{style_code}{styled_value}{self.reset}"
            styled_text = styled_text.replace(f"{{{key}}}", styled_value)

        if not style_function:

            # Apply additional styles for bullets, numbers, and sentences
            lines = styled_text.split('\n')
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                leading_whitespace = line[:len(line) - len(stripped_line)]

                if stripped_line.startswith('- ') and not stripped_line.endswith(':'):
                    # Apply main bullet style
                    parts = stripped_line.split(' ', 1)
                    if len(parts) == 2:
                        lines[
                            i] = f"{leading_whitespace}{self.get_style_code('main_bullets')}{parts[0]} {self.reset}{self.get_style_code('main_bullet_text')}{parts[1]}{self.reset}"
                elif len(stripped_line) > 1 and stripped_line[0].isdigit() and stripped_line[1] == '.':
                    # Apply number and period style, followed by phrase style
                    parts = stripped_line.split('. ', 1)
                    if len(parts) == 2:
                        lines[i] = f"{leading_whitespace}{self.get_style_code('numbers')}{parts[0]}.{self.reset} {self.get_style_code('sub_proj')}{parts[1]}{self.reset}"
                elif stripped_line.startswith('- ') and stripped_line.endswith(':'):
                    # Apply sub-bullet style
                    parts = stripped_line.split(' ', 2)
                    if len(parts) == 3:
                        lines[i] = f"{leading_whitespace}{self.get_style_code('sub_bullets')}{parts[1]} {self.reset}{self.get_style_code('sub_bullet_text')}{parts[2]}{self.reset}"
                elif leading_whitespace.startswith('   '):
                    # Apply sub-bullet sentence style
                    words = stripped_line.split()
                    if len(words) > 1:
                        lines[
                            i] = f"{leading_whitespace}{self.get_style_code('sub_bullet_title')}{words[0]} {self.reset}{self.get_style_code('sub_bullet_sentence')}{' '.join(words[1:])}{self.reset}"

            styled_text = '\n'.join(lines)

        else:
            styled_text = style_function(styled_text, **style_kwargs)

        self.debug(f"Styled text: '{styled_text}'")

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
        self.debug("Printing background color: {} with length: {}", color_name, length)

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


    def apply_style(self, style_name, text, fill_space=True):
        #self.debug("Applying style_name: {} to text: {}", self.apply_logging_style('info', style_name), self.apply_logging_style('info', text))
        #self.debug("Applying style_name: %s to text: %s", self.apply_logging_style('info', style_name), self.apply_logging_style('info', text))
        if text.isspace() and fill_space:
            style_code = self.bg_color_map.get(
                style_name,
                self.bg_color_map.get(
                    self.styles.get(style_name, 'default_bg').bg_color
                )
            )

        else:
            style_code = self.style_codes.get(style_name, self.styles[style_name].color)

        # Append the style code at the beginning of the text and the reset code at the end
        styled_text = f"{style_code}{text}{self.reset}"

        #escaped_string = self.escape_ansi_codes(styled_text)
        #self.debug('escaped_string: {}', escaped_string)
        #self.debug(styled_text)

        return styled_text


    def apply_index_style(self, strs_list, styles_list, return_list=False):
        styled_strs = [self.apply_style(style, str(text)) for style, text in zip(styles_list, strs_list)]
        return ' '.join(styled_strs) if not return_list else styled_strs


    def apply_my_new_style_code(self, code, text):
        return f'{code}{text}{self.reset}'


    def get_logging_style_code(self, style_name):
        return self.logging_style_codes.get(style_name, self.style_codes['default'])


    def apply_logging_style(self, style_name, text):
        # This method does not log debug messages to avoid recursion

        if isinstance(text, str) and text.isspace():
            style_code = self.bg_color_map.get(
                style_name,
                self.bg_color_map.get(
                    self.styles.get(style_name, TextStyle(bg_color="default_bg")).bg_color
                )
            )
        else:
            style_code = self.logging_style_codes[style_name]

        # Append the style code at the beginning of the text and the reset code at the end
        styled_text = f"{style_code}{text}{self.reset}"

        return styled_text


    def get_color_code(self, color_name):
        return self.color_map.get(color_name, self.color_map['default'])


    def apply_color(self, color_name, text, fill_space=True):

        if text.isspace() and fill_space:
            color_code = self.bg_color_map.get(
                color_name,
                'default'
            )
        else:
            color_code = self.color_map[color_name]

        colored_text = f"{color_code}{text}{self.reset}"

        return colored_text


    def get_bg_color_code(self, color_name):
        return self.bg_color_map.get(color_name)


    def apply_bg_color(self, color_name, text):
        bg_color_code = self.bg_color_map.get(color_name)
        bg_color_block = f"{bg_color_code}{text}{self.reset}"

        return bg_color_block


    def add_substring(self, substr: str, style_name: str) -> None:
        substr = str(substr)
        if style_name in self.styles:

            attribs = vars(self.styles.get(style_name)).copy()
            if attribs.get('reversed'):
                attribs['color'], attribs['bg_color'] = attribs.get('bg_color'), attribs.get('color')

            self.substring_map[substr] = {
                "style": style_name,
                "style_code": self.style_codes[style_name],
                "attribs": attribs
            }
        else:
            print(f"Style {style_name} not found in styles dictionary.")


    def add_variable(self, variable: str, style_name: str) -> None:

        """
        Adds a variable with a specific style.
    
        :param variable: The variable to be styled.
        :param style_name: The name of the style to apply.
        """

        variable = str(variable)
        if style_name in self.styles:
            style_code = self.style_codes.get(style_name)
            styled_string = f"{style_code}{variable}{self.reset}"

            attribs = vars(self.styles.get(style_name)).copy()
            if attribs.get('reversed'):
                attribs['color'], attribs['bg_color'] = attribs.get('bg_color'), attribs.get('color')


            if style_name == 'conceal':
                self.conceal_map[variable] = {
                    "style": style_name,
                    "styled": styled_string
                }
            contains_inner_space = ' ' in variable.strip()
            if contains_inner_space:
                self.phrase_map[variable] = {
                    "style": style_name,
                    "style_code": style_code,
                    "styled": styled_string,
                    "attribs": attribs
                }
            else:
                self.word_map[variable] = {
                    "style" : style_name,
                    "style_code": style_code,
                    "styled": styled_string,
                    "attribs": attribs
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

    def style_spaces_by_index(self, text: str, style_mapping: Dict[Union[int, Tuple[int, int]], str], bg_only=True) -> str:
        # Process each character instead of words
        styled_text = list(text)

        for i, char in enumerate(styled_text, start=1):  # Start indexing from 1
            for key in style_mapping:
                style_name = style_mapping[key]
                style_code = self.style_codes[style_name] if not bg_only else self.bg_color_map[style_name]
                if isinstance(key, tuple):
                    start, end = key
                    if start <= i <= end and style_name in self.styles:  # Inclusive end
                        styled_text[i - 1] = f"{style_code}{char}{self.reset}"
                elif isinstance(key, int):
                    if not bg_only:
                        if key == i and style_name in self.styles:
                            styled_text[i - 1] = f"{style_code}{char}{self.reset}"
                    else:
                        if key == i and style_name in self.bg_color_map:
                            styled_text[i - 1] = f"{style_code}{char}{self.reset}"
        styled_spaces = "".join(styled_text)

        return styled_spaces


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

    @staticmethod
    def remove_ansi_codes(text):
        ansi_escape = re.compile(r'\033\[[0-9;]*[mK]')
        return ansi_escape.sub('', text)



    def print(self,
              *args: Any,
              text: str = None,
              var: Any = None,
              tstyle: str = None,
              vstyle: str = None,
              style: Union[None, str, Dict[Union[int, Tuple[int, int]], str]] = None,
              color: str = None,
              bg_color: str = None,
              reverse: bool = None,
              bold: bool = None,
              dim: bool = None,
              italic: bool = None,
              underline: bool = None,
              overline: bool = None,
              strikethru: bool = None,
              conceal: bool = None,
              blink: bool = None,
              sep: str = ' ',
              share_alike_sep_bg: bool = True,
              share_alike_sep_ul: bool = False,
              share_alike_sep_ol: bool = False,
              share_alike_sep_st: bool = False,
              share_alike_sep_bl: bool = False,
              end: str = '\n',
              filename: str = None,
              skip_ansi_check: bool = False,
              **kwargs: Any) -> None:


        print_start = time.perf_counter()

        converted_args = [str(arg) for arg in args] if self.config["args_to_strings"] else args


        # Handle not colored text
        if not self.config["color_text"]:
            output = sep.join(converted_args)

            # Remove ANSI codes if present
            if self.contains_ansi_codes(output):
                output = self.remove_ansi_codes(output)

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
        self.debug('<text>{}</text>', text)

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


        style_instance, style_code = (
            (self.styles.get(style, self.styles['default']), self.style_codes.get(style, self.style_codes['default'])) if style and isinstance(style, str)
            else (self.styles.get('default'), self.style_codes.get('default'))
        )

        if any((color is not None,
                bg_color is not None,
                reverse is not None,
                bold is not None,
                dim is not None,
                italic is not None,
                underline is not None,
                overline is not None,
                strikethru is not None,
                conceal is not None,
                blink is not None)):

            style_instance = copy.copy(style_instance)


            updated_style = {k: v for k, v in {
                'color': color,
                'bg_color': bg_color,
                'reverse': reverse,
                'bold': bold,
                'dim': dim,
                'italic': italic,
                'underline': underline,
                'overline': overline,
                'strikethru': strikethru,
                'conceal': conceal,
                'blink': blink,

            }.items() if v is not None}


            style_instance.update(updated_style)


            style_key = (
                style_instance.color,
                style_instance.bg_color,
                style_instance.reverse,
                style_instance.bold,
                style_instance.dim,
                style_instance.italic,
                style_instance.underline,
                style_instance.overline,
                style_instance.strikethru,
                style_instance.conceal,
                style_instance.blink,
            )

            # Check the cache for the style code
            cached_style_code = self.style_cache.get(style_key)
            if cached_style_code:
                style_code = cached_style_code
            else:
                # Cache the style code
                style_code = self.create_style_code(style_instance)
                self.style_cache[style_key] = style_code


        # Convert the text to a list of words and spaces
        words_and_spaces = re.findall(r'\S+|\s+', text)

        # Initialize list to hold the final styled words and spaces
        styled_words_and_spaces = [None] * len(words_and_spaces)


        # Initialize the lists to keep track of which indexes are used by what
        indexes_used_by_phrases = set()
        indexes_used_by_words = set()
        indexes_used_by_substrings = set()
        indexes_used_by_default_styling = set()
        indexes_used_by_spaces = set()
        indexes_used_by_none_styling = set()


        boundary_indices_dict = {}

        # Define sentence-ending characters
        sentence_ending_characters = ".,!?:;"


        # Step 1: Handle phrases
        for phrase, details in self.phrase_map.items():
            if phrase in text:
                styled_phrase = details.get('styled', phrase)

                # Split the styled_phrase into words and spaces
                styled_phrase_words_and_spaces = re.findall(r'\S+|\s+', styled_phrase)

                # Find the starting index of this phrase in the list of words_and_spaces
                for i in range(len(words_and_spaces) - len(styled_phrase_words_and_spaces) + 1):
                    if words_and_spaces[i:i + len(styled_phrase_words_and_spaces)] == re.findall(r'\S+|\s+', phrase):
                        # Update the indexes_used_by_phrases set
                        indexes_used_by_phrases.update(list(range(i, i + len(styled_phrase_words_and_spaces))))

                        # Add the index before the starting index
                        if i > 0:
                            if i - 1 not in boundary_indices_dict:
                                boundary_indices_dict[i - 1] = details.get('attribs')

                        # Add the index after the ending index
                        if i + len(styled_phrase_words_and_spaces) < len(words_and_spaces):
                            if i + len(styled_phrase_words_and_spaces) not in boundary_indices_dict:
                                boundary_indices_dict[i + len(styled_phrase_words_and_spaces)] = details.get('attribs')


                        # Update the styled_words_and_spaces list
                        for j, styled_word_or_space in enumerate(styled_phrase_words_and_spaces):
                            styled_words_and_spaces[i + j] = styled_word_or_space


        # Step 2: Handle individual words and substrings
        for i, word_or_space in enumerate(words_and_spaces):
            if i in indexes_used_by_phrases:
                continue
            if not word_or_space.isspace():
                word = word_or_space.strip()
                stripped_word = word.rstrip(sentence_ending_characters)
                trailing_chars = word[len(stripped_word):]


                # Check if the word is in the word_map
                if stripped_word in self.word_map:

                    if trailing_chars:
                        style_start = self.word_map.get(stripped_word, {}).get('style_code', '')
                        styled_word_or_space = f'{style_start}{word}{self.reset}'
                    else:
                        styled_word_or_space = self.word_map.get(stripped_word, {}).get('styled', stripped_word)

                    styled_words_and_spaces[i] = styled_word_or_space

                    # Add the index before the starting index
                    if i > 0:
                        if i - 1 not in boundary_indices_dict:
                            boundary_indices_dict[i - 1] = self.word_map.get(stripped_word, {}).get('attribs')

                    # Add the index after the ending index
                    if i + 1 < len(words_and_spaces):
                        if i + 1 not in boundary_indices_dict:
                            boundary_indices_dict[i + 1] = self.word_map.get(stripped_word, {}).get('attribs')

                    # Update the indexes_used_by_words set
                    indexes_used_by_words.add(i)


                else:
                    # Check if the word contains any substring in the substring_map
                    for substring, details in self.substring_map.items():
                        if substring in word:
                            style_start = details.get('style_code', '')
                            style_end = self.reset
                            styled_word_or_space = f"{style_start}{word_or_space}{style_end}"
                            styled_words_and_spaces[i] = styled_word_or_space

                            # Add the index before the starting index
                            if i > 0:
                                if i - 1 not in boundary_indices_dict:
                                    boundary_indices_dict[i - 1] = details.get('attribs')

                            # Add the index after the ending index
                            if i + 1 < len(words_and_spaces):
                                if i + 1 not in boundary_indices_dict:
                                    boundary_indices_dict[i + 1] = details.get('attribs')

                            indexes_used_by_substrings.add(i)

                            break  # Stop after the first matching substring



        # Step 3: Handle other styled text and spaces
        for i, word_or_space in enumerate(words_and_spaces):
            # Skip the index if it's used by a phrase or a word in the word_map
            if i in indexes_used_by_phrases or i in indexes_used_by_words or i in indexes_used_by_substrings:
                continue

            if word_or_space.isspace():
                indexes_used_by_spaces.add(i)
                if i not in boundary_indices_dict:
                    styled_word_or_space = f"{style_code}{word_or_space}{self.reset}"
                else:

                    style_instance_dict = asdict(style_instance)
                    keys_to_compare = ['color', 'bg_color']
                    if share_alike_sep_ul:
                        keys_to_compare.append('underline')
                    if share_alike_sep_ol:
                        keys_to_compare.append('overline')
                    if share_alike_sep_st:
                        keys_to_compare.append('strikethru')
                    if share_alike_sep_bl:
                        keys_to_compare.append('blink')

                    comparison_results = self.compare_dicts(boundary_indices_dict[i], style_instance_dict, keys_to_compare)


                    space_style_codes = []
                    if share_alike_sep_bg and comparison_results.get('bg_color'):
                        space_style_codes.append(self.bg_color_map.get(style_instance_dict.get('bg_color')))

                    if len(keys_to_compare) > 2:
                        if comparison_results.get('color'):
                            space_style_codes.append(self.color_map.get(style_instance_dict.get('color'), self.color_map.get(boundary_indices_dict[i].get('color', ''))))

                            for key in keys_to_compare[2:]:
                                if comparison_results.get(key):
                                    space_style_codes.append(self.effect_map.get(key, ''))

                    new_style_code = ''.join(space_style_codes)
                    styled_word_or_space = f'{new_style_code}{word_or_space}{self.reset}'


            else:
                indexes_used_by_default_styling.add(i)
                styled_word_or_space = f"{style_code}{word_or_space}{self.reset}"

            # Update the styled_words_and_spaces list
            styled_words_and_spaces[i] = styled_word_or_space


        # Step 4: Handle default styling for remaining words and spaces
        for i, styled_word_or_space in enumerate(styled_words_and_spaces):
            if styled_word_or_space is None:
                styled_words_and_spaces[i] = f"{style_code}{words_and_spaces[i]}{self.reset}"
                indexes_used_by_none_styling.add(i)


        # Step 5: Join the styled_words_and_spaces to form the final styled text
        styled_text = ''.join(filter(None, styled_words_and_spaces))

        # Print or write to file
        if filename:
            with open(filename, 'a') as file:
                file.write(styled_text + end)
        else:
            print(styled_text, end=end)


    def compare_dicts(self, dict1, dict2, keys):
        dict2 = self.apply_reverse_effect(dict2)

        results = {}
        for key in keys:
            if key in ['color', 'bg_color']:
                results[key] = dict1.get(key) == dict2.get(key) and dict1.get(key) is not None
            else:
                results[key] = dict1.get(key) == dict2.get(key) and dict1.get(key) is True
        return results


    def apply_reverse_effect(self, style_dict):
        if style_dict.get('reversed'):
            style_dict['color'], style_dict['bg_color'] = style_dict.get('bg_color'), style_dict.get('color')
        return style_dict



    def print_progress_bar(self, total_steps: int = 4, bar_symbol: str = ' ', bar_length: int = 40, color: str = 'vgreen'):
        for i in range(total_steps):
            progress = (i + 1) / total_steps
            block = int(bar_length * progress)
            if bar_symbol == ' ':
                bar_symbol = self.apply_bg_color(color, bar_symbol)
            bar = bar_symbol * block + "-" * (bar_length - block)
            time.sleep(1)
            self.clear_line()
            self.print(f"Progress: |{bar}| {int(progress * 100)}%", end='', color=color)
            sys.stdout.flush()
            time.sleep(0.25)  # Simulate work



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


def get_default_printer() -> Any:
    p = PrintsCharming()
    return p.print




class TableManager:
    def __init__(self, cp: PrintsCharming = None, style_themes: dict = None, conditional_styles: dict = None):
        self.cp = cp or PrintsCharming()
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
                       double_space: bool = False,
                       use_styles=True
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

        if use_styles:
            styled_col_sep = self.cp.apply_style(col_sep_style, col_sep) if col_sep_style else col_sep
        else:
            styled_col_sep = self.cp.apply_color(col_sep_style, col_sep) if col_sep_style else col_sep

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
    def __init__(self, cp=None, horiz_width=None, horiz_char=' ', vert_width=None, vert_padding=1, vert_char='|'):
        self.cp = cp if cp else PrintsCharming()
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


    def split_text_to_lines_v2(self, text, available_width):
        lines = text.split('\n')
        split_lines = []
        for line in lines:
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 <= available_width:
                    if current_line:
                        current_line += " "
                    current_line += word
                else:
                    split_lines.append(current_line)
                    current_line = word
            if current_line:
                split_lines.append(current_line)
        return split_lines


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
        return self.horiz_width - (2 * self.vert_width) - (len(self.vert_padding) * 2) if self.vert_border else self.horiz_width - (len(self.vert_padding) * 2)

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


    def build_styled_border_box(self, horiz_border_top=True, horiz_border_top_style=None,
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



    def print_border_boxed_text(self, text, text_style=None, text_align='center',
                                subtext='', subtext_style=None, subtext_align='center',
                                horiz_border_top=True, horiz_border_top_style=None,
                                horiz_border_bottom=True, horiz_border_bottom_style=None,
                                text_vert_border_l_style=None, text_vert_border_r_style=None,
                                subtext_vert_border_l_style=None, subtext_vert_border_r_style=None,
                                first_line_blank=False):

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
                                 table_strs_vert_border_left=True,
                                 table_strs_vert_border_right=True,
                                 default_table_alignment='center',
                                 horiz_border_double=False):

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
            print(horiz_border_top * 2) if horiz_border_double else print(horiz_border_top)

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
            print(horiz_border_bottom * 2) if horiz_border_double else print(horiz_border_bottom)
            blank_text = ' '.center(available_width)
            print(f'{vert_border_left}{blank_text}{vert_border_right}')


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



    def print_multi_column_box(self, columns, col_widths, col_styles=None, col_alignments=None,
                               horiz_border_top=True, horiz_border_bottom=True,
                               vert_border_left=True, vert_border_right=True):
        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        total_col_width = sum(col_widths)
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.cp.apply_style('purple', self.horiz_border)
        vert_border = self.cp.apply_style('orange', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        # Split each column's text into lines
        col_lines = [self.split_text_to_lines(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        # Print each row of columns
        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = col_alignments[col_num] if col_alignments else 'center'
                if line_num < len(col_lines[col_num]):
                    line = col_lines[col_num][line_num]
                    aligned_text = self.cp.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align))
                else:
                    aligned_text = self.cp.apply_style(col_style, ' ' * col_widths[col_num])
                row.append(aligned_text)
            if vert_border_left and vert_border_right:
                print(f"{vert_border}{' '.join(row)}{vert_border}")
            elif vert_border_left:
                print(f"{vert_border}{' '.join(row)}")
            elif vert_border_right:
                print(f"{' '.join(row)}{vert_border}")
            else:
                print(' '.join(row))

        if horiz_border_bottom:
            print(horiz_border)


    def print_multi_column_box2(self, columns, col_widths, col_styles=None, col_alignments=None,
                               horiz_border_top=True, horiz_border_bottom=True,
                               vert_border_left=True, vert_border_right=True, col_sep=None,
                                col_widths_percent=False):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        #print(f'horiz_width: {self.horiz_width}')
        #print(f'available_width: {available_width}')
        #total_padding = sig_columns + len(self.vert_padding) * sig_columns
        #total_padding = sig_columns + len(self.vert_padding) * sig_columns + sig_columns
        #total_padding = sig_columns + len(self.vert_padding) * sig_columns + sig_columns
        num_columns = len(columns)
        sig_columns = num_columns - 1
        #total_padding = sig_columns * (len(self.vert_padding) + 2)
        total_padding = sig_columns * (len(self.vert_padding) * 3)
        #print(f'total_padding: {total_padding}')

        if col_widths_percent:
            # Convert percentages to absolute widths
            col_widths = [int(available_width * (w / 100)) if w != '' else '' for w in col_widths]


        if '' in col_widths:
            unspecified_index = col_widths.index('')
            specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index)
            #print(f'specified_width: {specified_width}')
            remaining_width = available_width - specified_width - total_padding
            #print(f'remaining_width: {remaining_width}')
            #col_widths[unspecified_index] = remaining_width - len(self.vert_padding) * 2
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        #print(f'total_col_width: {total_col_width}')
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.cp.apply_style('purple', self.horiz_border)
        vert_border = self.cp.apply_style('orange', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        # Split each column's text into lines
        col_lines = [self.split_text_to_lines_v2(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        # Print each row of columns
        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = col_alignments[col_num] if col_alignments else 'center'
                if line_num < len(col_lines[col_num]):
                    line = col_lines[col_num][line_num]
                    aligned_text = self.cp.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                    #aligned_text = self.align_text(line, col_widths[col_num], col_align)
                    #styled_text = self.cp.apply_style(col_style, aligned_text.strip())
                    #final_text = styled_text + ' ' * (col_widths[col_num] - len(aligned_text.strip()))
                else:
                    aligned_text = self.cp.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
                    #final_text = ' ' * col_widths[col_num]
                row.append(aligned_text)
                #row.append(final_text)
            row_text = f"{self.vert_padding}{col_sep}{self.vert_padding}".join(row)
            if vert_border_left and vert_border_right:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            elif vert_border_left:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}")
            elif vert_border_right:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            else:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}")

        if horiz_border_bottom:
            print(horiz_border)


    def print_multi_column_box3(self, columns, col_widths, col_styles=None, col_alignments=None,
                                horiz_border_top=True, horiz_border_bottom=True,
                                vert_border_left=True, vert_border_right=True, col_sep=None,
                                col_widths_percent=False):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        #print(f'horiz_width: {self.horiz_width}')
        #print(f'available_width: {available_width}')
        num_columns = len(columns)
        sig_columns = num_columns - 1
        total_padding = sig_columns * (len(self.vert_padding) * 3)
        #print(f'total_padding: {total_padding}')

        if col_widths_percent:
            # Convert percentages to absolute widths
            col_widths = [int(available_width * (w / 100)) if w != '' else '' for w in col_widths]

        if '' in col_widths:
            unspecified_index = col_widths.index('')
            specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index and col_widths[i] != '')
            #print(f'specified_width: {specified_width}')
            remaining_width = available_width - specified_width - total_padding
            #print(f'remaining_width: {remaining_width}')
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        #print(f'total_col_width: {total_col_width}')
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.cp.apply_style('purple', self.horiz_border)
        vert_border = self.cp.apply_style('orange', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        # Split each column's text into lines
        col_lines = [self.split_text_to_lines_v2(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        # Print each row of columns
        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = col_alignments[col_num] if col_alignments else 'center'
                if line_num < len(col_lines[col_num]):
                    line = col_lines[col_num][line_num]
                    aligned_text = self.cp.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                else:
                    aligned_text = self.cp.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
                row.append(aligned_text)
            row_text = f"{self.vert_padding}{col_sep}{self.vert_padding}".join(row)
            if vert_border_left and vert_border_right:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            elif vert_border_left:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}")
            elif vert_border_right:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            else:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}")

        if horiz_border_bottom:
            print(horiz_border)


    def print_multi_column_box4(self, columns, col_widths, col_styles=None, col_alignments=None,
                                horiz_border_top=True, horiz_border_bottom=True,
                                vert_border_left=True, vert_border_right=True, col_sep=None,
                                col_sep_width=1):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        #print(f'horiz_width: {self.horiz_width}')
        #print(f'available_width: {available_width}')

        num_columns = len(columns)
        sig_columns = num_columns - 1
        col_sep_length = len(col_sep) * col_sep_width
        col_sep = col_sep * col_sep_width
        #total_padding = (sig_columns * col_sep_length) * (len(self.vert_padding) * 3)
        total_padding = (sig_columns * len(col_sep) * (len(self.vert_padding) * 2))
        #print(f'total_padding: {total_padding}')

        if '' in col_widths:
            unspecified_index = col_widths.index('')
            specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index)
            #print(f'specified_width: {specified_width}')
            remaining_width = available_width - specified_width - total_padding
            #print(f'remaining_width: {remaining_width}')
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        #print(f'total_col_width: {total_col_width}')
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.cp.apply_style('purple', self.horiz_border)
        vert_border = self.cp.apply_style('orange', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        col_lines = [self.split_text_to_lines_v2(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = col_alignments[col_num] if col_alignments else 'center'
                if line_num < len(col_lines[col_num]):
                    line = col_lines[col_num][line_num]
                    aligned_text = self.cp.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                else:
                    aligned_text = self.cp.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
                row.append(aligned_text)
            row_text = f"{self.vert_padding}{col_sep * col_sep_width}{self.vert_padding}".join(row)
            if vert_border_left and vert_border_right:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            elif vert_border_left:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}")
            elif vert_border_right:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            else:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}")

        if horiz_border_bottom:
            print(horiz_border)


class PrintsCharmingError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self,
                 message: str,
                 cp: 'PrintsCharming',
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
        subclass_names_with_colon = list(get_all_subclass_names(PrintsCharmingError, trailing_char=':'))

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


class ColorNotFoundError(PrintsCharmingError):
    """Exception raised when a color is not found in the color map."""
    pass


class InvalidLengthError(PrintsCharmingError):
    """Exception raised when an invalid length is provided."""
    pass


class UnsupportedEffectError(PrintsCharmingError):
    """Exception raised when an unsupported effect is requested."""
    pass


# Define the global exception hook
def custom_excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, PrintsCharmingError):
        exc_value.handle_exception()
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def custom_excepthook_with_logging(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, PrintsCharmingError):
        exc_value.handle_exception()
    else:
        logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def set_custom_excepthook():
    sys.excepthook = custom_excepthook



def set_custom_excepthook_with_logging():
    sys.excepthook = custom_excepthook_with_logging





class WinUtils:
    # Constants for handle types
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    # Console mode flags
    ENABLE_PROCESSED_OUTPUT = 0x0001
    ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

    @staticmethod
    def enable_win_console_ansi_handling(handle_type=-11, mode=None):
        """
        Enables ANSI escape code handling for the specified console handle.

        Parameters:
        handle_type (int): The type of console handle (-10: stdin, -11: stdout, -12: stderr).
        mode (int): Custom mode flags to set. If None, the default mode enabling ANSI will be used.
        """
        try:
            k32 = ctypes.windll.kernel32

            # Get the console handle
            handle = k32.GetStdHandle(handle_type)

            # Save the original console mode
            original_mode = ctypes.c_uint32()
            if not k32.GetConsoleMode(handle, ctypes.byref(original_mode)):
                logging.error("Failed to get original console mode")
                return False

            if mode is None:
                # Default mode enabling ANSI escape code handling
                mode = (WinUtils.ENABLE_PROCESSED_OUTPUT |
                        WinUtils.ENABLE_WRAP_AT_EOL_OUTPUT |
                        WinUtils.ENABLE_VIRTUAL_TERMINAL_PROCESSING)

            # Set the new console mode
            if not k32.SetConsoleMode(handle, mode):
                logging.error("Failed to set console mode")
                return False

            logging.info(f"Console mode set to {mode}")
            return True
        except Exception as e:
            logging.error(f"Error enabling ANSI handling: {e}")
            return False

    @staticmethod
    def restore_console_mode(handle_type=-11):
        """
        Restores the original console mode for the specified console handle.

        Parameters:
        handle_type (int): The type of console handle (-10: stdin, -11: stdout, -12: stderr).
        """
        try:
            k32 = ctypes.windll.kernel32

            # Get the console handle
            handle = k32.GetStdHandle(handle_type)

            # Restore the original console mode
            original_mode = ctypes.c_uint32()
            if not k32.GetConsoleMode(handle, ctypes.byref(original_mode)):
                logging.error("Failed to get original console mode")
                return False

            if not k32.SetConsoleMode(handle, original_mode.value):
                logging.error("Failed to restore console mode")
                return False

            logging.info("Original console mode restored")
            return True
        except Exception as e:
            logging.error(f"Error restoring console mode: {e}")
            return False







