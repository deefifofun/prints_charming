# 🎉 prints_charming: The Ultimate Terminal Text Coloring and Styling Solution 🎉

![Project Illustration](./images/prints_charming_illustration.png)
I couldn't get chatGPT to spell Python correctly and include all the other important details lol had to settle for this after accepting it wasn't going to happen after 68 images.

## 🚀 Introduction

Announcing the first public release of **prints_charming**! Initially created in March of this year, this Python package has become an indispensable part of my development workflow. It has seen extensive use in 100+ of my own Python modules across various private projects I have been working on over the last eight months. "prints_charming" is more than just another color printing library; it's crafted to elevate your development experience by providing a swift and streamlined way to color and style terminal outputs—be it for standard printing, logging, debugging, or tracing—all without becoming an obstruction in your development process. While the library serves as a robust tool for making terminal outputs more readable, visually appealing, and informative, its true power lies in its versatility—enhancing the entire terminal and programming experience.

## ✅ Current State

For my current needs, this package does everything I require. It's particularly useful for developers who deal with extensive terminal outputs and need to quickly distinguish between different types of information. It's production-ready and has been rigorously tested in various internal projects.

## 🛠 Future Enhancements

Though **prints_charming** is replete with features tailored for Linux terminals, the fairy tale isn't over, and the door is always open for additional community-driven enhancements. While my current commitments across multiple projects may limit my immediate involvement in further development, your contributions could add new chapters to the prints_charming story. For those interested in broadening the library's reach, I welcome contributions that extend support to Windows Command Prompt and PowerShell, as this is currently outside the scope of my planned updates.

## 🌟 Key Features

- **No Dependencies**: Works with the standard Python libraries
- **Efficiency by Design**: With prints_charming, styling your terminal outputs is as simple as adding a keyword argument. Spend less time fiddling with string concatenation and more time writing great code.
- **Rich Text Styling**: Apply foreground and background colors, bold, italic, underlined, and more to your text.
- **Flexible and Customizable**: Use predefined styles or define your own.
- **Variable, Word, and Phrase Styling**: Automatically apply styles to specific variables, words, or phrases in your text.
- **Header Printing**: Create beautiful headers for sectioning your outputs.
- **Intelligent Defaults**: Comes with sensible defaults but allows you to tweak every aspect to your liking.
- **Built for Linux**: This module is developed and tested on Linux and is intended for use in Linux terminals.

## 🚀 Quick Start

To get started, install the package and add it to your project.

### Option 1: Using pip

```bash
pip install prints_charming
```

### Option 2: Cloning from GitHub

Alternatively, you can clone the repository directly from GitHub to access the latest features and updates that might not yet be published on PyPI:

1. Open a terminal window.

2. Navigate to the directory where you want to clone the repository.

3. Run the following command to clone the repository:

```bash
git clone https://github.com/deefifofun/prints_charming.git
```

4. Navigate into the cloned directory:

```bash
cd prints_charming
```

5. Install the package using:

```bash
pip install .
```

This will install the package from the source code.


### Here are examples of pretty much everything:

```python
from prints_charming import TextStyle, ColorPrinter

config = {
    "color_text"          : True,
    "args_to_strings"     : True,
    "style_names"         : True,
    "style_words_by_index": True,
    "kwargs"              : True,
    "conceal"             : True,
    "width"               : 80,
}

styles = {
    "default"      : TextStyle(),
    "white"        : TextStyle(color="white"),
    "gray"         : TextStyle(color="gray"),
    "green"        : TextStyle(color="green"),
    "vgreen"       : TextStyle(color="vgreen"),
    "red"          : TextStyle(color="red"),
    "vred"         : TextStyle(color="vred", bold=True, italic=True, underlined=True, overlined=True, blink=True),
    "blue"         : TextStyle(color="blue"),
    "vblue"        : TextStyle(color="vblue"),
    "yellow"       : TextStyle(color="yellow"),
    "vyellow"      : TextStyle(color="vyellow"),
    "cyan"         : TextStyle(color="cyan"),
    "vcyan"        : TextStyle(color="vcyan"),
    "magenta"      : TextStyle(color="magenta", bold=True, underlined=True),
    "pink"         : TextStyle(color="pink"),
    "purple"       : TextStyle(color="purple", bg_color="gray", reversed=True),
    "orange"       : TextStyle(color="orange"),
    "header_text"  : TextStyle(color="white", bg_color="purple", bold=True, reversed=True),
    "header_symbol": TextStyle(color="magenta", bold=True, overlined=True, strikethrough=True),
    "task"         : TextStyle(color="blue", bold=True),
    "conceal"      : TextStyle(conceal=True),
}

colorprinter_variables = {
    "vgreen": ["Hello, world!", "Connected", "Loaded", "Monitor", "ABOVE THRESHOLD", "wss://advanced-trade-ws.coinbase.com", "Starting", "True"],
    "vred": ["Failed!", "Error", "Failed", "None", "Skipping.", "Canceling", "Canceled"],
    "blue": ["CoinbaseWebsocketClient", "server"],
    "yellow": ["1", "returned",],
    "vyellow": ["File modified:", "File modified AGAIN", "subscribed"],
    "magenta": ["within 10 seconds."],
    "cyan": ["|", "#"],
    "orange": ["New Message!"],
    "purple": ["My background is purple"]
    # Uncomment the next line to hide API keys or sensitive information
    #"conceal": [os.environ[key] for key in os.environ if "API" in key],
}

# Create an instance of the ColorPrinter class with default colormap, custom config, and custom styles
cp = ColorPrinter(config=config, styles=styles)

# Print all the foreground colors in the color map with it's name to the right of it.
# You can optionally supply your own color_map as an arg in the init method.
# For styling of the first cp.print statement we will add 'Name:' to the word map.
cp.print("##############################################################################################", color="yellow")
cp.print("#### Print all the foreground colors in the color map each with it's name to the right of it.", color="yellow")
cp.print("#### You can optionally supply your own color_map as an arg in the init method.", color="yellow")
cp.print("#### For styling of the first cp.print statement we will add 'Name:' to the word map.", color="yellow")
cp.print("##############################################################################################", color="yellow")
cp.add_variable("Name:", style_name="default")
for color_name, color_code in cp.color_map.items():
    cp.print(f"### This is one of the prints_charming foreground colors in the color map. ### Name: {color_name}", color=color_name)

# Print all the styles in the styles dictionary with it's name to the right of it.
# As you can see most of the styles are named after the foreground color, but you can edit the styles and name them whatever you want!
# You can optionally supply your own styles dictionary as an arg in the init method as I have done here, but if you don't this is also the default.
cp.print("##############################################################################################", color="yellow")
cp.print("#### Print all the styles in the styles dictionary each with it's name to the right of it.", color="yellow")
cp.print("#### As you can see most of the styles in this example are named after the foreground color.", color="yellow")
cp.print("#### You can optionally supply your own styles dictionary or not and go with the default.", color="yellow")
cp.print("#### You can edit the styles and name them whatever you want!", color="yellow")
cp.print("##############################################################################################", color="yellow")
for style_name, style in cp.styles.items():
    cp.print(f"### This is one of the prints_charming above defined styles! ### Name: {style_name}", style=style_name)

# Print all the computed background colors from the color map dictionary.
cp.print("############################################################################", color="yellow")
cp.print("#### Print all the computed background colors from the color map dictionary.", color="yellow")
cp.print("############################################################################", color="yellow")
for color in cp.color_map:
    cp.print_bg(color, length=80)

# Basic printing with ColorPrinter will print in the default style with default color.
cp.print("# Basic printing with ColorPrinter will print in the default style with default color.")
cp.print("Hello, world!")

# Print in the default style reversed foreground and background.
cp.print("#  Print in the default style reversed foreground and background.")
cp.print("Hello, world!", reversed=True)

# Specify only the color of the args.
cp.print("# Specify only the color of the args.")
cp.print("Hello, world!", color="red")

# Specify only italic and underlined will print in the default color.
cp.print("# Specify only italic and underlined will print in the default color.")
cp.print("Hello, world!", italic=True, underlined=True)

# Specify a predefined style 'magenta'. The 'magenta' style is defined above.
cp.print("# Specify a predefined style 'magenta'. The 'magenta' style is defined above.")
cp.print("Hello, world!", style="magenta")

# Specify predefined style 'task' for printing. The 'task' style is defined above.
cp.print("# Specify predefined style 'task' for printing. The 'task' style is defined above.")
cp.print("This is a task.", style="task")

# Specify predefined style 'task' for printing. But change color to green and underlined to True.
cp.print("# Specify predefined style 'task' for printing. But change color to green and underlined to True.")
cp.print("This is a task.", style ="task", color="green", underlined=True)

# Show that 'Hello, world!' isn't color or style defined.
cp.print("# Show that 'Hello, world!' isn't color or style defined.")
cp.print("Hello, world!")

# Use the add_variable method to add 'Hello, world!' to the phrases dictionary with 'vgreen' style.
cp.print("# Use the add_variable method to add 'Hello, world!' to the phrases dictionary with 'vgreen' style.")
cp.add_variable("Hello, world!", style_name="vgreen")

# Show that 'Hello, world!' is style defined in the phrases dictionary.
cp.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
cp.print("Hello, world!")

# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.
cp.print("# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.")
cp.remove_variable("Hello, world!")

# Show that 'Hello, world!' has been removed from the styled phrases dictionary.
cp.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
cp.print("Hello, world!")

# Define a variable.
cp.print("# Define a variable.")
text = "Hello, world!"

# Use the add_variable method to add {text} to the phrases dictionary with 'yellow' style.
cp.print("# Use the add_variable method to add {text} to the phrases dictionary with 'yellow' style.")
cp.add_variable(text, style_name="yellow")

# Show that 'Hello, world!' is style defined in the phrases dictionary.
cp.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
cp.print(text)

# Show that 'Hello, world!' retains it's style while other words are unstyled.
cp.print("# Show that 'Hello, world!' retains it's style while other words are unstyled.")
cp.print(f"This sentence says, {text}")

# Show how you can style other words alongside, 'Hello, world!'.
cp.print("# Show how you can style other words alongside, 'Hello, world!'.")
cp.print(f"This sentence says, {text}", style='task')

# Show how the order of the words doesn't matter.
cp.print("# Show how the order of the words doesn't matter.")
cp.print(f"{text} Let me say that again, {text} {text} I said it again!", style="orange")

# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.
cp.print("# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.")
cp.remove_variable("Hello, world!")

# Show that 'Hello, world!' has been removed from the styled phrases dictionary.
cp.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
cp.print("Hello, world!")

# Show how to style words by index.
cp.print("# Show how to style words by index.")
cp.print(f"These words are going to be styled by their indexes",
         style={0:"vgreen", (1,4):"blue", (4,6):"yellow", 6:"purple", (7,10):"pink"})

# Printing styled variables in the middle of a string with text substitution without having to add the variable to the cp instance.
cp.print("# Printing styled variables in the middle of a string with text substitution without having to add the variable to the cp instance.")
# 'var' in text is subbed with the value of balance.
cp.print("# 'var' in text is subbed with the value of balance.")
balance = 1.25
cp.print(text=f"Value: var USD", var=balance, tstyle='orange', vstyle='vgreen')

# Now let's add some predefined words and phrases to our word and phrase map for automatic styling.
cp.print("# Now let's add some predefined words and phrases to our word and phrase map for automatic styling.")
cp.add_variables_from_dict(colorprinter_variables)

# Show printing text that will be automatically styled from the word and phrase maps created from the colorprinter_variables above.
cp.print("# Show printing text that will be automatically styled from the word and phrase maps created from the colorprinter_variables above.")
cp.print(f"Let's first print, Hello, world! styled as described above.")

# Show printing text same as above but adding additional style to the rest of the text.
cp.print("# Show printing text same as above but adding additional style to the rest of the text.")
cp.print(f"Let's first print, Hello, world! styled as described above and right here.", style="yellow")

# Show printing text same as above but include text from multiple phrases/words in the maps.
cp.print("# Show printing text same as above but include text from multiple phrases/words in the maps.")
cp.print(f"{text} Remember we assigned, 'Hello, world!' to the 'text' variable above. Let's pretend we are Connected to wss://advanced-trade-ws.coinbase.com", color="blue")

# Let's mix and match. Here we will combine the above with styling by index.
cp.print("# Let's mix and match. Here we will combine the above with styling by index.")
cp.print(f"These words are going to be styled by their indexes, {text}",
         style={0:"vgreen", (1,4):"blue", (4,6):"yellow", 6:"purple", (7,10):"pink"})

# What do you think will happen here?
cp.print("# What do you think will happen here?")
# When coloring by index, coloring by index takes precedence.
cp.print("# When coloring by index, coloring by index takes precedence.")
cp.print(f"{text} These words are going to be styled by their indexes, {text}",
         style={0:"vgreen", (1,4):"blue", (4,6):"yellow", 6:"purple", (7,10):"pink"})

# So to combine the two correctly we would have to do this.
cp.print("# So to combine the two correctly we would have to do this.")
cp.print(f"{text} Only these words are going to be styled by their indexes, {text}",
         style={(2,4):"orange", (4,7):"blue", (7,9):"yellow", 9:"purple", (10,13):"pink"})

# Print different styled automatically styled text.
cp.print(f"Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My background is purple these words are default. server")

# Same but specify a style for other words/phrases
cp.print(f"Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My background is purple these words are magenta. server", style='magenta')

# Using Dictionary with print_variables method
vars_and_styles_dict = {
    "balance" : (1000, "green"),
    "username": ("John", "blue")
}
cp.print_variables(vars_and_styles_dict, "Hello {username}, your balance is {balance} USD.", text_style="yellow")


# Using Lists with print_variables method
vars_and_styles_list = ([1000, "John"], ["green", "blue"])
cp.print_variables(vars_and_styles_list, "Hello var2, your balance is var1 USD.", text_style="yellow")

# Print word map
cp.pretty_print_cp_map(cp.word_map, style_name="default")

# Print phrase map
cp.pretty_print_cp_map(cp.phrase_map, style_name="default")

# Print conceal map
cp.pretty_print_cp_map(cp.conceal_map, style_name="default")
```

