# prints_charming.exceptions.utils.py

import sys
import traceback
import warnings
import logging
from typing import Any, Callable, Optional, Tuple, Type, Union
from .base_exceptions import PrintsCharmingException


def set_excepthook(
        pc: 'PrintsCharming',
        logger: Optional[logging.Logger] = None,
        log_exc_info: bool = False,
        critical_exceptions: Optional[Tuple[Type[BaseException], ...]] = None,
        update_exception_logging: bool = False
) -> None:
    """
    Configures a custom exception handler for unhandled exceptions, optionally
    logging them if a logger is provided.

    Args:
        pc (PrintsCharming): Instance of PrintsCharming used for styling exceptions.
        logger (Optional[logging.Logger]): Logger instance for logging unhandled
            exceptions, if provided.
        log_exc_info (bool): Whether to include exception info when logging.
        critical_exceptions (Optional[Tuple[Type[BaseException], ...]]): Tuple
            of exception types considered critical.
        update_exception_logging (bool): Whether to override an existing custom
            exception hook.
    """

    if pc:
        PrintsCharmingException.shared_pc_exception_instance = pc

    if critical_exceptions:
        PrintsCharmingException.critical_exceptions = critical_exceptions



    def custom_excepthook(
        exc_type: Union[Type[BaseException], Type[PrintsCharmingException]],
        exc_value: Union[BaseException, PrintsCharmingException],
        exc_traceback: Optional[Any]
    ) -> None:
        """
        Custom exception hook to handle both PrintsCharming-specific and general exceptions.

        Args:
            exc_type (Union[Type[BaseException], Type[PrintsCharmingException]]):
                Type of the exception raised.
            exc_value (Union[BaseException, PrintsCharmingException]):
                Exception instance raised.
            exc_traceback (Optional[Any]):
                Traceback object of the exception.
        """

        # Check if the exception is a subclass of PrintsCharmingException
        if issubclass(exc_type, PrintsCharmingException):
            exc_value.handle_exception()
        else:
            # Handle non-PrintsCharming exceptions
            general_exception = PrintsCharmingException(
                str(exc_value),
                pc,
                use_shared_pc=True
            )
            general_exception.handle_exception(
                logger=logger,
                exc_type=exc_type,
                exc_value=exc_value,
                exc_info=log_exc_info
            )

    # Store the original excepthook
    default_excepthook = sys.__excepthook__


    # Check if the current excepthook is custom
    def is_custom_excepthook() -> bool:
        """
        Checks if the current excepthook is custom.

        Returns:
            bool: True if a custom excepthook is already set, False otherwise.
        """
        return sys.excepthook is not default_excepthook


    if is_custom_excepthook():
        if not update_exception_logging:
            msg_parts = [
                pc.apply_style(
                    'red',
                    'sys.excepthook has already been custom set.'
                ),
                pc.apply_style(
                    'blue',
                    'Change'
                ),
                pc.apply_style(
                    'orange',
                    'update_custom_excepthook ='
                ),
                "True to update the custom excepthook."
            ]

            """
            msg_sec1 = pc.apply_style(
                'red',
                'sys.excepthook has already been custom set.'
            )
            msg_sec2 = pc.apply_style(
                'blue',
                'Change'
            )
            msg_sec3 = pc.apply_style(
                'orange',
                'update_custom_excepthook ='
            )
            msg_sec4 = f"True to update the custom excepthook."
            msg = f'{msg_sec1} {msg_sec2} {msg_sec3} {msg_sec4}'
            """

            msg = ' '.join(msg_parts)
            if logger:
                logger.info(msg)

            else:
                #pc.print(f"{msg_sec1} {msg_sec2} {msg_sec3} {msg_sec4}", color='blue')
                pc.print(msg, color='green')
        else:
            sys.excepthook = custom_excepthook
    else:
        sys.excepthook = custom_excepthook

