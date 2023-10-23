#!/usr/bin/env python3

import logging
from ..prints_charming import ColorPrinter
from datetime import datetime
import time

# To run this script as a module inside the package. Navigate to the top-level directory and run
# python -m prints_charming.examples.logging-granular


class ColorPrinterLogHandler(logging.Handler):
    TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


    def __init__(self):
        super().__init__()
        self.cp = ColorPrinter()


    def emit(self, record):
        log_entry = self.format(record)
        self.handle_log_event(log_entry, log_level=record.levelname)


    def handle_log_event(self, text, log_level):
        timestamp = time.time()
        formatted_timestamp = datetime.fromtimestamp(timestamp).strftime(self.TIMESTAMP_FORMAT)

        # Define styles for different components
        timestamp_style = 'magenta'
        level_styles = {
            'INFO'    : 'green',
            'WARNING' : 'yellow',
            'ERROR'   : 'red',
            'DEBUG'   : 'blue',
            'CRITICAL': 'vred'
        }

        log_level_style = level_styles.get(log_level, 'default')

        # Get styled components
        styled_timestamp = self.cp.apply_style(timestamp_style, f"LOG[{log_level}]")
        styled_level = self.cp.apply_style(log_level_style, log_level)
        styled_text = self.cp.apply_style(log_level_style, text)

        # Create the final styled message
        timestamped_message = f"{styled_timestamp}: {formatted_timestamp} {styled_level} - {styled_text}"

        print(timestamped_message)


# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create an instance of your custom logging handler
handler = ColorPrinterLogHandler()

# Add the custom handler to the logger
logger.addHandler(handler)

# Test out different log levels
logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")