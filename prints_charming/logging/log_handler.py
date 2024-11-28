# prints_charming.logging.log_handler.py

import sys
import logging
from typing import Optional
from .formatter import PrintsCharmingFormatter


class PrintsCharmingLogHandler(logging.Handler):
    """
    Custom logging handler that uses PrintsCharmingFormatter to format log records.

    Attributes:
        pc (PrintsCharming): PrintsCharming instance for styling.
    """

    def __init__(
        self,
        pc: 'PrintsCharming',
        formatter: Optional[logging.Formatter] = None,
        internal_logging: bool = False
    ) -> None:
        """
       Initialize the PrintsCharmingLogHandler.

       Args:
           pc (PrintsCharming): PrintsCharming instance for styling.
           formatter (Optional[logging.Formatter]): Formatter to use.
           internal_logging (bool): Whether internal logging is enabled.
       """
        super().__init__()
        self.pc = pc
        self.container_width = self.pc.terminal_width
        self.word_wrap = False,
        self.tab_width = 8
        self.remove_ansi_codes = self.pc.__class__.remove_ansi_codes
        self.fill_to_end = True if self.pc.default_bg_color else False
        self.fill_with = ' '
        self.setFormatter(
            formatter or PrintsCharmingFormatter(
                pc=pc, internal_logging=internal_logging
            )
        )

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record.

        Args:
            record (logging.LogRecord): The log record to emit.
        """
        try:
            formatted_message = self.format(record)

            if self.fill_to_end or self.word_wrap:
                if self.word_wrap:
                    # Use the new wrap_styled_text function
                    wrapped_styled_lines = self.pc.wrap_styled_text(formatted_message, self.container_width, self.tab_width)
                else:
                    wrapped_styled_lines = formatted_message.splitlines(keepends=True)

                final_lines = []
                for line in wrapped_styled_lines:

                    # Calculate the number of trailing newlines
                    trailing_newlines = len(line) - len(line.rstrip('\n'))

                    # Check if the line is empty (contains only a newline character)
                    stripped_line = line.rstrip('\n')
                    has_newline = line.endswith('\n')

                    if self.fill_to_end:
                        # Calculate the visible length of the line
                        visible_line = self.remove_ansi_codes(stripped_line)
                        current_length = self.pc.get_visible_length(visible_line.expandtabs(self.tab_width), tab_width=self.tab_width)
                        chars_needed = max(0, self.container_width - current_length)

                        # If the line ends with the ANSI reset code, remove it temporarily
                        has_reset = stripped_line.endswith(self.pc.reset)
                        if has_reset:
                            stripped_line = stripped_line[:-len(self.pc.reset)]

                        # Add padding spaces and then the reset code if it was present
                        padded_line = stripped_line + self.fill_with * chars_needed
                        if has_reset:
                            padded_line += self.pc.reset

                        # Re-append the newline character if it was present
                        if trailing_newlines > 0:
                            padded_line += '\n' * trailing_newlines

                        final_lines.append(padded_line)
                    else:
                        final_lines.append(line)

                # Combine the lines into the final styled output
                if any(line.endswith('\n') for line in final_lines):
                    # Lines already contain newline characters; avoid adding extra newlines
                    final_all_styled_text = ''.join(final_lines)
                else:
                    # Lines do not contain newlines; join them with '\n'
                    final_all_styled_text = '\n'.join(final_lines)

                """
                # Combine the lines into the final styled output
                final_all_styled_text = '\n'.join(final_lines)
                """

            else:
                final_all_styled_text = formatted_message

            sys.stdout.write(final_all_styled_text + '\n')

        except Exception as e:
            self.handleError(record)


