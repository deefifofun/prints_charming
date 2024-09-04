# prints_charming.py

import time
import os
import sys
import copy
import traceback
import re
import logging
import inspect
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from .logging_utils import logger
from .prints_charming_defaults import DEFAULT_CONFIG, DEFAULT_COLOR_MAP, DEFAULT_EFFECT_MAP, DEFAULT_STYLES, DEFAULT_LOGGING_STYLES
from .prints_style import PrintsStyle
if sys.platform == 'win32':
    from .win_utils import WinUtils






def get_terminal_width():
    terminal_size = os.get_terminal_size()
    return terminal_size.columns


def get_all_subclass_names(cls, trailing_char=None):
    subclasses = set(cls.__subclasses__())
    result = {subclass.__name__ + (trailing_char or '') for subclass in subclasses}
    for subclass in subclasses.copy():
        result.update(get_all_subclass_names(subclass, trailing_char))
    return result



# Marked for removal soon!
# Use from prints_charming.logging import CustomFormatter, CustomLogHandler.
# Check prints_charming.examples.main for examples.
class PrintsCharmingLogHandler(logging.Handler):
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, pc: 'PrintsCharming' = None, styles: Dict[str, PrintsStyle] = None, timestamp_style: str = 'timestamp',
                 level_styles: Optional[Dict[str, str]] = None, timestamp_format: str = None):
        super().__init__()
        self.pc = pc or PrintsCharming(styles=styles if styles else DEFAULT_LOGGING_STYLES.copy())
        self.apply_style = self.pc.apply_style
        self.timestamp_style = timestamp_style
        self.level_styles = level_styles or {
            'DEBUG': 'debug',
            'INFO': 'info',
            'WARNING': 'warning',
            'ERROR': 'error',
            'CRITICAL': 'critical'
        }
        self.pc.log_level_styles = self.level_styles
        self.timestamp_format = timestamp_format or self.TIMESTAMP_FORMAT

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
        timestamp = datetime.now().strftime(self.timestamp_format)

        log_level_style = self.level_styles.get(log_level, 'default')

        # Get styled components
        styled_log_level_prefix = self.apply_style(log_level_style, f"LOG[{log_level}]")
        styled_timestamp = self.apply_style(self.timestamp_style, timestamp)
        styled_level = self.apply_style(log_level_style, log_level)
        styled_text = self.apply_style(log_level_style, text)

        # Create the final styled message
        log_message = f"{styled_log_level_prefix} {styled_timestamp} {styled_level} - {styled_text}"

        print(log_message)




