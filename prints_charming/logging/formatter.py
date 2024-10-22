# prints_charming.logging.formatter.py

import logging
import copy
import time
from socket import gethostname

from ..prints_charming_defaults import (
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES
)

from ..prints_charming import PrintsCharming




class PrintsCharmingFormatter(logging.Formatter):

    def __init__(self, pc, datefmt=None, style='%', timestamp_style_name=None, level_styles=None, use_styles=True, internal_logging=False):
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
        self._style_cache = {}



    @property
    def default_level_styles(self):
        """Default log level to style mapping."""
        return {
            logging.DEBUG: 'debug',
            logging.INFO: 'info',
            logging.WARNING: 'warning',
            logging.ERROR: 'error',
            logging.CRITICAL: 'critical'
        }


    def formatTime(self, record, datefmt=None, ms_format="{:04.0f}"):
        t = time.localtime(record.created)
        if datefmt:
            s = time.strftime(datefmt, t)
            if '%f' in datefmt:
                # Replace the microsecond directive (%f) with milliseconds
                s = s.replace('%f', ms_format.format(record.msecs))
        else:
            s = f"{t.tm_year}-{t.tm_mon:02}-{t.tm_mday:02} {t.tm_hour:02}:{t.tm_min:02}:{t.tm_sec:02},{ms_format.format(record.msecs)}"
        return s


    def get_log_level_style(self, record):
        """Returns the style for the current log level."""
        return self.level_styles.get(record.levelno, 'default')

    def format_log_level_label(self, record):
        """Constructs the log level label."""
        log_level_label = f"LOG[{record.levelname}]" + ' ' * (8 - len(record.levelname))
        return self.apply_style(self.get_log_level_style(record), log_level_label)

    def style_record_attributes(self, record):
        """Styles the record attributes (hostname, filename, etc.)."""
        record.hostname = self.apply_style('hostname', self.hostname)
        record.filename = self.apply_style('filename', record.filename)
        record.name = self.apply_style('record_name', record.name)
        record.funcName = self.apply_style('method_name', record.funcName)
        record.lineno = self.apply_style('line_number', record.lineno)

    def format_message(self, record, log_level_style_code, log_level_label, timestamp):
        """Constructs the final log message."""
        styled_timestamp = self.apply_style(self.get_timestamp_style(record), timestamp) + f"{int(record.msecs):04.0f}"
        styled_log_level_prefix = log_level_label
        return f"{styled_timestamp} {styled_log_level_prefix} {record.msg}"

    def get_timestamp_style(self, record):
        """Gets the style for the timestamp."""
        return self.timestamp_style or self.get_log_level_style(record)

    def format(self, record: logging.LogRecord) -> str:
        """Main format method that builds the log message."""
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

    def format_record_message(self, record, log_level_style_code):
        """Formats the `record.msg`."""
        if record.args:
            args_style_code = self.get_style_code('args')
            record.msg = record.msg.format(*[
                f"{args_style_code}{arg}{self.reset}{log_level_style_code}" for arg in record.args
            ])
            record.args = ()  # Clear args to prevent further formatting
        record.msg = f"{log_level_style_code}{record.msg}{self.reset}"
        record.msg = f"{record.hostname} - {record.filename} {record.name} {record.funcName}:{record.lineno} - {record.msg}"

    def format_plain_message(self, record, timestamp, log_level_label):
        """Formats a plain (non-styled) log message."""
        if record.args:
            record.msg = record.msg.format(record.args)
            record.args = ()  # Prevent further formatting attempts
        return f"{timestamp} {log_level_label} {self.hostname} - {record.filename} {record.name} {record.funcName}:{record.lineno} - {record.msg}"


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


