from typing import Any, Optional, Dict, Union, List, Tuple, Type
import logging
import inspect
from prints_charming import (
    PStyle,
    PrintsCharming,
)

from prints_charming.logging import setup_logger



def get_pretty_caller_function_name() -> Optional[str]:
    """
    Retrieves a formatted string containing the name of the caller function.

    Returns:
        Optional[str]: Formatted caller function name or None if not available.
    """
    # Get the current frame, then the caller's frame
    stack = inspect.stack()
    if len(stack) > 2:  # Ensure there is a caller
        caller_frame = stack[1]
        return f"=== {caller_frame.function} ===\n"
    return None



def apply_logging_style(pc: PrintsCharming, level: str, style_name: str, text: str) -> str:
    """
    Applies a specified style to the text and appends the style code corresponding to the log level.

    Args:
        pc (PrintsCharming): Instance of PrintsCharming to apply styles.
        level (str): Log level name (e.g., 'debug', 'info', etc.).
        style_name (str): Name of the style to apply.
        text (str): Text to style.

    Returns:
        str: Styled text with appended log level style code.
    """
    return pc.apply_style(style_name, text) + pc.style_codes.get(level)


def apply_logging_debug_style(pc: PrintsCharming, style_name: str, text: str) -> str:
    """
    Applies the 'debug' log level style to the text.

    Args:
        pc (PrintsCharming): Instance of PrintsCharming to apply styles.
        style_name (str): Name of the style to apply.
        text (str): Text to style.

    Returns:
        str: Styled text with appended 'debug' log level style code.
    """
    return apply_logging_style(pc, 'debug', style_name, text)


def apply_logging_info_style(pc: PrintsCharming, style_name: str, text: str) -> str:
    """
    Applies the 'info' log level style to the text.

    Args:
        pc (PrintsCharming): Instance of PrintsCharming to apply styles.
        style_name (str): Name of the style to apply.
        text (str): Text to style.

    Returns:
        str: Styled text with appended 'info' log level style code.
    """
    return apply_logging_style(pc, 'info', style_name, text)


def apply_logging_warning_style(pc: PrintsCharming, style_name: str, text: str) -> str:
    """
    Applies the 'warning' log level style to the text.

    Args:
        pc (PrintsCharming): Instance of PrintsCharming to apply styles.
        style_name (str): Name of the style to apply.
        text (str): Text to style.

    Returns:
        str: Styled text with appended 'warning' log level style code.
    """
    return apply_logging_style(pc, 'warning', style_name, text)


def apply_logging_error_style(pc: PrintsCharming, style_name: str, text: str) -> str:
    """
    Applies the 'error' log level style to the text.

    Args:
        pc (PrintsCharming): Instance of PrintsCharming to apply styles.
        style_name (str): Name of the style to apply.
        text (str): Text to style.

    Returns:
        str: Styled text with appended 'error' log level style code.
    """
    return apply_logging_style(pc, 'error', style_name, text)


def apply_logging_critical_style(pc: PrintsCharming, style_name: str, text: str) -> str:
    """
    Applies the 'critical' log level style to the text.

    Args:
        pc (PrintsCharming): Instance of PrintsCharming to apply styles.
        style_name (str): Name of the style to apply.
        text (str): Text to style.

    Returns:
        str: Styled text with appended 'critical' log level style code.
    """
    return apply_logging_style(pc, 'critical', style_name, text)


def more_log_message_examples(logger: logging.Logger) -> None:
    """
    Provides more examples of log messages with different styles and log levels.

    Args:
        logger (logging.Logger): Logger instance to log messages.
    """
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


# Use positional formatting with *args
def positional_formatting_log_messages(logger: logging.Logger,
                                       arg1: str = 'argument_1',
                                       arg2: str = 'argument_2') -> None:
    """
    Logs messages using positional formatting with provided arguments.

    Args:
        logger (logging.Logger): Logger instance to log messages.
        arg1 (str): First argument for formatting.
        arg2 (str): Second argument for formatting.
    """

    logger.pc.print(get_pretty_caller_function_name(), color='orange', italic=True, fill_to_end=True if logger.pc.default_bg_color else False)

    logger.debug("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.info("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.warning("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.error("arg 1: {} and arg 2: {}", arg1, arg2)
    logger.critical("arg 1: {} and arg 2: {}\n", arg1, arg2)


def prestyle_parts_of_log_messages(logger: logging.Logger) -> None:
    """
    Logs messages with parts of the message pre-styled.

    Args:
        logger (logging.Logger): Logger instance to log messages.
    """
    logger.pc.print(get_pretty_caller_function_name(), color='orange', italic=True, fill_to_end=True if logger.pc.default_bg_color else False)

    # Access pc instance with
    pc = logger.pc

    def get_level_code(level):
        return pc.style_codes.get(level)

    # Pre-style parts of log messages
    styled_text = pc.apply_styles(
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


def default_log_messages(logger: logging.Logger) -> None:
    """
    Logs default messages for each log level without additional styling.

    Args:
        logger (logging.Logger): Logger instance to log messages.
    """
    logger.pc.trie_manager.add_string('===', 'vcyan')
    logger.pc.print(get_pretty_caller_function_name(), color='orange', italic=True, fill_to_end=True if logger.pc.default_bg_color else False)

    logger.debug("This is a plain 'debug' message.")
    logger.info("This is a plain 'info' message.")
    logger.warning("This is a plain 'warning' message.")
    logger.error("This is a plain 'error' message.")
    logger.critical("This is a plain 'critical' message.\n")


def create_logger_with_specific_pc_instance() -> None:
    """
    Creates a logger with a specific PrintsCharming instance and logs various messages.
    """
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


def create_logger_with_its_own_default_pc_instance() -> None:
    """
    Creates a logger with its own default PrintsCharming instance and logs various messages.
    """
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



def main() -> None:
    """
    Main function to execute logging examples with different PrintsCharming instances.
    """

    create_logger_with_its_own_default_pc_instance()
    create_logger_with_specific_pc_instance()


if __name__ == "__main__":
    main()
