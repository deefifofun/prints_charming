#!/usr/bin/env python3

from functools import partial
from datetime import datetime
from time import perf_counter
from functools import wraps
from typing import Any, Dict, List, Optional, Union


from prints_charming import (
    DEFAULT_COLOR_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES,
    DynamicFormatter,
    get_terminal_width,
    PStyle,
    PrintsCharming,
    TableManager,
    BoundCell,
    ToggleManager,
    FrameBuilder,
    InteractiveMenu,
    colors_map_one,
    get_key,
)

from prints_charming.exceptions import PrintsCharmingException, ColorNotFoundError, InvalidLengthError, set_excepthook, setup_exceptions

from prints_charming.logging import PrintsCharmingFormatter, PrintsCharmingLogHandler, setup_logger

import os
import sys
import time
import logging
import inspect
import copy
import textwrap
import random





styled_strings = {
    "vgreen": ["Hello, world!", "string", "Connected", "Loaded", "Monitor", "ABOVE THRESHOLD", "wss://advanced-trade-ws.coinbase.com", "Starting", "True", "C++"],
    "green": ["apple"],
    "vred": ["Error", "Failed", "None", "Skipping.", "Canceling", "Canceled", "Hobbies", "Skills", "False"],
    "blue": ["CoinbaseWebsocketClient", "server", "Python"],
    "yellow": ["1", "returned", "Flask", "Some", ],
    "vyellow": ["File modified:", "File modified AGAIN", "subscribed", "=", "JavaScript"],
    "magenta": ["within 10 seconds.", "how", "React", "this is a test"],
    "cyan": ["|", "#", "are", "your", "Project Management System"],
    "orange": ["New Message!", "Prints", "Software Developer", "Prince Charming"],
    "purple": ["My color is purple", "Reading"],
    # Uncomment the next line to hide API keys or sensitive information
    # "conceal": [os.environ[key] for key in os.environ if "API" in key],
}


styled_strings2 = {
    "vgreen": ["Hello, world!", "string", "Connected", "Loaded", "Monitor", "Starting", "True", "C++"],
    "green": ["apple"],
    "vred": ["Error", "Failed", "None", "Skipping.", "Canceling", "Canceled", "Hobbies", "Skills", "False"],
    "blue": ["CoinbaseWebsocketClient", "server", "Python"],
    "yellow": ["1", "returned", "Flask", "Some", ],
    "vyellow": ["File modified:", "File modified AGAIN", "subscribed", "=", "JavaScript"],
    "magenta": ["within 10 seconds.", "how", "React", "this is a test"],
    "cyan": ["|", "#", "are", "your", "Project Management System"],
    "orange": ["New Message,", "Prints", "Software Developer", "Prince Charming"],
    "purple": ["My color is purple", "Reading"],
    # Uncomment the next line to hide API keys or sensitive information
    # "conceal": [os.environ[key] for key in os.environ if "API" in key],
    }






class CustomError(PrintsCharmingException):
    """Custom error for specific use cases."""
    def __init__(self, message: str, pc: 'PrintsCharming', additional_info: str, format_specific_exception: bool = True) -> None:
        super().__init__(message, pc, format_specific_exception=format_specific_exception)
        self.additional_info = additional_info

    def handle_exception(self, logger=None, exc_type=None, exc_value=None, exc_info=None, print_error=False):
        super().handle_exception()
        print(self.pc.apply_style('cyan', self.additional_info), file=sys.stderr)


class CustomError2(PrintsCharmingException):
    """Custom error for specific use cases with additional context."""

    _pc_instance = None  # Subclass-specific PrintsCharming instance

    @classmethod
    def set_pc(cls, pc: 'PrintsCharming'):
        """Set the PrintsCharming instance for this subclass."""
        cls._pc_instance = pc

    def __init__(self, message: str = "Custom error occurred", additional_info: str = "Additional context info",
                 format_specific_exception: bool = True,
                 pc_error: 'PrintsCharming' = None,
                 check_subclass_names: bool = False,
                 use_shared_pc: bool = False):

        """
        Initialize the exception.
        If `use_shared_pc` is True, use the shared instance, otherwise use subclass-specific instance.
        """

        # Use subclass-specific pc instance if not using shared instance
        if not use_shared_pc:
            if not self.__class__._pc_instance:
                raise ValueError("The PrintsCharming instance must be set using `CustomError2.set_pc()` before raising.")
            self.pc = self.__class__._pc_instance
        else:
            if not PrintsCharmingException.shared_pc_exception_instance:
                if not pc_error:
                    raise ValueError(f"The init call to {self.__class__.__name__} instance must supply a pc instance to the pc_error parameter when use_shared_pc parameter is True.")
                PrintsCharmingException.shared_pc_exception_instance = pc
            self.pc = PrintsCharmingException.shared_pc_exception_instance  # Use shared instance



        # Call the superclass constructor with default and passed parameters
        super().__init__(message=message, pc=self.pc, format_specific_exception=format_specific_exception, check_subclass_names=check_subclass_names, use_shared_pc=use_shared_pc)

        # Store additional information for this custom error
        self.additional_info = additional_info

    def handle_exception(self, logger=None, exc_type=None, exc_value=None, exc_info=None, print_error=False):
        """Handle the exception and print additional information."""
        # Call the base class method to handle the exception
        super().handle_exception()

        # Print the additional information styled with cyan
        print(self.pc.apply_style('cyan', self.additional_info), file=sys.stderr)



class CustomError3(PrintsCharmingException):
    """Another custom error subclass with its own PrintsCharming instance."""

    _pc_instance = None  # Subclass-specific PrintsCharming instance

    @classmethod
    def set_pc(cls, pc: 'PrintsCharming'):
        """Set the PrintsCharming instance for this subclass."""
        cls._pc_instance = pc

    def __init__(self, message: str = "CustomError3 occurred", additional_info: str = "Different context",
                 format_specific_exception: bool = True,
                 pc_error: 'PrintsCharming' = None,
                 check_subclass_names: bool = False,
                 use_shared_pc: bool = False):
        """
        Initialize the exception.
        If `use_shared_pc` is True, use the shared instance, otherwise use subclass-specific instance.
        """
        if not use_shared_pc:
            if not self.__class__._pc_instance:
                raise ValueError("The PrintsCharming instance must be set using `CustomError3.set_pc()` before raising.")
            self.pc = self.__class__._pc_instance
        else:
            if not PrintsCharmingException.shared_pc_exception_instance:
                if not pc_error:
                    raise ValueError(f"The init call to {self.__class__.__name__} instance must supply a pc instance to the pc_error parameter when use_shared_pc parameter is True.")
                PrintsCharmingException.shared_pc_exception_instance = pc
            self.pc = PrintsCharmingException.shared_pc_exception_instance  # Use shared instance

        self.additional_info = additional_info
        super().__init__(message, pc=self.pc, format_specific_exception=format_specific_exception, check_subclass_names=check_subclass_names, use_shared_pc=use_shared_pc)

    def handle_exception(self, logger=None, exc_type=None, exc_value=None, exc_info=None, print_error=False):
        """Handle the exception and print additional information."""
        super().handle_exception()
        print(self.pc.apply_style('green', self.additional_info), file=sys.stderr)


