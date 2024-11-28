# 🎉 PrintsCharming: The Ultimate Toolkit for Terminal Interfaces, Text Styling, and Advanced Functionality 🎉

![Project Illustration](./images/prints_charming_illustration.png)


## 🚀 Introduction

PrintsCharming is a powerful, self-contained Python library that seamlessly integrates powerful advanced text styling and dynamic terminal interface capabilities into your projects. It provides unmatched flexibility and customizability to create visually appealing terminal outputs that are both functional and engaging. Whether you're looking to enhance readability, streamline debugging, or build interactive terminal applications, PrintsCharming delivers a comprehensive suite of tools to meet your needs. With features like layered styling mechanisms, dynamic text wrapping, interactive components, and advanced box and table printing, it empowers developers to craft polished and professional-grade terminal interfaces effortlessly.

## ✅ Current State

For my current needs, this package does everything I require. It's particularly useful for developers who deal with extensive terminal outputs and need to quickly distinguish between different types of information. It's production-ready and has been rigorously tested in various internal projects.

## 🛠 Future Enhancements

Though **prints_charming** is replete with features tailored for Linux terminals, the fairy tale isn't over, and the door is always open for additional community-driven enhancements. Your contributions could add new chapters to the prints_charming story. 

## 🌟 Key Features
- **No Dependencies**: Entirely self-contained, built using only standard Python libraries. No third-party dependencies required.
- **Efficiency by Design**: Simplifies terminal output styling with intuitive keyword arguments. Spend less time concatenating strings and more time creating polished terminal interfaces.
- **Comprehensive Text Styling**: Supports a wide range of styling options, including foreground and background colors, bold, italic, underline, overline, strikethrough, reverse, and blinking text.
- **Layered Styling Mechanism**: Allows multi-layered and nested styling for terminal text, enabling precise formatting of individual words, phrases, substrings, or whitespace based on dynamic conditions like indices, ranges, or custom rules.
- **Nested Style Application**: Apply styles hierarchically, with outer styles dynamically adjusting to nested styles within the same text for seamless integration.
- **Intelligent Space Styling**: Whitespace between styled words inherits styles from adjacent elements, creating a cohesive appearance without manual intervention.
- **Dynamic Word and Phrase Styling**: Utilize dictionaries with ranges or specific indices to control how words or phrases are styled, allowing flexibility to adjust for runtime conditions.
- **Advanced Word and Substring Detection**: Employs trie-based techniques for efficient detection and styling of phrases, words, or substrings, with customizable precedence and ordering rules.
- **Customizable Progression Styles**: Add progressive styles—such as gradient effects or style variations—across elements like words, spaces, or substrings for visually dynamic outputs.
- **Boundary-Aware Styling**: Smart handling of word and phrase boundaries ensures styles align with logical text breaks, even when spanning multiple nested elements.
- **Dynamic Text Wrapping with ANSI Code Support**: Ensures styled text wraps cleanly within a given width, preserving both visible length and embedded styling codes.
- **Flexible and Customizable**: Leverage predefined styles or define your own for ultimate control over terminal output appearance.
- **Advanced Box and Panel Printing**: Create elegantly bordered boxes and panels with the FrameBuilder for clean and structured output.
- **Sophisticated Table Management**: Build dynamic and interactive tables with TableManager that integrate seamlessly with boxes, frames, and other UI components.
- **Layered Box and Table Integration**: Nested tables, frames, and panels are supported, making it possible to create highly organized, multi-layered layouts for terminal applications.
- **Bound Cell Support**: Dynamically update cell content within tables, enabling real-time interactive elements.
- **Nested Tables and Frames**: Support for creating complex layouts with nested tables and frames, enhancing readability and organization.
- **Logging and Exception Handling**: Includes integrated tools for logging and exception handling to streamline debugging and output tracking.
- **Integrated Multi-Level Debugging**: Provides detailed debugging for nested or layered styling, with logs to inspect how and why specific styles were applied.
- **Mouse and Keyboard Input Handling**: Supports real-time interaction with mouse events, escape sequences, and keystrokes, enabling interactive terminal applications.
- **Interactive Components**: Use interactive features like menus and tools to create engaging terminal-based programs.
- **Intelligent Defaults**: Comes with sensible defaults but allows you to tweak every aspect to your liking.
- **Built for Linux**: "Designed and optimized for Linux terminals, with additional support for legacy Windows command prompts (via autoconf_win) and modern Windows terminals out of the box.


## Example Applications:

- **Calculator UI**: An interactive calculator with a dynamic display and clickable buttons, showcasing real-time input handling and UI updates.

- **Snake Game**: A classic Snake game implementation demonstrating the use of dynamic content, real-time rendering, and keyboard input handling in the terminal.

## Interactive Customizations

