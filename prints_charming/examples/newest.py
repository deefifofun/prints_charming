#!/usr/bin/env python3

from prints_charming import TextStyle, ColorPrinter, FormattedTextBox, ColorPrinterError, ColorNotFoundError
import traceback
import sys
import time


# To run this script as a module inside the package. Navigate to the top-level directory and run
# python -m prints_charming.examples.newest


config = {
    "color_text": True,
    "args_to_strings": True,
    "style_names": True,
    "style_words_by_index": True,
    "kwargs": True,
    "conceal": True,
    "width": 80,
}

styles = {
    "default": TextStyle(),
    "white": TextStyle(color="white"),
    "gray": TextStyle(color="gray"),
    "black": TextStyle(color="black"),
    "green": TextStyle(color="green"),
    "vgreen": TextStyle(color="vgreen"),
    "red": TextStyle(color="red"),
    "vred": TextStyle(color="vred"),
    "blue": TextStyle(color="blue"),
    "vblue": TextStyle(color="vblue"),
    "yellow": TextStyle(color="yellow"),
    "vyellow": TextStyle(color="vyellow"),
    "cyan": TextStyle(color="cyan"),
    "vcyan": TextStyle(color="vcyan"),
    "magenta": TextStyle(color="magenta", bold=True, underlined=True),
    "pink": TextStyle(color="pink"),
    "purple": TextStyle(color="purple"),
    "orange": TextStyle(color="orange"),
    "header_text": TextStyle(color="white", bg_color="purple", bold=True, reversed=True),
    "header_symbol": TextStyle(color="magenta", bold=True, overlined=True, strikethrough=True),
    "task": TextStyle(color="blue", bold=True),
    "header"       : TextStyle(color="vcyan"),
    "path"         : TextStyle(color="blue"),
    "filename"     : TextStyle(color="yellow"),
    "line_info"    : TextStyle(color="yellow", bold=True),
    "line_number"  : TextStyle(color="yellow", bold=True),
    "function_name": TextStyle(color="yellow", italic=True),
    "error_message": TextStyle(color="vred", bg_color="vyellow"),
    "code"         : TextStyle(color="yellow"),
    "conceal": TextStyle(conceal=True),
}

colorprinter_variables = {
    "vgreen": ["Hello, world!", "string", "Connected", "Loaded", "Monitor", "ABOVE THRESHOLD", "wss://advanced-trade-ws.coinbase.com", "Starting", "True"],
    "vred": ["Failed!", "Error", "Failed", "None", "Skipping.", "Canceling", "Canceled"],
    "blue": ["CoinbaseWebsocketClient", "server"],
    "yellow": ["1", "returned", "please"],
    "vyellow": ["File modified:", "File modified AGAIN", "subscribed", "="],
    "magenta": ["within 10 seconds.", "how"],
    "cyan": ["|", "#", "are", "your"],
    "orange": ["New Message!", "Prints"],
    "purple": ["My background is purple"],
    # Uncomment the next line to hide API keys or sensitive information
    # "conceal": [os.environ[key] for key in os.environ if "API" in key],
}



