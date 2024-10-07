#!/usr/bin/env python3

from functools import partial


from prints_charming import (
    get_terminal_width,
    PStyle,
    PrintsCharming,
    DEFAULT_COLOR_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES,
    TableManager,
    FrameBuilder,
    InteractiveMenu,
    PrintsCharmingError,
    ColorNotFoundError,
    set_custom_excepthook,
    colors_map_one
)

from prints_charming.logging import PrintsCharmingFormatter, PrintsCharmingLogHandler, setup_logger

import os
import sys
import logging
import inspect





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


def triangle(pc_instance, height, start_char='*', sep='\n', prog_sep=' ', step=1, right=False, reversed=False, flipped_mirrored=False, mirrored=False, style=None):
    prog_direction = 'forward'
    start_spaces = ''

    if right:
        # Create the triangle where the pointed end is on the right
        #args = [(prog_sep * (height - i - 1)) + (start_char * (i + 1)) for i in range(height)]
        # Create the triangle without leading spaces for right alignment
        args = [(start_char * (i + 1)).rjust(height) for i in range(height)]
        #prog_sep = ''
    else:
        args = [start_char * (i + 1) for i in range(height)]

    if reversed:
        args = args[::-1]

    if flipped_mirrored:
        # Create the mirrored triangle with progressively fewer spaces and more asterisks
        args = [(prog_sep * i) + (start_char * (height - i)) for i in range(height)]

    if mirrored:
        # Create the mirrored triangle with progressively more leading spaces and fewer asterisks
        args = [(prog_sep * (height - i - 1)) + (start_char * (i + 1)) for i in range(height)]
        start_spaces = ' ' * (len(args) - step)
        prog_direction = "reverse"


    format_with_sep = pc_instance.format_with_sep(*args, sep=sep, prog_sep=prog_sep, prog_step=step, prog_direction=prog_direction, start=start_spaces)

    if style:
        format_with_sep = pc_instance.apply_style(style, format_with_sep)

    return format_with_sep


def equilateral_triangle(pc_instance, height, start_char='*', sep='\n', prog_sep=' ', step=1, mirrored=False, reversed=False, flipped=False):
    args = [prog_sep * (height - i - 1) + start_char * (2 * i + 1) for i in range(height)]

    if reversed:
        args = args[::-1]

    if mirrored:
        max_width = len(args[-1])
        args = [(prog_sep * (max_width - len(line))) + line for line in args]

    # Flip each line vertically
    if flipped:
        args = [line[::-1] for line in args]

    return pc_instance.format_with_sep(*args, sep=sep, prog_sep='', prog_step=step)


def diamond_shape(pc_instance, height, start_char='*', sep='\n', prog_sep=' ', step=1, flipped=False):
    top = [prog_sep * (height - i - 1) + start_char * (2 * i + 1) for i in range(height)]
    bottom = [prog_sep * (i + 1) + start_char * (2 * (height - i - 1) - 1) for i in range(height - 1)]
    args = top + bottom

    if flipped:
        args = [line[::-1] for line in args]

    return pc_instance.format_with_sep(*args, sep=sep, prog_sep='', prog_step=step)


def make_box():
    pass


def get_current_function_name():
    return inspect.currentframe().f_back.f_code.co_name


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
            "welcome": self.welcome_style
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

    def welcome_style(self, position: str) -> str:
        return "purple" if position in ['top', 'right'] else "orange"


