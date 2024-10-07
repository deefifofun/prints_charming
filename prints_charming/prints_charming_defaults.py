# prints_charming_defaults.py

import logging
from typing import Dict
from .prints_style import PStyle
from .utils import (
    compute_bg_color_map,
    get_ansi_256_fg_color_code,
    get_ansi_256_bg_color_code
)



DEFAULT_CONFIG: Dict[str, bool] = {
        "color_text"          : True,
        "args_to_strings"     : True,
        "style_names"         : True,
        "style_words_by_index": True,
        "kwargs"              : True,
        "conceal"             : True,
        "internal_logging"    : False,
        "log_level"           : 'DEBUG',  # Default to DEBUG level
}



DEFAULT_COLOR_MAP: Dict[str, str] = {
        "default": "\033[0m",
        "dfff": "\033[38;5;147m",
        "black": "\033[38;5;0m",
        "red": "\033[38;5;1m",
        "vred": "\033[38;5;196m",
        "green": "\033[38;5;34m",
        "dgreen": "\033[38;5;28m",
        "vgreen": "\033[38;5;46m",
        "lblue": "\033[38;5;117m",
        "blue": "\033[38;5;4m",
        "dblue": "\033[38;5;27m",
        "vblue": "\033[38;5;39m",
        "lmagenta": "\033[38;5;205m",
        "magenta": "\033[38;5;5m",
        "vmagenta": "\033[38;5;198m",
        "lav": "\033[38;5;183m",
        "lpurple": "\033[38;5;135m",
        "purple": "\033[38;5;129m",
        "dpurple": "\033[38;5;93m",
        "lplum": "\033[38;5;177m",
        "plum": "\033[38;5;128m",
        "vplum": "\033[38;5;201m",
        "lpink": "\033[38;5;218m",
        "pink": "\033[38;5;206m",
        "vpink": "\033[38;5;199m",
        "cyan": "\033[38;5;6m",
        "vcyan": "\033[38;5;51m",
        "orange": "\033[38;5;208m",
        "vorange": "\033[38;5;202m",
        "copper": "\033[38;5;166m",
        "yellow": "\033[38;5;3m",
        "vyellow": "\033[38;5;226m",
        "gold": "\033[38;5;220m",
        "brass": "\033[38;5;178m",
        "bronze": "\033[38;5;136m",
        "lbrown": "\033[38;5;138m",
        "brown": "\033[38;5;94m",
        "sand": "\033[38;5;215m",
        "silver": "\033[38;5;12m",
        "dsilver": "\033[38;5;10m",
        "gray": "\033[38;5;248m",
        "dgray": "\033[38;5;8m",
        "plat": "\033[38;5;252m",
        "white": "\033[38;5;15m",
        "vwhite": "\033[38;5;231m",
        "jupyter": "\033[38;2;48;56;64m"
}



DEFAULT_BG_COLOR_MAP: Dict[str, str] = {
    color: compute_bg_color_map(code) for color, code in DEFAULT_COLOR_MAP.items()
}



DEFAULT_256_COLOR_INDEXES: Dict[str, int] = {
    "default": 0,
    "dfff": 147,
    "black": 0,
    "red": 1,
    "vred": 196,
    "green": 34,
    "dgreen": 28,
    "vgreen": 46,
    "lblue": 117,
    "blue": 4,
    "dblue": 27,
    "vblue": 39,
    "lmagenta": 205,
    "magenta": 5,
    "vmagenta": 198,
    "lav": 183,
    "lpurple": 135,
    "purple": 129,
    "dpurple": 93,
    "lplum": 177,
    "plum": 128,
    "vplum": 201,
    "lpink": 218,
    "pink": 206,
    "vpink": 199,
    "cyan": 6,
    "vcyan": 51,
    "orange": 208,
    "vorange": 202,
    "copper": 166,
    "yellow": 3,
    "vyellow": 226,
    "gold": 220,
    "brass": 178,
    "bronze": 136,
    "lbrown": 138,
    "brown": 94,
    "sand": 215,
    "silver": 12,
    "dsilver": 10,
    "gray": 248,
    "dgray": 8,
    "plat": 252,
    "white": 15,
    "vwhite": 231
}


