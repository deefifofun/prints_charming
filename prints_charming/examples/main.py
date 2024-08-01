#!/usr/bin/env python3

from functools import partial


from prints_charming import (
    TextStyle,
    PrintsCharming,
    PrintsCharmingLogHandler,
    TableManager,
    FormattedTextBox,
    PrintsCharmingError,
    ColorNotFoundError,
    set_custom_excepthook
)

import os
import sys
import logging




# To run this script as a module inside the package. Navigate to the top-level directory and run
# python -m prints_charming.examples.main





printscharming_variables = {
    "vgreen": ["Hello, world!", "string", "Connected", "Loaded", "Monitor", "ABOVE THRESHOLD", "wss://advanced-trade-ws.coinbase.com", "Starting", "True", "C++", "substring"],
    "green": ["apple"],
    "vred": ["Error", "Failed", "None", "Skipping.", "Canceling", "Canceled", "Hobbies", "Skills", "False"],
    "blue": ["CoinbaseWebsocketClient", "server", "Python"],
    "yellow": ["1", "returned", "Flask", "Some",],
    "vyellow": ["File modified:", "File modified AGAIN", "subscribed", "=", "JavaScript"],
    "magenta": ["within 10 seconds.", "how", "React"],
    "cyan": ["|", "#", "are", "your", "Project Management System"],
    "orange": ["New Message!", "Prints", "Software Developer", "Prince Charming"],
    "purple": ["My color is purple", "Reading"],
    # Uncomment the next line to hide API keys or sensitive information
    # "conceal": [os.environ[key] for key in os.environ if "API" in key],
}


logging_styles = {
    "default": TextStyle(),
    "timestamp": TextStyle(color="white"),
    "class_name": TextStyle(color="dfff"),
    "method_name": TextStyle(color="lpurple"),
    "line_number": TextStyle(color="purple"),
    "debug": TextStyle(color="blue"),
    "info": TextStyle(color="green"),
    "warning": TextStyle(color="yellow"),
    "error": TextStyle(color="red"),
    "critical": TextStyle(color="vred", bold=True, italic=True),
    "dict_key": TextStyle(color="sky"),
    "dict_value": TextStyle(color="white"),
    "true": TextStyle(color="vgreen"),
    "false": TextStyle(color="vred"),
    'none': TextStyle(color="lpurple"),
    "int": TextStyle(color="cyan"),
    "float": TextStyle(color="vcyan"),
    "other": TextStyle(color="lav"),
}






class BorderBoxStyles:

    def __init__(self):
        self.themes = {

        }

class FunctionStyles:

    def __init__(self):
        pass

    def welcome(self, position: str) -> str:
        return "purple" if position in ['top', 'right'] else "orange"



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

    def __init__(self, message: str, cp: 'PrintsCharming', additional_info: str):
        super().__init__(message, cp, cp.apply_style)
        self.additional_info = additional_info

    def handle_exception(self):
        super().handle_exception()
        print(self.cp.apply_style('cyan', self.additional_info), file=sys.stderr)



def custom_style_function(text: str, label_style: str, label_delimiter: str, cp) -> str:
    lines = text.split('\n')
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        leading_whitespace = line[:len(line) - len(stripped_line)]

        if stripped_line.startswith('- ') and not stripped_line.endswith(label_delimiter):
            # Apply main bullet style
            parts = stripped_line.split(' ', 1)
            if len(parts) == 2:
                lines[i] = f"{leading_whitespace}{cp.get_style_code(label_style)}{parts[0]} {cp.reset}{cp.get_style_code('main_bullet_text')}{parts[1]}{cp.reset}"
        elif len(stripped_line) > 1 and stripped_line[0].isdigit() and stripped_line[1] == '.':
            # Apply number and period style, followed by phrase style
            parts = stripped_line.split('. ', 1)
            if len(parts) == 2:
                lines[i] = f"{leading_whitespace}{cp.get_style_code('numbers')}{parts[0]}.{cp.reset} {cp.get_style_code('sub_proj')}{parts[1]}{cp.reset}"
        elif stripped_line.startswith('- ') and stripped_line.endswith(label_delimiter):
            # Apply sub-bullet style
            parts = stripped_line.split(' ', 2)
            if len(parts) == 3:
                lines[i] = f"{leading_whitespace}{cp.get_style_code('sub_bullets')}{parts[1]} {cp.reset}{cp.get_style_code('sub_bullet_text')}{parts[2]}{cp.reset}"
        elif leading_whitespace.startswith('   '):
            # Apply sub-bullet sentence style
            words = stripped_line.split()
            if len(words) > 1:
                lines[
                    i] = f"{leading_whitespace}{cp.get_style_code('sub_bullet_title')}{words[0]} {cp.reset}{cp.get_style_code('sub_bullet_sentence')}{' '.join(words[1:])}{cp.reset}"

    return '\n'.join(lines)