To take customization even further, prints_charming includes an interactive color_map creation wizard, allowing you to define and name your own custom colors. Simply run python -m prints_charming.colors_wizard to launch the wizard and generate a personalized color_map that you can use throughout your project for seamless, consistent styling. styles_wizard coming soon.

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

### Some random screenshots

### Nested tables from TableManager nested in FrameBuilder frame
![Project Illustration](./images/examples/main/snip1.png)

### More tables and frames
![Project Illustration](./images/examples/main/snip2.png)

### More tables showing more dynamic styling
![Project Illustration](./images/examples/main/snip3.png)

### More nested tables in frames showing different alignments
![Project Illustration](./images/examples/main/snip4.png)

### Showing multi column frames wrapping text
![Project Illustration](./images/examples/main/snip5.png)

### Screenshot from the code snippet below... 
create_logger_with_its_own_default_pc_instance()
![Project Illustration](./images/examples/basic_logging/with_default_pc_instance.png)

### Screenshot from the code snippet below... 
create_logger_with_specific_pc_instance()
![Project Illustration](./images/examples/basic_logging/specific_pc_instance_with_default_bg_color_provided.png)

### Here is the PrintsCharming init method for reference used in the code below

```python

    def __init__(self,
                 config: Optional[Dict[str, Union[bool, int, str]]] = None,
                 color_map: Optional[Dict[str, str]] = None,
                 default_bg_color: Optional[str] = None,
                 effect_map: Optional[Dict[str, str]] = None,
                 unicode_map: Optional[Dict[str, str]] = None,
                 styles: Optional[Dict[str, PStyle]] = None,
                 enable_input_parsing: bool = False,
                 enable_trie_manager: bool = True,
                 styled_strings: Optional[Dict[str, List[str]]] = None,
                 styled_subwords: Optional[Dict[str, List[str]]] = None,
                 style_conditions: Optional[Any] = None,
                 formatter: Optional['Formatter'] = None,
                 autoconf_win: bool = False
                 ) -> None:

        """
        Initialize PrintsCharming with args to any of these optional params.

        :param config: enable or disable various functionalities of this class.

        :param color_map: supply your own color_map dictionary.
                          'color_name': 'ansi_code'

        :param default_bg_color: change the default background color to a color
                                 other than your terminal's background color by
                                 supplying the name of a color defined in the
                                 color map.

        :param effect_map: supply your own effect_map dictionary. Default is
                           PrintsCharming.shared_effect_map

        :param unicode_map: supply your own unicode_map dictionary. Default is
                            PrintsCharming.shared_unicode_map

        :param styles: supply your own style_map dictionary. Default is a copy
                       of the DEFAULT_STYLES dictionary unless
                       cls.shared_style_map is defined.

        :param enable_input_parsing: if True define cls.shared_reverse_input_map
                       by calling self.__class__.create_reverse_input_mapping()

        :param enable_trie_manager: if True initializes an instance of
                                    TrieManager.

        :param styled_strings: calls the add_strings_from_dict method with your
                               provided styled_strings dictionary.

        :param styled_strings: calls the add_subwords_from_dict method with your
                               provided styled_subwords dictionary.

        :param style_conditions: A custom class for implementing dynamic
                                 application of styles to text based on
                                 conditions.

        :param formatter: supply your own formatter class instance to be used
                          for formatting text printed using the print method in
                          this class.

        :param autoconf_win: If your using legacy windows cmd prompt and not
                             getting colored/styled text then change this to
                             True to make things work.
        """


```

### Here is the setup_logger function for reference used in the code below

