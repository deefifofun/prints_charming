import re
import traceback
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union





def get_all_subclass_names(cls, trailing_char=None):
    subclasses = set(cls.__subclasses__())
    result = {subclass.__name__ + (trailing_char or '') for subclass in subclasses}
    for subclass in subclasses.copy():
        result.update(get_all_subclass_names(subclass, trailing_char))
    return result



class PrintsCharmingError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self,
                 message: str,
                 pc: 'PrintsCharming',
                 apply_style: Callable[[str, str], str],
                 tb_style_name: str = 'default',
                 format_specific_exception: bool = False
                 ) -> None:

        super().__init__(message)
        self.message = message
        self.pc = pc
        self.apply_style = apply_style
        self.tb_style_name = tb_style_name
        self.format_specific_exception = format_specific_exception

    def __str__(self):
        return self.message

    def format_traceback(self, tb):
        return self.apply_style(self.tb_style_name, tb)

    def print_error(self):
        print(self.message)
        print()

    def stylize_traceback(self, tb_lines, check_subclass_names=True):

        styled_lines = []
        file_line_regex = re.compile(r'(File ")(.*?)(/[^/]+)(", line )(\d+)(, )(in )(.*)')

        # Only fetch subclass names if the flag is set to True
        subclass_names_with_colon = []
        if check_subclass_names:
            subclass_names_with_colon = list(get_all_subclass_names(PrintsCharmingError, trailing_char=':'))

        for line in tb_lines:
            leading_whitespace = re.match(r"^\s*", line).group()

            if line.startswith("Traceback"):
                styled_line = self.apply_style('header', line)
                styled_lines.append(' ')
                styled_lines.append(styled_line)
                styled_lines.append(' ')

            elif line.strip().startswith("File"):
                match = file_line_regex.search(line)
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
                    styled_line = self.apply_style('blue', line)
                    styled_lines.append(f"{leading_whitespace}{styled_line}")

            elif line.strip().startswith("raise") or line.strip().startswith("ValueError"):
                styled_line = self.apply_style('red', line)
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
                            styled_before_name = self.apply_style('gray', before_name)
                            styled_subclass_name = self.apply_style('vyellow', subclass_name)
                            styled_after_name = self.apply_style('default', after_name)

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
                    styled_line = self.apply_style('default', line)
                    styled_lines.append(styled_line)
                    styled_lines.append(' ')

        return styled_lines


    def handle_exception(self):
        self.print_error()

        if self.format_specific_exception:
            tb = ''.join(traceback.format_exception(None, self, self.__traceback__))
        else:
            tb = traceback.format_exc()

        tb_lines = tb.split('\n')

        # Stylize the traceback
        styled_tb_lines = self.stylize_traceback(tb_lines)

        # Print the stylized traceback
        for line in styled_tb_lines:
            print(line, file=sys.stderr)

        print()


class ColorNotFoundError(PrintsCharmingError):
    """Exception raised when a color is not found in the color map."""
    pass


class InvalidLengthError(PrintsCharmingError):
    """Exception raised when an invalid length is provided."""
    pass


class UnsupportedEffectError(PrintsCharmingError):
    """Exception raised when an unsupported effect is requested."""
    pass


# Custom exception hook to log unhandled exceptions using the logger
def set_custom_excepthook_with_logging(logger, pc, unhandled_exception_debug=False, log_exc_info=False):
    def custom_excepthook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, PrintsCharmingError):
            # Handle PrintsCharming-specific exceptions
            exc_value.handle_exception()
        else:
            general_exception = PrintsCharmingError(str(exc_value), pc, pc.apply_style)
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            styled_tb_lines = general_exception.stylize_traceback(tb_lines, check_subclass_names=False)

            # Log the styled traceback
            for line in styled_tb_lines:
                logger.error(line, exc_info=log_exc_info)

            if unhandled_exception_debug:
                # Call the default system excepthook
                sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = custom_excepthook

