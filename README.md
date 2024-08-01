# 🎉 prints_charming: The Ultimate Terminal Text Coloring and Styling Solution 🎉

![Project Illustration](./images/prints_charming_illustration.png)


## 🚀 Introduction

Announcing the third public release of **prints_charming**! Initially created in March of 2023, this Python package has become an indispensable part of my development workflow. It has seen extensive use in 100+ of my own Python modules across various private projects I have been working on over the last eight months. "prints_charming" is more than just another color printing library; it's crafted to elevate your development experience by providing a swift and streamlined way to color and style terminal outputs—be it for standard printing, logging, debugging, or tracing—all without becoming an obstruction in your development process. While the library serves as a robust tool for making terminal outputs more readable, visually appealing, and informative, its true power lies in its versatility—enhancing the entire terminal and programming experience.

## ✅ Current State

For my current needs, this package does everything I require. It's particularly useful for developers who deal with extensive terminal outputs and need to quickly distinguish between different types of information. It's production-ready and has been rigorously tested in various internal projects.

## 🛠 Future Enhancements

Though **prints_charming** is replete with features tailored for Linux terminals, the fairy tale isn't over, and the door is always open for additional community-driven enhancements. While my current commitments across multiple projects may limit my immediate involvement in further development, your contributions could add new chapters to the prints_charming story. 

## 🌟 Key Features

- **No Dependencies**: Works with the standard Python libraries
- **Efficiency by Design**: With prints_charming, styling your terminal outputs is as simple as adding a keyword argument. Spend less time fiddling with string concatenation and more time writing great code.
- **Text Styling**: Apply foreground and background colors, bold, italic, underlined, and more to your text.
- **Flexible and Customizable**: Use predefined styles or define your own.
- **Variable, Word, Phrase, and substring Styling**: Automatically apply styles to specific variables, words, substrings or phrases in your text.
- **Box/Panel Printing with FormattedTextBox**: Create beautiful Bordered Boxes for sectioning your outputs.
- -**Tablel Printing with TableManager**: Create beautiful Tables inside Boxes or on their own.
- **Intelligent Defaults**: Comes with sensible defaults but allows you to tweak every aspect to your liking.
- **Built for Linux**: This module is developed on Linux for use in Linux terminals, but also supports legacy windows cmd prompt if you set the autoconf_win parameter to True in the init method of PrintsCharming or the WinUtils class, and it supports newer versions of windows os out of the box.

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


### Here are examples of the basics. Please check out main.py in the examples folder for more 

- **show_colors module**: run python -m prints_charming.show_colors for an interactive way to select and name your own colors for the color_map.



```python



from prints_charming import (
    TextStyle,
    PrintsCharming,
    PrintsCharmingLogHandler,
    TableManager,
    FormattedTextBox,
    PrintsCharmingError,
    set_custom_excepthook
)

import os
import sys
import logging




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

# Create an instance of the PrintsCharming class with default settings, but add printscharming_variables
pc = PrintsCharming(printscharming_variables=printscharming_variables)
pc.print("# Basic printing with ColorPrinter will print in the default style with default color.")
pc.print("Hello, world!")
pc.print("# Print in the default style reverse foreground and background.")
pc.print("Hello, world!", reverse=True)
pc.print("# Specify only the color of the args.")
pc.print("Hello, world!", color="red", dim=True)
pc.print("# Specify only italic and underline will print in the default color.")
pc.print("Hello, world!", italic=True, underline=True)
pc.print("# Specify a predefined style 'magenta'. The 'magenta' style is defined above.")
pc.print("Hello, world!", style="magenta")
pc.print("# Specify predefined style 'task' for printing. The 'task' style is defined above.")
pc.print("This is a task.", style="task")
pc.print("# Specify predefined style 'task' for printing but change color to green and underline to True.")
pc.print("This is a task.", style="task", color="green", underline=True)
pc.print("Show text with bg_color:")
pc.print("This has a bg_color", style="bg_color_green")
pc.print("# Show that 'Hello, world!' isn't color or style defined.")
pc.print("Hello, world!")
print()

```

```python



from prints_charming import (
    TextStyle,
    PrintsCharming,
    PrintsCharmingLogHandler,
    TableManager,
    FormattedTextBox,
    PrintsCharmingError,
    set_custom_excepthook
)

import os
import sys
import logging

pc = PrintsCharming()

pc.print("# Use the add_variable method to add 'Hello, world!' to the phrases dictionary with 'vgreen' style.")
pc.add_variable("Hello, world!", style_name="vgreen")
pc.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
pc.print("Hello, world!")
pc.print("# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.")
pc.remove_variable("Hello, world!")
pc.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
pc.print("Hello, world!")
pc.print("# Define a variable.")
text = "Hello, world!"
pc.print(f"# Use the add_variable method to add {text} to the phrases dictionary with 'yellow' style.")
pc.add_variable(text, style_name="yellow")
pc.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
pc.print(text)
pc.print("# Show that 'Hello, world!' retains its style while other words are unstyled.")
pc.print(f"This sentence says, {text}")
pc.print("# Show how you can style other words alongside, 'Hello, world!'.")
pc.print(f"This sentence says, {text}", style='task')
pc.print("# Show how the order of the words doesn't matter.")
pc.print(f"{text} Let me say that again, {text} {text} I said it again!", style="orange")
pc.print("# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.")
pc.remove_variable("Hello, world!")
pc.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
pc.print("Hello, world!")
print()

```

```python



from prints_charming import (
    TextStyle,
    PrintsCharming,
    PrintsCharmingLogHandler,
    TableManager,
    FormattedTextBox,
    PrintsCharmingError,
    set_custom_excepthook
)

import os
import sys
import logging

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

    
    play_around_with_logging()
    
    
    
if __name__ == "__main__":
    main()

```



## 📧 Contact
For bugs, feature requests, and suggestions, please open an issue on GitHub.