DEFAULT_256_FG_COLOR_CODES: Dict[str, str] = {
    color: get_ansi_256_fg_color_code(code) for color, code in DEFAULT_256_COLOR_INDEXES.items()
}


DEFAULT_256_BG_COLOR_CODES: Dict[str, str] = {
    color: get_ansi_256_bg_color_code(code) for color, code in DEFAULT_256_COLOR_INDEXES.items()
}



DEFAULT_EFFECT_MAP: Dict[str, str] = {
        "reverse"      : "\033[7m",
        "bold"         : "\033[1m",
        "dim"          : "\033[2m",
        "italic"       : "\033[3m",
        "underline"    : "\033[4m",
        "overline"     : "\033[53m",
        "strikethru"   : "\033[9m",
        "conceal"      : "\033[8m",
        "blink"        : "\033[5m",
}

DEFAULT_STYLES: Dict[str, PStyle] = {
        "default"      : PStyle(),
        "bold"      : PStyle(bold=True),
        "dim"       : PStyle(dim=True),
        "italic" : PStyle(italic=True),
        "bold_italic": PStyle(bold=True, italic=True),
        "underline" : PStyle(underline=True),
        "overline" : PStyle(overline=True),
        "strikethru" : PStyle(strikethru=True),
        "blink"      : PStyle(blink=True),
        "down_arrow": PStyle(color='vred', bold=True),
        "up_arrow": PStyle(color='vgreen', bold=True),
        "left_arrow": PStyle(color='vred', bold=True),
        "right_arrow": PStyle(color='vgreen', bold=True),
        "pc_title": PStyle(color='dfff', bold=True),
        "message": PStyle(color='yellow', italic=True, dim=True),
        "bullet": PStyle(color='green'),
        "link": PStyle(color='lblue', underline=True),
        "inline_code": PStyle(color='vmagenta'),
        "code_block": PStyle(color='vwhite', bold=True),
        "class_name": PStyle(color="dfff"),
        "method_name": PStyle(color="lpurple"),
        "top_level_label": PStyle(bold=True, italic=True),
        "sub_level_label": PStyle(color='lblue'),
        "numbers"      : PStyle(color="yellow"),
        'main_bullets' : PStyle(color="purple"),
        "sub_bullets"  : PStyle(color="pink"),
        "sub_proj"     : PStyle(color="cyan"),
        "sub_bullet_title": PStyle(color="orange"),
        "sub_bullet_sentence": PStyle(color="dblue"),
        "white"        : PStyle(color="white"),
        "gray"         : PStyle(color="gray"),
        "dgray"        : PStyle(color="dgray"),
        "black"        : PStyle(color="black"),
        "green"        : PStyle(color="green", bold=True),
        "vgreen"       : PStyle(color="vgreen", bold=True),
        "log_true"     : PStyle(color='vgreen'),
        "bg_color_green": PStyle(color="white", bg_color='green'),
        "red"          : PStyle(color="red"),
        "vred"         : PStyle(color="vred", bold=True),
        "blue"         : PStyle(color="blue"),
        "dblue"        : PStyle(color="dblue"),
        "lblue"          : PStyle(color="lblue"),
        "vblue"         : PStyle(color="vblue"),
        "yellow"       : PStyle(color="yellow"),
        "vyellow"      : PStyle(color="vyellow"),
        "brass"        : PStyle(color="brass"),
        "bronze"       : PStyle(color="bronze"),
        "lbrown"       : PStyle(color="lbrown"),
        "vorange"      : PStyle(color="vorange"),
        "lplum"        : PStyle(color="lplum"),
        "plum"         : PStyle(color="plum"),
        "vplum"        : PStyle(color="vplum"),
        "lmagenta"     : PStyle(color="lmagenta"),
        "magenta"      : PStyle(color="magenta", bold=True),
        "vmagenta"     : PStyle(color="vmagenta"),
        "lpink"        : PStyle(color="lpink"),
        "pink"         : PStyle(color="pink",),
        "vpink"        : PStyle(color="vpink"),
        "purple"       : PStyle(color="purple"),
        "dpurple"      : PStyle(color="dpurple"),
        "gold"         : PStyle(color="gold"),
        "cyan"         : PStyle(color="cyan"),
        "vcyan"        : PStyle(color="vcyan"),
        "orange"       : PStyle(color="orange"),
        "orangewhite"  : PStyle(color="green", bg_color='dgray', underline=True),
        "copper"       : PStyle(color="copper"),
        "brown"        : PStyle(color="brown"),
        "sand"         : PStyle(color="sand"),
        "lav"          : PStyle(color="lav"),
        "lpurple"      : PStyle(color="lpurple"),
        "plat"         : PStyle(color="plat"),
        "silver"       : PStyle(color="dfff", bg_color="dsilver"),
        "dfff"        : PStyle(color="dfff", bg_color="purple", reverse=True),
        "vwhite"       : PStyle(color="vwhite"),
        "header"       : PStyle(color="vcyan"),
        "header1"      : PStyle(color="blue", bold=True, underline=True),
        "header2" : PStyle(color="cyan", bold=True),
        "header_main"  : PStyle(color="vcyan", bold=True),
        "header_text"  : PStyle(color="purple", bg_color="gray", bold=True, italic=True),
        "header_text2" : PStyle(color="gray", bg_color="purple", bold=True),
        "task"         : PStyle(color="blue", bold=True),
        "path"         : PStyle(color="blue"),
        "filename"     : PStyle(color="yellow"),
        "line_info"    : PStyle(color="yellow", bold=True),
        "line_number"  : PStyle(color="orange", bold=True),
        "function_name": PStyle(color="yellow", italic=True),
        "error_message": PStyle(color="vred", bold=True, dim=True),
        "code"         : PStyle(color="yellow"),
        "dict_key": PStyle(color="lblue"),
        "dict_value": PStyle(color="white"),
        "true": PStyle(color="vgreen"),
        "false": PStyle(color="vred"),
        'none': PStyle(color="lpurple"),
        "int": PStyle(color="cyan"),
        "float": PStyle(color="vcyan"),
        "other": PStyle(color="lav"),
        "python_keyword": PStyle(color="lav", italic=True),
        "python_string": PStyle(color="dgreen"),
        "python_comment": PStyle(dim=True),
        "python_builtin": PStyle(color="blue"),
        "python_number": PStyle(color="yellow"),
        "python_function_name": PStyle(color="cyan"),
        "python_parenthesis": PStyle(color="vwhite"),
        "python_param": PStyle(color="orange"),
        "python_self_param": PStyle(color="red"),
        "python_operator": PStyle(color="vpink"),
        "python_default_value": PStyle(color="lav", italic=True),
        "python_colon": PStyle(color="vpink"),
        "python_variable": PStyle(color="white"),
        "python_fstring_variable": PStyle(color="orange"),
        "conceal": PStyle(conceal=True)
}


