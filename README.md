# 🎉 prints_charming v1.0.0: The Ultimate Terminal Text Coloring and Styling Solution 🎉

## 🚀 Introduction

Announcing the first public release of **prints_charming**! Initially created in March of this year, this Python package has become an indispensable part of my development workflow. It has seen extensive use in 100+ of my own Python modules across various private projects I have been working on over the last eight months. "prints_charming" is more than just another color printing library; it's crafted to elevate your development experience by providing a swift and streamlined way to color and style terminal outputs—be it for standard printing, logging, debugging, or tracing—all without becoming an obstruction in your development process. While the library serves as a robust tool for making terminal outputs more readable, visually appealing, and informative, its true power lies in its versatility—enhancing the entire terminal and programming experience.

## ✅ Current State

For my current needs, this package does everything I require. It's particularly useful for developers who deal with extensive terminal outputs and need to quickly distinguish between different types of information. It's production-ready and has been rigorously tested in various internal projects.

## 🛠 Future Enhancements

Though **prints_charming** is replete with features tailored for Linux terminals, the door is always open for additional community-driven enhancements. While my current commitments across multiple projects may limit my immediate involvement in further development, your contributions can play a pivotal role in expanding this package's capabilities. For those interested in broadening the library's reach, I welcome contributions that extend support to Windows Command Prompt and PowerShell, as this is currently outside the scope of my planned updates.

## 🌟 Key Features

- **Efficiency by Design**: With prints_charming, styling your terminal outputs is as simple as adding a keyword argument. Spend less time fiddling with string concatenation and more time writing great code.
- **Rich Text Styling**: Apply foreground and background colors, bold, italic, underlined, and more to your text.
- **Flexible and Customizable**: Use predefined styles or define your own.
- **Variable, Word, and Phrase Styling**: Automatically apply styles to specific variables, words, or phrases in your text.
- **Header Printing**: Create beautiful headers for sectioning your outputs.
- **Intelligent Defaults**: Comes with sensible defaults but allows you to tweak every aspect to your liking.
- **Built for Linux**: This module is developed and tested on Linux and is intended for use in Linux terminals.

## 🚀 Quick Start

To get started, install the package and add it to your project.

### Here's a simple example:

```python
# Import the ColorPrinter class from the prints_charming module
from prints_charming import ColorPrinter

# Create an instance of the ColorPrinter class
cp = ColorPrinter()

# Basic printing with ColorPrinter
# 'vgreen' specifies a very bright green color
cp.print("Hello, world!", color="vgreen")

# Using a predefined style called 'task' for printing
cp.print("This is a task.", style="task")

# Using variable printing; 'orange' for text and 'vgreen' for the variable value
balance = 1.25
cp.print_var(f"Value: var USD", balance, 'orange', 'vgreen')

# Define custom styles and variables for automatic coloring/styling
# This dictionary can also be passed during instance creation as an optional parameter
colorprinter_variables = {
    "vgreen": ["Confirmed!", "Connected", "Loaded", "Monitor", "ABOVE THRESHOLD", "wss://advanced-trade-ws.coinbase.com", "Starting"],
    "vred": ["Failed!", "Error", "Failed", "None", "Skipping.", "Canceling", "Canceled"],
    "blue": ["CoinbaseWebsocketClient", "server"],
    "yellow": ["1", "returned",],
    "vyellow": ["File modified:", "File modified AGAIN", "subscribed"],
    "magenta": ["within 10 seconds."],
    "cyan": ["|", "#"],
    "orange": ["New Message!"],
    # Uncomment the next line to hide API keys or sensitive information
    #"conceal": [os.environ[key] for key in os.environ if "API" in key],
}

# Add custom variables from the dictionary to the ColorPrinter instance
cp.add_variables_from_dict(colorprinter_variables)

# Demonstration of automatic styling based on defined variables
var1 = "#"
cp.print(f"printing things and some of it will be colored the color or style defined in the dictionary. If it's Confirmed! it will be vgreen. New Message will not be colored, but New Message! will be colored orange! The number 1 will be yellow. The pound sign, {var1} will be styled/colored cyan")

# Adding a single variable for styling
cp.add_variable("some text", style_name="vcyan")
cp.print(f"part of me is styled vcyan. Some of this some text will be vcyan.")

# Adding another single variable for styling. 
# Also specifying that the text that hasn't been added to the cp instance be printed in the color, "vgreen".
var2 = "Failed to connect"
cp.add_variable(var2, style_name="red")
cp.print(f"{var2} to some server", color="vgreen")

# Adding yet another single variable for styling
cp.add_variable("more text", style_name="green")
cp.print(f"some of this will be green. Less text, more text other text.")

 # Using Dictionary with print_variables method
vars_and_styles_dict = {
    "balance" : (1000, "green"),
    "username": ("John", "blue")
}
cp.print_variables(vars_and_styles_dict, "Hello {username}, your balance is {balance} USD.", text_style="yellow")

# Using Lists with print_variables method
vars_and_styles_list = ([1000, "John"], ["green", "blue"])
cp.print_variables(vars_and_styles_list, "Hello var2, your balance is var1 USD.", text_style="yellow")
```

