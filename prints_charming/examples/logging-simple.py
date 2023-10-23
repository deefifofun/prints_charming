#!/usr/bin/env python3

import logging
from ..prints_charming import ColorPrinter
from datetime import datetime
import time

# To run this script as a module inside the package. Navigate to the top-level directory and run
# python -m prints_charming.examples.logging-simple

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

        color = 'blue'  # default color
        if 'ERROR' in log_level.upper():
            color = 'red'
        elif 'WARNING' in log_level.upper():
            color = 'yellow'
        elif 'INFO' in log_level.upper():
            color = 'green'

        timestamped_message = f"LOG[{log_level}]: {formatted_timestamp} {text}"
        self.cp.print(timestamped_message, color=color)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add custom handler to the logger
handler = ColorPrinterLogHandler()
logger.addHandler(handler)

# Test logging
logger.info('This is an info message.')
logger.warning('This is a warning message.')
logger.error('This is an error message.')