# Timing decorator
def time_step(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        step_start = perf_counter()
        result = func(*args, **kwargs)
        step_end = perf_counter()
        elapsed_time = step_end - step_start
        elapsed_time = f'{elapsed_time:.4f}'
        print(f'{pc.apply_style('cyan', func.__name__)} took {pc.apply_style('vgreen', elapsed_time)} seconds to complete\n')
        return result

    return wrapper


def time_total_execution(main_func):
    def wrapper():
        start_time = perf_counter()
        try:
            main_func()
        except Exception as e:
            message = f'An error occurred: {str(e)}'
            styled_message = pc.apply_style('red', message)
            # Raising the custom error with additional context
            raise CustomError2(styled_message, pc_error=pc, additional_info="Execution failed in time_total_execution")
        finally:
            end_time = perf_counter()
            total_time = end_time - start_time
            total_time = f'{total_time:.4f}'
            # Print total execution time with your styling
            print(f'Total script execution time: {pc.apply_style('vgreen', total_time)} seconds!!!')

    return wrapper



@time_step
def example_menu():
    # Remove '1' from word_map so that it isn't printed in yellow style
    pc.remove_string('1')
    # Cycle thru the options with 'n' or 'p' <enter> and then <enter> again on the selection
    menu_options = ["main_menu", "vert", "Option 1", "Option 2", "Option 3"]
    menu = InteractiveMenu(menu_options, pc=pc, selected_style='vcyan', confirmed_style='vgreen', alt_buffer=True)
    menu.run()



class BorderBoxStyles:

    def __init__(self):
        self.themes = {

        }


class FunctionStyles:

    def __init__(self):
        self.border1_styles = {
            'top': 'purple',
            'right': 'purple',
            'bottom': 'orange',
            'left': 'orange'
        }

        self.border2_styles = {
            'top': 'dblue',
            'right': 'dblue',
            'bottom': 'vblue',
            'left': 'vblue'
        }

        self.header_styles = {
            'main': 'header_main',
            'standard': 'bold',
            'important': 'red_bold',
            'subtitle': 'italic',
            # Add more header styles as needed
        }

        self.sentence_styles = {
            'question': 'orangewhite',
            'statement': 'normal',
            'exclamation': 'bold',
            'paragraph': 'indented',
            'column': 'justified',
            # Add more sentence styles as needed
        }

        # Placeholder for future groupings
        self.default_styles = DEFAULT_STYLES.copy()

    def welcome(self, style_cat: str, sub_cat: str = None) -> str:
        # Mapping of style categories to their corresponding dictionaries
        styles_mapping = {
            "border1": self.border1_styles,
            "border2": self.border2_styles,
            "header": self.header_styles,
            "sentence": self.sentence_styles,
            "default": self.default_styles,
            # Add more style types as needed
        }

        if style_cat in styles_mapping:
            style_dict = styles_mapping[style_cat]
            return style_dict.get(sub_cat, 'default_style')
        else:
            raise ValueError(f"Unknown style type: {style_cat}")


class StyleConditionsManager:

    def __init__(self, conditions=None):
        self.function_styles = FunctionStyles()
        self.border_styles = BorderBoxStyles()
        self.map = conditions if conditions else {
            "name": self.name_style,
            "age": self.age_style,
            "balance": self.balance_style,
            "occupation": self.occupation_style,
            "welcome": self.welcome_style,
            "real": self.real_style,
        }

    def name_style(self, value: str) -> str:
        if value in ["John", "Michael", "David", "John Doe"]:  # Add more boy names
            return "blue"
        elif value in ["Alice", "Sophia", "Emma"]:  # Add more girl names
            return "pink"
        return "default"

    def age_style(self, value: int) -> str:
        if value < 18:
            return "red"
        elif value < 21:
            return "pink"
        else:
            return "green"

    def balance_style(self, value: float) -> str:
        if value > 0:
            return "vgreen"
        elif value == 0:
            return "vblue"
        else:
            return "vred"

    def occupation_style(self, value: str) -> str:
        return "orange"

    def real_style(self, value: str) -> str:
        return "red" if value == 'False' else "green"

    def welcome_style(self, position: str) -> str:
        return "purple" if position in ['top', 'right'] else "orange"



@time_step
def custom_style_function(text: str, label_style: str, label_delimiter: str, pc) -> str:
    lines = text.split('\n')
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        leading_whitespace = line[:len(line) - len(stripped_line)]

        if stripped_line.startswith('- ') and not stripped_line.endswith(label_delimiter):
            # Apply main bullet style
            parts = stripped_line.split(' ', 1)
            if len(parts) == 2:
                lines[i] = f"{leading_whitespace}{pc.get_style_code(label_style)}{parts[0]} {pc.reset}{pc.get_style_code('main_bullet_text')}{parts[1]}{pc.reset}"
        elif len(stripped_line) > 1 and stripped_line[0].isdigit() and stripped_line[1] == '.':
            # Apply number and period style, followed by phrase style
            parts = stripped_line.split('. ', 1)
            if len(parts) == 2:
                lines[i] = f"{leading_whitespace}{pc.get_style_code('numbers')}{parts[0]}.{pc.reset} {pc.get_style_code('sub_proj')}{parts[1]}{pc.reset}"
        elif stripped_line.startswith('- ') and stripped_line.endswith(label_delimiter):
            # Apply sub-bullet style
            parts = stripped_line.split(' ', 2)
            if len(parts) == 3:
                lines[i] = f"{leading_whitespace}{pc.get_style_code('sub_bullets')}{parts[1]} {pc.reset}{pc.get_style_code('sub_bullet_text')}{parts[2]}{pc.reset}"
        elif leading_whitespace.startswith('   '):
            # Apply sub-bullet sentence style
            words = stripped_line.split()
            if len(words) > 1:
                lines[
                    i] = f"{leading_whitespace}{pc.get_style_code('sub_bullet_title')}{words[0]} {pc.reset}{pc.get_style_code('sub_bullet_sentence')}{' '.join(words[1:])}{pc.reset}"

    return '\n'.join(lines)


def my_custom_error(pc):
    print(styled_mini_border)
    print(f'function: my_custom_erro:')
    print(f'{styled_mini_border}\n')
    try:
        message = f'A custom error occurred'
        styled_message = pc.apply_style('purple', message)
        raise CustomError(styled_message, pc, "Additional context-specific information")
    except CustomError as e:
        e.handle_exception()


@time_step
def formatted_text_box_stuff():
    pc = PrintsCharming(config={"enable_logging": True}, style_conditions=StyleConditionsManager(), styled_strings=styled_strings)
    builder = FrameBuilder(pc=pc, horiz_width=100, horiz_char=' ', vert_width=5, vert_padding=1, vert_char='|')

    horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom = builder.build_styled_border_box(horiz_border_top_style='purple',
                                                                                                                 horiz_border_bottom_style='orange',
                                                                                                                 vert_border_left_style='orange',
                                                                                                                 vert_border_right_style='purple')

    purple_horiz_border = pc.apply_style('purple', builder.horiz_border)
    orange_horiz_border = pc.apply_style('orange', builder.horiz_border)

    purple_vert_border = builder.vert_padding + pc.apply_style('purple', builder.vert_border)
    orange_vert_border = pc.apply_style('orange', builder.vert_border) + builder.vert_padding

    available_width = builder.get_available_width()

    title = 'Prints Charming'
    subtitle = 'Hope you find the user guide helpful'


    title_center_aligned = pc.apply_style('vgreen', builder.align_text(title, available_width, 'center'))
    subtitle_center_aligned = pc.apply_style('white', builder.align_text(subtitle, available_width, 'center'))


    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_center_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_center_aligned}{purple_vert_border}')
    print(f'{orange_horiz_border}\n')

    title_left_aligned = pc.apply_style('vgreen', builder.align_text(title, available_width, 'left'))
    subtitle_left_aligned = pc.apply_style('white', builder.align_text(subtitle, available_width, 'left'))

    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_left_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_left_aligned}{purple_vert_border}')
    print(f'{orange_horiz_border}\n')

    title_right_aligned = pc.apply_style('vgreen', builder.align_text(title, available_width, 'right'))
    subtitle_right_aligned = pc.apply_style('white', builder.align_text(subtitle, available_width, 'right'))

    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_right_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_right_aligned}{purple_vert_border}')
    print(f'{orange_horiz_border}\n\n')

    print(horiz_border_top)

    center_padding = " ".center(available_width)
    empty_line_with_borders = f"{vert_border_left}{center_padding}{vert_border_right}"
    print(empty_line_with_borders)
    print(empty_line_with_borders)

    left_open_border = (" " * builder.vert_width) + builder.vert_padding
    naked_right_text = "Prints Charming".rjust(available_width)
    print(f"{left_open_border}{naked_right_text}{vert_border_right}")

    left_open_border = (" " * builder.vert_width) + builder.vert_padding
    right_open_border = builder.vert_padding + (" " * builder.vert_width)
    naked_right_text = "Prints Charming".rjust(available_width)

    print(f"{left_open_border}{naked_right_text}{right_open_border}")
    print(f"{left_open_border}{naked_right_text}{vert_border_right}")

    naked_left_text = "Prints Charming"
    print(f"{vert_border_left}{naked_left_text}")

    centered_text = "Prints Charming".center(available_width)
    centered_subtext = "Hope you find the user guide helpful".center(available_width)
    left_text = "Prints Charming".ljust(available_width)
    left_subtext = "Hope you find the user guide helpful".ljust(available_width)
    right_text = "Prints Charming".rjust(available_width)
    right_subtext = "Hope you find the user guide helpful".rjust(available_width)
    print(f'{vert_border_left}{centered_text}{vert_border_right}')
    print(f'{vert_border_left}{centered_subtext}{vert_border_right}')
    print(f'{vert_border_left}{left_text}{vert_border_right}')
    print(f'{vert_border_left}{left_subtext}{vert_border_right}')
    print(f'{vert_border_left}{right_text}{vert_border_right}')
    print(f'{vert_border_left}{right_subtext}{vert_border_right}')
    print(f'{horiz_border_bottom}\n')

    one_col_text = 'center aligned single col'
    two_col_aligned_text_tuple = ('left aligned double col', 'right aligned double col')
    three_col_text_tuple = ('column_1', 'column_2', 'column_3')

    one_col_string = pc.apply_style('vgreen', builder.align_text(one_col_text, available_width, align='center'))
    two_col_strings_centered = builder.align_strings(['center aligned double col', 'center aligned double call'], available_width, styles=['purple', 'orange'])
    two_col_strings_hug_borders = builder.align_strings(['left aligned double col', 'right aligned double col'], available_width, styles=['purple', 'orange'],
                                                        alignments=['left', 'right'])
    two_col_strings_hug_left = builder.align_strings(['left aligned double col', 'left aligned double col'], available_width, styles=['purple', 'orange'],
                                                     alignments=['left', 'left'])
    two_col_strings_hug_right = builder.align_strings(['right aligned double col', 'right aligned double col'], available_width, styles=['purple', 'orange'],
                                                      alignments=['right', 'right'])

    three_col_strings_centered = builder.align_strings(three_col_text_tuple, available_width, styles=['purple', 'vgreen', 'orange'])
    three_col_strings_mixed = builder.align_strings(three_col_text_tuple, available_width, styles=['purple', 'vgreen', 'orange'], alignments=['left', 'center', 'right'])

    print(purple_horiz_border)
    print(f'{orange_vert_border}{one_col_string}{purple_vert_border}')
    print(f'{orange_vert_border}{two_col_strings_hug_borders}{purple_vert_border}')
    print(f'{orange_vert_border}{two_col_strings_centered}{purple_vert_border}')
    print(f'{orange_vert_border}{two_col_strings_hug_left}{purple_vert_border}')
    print(f'{orange_vert_border}{two_col_strings_hug_right}{purple_vert_border}')
    print(f'{orange_vert_border}{three_col_strings_centered}{purple_vert_border}')
    print(f'{orange_vert_border}{three_col_strings_mixed}{purple_vert_border}')
    print(f'{orange_horiz_border}\n\n\n\n')

    # Print a simple border boxed text for the welcome message in the welcome function
    builder.print_simple_border_boxed_text("Prints Charming", subtitle="Hope you find the user guide helpful!", align='center')
    print()


@time_step
def progress_bar(pc):
    print("Starting process...")
    pc.print_progress_bar()
    print("\nProcess complete.")