def my_custom_error(cp):
    print(styled_mini_border)
    print(f'function: my_custom_erro:')
    print(styled_mini_border)
    print()
    try:
        message = f'A custom error occurred'
        styled_message = cp.apply_style('purple', message)
        raise CustomError(styled_message, cp, "Additional context-specific information")
    except CustomError as e:
        e.handle_exception()



def formatted_text_box_stuff():
    cp = PrintsCharming(config={"enable_logging": True}, style_conditions=StyleConditionsManager(), printscharming_variables=printscharming_variables, logging_styles=logging_styles)
    builder = FormattedTextBox(cp=cp, horiz_width=100, horiz_char=' ', vert_width=5, vert_padding=1, vert_char='|')

    horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom = builder.build_styled_border_box(horiz_border_top_style='purple',
                                                                                                                 horiz_border_bottom_style='orange',
                                                                                                                 vert_border_left_style='orange',
                                                                                                                 vert_border_right_style='purple')

    purple_horiz_border = cp.apply_style('purple', builder.horiz_border)
    orange_horiz_border = cp.apply_style('orange', builder.horiz_border)

    purple_vert_border = builder.vert_padding + cp.apply_style('purple', builder.vert_border)
    orange_vert_border = cp.apply_style('orange', builder.vert_border) + builder.vert_padding

    available_width = builder.get_available_width()

    title = 'Prints Charming'
    subtitle = 'Hope you find the user guide helpful'

    title_center_aligned = cp.apply_style('vgreen', builder.align_text(title, available_width, 'center'))
    subtitle_center_aligned = cp.apply_style('white', builder.align_text(subtitle, available_width, 'center'))

    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_center_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_center_aligned}{purple_vert_border}')
    print(orange_horiz_border)
    print()

    title_left_aligned = cp.apply_style('vgreen', builder.align_text(title, available_width, 'left'))
    subtitle_left_aligned = cp.apply_style('white', builder.align_text(subtitle, available_width, 'left'))

    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_left_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_left_aligned}{purple_vert_border}')
    print(orange_horiz_border)
    print()

    title_right_aligned = cp.apply_style('vgreen', builder.align_text(title, available_width, 'right'))
    subtitle_right_aligned = cp.apply_style('white', builder.align_text(subtitle, available_width, 'right'))

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

    one_col_string = cp.apply_style('vgreen', builder.align_text(one_col_text, available_width, align='center'))
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

    cp.print('These will purposely cause an error that is styled', color='vgreen')
    print()
    print()
    print_horizontal_bg_strip(cp)

    my_custom_error(cp)
    print()
    print()

    # Print a simple border boxed text for the welcome message in the welcome function
    builder.print_simple_border_boxed_text("Prints Charming", subtitle="Hope you find the user guide helpful!", align='center')

    print()