class Escape:
    COLOR_MAP = {
        "default": "\033[0m",
        "white": "\033[97m",
        "black": "\033[30m",
        "green": "\033[32m",
        "vgreen": "\033[38;5;46m",
        "red": "\033[31m",
        "vred": "\033[38;5;196m",
        "blue": "\033[34m",
        "vblue": "\033[38;5;21m",
        "yellow": "\033[33m",
        "vyellow": "\033[38;5;226m",
        "magenta": "\033[35m",
        "vmagenta": "\033[38;5;201m",
        "cyan": "\033[36m",
        "vcyan": "\033[38;5;51m",
        "orange": "\033[38;5;208m",
        "gray": "\033[38;5;252m",
        "pink": "\033[38;5;200m",
        "purple": "\033[38;5;129m"
    }

    # ANSI escape sequences
    ESCAPE_SEQUENCES = {
        "clear_line": "\033[2K",
    }

    def clear_line(self, use_carriage_return: bool = True):
        if use_carriage_return:
            print("\r" + self.ESCAPE_SEQUENCES["clear_line"], end='')
        else:
            print(self.ESCAPE_SEQUENCES["clear_line"], end='')

    def print(self, *args, color=None, end='\n'):
        if color:
            color_code = self.COLOR_MAP.get(color, self.COLOR_MAP['default'])
            reset_code = self.COLOR_MAP['default']
            print(color_code + ' '.join(map(str, args)) + reset_code, end=end)
        else:
            print(*args, end=end)

    def print_progress_bar(self, total_steps: int, bar_length: int = 40, color: str = 'vgreen'):
        for i in range(total_steps):
            progress = (i + 1) / total_steps
            block = int(bar_length * progress)
            bar = "#" * block + "-" * (bar_length - block)
            time.sleep(1)
            self.clear_line()
            self.print(f"Progress: |{bar}| {int(progress * 100)}%", end='', color=color)
            sys.stdout.flush()
            time.sleep(0.5)  # Simulate work




class CustomError(ColorPrinterError):
    """Custom error for specific use cases."""

    def __init__(self, message: str, cp: 'ColorPrinter', additional_info: str):
        super().__init__(message, cp, cp.apply_style)
        self.additional_info = additional_info

    def handle_exception(self):
        super().handle_exception()
        print(self.cp.apply_style('cyan', self.additional_info), file=sys.stderr)


def print_foreground_colors():
    #cp.add_variable("Name:", style_name="default")
    for color_name in cp.color_map.keys():
        fg_vert_border_left = builder.cp.apply_color(color_name, builder.vert_border) + builder.vert_padding
        fg_vert_border_right = builder.vert_padding + builder.cp.apply_color(color_name, builder.vert_border)

        fg_available_width = builder.get_available_width()
        print()

        fg_text = f"This is one of the prints_charming foreground colors in the color map # Name: {color_name}"
        fg_text_left_aligned = builder.cp.apply_color(color_name, builder.align_text(fg_text, fg_available_width, 'center'))
        print(f'{fg_vert_border_left}{fg_text_left_aligned}{fg_vert_border_right}')


        #cp.print(f"This is one of the prints_charming foreground colors in the color map. ### Name: {color_name}", color=color_name)
    print()

def print_background_colors():
    for color in cp.color_map.keys():
        bg_vert_border_left = builder.cp.apply_color(color, builder.vert_border) + builder.vert_padding
        bg_vert_border_right = builder.vert_padding + builder.cp.apply_color(color, builder.vert_border)

        bg_available_width = builder.get_available_width()
        print()

        bg_bar_strip = cp.return_bg(color, length=bg_available_width)
        bg_bar_center_aligned = builder.align_text(bg_bar_strip, bg_available_width, 'left')
        print(f"{bg_vert_border_left}{bg_bar_center_aligned}{bg_vert_border_right}")
    print()


def print_styles():
    print()
    for style_name in cp.styles.keys():
        print_styles_vert_border_left = builder.cp.apply_style(style_name, builder.vert_border) + builder.vert_padding
        print_styles_vert_border_right = builder.vert_padding + builder.cp.apply_style(style_name, builder.vert_border)

        available_width = builder.get_available_width()
        print()

        text = f"This is one of the prints_charming defined styles! # Name: {style_name}"
        text_center_aligned = builder.cp.apply_style(style_name, builder.align_text(text, available_width, 'center'))
        print(f'{print_styles_vert_border_left}{text_center_aligned}{print_styles_vert_border_right}')



