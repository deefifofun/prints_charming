import inspect
import logging
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



def default_log_messages(logger, print_func_name=True):
    if print_func_name:
        logger.pc.add_string('===', 'vcyan')
        logger.pc.print(get_pretty_caller_function_name(), color='orange', italic=True)

    logger.debug("This is a plain 'debug' message.")
    logger.info("This is a plain 'info' message.")
    logger.warning("This is a plain 'warning' message.")
    logger.error("This is a plain 'error' message.")
    logger.critical("This is a plain 'critical' message.\n\n")


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