def progress_bar(cp):

    print("Starting process...")
    cp.print_progress_bar()
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


    cp = PrintsCharming(style_conditions=StyleConditionsManager(), printscharming_variables=printscharming_variables, logging_styles=logging_styles)


    # Assign dynamic values to my_kwargs
    my_kwargs = {
        "name": get_dynamic_name(),
        "age": get_dynamic_age(),
        "balance": get_dynamic_balance(),
        "occupation": get_dynamic_occupation(),
    }


    my_text = "Hello, {name}. You are {age} years old, your occupation is {occupation}, and you have {balance} USD in your account."

    cp.print(my_text, **my_kwargs)  # print my_text directly thru the PrintCharming print method

    colored_text = cp.replace_and_style_placeholders(text=my_text, kwargs=my_kwargs)  # return the styled text from the method
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

    cp.print(structured_text, **my_kwargs)  # print with the PrintsCharming print method. This will be directed to the replace_and_style_placeholders method because of the kwargs


    styled_structured_text = cp.replace_and_style_placeholders(text=structured_text, kwargs=my_kwargs)  # return the styled text from the method


    print(f'reg print command styled_structured_text:')
    print(styled_structured_text)

    print(f'cp.print(structured_text):')
    cp.print(structured_text, color='silver')  # print with the PrintsCharming print method. This will not be directed to the replace_and_style_placeholders method because no kwargs

    print()
    print()
    print()

    # Create a partial function with specific parameters
    custom_style_with_params = partial(custom_style_function, label_style='main_bullets', label_delimiter=':', cp=cp)

    # Usage example
    custom_replace_and_style_placeholders = cp.replace_and_style_placeholders(structured_text, my_kwargs, style_function=custom_style_with_params)

    print(f'result of custom function with replace_and_style_placeholders method:')
    print(custom_replace_and_style_placeholders)




def add_styled_substrings_to_instance(cp):
    cp.add_substring('please', 'yellow')
    # cp.add_substring('substring', 'vgreen')
    cp.add_substring('color', 'blue')
    cp.add_substring('apple', 'forest')
    cp.add_substring('ex', 'vred')


def random_examples():
    # Create a preconfigured instance of ColorPrinter
    # The first couple print statements though ugly demonstrate the nuanced and highly customizable and unbreakable relationship between color, bg_color, underlines, overlines, etc
    # and how they are configured to behave in the spacing between words dependent on the share_alike parameters in the print statement, which default to what made the most sense to
    # me but is highly customizable for different use cases. Like when spacing/gaps/etc between words are filled with bg, underline etc they need to share fg_colors for underline,
    # bg_colors for bg_color in the space/gap/sep, the rules and relationships depend on the different styles associated with the indexes of the different
    # words/phrases/substrings/variables/numbers/other/styles/etc/highly dynamic and like i said configurable if you understand the rules and relationships...legit documentation
    # to come. In the meantime you can keep as is or mess around with the PrintsCharming print method parameters.

    cp = PrintsCharming(printscharming_variables=printscharming_variables,logging_styles=logging_styles)

    add_styled_substrings_to_instance(cp)

    cp.print(f"This is an example text with the Some please phrase hello world. This includes snapple.")

    print()

    cp.print(f'Here    are    some examples of substrings.     Some make the whole please word it is part of colored others only color the substring. part of the word.     apple     snapple    pineapple!', color='purple')
    print()

    term_width = os.get_terminal_size().columns

    cp.print(' ' * term_width, style="purple", overline=True, underline=True)
    print()

    cp.print(f' ' * term_width, color="default", bg_color="purple", bold=True, overline=True, underline=True)

    # Basic printing with ColorPrinter using default style and color
    cp.print("Hello, world!")

    # Print with default style reversed foreground and background colors
    cp.print("Hello, world!", reverse=True)

    my_style_code = cp.create_style_code(TextStyle(color='green', bg_color='white', underline=True))

    my_style_code2 = cp.create_style_code(dict(color='orange', bg_color='white'))

    print(f'{my_style_code}Hello                 World!{cp.reset}')

    print(f'{my_style_code2}Hello                 World!{cp.reset}')

    my_style_code3 = cp.create_style_code(dict(color='blue', bg_color='white'))

    mytext3 = f'Hello World'

    mytext3_styled = cp.apply_my_new_style_code(my_style_code3, mytext3)

    print(mytext3_styled)

    cp.add_variable('This phrase styled in green', 'green')
    cp.add_variable("I'm completely yellow!", 'vyellow')
    cp.add_variable('wordl', 'red')
    cp.add_variable('Blue', 'blue')
    cp.add_variable("orange phrase          white bg", 'orangewhite')

    cp.print(f"A single wordl styled red. This phrase styled in green Hello                     World.", f"I'm Blue mostly default styling I'm completely yellow! except that",
             '   orange phrase          white bg', color='green', bg_color='white', underline=True, overline=True, skip_ansi_check=True)

    cp.print(f"A single wordl styled red. This phrase styled in green Hello                     World.", f"I'm Blue mostly default styling I'm completely yellow! except that",
             '   orange phrase          white bg', color='green', underline=True, overline=True, skip_ansi_check=True)

    cp.print(mytext3_styled, skip_ansi_check=True)

    some_var = 21

    # Print specifying only the color of the text
    cp.print("Hello, world!", color="red" if some_var < 21 else "green")

    # Print specifying italic and underline styles with default color
    cp.print("Hello, world!", italic=True, underline=True)

    # Print using a predefined style 'magenta' defined above
    cp.print("Hello, world!", style="magenta")

    # Print using a predefined style 'task' defined above
    cp.print("# Specify predefined style 'task' for printing. The 'task' style is defined above.")
    cp.print("This is a task.", style="task")

    # Print using a predefined style 'task' with color changed to green and underline
    cp.print("# Specify predefined style 'task' for printing but change color to green and underline to True.")
    cp.print("This is a task.", style="task", color="green", underline=True)