DEFAULT_CONTROL_MAP: Dict[str, str] = {

        # 256 Color Mode (Foreground)
        "fg_color_256": "\033[38;5;{n}m",  # Set 256 color mode foreground (0-255)

        # 256 Color Mode (Background)
        "bg_color_256": "\033[48;5;{n}m",  # Set 256 color mode background (0-255)

        # True Color Mode (Foreground)
        "fg_truecolor": "\033[38;2;{r};{g};{b}m",  # Set true color mode foreground (RGB)

        # True Color Mode (Background)
        "bg_truecolor": "\033[48;2;{r};{g};{b}m",  # Set true color mode background (RGB)

        # Buffer Control
        "alt_buffer": "\033[?1049h",
        "normal_buffer": "\033[?1049l",
        "alt_buffer_no_save": "\033[?47h",  # Switch to alternate buffer without saving the cursor
        "normal_buffer_no_save": "\033[?47l",  # Switch back to normal buffer without restoring the cursor

        # Screen Clearing
        "clear_screen": "\033[2J",  # Clear the entire screen
        "clear_screen_from_cursor": "\033[0J",  # Clear screen from the cursor down
        "clear_screen_to_cursor": "\033[1J",  # Clear screen from the cursor up

        # Line Clearing
        "clear_line": "\033[2K",  # Clear the entire current line
        "clear_line_from_cursor": "\033[0K",  # Clear from the cursor to the end of the line
        "clear_line_to_cursor": "\033[1K",  # Clear from the beginning of the line to the cursor

        # Cursor Movement
        "cursor_home": "\033[H",  # Move cursor to the home position (top-left corner)
        "cursor_position": "\033[{row};{col}H",  # Move cursor to specified row and column
        "cursor_up": "\033[{n}A",  # Move cursor up by n rows
        "cursor_down": "\033[{n}B",  # Move cursor down by n rows
        "cursor_right": "\033[{n}C",  # Move cursor forward (right) by n columns
        "cursor_left": "\033[{n}D",  # Move cursor backward (left) by n columns
        "save_cursor_position": "\033[s",  # Save the current cursor position
        "restore_cursor_position": "\033[u",  # Restore saved cursor position
        "hide_cursor": "\033[?25l",  # Hide the cursor
        "show_cursor": "\033[?25h",  # Show the cursor

        # Line and Text Manipulation
        "insert_line": "\033[L",  # Insert a blank line at the current cursor position
        "delete_line": "\033[M",  # Delete the current line
        "scroll_up": "\033[S",  # Scroll the page up
        "scroll_down": "\033[T",  # Scroll the page down

        # Mouse Control (Enable or disable mouse reporting)
        "enable_mouse": "\033[?1000h",  # Enable basic mouse tracking (xterm-style)
        "disable_mouse": "\033[?1000l",  # Disable mouse tracking
        "enable_mouse_button_event_tracking": "\033[?1002h",  # Enable mouse button event tracking
        "disable_mouse_button_event_tracking": "\033[?1002l",  # Disable mouse button event tracking

        # Miscellaneous
        "bell": "\007",  # Bell (beep sound)
        "enable_application_keypad": "\033[?1h",  # Enable application keypad mode (for arrow keys, etc.)
        "disable_application_keypad": "\033[?1l",  # Disable application keypad mode

        # Key Codes (Special Keys)
        "arrow_up": "\033[A",  # Up arrow key
        "arrow_down": "\033[B",  # Down arrow key
        "arrow_right": "\033[C",  # Right arrow key
        "arrow_left": "\033[D",  # Left arrow key

        # Function Keys (F1 to F12)
        "f1": "\x1bOP",              # F1 key
        "f2": "\x1bOQ",              # F2 key
        "f3": "\x1bOR",              # F3 key
        "f4": "\x1bOS",              # F4 key
        "f5": "\x1b[15~",            # F5 key
        "f6": "\x1b[17~",            # F6 key
        "f7": "\x1b[18~",            # F7 key
        "f8": "\x1b[19~",            # F8 key
        "f9": "\x1b[20~",            # F9 key
        "f10": "\x1b[21~",           # F10 key
        "f11": "\x1b[23~",           # F11 key
        "f12": "\x1b[24~",           # F12 key

        # Home, End, Insert, Delete, Page Up, Page Down
        "home": "\x1b[H",            # Home key
        "end": "\x1b[F",             # End key
        "insert": "\x1b[2~",         # Insert key
        "delete": "\x1b[3~",         # Delete key
        "page_up": "\x1b[5~",        # Page Up key
        "page_down": "\x1b[6~",      # Page Down key

        # Escape Key
        "escape": "\x1b",            # Escape key

        # Tab Key
        "tab": "\t",                 # Tab key

        # Backspace Key
        "backspace": "\x7f",         # Backspace key (sometimes "\x08" in some terminals)

        # Enter/Return Key
        "enter": "\r",               # Enter/Return key (same as newline in raw mode)

        # Control Keys (Ctrl+A to Ctrl+Z)
        "ctrl_a": "\x01",            # Ctrl+A
        "ctrl_b": "\x02",            # Ctrl+B
        "ctrl_c": "\x03",            # Ctrl+C
        "ctrl_d": "\x04",            # Ctrl+D
        "ctrl_e": "\x05",            # Ctrl+E
        "ctrl_f": "\x06",            # Ctrl+F
        "ctrl_g": "\x07",            # Ctrl+G
        "ctrl_h": "\x08",            # Ctrl+H (usually Backspace)
        "ctrl_i": "\x09",            # Ctrl+I (usually Tab)
        "ctrl_j": "\x0a",            # Ctrl+J (Line Feed)
        "ctrl_k": "\x0b",            # Ctrl+K
        "ctrl_l": "\x0c",            # Ctrl+L (Clear screen in some systems)
        "ctrl_m": "\x0d",            # Ctrl+M (Carriage Return)
        "ctrl_n": "\x0e",            # Ctrl+N
        "ctrl_o": "\x0f",            # Ctrl+O
        "ctrl_p": "\x10",            # Ctrl+P
        "ctrl_q": "\x11",            # Ctrl+Q (Resume, XON)
        "ctrl_r": "\x12",            # Ctrl+R
        "ctrl_s": "\x13",            # Ctrl+S (Stop, XOFF)
        "ctrl_t": "\x14",            # Ctrl+T
        "ctrl_u": "\x15",            # Ctrl+U
        "ctrl_v": "\x16",            # Ctrl+V
        "ctrl_w": "\x17",            # Ctrl+W
        "ctrl_x": "\x18",            # Ctrl+X
        "ctrl_y": "\x19",            # Ctrl+Y
        "ctrl_z": "\x1a",            # Ctrl+Z

        # Other Control Keys
        "ctrl_backslash": "\x1c",    # Ctrl+\
        "ctrl_square_bracket": "\x1b",  # Ctrl+[
        "ctrl_caret": "\x1e",        # Ctrl+^
        "ctrl_underscore": "\x1f",   # Ctrl+_

        # Shift + Arrow Keys (Some terminals may have different codes)
        "shift_arrow_up": "\x1b[1;2A",   # Shift + Up arrow
        "shift_arrow_down": "\x1b[1;2B", # Shift + Down arrow
        "shift_arrow_right": "\x1b[1;2C",# Shift + Right arrow
        "shift_arrow_left": "\x1b[1;2D", # Shift + Left arrow

        # Alt + Arrow Keys (Some terminals may have different codes)
        "alt_arrow_up": "\x1b[1;3A",     # Alt + Up arrow
        "alt_arrow_down": "\x1b[1;3B",   # Alt + Down arrow
        "alt_arrow_right": "\x1b[1;3C",  # Alt + Right arrow
        "alt_arrow_left": "\x1b[1;3D",   # Alt + Left arrow

        # Meta Key (Alt or Esc)
        "meta": "\x1b",               # Meta key (typically Alt or Esc)
}





