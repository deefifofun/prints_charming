import logging.handlers
import sys
import inspect
import copy
from typing import Optional, Dict, Union
from .formatter import PrintsCharmingFormatter
from .log_handler import PrintsCharmingLogHandler
from ..prints_charming_defaults import DEFAULT_COLOR_MAP, DEFAULT_STYLES, DEFAULT_LOGGING_STYLES
from ..prints_charming import PrintsCharming
from ..exceptions import set_custom_excepthook_with_logging






def setup_logger(pc: Optional['PrintsCharming'] = None,
                 name: Optional[str] = None,
                 level: int = logging.DEBUG,
                 datefmt: str = '%Y-%m-%d %H:%M:%S',
                 handler_configs: Optional[Dict[str, Dict[str, Union[bool, str, int]]]] = None,
                 color_map: Optional[Dict[str, str]] = None,
                 styles: Optional[Dict[str, 'PStyle']] = None,
                 level_styles: Optional[Dict[int, str]] = None,
                 default_bg_color: Optional[str] = None,
                 internal_logging: bool = False,
                 internal_log_level: str = 'DEBUG',
                 enable_exception_logging: bool = True,
                 unhandled_exception_debug: bool = False,
                 log_exc_info: bool = False) -> logging.Logger:
    """
    Setup and return a logger with customizable handlers and formatters, including user-supplied custom handlers.
    Use PrintsCharmingLogHandler by default for custom styling and formatting.

    Args:
        pc (PrintsCharming): An instance of PrintsCharming for styling logs.
        name (str): Logger name (uses calling module name if None).
        level (int): Logging level for the logger. Defaults to logging.DEBUG.
        datefmt (str): Date format for the formatter.
        handler_configs (Optional[Dict[str, Dict[str, Union[bool, str, int]]]]): e.g. {
            'console': {'enabled': True, 'use_styles': True, 'formatter': CustomFormatter()},
            'file': {'path': '/path/to/log', 'use_styles': False, 'level': logging.INFO},
            'custom_handler': {'handler': MyCustomHandler(), 'formatter': CustomFormatter(), 'use_styles': False}
        }
        color_map (Optional[Dict[str, str]]): Custom color map.
        styles (Optional[Dict[str, PStyle]]): Custom styles.
        level_styles (Optional[Dict[int, str]]): Dictionary mapping logging levels to style names.
        default_bg_color (Optional[str]): Default background color for logs.
        internal_logging (bool): Toggle internal library logging.
        enable_exception_logging (bool): Enable logging of unhandled exceptions.
        unhandled_exception_debug (bool): Debug mode for unhandled exceptions.
        log_exc_info (bool): Enable logging of exception info.

    Returns:
        logging.Logger: Configured logger instance with specified handlers.
    """

    # If internal_logging is True, include it in the config
    config = {
        'internal_logging': internal_logging,
        'log_level': internal_log_level,
    }

    pc = pc or PrintsCharming(
        config=config,
        color_map=color_map or DEFAULT_COLOR_MAP.copy(),
        styles=copy.deepcopy(styles) or copy.deepcopy(DEFAULT_STYLES),
        default_bg_color=default_bg_color)

    if name is None:
        # Use inspect to get the module name of the caller
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        if caller_module is not None:
            name = caller_module.__name__
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Attach the `pc` instance to the logger for future access
    logger.pc = pc

    if enable_exception_logging:
        set_custom_excepthook_with_logging(logger, pc, unhandled_exception_debug, log_exc_info)

    # Helper function to create or use a supplied formatter
    def create_formatter(use_styles=None, custom_formatter=None):
        if custom_formatter:
            return custom_formatter  # If a custom formatter is provided, use it

        # Otherwise, create a PrintsCharmingFormatter with or without styles
        return PrintsCharmingFormatter(
            pc=pc,
            datefmt=datefmt,
            level_styles=level_styles or {
                logging.DEBUG: 'debug',
                logging.INFO: 'info',
                logging.WARNING: 'warning',
                logging.ERROR: 'error',
                logging.CRITICAL: 'critical'
            },
            internal_logging=internal_logging,
            use_styles=use_styles
        )

    # Handler factory function to create standard handlers
    def handler_factory(handler_name, config):
        if handler_name == 'console':
            return PrintsCharmingLogHandler(pc=pc, internal_logging=internal_logging)  # Custom handler for console
        elif handler_name == 'file':
            return logging.FileHandler(config['path'])  # For files, use standard FileHandler
        elif handler_name == 'rotating_file':
            return logging.handlers.RotatingFileHandler(
                config['path'],
                maxBytes=config.get('max_bytes', 10485760),
                backupCount=config.get('backup_count', 5)
            )
        elif handler_name == 'syslog':
            return logging.handlers.SysLogHandler(address=config.get('address', '/dev/log'))
        elif handler_name == 'smtp':
            mailhost = config.get('mailhost', 'localhost')
            fromaddr = config.get('fromaddr', 'error@example.com')
            toaddrs = config.get('toaddrs', ['admin@example.com'])
            subject = config.get('subject', 'Application Error')
            credentials = config.get('credentials', None)
            secure = config.get('secure', None)
            return logging.handlers.SMTPHandler(
                mailhost=mailhost,
                fromaddr=fromaddr,
                toaddrs=toaddrs,
                subject=subject,
                credentials=credentials,
                secure=secure
            )
        return None  # Return None if no handler matches

    # Helper function to add handler
    def add_handler(handler, level, formatter):
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Set default handler configurations if none are provided
    if not handler_configs:
        handler_configs = {
            'console': {'enabled': True, 'use_styles': True},
            'file': {'enabled': False},
            'rotating_file': {'enabled': False},
            'syslog': {'enabled': False},
            'smtp': {'enabled': False}
        }

    # Loop over handler configurations and create handlers
    for handler_name, config in handler_configs.items():
        if not config.get('enabled', False):
            continue  # Skip disabled handlers

        # Check if the user supplied a custom handler
        handler = config.get('handler') or handler_factory(handler_name, config)
        if not handler:
            continue  # Skip if no handler was created

        use_styles = config.get('use_styles', True)
        custom_formatter = config.get('formatter')  # User-supplied custom formatter (optional)

        # Determine the formatter to use (custom or default)
        log_formatter = create_formatter(use_styles=use_styles, custom_formatter=custom_formatter)
        handler_level = config.get('level', level)

        # Add the handler to the logger
        add_handler(handler, handler_level, log_formatter)

    return logger




__all__ = ['PrintsCharmingFormatter', 'PrintsCharmingLogHandler', 'setup_logger']
