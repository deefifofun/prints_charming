# prints_charming.logging.__init__.py

import logging.handlers
import sys
import inspect
import uuid
import copy
from typing import Any, Optional, Dict, Union, List, Tuple, Type


from .formatter import PrintsCharmingFormatter
from .log_handler import PrintsCharmingLogHandler
from ..prints_charming_defaults import (
    DEFAULT_COLOR_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES
)
from ..prints_charming import PrintsCharming, PStyle
from ..exceptions.utils import set_excepthook



def set_custom_excepthook_with_logging(
        logger: logging.Logger,
        pc: PrintsCharming,
        log_exc_info: bool = False,
        critical_exceptions: Optional[Tuple[Type[BaseException], ...]] = None,
        unhandled_exception_debug: bool = False,
        update_exception_logging: bool = False,
) -> None:
    """
    Set custom exception hook with logging capabilities.

    Args:
        logger (logging.Logger): Logger to use for logging exceptions.
        pc (PrintsCharming): An instance of PrintsCharming for styling logs.
        log_exc_info (bool): Whether to log exception info.
        critical_exceptions (Optional[Tuple[Type[BaseException], ...]]): A tuple
            of exception types to log as critical.
        unhandled_exception_debug (bool): If True, calls sys.__excepthook__ for
            unhandled exceptions.
        update_exception_logging (bool): If True, updates exception logging to
            new values.
    """
    set_excepthook(pc,
                   logger=logger,
                   log_exc_info=log_exc_info,
                   critical_exceptions=critical_exceptions,
                   update_exception_logging=update_exception_logging)

    # Handle unhandled_exception_debug (calling sys.__excepthook__ if necessary)
    if unhandled_exception_debug:
        def debug_excepthook(
                exc_type: Type[BaseException],
                exc_value: BaseException,
                exc_traceback: Any
        ) -> None:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        sys.excepthook = debug_excepthook


def get_log_level(level: Union[int, str]) -> int:
    """
    Converts a log level given as a string or integer to an integer.

    Args:
        level (Union[int, str]): Log level (e.g., "debug", "INFO", logging.DEBUG).

    Returns:
        int: Corresponding logging level as an integer.

    Raises:
        ValueError: If the level is invalid.
    """
    if isinstance(level, int):
        return level
    elif isinstance(level, str):
        level = level.upper()
        if level in logging._nameToLevel:
            return logging._nameToLevel[level]
        else:
            raise ValueError(f"Invalid log level: {level}")
    else:
        raise TypeError("Log level must be an int or a str")



