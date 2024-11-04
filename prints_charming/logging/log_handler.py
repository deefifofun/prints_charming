# prints_charming.logging.log_handler.py

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
            print(formatted_message)
        except Exception as e:
            self.handleError(record)