### Here's a logging example:

```python

import logging
from prints_charming import ColorPrinter
from datetime import datetime
import time

class ColorPrinterLogHandler(logging.Handler):
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self):
        super().__init__()
        self.cp = ColorPrinter()

    def emit(self, record):
        log_entry = self.format(record)
        self.handle_log_event(log_entry, log_level=record.levelname)

    def handle_log_event(self, text, log_level):
        timestamp = time.time()
        formatted_timestamp = datetime.fromtimestamp(timestamp).strftime(self.TIMESTAMP_FORMAT)

        color = 'blue'  # default color
        if 'ERROR' in log_level.upper():
            color = 'red'
        elif 'WARNING' in log_level.upper():
            color = 'yellow'
        elif 'INFO' in log_level.upper():
            color = 'green'

        timestamped_message = f"LOG[{log_level}]: {formatted_timestamp} {text}"
        self.cp.print(timestamped_message, color=color)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add custom handler to the logger
handler = ColorPrinterLogHandler()
logger.addHandler(handler)

# Test logging
logger.info('This is an info message.')
logger.warning('This is a warning message.')
logger.error('This is an error message.')
```

### Here's another logging example for more fine-grained control of individual components:

```python

import logging
from prints_charming import ColorPrinter
from datetime import datetime
import time

class ColorPrinterLogHandler(logging.Handler):
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self):
        super().__init__()
        self.cp = ColorPrinter()

    def emit(self, record):
        log_entry = self.format(record)
        self.handle_log_event(log_entry, log_level=record.levelname)

    def handle_log_event(self, text, log_level):
        timestamp = time.time()
        formatted_timestamp = datetime.fromtimestamp(timestamp).strftime(self.TIMESTAMP_FORMAT)

        # Define styles for different components
        timestamp_style = 'gray'  # Change as needed
        level_styles = {
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'DEBUG': 'blue',
            'CRITICAL': 'vred'
        }

        log_level_style = level_styles.get(log_level, 'default')

        # Get styled components
        styled_timestamp = self.cp.apply_style(timestamp_style, f"LOG[{log_level}]")
        styled_level = self.cp.apply_style(log_level_style, log_level)
        styled_text = self.cp.apply_style(log_level_style, text)

        # Create the final styled message
        timestamped_message = f"{styled_timestamp}: {formatted_timestamp} {styled_level} - {styled_text}"
        
        
        print(timestamped_message)


# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create an instance of your custom logging handler
handler = ColorPrinterLogHandler()

# Add the custom handler to the logger
logger.addHandler(handler)

# Test out different log levels
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
```

## 📧 Contact
For bugs, feature requests, and suggestions, please open an issue on GitHub.



