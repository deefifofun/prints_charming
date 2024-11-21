# prints_charming.exceptions.base_exceptions.py

import re
import traceback
import sys
import copy
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union
from ..prints_charming_defaults import DEFAULT_STYLES




def get_all_subclass_names(cls: Type[Any],
                           trailing_char: Optional[str] = None
                           ) -> Set[str]:
    """
    Recursively get the names of all subclasses of a given class.

    Args:
        cls (Type[Any]): The base class to find subclasses of.
        trailing_char (Optional[str]): A character to append to each subclass name.

    Returns:
        Set[str]: A set of subclass names.
    """
    subclasses = set(cls.__subclasses__())
    result = {subclass.__name__ + (trailing_char or '') for subclass in subclasses}
    for subclass in subclasses.copy():
        result.update(get_all_subclass_names(subclass, trailing_char))
    return result



class PrintsCharmingException(Exception):
    """Base class for all exceptions using PrintsCharming.

    Attributes:
        message (str): The exception message.
        pc (PrintsCharming): Instance of PrintsCharming for styling.
        reset (str): ANSI reset code.
        apply_style (Callable): Method to apply styles.
        tb_style_name (str): Name of the traceback style to use.
        format_specific_exception (bool): Whether to format specific exceptions.
        file_line_regex (re.Pattern): Compiled regex pattern for file lines in tracebacks.
        check_subclass_names (bool): Whether to check subclass names when styling.
    """

    # Class-level instance as the fallback
    shared_pc_exception_instance: Optional['PrintsCharming'] = None

    # Critical Exceptions
    critical_exceptions: Tuple[Type[BaseException], ...] = (
        SystemExit, MemoryError, KeyboardInterrupt, OSError
    )



    def __init__(
        self,
        message: str,
        pc: 'PrintsCharming',
        use_shared_pc: bool = False,
        tb_style_name: str = 'default',
        format_specific_exception: bool = False,
        file_line_regex: Optional[str] = r'(File ")(.*?)(/[^/]+)(", line )(\d+)(, )(in )(.*)',
        check_subclass_names: bool = True
    ) -> None:

        """
        Initialize the exception.

        Args:
            message (str): The exception message.
            pc (PrintsCharming): Instance of PrintsCharming for styling.
            use_shared_pc (bool): Use shared PrintsCharming instance across subclasses.
            tb_style_name (str): Name of the traceback style to use.
            format_specific_exception (bool): Format specific exceptions.
            file_line_regex (Optional[str]): Regex pattern for file lines in tracebacks.
            check_subclass_names (bool): Check subclass names when styling tracebacks.
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

        self.reset = self.pc.__class__.RESET
        self.apply_style = self.pc.apply_style
        self.tb_style_name = tb_style_name
        self.format_specific_exception = format_specific_exception
        self.file_line_regex = re.compile(file_line_regex)
        self.check_subclass_names = check_subclass_names

    def __str__(self) -> str:
        """Return the exception message as a string."""
        return self.message

    def format_traceback(self, tb: str) -> str:
        """
        Apply style to the traceback.

        Args:
            tb (str): The traceback string.

        Returns:
            str: The styled traceback.
        """
        return self.apply_style(self.tb_style_name, tb)

    def print_error(self) -> None:
        """Print the error message."""
        print(f'{self.message}\n')

    def stylize_traceback(self,
                          tb_lines: List[str],
                          check_subclass_names: bool = True
                          ) -> List[str]:
        """
        Apply custom styles to the lines of a traceback.

        Args:
            tb_lines (List[str]): List of traceback lines.
            check_subclass_names (bool): Whether to check subclass names.

        Returns:
            List[str]: List of styled traceback lines.
        """

        styled_lines: List[str] = []

        # Only fetch subclass names if the flag is set to True
        subclass_names_with_colon: List[str] = []
        if check_subclass_names:
            subclass_names_with_colon = list(
                get_all_subclass_names(
                    PrintsCharmingException,
                    trailing_char=':'
                )
            )

        for line in tb_lines:
            leading_whitespace_match = re.match(r"^\s*", line)
            leading_whitespace = leading_whitespace_match.group() if leading_whitespace_match else ''

            if line.startswith("Traceback"):
                styled_line = self.apply_style('header', line)
                styled_lines.extend([styled_line, ' '])

            elif line.strip().startswith("File"):
                match = self.file_line_regex.search(line)
                if match:
                    path_style_code = self.pc.get_style_code('path')
                    reset = self.reset

                    section1 = match.group(1) + match.group(2)  # File path excluding last part
                    section2 = match.group(3)  # Last part of the path (filename)
                    section3 = match.group(4)  # ", line "
                    section4 = match.group(5)  # Line number
                    section5 = match.group(6)  # ", "
                    section6 = match.group(7)  # in
                    section7 = match.group(8)  # Function name

                    # Apply styles to each section
                    styled_sections = [
                        path_style_code + section1 + reset,
                        self.apply_style('error_filename', section2),
                        self.apply_style('line_info', section3),
                        self.apply_style('error_line_number', section4),
                        path_style_code + section5 + reset,
                        path_style_code + section6 + reset,
                        self.apply_style('function_name', section7)
                    ]

                    # Combine the styled sections
                    styled_line = ''.join(styled_sections)
                    styled_lines.append(f"{leading_whitespace}{styled_line}")

                else:
                    # If regex matching fails, style the whole line as fallback
                    styled_line = self.apply_style('regex_fail_line_fb', line)
                    styled_lines.append(f"{leading_whitespace}{styled_line}")

            elif line.strip().startswith("raise"):
                styled_line = line.replace(
                    "raise",
                    self.apply_style('vcyan', 'raise'))
                if "ColorNotFoundError" in styled_line:
                    styled_line = styled_line.replace(
                        "ColorNotFoundError",
                        self.apply_style("lav", "ColorNotFoundError"))
                if "ValueError" in styled_line:
                    styled_line = styled_line.replace(
                        "ValueError",
                        self.apply_style('lav', 'ValueError'))
                styled_lines.extend([' ', styled_line, ' '])

            else:
                # Skip subclass name checks if the flag is False
                if check_subclass_names:
                    for name in subclass_names_with_colon:
                        if name in line:
                            start_index = line.find(name)
                            before_name = line[:start_index]
                            subclass_name = line[start_index:start_index + len(name)]
                            after_name = line[start_index + len(name):]

                            styled_parts = [
                                self.apply_style(
                                    'subclass_name_before',
                                    before_name
                                ),
                                self.apply_style(
                                    'subclass_name',
                                    subclass_name
                                ),
                                self.apply_style(
                                    'subclass_name_after',
                                    after_name
                                )
                            ]

                            # Combine the styled parts
                            styled_line = ''.join(styled_parts)
                            styled_lines.extend(
                                [' ', f"{leading_whitespace}{styled_line}", ' ']
                            )
                            break

                    else:
                        styled_line = self.apply_style('default', line)
                        styled_lines.extend([styled_line, ' '])

                else:
                    styled_line = self.apply_style('unhandled_exception_line', line)
                    styled_lines.extend([styled_line, ' '])

        return styled_lines


    def handle_exception(self,
                         logger: Optional[Any] = None,
                         exc_type: Optional[Type[BaseException]] = None,
                         exc_value: Optional[BaseException] = None,
                         exc_info: Optional[Any] = None,
                         print_error: bool = False,
                         full_traceback: bool = True,
                         ) -> None:
        """
        Handle the exception by printing or logging the styled traceback.

        Args:
            logger (Optional[Any]): Logger to log the exception.
            exc_type (Optional[Type[BaseException]]): Exception type.
            exc_value (Optional[BaseException]): Exception value.
            exc_info (Optional[Any]): Exception info.
            print_error (Optional[bool]): Print unstyled error message first.
            full_traceback (bool): Current active exception if True else specific.
        """
        if print_error:
            self.print_error()


        if self.format_specific_exception:
            if full_traceback:
                # Current active exception traceback (more detailed)
                tb = traceback.format_exc()
            else:
                # Specific styled traceback from this instance
                tb = ''.join(traceback.format_exception(None, self, self.__traceback__))
        else:
            tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_info))
            #tb = traceback.format_exc()

        tb_lines = tb.split('\n')

        # Stylize the traceback
        styled_tb_lines = self.stylize_traceback(tb_lines, self.check_subclass_names)

        # Join the styled traceback lines into a single message
        complete_traceback = '\n'.join(styled_tb_lines)

        # Log the entire traceback as a single message
        if logger:
            if exc_type and issubclass(exc_type, self.__class__.critical_exceptions):
                logger.critical(f"\n{complete_traceback}", exc_info=exc_info)
            else:
                logger.error(f"\n{complete_traceback}", exc_info=exc_info)
        else:
            # Print the styled traceback to stderr if no logger is provided
            print(complete_traceback, file=sys.stderr)

            print()