def print_examples():
    print()
    cp.print("# Basic printing with ColorPrinter will print in the default style with default color.")
    cp.print("Hello, world!")
    cp.print("# Print in the default style reversed foreground and background.")
    cp.print("Hello, world!", reversed=True)
    cp.print("# Specify only the color of the args.")
    cp.print("Hello, world!", color="red")
    cp.print("# Specify only italic and underlined will print in the default color.")
    cp.print("Hello, world!", italic=True, underlined=True)
    cp.print("# Specify a predefined style 'magenta'. The 'magenta' style is defined above.")
    cp.print("Hello, world!", style="magenta")
    cp.print("# Specify predefined style 'task' for printing. The 'task' style is defined above.")
    cp.print("This is a task.", style="task")
    cp.print("# Specify predefined style 'task' for printing but change color to green and underlined to True.")
    cp.print("This is a task.", style="task", color="green", underlined=True)
    cp.print("# Show that 'Hello, world!' isn't color or style defined.")
    cp.print("Hello, world!")
    print()

def variable_examples():
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

def kwargs_styling_examples():
    print()
    text = "Hello, {name}. You are {age} years old."
    kwargs = {"name": "Alice", "age": 30}

    styled_text = cp.apply_kwargs_placeholders(text, kwargs)
    print(styled_text)

def index_styling_examples():
    print()
    cp.print("# Show how to style words by index.")
    styled_by_index = {
        1: "vgreen",
        (2, 4): "blue",
        (5, 6): "yellow",
        7: "purple",
        (8, 10): "pink"
    }
    cp.print("These words are going to be styled by their indexes.", style=styled_by_index)
    cp.print("# Printing styled variables in the middle of a string with text substitution without having to add the variable to the cp instance.")
    balance = 1.25
    cp.print(text=f"Value: var USD", var=balance, tstyle='orange', vstyle='vgreen')
    print()

def auto_styling_examples(text):
    print()
    cp.print("# Now let's add some predefined words and phrases to our word and phrase map for automatic styling.")
    cp.add_variables_from_dict(colorprinter_variables)
    cp.print("# Show printing text that will be automatically styled from the word and phrase maps created from the colorprinter_variables above.")
    cp.print("Let's first print, Hello, world! styled as described above.")
    cp.print("# Show printing text same as above but adding additional style to the rest of the text.")
    cp.print("Let's first print, Hello, world! styled as described above and right here.", style="yellow")
    cp.print("# Show printing text same as above but include text from multiple phrases/words in the maps.")
    cp.print(f"{text} Remember we assigned, 'Hello, world!' to the 'text' variable above. Let's pretend we are Connected to wss://advanced-trade-ws.coinbase.com", color="blue")
    cp.print("# Let's mix and match. Here we will combine the above with styling by index.")
    cp.print("These words are going to be styled by their indexes, Hello, world!",
             style={0: "vgreen", (1, 4): "blue", (4, 6): "yellow", 6: "purple", (7, 10): "pink"})
    cp.print("# What do you think will happen here?")
    cp.print("Hello, world! These words are going to be styled by their indexes, Hello, world!",
             style={0: "vgreen", (1, 4): "blue", (4, 6): "yellow", 6: "purple", (7, 10): "pink"})
    cp.print("# So to combine the two correctly we would have to do this.")
    cp.print("Hello, world! Only these words are going to be styled by their indexes, Hello, world!",
             style={(2, 4): "orange", (4, 7): "blue", (7, 9): "yellow", 9: "purple", (10, 13): "pink"})
    cp.print("# Print different styled automatically styled text.")
    cp.print("Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My background is purple these words are default. server")
    cp.print("# Same but specify a style for other words/phrases")
    cp.print("Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My background is purple these words are magenta. server", style='magenta')
    print()

    cp.print("Hello", "how are you?", sep="---", color='green')
    cp.print()
    cp.print("This string is not connected to another", color='blue')
    cp.print()
    cp.print("This string is connected to another", "string", color='vyellow')
    print()


