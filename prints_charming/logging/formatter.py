# prints_charming.logging.formatter.py

import logging
import copy
import time
from socket import gethostname
from typing import Any, Callable, Dict, Optional, Union

from ..prints_charming_defaults import (
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES
)

from ..prints_charming import PrintsCharming




class PrintsCharmingFormatter(logging.Formatter):
    """
    Custom logging formatter using PrintsCharming for styling log messages.

    Attributes:
        pc (PrintsCharming): PrintsCharming instance for styling.
        apply_style (Callable): Method to apply styles.
        get_style_code (Callable): Method to get style codes.
        reset (str): ANSI reset code.
        hostname (str): Hostname of the machine.
        timestamp_style (Optional[str]): Style name for the timestamp.
        level_styles (Dict[int, str]): Mapping from log levels to style names.
        use_styles (bool): Whether to apply styles.
        _style_cache (Dict[str, str]): Cache for style codes.
    """

    def __init__(
        self,
        pc: Optional[PrintsCharming],
        datefmt: Optional[str] = None,
        style: str = '%',
        timestamp_style_name: Optional[str] = None,
        level_styles: Optional[Dict[int, str]] = None,
        use_styles: bool = True,
        args_style_name: str = 'args',
        internal_logging: bool = False
    ) -> None:
        """
        Initialize the PrintsCharmingFormatter.

        Args:
            pc (Optional[PrintsCharming]): PrintsCharming instance for styling.
            datefmt (Optional[str]): Date format string.
            style (str): Style for formatting.
            timestamp_style_name (Optional[str]): Style name for the timestamp.
            level_styles (Optional[Dict[int, str]]): Mapping from log levels to style names.
            use_styles (bool): Whether to apply styles.
            internal_logging (bool): Whether internal logging is enabled.
        """
        super().__init__(datefmt=datefmt, style=style)
        self.pc = pc or PrintsCharming(styles=copy.deepcopy(DEFAULT_LOGGING_STYLES))

        if internal_logging:
            self.apply_style = self.pc._apply_style_internal
        else:
            self.apply_style = self.pc.apply_style

        self.get_style_code = self.pc.get_style_code
        self.reset = self.pc.reset
        self.hostname = gethostname()
        self.timestamp_style = timestamp_style_name
        self.level_styles = level_styles or self.default_level_styles
        self.use_styles = use_styles
        self.args_style_name = args_style_name
        self._style_cache: Dict[str, str] = {}



    @property
    def default_level_styles(self) -> Dict[int, str]:
        """
        Default log level to style mapping.

        Returns:
            Dict[int, str]: Mapping from log levels to style names.
        """
        return {
            logging.DEBUG: 'debug',
            logging.INFO: 'info',
            logging.WARNING: 'warning',
            logging.ERROR: 'error',
            logging.CRITICAL: 'critical'
        }


    def formatTime(
        self,
        record: logging.LogRecord,
        datefmt: Optional[str] = None,
        ms_format: str = "{:04.0f}"
    ) -> str:
        """
        Format the time of the log record.

        Args:
            record (logging.LogRecord): The log record.
            datefmt (Optional[str]): Date format string.
            ms_format (str): Milliseconds format.

        Returns:
            str: Formatted timestamp.
        """
        t = time.localtime(record.created)
        if datefmt:
            s = time.strftime(datefmt, t)
            if '%f' in datefmt:
                # Replace the microsecond directive (%f) with milliseconds
                s = s.replace('%f', ms_format.format(record.msecs))
        else:
            s = f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02} {t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02},{ms_format.format(record.msecs)}"
        return s


    def get_log_level_style(self, record: logging.LogRecord) -> str:
        """
        Returns the style for the current log level.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            str: Style name.
        """
        return self.level_styles.get(record.levelno, 'default')


    def format_log_level_label(self, record: logging.LogRecord) -> str:
        """Constructs the log level label.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            str: Styled log level label.
        """
        log_level_label = f"LOG[{record.levelname}]" + ' ' * (8 - len(record.levelname))
        return self.apply_style(self.get_log_level_style(record), log_level_label)


    def style_record_attributes(self, record: logging.LogRecord) -> None:
        """
        Styles the record attributes (hostname, filename, etc.).

        Args:
            record (logging.LogRecord): The log record.
        """
        record.hostname = self.apply_style('hostname', self.hostname)
        record.filename = self.apply_style('filename', record.filename)
        record.name = self.apply_style('record_name', record.name)
        record.funcName = self.apply_style('method_name', record.funcName)
        record.lineno = self.apply_style('line_number', record.lineno)


    def format_message(
        self,
        record: logging.LogRecord,
        log_level_style_code: str,
        log_level_label: str,
        timestamp: str
    ) -> str:
        """
        Constructs the final log message.

        Args:
            record (logging.LogRecord): The log record.
            log_level_style_code (str): Style code for the log level.
            log_level_label (str): Styled log level label.
            timestamp (str): Formatted timestamp.

        Returns:
            str: Final formatted log message.
        """
        styled_timestamp = self.apply_style(self.get_timestamp_style(record), timestamp) + f"{int(record.msecs):04.0f}"
        styled_log_level_prefix = log_level_label
        return f"{styled_timestamp} {styled_log_level_prefix} {record.msg}"


    def get_timestamp_style(self, record: logging.LogRecord) -> str:
        """
        Gets the style for the timestamp.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            str: Style name for the timestamp.
        """
        return self.timestamp_style or self.get_log_level_style(record)


    def format(self, record: logging.LogRecord) -> str:
        """
        Main format method that builds the log message.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            str: Formatted log message.
        """
        timestamp = f"{self.formatTime(record, self.datefmt)}"
        log_level_style_code = self.get_style_code(self.get_log_level_style(record))
        log_level_label = self.format_log_level_label(record)

        if self.use_styles:
            self.style_record_attributes(record)
            self.format_record_message(record, log_level_style_code)
            log_message = self.format_message(record, log_level_style_code, log_level_label, timestamp)
        else:
            log_message = self.format_plain_message(record, timestamp, log_level_label)

        return log_message


    def format_record_message(
        self,
        record: logging.LogRecord,
        log_level_style_code: str
    ) -> None:
        """
        Formats the `record.msg`.

        Args:
            record (logging.LogRecord): The log record.
            log_level_style_code (str): Style code for the log level.
        """
        if record.args:
            args_style_code = self.get_style_code(self.args_style_name)
            record.msg = record.msg.format(*[
                f"{args_style_code}{arg}{self.reset}{log_level_style_code}" for arg in record.args
            ])
            record.args = ()  # Clear args to prevent further formatting
        record.msg = f"{log_level_style_code}{record.msg}{self.reset}"
        record.msg = (
            f"{record.hostname} - {record.filename} {record.name} "
            f"{record.funcName}:{record.lineno} - {record.msg}"
        )


    def format_plain_message(
        self,
        record: logging.LogRecord,
        timestamp: str,
        log_level_label: str
    ) -> str:
        """
        Formats a plain (non-styled) log message.

        Args:
            record (logging.LogRecord): The log record.
            timestamp (str): Formatted timestamp.
            log_level_label (str): Log level label.

        Returns:
            str: Plain formatted log message.
        """
        if record.args:
            record.msg = record.msg.format(record.args)
            record.args = ()  # Prevent further formatting attempts
        #return f"{timestamp} {log_level_label} {self.hostname} - {record.filename} {record.name} {record.funcName}:{record.lineno} - {record.msg}"
        record.msg = (
            f"{self.hostname} - {record.filename} {record.name} "
            f"{record.funcName}:{record.lineno} - {record.msg}"
        )
        return f"{timestamp} {log_level_label} {record.msg}"


    def format_orig(self, record: logging.LogRecord) -> str:

        if self.use_styles:
            log_level_style = self.level_styles.get(record.levelno, 'default')
            log_level_style_code = self.get_style_code(log_level_style)
            args_style_code = self.get_style_code('args')

            timestamp = f"{self.formatTime(record, self.datefmt)}"
            log_level_label = f"LOG[{record.levelname}]" + ' ' * (8 - len(record.levelname))

            if isinstance(record.msecs, (int, float)):
                record.msecs = "{:04.0f}".format(record.msecs)

            record.hostname = self.apply_style('hostname', self.hostname)
            record.filename = self.apply_style('filename', record.filename)
            record.name = self.apply_style('record_name', record.name)
            record.funcName = self.apply_style('method_name', record.funcName)
            record.lineno = self.apply_style('line_number', record.lineno)

            if record.args:

                # Prepare the formatted message by applying the style to each argument
                formatted_args = [f"{args_style_code}{arg}{self.reset}{log_level_style_code}" for arg in record.args]

                # Apply the formatting to the message
                record.msg = record.msg.format(*formatted_args)
                record.args = ()  # Clear args to prevent further formatting attempts

            timestamp_style = log_level_style if not self.timestamp_style else self.timestamp_style

            styled_timestamp = self.apply_style(timestamp_style, timestamp) + record.msecs
            styled_log_level_prefix = self.apply_style(log_level_style, log_level_label)
            styled_level = self.apply_style(log_level_style, record.levelname)


            # Apply log level style to the entire message
            record.msg = f"{log_level_style_code}{record.msg}{self.reset}"

            record.msg = f"{record.hostname} - {record.filename} {record.name} {record.funcName}:{record.lineno} - {record.msg}"

            log_message = f"{styled_timestamp} {styled_log_level_prefix} {record.msg}"
        else:
            # No styling: plain text formatting
            timestamp = f"{self.formatTime(record, self.datefmt)}"
            log_level_label = f"LOG[{record.levelname}]" + ' ' * (8 - len(record.levelname))

            if isinstance(record.msecs, (int, float)):
                record.msecs = "{:04.0f}".format(record.msecs)

            if record.args:
                record.msg = record.msg.format(record.args)
                record.args = ()  # Clear args to prevent further formatting attempts

            record.msg = f"{self.hostname} - {record.filename} {record.name} {record.funcName}:{record.lineno} - {record.msg}"

            log_message = f"{timestamp} {log_level_label} {record.msg}"

        return log_message


