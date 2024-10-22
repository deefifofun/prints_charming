# prints_charming.exceptions.base_exceptions.py

import re
import traceback
import sys
import copy
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from ..prints_charming_defaults import DEFAULT_STYLES




def get_all_subclass_names(cls, trailing_char=None):
    subclasses = set(cls.__subclasses__())
    result = {subclass.__name__ + (trailing_char or '') for subclass in subclasses}
    for subclass in subclasses.copy():
        result.update(get_all_subclass_names(subclass, trailing_char))
    return result



class PrintsCharmingException(Exception):
    """Base class for all exceptions using PrintsCharming."""

    # Class-level instance as the fallback
    shared_pc_exception_instance = None

    # Critical Exceptions
    critical_exceptions = (SystemExit, MemoryError, KeyboardInterrupt, OSError)

    # Builtin Exceptions
    builtin_exceptions = [
        OverflowError,
        ZeroDivisionError,
        FloatingPointError,
        AssertionError,
        AttributeError,
        BufferError,
        EOFError,
        ImportError,
        ModuleNotFoundError,
        IndexError,
        KeyError,
        MemoryError,
        NameError,
        UnboundLocalError,
        BlockingIOError,
        FileNotFoundError,
        PermissionError,
        ReferenceError,
        RuntimeError,
        RecursionError,
        SyntaxError,
        TypeError,
        ValueError,
        UnicodeEncodeError,
        ChildProcessError,
        ConnectionError,
        BrokenPipeError,
        ProcessLookupError,
        TimeoutError,
        NotImplementedError,
        StopIteration,
        StopAsyncIteration,
        SystemError,
        TabError,
        DeprecationWarning,
        PendingDeprecationWarning,
        SyntaxWarning,
        UserWarning,
        ResourceWarning,
        BytesWarning,
        GeneratorExit,
        KeyboardInterrupt,
        SystemExit
    ]

    def __init__(self,
                 message: str,
                 pc: 'PrintsCharming',
                 use_shared_pc: bool = False,
                 tb_style_name: str = 'default',
                 format_specific_exception: bool = False,
                 file_line_regex: Optional[str] = r'(File ")(.*?)(/[^/]+)(", line )(\d+)(, )(in )(.*)',
                 check_subclass_names: bool = True) -> None:

        """
        Initialize the exception.
        If `use_shared_pc` is True, use the shared `PrintsCharming` instance across all subclasses.
        Otherwise, use the provided or subclass-specific `PrintsCharming` instance.
        """

        super().__init__(message)
        self.message = message

        # If using the shared PrintsCharming instance, set it at the class level
        if use_shared_pc:
            if not self.__class__.shared_pc_exception_instance:
                self.__class__.shared_pc_exception_instance = pc
            self.pc = self.__class__.shared_pc_exception_instance  # Use shared instance if flagged
        else:
            self.pc = pc  # Use provided instance
        self.apply_style = self.pc.apply_style
        self.tb_style_name = tb_style_name
        self.format_specific_exception = format_specific_exception
        self.file_line_regex = re.compile(file_line_regex)
        self.check_subclass_names = check_subclass_names

    def __str__(self):
        return self.message

    def format_traceback(self, tb):
        return self.apply_style(self.tb_style_name, tb)

    def print_error(self):
        print(self.message)
        print()

    def stylize_traceback(self, tb_lines, check_subclass_names=True):

        styled_lines = []

        # Only fetch subclass names if the flag is set to True
        subclass_names_with_colon = []
        if check_subclass_names:
            subclass_names_with_colon = list(get_all_subclass_names(PrintsCharmingException, trailing_char=':'))

        for line in tb_lines:
            leading_whitespace = re.match(r"^\s*", line).group()

            if line.startswith("Traceback"):
                styled_line = self.apply_style('header', line)
                styled_lines.append(' ')
                styled_lines.append(styled_line)
                styled_lines.append(' ')

            elif line.strip().startswith("File"):
                match = self.file_line_regex.search(line)
                if match:
                    section1 = match.group(1) + match.group(2)  # File path excluding last part
                    section2 = match.group(3)  # Last part of the path (filename)
                    section3 = match.group(4)  # ", line "
                    section4 = match.group(5)  # Line number
                    section5 = match.group(6)  # ", "
                    section6 = match.group(7)  # in
                    section7 = match.group(8)  # Function name

                    # Apply styles to each section
                    styled_section1 = self.apply_style('path', section1)
                    styled_section2 = self.apply_style('error_filename', section2)
                    styled_section3 = self.apply_style('line_info', section3)
                    styled_section4 = self.apply_style('error_line_number', section4)
                    styled_section5 = self.apply_style('path', section5)
                    styled_section6 = self.apply_style('path', section6)
                    styled_section7 = self.apply_style('function_name', section7)

                    # Combine the styled sections
                    styled_line = f"{styled_section1}{styled_section2}{styled_section3}{styled_section4}{styled_section5}{styled_section6}{styled_section7}"
                    styled_lines.append(f"{leading_whitespace}{styled_line}")
                else:
                    # If regex matching fails, style the whole line as fallback
                    styled_line = self.apply_style('regex_fail_line_fb', line)
                    styled_lines.append(f"{leading_whitespace}{styled_line}")

            #elif line.strip().startswith("raise") or line.strip().startswith("ValueError") or 'ValueError' in line:
            elif line.strip().startswith("raise"):
                styled_line = line.replace("raise", self.apply_style('vcyan', 'raise'))
                if "ColorNotFoundError" in styled_line:
                    styled_line = styled_line.replace("ColorNotFoundError", self.apply_style("lav", "ColorNotFoundError"))
                if "ValueError" in styled_line:
                    styled_line = styled_line.replace("ValueError", self.apply_style('lav', 'ValueError'))
                #styled_line = self.apply_style('red', line)
                styled_lines.append(' ')
                styled_lines.append(styled_line)
                styled_lines.append(' ')

            else:
                # Skip subclass name checks if the flag is False
                if check_subclass_names:
                    for name in subclass_names_with_colon:
                        if name in line:
                            start_index = line.find(name)
                            before_name = line[:start_index]
                            subclass_name = line[start_index:start_index + len(name)]
                            after_name = line[start_index + len(name):]

                            # Apply styles
                            styled_before_name = self.apply_style('subclass_name_before', before_name)
                            styled_subclass_name = self.apply_style('subclass_name', subclass_name)
                            styled_after_name = self.apply_style('subclass_name_after', after_name)

                            # Combine the styled parts
                            styled_line = f"{styled_before_name}{styled_subclass_name}{styled_after_name}"
                            styled_lines.append(' ')
                            styled_lines.append(f"{leading_whitespace}{styled_line}")
                            styled_lines.append(' ')
                            break

                    else:
                        styled_line = self.apply_style('default', line)
                        styled_lines.append(styled_line)
                        styled_lines.append(' ')

                else:
                    styled_line = self.apply_style('unhandled_exception_line', line)
                    styled_lines.append(styled_line)
                    styled_lines.append(' ')

        return styled_lines


    def handle_exception(self, logger=None, exc_type=None, exc_value=None, exc_info=None):
        self.print_error()

        if self.format_specific_exception:
            tb = ''.join(traceback.format_exception(None, self, self.__traceback__))
        else:
            tb = traceback.format_exc()

        tb_lines = tb.split('\n')

        # Stylize the traceback
        styled_tb_lines = self.stylize_traceback(tb_lines)

        # Log the exception if a logger is provided
        if logger:
            if issubclass(exc_type, self.__class__.critical_exceptions):
                for line in styled_tb_lines:
                    logger.critical(line, exc_info=exc_info)
            else:
                for line in styled_tb_lines:
                    logger.error(line, exc_info=exc_info)
        else:
            # Print the styled traceback to stderr
            for line in styled_tb_lines:
                print(line, file=sys.stderr)

        """

        # Print the stylized traceback
        for line in styled_tb_lines:
            print(line, file=sys.stderr)
        """

        print()