```python

def setup_logger(
    pc: Optional[PrintsCharming] = None,
    name: Optional[str] = None,
    level: Union[int, str] = logging.DEBUG,
    datefmt: str = '%Y-%m-%d %H:%M:%S',
    handler_configs: Optional[Dict[str, Dict[str, Union[bool, str, int]]]] = None,
    color_map: Optional[Dict[str, str]] = None,
    styles: Optional[Dict[str, PStyle]] = None,
    level_styles: Optional[Dict[int, str]] = None,
    default_bg_color: Optional[str] = None,
    enable_unhandled_exception_logging: bool = False,
    update_unhandled_exception_logging: bool = False,
    log_exc_info: bool = True,
    critical_exceptions: Optional[Tuple[Type[BaseException], ...]] = None,
    unhandled_exception_debug: bool = False,
    unique: bool = True,
) -> logging.Logger:
    """
    Setup and return a logger with customizable handlers and formatters, including
    user-supplied custom handlers. Use PrintsCharmingLogHandler by default for
    custom styling and formatting.

    Args:
        pc (Optional[PrintsCharming]): An instance of PrintsCharming for styling logs.
        name (Optional[str]): Logger name (uses calling module name if None).
        level (int): Logging level for the logger. Defaults to logging.DEBUG.
        datefmt (str): Date format for the formatter.
        handler_configs (Optional[Dict[str, Dict[str, Union[bool, str, int]]]]):
            Configuration for handlers. Example:
                {
                    'console': {
                        'enabled': True,
                        'use_styles': True,
                        'formatter': CustomFormatter()
                    },
                    'file': {
                        'path': '/path/to/log',
                        'use_styles': False,
                        'level': logging.INFO
                    },
                    'custom_handler': {
                        'handler': MyCustomHandler(),
                        'formatter': CustomFormatter(),
                        'use_styles': False
                    }
                }
        color_map (Optional[Dict[str, str]]): Custom color map.
        styles (Optional[Dict[str, PStyle]]): Custom styles.
        level_styles (Optional[Dict[int, str]]): Dictionary mapping logging
            levels to style names.
        default_bg_color (Optional[str]): Default background color for logs.
        enable_unhandled_exception_logging (bool): Enable logging of unhandled exceptions.
        update_unhandled_exception_logging (bool): Update exception logging to new values.
        log_exc_info (bool): Enable logging of exception info.
        critical_exceptions (Optional[Tuple[Type[BaseException], ...]]): A tuple
            of exception types to log as critical.
        unhandled_exception_debug (bool): Debug mode for unhandled exceptions.
        unique (bool): If True (default), create a unique logger if the specified
            or derived name already exists.

    Returns:
        logging.Logger: Configured logger instance with specified handlers.
    """

    # Convert level to integer
    level = get_log_level(level)

    pc = pc or PrintsCharming(
        color_map=color_map or DEFAULT_COLOR_MAP.copy(),
        styles=copy.deepcopy(styles) or copy.deepcopy(DEFAULT_STYLES),
        default_bg_color=default_bg_color)

    if name is None:
        # Use inspect to get the module name of the caller
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        if caller_module is not None:
            name = caller_module.__name__

    # Check if a logger with this name already exists
    if unique and name in logging.Logger.manager.loggerDict:
        # Append a unique identifier to ensure a unique logger name
        name = f"{name}_{uuid.uuid4().hex}"

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Attach the `pc` instance to the logger for future access
    logger.pc = pc

    if enable_unhandled_exception_logging:
        set_custom_excepthook_with_logging(
            logger,
            pc,
            log_exc_info,
            critical_exceptions,
            unhandled_exception_debug,
            update_unhandled_exception_logging,
        )

    # Helper function to create or use a supplied formatter
    def create_formatter(
            use_styles: Optional[bool] = None,
            custom_formatter: Optional[logging.Formatter] = None,
    ) -> logging.Formatter:
        """
        Helper function to create or use a supplied formatter.

        Args:
            use_styles (Optional[bool]): Whether to use styles.
            custom_formatter (Optional[logging.Formatter]): Custom formatter provided by the user.

        Returns:
            logging.Formatter: Formatter instance.
        """

        if custom_formatter:
            return custom_formatter  # If a custom formatter is provided, use it

        # Otherwise, create a PrintsCharmingFormatter with or without styles
        return PrintsCharmingFormatter(
            pc=pc,
            datefmt=datefmt,
            level_styles=level_styles or {
                logging.DEBUG: 'debug',
                logging.INFO: 'info',
                logging.WARNING: 'warning',
                logging.ERROR: 'error',
                logging.CRITICAL: 'critical'
            },
            use_styles=use_styles
        )

    # Handler factory function to create standard handlers
    def handler_factory(
            handler_name: str, config: Dict[str, Union[bool, str, int]]
    ) -> Optional[logging.Handler]:
        """
        Factory function to create standard handlers.

        Args:
            handler_name (str): Name of the handler.
            config (Dict[str, Any]): Configuration for the handler.

        Returns:
            Optional[logging.Handler]: Handler instance or None.
        """

        if handler_name == 'console':
            return PrintsCharmingLogHandler(pc=pc)
        elif handler_name == 'file':
            return logging.FileHandler(config['path'])  # Use standard FileHandler
        elif handler_name == 'rotating_file':
            return logging.handlers.RotatingFileHandler(
                config['path'],
                maxBytes=config.get('max_bytes', 10485760),
                backupCount=config.get('backup_count', 5)
            )
        elif handler_name == 'syslog':
            return logging.handlers.SysLogHandler(address=config.get('address', '/dev/log'))
        elif handler_name == 'smtp':
            mailhost = config.get('mailhost', 'localhost')
            fromaddr = config.get('fromaddr', 'error@example.com')
            toaddrs = config.get('toaddrs', ['admin@example.com'])
            subject = config.get('subject', 'Application Error')
            credentials = config.get('credentials', None)
            secure = config.get('secure', None)
            return logging.handlers.SMTPHandler(
                mailhost=mailhost,
                fromaddr=fromaddr,
                toaddrs=toaddrs,
                subject=subject,
                credentials=credentials,
                secure=secure
            )
        return None  # Return None if no handler matches

    # Helper function to add handler
    def add_handler(
            handler: logging.Handler,
            level: int,
            formatter: logging.Formatter,
    ) -> None:
        """
        Helper function to add handler to the logger.

        Args:
            handler (logging.Handler): The logging handler.
            level (int): Logging level.
            formatter (logging.Formatter): Formatter for the handler.
        """
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Set default handler configurations if none are provided
    if not handler_configs:
        handler_configs = {
            'console': {'enabled': True, 'use_styles': True},
            'file': {'enabled': False},
            'rotating_file': {'enabled': False},
            'syslog': {'enabled': False},
            'smtp': {'enabled': False}
        }

    # Loop over handler configurations and create handlers
    for handler_name, config in handler_configs.items():
        if not config.get('enabled', False):
            continue  # Skip disabled handlers

        # Check if the user supplied a custom handler
        handler = config.get('handler') or handler_factory(handler_name, config)
        if not handler:
            continue  # Skip if no handler was created

        use_styles = config.get('use_styles', True)
        custom_formatter = config.get('formatter')  # User-supplied custom formatter (optional)

        # Determine the formatter to use (custom or default)
        log_formatter = create_formatter(
            use_styles=use_styles, custom_formatter=custom_formatter
        )
        handler_level = config.get('level', level)

        # Add the handler to the logger
        add_handler(handler, handler_level, log_formatter)

    return logger

```


