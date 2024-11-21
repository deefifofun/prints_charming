import sys
from typing import Any, Dict, List, Optional, Union
from prints_charming import (
    PStyle,
    DEFAULT_COLOR_MAP,
    DEFAULT_STYLES,
    get_terminal_width,
    PrintsCharming,
)

from prints_charming.logging import setup_logger

from prints_charming.exceptions import PrintsCharmingException





class CustomError(PrintsCharmingException):
    """Custom error for specific use cases."""
    def __init__(self, message: str, pc: 'PrintsCharming', additional_info: str, format_specific_exception: bool = True) -> None:
        super().__init__(message, pc, format_specific_exception=format_specific_exception)
        self.additional_info = additional_info

    def __str__(self):
        # Include both the main message and any additional info in the output
        return f"{self.message} | Additional Info: {self.additional_info}"

    def handle_exception(self, logger=None, exc_type=None, exc_value=None, exc_info=None, print_error=False, full_traceback=True):
        super().handle_exception(logger, exc_type, exc_value, exc_info, print_error)


class CustomError2(PrintsCharmingException):
    """Custom error for specific use cases with additional context."""

    _pc_instance = None  # Subclass-specific PrintsCharming instance

    @classmethod
    def set_pc(cls, pc: 'PrintsCharming'):
        """Set the PrintsCharming instance for this subclass."""
        cls._pc_instance = pc

    def __init__(self, message: str = "Custom error occurred", additional_info: str = "Additional context info",
                 format_specific_exception: bool = True,
                 pc_error: 'PrintsCharming' = None,
                 check_subclass_names: bool = False,
                 use_shared_pc: bool = False):

        """
        Initialize the exception.
        If `use_shared_pc` is True, use the shared instance, otherwise use subclass-specific instance.
        """

        # Use subclass-specific pc instance if not using shared instance
        if not use_shared_pc:
            if not self.__class__._pc_instance:
                raise ValueError("The PrintsCharming instance must be set using `CustomError2.set_pc()` before raising.")
            self.pc = self.__class__._pc_instance
        else:
            if not PrintsCharmingException.shared_pc_exception_instance:
                if not pc_error:
                    raise ValueError(f"The init call to {self.__class__.__name__} instance must supply a pc instance to the pc_error parameter when use_shared_pc parameter is True.")
                PrintsCharmingException.shared_pc_exception_instance = pc
            self.pc = PrintsCharmingException.shared_pc_exception_instance  # Use shared instance



        # Call the superclass constructor with default and passed parameters
        super().__init__(message=message, pc=self.pc, format_specific_exception=format_specific_exception, check_subclass_names=check_subclass_names, use_shared_pc=use_shared_pc)

        # Store additional information for this custom error
        self.additional_info = additional_info

    def handle_exception(self, logger=None, exc_type=None, exc_value=None, exc_info=None, print_error=False, full_traceback=True):
        """Handle the exception and print additional information."""
        # Call the base class method to handle the exception
        super().handle_exception()

        # Print the additional information styled with cyan
        print(self.pc.apply_style('cyan', self.additional_info), file=sys.stderr)



class CustomError3(PrintsCharmingException):
    """Another custom error subclass with its own PrintsCharming instance."""

    _pc_instance = None  # Subclass-specific PrintsCharming instance

    @classmethod
    def set_pc(cls, pc: 'PrintsCharming'):
        """Set the PrintsCharming instance for this subclass."""
        cls._pc_instance = pc

    def __init__(self, message: str = "CustomError3 occurred", additional_info: str = "Different context",
                 format_specific_exception: bool = True,
                 pc_error: 'PrintsCharming' = None,
                 check_subclass_names: bool = False,
                 use_shared_pc: bool = False):
        """
        Initialize the exception.
        If `use_shared_pc` is True, use the shared instance, otherwise use subclass-specific instance.
        """
        if not use_shared_pc:
            if not self.__class__._pc_instance:
                raise ValueError("The PrintsCharming instance must be set using `CustomError3.set_pc()` before raising.")
            self.pc = self.__class__._pc_instance
        else:
            if not PrintsCharmingException.shared_pc_exception_instance:
                if not pc_error:
                    raise ValueError(f"The init call to {self.__class__.__name__} instance must supply a pc instance to the pc_error parameter when use_shared_pc parameter is True.")
                PrintsCharmingException.shared_pc_exception_instance = pc
            self.pc = PrintsCharmingException.shared_pc_exception_instance  # Use shared instance

        self.additional_info = additional_info
        super().__init__(message, pc=self.pc, format_specific_exception=format_specific_exception, check_subclass_names=check_subclass_names, use_shared_pc=use_shared_pc)

    def handle_exception(self, logger=None, exc_type=None, exc_value=None, exc_info=None, print_error=False, full_traceback=True):
        """Handle the exception and print additional information."""
        super().handle_exception()
        print(self.pc.apply_style('green', self.additional_info), file=sys.stderr)



def raise_type_error():
    """Example of triggering a TypeError."""
    sample_list = [1, 2, 3]
    # This will raise a TypeError as you can't add a string to an int in a list
    invalid_operation = sum(sample_list) + 'a'


def raise_attribute_error():
    """Example of triggering an AttributeError."""
    class Sample:
        def __init__(self):
            self.name = 'Sample'

    sample_instance = Sample()
    # Trying to access a non-existent attribute
    invalid_attr = sample_instance.non_existent_attribute


def raise_key_error():
    """Example of triggering a KeyError."""
    sample_dict = {'a': 1, 'b': 2}
    # Accessing a non-existent key
    non_existent_key = sample_dict['c']


def custom_excepthook_error_example():
    zero_div_error = 1 / 0


def handle_exception_with_custom_error(exc, logger, pc, info):
    wrapped_exception = CustomError(str(exc), pc, info)
    wrapped_exception.handle_exception(logger=logger, exc_type=type(exc), exc_value=exc, exc_info=info)



def custom_exception_handling_demo(logger):
    """Set up custom exception handling with additional debug logging."""

    # Get PrintsCharming instance attached to logger
    pc = logger.pc

    # Trigger unhandled exceptions
    try:
        raise_type_error()
    except Exception as e:
        handle_exception_with_custom_error(e, logger, pc, "TypeError occurred")

    try:
        raise_attribute_error()
    except Exception as e:
        handle_exception_with_custom_error(e, logger, pc, "AttributeError occurred")

    try:
        raise_key_error()
    except Exception as e:
        handle_exception_with_custom_error(e, logger, pc, "KeyError occurred")

    # No try-except block; this will be caught by custom_excepthook
    custom_excepthook_error_example()  # This will raise a ZeroDivisionError

    try:
        raise CustomError("Error in custom_exception_handling_demo", pc, 'Context for CustomError')
    except CustomError as e:
        e.handle_exception(logger=logger, exc_type=type(e), exc_value=e, exc_info=e.__traceback__)


def create_logger_with_unhandled_exception_logging():
    pc = PrintsCharming()
    logger = setup_logger(pc=pc, name='exception_logger', enable_unhandled_exception_logging=True)

    custom_exception_handling_demo(logger)







def main():
    create_logger_with_unhandled_exception_logging()





if __name__ == "__main__":
    try:
        main()
    except CustomError2 as e:
        print(f"Caught CustomError2: {e}")
        print(f"Additional info: {e.additional_info}")
        e.handle_exception()