class CustomError(PrintsCharmingError):
    """Custom error for specific use cases."""

    def __init__(self, message: str, pc: 'PrintsCharming', additional_info: str):
        super().__init__(message, pc, pc.apply_style)
        self.additional_info = additional_info

    def handle_exception(self):
        super().handle_exception()
        print(self.pc.apply_style('cyan', self.additional_info), file=sys.stderr)


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
    print(styled_mini_border)
    print()
    try:
        message = f'A custom error occurred'
        styled_message = pc.apply_style('purple', message)
        raise CustomError(styled_message, pc, "Additional context-specific information")
    except CustomError as e:
        e.handle_exception()


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
    print(orange_horiz_border)
    print()

    title_left_aligned = pc.apply_style('vgreen', builder.align_text(title, available_width, 'left'))
    subtitle_left_aligned = pc.apply_style('white', builder.align_text(subtitle, available_width, 'left'))

    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_left_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_left_aligned}{purple_vert_border}')
    print(orange_horiz_border)
    print()

    title_right_aligned = pc.apply_style('vgreen', builder.align_text(title, available_width, 'right'))
    subtitle_right_aligned = pc.apply_style('white', builder.align_text(subtitle, available_width, 'right'))

    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_right_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_right_aligned}{purple_vert_border}')
    print(orange_horiz_border)
    print()

    print()
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
    print(horiz_border_bottom)
    print()
    print()

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
    print(orange_horiz_border)
    print()

    print()
    print()
    print()

    pc.print('These will purposely cause an error that is styled', color='vgreen')
    print()
    print()
    print_horizontal_bg_strip(pc)

    my_custom_error(pc)
    print()
    print()

    # Print a simple border boxed text for the welcome message in the welcome function
    builder.print_simple_border_boxed_text("Prints Charming", subtitle="Hope you find the user guide helpful!", align='center')

    print()


def progress_bar(pc):
    print("Starting process...")
    pc.print_progress_bar()
    print("\nProcess complete.")


# Dynamic Value Functions
def get_dynamic_name():
    return "John Doe"


def get_dynamic_age():
    return 20


def get_dynamic_balance():
    return 5


def get_dynamic_occupation():
    return "Software Developer"


def kwargs_replace_and_style_placeholders_examples():
    pc = PrintsCharming(style_conditions=StyleConditionsManager(), styled_strings=styled_strings)

    # Assign dynamic values to my_kwargs
    my_kwargs = {
        "name": get_dynamic_name(),
        "age": get_dynamic_age(),
        "balance": get_dynamic_balance(),
        "occupation": get_dynamic_occupation(),
    }

    my_text = "Hello, {name}. You are {age} years old, your occupation is {occupation}, and you have {balance} USD in your account."

    pc.print(my_text, **my_kwargs)  # print my_text directly thru the PrintCharming print method

    colored_text = pc.replace_and_style_placeholders(text=my_text, kwargs=my_kwargs)  # return the styled text from the method
    print(colored_text)  # print the styled text with standard python print

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

    pc.print(structured_text, **my_kwargs)  # print with the PrintsCharming print method. This will be directed to the replace_and_style_placeholders method because of the kwargs

    styled_structured_text = pc.replace_and_style_placeholders(text=structured_text, kwargs=my_kwargs)  # return the styled text from the method

    print(f'reg print command styled_structured_text:')
    print(styled_structured_text)

    print(f'pc.print(structured_text):')
    pc.print(structured_text,
             color='silver')  # print with the PrintsCharming print method. This will not be directed to the replace_and_style_placeholders method because no kwargs

    print()
    print()
    print()

    # Create a partial function with specific parameters
    custom_style_with_params = partial(custom_style_function, label_style='main_bullets', label_delimiter=':', pc=pc)

    # Usage example
    custom_replace_and_style_placeholders = pc.replace_and_style_placeholders(structured_text, my_kwargs, style_function=custom_style_with_params)

    print(f'result of custom function with replace_and_style_placeholders method:')
    print(custom_replace_and_style_placeholders)


def add_styled_substrings_to_instance(pc):
    pc.add_subword('please', 'yellow')
    pc.add_subword('substring', 'vyellow')
    pc.add_subword('color', 'blue')
    pc.add_subword('apple', 'orange')
    pc.add_subword('pine', 'white')
    pc.add_subword('ex', 'vred')


