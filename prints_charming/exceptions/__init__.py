# prints_charming.exceptions.__init__.py

from .utils import set_excepthook
from .base_exceptions import PrintsCharmingException
from .internal_exceptions import (
    ColorNotFoundError,
    InvalidLengthError,
    UnsupportedEffectError
)


def setup_exceptions(pc: 'PrintsCharming') -> None:
    """
    Set up PrintsCharming to be used for all exceptions, including unhandled exceptions.

    Args:
        pc (PrintsCharming): Instance of PrintsCharming to be used for exception styling.
    """
    set_excepthook(pc)


__all__ = [
    'set_excepthook',
    'PrintsCharmingException',
    'ColorNotFoundError',
    'InvalidLengthError',
    'UnsupportedEffectError'
]
