import logging.handlers
import inspect
from .formatter import PrintsCharmingFormatter
from .log_handler import PrintsCharmingLogHandler
from ..prints_charming_defaults import DEFAULT_COLOR_MAP, DEFAULT_LOGGING_STYLES
from ..prints_charming import PrintsCharming



def setup_logger(pc=None, name=None, level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S.',
                 handler_configs=None, color_map=None, styles=None, level_styles=None,
                 internal_logging=False):
    """
    Setup and return a logger with customizable handlers and formatters, including user-supplied custom handlers.
    Use PrintsCharmingLogHandler by default for custom styling and formatting.

    Args:
        pc (PrintsCharming): An instance of PrintsCharming for styling logs.
        name (str): Logger name (uses calling module name if None).
        level (int): Logging level for the logger. Defaults to logging.DEBUG.
        datefmt (str): Date format for the formatter.
        handler_configs (dict): Dictionary containing handler configurations, e.g. {
            'console': {'enabled': True, 'use_styles': True, 'formatter': CustomFormatter()},
            'file': {'path': '/path/to/log', 'use_styles': False, 'level': logging.INFO},
            'custom_handler': {'handler': MyCustomHandler(), 'formatter': CustomFormatter(), 'use_styles': False}
        }

        level_styles (dict): Dictionary mapping logging levels to style names.
        internal_logging (bool): Toggle internal logging styles.

    Returns:
        logging.Logger: Configured logger instance with specified handlers.
    """

    pc = pc or PrintsCharming(color_map=color_map or DEFAULT_COLOR_MAP.copy(), styles=styles or DEFAULT_LOGGING_STYLES.copy())

    if name is None:
        # Use inspect to get the module name of the caller
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        if caller_module is not None:
            name = caller_module.__name__
    logger = logging.getLogger(name)
    logger.setLevel(level)

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