DEFAULT_ERROR_STYLES: Dict[str, PStyle] = {
        "header"       : PStyle(color="vcyan"),
        "path"         : PStyle(color="blue"),
        "filename"     : PStyle(color="yellow"),
        "line_info"    : PStyle(color="yellow", bold=True),
        "line_number"  : PStyle(color="orange", bold=True),
        "function_name": PStyle(color="yellow", italic=True),
        "error_message": PStyle(color="vred", bold=True, dim=True),
}


DEFAULT_LOGGING_STYLES: Dict[str, PStyle] = {
        "default": PStyle(),
        "timestamp": PStyle(color="vwhite"),
        "filename": PStyle(color="cyan", bold=True),
        'record_name': PStyle(color="orange"),
        "hostname": PStyle(color="white"),
        "class_name": PStyle(color="dfff"),
        "method_name": PStyle(color="vwhite"),
        "line_number": PStyle(color="vcyan"),
        "highlight_arg": PStyle(color="vcyan"),
        "args": PStyle(color="dfff", italic=True),
        "debug": PStyle(color="blue"),
        "info": PStyle(color="green"),
        "warning": PStyle(color="yellow"),
        "error": PStyle(color="red"),
        "critical": PStyle(color="vred", bold=True, italic=True),
        "dict_key": PStyle(color="lblue"),
        "dict_value": PStyle(color="white"),
        "true": PStyle(color="vgreen"),
        "false": PStyle(color="vred"),
        'none': PStyle(color="lpurple"),
        "int": PStyle(color="cyan"),
        "float": PStyle(color="vcyan"),
        "other": PStyle(color="lav"),
        "conceal": PStyle(conceal=True)
}



DEFAULT_LEVEL_STYLES = {
    logging.DEBUG: 'debug',
    logging.INFO: 'info',
    logging.WARNING: 'warning',
    logging.ERROR: 'error',
    logging.CRITICAL: 'critical'
}





