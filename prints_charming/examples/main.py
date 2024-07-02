#!/usr/bin/env python3

from prints_charming import TextStyle, ColorPrinter, ColorPrinterError, ColorNotFoundError
import traceback
import sys


config = {
    "color_text": True,
    "args_to_strings": True,
    "style_names": True,
    "style_words_by_index": True,
    "kwargs": True,
    "conceal": True,
}

styles = {
    "default": TextStyle(),
    "white": TextStyle(color="white"),
    "gray": TextStyle(color="gray"),
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


class CustomError(ColorPrinterError):
    """Custom error for specific use cases."""

    def __init__(self, message: str, cp: 'ColorPrinter', additional_info: str):
        super().__init__(message, cp, cp.apply_style)
        self.additional_info = additional_info

    def handle_exception(self):
        super().handle_exception()
        print(self.cp.apply_style('cyan', self.additional_info), file=sys.stderr)




class StylishHeader:
    def __init__(self, horiz_width=60, horiz_char="#", vert_width=None, vert_char='|'):
        self.horiz_width = horiz_width
        self.horiz_char = horiz_char
        self.horiz_border = horiz_width * horiz_char
        self.vert_width = vert_width
        self.vert_char = horiz_char if vert_width and not vert_char else vert_char
        self.vert_border = '' if not vert_width else vert_width * self.vert_char


    @staticmethod
    def _align_text(text, available_width, alignment='center'):
        if alignment == 'left':
            return text.ljust(available_width)
        elif alignment == 'right':
            return text.rjust(available_width)
        elif alignment == 'center':
            return text.center(available_width)
        else:
            raise ValueError("Invalid alignment. Choose from 'left', 'right', or 'center'.")

    def _get_available_width(self):
        return self.horiz_width - (2 * self.vert_width) - 1 if self.vert_border else self.horiz_width


    def print_header(self, title, subtitle='', alignment='center'):
        available_width = self._get_available_width()

        title_aligned_text = cp.apply_style('vgreen', self._align_text(title, available_width, alignment))

        if subtitle:
            subtitle_aligned_text = cp.apply_style('white', self._align_text(subtitle, available_width, alignment))
        else:
            subtitle_aligned_text = ''

        horiz_border_top = cp.apply_style('purple', self.horiz_border)
        horiz_border_bottom = cp.apply_style('orange', self.horiz_border)

        title_vert_border_left = cp.apply_style('orange', self.vert_border)
        title_vert_border_right = cp.apply_style('purple', self.vert_border)

        subtitle_vert_border_left = cp.apply_style('orange', self.vert_border)
        subtitle_vert_border_right = cp.apply_style('purple', self.vert_border)

        # Add space after left border and before right border for left and right alignments
        if alignment == 'left':
            formatted_title_line = f"{title_vert_border_left} {title_aligned_text}{title_vert_border_right}"
            if subtitle:
                formatted_subtitle_line = f"{subtitle_vert_border_left} {subtitle_aligned_text}{subtitle_vert_border_right}"
        elif alignment == 'right':
            formatted_title_line = f"{title_vert_border_left}{title_aligned_text} {title_vert_border_right}"
            if subtitle:
                formatted_subtitle_line = f"{subtitle_vert_border_left}{subtitle_aligned_text} {subtitle_vert_border_right}"
        else:  # center alignment
            formatted_title_line = f"{title_vert_border_left}{title_aligned_text} {title_vert_border_right}"
            if subtitle:
                formatted_subtitle_line = f"{subtitle_vert_border_left}{subtitle_aligned_text} {subtitle_vert_border_right}"

        print(horiz_border_top)
        print(formatted_title_line)
        if subtitle:
            print(formatted_subtitle_line)
        print(horiz_border_bottom)
        print()

    def _split_text_to_lines(self, text, available_width):
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

    def print_header_2(self, title, subtitle='', alignment='center'):
        available_width = self._get_available_width()
        title_lines = self._split_text_to_lines(title, available_width)
        subtitle_lines = self._split_text_to_lines(subtitle, available_width) if subtitle else []

        horiz_border_top = self.horiz_border
        horiz_border_bottom = self.horiz_border

        print(horiz_border_top)
        for line in title_lines:
            aligned_text = self._align_text(line, available_width, alignment)
            if self.vert_border:
                print(f"{self.vert_border} {aligned_text} {self.vert_border}")
            else:
                print(aligned_text)

        for line in subtitle_lines:
            aligned_text = self._align_text(line, available_width, alignment)
            if self.vert_border:
                print(f"{self.vert_border} {aligned_text} {self.vert_border}")
            else:
                print(aligned_text)

        print(horiz_border_bottom)


def print_foreground_colors():
    text = """
        Print all the foreground colors in the color map each with its name to the right of it. 
        You can optionally supply your own color_map as an argument in the init method. 
        For the first cp.print statement, we will add 'Name:' to the word map.
        """

    header.print_header_2(text, alignment='left')
    print()
    separator = "#" * 96
    cp.print(separator, color="yellow")
    cp.print("#### Print all the foreground colors in the color map each with its name to the right of it.", color="yellow")
    cp.print("#### You can optionally supply your own color_map as an argument in the init method.", color="yellow")
    cp.print("#### For the first cp.print statement, we will add 'Name:' to the word map.", color="yellow")
    cp.print(separator, color="yellow")
    print()
    cp.add_variable("Name:", style_name="default")
    for color_name in cp.color_map.keys():
        cp.print(f"### This is one of the prints_charming foreground colors in the color map. ### Name: {color_name}", color=color_name)
    print()

def print_background_colors():
    print()
    cp.print("#" * 76, color="yellow")
    cp.print("#### Print all the computed background colors from the color map dictionary.", color="yellow")
    cp.print("#" * 76, color="yellow")
    print()
    for color in cp.color_map.keys():
        cp.print_bg(color, length=80)
    print()


def print_styles():
    print()
    separator = "#" * 96
    cp.print(separator, color="yellow")
    cp.print("#### Print all the styles in the styles dictionary each with its name to the right of it.", color="yellow")
    cp.print("#### As you can see, most of the styles in this example are named after the foreground color.", color="yellow")
    cp.print("#### You can optionally supply your own styles dictionary or go with the default.", color="yellow")
    cp.print("#### You can edit the styles and name them whatever you want!", color="yellow")
    cp.print(separator, color="yellow")
    print()
    for style_name in cp.styles.keys():
        cp.print(f"### This is one of the prints_charming defined styles! ### Name: {style_name}", style=style_name)
    print()



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


    header = StylishHeader(
        horiz_width=100,
        horiz_char="|",
        vert_width=5
    )
    header.print_header("Prints Charming", subtitle="Hope you find the user guide helpful!", alignment='center')
    header.print_header("Prints Charming", subtitle="Monitor your Kingdom in Style", alignment='left')
    header.print_header("Prints Charming", subtitle="Monitor your Kingdom in Style", alignment='right')
    print()



    print_foreground_colors()
    print_background_colors()
    print_styles()
    print_examples()
    text_from_variable_examples = variable_examples()
    kwargs_styling_examples()
    index_styling_examples()
    auto_styling_examples(text_from_variable_examples)
    print_variable_examples()
    print_table()

    #print_horizontal_bg_strip()

    my_custom_error()