def print_horizontal_bg_strip(cp):
    print(styled_mini_border)
    print(f'function: print_horizontal_bg_strip:')
    print(styled_mini_border)
    print()
    try:
        cp.print_bg('tree_color')
    except ColorNotFoundError as e:
        e.handle_exception()



def print_variable_examples(cp):
    print(styled_mini_border)
    print(f'function: print_variable_examples:')
    print(styled_mini_border)
    print()
    vars_and_styles_dict = {
        "balance": (1000, "green"),
        "username": ("Prince", "blue")
    }
    cp.print_variables(vars_and_styles_dict, "Hello {username}, your balance is {balance} USD.", text_style="yellow")
    vars_and_styles_list = ([1000, "Princess"], ["green", "blue"])
    cp.print_variables(vars_and_styles_list, "Hello var2, your balance is var1 USD.", text_style="yellow")
    print()



def auto_styling_examples(cp, text):
    print(styled_mini_border)
    print(f'function: auto_styling_examples:')
    print(styled_mini_border)
    print()
    cp.add_variables_from_dict(printscharming_variables)
    cp.print("Let's first print, Hello, world! styled as described above.")
    cp.print("Let's first print, Hello, world! styled as described above and right here.", style="yellow")
    cp.print(f"{text} Remember we assigned, 'Hello, world!' to the 'text' variable above. Let's pretend we are Connected to wss://advanced-trade-ws.coinbase.com", color="blue")
    cp.print("These words are going to be styled by their indexes, Hello, world!", style={1: "vgreen", (2, 4): "blue", (5, 7): "yellow", (8, 10): "purple", (11, 12): "pink"})
    cp.print("Hello, world! These words are going to be styled by their indexes, Hello, world!", style={1: "vgreen", (2, 4): "blue", (5, 7): "yellow", (8, 11): "purple", (13, 14): "pink"}, color='red')
    cp.print("Hello, world! Only these words are going to be styled by their indexes, Hello, world!", style={(3, 4): "orange", (5, 7): "blue", (8, 9): "yellow", (10, 13): "purple", (14, 15): "pink"})
    cp.print("Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My color is purple! these words are default. server")
    cp.print("Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My color is purple these words are magenta. server", style='magenta')
    cp.print("Hello", "how are you?", sep="---", color='green')
    cp.print("This string is not connected to another", color='blue')
    cp.print("This string is connected to another", "string", color='vyellow')
    balance = 1.25
    cp.print("Check out this... ", text=f"Value: var USD", var=balance, tstyle='orange', vstyle='vgreen')
    print()



def index_styling_examples(cp):
    print(styled_mini_border)
    print(f'function: index_styling_examples:')
    print(styled_mini_border)
    print()
    cp.print("These words are going to be styled by their indexes.", style={1: "vgreen", (2, 4): "blue", (5, 6): "yellow", 7: "purple", (8, 10): "pink"})
    balance = 1.25
    cp.print(text=f"Value: var USD", var=balance, tstyle='orange', vstyle='vgreen')
    print()