```python

import inspect
from prints_charming import (
    PStyle,
    PrintsCharming,
)

from prints_charming.logging import setup_logger



def get_pretty_caller_function_name():
    # Get the current frame, then the caller's frame
    stack = inspect.stack()
    if len(stack) > 2:  # Ensure there is a caller
        caller_frame = stack[1]
        return f"=== {caller_frame.function} ===\n"
    return None


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
    logger.pc.print(get_pretty_caller_function_name(), color='orange', italic=True, fill_to_end=True if logger.pc.default_bg_color else False)

    # PrintsCharming instance
    pc = logger.pc

    nl = '\n\n'

    # Dynamically populate log_methods using PrintsCharming.log_level_style_names
    log_methods = {level_name: getattr(logger, level_name) for level_name in PrintsCharming.log_level_style_names}

    # Iterate through each log level, applying unique styles and logging
    for level_name, log_method in log_methods.items():
        # Apply styles specific to each log level
        styled_text1 = apply_logging_style(pc, level_name, 'purple', 'pre-styled')
        styled_text2 = apply_logging_style(pc, level_name, 'orange', 'message.')

        # Log the message with the dynamically styled texts
        log_method(f"This is another {styled_text1} '{level_name}' {styled_text2}{nl if level_name == 'critical' else ''}")

    for level_name, log_method in log_methods.items():
        if level_name != 'critical':
            # Log the message using log_method with positional formatting
            log_method("arg 1: {} and arg 2: {}", "arg1 is a phrase!", "arg2 is a phrase too!")
        else:
            # Log the message using log_method with positional formatting + newlines
            log_method("arg 1: {} and arg 2: {} {}", "arg1 is a phrase!", "arg2 is a phrase too!", nl)


# use positional formatting with *args
def positional_formatting_log_messages(logger,
                                       arg1='argument_1',
                                       arg2='argument_2'):

    logger.pc.print(get_pretty_caller_function_name(), color='orange', italic=True, fill_to_end=True if logger.pc.default_bg_color else False)

    logger.debug("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.info("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.warning("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.error("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.critical("arg 1: {} and arg 2: {}\n", arg1, arg2)


def prestyle_parts_of_log_messages(logger):
    logger.pc.print(get_pretty_caller_function_name(), color='orange', italic=True, fill_to_end=True if logger.pc.default_bg_color else False)
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
    logger.critical(f"This is a 'critical' {critical_styled_text[0]} with some {critical_styled_text[1]} text.\n")


def default_log_messages(logger):
    logger.pc.trie_manager.add_string('===', 'vcyan')
    logger.pc.print(get_pretty_caller_function_name(), color='orange', italic=True, fill_to_end=True if logger.pc.default_bg_color else False)

    logger.debug("This is a plain 'debug' message.")
    logger.info("This is a plain 'info' message.")
    logger.warning("This is a plain 'warning' message.")
    logger.error("This is a plain 'error' message.")
    logger.critical("This is a plain 'critical' message.\n")


def create_logger_with_specific_pc_instance():
    # Create specific PrintsCharming instance.
    # use default_bg_color of the environment your printing to if not in a terminal session.
    # For instance pycharm jupyter notebook
    pc = PrintsCharming(default_bg_color='dgray')

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

    logger.pc.trie_manager.add_string('===', 'vcyan')

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




## 📧 Contact
For bugs, feature requests, and suggestions, please open an issue on GitHub.