"""
# Custom exception hook to log unhandled exceptions using the logger
def set_custom_excepthook_with_logging(logger, pc=None, unhandled_exception_debug=False, log_exc_info=False, critical_exceptions=None):
    # Default critical exceptions if none are provided
    if critical_exceptions is None:
        critical_exceptions = (SystemExit, MemoryError, KeyboardInterrupt, OSError)

    def custom_excepthook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, PrintsCharmingException):
            # Handle PrintsCharming-specific exceptions
            exc_value.handle_exception()
        else:
            # Use the passed `pc` or fallback to the class-level instance
            pc_to_use = pc or PrintsCharmingException.pc_exception_instance
            general_exception = PrintsCharmingException(str(exc_value), pc_to_use)
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            styled_tb_lines = general_exception.stylize_traceback(tb_lines, check_subclass_names=False)

            if issubclass(exc_type, critical_exceptions):
                # Log the styled traceback as critical for system-exiting or fatal errors
                for line in styled_tb_lines:
                    logger.critical(line, exc_info=log_exc_info)
            else:
                # Log the styled traceback as error for non-critical exceptions
                for line in styled_tb_lines:
                    logger.error(line, exc_info=log_exc_info)


            if unhandled_exception_debug:
                # Call the default system excepthook
                sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = custom_excepthook
"""


