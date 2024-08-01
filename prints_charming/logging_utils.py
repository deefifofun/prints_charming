# logging_utils.py
import logging

# Use the library's name as the logger's name
logger = logging.getLogger('prints_charming')
logger.setLevel(logging.NOTSET)  # Allow users to configure the level

# Check if handlers are already set to avoid duplicates
if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.NOTSET)  # Default to inherit the logger's level
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