def random_examples():
    # Create a preconfigured instance of PrintsCharming
    # The first couple print statements though ugly demonstrate the nuanced and highly customizable and unbreakable relationship between color, bg_color, underlines, overlines, etc
    # and how they are configured to behave in the spacing between words dependent on the share_alike parameters in the print statement, which default to what made the most sense to
    # me but is highly customizable for different use cases. Like when spacing/gaps/etc between words are filled with bg, underline etc they need to share fg_colors for underline,
    # bg_colors for bg_color in the space/gap/sep, the rules and relationships depend on the different styles associated with the indexes of the different
    # words/phrases/substrings/variables/numbers/other/styles/etc/highly dynamic and like i said configurable...legit documentation
    # to come. In the meantime you can keep as is or mess around with the PrintsCharming print method parameters.

    pc = PrintsCharming(styled_strings=styled_strings)

    add_styled_substrings_to_instance(pc)

    pc.print(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.", subword_style_option=5)

    print('\n\n')

    pc.print(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.", subword_style_option=1)

    print('\n\n')

    pc.print(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.", subword_style_option=2)

    print('\n\n')

    pc.print(f"This is an example text with the Some please tsubstring tsubstrings phrase hello world. This includes snapple.", subword_style_option=3)

    print('\n\n')

    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!',
        color='purple', subword_style_option=5)

    print('\n\n')

    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!',
        color='purple', subword_style_option=1)

    print('\n\n')

    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!',
        color='purple', subword_style_option=2)

    print('\n\n')

    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it this is a test is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!',
        color='purple', subword_style_option=2)

    print('\n\n')

    pc.print(
        f'Here    are    some examples of substringsse.     Some make the whole please word it this\nis\na test is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!\n',
        color='purple', phrase_norm=True, subword_style_option=2)




    term_width = os.get_terminal_size().columns

    pc.print(' ' * term_width, style="purple", overline=True, underline=True)
    print()

    pc.print(f' ' * term_width, color="default", bg_color="purple", bold=True, overline=True, underline=True)

    # Basic printing with ColorPrinter using default style and color
    pc.print("Hello, world!")

    # Print with default style reversed foreground and background colors
    pc.print("Hello, world!", reverse=True)

    my_style_code = pc.create_style_code(PStyle(color='green', bg_color='white', underline=True))

    my_style_code2 = pc.create_style_code(dict(color='orange', bg_color='white'))

    print(f'{my_style_code}Hello                 World!{pc.reset}')

    print(f'{my_style_code2}Hello                 World!{pc.reset}')

    my_style_code3 = pc.create_style_code(dict(color='blue', bg_color='white'))

    mytext3 = f'Hello World'

    mytext3_styled = pc.apply_style_code(my_style_code3, mytext3)

    print(mytext3_styled)

    pc.add_string('This phrase styled in green', 'green')
    pc.add_string("I'm completely yellow!", 'vyellow')
    pc.add_string('wordl', 'red')
    pc.add_string('Blue', 'blue')
    pc.add_string("orange phrase          white bg", 'orangewhite')

    pc.print(f"A single wordl styled red. This phrase styled in green Hello                     World.", f"I'm Blue mostly default styling I'm completely yellow! except that",
             '   orange phrase          white bg', color='green', bg_color='white', underline=True, overline=True, skip_ansi_check=True)

    pc.print(f"A single wordl styled red. This phrase styled in green Hello                     World.", f"I'm Blue mostly default styling I'm completely yellow! except that",
             '   orange phrase          white bg', color='green', underline=True, overline=True, skip_ansi_check=True)

    pc.print(mytext3_styled, skip_ansi_check=True)

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
    pc.print("This is a task.", style="task", color="green", underline=True)


def print_horizontal_bg_strip(pc):
    print(styled_mini_border)
    print(f'function: print_horizontal_bg_strip:')
    print(styled_mini_border)
    print()
    try:
        pc.print_bg('green', 50)
        pc.print_bg('vyellow')
        pc.print_bg('tree_color')
    except ColorNotFoundError as e:
        e.handle_exception()


def print_variable_examples(pc):
    print(styled_mini_border)
    print(f'function: print_variable_examples:')
    print(styled_mini_border)
    print()

    pc.print_variables("Hello {username}, your balance is {balance} USD.", text_style="yellow",
                       username=("Prince", "blue"), balance=(1000, "green"))

    pc.print_variables("Hello {var2}, your balance is {var1} USD.", text_style="yellow",
                       var1=(1000, "green"), var2=("Princess", "blue"))

    print()


def auto_styling_examples(pc, text):
    print(styled_mini_border)
    print(f'function: auto_styling_examples:')
    print(styled_mini_border)
    print()
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
    pc.print("This string is connected to another", "string", color='vyellow')
    print()


