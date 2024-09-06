# logging_utils.py

import logging

# Use the library's name as the logger's name
shared_logger = logging.getLogger('prints_charming')
shared_logger.setLevel(logging.NOTSET)  # allow users to configure the level

# Ensure the logger only gets configured once
if not shared_logger.hasHandlers():
    fh = logging.FileHandler('spam.log')
    fh.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.NOTSET)  # Default to inherit the logger's level

    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    shared_logger.addHandler(console_handler)




