from .prints_style import PStyle

from .prints_charming_defaults import (
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES,
    DEFAULT_LEVEL_STYLES,
    DEFAULT_CONTROL_MAP
)

from .utils import (
    get_terminal_width,
    set_custom_excepthook,
    set_custom_excepthook_with_logging,
    custom_excepthook,
    custom_excepthook_with_logging
)

from .prints_charming import PrintsCharming



from .exceptions import (
    PrintsCharmingError,
    ColorNotFoundError,
    InvalidLengthError
)

from .frame_builder import FrameBuilder
from .interactive_menu import InteractiveMenu
from .table_manager import TableManager
from .toggle_manager import ToggleManager

from .win_utils import WinUtils

# Capture the state of the namespace before the import
before_import = set(globals().keys())

from .color_maps import *

# Capture the state of the namespace after the import
after_import = set(globals().keys())

# Find the symbols added by the import from .color_maps
imported_symbols = after_import - before_import


__all__ = ['PStyle', 'PrintsCharming', 'DEFAULT_CONFIG', 'DEFAULT_COLOR_MAP', 'DEFAULT_EFFECT_MAP',
           'DEFAULT_STYLES', 'DEFAULT_LOGGING_STYLES', 'DEFAULT_LEVEL_STYLES', 'PrintsCharmingError',
           'ColorNotFoundError', 'InvalidLengthError', 'FrameBuilder', 'InteractiveMenu', 'TableManager',
           'ToggleManager', 'get_terminal_width', 'set_custom_excepthook', 'set_custom_excepthook_with_logging',
           'custom_excepthook', 'custom_excepthook_with_logging', 'WinUtils']


# Extend __all__ with only the symbols imported from .color_maps
__all__.extend([name for name in imported_symbols if not name.startswith('_')])