### Here's another simple example of creating an instance with colorprinter_variables and your own defined TextStyle styles:

```python
# Import the ColorPrinter and TextStyle classes from the colorprinter module
from prints_charming import ColorPrinter, TextStyle

colorprinter_variables = {
    "vgreen": ["Confirmed!", "Connected", "Loaded", "Monitor", "ABOVE THRESHOLD", "wss://advanced-trade-ws.coinbase.com", "Starting"],
    "vred": ["Failed!", "Error", "Failed", "None", "Skipping.", "Canceling", "Canceled"],
    "blue": ["CoinbaseWebsocketClient", "server"],
    "yellow": ["1", "returned",],
    "vyellow": ["File modified:", "File modified AGAIN", "subscribed"],
    "magenta": ["within 10 seconds."],
    "cyan": ["|", "#"],
    "orange": ["New Message!"],
    "purple": ["My background is purple and my foreground is gray because the purple style reversed option is set to True"]
    # Uncomment the next line to hide API keys or sensitive information
    #"conceal": [os.environ[key] for key in os.environ if "API" in key],
}

styles = {
        "default"      : TextStyle(),
        "vgreen"       : TextStyle(color="vgreen", bold=True, italic=True, underlined=True, overlined=True, strikethrough=True, blink=True),
        "red"          : TextStyle(color="red"),
        "vred"         : TextStyle(color="vred"),
        "blue"         : TextStyle(color="blue"),
        "yellow"       : TextStyle(color="yellow"),
        "vyellow"      : TextStyle(color="vyellow"),
        "magenta"      : TextStyle(color="magenta", bold=True),
        "vmagenta"     : TextStyle(color="vmagenta"),
        "pink"         : TextStyle(color="pink"),
        "purple"       : TextStyle(color="purple", bg_color="gray", reversed=True),
        "cyan"         : TextStyle(color="cyan"),
        "vcyan"        : TextStyle(color="vcyan"),
        "orange"       : TextStyle(color="orange"),
        "gray"         : TextStyle(color="gray"),
        "header_text"  : TextStyle(color="white", bg_color="purple", bold=True),
        "header_symbol": TextStyle(color="magenta", bold=True, overlined=True, strikethrough=True),
        "task"         : TextStyle(color="blue", bold=True),
        "conceal"      : TextStyle(conceal=True),
}


# Create an instance of the ColorPrinter class with colorprinter_variables and styles dictionaries
cp = ColorPrinter(colorprinter_variables=colorprinter_variables, styles=styles)

# Demonstration of automatic styling based on defined variables and styles
cp.print(f"My background is purple and my foreground is gray because the purple style reversed option is set to True and that phrase is in the colorprinter_variables dictionary that was added to this ColorPrinter instance. All the additional text will use default bg_color and orange text as specified in this cp.print statement", color="orange")
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