class PrintsCharming:
    RESET = "\033[0m"
    _TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'



    """
    This module provides a PrintsCharming class for handling colored text printing tasks.
    It also includes PrintsStyle, a dataclass for managing text styles. In the COLOR_MAP "v" before a color stands for "vibrant".

    Note: This module is developed and tested on Linux and is intended for use in Linux terminals.

    Optional Feature: The `set_shared_maps` class method allows for shared configurations across all instances, 
    but it is entirely optional. If you do not need shared configurations, you can skip this method and proceed 
    with individual instance configurations.

    """

    # These maps are optionally available to be shared between all instances of the class if the set_shared_maps classmethod is called.
    shared_color_map: Optional[Dict[str, str]] = None
    shared_bg_color_map: Optional[Dict[str, str]] = None
    shared_effect_map: Optional[Dict[str, str]] = DEFAULT_EFFECT_MAP
    shared_styles: Optional[Dict[str, PrintsStyle]] = None
    shared_logging_styles: Optional[Dict[str, PrintsStyle]] = None
    shared_internal_logging_styles: Optional[Dict[str, PrintsStyle]] = DEFAULT_LOGGING_STYLES.copy()

    # This method is entirely optional and not required for the usage of the PrintsCharming class.
    @classmethod
    def set_shared_maps(cls,
                        shared_color_map: Optional[Dict[str, str]] = None,
                        shared_bg_color_map: Optional[Dict[str, str]] = None,
                        shared_effect_map: Optional[Dict[str, str]] = None,
                        shared_styles: Optional[Dict[str, PrintsStyle]] = None,
                        shared_logging_styles: Optional[Dict[str, PrintsStyle]] = None):
        """
        Set shared maps across all instances of the PrintsCharming class.

        **Purpose:**
        The `set_shared_maps` method allows you to define shared configurations that are accessible by all instances of the
        PrintsCharming class. This method lets you establish a consistent set of color maps, styles, and effects that will be
        applied uniformly across all instances unless specifically overridden. This behavior is similar to having default
        configurations that other libraries might hardcode, but with the added flexibility that you can modify these shared
        configurations at runtime.

        **Flexibility & Power:**
        While this method allows you to set shared configurations that apply to all instances—similar to class-level
        defaults—PrintsCharming’s true strength lies in its flexibility. Unlike many similar libraries with rigid,
        predefined constants, PrintsCharming offers the freedom to configure each instance individually. This approach
        gives you the power to either enforce consistency across all instances or tailor the behavior and styling of text
        printing according to the specific needs of your application.

        **When to Use This Method:**
        - If you have a scenario where consistent styling or configurations are required across all instances, using
          `set_shared_maps` can be very powerful.
        - For many other cases, where instance-specific customization is more appropriate, you can skip this method
          altogether and rely on individual configurations for each instance.

        **Important Considerations:**
        - This method is an option, not a requirement. Use it when it makes sense for your project.
        - Shared maps set through this method will be applied to all future instances unless overridden in the instance's
          `__init__` method.

        **Parameters:**
        :param shared_color_map: (Optional) A dictionary of shared color mappings to be accessible globally across
                                 all instances. If not provided, `DEFAULT_COLOR_MAP.copy()` will be used.
        :param shared_bg_color_map: (Optional) A dictionary of shared background color mappings. to be accessible globally across
                                    all instances. If None (as it should be unless your really know what your doing), it will be computed
                                    from shared_color_map.
        :param shared_effect_map: (Optional) A dictionary of effect mappings.
                                  **This should not be changed unless you are certain of what you're doing.**
        :param shared_styles: (Optional) A dictionary of shared styles. This allows for the consistent application
                              of text styles across all instances.
        :param shared_logging_styles: (Optional) A dictionary of shared logging styles, useful for ensuring uniform
                                      logging output across instances.
        """

        # Setting the shared maps to be used globally across instances
        cls.shared_color_map = shared_color_map or DEFAULT_COLOR_MAP.copy()
        cls.shared_color_map.setdefault('default', PrintsCharming.RESET)
        cls.shared_bg_color_map = shared_bg_color_map or {
            color: PrintsCharming.compute_bg_color_map(code) for color, code in cls.shared_color_map.items()
        }

        if shared_effect_map:
            cls.shared_effect_map = shared_effect_map

        if shared_styles:
            cls.shared_styles = shared_styles

        if shared_logging_styles:
            cls.shared_logging_styles = shared_logging_styles




    CONTROL_MAP: Dict[str, str] = {
        "alt_buffer": "\033[?1049h",
        "normal_buffer": "\033[?1049l",
        "alt_buffer_no_save": "\033[?47h",  # Switch to alternate buffer without saving the cursor
        "normal_buffer_no_save": "\033[?47l",  # Switch back to normal buffer without restoring the cursor
        "clear_line": "\033[2K",
        "clear_screen": "\033[2J",
        "cursor_position": "\033[{row};{col}H",
        "cursor_home": "\033[H",  # Move cursor to the home position (top-left corner)
        "move_cursor_up": "\033[{n}A",
        "move_cursor_down": "\033[{n}B",
        "move_cursor_right": "\033[{n}C",
        "move_cursor_left": "\033[{n}D",
        "save_cursor_position": "\033[s",
        "restore_cursor_position": "\033[u",
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
                 styles: Optional[Dict[str, PrintsStyle]] = None,
                 styled_strings: Optional[Dict[str, List[str]]] = None,
                 style_conditions: Optional[Any] = None,
                 logging_styles: Optional[Dict[str, PrintsStyle]] = None,
                 autoconf_win: bool = False
                 ) -> None:

        """
        Initialize PrintsCharming with args to any of these optional parameters.

        :param config: enable or disable various functionalities of this class.
        :param color_map: supply your own color_map dictionary. 'color_name': 'ansi_code'
        :param bg_color_map: supply your own bg_color_map dictionary. Default is computed from color_map dictionary
        :param effect_map: supply your own effect_map dictionary. Default is the PrintsCharming.EFFECT_MAP dictionary above
        :param styles: supply your own styles dictionary. Default is a copy of the DEFAULT_STYLES dictionary unless cls.shared_styles is defined.
        :param printscharming_variables: calls the add_variables_from_dict method with your provided dictionary. See README for more info.
        :param style_conditions: A custom class for implementing dynamic application of styles to text based on conditions.
        :param logging_styles: A separate dict for logging_styles.
        :param autoconf_win: If your using legacy windows cmd prompt and not getting colored/styled text then change this to True to make things work.
        """

        self.config = {**DEFAULT_CONFIG, **(config or {})}

        # Set self.color_map based on the provided arguments and class-level settings
        self.color_map = color_map or PrintsCharming.shared_color_map or DEFAULT_COLOR_MAP.copy()
        self.color_map.setdefault('default', PrintsCharming.RESET)

        # Set self.bg_color_map based on the provided arguments and class-level settings
        self.bg_color_map = bg_color_map or PrintsCharming.shared_bg_color_map or {
                    color: PrintsCharming.compute_bg_color_map(code) for color, code in self.color_map.items()
                }

        self.effect_map = effect_map or PrintsCharming.shared_effect_map

        self.styles = styles or PrintsCharming.shared_styles or DEFAULT_STYLES.copy()

        self.style_codes: Dict[str, str] = {
            name: self.create_style_code(style) for name, style in self.styles.items() if self.styles[name].color in self.color_map
        }

        self.logging_styles = logging_styles or PrintsCharming.shared_logging_styles or DEFAULT_LOGGING_STYLES.copy()


        self.logging_style_codes: Dict[str, str] = {
            name: self.create_style_code(style) for name, style in self.logging_styles.items() if self.logging_styles[name].color in self.color_map
        }

        self.reset = PrintsCharming.RESET

        self.conceal_map: Dict[str, Dict[str, str]] = {}
        self.styled_phrase_map: Dict[str, Dict[str, str]] = {}
        self.styled_word_map: Dict[str, Dict[str, str]] = {}
        self.styled_substring_map: Dict[str, Dict[str, str]] = {}
        self.styled_variable_map: Dict[str, str] = {}

        self.enable_conceal_map = False
        self.enable_styled_phrase_map = False
        self.enable_styled_word_map = False
        self.enable_styled_substring_map = False
        self.enable_styled_variable_map = False


        if styled_strings:
            self.add_strings_from_dict(styled_strings)

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
            import ctypes
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
        formatted_timestamp = datetime.fromtimestamp(timestamp).strftime(self._TIMESTAMP_FORMAT)

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


    @staticmethod
    def compute_bg_color_map(code):
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



    def create_style_code(self, style: Union[PrintsStyle, Dict[str, Any]]):
        style_codes = []

        if isinstance(style, PrintsStyle):
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


    def add_style(self, name: str, style: PrintsStyle):
        self.styles[name] = style
        if self.styles[name].color in self.color_map:
            style_code = self.create_style_code(self.styles[name])
            self.style_codes[name] = style_code


    def add_styles(self, styles: dict[str, PrintsStyle]) -> None:
        for style_name, style in styles.items():
            if style.color in self.color_map:
                self.add_style(style_name, style)


    def get_style_code(self, style_name):
        return self.style_codes.get(style_name, self.style_codes['default'])


    def apply_style(self, style_name, text, fill_space=True, reset=True):
        #self.debug("Applying style_name: {} to text: {}", self.apply_logging_style('info', style_name), self.apply_logging_style('info', text))
        #self.debug("Applying style_name: %s to text: %s", self.apply_logging_style('info', style_name), self.apply_logging_style('info', text))
        text = str(text)
        if text.isspace() and fill_space:
            style_code = self.bg_color_map.get(
                style_name,
                self.bg_color_map.get(
                    self.styles.get(style_name, 'default_bg').bg_color
                )
            )

        else:
            style_code = self.style_codes.get(style_name, self.color_map.get(style_name, self.color_map.get('default')))

        # Append the style code at the beginning of the text and the reset code at the end
        styled_text = f"{style_code}{text}{self.reset if reset else ''}"

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
                    self.styles.get(style_name, PrintsStyle(bg_color="default_bg")).bg_color
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

        text = str(text)
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
        bg_color_code = self.get_bg_color_code(color_name)
        bg_color_block = f"{bg_color_code}{text}{self.reset}"

        return bg_color_block


    def add_substring(self, substring: str, style_name: str) -> None:
        substring = str(substring)
        if style_name in self.styles:

            attribs = vars(self.styles.get(style_name)).copy()
            if attribs.get('reversed'):
                attribs['color'], attribs['bg_color'] = attribs.get('bg_color'), attribs.get('color')

            self.styled_substring_map[substring] = {
                "style": style_name,
                "style_code": self.style_codes[style_name],
                "attribs": attribs
            }
        else:
            print(f"Style {style_name} not found in styles dictionary.")


    def add_string(self, string: str, style_name: str) -> None:
        """
                Adds a string to the styled_string_map with a specific style.

                :param string: The string to be styled.
                :param style_name: The name of the style to apply.
                """

        string = str(string)
        if style_name in self.styles:
            style_code = self.get_style_code(style_name)
            styled_string = f"{style_code}{string}{self.reset}"

            attribs = vars(self.styles.get(style_name)).copy()
            if attribs.get('reversed'):
                attribs['color'], attribs['bg_color'] = attribs.get('bg_color'), attribs.get('color')

            if style_name == 'conceal':
                self.conceal_map[string] = {
                    "style": style_name,
                    "styled": styled_string
                }
                if not self.enable_conceal_map:
                    self.enable_conceal_map = True

            contains_inner_space = ' ' in string.strip()
            if contains_inner_space:
                self.styled_phrase_map[string] = {
                    "style": style_name,
                    "style_code": style_code,
                    "styled": styled_string,
                    "attribs": attribs
                }
                if not self.enable_styled_phrase_map:
                    self.enable_styled_phrase_map = True

            else:
                self.styled_word_map[string] = {
                    "style": style_name,
                    "style_code": style_code,
                    "styled": styled_string,
                    "attribs": attribs
                }
                if not self.enable_styled_word_map:
                    self.enable_styled_word_map = True
        else:
            print(f"Style {style_name} not found in styles dictionary.")


    def add_strings(self, strings: List[str], style_name: str) -> None:
        if style_name in self.styles:
            style_code = self.style_codes[style_name]
            for string in strings:
                self.add_string(string, style_name)


    def add_strings_from_dict(self, strings_dict: Dict[str, List[str]]) -> None:
        for style_name, strings in strings_dict.items():
            if style_name in self.styles:
                self.add_strings(strings, style_name)
            else:
                print(f"Style {style_name} not found in styles dictionary.")


    def remove_string(self, string: str) -> None:
        if string in self.styled_word_map:
            del self.styled_word_map[string]
        if string in self.styled_phrase_map:
            del self.styled_phrase_map[string]
        elif string in self.conceal_map[string]:
            del self.conceal_map[string]


    def conceal_text(self, text_to_conceal, replace=False, style_name=None):
        if replace:
            style_code = self.get_style_code(style_name)
            if not style_code:
                style_code = self.style_codes.get('default')
            concealed_text = f"{style_code}***concealed_text***{self.reset}"
        else:
            style_code = self.style_codes.get('conceal')
            if not style_code:
                style_code = PrintsCharming.shared_effect_map.get('conceal')
            concealed_text = f"{style_code}{text_to_conceal}{self.reset}"

        return concealed_text



    def print_variables(self, text: str, text_style: str = None, **kwargs) -> None:
        # Apply styles to each variable in kwargs
        for key, value in kwargs.items():
            variable, var_style = value
            styled_var = f"{self.style_codes[var_style]}{str(variable)}{self.reset}"
            kwargs[key] = styled_var

        # Replace placeholders with styled variables
        text = text.format(**kwargs)

        self.print(text, style=text_style, skip_ansi_check=True)



    def segment_with_splitter_and_style(self, text: str, splitter_match: str, splitter_swap: Union[str, bool], splitter_show: bool, splitter_style: Union[str, List[str]], splitter_arms: bool, string_style: List[str]) -> str:
        if isinstance(splitter_style, str):
            splitter_styles = [splitter_style]
        else:
            splitter_styles = splitter_style

        # Determine the actual splitter to use
        actual_splitter = splitter_swap if splitter_swap else splitter_match

        # Split the text based on the splitter_match
        segments = text.split(splitter_match)
        styled_segments = []

        for i, segment in enumerate(segments):
            # Apply string style to the segment
            segment_style = string_style[i % len(string_style)] if string_style else 'default'
            styled_segment = f"{self.style_codes[segment_style]}{segment}{self.reset}"
            #styled_segment = segment  # Start with the original segment

            if splitter_show and i > 0:

                if len(splitter_styles) == 1:
                    styled_splitter = f"{self.style_codes[splitter_styles[0]]}{actual_splitter}{self.reset}"
                else:
                    styled_splitter = f"{self.style_codes[splitter_styles[i % len(splitter_styles)]]}{actual_splitter}{self.reset}"
                    #styled_segment = styled_splitter + styled_segment

                # Apply the appropriate style to the splitter and padding if splitter_arms is True
                if splitter_arms:
                    styled_segment = styled_splitter + styled_segment
                else:
                    styled_segment = actual_splitter + styled_segment

            styled_segments.append(styled_segment)

        return ''.join(styled_segments)



    def segment_and_style2(self, text: str, styles_dict: Dict[str, Union[str, int, List[Union[str, int]]]]) -> str:
        words = text.split()
        word_indices = {word: i for i, word in enumerate(words)}  # Map words to their indices
        operations = []

        final_style = None

        # Prepare operations by iterating over the styles_dict
        for style, value in styles_dict.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, int):
                        operations.append((item - 1, style))  # Convert 1-based index to 0-based
                    elif item in word_indices:
                        operations.append((word_indices[item], style))
            else:
                if isinstance(value, int):
                    operations.append((value - 1, style))  # Convert 1-based index to 0-based
                elif value in word_indices:
                    operations.append((word_indices[value], style))
                elif value == '':  # Handle the final style indicated by an empty string
                    final_style = style

        # Sort operations by index
        operations.sort()

        # Initialize the styled words with the entire text unstyled
        styled_words = words.copy()

        # Apply styles in the correct order
        for i, (index, style) in enumerate(operations):
            prev_index = operations[i - 1][0] + 1 if i > 0 else 0
            for j in range(prev_index, index + 1):
                styled_words[j] = f"{self.style_codes[style]}{words[j]}{self.reset}"

        # Apply the final style to any remaining words after the last operation
        if final_style:
            last_index = operations[-1][0] if operations else 0
            for j in range(last_index + 1, len(words)):
                styled_words[j] = f"{self.style_codes[final_style]}{words[j]}{self.reset}"

        return " ".join(styled_words)



    def segment_and_style(self, text: str, styles_dict: Dict[str, Union[str, int]]) -> str:
        words = text.split()
        previous_index = 0
        value_style = None

        # Iterate over the styles_dict items
        for style, key in styles_dict.items():
            if key:  # If key is provided (not an empty string or None)
                if isinstance(key, int):  # Handle key as an index
                    key_index = key - 1  # Convert 1-based index to 0-based
                else:  # Handle key as a word (string)
                    try:
                        key_index = words.index(str(key), previous_index)
                    except ValueError:
                        continue  # If key is not found, skip to the next item

                # Apply the style to the words between previous_index and key_index
                for i in range(previous_index, key_index):
                    words[i] = f"{self.style_codes[style]}{words[i]}{self.reset}"

                # Apply the style to the key word itself
                words[key_index] = f"{self.style_codes[style]}{words[key_index]}{self.reset}"

                # Update previous_index to the current key_index + 1 for the next iteration
                previous_index = key_index + 1
            else:
                # This handles the case where the key is empty, meaning style from the last key to the end
                value_style = style

        # Apply the final style to the remaining words after the last key
        if value_style:
            for i in range(previous_index, len(words)):
                words[i] = f"{self.style_codes[value_style]}{words[i]}{self.reset}"

        return " ".join(words)



    def style_words_by_index(self, text: str, style: Dict[Union[int, Tuple[int, int]], str]) -> str:

        words = text.split()

        for i, word in enumerate(words, start=1):  # Start indexing from 1
            for key in style:
                style_name = style[key]
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


        text = sep.join(converted_args)
        #self.debug('<text>{}</text>', text)

        if isinstance(style, dict):
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


        #if self.enable_styled_phrase_map:
        # Step 1: Handle phrases
        for phrase, details in self.styled_phrase_map.items():
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
                if stripped_word in self.styled_word_map:

                    if trailing_chars:
                        style_start = self.styled_word_map.get(stripped_word, {}).get('style_code', '')
                        styled_word_or_space = f'{style_start}{word}{self.reset}'
                    else:
                        styled_word_or_space = self.styled_word_map.get(stripped_word, {}).get('styled', stripped_word)

                    styled_words_and_spaces[i] = styled_word_or_space

                    # Add the index before the starting index
                    if i > 0:
                        if i - 1 not in boundary_indices_dict:
                            boundary_indices_dict[i - 1] = self.styled_word_map.get(stripped_word, {}).get('attribs')

                    # Add the index after the ending index
                    if i + 1 < len(words_and_spaces):
                        if i + 1 not in boundary_indices_dict:
                            boundary_indices_dict[i + 1] = self.styled_word_map.get(stripped_word, {}).get('attribs')

                    # Update the indexes_used_by_words set
                    indexes_used_by_words.add(i)


                else:
                    # Check if the word contains any substring in the substring_map
                    for substring, details in self.styled_substring_map.items():
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



