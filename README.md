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


### Here are examples of the basics. Please check out main.py in the examples folder for more. Will be updated soon. 

- **show_colors module**: run python -m prints_charming.show_colors for an interactive way to select and name your own colors for the color_map.



```python

from prints_charming import (
    PStyle,
    PrintsCharming,
)

from prints_charming.logging import setup_logger



def apply_logging_style(pc, level, style_name, text):
    return pc.apply_style(style_name, text) + pc.style_codes.get(level)


def apply_logging_debug_style(pc, style_name, text):
    return apply_logging_style(pc, 'debug', style_name, text)


def apply_logging_info_style(pc, style_name, text):
    return apply_logging_style(pc, 'info', style_name, text)


def apply_logging_warning_style(pc, style_name, text):
    return apply_logging_style(pc, 'warning', style_name, text)


def apply_logging_error_style(pc, style_name, text):
    return apply_logging_style(pc, 'error', style_name, text)


def apply_logging_critical_style(pc, style_name, text):
    return apply_logging_style(pc, 'critical', style_name, text)


def more_log_message_examples(logger):

    # PrintsCharming instance
    pc = logger.pc

    newlines = f'\n\n'

    # Dynamically populate log_methods using PrintsCharming.log_level_style_names
    log_methods = {level_name: getattr(logger, level_name) for level_name in PrintsCharming.log_level_style_names}

    # Iterate through each log level, applying unique styles and logging
    for level_name, log_method in log_methods.items():
        # Apply styles specific to each log level
        styled_text1 = apply_logging_style(pc, level_name, 'purple', 'pre-styled')
        styled_text2 = apply_logging_style(pc, level_name, 'orange', 'message.')

        # Log the message with the dynamically styled texts
        log_method(f"This is another {styled_text1} '{level_name}' {styled_text2}{newlines if level_name == 'critical' else ''}")

    for level_name, log_method in log_methods.items():
        if level_name != 'critical':
            # Log the message using log_method with positional formatting
            log_method("arg 1: {} and arg 2: {}", "arg1 is a phrase!", "arg2 is a phrase too!")
        else:
            # Log the message using log_method with positional formatting + newlines
            log_method("arg 1: {} and arg 2: {} {}", "arg1 is a phrase!", "arg2 is a phrase too!", "\n\n")


# use positional formatting with *args
def positional_formatting_log_messages(logger,
                                       arg1='argument_1',
                                       arg2='argument_2'):

    logger.debug("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.info("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.warning("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.error("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.critical("arg 1: {} and arg 2: {}\n\n", arg1, arg2)


def prestyle_parts_of_log_messages(logger):
    # Access pc instance with
    pc = logger.pc

    def get_level_code(level):
        return pc.style_codes.get(level)

    # Pre-style parts of log messages
    styled_text = pc.apply_indexed_styles(
        ['message', 'pre-styled'],
        ['vyellow', 'purple'],
        return_list=True
    )

    # Append log level codes to styled text
    debug_styled_text = [styled_text[0] + get_level_code('debug'), styled_text[1] + get_level_code('debug')]
    info_styled_text = [styled_text[0] + get_level_code('info'), styled_text[1] + get_level_code('info')]
    warning_styled_text = [styled_text[0] + get_level_code('warning'), styled_text[1] + get_level_code('warning')]
    error_styled_text = [styled_text[0] + get_level_code('error'), styled_text[1] + get_level_code('error')]
    critical_styled_text = [styled_text[0] + get_level_code('critical'), styled_text[1] + get_level_code('critical')]

    # Pre-styled log messages
    logger.debug(f"This is a 'debug' {debug_styled_text[0]} with some {debug_styled_text[1]} text.")
    logger.info(f"This is an 'info' {info_styled_text[0]} with some {info_styled_text[1]} text.")
    logger.warning(f"This is a 'warning' {warning_styled_text[0]} with some {warning_styled_text[1]} text.")
    logger.error(f"This is an 'error' {error_styled_text[0]} with some {error_styled_text[1]} text.")
    logger.critical(f"This is a 'critical' {critical_styled_text[0]} with some {critical_styled_text[1]} text.\n\n")



def default_log_messages(logger):
    logger.debug("This is a plain 'debug' message.")
    logger.info("This is a plain 'info' message.")
    logger.warning("This is a plain 'warning' message.")
    logger.error("This is a plain 'error' message.")
    logger.critical("This is a plain 'critical' message.\n\n")





def create_logger_with_specific_pc_instance():
    # Create specific PrintsCharming instance.
    pc = PrintsCharming(default_bg_color='jupyter')

    # Pass PrintsCharming instance 'pc' and give the logger a name
    logger = setup_logger(pc=pc, name='my_logger')

    default_log_messages(logger)

    prestyle_parts_of_log_messages(logger)

    positional_formatting_log_messages(logger)

    # Edit args styling
    args_style = PStyle(color="vyellow", bold=True)
    pc.edit_style("args", args_style)

    positional_formatting_log_messages(logger)

    more_log_message_examples(logger)





def create_logger_with_its_own_default_pc_instance():
    # setup a logger with default values
    logger = setup_logger()
    pc = logger.pc

    default_log_messages(logger)

    prestyle_parts_of_log_messages(logger)

    positional_formatting_log_messages(logger)

    # Edit args styling
    args_style = PStyle(color="magenta", bold=True)
    pc.edit_style("args", args_style)

    positional_formatting_log_messages(logger)

    more_log_message_examples(logger)



def main():

    create_logger_with_its_own_default_pc_instance()
    create_logger_with_specific_pc_instance()


if __name__ == "__main__":
    main()



```

```python





```

```python





```



## 📧 Contact
For bugs, feature requests, and suggestions, please open an issue on GitHub.