def index_styling_examples(pc):
    print(styled_mini_border)
    print(f'function: index_styling_examples:')
    print(styled_mini_border)
    print()
    indexed_style = {
        1: "vgreen",
        (2, 4): "blue",
        (5, 6): "yellow",
        7: "purple",
        (8, 10): "pink"
    }
    pc.print("These, words are going to be styled by their indexes.", style=indexed_style)
    print()

    index_styled_text = pc.style_words_by_index("These, words are going to be styled by their indexes.", indexed_style)
    print(index_styled_text)
    print()
    print()
    print()

    text = f'This is a sentence where the way we determine 1 how and 2 where the text gets styled depends on: where the word: that is the dictionary key falls within this text.'

    splits = dict(green='sentence', red='2', orange='gets', blue='word:', yellow='')
    styled_sentence = pc.segment_and_style(text, splits)
    print(styled_sentence)

    print()

    splits2 = dict(green='sentence', red=['2', 'word:'], blue='gets', yellow='')
    styled_sentence2 = pc.segment_and_style2(text, splits2)
    print(styled_sentence2)

    splitter_text = f' | This is a sentence | where the way we determine 1 how and 2 | where the text gets | styled depends on: where the word: | that is the dictionary key falls within this text. |'

    splitter_match = '|'
    splitter_swap = '|+|'
    splitter_show = True
    single_splitter_style = True
    splitter_style = 'vcyan' if single_splitter_style else ['vcyan', 'red', 'green', 'yellow', 'blue', 'orange']
    splitter_arms = True
    string_style = ['yellow', 'orange', 'purple', 'vgreen', 'blue']
    styled_sentence3 = pc.segment_with_splitter_and_style(splitter_text, splitter_match, splitter_swap, splitter_show, splitter_style, splitter_arms, string_style)
    print(styled_sentence3)


def variable_examples(pc):
    print(styled_mini_border)
    print(f'function: variable_examples:')
    print(styled_mini_border)
    print()
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
    pc.print("Hello, world!")
    print()

    return text



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
    pc.print("# Show that 'Hello, world!' isn't color or style defined.")
    pc.print("Hello, world!", end=ts)




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
        pc.print()
        pc.print(f'{fg_vert_border_left}{fg_text_center_aligned}{fg_vert_border_right}')

        # pc.print(f"This is one of the prints_charming foreground colors in the color map. ### Name: {color_name}", color=color_name)
    pc.print()


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

        bg_bar_strip = pc.return_bg(color, length=bg_available_width)
        bg_bar_center_aligned = builder.align_text(bg_bar_strip, bg_available_width, 'center')
        pc.print(f"{bg_vert_border_left}{bg_bar_center_aligned}{bg_vert_border_right}")


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


def print_colors_and_styles():
    pc = PrintsCharming()
    builder = FrameBuilder(pc=pc, horiz_char='|', vert_width=5, vert_padding=1, vert_char='|')

    print_foreground_colors(pc, builder)
    print_background_colors(pc, builder)
    print_styles(pc, builder)


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


def create_style_table_data(pc: PrintsCharming):
    table_data = [["Style Name", "Styled Text", "Styled Definition"]]
    for style_name, style_definition in pc.styles.items():
        styled_text_example = "Styled Text Example"
        # Filter the enabled attributes and format the definition
        enabled_attribs = {k: v for k, v in vars(style_definition).items() if v not in (None, False)}
        enabled_definition = f"PStyle({', '.join(f'{k}={repr(v)}' for k, v in enabled_attribs.items())})"
        table_data.append([style_name, styled_text_example, enabled_definition])
    return table_data


