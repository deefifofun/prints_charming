from typing import Dict
from .textstyle import TextStyle




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

DEFAULT_STYLES: Dict[str, TextStyle] = {
        "default"      : TextStyle(),
        "top_level_label": TextStyle(bold=True, italic=True),
        "sub_level_label": TextStyle(color='lblue'),
        "numbers"      : TextStyle(color="yellow"),
        'main_bullets' : TextStyle(color="purple"),
        "sub_bullets"  : TextStyle(color="pink"),
        "sub_proj"     : TextStyle(color="cyan"),
        "sub_bullet_title": TextStyle(color="orange"),
        "sub_bullet_sentence": TextStyle(color="dblue"),
        "default_bg"   : TextStyle(bg_color="black"),
        "white"        : TextStyle(color="white"),
        "gray"         : TextStyle(color="gray"),
        "dgray"        : TextStyle(color="dgray"),
        "black"        : TextStyle(color="black"),
        "green"        : TextStyle(color="green", bold=True),
        "vgreen"       : TextStyle(color="vgreen", bold=True),
        "log_true"     : TextStyle(color='vgreen'),
        "bg_color_green": TextStyle(color="white", bg_color='green'),
        "red"          : TextStyle(color="red"),
        "vred"         : TextStyle(color="vred", bold=True),
        "blue"         : TextStyle(color="blue"),
        "dblue"        : TextStyle(color="dblue"),
        "lblue"          : TextStyle(color="lblue"),
        "vblue"         : TextStyle(color="vblue"),
        "yellow"       : TextStyle(color="yellow"),
        "vyellow"      : TextStyle(color="vyellow"),
        "brass"        : TextStyle(color="brass"),
        "bronze"       : TextStyle(color="bronze"),
        "lbrown"       : TextStyle(color="lbrown"),
        "vorange"      : TextStyle(color="vorange"),
        "lplum"        : TextStyle(color="lplum"),
        "plum"         : TextStyle(color="plum"),
        "vplum"        : TextStyle(color="vplum"),
        "lmagenta"     : TextStyle(color="lmagenta"),
        "magenta"      : TextStyle(color="magenta", bold=True),
        "vmagenta"     : TextStyle(color="vmagenta"),
        "lpink"        : TextStyle(color="lpink"),
        "pink"         : TextStyle(color="pink",),
        "vpink"        : TextStyle(color="vpink"),
        "purple"       : TextStyle(color="purple"),
        "dpurple"      : TextStyle(color="dpurple"),
        "gold"         : TextStyle(color="gold"),
        "cyan"         : TextStyle(color="cyan"),
        "vcyan"        : TextStyle(color="vcyan"),
        "orange"       : TextStyle(color="orange"),
        "orangewhite"  : TextStyle(color="green", bg_color='dgray', underline=True),
        "copper"       : TextStyle(color="copper"),
        "brown"        : TextStyle(color="brown"),
        "sand"         : TextStyle(color="sand"),
        "lav"          : TextStyle(color="lav"),
        "lpurple"      : TextStyle(color="lpurple"),
        "plat"         : TextStyle(color="plat"),
        "silver"       : TextStyle(color="dfff", bg_color="dsilver"),
        "dfff"        : TextStyle(color="dfff", bg_color="purple", reverse=True),
        "vwhite"       : TextStyle(color="vwhite"),
        "header"       : TextStyle(color="vcyan"),
        "header_main"  : TextStyle(color="vcyan", bold=True, italic=True),
        "header_text"  : TextStyle(color="purple", bg_color="gray", bold=True, italic=True),
        "header_text2" : TextStyle(color="gray", bg_color="purple", bold=True),
        "task"         : TextStyle(color="blue", bold=True),
        "path"         : TextStyle(color="blue"),
        "filename"     : TextStyle(color="yellow"),
        "line_info"    : TextStyle(color="yellow", bold=True),
        "line_number"  : TextStyle(color="orange", bold=True),
        "function_name": TextStyle(color="yellow", italic=True),
        "error_message": TextStyle(color="vred", bold=True, dim=True),
        "code"         : TextStyle(color="yellow"),
        "dict_key": TextStyle(color="lblue"),
        "dict_value": TextStyle(color="white"),
        "true": TextStyle(color="vgreen"),
        "false": TextStyle(color="vred"),
        'none': TextStyle(color="lpurple"),
        "int": TextStyle(color="cyan"),
        "float": TextStyle(color="vcyan"),
        "other": TextStyle(color="lav"),
        "conceal": TextStyle(conceal=True),
}

DEFAULT_LOGGING_STYLES: Dict[str, TextStyle] = {
        "default": TextStyle(),
        "timestamp": TextStyle(color="white"),
        "class_name": TextStyle(color="dfff"),
        "method_name": TextStyle(color="lpurple"),
        "line_number": TextStyle(color="lav"),
        "debug": TextStyle(color="blue"),
        "info": TextStyle(color="green"),
        "warning": TextStyle(color="yellow"),
        "error": TextStyle(color="red"),
        "critical": TextStyle(color="vred"),
        "dict_key": TextStyle(color="lblue"),
        "dict_value": TextStyle(color="white"),
        "true": TextStyle(color="vgreen"),
        "false": TextStyle(color="vred"),
        'none': TextStyle(color="lpurple"),
        "int": TextStyle(color="cyan"),
        "float": TextStyle(color="vcyan"),
        "other": TextStyle(color="lav"),
}




