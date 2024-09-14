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
        "vwhite": "\033[38;5;231m"
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
        "default_bg"   : PStyle(bg_color="black"),
        "bold"      : PStyle(bold=True),
        "dim"       : PStyle(dim=True),
        "italic" : PStyle(italic=True),
        "bold_italic": PStyle(bold=True, italic=True),
        "underline" : PStyle(underline=True),
        "overline" : PStyle(overline=True),
        "strikethru" : PStyle(strikethru=True),
        "blink"      : PStyle(blink=True),
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
        "alt_buffer": "\033[?1049h",
        "normal_buffer": "\033[?1049l",
        "alt_buffer_no_save": "\033[?47h",  # Switch to alternate buffer without saving the cursor
        "normal_buffer_no_save": "\033[?47l",  # Switch back to normal buffer without restoring the cursor
        "clear_line": "\033[2K",
        "clear_screen": "\033[2J",
        "cursor_position": "\033[{row};{col}H",
        "cursor_home": "\033[H",  # Move cursor to the home position (top-left corner)
        "move_cursor_up": "\033[{n}A",
        "move_cursor_down": "\033[{n}B",
        "move_cursor_right": "\033[{n}C",
        "move_cursor_left": "\033[{n}D",
        "save_cursor_position": "\033[s",
        "restore_cursor_position": "\033[u",
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