def variable_examples(cp):
    print(styled_mini_border)
    print(f'function: variable_examples:')
    print(styled_mini_border)
    print()
    cp.print("# Use the add_variable method to add 'Hello, world!' to the phrases dictionary with 'vgreen' style.")
    cp.add_variable("Hello, world!", style_name="vgreen")
    cp.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
    cp.print("Hello, world!")
    cp.print("# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.")
    cp.remove_variable("Hello, world!")
    cp.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
    cp.print("Hello, world!")
    cp.print("# Define a variable.")
    text = "Hello, world!"
    cp.print(f"# Use the add_variable method to add {text} to the phrases dictionary with 'yellow' style.")
    cp.add_variable(text, style_name="yellow")
    cp.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
    cp.print(text)
    cp.print("# Show that 'Hello, world!' retains its style while other words are unstyled.")
    cp.print(f"This sentence says, {text}")
    cp.print("# Show how you can style other words alongside, 'Hello, world!'.")
    cp.print(f"This sentence says, {text}", style='task')
    cp.print("# Show how the order of the words doesn't matter.")
    cp.print(f"{text} Let me say that again, {text} {text} I said it again!", style="orange")
    cp.print("# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.")
    cp.remove_variable("Hello, world!")
    cp.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
    cp.print("Hello, world!")
    print()

    return text




def simple_use_case(cp):

    print(styled_mini_border)
    cp.print(f'function: simple_use_case:')
    print(styled_mini_border)
    print()

    cp.print("# Basic printing with ColorPrinter will print in the default style with default color.")
    cp.print("Hello, world!")
    cp.print("# Print in the default style reverse foreground and background.")
    cp.print("Hello, world!", reverse=True)
    cp.print("# Specify only the color of the args.")
    cp.print("Hello, world!", color="red")
    cp.print("# Specify only italic and underline will print in the default color.")
    cp.print("Hello, world!", italic=True, underline=True)
    cp.print("# Specify a predefined style 'magenta'. The 'magenta' style is defined above.")
    cp.print("Hello, world!", style="magenta")
    cp.print("# Specify predefined style 'task' for printing. The 'task' style is defined above.")
    cp.print("This is a task.", style="task")
    cp.print("# Specify predefined style 'task' for printing but change color to green and underline to True.")
    cp.print("This is a task.", style="task", color="green", underline=True)
    cp.print("Show text with bg_color:")
    cp.print("This has a bg_color", style="bg_color_green")
    cp.print("# Show that 'Hello, world!' isn't color or style defined.")
    cp.print("Hello, world!")
    print()







def more_stuff():

    pc = PrintsCharming(logging_styles=logging_styles)

    print(styled_mini_border)
    print(f'function: more_stuff')
    print(styled_mini_border)

    builder = FormattedTextBox(cp=pc, horiz_char='|', vert_width=2, vert_padding=1, vert_char='|')
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




def print_foreground_colors(cp, builder):
    for color in cp.color_map.keys():
        if builder.vert_char == ' ':
            fg_vert_border_left = builder.cp.apply_bg_color(color, builder.vert_border) + builder.vert_padding
            fg_vert_border_right = builder.vert_padding + builder.cp.apply_bg_color(color, builder.vert_border)
        else:
            fg_vert_border_left = builder.cp.apply_color(color, builder.vert_border) + builder.vert_padding
            fg_vert_border_right = builder.vert_padding + builder.cp.apply_color(color, builder.vert_border)

        fg_available_width = builder.get_available_width()

        fg_text = f"This is one of the prints_charming foreground colors in the color map # Name: {color}"
        fg_text2 = f"{color} foreground color in prints_charming ColorPrinter color map"
        fg_text_center_aligned = builder.cp.apply_color(color, builder.align_text(fg_text2, fg_available_width, 'center'))
        cp.print()
        cp.print(f'{fg_vert_border_left}{fg_text_center_aligned}{fg_vert_border_right}')

        #cp.print(f"This is one of the prints_charming foreground colors in the color map. ### Name: {color_name}", color=color_name)
    cp.print()



def print_background_colors(cp, builder):
    for color in cp.color_map.keys():
        if builder.vert_char == ' ':
            bg_vert_border_left = builder.cp.apply_bg_color(color, builder.vert_border) + builder.vert_padding
            bg_vert_border_right = builder.vert_padding + builder.cp.apply_bg_color(color, builder.vert_border)
        else:
            bg_vert_border_left = builder.cp.apply_color(color, builder.vert_border) + builder.vert_padding
            bg_vert_border_right = builder.vert_padding + builder.cp.apply_color(color, builder.vert_border)

        bg_available_width = builder.get_available_width()
        cp.print()

        bg_bar_strip = cp.return_bg(color, length=bg_available_width)
        bg_bar_center_aligned = builder.align_text(bg_bar_strip, bg_available_width, 'center')
        cp.print(f"{bg_vert_border_left}{bg_bar_center_aligned}{bg_vert_border_right}")