class FormattedTextBox:
    def __init__(self, pc=None, horiz_width=None, horiz_char=' ', vert_width=None, vert_padding=1, vert_char='|'):
        self.pc = pc if pc else PrintsCharming()
        self.terminal_width = get_terminal_width()
        self.horiz_width = horiz_width if horiz_width else self.terminal_width
        self.horiz_char = horiz_char
        self.horiz_border = self.horiz_width * horiz_char
        self.vert_width = vert_width
        self.vert_padding = vert_padding * ' '
        self.vert_char = horiz_char if vert_width and not vert_char else vert_char
        self.vert_border = '' if not vert_width else vert_width * self.vert_char
        self.available_width = None


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

            left_aligned = self.pc.apply_style(styles[0], self.align_text(strings[0], left_right_width, alignments[0]))
            center_aligned = self.pc.apply_style(styles[1], self.align_text(strings[1], center_width, alignments[1]))
            right_aligned = self.pc.apply_style(styles[2], self.align_text(strings[2], left_right_width, alignments[2]))

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

            left_aligned = self.pc.apply_style(styles[0], self.align_text(strings[0], part_width, alignments[0]))
            right_aligned = self.pc.apply_style(styles[1], self.align_text(strings[1], part_width, alignments[1]))

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
        if self.available_width is None:
            self.available_width = (
                self.horiz_width - (2 * self.vert_width) - (len(self.vert_padding) * 2)
                if self.vert_border
                else self.horiz_width - (len(self.vert_padding) * 2)
            )
        return self.available_width


    def strip_ansi_escape_sequences(self, text):
        ansi_escape = re.compile(r'\x1b\[([0-9]+)(;[0-9]+)*m')
        return ansi_escape.sub('', text)

    def print_simple_border_boxed_text(self, title, subtitle='', align='center'):
        available_width = self.get_available_width()

        title_aligned_text = self.pc.apply_style('vgreen', self.align_text(title, available_width, align))

        if subtitle:
            subtitle_aligned_text = self.pc.apply_style('white', self.align_text(subtitle, available_width, align))
        else:
            subtitle_aligned_text = ''

        horiz_border_top = self.pc.apply_style('purple', self.horiz_border)
        horiz_border_bottom = self.pc.apply_style('orange', self.horiz_border)

        title_vert_border_left = self.pc.apply_style('orange', self.vert_border) + self.vert_padding
        title_vert_border_right = self.vert_padding + self.pc.apply_style('purple', self.vert_border)

        subtitle_vert_border_left = self.pc.apply_style('orange', self.vert_border) + self.vert_padding
        subtitle_vert_border_right = self.vert_padding + self.pc.apply_style('purple', self.vert_border)

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
            horiz_border_top = self.horiz_border if not horiz_border_top_style else self.pc.apply_style(horiz_border_top_style, self.horiz_border)
        else:
            horiz_border_top = None

        if horiz_border_bottom:
            horiz_border_bottom = self.horiz_border if not horiz_border_bottom_style else self.pc.apply_style(horiz_border_bottom_style, self.horiz_border)
        else:
            horiz_border_bottom = None

        if self.vert_char == ' ':
            if vert_border_left:
                vert_border_left = self.vert_border + self.vert_padding if not vert_border_left_style else self.pc.apply_bg_color(vert_border_left_style, self.vert_border) + self.vert_padding
            else:
                vert_border_left = self.vert_padding

            if vert_border_right:
                vert_border_right = self.vert_padding + self.vert_border if not vert_border_right_style else self.vert_padding + self.pc.apply_bg_color(vert_border_right_style, self.vert_border)
            else:
                vert_border_right = self.vert_padding

        else:
            if vert_border_left:
                vert_border_left = self.vert_border + self.vert_padding if not vert_border_left_style else self.pc.apply_style(vert_border_left_style, self.vert_border) + self.vert_padding
            else:
                vert_border_left = self.vert_padding

            if vert_border_right:
                vert_border_right = self.vert_padding + self.vert_border if not vert_border_right_style else self.vert_padding + self.pc.apply_style(vert_border_right_style, self.vert_border)
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
            horiz_border_top = self.horiz_border if not horiz_border_top_style else self.pc.apply_style(horiz_border_top_style, self.horiz_border)
            print(horiz_border_top)

        if first_line_blank:
            blank_text = ' '
            blank_aligned_text = self.align_text(blank_text, available_width, text_align)
            if self.vert_border:
                blank_text_vert_border_left = self.vert_border + self.vert_padding if not text_vert_border_l_style else self.pc.apply_style(text_vert_border_l_style, self.vert_border) + self.vert_padding
                blank_text_vert_border_right = self.vert_padding + self.vert_border + self.vert_padding if not text_vert_border_r_style else self.vert_padding + self.pc.apply_style(text_vert_border_r_style, self.vert_border)
                print(f"{blank_text_vert_border_left}{blank_aligned_text}{blank_text_vert_border_right}")
            else:
                print(f"{self.vert_padding}{blank_aligned_text}{self.vert_padding}")


        for line in text_lines:
            aligned_text = self.pc.apply_style(text_style, self.align_text(line, available_width, text_align))
            if self.vert_border:
                text_vert_border_left = self.vert_border + self.vert_padding if not text_vert_border_l_style else self.pc.apply_style(text_vert_border_l_style, self.vert_border) + self.vert_padding
                text_vert_border_right = self.vert_padding + self.vert_border + self.vert_padding if not text_vert_border_r_style else self.vert_padding + self.pc.apply_style(text_vert_border_r_style, self.vert_border)
                print(f"{text_vert_border_left}{aligned_text}{text_vert_border_right}")
            else:
                txt_vert_border_left = self.vert_padding
                txt_vert_border_right = self.vert_padding
                print(f"{self.vert_padding}{aligned_text}{self.vert_padding}")

        for line in subtext_lines:
            aligned_subtext = self.pc.apply_style(subtext_style, self.align_text(line, available_width, subtext_align))
            if self.vert_border:
                subtext_vert_border_left = self.vert_border + self.vert_padding if not subtext_vert_border_l_style else self.pc.apply_style(subtext_vert_border_l_style, self.vert_border) + self.vert_padding
                subtext_vert_border_right = self.vert_padding + self.vert_border if not subtext_vert_border_r_style else self.vert_padding + self.pc.apply_style(subtext_vert_border_r_style, self.vert_border)
                print(f"{subtext_vert_border_left}{aligned_subtext}{subtext_vert_border_right}")
            else:
                print(f"{self.vert_padding}{aligned_subtext}{self.vert_padding}")

        if horiz_border_bottom:
            horiz_border_bottom = self.horiz_border if not horiz_border_bottom_style else self.pc.apply_style(horiz_border_bottom_style, self.horiz_border)
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
                    aligned_text = self.pc.apply_style(text_style, self.align_text(line, available_width, text_align))

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
                                 horiz_border_height=1):

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
            print(horiz_border_top * horiz_border_height)

        for lines, text_style, text_align in zip(lines_list, text_styles, text_alignments):
            for line in lines:
                if line == 'invisible_text' or line == '':
                    line = ' '
                    aligned_text = self.align_text(line, available_width, text_align)
                else:
                    aligned_text = self.pc.apply_style(text_style, self.align_text(line, available_width, text_align))

                final_text = self.construct_text(vert_border_left, vert_border_right, aligned_text)

                print(final_text)

        if horiz_border_bottom:
            print(horiz_border_bottom * horiz_border_height)
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

        horiz_border = self.pc.apply_style('purple', self.horiz_border)
        vert_border = self.pc.apply_style('orange', self.vert_border) if self.vert_border else ''

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
                    aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align))
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num])
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

        horiz_border = self.pc.apply_style('purple', self.horiz_border)
        vert_border = self.pc.apply_style('orange', self.vert_border) if self.vert_border else ''

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
                    aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                    #aligned_text = self.align_text(line, col_widths[col_num], col_align)
                    #styled_text = self.pc.apply_style(col_style, aligned_text.strip())
                    #final_text = styled_text + ' ' * (col_widths[col_num] - len(aligned_text.strip()))
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
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

        horiz_border = self.pc.apply_style('purple', self.horiz_border)
        vert_border = self.pc.apply_style('orange', self.vert_border) if self.vert_border else ''

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
                    aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
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

        horiz_border = self.pc.apply_style('purple', self.horiz_border)
        vert_border = self.pc.apply_style('orange', self.vert_border) if self.vert_border else ''

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
                    aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
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
                 pc: 'PrintsCharming',
                 apply_style: Callable[[str, str], str],
                 tb_style_name: str = 'default',
                 format_specific_exception: bool = False
                 ) -> None:

        super().__init__(message)
        self.message = message
        self.pc = pc
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












