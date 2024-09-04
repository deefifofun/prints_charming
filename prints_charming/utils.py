import os
import sys
import logging

from .exceptions import PrintsCharmingError




def get_terminal_width():
    terminal_size = os.get_terminal_size()
    return terminal_size.columns



# Define the global exception hook
def custom_excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, PrintsCharmingError):
        exc_value.handle_exception()
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def custom_excepthook_with_logging(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, PrintsCharmingError):
        exc_value.handle_exception()
    else:
        logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def set_custom_excepthook():
    sys.excepthook = custom_excepthook



def set_custom_excepthook_with_logging():
    sys.excepthook = custom_excepthook_with_logging