@time_step
def kwargs_replace_and_style_placeholders_examples():
    pc = PrintsCharming(style_conditions=StyleConditionsManager(), styled_strings=styled_strings)

    # Assign dynamic values to my_placeholders
    my_placeholders = {
        "name": "John Doe",
        "age": 20,
        "balance": 5,
        "occupation": "Software Developer",
        "real:": 'True',
    }

    my_text = "Hello, {name}. You are {age} years old, your occupation is {occupation}, and you have {balance} USD in your account and you are real: {real}."
    pc.print(my_text, **my_placeholders)  # print my_text directly thru the PrintCharming print method

    colored_text = pc.replace_and_style_placeholders(text=my_text, placeholders=my_placeholders)  # return the styled text from the method
    print(colored_text)  # print the styled text with standard python print

    structured_text = """
                Name: {name}
                Age: {age}
                Balance: {balance}
                Occupation: {occupation}
                Real: {real}

                Skills:
                - Python
                - JavaScript
                - C++

                Projects:
                1. Project Management System
                   - Description: A web-based application to manage projects and tasks.
                   - Technologies: Django, React, PostgreSQL

                2. E-commerce Platform
                   - Description: An online store with payment integration.
                   - Technologies: Flask, Angular, MySQL

                Hobbies:
                - Reading
                - Hiking
                - Chess
                """

    pc.print(structured_text, **my_placeholders)  # print with the PrintsCharming print method. This will be directed to the replace_and_style_placeholders method because of the kwargs

    styled_structured_text = pc.replace_and_style_placeholders(text=structured_text, placeholders=my_placeholders)  # return the styled text from the method

    print(f'reg print command styled_structured_text:')
    print(styled_structured_text)

    print(f'pc.print(structured_text):')
    pc.print(structured_text,
             color='silver')  # print with the PrintsCharming print method. This will not be directed to the replace_and_style_placeholders method because no kwargs

    print('\n\n\n')

    # Create a partial function with specific parameters
    custom_style_with_params = partial(custom_style_function, label_style='main_bullets', label_delimiter=':', pc=pc)

    # Usage example
    custom_replace_and_style_placeholders = pc.replace_and_style_placeholders(structured_text, my_placeholders, style_function=custom_style_with_params)

    print(f'result of custom function with replace_and_style_placeholders method:')
    print(custom_replace_and_style_placeholders)


@time_step
def add_styled_substrings_to_instance(pc):
    pc.add_subword('please', 'yellow')
    pc.add_subword('substring', 'vyellow')
    pc.add_subword('color', 'blue')
    pc.add_subword('apple', 'orange')
    pc.add_subword('pine', 'white')
    pc.add_subword('ex', 'vred')