def create_color_table_data(pc: PrintsCharming):
    table_data = [["Color Name", "Foreground Text", "Background Block"]]
    for color_name in pc.color_map.keys():
        fg_example = "Foreground Colored Text"
        bg_example = pc.return_bg(color_name, length=10)
        table_data.append([color_name, fg_example, bg_example])
    return table_data


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

    colors_table_data = create_color_table_data(pc)
    colors_table = table_manager.generate_table(
        table_data=colors_table_data,
        table_name="PrintsCharming Color Map",
        show_table_name=True,
        border_char="=",
        col_sep=" | ",
        header_style="magenta",
        border_style="white",
        col_sep_style="white",
        target_text_box=True,
        double_space=True,
    )

    styles_table_data = create_style_table_data(pc)
    styles_table = table_manager.generate_table(
        table_data=styles_table_data,
        table_name="PStyle Style Map",
        show_table_name=True,
        border_char="=",
        col_sep=" | ",
        header_style="magenta",
        border_style="white",
        col_sep_style="white",
        target_text_box=True,
        double_space=True,
    )

    (horiz_border_top,
     vert_border_left,
     vert_border_right,
     horiz_border_bottom) = builder.build_styled_border_box(horiz_border_top_style=style_conditions.function_styles.welcome('border2', 'top'),
                                                            vert_border_left_style=style_conditions.function_styles.welcome('border2', 'left'),
                                                            vert_border_right_style=style_conditions.function_styles.welcome('border2', 'right'),
                                                            horiz_border_bottom_style=style_conditions.function_styles.welcome('border2', 'bottom'))

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

    simple_table = table_manager.generate_table(table_data=table_data, header_style="magenta", border_style="vgreen", col_sep_style="vgreen", target_text_box=True,
                                                cell_style="header_text")
    print(simple_table)

    less_simple_table = table_manager.generate_table(table_data=table_data, header_style="magenta", border_style="vgreen", col_sep_style="vgreen", target_text_box=True,
                                                     cell_style=["orange", "purple"])
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
        conditional_style_functions=conditional_style_functions1
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
        cell_style=["orange", "purple"]
    )

    print(really_complex_table_str)

    more_complex_table_data = [
        ["Timestamp", "Log Level", "Source", "Message"],
        ["2024-08-31 12:00:01", "INFO", "auth-service", "User login successful: user123"],
        ["2024-08-31 12:01:15", "WARN", "auth-service", "User login attempt failed: user456"],
        ["2024-08-31 12:02:30", "ERROR", "payment-service", "Payment processing error: ERR1234"],
        ["2024-08-31 12:03:45", "INFO", "payment-service", "Payment processed successfully for order 789"],
        ["2024-08-31 12:04:50", "DEBUG", "inventory-service", "Checking inventory levels for item 567"],
        ["2024-08-31 12:05:55", "ERROR", "inventory-service", "Inventory level check failed: OUT_OF_STOCK"]
    ]

    more_conditional_style_functions = {
        "Log Level": log_level_style_function,
        "Source": source_style_function,
        "Message": message_style_function
    }

    header_column_styles = {
        0: 'white'
    }

    more_complex_table_str = table_manager.generate_table(
        table_data=more_complex_table_data,
        conditional_style_functions=more_conditional_style_functions,
        header_style="header_main",
        header_column_styles=header_column_styles,
        border_style="vgreen",
        col_sep_style="vgreen",
        show_table_name=True,
        table_name="System Log Summary",
        target_text_box=True,
        default_column_styles={3: 'white'},
        cell_style="white",
        double_space=True
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
def create_markdown_printer(pc_instance):
    def printer(*args, **kwargs):
        pc_instance.print_markdown(*args, sep=' ', **kwargs)

    return printer


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
    print()
    print()


def print_shapes():
    print('\n\n')

    # Running test cases for the shapes
    left_triangle = triangle(quick_pc, 5, style='vgreen')
    left_mirrored = triangle(quick_pc, 5, mirrored=True, style='vgreen')
    right_triangle = triangle(quick_pc, 5, right=True, style='purple')
    right_mirrored = triangle(quick_pc, 5, right=True, mirrored=True, style='purple')

    equilateral = equilateral_triangle(quick_pc, 5)
    diamond = diamond_shape(quick_pc, 5)

    reversed_triangle = triangle(quick_pc, 5, reversed=True, style='purple')

    mirrored_equilateral = equilateral_triangle(quick_pc, 5, mirrored=True)
    reversed_equilateral = equilateral_triangle(quick_pc, 5, reversed=True)
    flipped_equilateral = equilateral_triangle(quick_pc, 5, flipped=True)

    flipped_diamond = diamond_shape(quick_pc, 5, flipped=True)

    print(f'left_triangle:\n{left_triangle}\n\n')
    print(f'left_mirrored:\n{left_mirrored}\n\n')
    print(f'right_triangle:\n{right_triangle}\n\n')
    print(f'right_mirrored:\n{right_mirrored}\n\n')
    print(f'Reversed Triangle:\n{reversed_triangle}\n\n')

    #print(f'equilateral:\n{equilateral}\n\n')
    #print(f'Mirrored Equilateral:\n{mirrored_equilateral}\n\n')
    #print(f'Reversed Equilateral:\n{reversed_equilateral}\n\n')
    #print(f'Flipped Equilateral:\n{flipped_equilateral}\n\n')

    #print(f'diamond:\n{diamond}\n\n')
    #print(f'Flipped Diamond:\n{flipped_diamond}\n\n')



def setup_logger2(pc, name=None):
    logger = logging.getLogger(__name__) if not name else logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = PrintsCharmingFormatter(
        pc=pc,
        datefmt='%Y-%m-%d %H:%M:%S.',
        level_styles={
            logging.DEBUG: 'debug',
            logging.INFO: 'info',
            logging.WARNING: 'warning',
            logging.ERROR: 'error',
            logging.CRITICAL: 'critical'
        }
    )

    handler = PrintsCharmingLogHandler(pc, formatter=formatter)
    logger.addHandler(handler)

    return logger


class NewClass():
    def __init__(self, pc, instance_name, arg1):
        self.pc = pc
        self.class_name = self.__class__.__name__
        self.instance_name = instance_name
        self.arg1 = arg1
        self.logger = setup_logger(pc=pc, name=self.class_name)

    def highlight(self, text, style_name='highlight_arg'):
        return self.pc.apply_style(style_name, text)

    def get_names(self):
        self.logger.debug('Getting name of class: {} from class_instance: {} with instance arg1 value: {}',
                          self.highlight(self.class_name), self.highlight(self.instance_name), self.highlight(self.arg1))

        return self.class_name, self.instance_name, self.arg1


def play_around_with_logging():
    pc = PrintsCharming(styles=DEFAULT_LOGGING_STYLES.copy())

    my_logger = setup_logger(pc, name='scratch')

    init_message = f"my_logger initialized with pc configuration:\n{pc.print_dict(pc.config)}"
    my_logger.debug(init_message)

    my_logger.debug("arg 1: {} and arg 2: {}", 'arg1 is a phrase!', 'arg2 is a phrase too!')

    my_logger.debug("Debugging information.")
    my_logger.info("General info.")
    my_logger.warning("Warning message.")
    my_logger.error("Error encountered.")
    my_logger.critical("Critical issue.")

    new_class = NewClass(pc, 'new_instance', 'my_arg')
    class_name, instance_name, arg1 = new_class.get_names()
    my_logger.debug(f"Successfully retrieved class_name: {class_name}, instance_name: {instance_name}, and instance arg1: {arg1}.")

    ###########################################################################################################

    my_logger2 = setup_logger()

    my_logger2.debug("arg 1: {} and arg 2: {}", 'arg1 is a phrase!', 'arg2 is a phrase too!')

    my_logger2.debug("Debugging information.")
    my_logger2.info("General info.")
    my_logger2.warning("Warning message.")
    my_logger2.error("Error encountered.")
    my_logger2.critical("Critical issue.")
    print()


def main():
    set_custom_excepthook()

    # uncomment to play around with logging
    #play_around_with_logging()

    random_examples()



    welcome()

    pc = PrintsCharming()
    builder = FrameBuilder(pc=pc, horiz_char='|', vert_width=5, vert_padding=1, vert_char='|')

    pc.add_string('function', 'blue')

    print_colors_and_styles()

    simple_use_case(pc)

    text_from_variable_examples = variable_examples(pc)
    index_styling_examples(pc)
    auto_styling_examples(pc, text_from_variable_examples)
    print_variable_examples(pc)
    print_horizontal_bg_strip(pc)
    more_stuff()
    kwargs_replace_and_style_placeholders_examples()
    formatted_text_box_stuff()
    my_custom_error(pc)
    progress_bar(pc)
    print_markdown(pc)
    print_shapes()



if __name__ == "__main__":
    PrintsCharming.set_shared_maps(shared_color_map=DEFAULT_COLOR_MAP)
    quick_pc = PrintsCharming()
    mini_border = '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    styled_mini_border = quick_pc.apply_color('orange', mini_border)
    main()

    # Cycle thru the options with 'n' or 'p' <enter> and then <enter> again on the selection
    menu_options = ["main_menu", "vert", "Option 1", "Option 2", "Option 3"]
    menu = InteractiveMenu('vcyan', menu_options, pc=quick_pc, confirmed_style='vgreen', alt_buffer=True)
    menu.run()