def print_variable_examples():
    print()
    cp.print("# Using Dictionary with print_variables method")
    vars_and_styles_dict = {
        "balance": (1000, "green"),
        "username": ("Prince", "blue")
    }
    cp.print_variables(vars_and_styles_dict, "Hello {username}, your balance is {balance} USD.", text_style="yellow")
    cp.print("# Using Lists with print_variables method")
    vars_and_styles_list = ([1000, "Princess"], ["green", "blue"])
    cp.print_variables(vars_and_styles_list, "Hello var2, your balance is var1 USD.", text_style="yellow")
    print()


def print_maps():
    print()
    cp.print("# Print word map")
    cp.ugly_print_map(cp.word_map, style_name="default")
    cp.print("# Print phrase map")
    cp.ugly_print_map(cp.phrase_map, style_name="default")
    cp.print("# Print conceal map")
    cp.ugly_print_map(cp.conceal_map, style_name="default")
    print()

def print_table():
    print()
    cp.print("# Print a sample table")
    table_data = [
        ["Name", "Age", "Occupation"],
        ["Prince Charming", 27, "Prince"],
        ["Cinderella", 21, "Princess"],
        ["Anastasia", 24, "Socialite"],
        ["Drizella", 22, "Socialite"]
    ]
    cp.print_table(table_data, header_style="magenta", border_style="green")
    print()


def my_custom_error():
    try:
        message = f'A custom error occurred'
        styled_message = cp.apply_style('purple', message)
        raise CustomError(styled_message, cp, "Additional context-specific information")
    except CustomError as e:
        e.handle_exception()


def print_horizontal_bg_strip():
    print()
    cp.print_bg('tree_color')  # Will raise ColorNotFoundError
    """
    try:
        cp.print_bg('tree_color')
    except ColorNotFoundError as e:
        print(e)
    """
    """
    try:
        #cp.print_bg('vcyan')
        cp.print_bg('tree_color')
    except ColorNotFoundError as e:
        e.handle_exception()
        #traceback.print_exc()
    """

    print()