@time_step
def print1(pc):
    pc.print(f"\nThis is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.\n\n", subword_style_option=5)
    pc.print(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.\n\n", subword_style_option=1)
    pc.print(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.\n\n", subword_style_option=2)
    pc.print(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.\n\n", subword_style_option=3)
    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', subword_style_option=5)
    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', subword_style_option=1)
    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', subword_style_option=2)
    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it this is a test is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', subword_style_option=2)
    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it this\nis\na test is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', phrase_norm=True, subword_style_option=2)
    pc.print(' ' * term_width, color="default", bg_color="purple", bold=True, overline=True, underline=True, end='\n\n')





@time_step
def print2(pc):
    pc.print2(f"\nThis is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.\n\n", subword_style_option=5)
    pc.print2(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.\n\n", subword_style_option=1)
    pc.print2(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.\n\n", subword_style_option=2)
    pc.print2(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.\n\n", subword_style_option=3)
    pc.print2(
        f'Here    are    some examples of substringsse.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', subword_style_option=5)
    pc.print2(
        f'Here    are    some examples of substringsse.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', subword_style_option=1)
    pc.print2(
        f'Here    are    some examples of substringsse.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', subword_style_option=2)
    pc.print2(
        f'Here    are    some examples of substringsse.     Some make the whole please word it this is a test is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', subword_style_option=2)
    pc.print2(
        f'Here    are    some examples of substringsse.     Some make the whole please word it this\nis\na test is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n\n',
        color='purple', phrase_norm=True, subword_style_option=2)
    pc.print2(' ' * term_width, color="default", bg_color="purple", bold=True, overline=True, underline=True, end='\n\n')



@time_step
def test_my_style_code(pc):
    print(styled_mini_border)
    pc.print(f'function: test_my_style_code:')
    print(f'{styled_mini_border}\n')

    my_style_code = pc.create_style_code(PStyle(color='green', bg_color='white', underline=True))

    my_style_code2 = pc.create_style_code(dict(color='orange', bg_color='white'))

    print(f'{my_style_code}Hello                 World!{pc.reset}')

    print(f'{my_style_code2}Hello                 World!{pc.reset}')

    my_style_code3 = pc.create_style_code(dict(color='blue', bg_color='white'))

    mytext3 = f'Hello World'

    mytext3_styled = pc.apply_style_code(my_style_code3, mytext3)

    pc.print(mytext3_styled, skip_ansi_check=True)

    pc.print2(mytext3_styled, skip_ansi_check=True)

    print(f'{mytext3_styled}\n\n')


@time_step
def random_examples():
    # Create a preconfigured instance of PrintsCharming
    # The first couple print statements though ugly demonstrate the nuanced and highly customizable and unbreakable relationship between color, bg_color, underlines, overlines, etc
    # and how they are configured to behave in the spacing between words dependent on the share_alike parameters in the print statement, which default to what made the most sense to
    # me but is highly customizable for different use cases. Like when spacing/gaps/etc between words are filled with bg, underline etc they need to share fg_colors for underline,
    # bg_colors for bg_color in the space/gap/sep, the rules and relationships depend on the different styles associated with the indexes of the different
    # words/phrases/substrings/variables/numbers/other/styles/etc/highly dynamic and like i said configurable...legit documentation
    # to come. In the meantime you can keep as is or mess around with the PrintsCharming print method parameters.

    pc = PrintsCharming(styled_strings=styled_strings)

    print(styled_mini_border)
    pc.print(f'function: random_examples:')
    print(f'{styled_mini_border}\n')



    add_styled_substrings_to_instance(pc)

    print1(pc)

    print2(pc)

    test_my_style_code(pc)




    pc.add_string('This phrase styled in green', 'green')
    pc.add_string("I'm completely yellow!", 'vyellow')
    pc.add_string('wordl', 'red')
    pc.add_string('Blue', 'blue')
    pc.add_string("orange phrase          white bg", 'orangewhite')

    pc.print(f"A single wordl styled red. This phrase styled in green Hello                     World.", f"I'm Blue mostly default styling I'm completely yellow! except that",
             '   orange phrase          white bg', color='green', bg_color='white', underline=True, overline=True, skip_ansi_check=True)

    pc.print2(f"A single wordl styled red. This phrase styled in green Hello                     World.", f"I'm Blue mostly default styling I'm completely yellow! except that",
             '   orange phrase          white bg', color='green', bg_color='white', underline=True, overline=True, skip_ansi_check=True)

    pc.print(f"A single wordl styled red. This phrase styled in green Hello                     World.", f"I'm Blue mostly default styling I'm completely yellow! except that",
             '   orange phrase          white bg', color='green', underline=True, overline=True, skip_ansi_check=True)

    pc.print2(f"A single wordl styled red. This phrase styled in green Hello                     World.", f"I'm Blue mostly default styling I'm completely yellow! except that",
             '   orange phrase          white bg', color='green', underline=True, overline=True, skip_ansi_check=True)


    some_var = 21

    # Print specifying only the color of the text
    pc.print("Hello, world!", color="red" if some_var < 21 else "green")

    # Print specifying italic and underline styles with default color
    pc.print("Hello, world!", italic=True, underline=True)

    # Print using a predefined style 'magenta' defined above
    pc.print("Hello, world!", style="magenta")

    # Print using a predefined style 'task' defined above
    pc.print("# Specify predefined style 'task' for printing. The 'task' style is defined above.")
    pc.print("This is a task.", style="task")

    # Print using a predefined style 'task' with color changed to green and underline
    pc.print("# Specify predefined style 'task' for printing but change color to green and underline to True.")
    pc.print("This is a task.\n\n", style="task", color="green", underline=True)


@time_step
def print_horizontal_bg_strip(pc):
    print(styled_mini_border)
    pc.print(f'function: print_horizontal_bg_strip:')
    print(f'{styled_mini_border}\n')


    print(pc.generate_bg_bar_strip('green', 50))
    print(pc.generate_bg_bar_strip('vyellow'))




@time_step
def print_variable_examples(pc):
    print(styled_mini_border)
    pc.print(f'function: print_variable_examples:')
    print(f'{styled_mini_border}\n')

    pc.print_variables("Hello {username}, your balance is {balance} USD.", text_style="yellow",
                       username=("Prince", "blue"), balance=(1000, "green"))

    pc.print_variables("Hello {var2}, your balance is {var1} USD.", text_style="yellow",
                       var1=(1000, "green"), var2=("Princess", "blue"))

    print()


@time_step
def auto_styling_examples(pc, text):
    print(f'\n\n{styled_mini_border}')
    pc.print(f'function: auto_styling_examples:')
    print(f'{styled_mini_border}\n')

    pc.add_strings_from_dict(styled_strings)
    pc.print("Let's first print, Hello, world! styled as described above.")
    pc.print("Let's first print, Hello, world! styled as described above and right here.", style="yellow")
    pc.print(f"{text} Remember we assigned, 'Hello, world!' to the 'text' variable above. Let's pretend we are Connected to wss://advanced-trade-ws.coinbase.com", color="blue")
    pc.print("These words are going to be styled by their indexes, Hello, world!", style={1: "vgreen", (2, 4): "blue", (5, 7): "yellow", (8, 10): "purple", (11, 12): "pink"})
    pc.print("Hello, world! These words are going to be styled by their indexes, Hello, world!",
             style={1: "vgreen", (2, 4): "blue", (5, 7): "yellow", (8, 11): "purple", (13, 14): "pink"}, color='red')
    pc.print("Hello, world! Only these words are going to be styled by their indexes, Hello, world!",
             style={(3, 4): "orange", (5, 7): "blue", (8, 9): "yellow", (10, 13): "purple", (14, 15): "pink"})
    pc.print("Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My color is purple! these words are default. server")
    pc.print("Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My color is purple these words are magenta. server",
             style='magenta')
    pc.print("Hello", "how are you?", sep="---", color='green')
    pc.print("This string is not connected to another", color='blue')
    pc.print("This string is connected to another", "string\n", color='vyellow')


@time_step
def style_words_by_index_examples(local_pc):
    print(styled_mini_border)
    pc.print(f'function: style_words_by_index_examples:')
    print(f'{styled_mini_border}\n')
    indexed_style = {
        1: "vgreen",
        (2, 4): "blue",
        (5, 6): "yellow",
        7: "purple",
        (8, 10): "pink"
    }

    text1 = "These,    words are going to be    styled by their indexes."

    index_styled_text = local_pc.style_words_by_index(text1, indexed_style)
    print(f'{index_styled_text}\n')  # 1
    local_pc.print(f'Orange text here, {index_styled_text}, more orange text.', color='orange', skip_ansi_check=True)  # 2
    local_pc.print2(f'Orange text here, {index_styled_text}, more orange text.', color='orange', skip_ansi_check=True)  # 3
    print()

    local_pc.print2(f'Orange text here', {index_styled_text}, f'more orange text', 'gold text here!', color=['orange', None, 'orange', 'gold'], skip_ansi_check=True, style_args_as_one=False)  # 4


    local_pc.print("These,    words are going to be    styled by their indexes. ", style=indexed_style)  # 5
    local_pc.print("These,    words are going to be    styled by their indexes. ", style=indexed_style, color="blue", skip_ansi_check=True)  # 6


    index_styled_text2 = local_pc.style_words_by_index("These,    words are going to be    styled by their indexes. ", indexed_style)
    print(f'{index_styled_text2}\n\n')  # 7

    local_pc.print(f'{index_styled_text2}\n\n')  # 8
    local_pc.print("These,    words are going to be    styled by their indexes. ", style=indexed_style)  # 9

    indexed_style2 = {
        (2, 4): "blue",
        (5, 6): "yellow",
        7: "purple",
        (8, 9): "pink"
    }

    local_pc.print("These, words are going to be styled by their indexes.", style=indexed_style2, color='orange')  # 10
    local_pc.print2("These, words are going to be styled by their indexes.", style=indexed_style2, color='orange')  # 11

    index_styled_text3 = local_pc.style_words_by_index("These,    words are going to be    styled by their indexes.  ", indexed_style2)
    print(f'{index_styled_text3}\n\n')  # 12
    local_pc.print(f'{index_styled_text3} not these though\n\nor these', skip_ansi_check=True, color='green')  # 13


@time_step
def segment_and_style_example_1(local_pc):
    print(styled_mini_border)
    pc.print(f'function: segment_and_style_example_1:')
    print(f'{styled_mini_border}\n')

    text = f'This is a sentence where the way we determine 1 how and 2 where the text gets styled depends on: where the word: that is the dictionary key falls within this text.'

    splits = dict(green='sentence', red='2', orange='gets', blue='word:', yellow='')
    #styled_sentence = local_pc.segment_and_style(text, splits)
    #print(f'{styled_sentence}\n\n')

    local_pc.print(f'{text}\n\n', style=splits)
    local_pc.print2(f'{text}\n\n', style=splits)

    styled_sentence2 = local_pc.segment_and_style_update(text, splits)
    print(f'{styled_sentence2}\n')


@time_step
def segment_and_style_example_2(local_pc):
    print(styled_mini_border)
    pc.print(f'function: segment_and_style_example_2:')
    print(f'{styled_mini_border}\n')

    text = f'This is a sentence where the way we determine 1 how and 2 where the text gets styled depends on: where the word: that is the dictionary key falls within this text.'

    splits = dict(green='sentence', red=['2', 'word:'], blue='gets', yellow='')

    local_pc.print(f'{text}\n\n', style=splits)
    local_pc.print2(f'{text}\n\n', style=splits)

    styled_sentence2 = local_pc.segment_and_style2(text, splits)
    print(f'{styled_sentence2}\n\n')


@time_step
def segment_and_style_examples(local_pc):
    print(styled_mini_border)
    pc.print(f'function: segment_and_style_examples:')
    print(f'{styled_mini_border}\n')

    text = f'This is a sentence where the way we determine 1 how and 2 where the text gets styled depends on: where the word: that is the dictionary key falls within this text.'

    segment_and_style_example_1(local_pc)
    segment_and_style_example_2(local_pc)


@time_step
def segment_with_splitter_example(local_pc):
    print(styled_mini_border)
    pc.print(f'function: segment_with_splitter_example:')
    print(f'{styled_mini_border}\n')

    splitter_text = f' | This is a sentence | where the way we determine 1 how and 2 | where the text gets | styled depends on: where the word: | that is the dictionary key falls within this text. |'

    splitter_match = '|'
    splitter_swap = '|+|'
    splitter_show = True
    single_splitter_style = True
    splitter_style = 'vcyan' if single_splitter_style else ['vcyan', 'red', 'green', 'yellow', 'blue', 'orange']
    splitter_arms = True
    string_style = ['yellow', 'orange', 'purple', 'vgreen', 'blue']
    styled_sentence3 = local_pc.segment_with_splitter_and_style(splitter_text, splitter_match, splitter_swap, splitter_show, splitter_style, splitter_arms, string_style)
    print(f'{styled_sentence3}\n')



@time_step
def index_styling_examples(default_bg='jupyter'):
    print(styled_mini_border)
    pc.print(f'function: index_styling_examples:')
    print(f'{styled_mini_border}\n')

    local_pc = PrintsCharming(default_bg_color=default_bg)

    style_words_by_index_examples(local_pc)
    segment_and_style_examples(local_pc)
    segment_with_splitter_example(local_pc)


@time_step
def variable_examples(pc):
    print(styled_mini_border)
    pc.print(f'function: variable_examples:')
    print(f'{styled_mini_border}\n')

    pc.print("# Use the add_string method to add 'Hello, world!' to the phrases dictionary with 'vgreen' style.")
    pc.add_string("Hello, world!", style_name="vgreen")
    pc.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
    pc.print("Hello, world!")
    pc.print("# Use the remove_string method to remove 'Hello, world!' from the styled phrases dictionary.")
    pc.remove_string("Hello, world!")
    pc.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
    pc.print("Hello, world!")
    pc.print("# Define a variable.")
    text = "Hello, world!"
    pc.print(f"# Use the add_string method to add {text} to the phrases dictionary with 'yellow' style.")
    pc.add_string(text, style_name="yellow")
    pc.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
    pc.print(text)
    pc.print("# Show that 'Hello, world!' retains its style while other words are unstyled.")
    pc.print(f"This sentence says, {text}")
    pc.print("# Show how you can style other words alongside, 'Hello, world!'.")
    pc.print(f"This sentence says, {text}", style='task')
    pc.print("# Show how the order of the words doesn't matter.")
    pc.print(f"{text} Let me say that again, {text} {text} I said it again!", style="orange")
    pc.print("# Use the remove_string method to remove 'Hello, world!' from the styled phrases dictionary.")
    pc.remove_string("Hello, world!")
    pc.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
    pc.print("Hello, world!\n")

    return text


@time_step
def simple_use_case(pc):
    ds = '\n' * 2
    ts = '\n' * 3
    print(styled_mini_border)
    pc.print(f'function: simple_use_case:')
    print(styled_mini_border, end=ds)

    pc.print("# Basic printing with ColorPrinter will print in the default style with default color.")
    pc.print("Hello, world!", end=ds)
    pc.print("# Print in the default style reverse foreground and background.")
    pc.print("Hello, world!", reverse=True, end=ds)
    pc.print("# Specify only the color of the args.")
    pc.print("Hello, world!", color="red", end=ds)
    pc.print("# Specify only italic and underline will print in the default color.")
    pc.print("Hello, world!", italic=True, underline=True, end=ds)
    pc.print("# Specify a predefined style 'magenta'. The 'magenta' style is defined above.")
    pc.print("Hello, world!", style="magenta", end=ds)
    pc.print("# Specify predefined style 'task' for printing. The 'task' style is defined above.")
    pc.print("This is a task.", style="task", end=ds)
    pc.print("# Specify predefined style 'task' for printing but change color to green and underline to True.")
    pc.print("This is a task.", style="task", color="green", underline=True, end=ds)
    pc.print("Show text with bg_color:")
    pc.print("This has a bg_color", style="bg_color_green", end=ds)
    pc.print2("This has a bg_color", style="bg_color_green", end=ds)
    pc.print("# Show that 'Hello, world!' isn't color or style defined.")
    pc.print("Hello, world!", end=ts)



@time_step
def more_stuff():
    pc = PrintsCharming()

    print(styled_mini_border)
    print(f'function: more_stuff')
    print(styled_mini_border)

    builder = FrameBuilder(pc=pc, horiz_char='|', vert_width=2, vert_padding=1, vert_char='|')
    solid_horiz_rule = builder.terminal_width * ' '
    avail_width = builder.get_available_width()

    structured_text = """
            Name: {name}
            Age: {age}
            Balance: {balance}
            Occupation: {occupation}

            Skills:
            - Python
            - JavaScript
            - C++

            Projects:
            1. Project Management System
               - Description: A web-based application to manage projects and tasks.
               - Technologies: Django, React, PostgreSQL

            2. E-commerce Platform
               - Description: An online store with payment integration.
               - Technologies: Flask, Angular, MySQL

            Hobbies:
            - Reading
            - Hiking
            - Chess
        """

    columns = [structured_text]
    col_widths = [builder.get_available_width()]
    col_styles = ['red']
    col_alignments = ['left']
    builder.print_multi_column_box2(columns, col_widths, col_styles, col_alignments, col_sep='|')
    print('\n')

    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line", structured_text, "Column 4", " "]
    col_widths = ['', 25, 68, 20, 20]
    col_styles = ['red', 'green', 'blue', 'yellow', 'magenta']
    col_alignments = ['left', 'center', 'left', 'center', 'center']
    builder.print_multi_column_box2(columns, col_widths, col_styles, col_alignments, col_sep='|')
    print('\n')

    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line"]
    col_widths = ['', 25]
    col_styles = ['red', 'green']
    col_alignments = ['center', 'center']
    builder.print_multi_column_box2(columns, col_widths, col_styles, col_alignments, col_sep='|')
    print(pc.apply_style('orange', solid_horiz_rule) * 4)

    columns = [structured_text]
    col_widths = [100]
    col_styles = ['red']
    col_alignments = ['left']
    builder.print_multi_column_box3(columns, col_widths, col_styles, col_alignments, col_sep='|', col_widths_percent=True)
    print(pc.apply_style('orange', solid_horiz_rule) * 3)

    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line", structured_text, "Column 4", "Col 5"]
    col_widths = ['', 15, 55, 10, 10]
    col_styles = ['red', 'green', 'blue', 'yellow', 'magenta']
    col_alignments = ['left', 'center', 'left', 'center', 'center']
    builder.print_multi_column_box3(columns, col_widths, col_styles, col_alignments, col_sep='|', col_widths_percent=True)

    print(pc.apply_style('orange', solid_horiz_rule) * 2)

    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line"]
    col_widths = ['', 25]
    col_styles = ['red', 'green']
    col_alignments = ['center', 'center']
    builder.print_multi_column_box3(columns, col_widths, col_styles, col_alignments, col_sep='|', col_widths_percent=True)

    print(pc.apply_style('orange', solid_horiz_rule))

    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line"]
    col_widths = ['', 25]
    col_styles = ['red', 'green']
    col_alignments = ['center', 'center']
    builder.print_multi_column_box4(columns, col_widths, col_styles, col_alignments, col_sep='||', col_sep_width=1)
    print()


@time_step
def print_foreground_colors(pc, builder):
    for color in pc.color_map.keys():
        if builder.vert_char == ' ':
            fg_vert_border_left = builder.pc.apply_bg_color(color, builder.vert_border) + builder.vert_padding
            fg_vert_border_right = builder.vert_padding + builder.pc.apply_bg_color(color, builder.vert_border)
        else:
            fg_vert_border_left = builder.pc.apply_color(color, builder.vert_border) + builder.vert_padding
            fg_vert_border_right = builder.vert_padding + builder.pc.apply_color(color, builder.vert_border)

        fg_available_width = builder.get_available_width()

        fg_text = f"This is one of the prints_charming foreground colors in the color map # Name: {color}"
        fg_text2 = f"{color} foreground color in prints_charming ColorPrinter color map"
        fg_text_center_aligned = builder.pc.apply_color(color, builder.align_text(fg_text2, fg_available_width, 'center'))
        pc.print(f'\n{fg_vert_border_left}{fg_text_center_aligned}{fg_vert_border_right}')

        # pc.print(f"This is one of the prints_charming foreground colors in the color map. ### Name: {color_name}", color=color_name)
    pc.print()


@time_step
def print_background_colors(pc, builder):
    for color in pc.color_map.keys():
        if builder.vert_char == ' ':
            bg_vert_border_left = builder.pc.apply_bg_color(color, builder.vert_border) + builder.vert_padding
            bg_vert_border_right = builder.vert_padding + builder.pc.apply_bg_color(color, builder.vert_border)
        else:
            bg_vert_border_left = builder.pc.apply_color(color, builder.vert_border) + builder.vert_padding
            bg_vert_border_right = builder.vert_padding + builder.pc.apply_color(color, builder.vert_border)

        bg_available_width = builder.get_available_width()
        pc.print()

        bg_bar_strip = pc.generate_bg_bar_strip(color, length=bg_available_width)
        bg_bar_center_aligned = builder.align_text(bg_bar_strip, bg_available_width, 'center')
        pc.print(f"{bg_vert_border_left}{bg_bar_center_aligned}{bg_vert_border_right}")


@time_step
def print_styles(pc, builder):
    pc.print()
    for style_name in pc.styles.keys():
        if builder.vert_char == ' ':
            color = style_name if builder.pc.bg_color_map.get(style_name) else builder.pc.styles.get(style_name).bg_color if not builder.pc.styles.get(
                style_name).reverse else builder.pc.styles.get(style_name).color
            if not color:
                color = builder.pc.styles.get(style_name).color
            print_styles_vert_border_left = builder.pc.apply_bg_color(color, builder.vert_border) + builder.vert_padding
            print_styles_vert_border_right = builder.vert_padding + builder.pc.apply_bg_color(color, builder.vert_border)
        else:
            print_styles_vert_border_left = builder.pc.apply_style(style_name, builder.vert_border) + builder.vert_padding
            print_styles_vert_border_right = builder.vert_padding + builder.pc.apply_style(style_name, builder.vert_border)

        available_width = builder.get_available_width()
        pc.print()

        text = f"This is one of the prints_charming defined styles! # Name: {style_name}"
        text_center_aligned = builder.pc.apply_style(style_name, builder.align_text(text, available_width, 'center'))
        pc.print(f'{print_styles_vert_border_left}{text_center_aligned}{print_styles_vert_border_right}')


@time_step
def print_colors_and_styles():
    pc = PrintsCharming()
    builder = FrameBuilder(pc=pc, horiz_char='|', vert_width=5, vert_padding=1, vert_char='|')

    print_foreground_colors(pc, builder)
    print_background_colors(pc, builder)
    print_styles(pc, builder)




def accuracy_style_function(accuracy):
    if accuracy > 0.9:
        return "vgreen"  # Very good accuracy
    elif 0.8 < accuracy <= 0.9:
        return "green"  # Good accuracy
    else:
        return "red"  # Poor accuracy


def precision_style_function(precision):
    if precision < 0.75:
        return "red"  # Low precision
    return None  # No style for acceptable precision


def recall_style_function(recall):
    if recall > 0.9:
        return "vgreen"  # High recall
    elif 0.75 < recall <= 0.9:
        return "yellow"  # Medium recall
    else:
        return "red"  # Low recall


def f1_score_style_function(f1_score, row):
    accuracy = row[1]  # Assume accuracy is the second column
    if abs(f1_score - accuracy) <= 0.05:
        return "blue"  # F1 score close to accuracy
    return None


def training_time_style_function(training_time):
    if training_time > 300:
        return "orange"  # Long training time
    return None


def age_style_function(age):
    if age < 18:
        return "vred"
    elif age < 21:
        return "green"
    elif age >= 21:
        return "vgreen"
    return None



def name_style_function(name):
    if name in ["Prince Charming", "John Smith"]:
        return "blue"
    elif name in ["Cinderella", "Anastasia", "Drizella", "Ariel"]:
        return "pink"
    return None


def occupation_style_function(occupation):
    if occupation in ['Prince', 'Princess']:
        return "orange"
    elif occupation == "Mermaid":
        return "vyellow"
    elif occupation == "Socialite":
        return "cyan"
    elif occupation not in ['Prince', 'Princess']:
        return "gray"
    return None


@time_step
def create_style_table_data(pc: PrintsCharming):
    table_data = [["Style Name", "Styled Text", "Styled Definition"]]
    for style_name, style_definition in pc.styles.items():
        styled_text_example = "Styled Text Example"
        # Filter the enabled attributes and format the definition
        enabled_attribs = {k: v for k, v in vars(style_definition).items() if v not in (None, False)}
        enabled_definition = f"PStyle({', '.join(f'{k}={repr(v)}' for k, v in enabled_attribs.items())})"
        table_data.append([style_name, styled_text_example, enabled_definition])
    return table_data


@time_step
def create_color_table_data(pc: PrintsCharming):
    table_data = [["Color Name", "Foreground Text", "Background Block"]]
    for color_name in pc.color_map.keys():
        fg_example = "Foreground Colored Text"
        bg_example = pc.generate_bg_bar_strip(color_name, length=10)
        table_data.append([color_name, fg_example, bg_example])
    return table_data


@time_step
def welcome():
    # None of these parameters are required for simple use cases as will be shown soon. You can simply init PrintsCharming with pc_instance = PrintsCharming()
    # To interactively create your own color_map where you can pick and name your own colors and default color do python -m prints_charming.show_colors. The point of this is to
    # show various ways to align text and tables and objects within boxes and tables. More on it later and some of the box methods will be weeded out.
    style_conditions = StyleConditionsManager()
    pc = PrintsCharming(style_conditions=style_conditions)

    # Create an instance of FrameBuilder
    builder = FrameBuilder(pc=pc, horiz_char=' ', vert_width=2, vert_padding=1, vert_char=' ')

    available_width = builder.get_available_width()
    available_half_width = available_width // 2
    available_third_width = available_width // 3
    available_fourth_width = available_width // 4

    table_manager = TableManager(pc=pc)

    specific_headers_colors = {
        'Color Name': lambda cell_str, aligned_cell, row, row_idx, col_idx, max_length: pc.apply_color(cell_str, aligned_cell),
        'Foreground Text': lambda cell_str, aligned_cell, row, row_idx, col_idx, max_length: pc.apply_color(row[0], aligned_cell),
        'Background Block': lambda cell_str, aligned_cell, row, row_idx, col_idx, max_length: pc.generate_bg_bar_strip(row[0], length=max_length),
    }

    @time_step
    def create_color_table_data2(pc: PrintsCharming):
        table_data = [list(specific_headers_colors)]
        for color_name in pc.color_map:
            fg_example = "Foreground Colored Text"
            bg_example = pc.generate_bg_bar_strip(color_name, length=10)
            table_data.append([color_name, fg_example, bg_example])
        return table_data


    colors_table_data = create_color_table_data2(pc)
    colors_table = table_manager.generate_table(
        table_data=colors_table_data,
        table_name="PrintsCharming Color Map",
        show_table_name=True,
        border_char="=",
        col_sep=" | ",
        header_style="magenta",
        border_style="white",
        col_sep_style="white",
        specific_headers=specific_headers_colors,
        target_text_box=True,
        double_space=True,
        ephemeral=True,
        append_newline=True,
    )

    specific_headers_styles = {
        'Style Name': lambda cell_str, aligned_cell, row, row_idx, col_idx, max_length: pc.apply_style(cell_str, aligned_cell),
        'Styled Text': lambda cell_str, aligned_cell, row, row_idx, col_idx, max_length: pc.apply_style(row[0], aligned_cell),
        'Style Definition': lambda cell_str, aligned_cell, row, row_idx, col_idx, max_length: pc.apply_style('default', aligned_cell)
    }

    @time_step
    def create_style_table_data2(pc: PrintsCharming):
        table_data = [list(specific_headers_styles)]
        for style_name, style_definition in pc.styles.items():
            styled_text_example = "Styled Text Example"
            # Filter the enabled attributes and format the definition
            enabled_attribs = {k: v for k, v in vars(style_definition).items() if v not in (None, False)}
            enabled_definition = f"PStyle({', '.join(f'{k}={repr(v)}' for k, v in enabled_attribs.items())})"
            table_data.append([style_name, styled_text_example, enabled_definition])
        return table_data



    styles_table_data = create_style_table_data2(pc)
    styles_table = table_manager.generate_table(
        table_data=styles_table_data,
        table_name="PStyle Style Map",
        show_table_name=True,
        border_char="=",
        col_sep=" | ",
        header_style="magenta",
        border_style="white",
        col_sep_style="white",
        specific_headers=specific_headers_styles,
        target_text_box=True,
        double_space=True,
        ephemeral=True,
        append_newline=True,
    )

    (horiz_border_top,
     vert_border_left,
     vert_border_inner,
     vert_border_right,
     horiz_border_bottom) = builder.build_styled_border_box2(style="dblue")



    """
    (horiz_border_top,
     vert_border_left,
     vert_border_right,
     horiz_border_bottom) = builder.build_styled_border_box(horiz_border_top_style=style_conditions.function_styles.welcome('border2', 'top'),
                                                            vert_border_left_style=style_conditions.function_styles.welcome('border2', 'left'),
                                                            vert_border_right_style=style_conditions.function_styles.welcome('border2', 'right'),
                                                            horiz_border_bottom_style=style_conditions.function_styles.welcome('border2', 'bottom'))
    """

    texts = []
    blank_line = 'invisible_text'
    title_border_top = '#' * builder.get_available_width()
    title = 'Prints Charming'
    subtitle = 'Hope you find the user guide examples helpful'
    subtitle2 = '#' * builder.get_available_width()
    texts.extend([blank_line, title_border_top, blank_line, title, subtitle, subtitle2, blank_line, blank_line])
    text_styles = ['default', 'purple', 'default', 'vgreen', 'white', 'orange', 'default', 'default']

    builder.print_border_boxed_text4(texts, text_styles=text_styles,
                                     horiz_border_top=horiz_border_top,
                                     vert_border_left=vert_border_left,
                                     vert_border_right=vert_border_right,
                                     horiz_border_bottom=horiz_border_bottom,
                                     table_strs=[colors_table], table_strs_alignments=['left'],
                                     horiz_border_height=1)

    print()

    # Print the table within a border box
    builder.print_border_boxed_table(colors_table,
                                     horiz_border_top,
                                     vert_border_left,
                                     vert_border_right,
                                     horiz_border_bottom,
                                     text_style="default",
                                     text_align="right")

    print()

    # Print the table within a border box
    builder.print_border_boxed_table(styles_table,
                                     horiz_border_top,
                                     vert_border_left,
                                     vert_border_right,
                                     horiz_border_bottom,
                                     text_style="default",
                                     text_align="center")

    print()
    print(horiz_border_top)

    texts = []
    blank_line = 'invisible_text'  # I want to instead use blank_line = ' '
    title_border_top = '#' * builder.get_available_width()
    title = 'Prints Charming'
    subtitle = 'Hope you find the user guide examples helpful'
    subtitle2 = '#' * builder.get_available_width()
    texts.extend([blank_line, title_border_top, blank_line, title, subtitle, subtitle2, blank_line, blank_line])
    text_styles = ['default', 'purple', 'default', 'vgreen', 'white', 'orange', 'default', 'default']

    builder.print_border_boxed_text4(texts, text_styles=text_styles,
                                     horiz_border_top=horiz_border_top,
                                     vert_border_left=vert_border_left,
                                     vert_border_right=vert_border_right,
                                     horiz_border_bottom=horiz_border_bottom,
                                     table_strs=[colors_table, colors_table], table_strs_alignments=['left', 'right'])
    print(horiz_border_bottom)
    print()

    table_data = [
        ["Name", "Age", "Occupation"],
        ["Prince Charming", 25, "Prince"],
        ["Cinderella", 18, "Princess"],
        ["Anastasia", 22, "Socialite"],
        ["Drizella", 20, "Socialite"],
        ["Ariel", 16, "Mermaid"],
        ["John Smith", 17, "Normie"]
    ]

    simple_table = table_manager.generate_table(table_data=table_data,
                                                header_style="magenta",
                                                border_style="vgreen",
                                                col_sep_style="vgreen",
                                                target_text_box=True,
                                                cell_style="header_text",
                                                ephemeral=True,
                                                append_newline=True,)
    print(simple_table)

    less_simple_table = table_manager.generate_table(table_data=table_data,
                                                     header_style="magenta",
                                                     border_style="vgreen",
                                                     col_sep_style="vgreen",
                                                     target_text_box=True,
                                                     cell_style=["orange", "purple"],
                                                     ephemeral=True,
                                                     append_newline=True,
                                                      )
    print(less_simple_table)

    builder.print_border_boxed_tables2([less_simple_table, less_simple_table, less_simple_table, less_simple_table],
                                       horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom,
                                       table_alignments=['center', 'center', 'center', 'center'])

    conditional_style_functions1 = {
        "Age": age_style_function,
        "Name": name_style_function,
        "Occupation": occupation_style_function
    }

    complex_table = table_manager.generate_table(
        table_data=table_data,
        table_name="Fairy Tale Characters:",
        show_table_name=True,
        header_style="magenta",
        border_style="vgreen",
        col_sep_style="vgreen",
        target_text_box=True,
        cell_style=["orange", "purple"],
        conditional_style_functions=conditional_style_functions1,
        ephemeral=True,
        append_newline=True,
    )

    print(complex_table)

    really_complex_table_data = [
        ["Model", "Accuracy", "Precision", "Recall", "F1 Score", "Training Time (s)"],
        ["Model A", 0.92, 0.88, 0.90, 0.89, 240],
        ["Model B", 0.85, 0.80, 0.82, 0.81, 180],
        ["Model C", 0.78, 0.75, 0.70, 0.72, 300],
        ["Model D", 0.95, 0.92, 0.94, 0.93, 420]
    ]

    conditional_style_functions = {
        "Accuracy": accuracy_style_function,
        "Precision": precision_style_function,
        "Recall": recall_style_function,
        "F1 Score": lambda f1_score, row: f1_score_style_function(f1_score, row),  # Pass the entire row for F1 Score logic
        "Training Time (s)": training_time_style_function
    }

    column_styles = {
        5: 'white',
    }

    really_complex_table_str = table_manager.generate_table(
        table_data=really_complex_table_data,
        conditional_style_functions=conditional_style_functions,
        header_style="magenta",
        border_style="vgreen",
        col_sep_style="vgreen",
        show_table_name=True,
        table_name="ML Model Performance Summary",
        target_text_box=True,
        default_column_styles=column_styles,
        cell_style=["orange", "purple"],
        ephemeral=True,
        append_newline=True,
    )

    print(really_complex_table_str)
    print('\n\n\n\n\n')



    pc.print(f'live_update_bound_cells:\n\n', style='orange')

    """
    bound_data_values = {
        "temperature": 25.0,
        "humidity": 40.0,
        "pressure": 1013.25,
    }

    def get_temperature(data):
        data["temperature"] += random.uniform(-0.5, 0.5)
        return round(data["temperature"], 2)

    def get_humidity(data):
        data["humidity"] += random.uniform(-1, 1)
        return round(data["humidity"], 2)

    def get_pressure(data):
        data["pressure"] += random.uniform(-0.2, 0.2)
        return round(data["pressure"], 2)


    # Example usage
    bound_table_data = [
        ["Metric", "Value"],
        ["Temperature (°C)", BoundCell(lambda: get_temperature(bound_data_values))],
        ["Humidity (%)", BoundCell(lambda: get_humidity(bound_data_values))],
        ["Pressure (hPa)", BoundCell(lambda: get_pressure(bound_data_values))],
    ]

    def value_style_function(value):
        if value > 50:
            return 'vgreen'
        else:
            return 'red'

    bound_conditional_style_functions = {
        "Value": value_style_function,
    }

    # Create an instance of TableManager
    table_manager = TableManager()

    gen_table_args = dict(
        table_data=bound_table_data,
        table_name="environmental_metrics",
        show_table_name=True,
        header_style="magenta",
        border_style="vgreen",
        col_sep_style="vgreen",
        target_text_box=True,
        cell_style=["orange", "purple"],
        conditional_style_functions=bound_conditional_style_functions,
        ephemeral=False,
        append_newline=True,
    )

    formatted_table = table_manager.add_bound_table(**gen_table_args)

    # Initial display setup
    os.system('clear')  # Clear terminal for fresh display

    print(formatted_table)


    # Update loop for selective cell updating
    try:
        while True:
            table_manager.refresh_bound_table("environmental_metrics")
            time.sleep(1)  # Adjust interval as needed
    except KeyboardInterrupt:
        print("\nLive update terminated.")
    """






    ################################################################################################################################
    # Logging Table
    ################################################################################################################################

    logs_table_data = [
        ["Timestamp", "Log Level", "Source", "Message"],
        ["2024-08-31 12:00:01", "INFO", "auth-service", "User login successful: user123"],
        ["2024-08-31 12:01:15", "WARN", "auth-service", "User login attempt failed: user456"],
        ["2024-08-31 12:02:30", "ERROR", "payment-service", "Payment processing error: ERR1234"],
        ["2024-08-31 12:03:45", "INFO", "payment-service", "Payment processed successfully for order 789"],
        ["2024-08-31 12:04:50", "DEBUG", "inventory-service", "Checking inventory levels for item 567"],
        ["2024-08-31 12:05:55", "ERROR", "inventory-service", "Inventory level check failed: OUT_OF_STOCK"]
    ]


    def log_level_style_function(log_level):
        level_styles = {
            "INFO": "blue",
            "WARN": "yellow",
            "ERROR": "red",
            "DEBUG": "gray"
        }
        return level_styles.get(log_level, None)

    def source_style_function(source):
        if "auth-service" in source:
            return "cyan"  # Highlight authentication service logs
        elif "payment-service" in source:
            return "magenta"  # Highlight payment service logs
        elif "inventory-service" in source:
            return "green"  # Highlight inventory service logs
        return None

    def message_style_function(message):
        if "successful" in message.lower():
            return "vgreen"  # Success messages in green
        elif "failed" in message.lower():
            return "vred"  # Failure messages in red
        elif "error" in message.lower():
            return "red"  # Error messages in red
        elif "out_of_stock" in message.upper():
            return "orange"  # Specific error codes in orange
        return None

    logs_style_functions = {
        "Log Level": log_level_style_function,
        "Source": source_style_function,
        "Message": message_style_function
    }

    header_column_styles = {
        0: 'white'
    }

    more_complex_table_str = table_manager.generate_table(
        table_data=logs_table_data,
        header_column_styles=header_column_styles,
        conditional_style_functions=logs_style_functions,
        header_style="header_main",

        border_style="vgreen",
        col_sep_style="vgreen",
        show_table_name=True,
        table_name="System Log Summary",
        target_text_box=True,
        default_column_styles={3: 'white'},
        cell_style="white",
        double_space=True,
        append_newline=True,
    )

    print(more_complex_table_str)

    builder = FrameBuilder(pc=pc, horiz_width=100, horiz_char=' ', vert_width=5, vert_padding=1, vert_char='|')
    horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom = builder.build_styled_border_box(horiz_border_top_style=style_conditions.welcome_style('top'),
                                                                                                                 vert_border_left_style=style_conditions.welcome_style('left'),
                                                                                                                 vert_border_right_style=style_conditions.welcome_style(
                                                                                                                     'right'),
                                                                                                                 horiz_border_bottom_style=style_conditions.welcome_style(
                                                                                                                     'bottom'))

    builder.print_border_boxed_table(less_simple_table, horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom, text_style="default", text_align="right")
    builder.print_border_boxed_table(less_simple_table, horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom, text_style="default", text_align="center")
    builder.print_border_boxed_table(less_simple_table, horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom, text_style="default", text_align="left")


@time_step
def experiment():
    style_conditions = StyleConditionsManager()
    pc = PrintsCharming(style_conditions=style_conditions)

    table_manager = TableManager(pc=pc)

    # Create an instance of FrameBuilder
    builder = FrameBuilder(pc=pc, horiz_char=' ', vert_width=2, vert_padding=1, vert_char=' ')

    (horiz_border_top,
     vert_border_left,
     vert_border_right,
     horiz_border_bottom) = builder.build_styled_border_box(horiz_border_top_style='dblue',
                                                            vert_border_left_style='vblue',
                                                            vert_border_right_style='dblue',
                                                            horiz_border_bottom_style='vblue')


# Define the markdown printer using def
@time_step
def create_markdown_printer(pc_instance):
    def printer(*args, **kwargs):
        pc_instance.print_markdown(*args, sep=' ', **kwargs)

    return printer


@time_step
def print_markdown(pc):
    printer = create_markdown_printer(pc)
    md_text = """
    # Header 1
    This is **bold** and *italic* text.

    ## Header 2
    - List item 1
    - List item 2

    [prints_charming Documentation](https://github.com/deefifofun/prints_charming)

    Inline code: `print("Hello, World!")`

    ```python

    def hello(arg1, enable_print=True, sep=' '):
        # code comment
        if not enable_print:
            return arg1
        else:
            print(f"{arg1}{sep}no other args!")

    greeting = "Hello, World!"    
    result = hello(greeting, enable_print=False)
    print(result)
    hello(greeting)
    ```
    """

    print()
    printer(md_text)
    print('\n\n')



def example_dynamic_formatter():
    # Example usage
    formatter = DynamicFormatter()

    formatter_style_names = {
        'neg': 'vred',
        'pos': 'vgreen',
        'zero': 'blue',
    }

    formatter.styles = formatter_style_names

    # Format multiple strings and write them to stdout
    formatter.set_width(30)
    string1 = formatter.format("First formatted string", tabs=1)
    string2 = formatter.format("Second formatted string", tabs=2)
    string3 = formatter.format("Third formatted string", tabs=2)

    # Write all formatted strings at once (with newlines) to stdout
    formatter.write(string1, end='\n')
    formatter.write(string2, end='\n')
    formatter.write(string3, end='\n\n')

    # String formatting with newlines and tabs using sys.stdout.write
    formatter.set_width(10)
    string1 = formatter.format("Text with 2 tabs and newline", tabs=2, newlines=1)
    formatter.write(string1, end='\n')

    # Multi-line text with wrapping and indentation
    text_block = "This text will wrap at a specified width and be indented with tabs."
    formatter.set_width(15)
    multiple_lines = formatter.format_multiline(text_block, width=15, tabs=1)
    for line in multiple_lines:
        sys.stdout.write(line)

    print(f'\tAfter manual write multiple lines\n\n')

    formatter.write(multiple_lines, start="Start:\n", end="\nEnd.\n\n\n", spacing=0)

    # Conditional formatting for a negative number
    neg_string = formatter.conditional_format(-42, pc)
    print(neg_string)

    # Conditional formatting for a positive number
    pos_string = formatter.conditional_format(42, pc)
    print(pos_string)

    # Conditional formatting for zero
    zero_string = formatter.conditional_format(0, pc)
    print(zero_string)

    # Formatting datetime objects
    formatter.set_datetime_format('%d-%b-%Y %H:%M:%S')
    dt_now = formatter.format(datetime.now(), newlines=1)

    formatter.write(dt_now)

    # Set left and right padding characters, fill char, and format a string
    formatter.set_pad_char_left('*')
    formatter.set_pad_char_right('#')
    formatter.set_fill_char('-')
    formatter.set_width(20)
    padded_string = formatter.format("Padded String", tabs=1)

    # Write the formatted string with padding applied
    formatter.write(padded_string, end='\nEnd.\n\n\n')

    # Uniform single spacing after each item
    formatter.write(["Line 1", "Line 2", "Line 3"], start="<<", end=">>", spacing=1)

    # Cyclical pattern for spacing (1 newline after first, 2 after second, 3 after third)
    formatter.write(["Item 1", "Item 2", "Item 3"], start="Start:\n", end="\nEnd.", spacing=[1, 2, 3])

    # Example tokens to format: characters, words, or phrases
    tokens = ["Hello", " ", "world", "!", "\nNext", " ", "line"]

    # Format each token incrementally, storing results in buffer
    formatter.format_token_by_token(tokens)

    # Get the final formatted string
    formatted_output = formatter.get_formatted_buffer()

    # Output the final result
    print(formatted_output)
    print(f'\n\n\n')

    pc2 = PrintsCharming(styled_strings=styled_strings2)

    print_statements = [
        f'This is some green text with other colors too like, New Message, Reading',
        f'This is some red text with other colors too like, Hello, world!',
        f'This is some yellow text with other colors too like your',
        f'This is more yellow text with other colors too like My color is purple',
        f'This is more red text with other colors too like, 1'
    ]

    pc2.print(*print_statements, start="Start:\n", end="\nEnd.\n", style='vgreen')
    print(f'\n\n\n')

    pc2.print2(*print_statements, start="Start:\n", end="\nEnd.\n", style='vgreen')
    print(f'\n\n\n')

    styles = ['green', 'red', 'yellow', 'yellow', 'red']
    pc2.print2(*print_statements, start="\nStart:\n\t", end="\nEnd.\n", sep='\n\n\t\t', style=styles, style_args_as_one=False)

    print_statements2 = [
        f'\tThis is some green text with other colors too like, New Message, Reading\n\n',
        f'\t\tThis is some red text with other colors too like, Hello, world!\n\n',
        f'\t\tThis is some yellow text with other colors too like your\n\n',
        f'\tThis is more yellow text with other colors too like My color is purple\n\n',
        f'\t\tThis is more red text with other colors too like, 1'
    ]

    styles = ['green', 'red', 'yellow', 'yellow', 'red']
    pc2.print2(*print_statements2, start="\nStart:\n", end="\nEnd.\n", sep='', style=styles, style_args_as_one=False)

    pc2.print2(*print_statements2, start="\nStart:\n", end="\nEnd.\n", sep='', color=styles, style_args_as_one=False)

    styled_args_list = pc2.print2(*print_statements2, start="", end="", sep='', style=styles, style_args_as_one=False, return_styled_args_list=True)

    # Uniform single spacing after each item
    formatter.write(styled_args_list, start="<<", end=">>", spacing=1)

    # Cyclical pattern for spacing (1 newline after first, 2 after second, 3 after third)
    formatter.write(["Item 1", "Item 2", "Item 3"], start="Start:\n", end="\nEnd.", spacing=[1, 2, 3])



def highlight(text, style_name=None, return_list=False):
    if not style_name:
        style_name = 'highlight_arg'

    if isinstance(text, str):
        return pc.apply_style(style_name, text)
    else:
        return pc.apply_indexed_styles(text, style_name, return_list=return_list)



class NewClass:

    @time_step
    def __init__(self, pc, instance_name, arg1):
        self.pc = pc
        self.class_name = self.__class__.__name__
        self.instance_name = instance_name
        self.arg1 = arg1
        self.logger = setup_logger(pc=pc, name=self.class_name)

    @time_step
    def highlight(self, text, style_name=None, return_list=False):
        if not style_name:
            style_name = 'highlight_arg'

        if isinstance(text, str):
            return self.pc.apply_style(style_name, text)
        else:
            return self.pc.apply_indexed_styles(text, style_name, return_list=return_list)


    @time_step
    def get_names(self):
        text_args = [self.class_name, self.instance_name, self.arg1]
        style_name = ['red', 'orange', 'yellow']
        highlighted_args = self.highlight(text_args, style_name=style_name, return_list=True)
        self.logger.debug('Getting name of class: {} from class_instance: {} with instance arg1 value: {}',
                          *highlighted_args)

        return self.class_name, self.instance_name, self.arg1



@time_step
def play_around_with_logging():
    logger = setup_logger(enable_unhandled_exception_logging=True)
    pc = logger.pc

    print()

    init_message = f"logger initialized with pc configuration:\n{pc.format_dict(pc.config)}"
    logger.debug(init_message)

    logger.debug("arg 1: {} and arg 2: {}", 'arg1 is a phrase!', 'arg2 is a phrase too!')

    logger.debug("Debugging information.")
    logger.info("General info.")
    logger.warning("Warning message.")
    logger.error("Error encountered.")
    logger.critical("Critical issue.")

    new_class = NewClass(pc, 'new_instance', 'my_arg')
    class_name, instance_name, arg1 = new_class.get_names()
    logger.debug(f"Retrieved class_name: {class_name}, instance_name: {instance_name}, and instance arg1: {arg1}.\n")

    pc.print(' ' * term_width + '\n', style="vmagenta", overline=True, underline=True)

    ###########################################################################################################

    # default_bg_color set to match jupyter notebook background in pycharm
    logger2 = setup_logger(name='scratch', default_bg_color='jupyter', enable_unhandled_exception_logging=True)

    init_message = f"logger2 initialized with pc configuration:\n{logger2.pc.format_dict(logger2.pc.config)}"
    logger2.debug(init_message)

    logger2.info(f"default_bg_color is set to 'jupyter' for this instance of PrintsCharming.")
    logger2.debug("arg 1: {} and arg 2: {}", 'arg1 is a phrase!', 'arg2 is a phrase too!')

    logger2.debug("Debugging information.")
    logger2.info("General info.")
    logger2.warning("Warning message.")
    logger2.error("Error encountered.")
    logger2.critical("Critical issue.")
    print('\n')

    pc.print(' ' * term_width + '\n', style="vmagenta", overline=True, underline=True)

    return logger, logger2


@time_step
def set_shared_pc_exception_instance():
    PrintsCharmingException.shared_pc_instance = PrintsCharming()



@time_step
def custom_errors_orig(loggers):

    for logger in loggers:

        try:
            # Raise a CustomError
            raise CustomError(f"CustomError occurred!", logger.pc, f"Context for CustomError")
        except CustomError as e:
            logger.error(f"Error caught: {e}")


        try:
            # Raise a CustomError
            raise CustomError("CustomError occurred!", logger.pc, "Context for CustomError")
        except CustomError as e:
            logger.error(f"Error caught: {e}")


@time_step
def custom_errors_2(logger1):
    CustomError2.set_pc(pc)

    # Raise CustomError2 with logger1's PrintsCharming instance (subclass-specific)
    try:
        raise CustomError2("Error in CustomError2", additional_info="Context for CustomError2")
    except CustomError2 as e:
        e.handle_exception()

    try:
        raise CustomError2("Custom error occurred!", additional_info="Logging CustomError2")
    except CustomError2 as e:
        logger1.error(f"Error caught: {e}")

    # Change pc_instance
    CustomError2.set_pc(pc)

    # Raise CustomError2 using the shared PrintsCharming instance
    try:
        raise CustomError2("Error in CustomError2 (Shared)", additional_info="Shared context for CustomError2", use_shared_pc=True)
    except CustomError2 as e:
        e.handle_exception()


@time_step
def custom_errors_3():
    # Raise CustomError3 with logger2's PrintsCharming instance (subclass-specific)
    try:
        raise CustomError3("Error in CustomError3", additional_info="Context for CustomError3", pc_error=pc, use_shared_pc=True)
    except CustomError3 as e:
        e.handle_exception()

    # Raise CustomError3 using the shared PrintsCharming instance
    try:
        raise CustomError3("Error in CustomError3 (Shared)", additional_info="Shared context for CustomError3", use_shared_pc=True)
    except CustomError3 as e:
        e.handle_exception()


def custom_excepthook_error_example():
    zero_div_error = 1 / 0


def exception_examples(logger1, logger2, enable_custom_excepthook_error_example=False):
    # Set different PrintsCharming instances for each CustomError subclass
    CustomError2.set_pc(logger1.pc)
    CustomError3.set_pc(logger2.pc)

    loggers = [logger1, logger2]
    custom_errors_orig(loggers)
    custom_errors_2(logger1)
    custom_errors_3()

    # Default to False because script will exit
    if enable_custom_excepthook_error_example:
        custom_excepthook_error_example()



def live_realtime_updates():
    # Initialize data for 25 sensors
    sensor_data = {}
    for sensor_id in range(1, 26):
        sensor_data[sensor_id] = {
            "temperature": random.uniform(20, 30),
            "humidity": random.uniform(30, 70),
            "pressure": random.uniform(1000, 1020),
            "battery": random.uniform(50, 100),
            "status": "OK"
        }

    # Define functions to update each sensor's data
    def get_temperature(sensor_id):
        data = sensor_data[sensor_id]
        data["temperature"] += random.uniform(-0.5, 0.5)
        return round(data["temperature"], 2)

    def get_humidity(sensor_id):
        data = sensor_data[sensor_id]
        data["humidity"] += random.uniform(-1, 1)
        return round(data["humidity"], 2)

    def get_pressure(sensor_id):
        data = sensor_data[sensor_id]
        data["pressure"] += random.uniform(-0.2, 0.2)
        return round(data["pressure"], 2)

    def get_battery(sensor_id):
        data = sensor_data[sensor_id]
        data["battery"] -= random.uniform(0.1, 0.5)  # Battery drains over time
        data["battery"] = max(data["battery"], 0)  # Battery can't be negative
        return round(data["battery"], 2)

    def get_status(sensor_id):
        data = sensor_data[sensor_id]
        # If battery low, status changes
        if data["battery"] < 20:
            data["status"] = "Low Battery"
        else:
            data["status"] = "OK"
        return data["status"]

    # Function to create BoundCell with correct closure
    def make_bound_cell(func, sensor_id):
        return BoundCell(lambda s_id=sensor_id: func(s_id))

    # Create the table data with BoundCells
    bound_table_data = []

    # Header row
    bound_table_data.append(["Sensor ID", "Temperature (°C)", "Humidity (%)", "Pressure (hPa)", "Battery Level (%)", "Status"])

    # Rows for each sensor
    for sensor_id in range(1, 26):
        row = [
            sensor_id,
            make_bound_cell(get_temperature, sensor_id),
            make_bound_cell(get_humidity, sensor_id),
            make_bound_cell(get_pressure, sensor_id),
            make_bound_cell(get_battery, sensor_id),
            make_bound_cell(get_status, sensor_id),
        ]
        bound_table_data.append(row)

    # Define conditional style functions
    def battery_style_function(value):
        value = float(value)
        if value < 20:
            return 'red'
        elif value < 50:
            return 'yellow'
        else:
            return 'green'

    def status_style_function(value):
        if value == "Low Battery":
            return 'red'
        else:
            return 'green'

    bound_conditional_style_functions = {
        "Battery Level (%)": battery_style_function,
        "Status": status_style_function,
    }

    # Create an instance of TableManager
    table_manager = TableManager()

    gen_table_args = dict(
        table_data=bound_table_data,
        table_name="sensor_metrics",
        show_table_name=True,
        header_style="magenta",
        border_style="vgreen",
        col_sep_style="vgreen",
        target_text_box=True,
        cell_style=["orange", "purple"],
        conditional_style_functions=bound_conditional_style_functions,
        ephemeral=False,
        append_newline=True,
    )

    formatted_table = table_manager.add_bound_table(**gen_table_args)

    # Initial display setup
    os.system('clear')  # Clear terminal for fresh display

    print(formatted_table)

    # Update loop for selective cell updating
    try:
        while True:
            table_manager.refresh_bound_table("sensor_metrics")
            time.sleep(1)  # Adjust interval as needed
    except KeyboardInterrupt:
        print("\nLive update terminated.")



@time_total_execution
def main():

    #################################################
    # Logging
    #################################################
    logger1, logger2 = play_around_with_logging()

    #################################################
    # Exceptions
    # I may have introduced some breaking changes with customn exception logging i need to correct and will soon if need be
    # but haven't had time to test.
    #################################################
    exception_examples(logger1, logger2)

    #################################################
    # Random Examples
    #################################################
    random_examples()

    #################################################

    welcome()

    #pc = PrintsCharming(config={'internal_logging': True}) if internal_logging else PrintsCharming()
    builder = FrameBuilder(pc=pc, horiz_char='|', vert_width=5, vert_padding=1, vert_char='|')

    pc.add_string('function', 'blue')

    print_colors_and_styles()

    simple_use_case(pc)

    text_from_variable_examples = variable_examples(pc)
    index_styling_examples()
    auto_styling_examples(pc, text_from_variable_examples)
    print_variable_examples(pc)
    print_horizontal_bg_strip(pc)
    more_stuff()
    kwargs_replace_and_style_placeholders_examples()
    formatted_text_box_stuff()
    my_custom_error(pc)
    #progress_bar(pc)
    print_markdown(pc)

    example_menu()

    #uncomment for realtime updates example
    #live_realtime_updates()



    #example_dynamic_formatter()




def divide_term_width(divisor):
    return term_width // divisor



if __name__ == "__main__":
    PrintsCharming.set_shared_maps(shared_color_map=DEFAULT_COLOR_MAP.copy())
    term_width = os.get_terminal_size().columns
    pc = PrintsCharming()

    mini_border = '!' * divide_term_width(6)
    styled_mini_border = pc.apply_color('orange', mini_border)


    # Change pc_instance
    #CustomError2.set_pc(pc)

    try:
        main()
    except CustomError2 as e:
        print(f"Caught CustomError2: {e}")
        print(f"Additional info: {e.additional_info}")
        e.handle_exception()