def print_styles(cp, builder):
    cp.print()
    for style_name in cp.styles.keys():
        if builder.vert_char == ' ':
            color = style_name if builder.cp.bg_color_map.get(style_name) else builder.cp.styles.get(style_name).bg_color if not builder.cp.styles.get(style_name).reverse else builder.cp.styles.get(style_name).color
            if not color:
                color = builder.cp.styles.get(style_name).color
            print_styles_vert_border_left = builder.cp.apply_bg_color(color, builder.vert_border) + builder.vert_padding
            print_styles_vert_border_right = builder.vert_padding + builder.cp.apply_bg_color(color, builder.vert_border)
        else:
            print_styles_vert_border_left = builder.cp.apply_style(style_name, builder.vert_border) + builder.vert_padding
            print_styles_vert_border_right = builder.vert_padding + builder.cp.apply_style(style_name, builder.vert_border)

        available_width = builder.get_available_width()
        cp.print()

        text = f"This is one of the prints_charming defined styles! # Name: {style_name}"
        text_center_aligned = builder.cp.apply_style(style_name, builder.align_text(text, available_width, 'center'))
        cp.print(f'{print_styles_vert_border_left}{text_center_aligned}{print_styles_vert_border_right}')




def print_colors_and_styles():
    cp = PrintsCharming(logging_styles=logging_styles)
    builder = FormattedTextBox(cp=cp, horiz_char='|', vert_width=5, vert_padding=1, vert_char='|')

    print_foreground_colors(cp, builder)
    print_background_colors(cp, builder)
    print_styles(cp, builder)




def create_color_table_data(cp: PrintsCharming):
    table_data = [["Color Name", "Foreground Text", "Background Block"]]
    for color_name in cp.color_map.keys():
        fg_example = "Foreground Colored Text"
        bg_example = cp.return_bg(color_name, length=10)
        table_data.append([color_name, fg_example, bg_example])
    return table_data



