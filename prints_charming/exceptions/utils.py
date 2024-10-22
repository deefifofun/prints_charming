# prints_charming.exceptions.utils.py

import sys
import traceback
import warnings
from .base_exceptions import PrintsCharmingException


def set_excepthook(pc, logger=None, log_exc_info=False, critical_exceptions=None, update_exception_logging=False):
    """
    Common helper to set sys.excepthook for handling exceptions with PrintsCharming.
    Optionally, add logging functionality if logger is provided.

    Args:
        pc (PrintsCharming): Instance of PrintsCharming used for styling exceptions.
        logger (logging.Logger): Logger instance for logging unhandled exceptions.
        log_exc_info (bool): Whether to log exception info when logging is enabled.
        critical_exceptions (tuple): List of critical exceptions to log as critical.
    """

    if pc:
        PrintsCharmingException.shared_pc_exception_instance = pc

    if critical_exceptions:
        PrintsCharmingException.critical_exceptions = critical_exceptions



    def custom_excepthook(exc_type, exc_value, exc_traceback):
        # Check if the exception is a subclass of PrintsCharmingException
        if issubclass(exc_type, PrintsCharmingException):
            exc_value.handle_exception()
        else:
            # Handle non-PrintsCharming exceptions
            general_exception = PrintsCharmingException(str(exc_value), pc, use_shared_pc=True)
            general_exception.handle_exception(logger=logger, exc_type=exc_type, exc_value=exc_value, exc_info=log_exc_info)

            """
            
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            styled_tb_lines = general_exception.stylize_traceback(tb_lines, check_subclass_names=False)
            """

            """
            # Log the exception if a logger is provided
            if logger:
                if issubclass(exc_type, critical_exceptions):
                    for line in styled_tb_lines:
                        logger.critical(line, exc_info=log_exc_info)
                else:
                    for line in styled_tb_lines:
                        logger.error(line, exc_info=log_exc_info)
            else:
                # Print the styled traceback to stderr
                for line in styled_tb_lines:
                    print(line, file=sys.stderr)
            """

    # Store the original excepthook
    default_excepthook = sys.__excepthook__

    # Check if the current excepthook is custom
    def is_custom_excepthook():
        return sys.excepthook is not default_excepthook

    # Check if it's custom
    if is_custom_excepthook():
        if not update_exception_logging:
            if logger:
                pc.print(
                    f"{pc.apply_style('red', 'sys.excepthook has already been custom set.')} {pc.apply_style('blue', 'Change')} {pc.apply_style('orange', 'update_custom_excepthook =')} True to update the custom excepthook.", color='blue')
            else:
                pc.print(f"{pc.apply_style('red', 'sys.excepthook has already been custom set.')} {pc.apply_style('blue', 'Change')} {pc.apply_style('orange', 'update_custom_excepthook =')} True to update the custom excepthook.", color='blue')
        else:
            sys.excepthook = custom_excepthook
    else:
        sys.excepthook = custom_excepthook

    # Set the custom excepthook globally
    #sys.excepthook = custom_excepthook
