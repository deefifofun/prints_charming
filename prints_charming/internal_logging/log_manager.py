# log_manager.py

import logging
import inspect
from datetime import datetime

class LoggingManager:
    def __init__(self, prints_charming_instance, log_level="DEBUG"):
        """
        Initializes LoggingManager with a reference to PrintsCharming instance.
        """
        self.pc = prints_charming_instance
        self.logger = logging.getLogger("prints_charming")
        self.log_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self.logger.setLevel(self.log_level)

    def format_message(self, level, message):
        """
        Uses the PrintsCharming instance to format log messages with styles.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        styled_timestamp = self.pc._apply_style_internal("timestamp", timestamp)
        styled_level = self.pc._apply_style_internal(level.lower(), level.upper())
        styled_message = self.pc._apply_style_internal(level.lower(), message)

        return f"{styled_level} {styled_timestamp} - {styled_message}"

    def log(self, level: str, message: str, *args, **kwargs) -> None:
        """
        Log the message using the appropriate level and formatting.
        """
        if args or kwargs:
            message = message.format(*args, **kwargs)
        formatted_message = self.format_message(logging.getLevelName(level), message)
        self.logger.log(level, formatted_message)

    def debug(self, message, *args, **kwargs):
        # Get the current stack frame
        current_frame = inspect.currentframe()
        # Get the caller frame
        caller_frame = current_frame.f_back
        # Extract the relevant information
        class_name = self.pc._apply_style_internal('class_name', caller_frame.f_globals['__name__'])
        method_name = self.pc._apply_style_internal('method_name', caller_frame.f_code.co_name)
        line_number = self.pc._apply_style_internal('line_number', caller_frame.f_lineno)

        # Include the extracted information in the log message
        message = f"{class_name}.{method_name}:{line_number} - {message}"

        self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.log(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self.log(logging.CRITICAL, message, *args, **kwargs)