def welcome():

    # None of these parameters are required for simple use cases as will be shown soon. You can simply init PrintsCharming with pc_instance = PrintsCharming()
    # To interactively create your own color_map where you can pick and name your own colors and default color do python -m prints_charming.show_colors. The point of this is to
    # show various ways to align text and tables and objects within boxes and tables. More on it later and some of the box methods will be weeded out.
    style_conditions = StyleConditionsManager()
    cp = PrintsCharming(logging_styles=logging_styles, style_conditions=style_conditions)


    table_manager = TableManager(cp=cp)

    colors_table_data = create_color_table_data(cp)
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

    # Create an instance of FormattedTextBox
    builder = FormattedTextBox(cp=cp, horiz_char=' ', vert_width=5, vert_padding=1, vert_char=' ')

    (horiz_border_top,
     vert_border_left,
     vert_border_right,
     horiz_border_bottom) = builder.build_styled_border_box(horiz_border_top_style=style_conditions.welcome_style('top'),
                                                            vert_border_left_style=style_conditions.welcome_style('left'),
                                                            vert_border_right_style=style_conditions.welcome_style('right'),
                                                            horiz_border_bottom_style=style_conditions.welcome_style('bottom'))

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
                                     horiz_border_double=True)

    print(horiz_border_bottom)
    print()
    print(horiz_border_top)

    # Print the table within a border box
    builder.print_border_boxed_table(colors_table,
                                     horiz_border_top,
                                     vert_border_left,
                                     vert_border_right,
                                     horiz_border_bottom,
                                     text_style="default",
                                     text_align="right")

    print(horiz_border_bottom)
    print()
    print(horiz_border_top)

    # Print the table within a border box
    builder.print_border_boxed_table(colors_table,
                                     horiz_border_top,
                                     vert_border_left,
                                     vert_border_right,
                                     horiz_border_bottom,
                                     text_style="default",
                                     text_align="center")

    print(horiz_border_bottom)
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

    conditional_styles = {
        "Age": [
            {"type": "below", "value": 18, "style": "vred"},
            {"type": "below", "value": 21, "style": "green"},
            {"type": "above_or_equal", "value": 21, "style": "vgreen"}
        ],
        "Name": [
            {"type": "in_list", "value": ["Prince Charming", "John Smith"], "style": "blue"},
            {"type": "in_list", "value": ["Cinderella", "Anastasia", "Drizella", "Ariel"], "style": "pink"}
        ],
        "Occupation": [
            {"type": "in_list", "value": ['Prince', 'Princess'], "style": "orange"},
            {"type": "equals", "value": "Mermaid", "style": "vyellow"},
            {"type": "equals", "value": "Socialite", "style": "cyan"},
            {"type": "not_in_list", "value": ['Prince', 'Princess'], "style": "gray"}
        ]
    }

    builder.print_border_boxed_tables2([less_simple_table, less_simple_table, less_simple_table, less_simple_table],
                                       horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom,
                                       table_alignments=['center', 'center', 'center', 'center'])

    complex_table = table_manager.generate_table(table_data=table_data, table_name="Fairy Tale Characters:",
                                                 show_table_name=True, header_style="magenta", border_style="vgreen",
                                                 col_sep_style="vgreen", target_text_box=True, cell_style=["orange", "purple"],
                                                 conditional_styles=conditional_styles)

    print(complex_table)

    builder = FormattedTextBox(cp=cp, horiz_width=100, horiz_char=' ', vert_width=5, vert_padding=1, vert_char='|')
    horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom = builder.build_styled_border_box(horiz_border_top_style=style_conditions.welcome_style('top'),
                                                                                                                 vert_border_left_style=style_conditions.welcome_style('left'),
                                                                                                                 vert_border_right_style=style_conditions.welcome_style(
                                                                                                                     'right'),
                                                                                                                 horiz_border_bottom_style=style_conditions.welcome_style(
                                                                                                                     'bottom'))

    builder.print_border_boxed_table(less_simple_table, horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom, text_style="default", text_align="right")
    builder.print_border_boxed_table(less_simple_table, horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom, text_style="default", text_align="center")
    builder.print_border_boxed_table(less_simple_table, horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom, text_style="default", text_align="left")



def setup_logger(pc):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = PrintsCharmingLogHandler(pc)
    logger.addHandler(handler)
    return logger



def play_around_with_logging():

    pc = PrintsCharming()

    my_logger = setup_logger(pc)

    init_message = f"PrintsCharmingLogHandler initialized with configuration:\n{pc.print_dict(pc.config)}"
    my_logger.debug(init_message)

    apply_style = lambda a, b: pc.apply_logging_style(a, b)

    my_logger.debug("Debug message with argument 1: {} and argument 2: {}", apply_style('class_name', 'arg1'), apply_style('method_name', 'arg2'))

    my_logger.debug("Debugging information.")
    my_logger.info("General info.")
    my_logger.warning("Warning message.")
    my_logger.error("Error encountered.")
    my_logger.critical("Critical issue.")
    print()

    pc.config['internal_logging'] = True
    pc.update_logging()


    pc.debug(f"PrintsCharming enabled internal logging:\n{pc.print_dict(pc.config)}")



def main():
    set_custom_excepthook()

    # uncomment to play around with logging
    play_around_with_logging()

    welcome()

    cp = PrintsCharming(logging_styles=logging_styles)
    builder = FormattedTextBox(cp=cp, horiz_char='|', vert_width=5, vert_padding=1, vert_char='|')

    cp.add_variable('function', 'blue')

    print_colors_and_styles()

    simple_use_case(cp)

    text_from_variable_examples = variable_examples(cp)
    index_styling_examples(cp)
    auto_styling_examples(cp, text_from_variable_examples)
    print_variable_examples(cp)
    print_horizontal_bg_strip(cp)
    more_stuff()
    kwargs_replace_and_style_placeholders_examples()
    formatted_text_box_stuff()
    my_custom_error(cp)
    progress_bar(cp)


if __name__ == "__main__":
    quick_pc = PrintsCharming()
    mini_border = '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    styled_mini_border = quick_pc.apply_style('orange', mini_border)
    main()

