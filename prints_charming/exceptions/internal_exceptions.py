# prints_charming.exceptions.internal_exceptions.py

from .base_exceptions import PrintsCharmingException




class ColorNotFoundError(PrintsCharmingException):
    """Exception raised when a color is not found in the color map."""
    pass


class InvalidLengthError(PrintsCharmingException):
    """Exception raised when an invalid length is provided."""
    pass


class UnsupportedEffectError(PrintsCharmingException):
    """Exception raised when an unsupported effect is requested."""
    pass