if __name__ == "__main__":
    # Create an instance of the ColorPrinter class with custom configuration and styles
    cp = ColorPrinter(config=config, styles=styles)

    builder = FormattedTextBox(cp=cp, horiz_width=100, horiz_char='|', vert_width=5, vert_padding=1, vert_char='|')

    builder2 = FormattedTextBox(cp=cp, horiz_width=100, horiz_char='|', vert_width=None, vert_padding=1)

    builder3 = FormattedTextBox(cp=cp, horiz_width=90, horiz_char='|', vert_width=5, vert_padding=1, vert_char='|')

    builder.print_simple_border_boxed_text("Prints Charming", subtitle="Hope you find the user guide helpful!", align='center')
    print()

    builder.print_border_boxed_text('Prints Charming',
                                    text_style='vgreen',
                                    text_align='left',
                                    subtext='Hope you find the user guide helpful!',
                                    subtext_style='white',
                                    subtext_align='center',
                                    horiz_border_top_style='purple',
                                    horiz_border_bottom_style='orange',
                                    text_vert_border_l_style='orange',
                                    text_vert_border_r_style='purple',
                                    subtext_vert_border_l_style='orange',
                                    subtext_vert_border_r_style='purple')

    print()
    texts = []
    blank_line1 = 'invisible_text'
    title_border_top = '#' * builder.get_available_width()
    blank_line2 = 'invisible_text'
    title = 'Prints Charming'
    subtitle = 'Hope you find the user guide helpful'
    subtitle2 = '#' * builder.get_available_width()
    subtitle3 = 'invisible_text'
    subtitle4 = 'invisible_text'
    texts.extend([blank_line1, title_border_top, blank_line2, title, subtitle, subtitle2, subtitle3, subtitle4])

    text_styles = ['default', 'vblue', 'default', 'vgreen', 'white', 'vblue', 'default', 'default']
    alignments = ['center', 'center', 'center', 'center', 'center', 'center', 'center', 'center']


    builder.print_border_boxed_text2(texts, text_styles=text_styles, alignments=alignments,
                                     horiz_border_top_style='purple', horiz_border_bottom_style='orange',
                                     vert_border_l_style='orange', vert_border_r_style='purple')

    fg_text = """
        Print all the foreground colors in the color map dictionary.
        """
    print()
    builder.print_border_boxed_text(fg_text, text_align='center', horiz_border_bottom=False, horiz_border_top=False, text_style='vcyan', text_vert_border_l_style='cyan', text_vert_border_r_style='cyan')
    print()
    print_foreground_colors()

    horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom = builder.build_border_box(horiz_border_top_style='purple',
                                                                                                          horiz_border_bottom_style='orange',
                                                                                                          vert_border_left_style='orange',
                                                                                                          vert_border_right_style='purple')

    print(horiz_border_bottom)

    bg_text = """
        Print all the computed background colors from the color map dictionary.
    """
    print()
    builder.print_border_boxed_text(bg_text, text_align='center', horiz_border_bottom=False, horiz_border_top=False, text_style='vcyan', text_vert_border_l_style='cyan', text_vert_border_r_style='cyan')
    print_background_colors()
    print(horiz_border_bottom)


    print_styles_text = """
        Print all the styles in the styles dictionary each with its name to the right of it.
        As you can see, most of the styles in this example are named after the foreground color.
        You can optionally supply your own styles dictionary or go with the default.
        You can edit the styles and name them whatever you want!
    """
    print()
    builder.print_border_boxed_text(print_styles_text, text_align='left', horiz_border_bottom=False, horiz_border_top=False, text_style='vcyan', text_vert_border_l_style='cyan', text_vert_border_r_style='cyan')
    print_styles()
    print(horiz_border_bottom)


    print_examples()
    text_from_variable_examples = variable_examples()
    kwargs_styling_examples()
    index_styling_examples()
    auto_styling_examples(text_from_variable_examples)
    print_variable_examples()
    print_table()


    printer = Escape()

    print()
    print()

    print("Starting process...")
    printer.print_progress_bar(5)
    print("\nProcess complete.")

    print()
    print()

    print("""
        More border box examples of different ways to use them. It is less complicated than this. 
        I was under time constraints, but wanted to get examples of the new updates out there anyway!""")


    print()
    print()

    builder2.print_border_boxed_text('Prints Charming',
                                     text_style='vgreen',
                                     text_align='center',
                                     subtext='Hope you find the user guide helpful!',
                                     subtext_style='white',
                                     subtext_align='center',
                                     horiz_border_top_style='purple',
                                     horiz_border_bottom_style='orange',
                                     text_vert_border_l_style='orange',
                                     text_vert_border_r_style='purple',
                                     subtext_vert_border_l_style='orange',
                                     subtext_vert_border_r_style='purple')


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
    two_col_strings_hug_borders = builder.align_strings(['left aligned double col', 'right aligned double col'], available_width, styles=['purple', 'orange'], alignments=['left', 'right'])
    two_col_strings_hug_left = builder.align_strings(['left aligned double col', 'left aligned double col'], available_width, styles=['purple', 'orange'], alignments=['left', 'left'])
    two_col_strings_hug_right = builder.align_strings(['right aligned double col', 'right aligned double col'], available_width, styles=['purple', 'orange'], alignments=['right', 'right'])

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


    text = """
            Display all the splizzorp colors in the wibble blorple each with its flibber to the left of it.
            You can optionally supply your own wibble_blorple as a nerble in the sproing method.
            For the first fribble statement, we will add 'Flibble:' to the word wibble.
            """

    builder.print_border_boxed_text(text, text_align='left')
    print()

    cp.print('These will purposely cause an error that is styled', color='vgreen')
    print()
    print()
    print_horizontal_bg_strip()

    my_custom_error()
    print()
    print()