def setup_logger(
    pc: Optional[PrintsCharming] = None,
    name: Optional[str] = None,
    level: Union[int, str] = logging.DEBUG,
    datefmt: str = '%Y-%m-%d %H:%M:%S',
    handler_configs: Optional[Dict[str, Dict[str, Union[bool, str, int]]]] = None,
    color_map: Optional[Dict[str, str]] = None,
    styles: Optional[Dict[str, PStyle]] = None,
    level_styles: Optional[Dict[int, str]] = None,
    default_bg_color: Optional[str] = None,
    enable_unhandled_exception_logging: bool = False,
    update_unhandled_exception_logging: bool = False,
    log_exc_info: bool = True,
    critical_exceptions: Optional[Tuple[Type[BaseException], ...]] = None,
    unhandled_exception_debug: bool = False,
    unique: bool = True,
) -> logging.Logger:
    """
    Setup and return a logger with customizable handlers and formatters, including
    user-supplied custom handlers. Use PrintsCharmingLogHandler by default for
    custom styling and formatting.

    Args:
        pc (Optional[PrintsCharming]): An instance of PrintsCharming for styling logs.
        name (Optional[str]): Logger name (uses calling module name if None).
        level (int): Logging level for the logger. Defaults to logging.DEBUG.
        datefmt (str): Date format for the formatter.
        handler_configs (Optional[Dict[str, Dict[str, Union[bool, str, int]]]]):
            Configuration for handlers. Example:
                {
                    'console': {
                        'enabled': True,
                        'use_styles': True,
                        'formatter': CustomFormatter()
                    },
                    'file': {
                        'path': '/path/to/log',
                        'use_styles': False,
                        'level': logging.INFO
                    },
                    'custom_handler': {
                        'handler': MyCustomHandler(),
                        'formatter': CustomFormatter(),
                        'use_styles': False
                    }
                }
        color_map (Optional[Dict[str, str]]): Custom color map.
        styles (Optional[Dict[str, PStyle]]): Custom styles.
        level_styles (Optional[Dict[int, str]]): Dictionary mapping logging
            levels to style names.
        default_bg_color (Optional[str]): Default background color for logs.
        enable_unhandled_exception_logging (bool): Enable logging of unhandled exceptions.
        update_unhandled_exception_logging (bool): Update exception logging to new values.
        log_exc_info (bool): Enable logging of exception info.
        critical_exceptions (Optional[Tuple[Type[BaseException], ...]]): A tuple
            of exception types to log as critical.
        unhandled_exception_debug (bool): Debug mode for unhandled exceptions.
        unique (bool): If True (default), create a unique logger if the specified
            or derived name already exists.

    Returns:
        logging.Logger: Configured logger instance with specified handlers.
    """

    # Convert level to integer
    level = get_log_level(level)

    pc = pc or PrintsCharming(
        color_map=color_map or DEFAULT_COLOR_MAP.copy(),
        styles=copy.deepcopy(styles) or copy.deepcopy(DEFAULT_STYLES),
        default_bg_color=default_bg_color)

    if name is None:
        # Use inspect to get the module name of the caller
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        if caller_module is not None:
            name = caller_module.__name__

    # Check if a logger with this name already exists
    if unique and name in logging.Logger.manager.loggerDict:
        # Append a unique identifier to ensure a unique logger name
        name = f"{name}_{uuid.uuid4().hex}"

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Attach the `pc` instance to the logger for future access
    logger.pc = pc

    if enable_unhandled_exception_logging:
        set_custom_excepthook_with_logging(
            logger,
            pc,
            log_exc_info,
            critical_exceptions,
            unhandled_exception_debug,
            update_unhandled_exception_logging,
        )

    # Helper function to create or use a supplied formatter
    def create_formatter(
            use_styles: Optional[bool] = None,
            custom_formatter: Optional[logging.Formatter] = None,
    ) -> logging.Formatter:
        """
        Helper function to create or use a supplied formatter.

        Args:
            use_styles (Optional[bool]): Whether to use styles.
            custom_formatter (Optional[logging.Formatter]): Custom formatter provided by the user.

        Returns:
            logging.Formatter: Formatter instance.
        """

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
            use_styles=use_styles
        )

    # Handler factory function to create standard handlers
    def handler_factory(
            handler_name: str, config: Dict[str, Union[bool, str, int]]
    ) -> Optional[logging.Handler]:
        """
        Factory function to create standard handlers.

        Args:
            handler_name (str): Name of the handler.
            config (Dict[str, Any]): Configuration for the handler.

        Returns:
            Optional[logging.Handler]: Handler instance or None.
        """

        if handler_name == 'console':
            return PrintsCharmingLogHandler(pc=pc)
        elif handler_name == 'file':
            return logging.FileHandler(config['path'])  # Use standard FileHandler
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
    def add_handler(
            handler: logging.Handler,
            level: int,
            formatter: logging.Formatter,
    ) -> None:
        """
        Helper function to add handler to the logger.

        Args:
            handler (logging.Handler): The logging handler.
            level (int): Logging level.
            formatter (logging.Formatter): Formatter for the handler.
        """
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
        log_formatter = create_formatter(
            use_styles=use_styles, custom_formatter=custom_formatter
        )
        handler_level = config.get('level', level)

        # Add the handler to the logger
        add_handler(handler, handler_level, log_formatter)

    return logger



__all__ = ['PrintsCharmingFormatter', 'PrintsCharmingLogHandler', 'setup_logger']



