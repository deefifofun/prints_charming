# prints_charming.settings.style_maps

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from ..prints_style import PStyle


DEFAULT_STYLES: Dict[str, PStyle] = {
        "default"      : PStyle(),
        "pc_title": PStyle(color='dfff', bold=True),

        "bold"      : PStyle(bold=True),
        "dim"       : PStyle(dim=True),
        "italic" : PStyle(italic=True),
        "bold_italic": PStyle(bold=True, italic=True),
        "underline" : PStyle(underline=True),
        "overline" : PStyle(overline=True),
        "strikethru" : PStyle(strikethru=True),
        "blink"      : PStyle(blink=True),

        "numbers"      : PStyle(color="yellow"),

        "down_arrow": PStyle(color='vred', bold=True),
        "up_arrow": PStyle(color='vgreen', bold=True),
        "left_arrow": PStyle(color='vred', bold=True),
        "right_arrow": PStyle(color='vgreen', bold=True),


        "header1"      : PStyle(color="blue", bold=True, underline=True),
        "header2": PStyle(color="cyan", bold=True),
        "header_main"  : PStyle(color="vcyan", bold=True),
        "header_text"  : PStyle(color="purple", bg_color="gray", bold=True, italic=True),
        "header_text2" : PStyle(color="gray", bg_color="purple", bold=True),

        "task"         : PStyle(color="blue", bold=True),
        "message": PStyle(color='yellow', italic=True, dim=True),
        "link": PStyle(color='lblue', underline=True),

        "top_level_label": PStyle(bold=True, italic=True),
        "sub_level_label": PStyle(color='lblue'),
        'main_bullets' : PStyle(color="purple"),
        "sub_bullets"  : PStyle(color="pink"),
        "sub_proj"     : PStyle(color="cyan"),
        "sub_bullet_title": PStyle(color="orange"),
        "sub_bullet_sentence": PStyle(color="dblue"),
        "bullet": PStyle(color='green'),

        #"method_name": PStyle(color="lpurple"),
        "inline_code": PStyle(color='vmagenta'),
        "code_block": PStyle(color='vwhite', bold=True),

        # Error styles
        "header"       : PStyle(color="vcyan"),
        "path"         : PStyle(color="blue"),
        "error_filename": PStyle(color="yellow"),
        "line_info"    : PStyle(color="yellow", bold=True),
        "error_line_number"  : PStyle(color="orange", bold=True),
        "function_name": PStyle(color="yellow", italic=True),
        "error_message": PStyle(color="vred", bold=True, dim=True),
        "regex_fail_line_fb": PStyle(color="blue"),
        "subclass_name": PStyle(color="vyellow"),
        "subclass_name_before": PStyle(color="vwhite"),
        "subclass_name_after": PStyle(),
        "unhandled_exception_line": PStyle(color="vred", bold=True, italic=True),
        "log_true"     : PStyle(color='vgreen'),

        # Default Logging
        "timestamp": PStyle(color="vwhite"),
        "debug": PStyle(color="blue"),
        "info": PStyle(color="green"),
        "warning": PStyle(color="yellow"),
        "error": PStyle(color="red"),
        "critical": PStyle(color="vred", bold=True, italic=True),
        "filename": PStyle(color="cyan", bold=True),
        'record_name': PStyle(color="orange"),
        "hostname": PStyle(color="white"),
        "class_name": PStyle(color="dfff"),
        "method_name": PStyle(color="vwhite"),
        "line_number": PStyle(color="vcyan"),
        "highlight_arg": PStyle(color="vcyan"),
        "args": PStyle(color="dfff", italic=True),

        # Python dict styles
        "dict_key": PStyle(color="lblue"),
        "dict_value": PStyle(color="white"),
        "true": PStyle(color="vgreen"),
        "false": PStyle(color="vred"),
        'none': PStyle(color="lpurple"),
        "int": PStyle(color="cyan"),
        "float": PStyle(color="vcyan"),
        "other": PStyle(color="lav"),

        "code"         : PStyle(color="yellow"),

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


        "bg_color_green": PStyle(color="white", bg_color='green'),
        "black"        : PStyle(color="black"),
        "blue"         : PStyle(color="blue"),
        "dblue"        : PStyle(color="dblue"),
        "lblue"          : PStyle(color="lblue"),
        "vblue"         : PStyle(color="vblue"),
        "brass"        : PStyle(color="brass"),
        "bronze"       : PStyle(color="bronze"),
        "lbrown"       : PStyle(color="lbrown"),
        "brown"        : PStyle(color="brown"),

        "copper"       : PStyle(color="copper"),
        "cyan"         : PStyle(color="cyan"),
        "vcyan"        : PStyle(color="vcyan"),

        "dfff"        : PStyle(color="dfff", bg_color="purple", reverse=True),

        "gold"         : PStyle(color="gold"),
        "dgray"        : PStyle(color="dgray"),
        "gray"         : PStyle(color="gray"),
        "green"        : PStyle(color="green", bold=True),
        "vgreen"       : PStyle(color="vgreen", bold=True),

        "lav"          : PStyle(color="lav"),

        "lmagenta"     : PStyle(color="lmagenta"),
        "magenta"      : PStyle(color="magenta", bold=True),
        "vmagenta"     : PStyle(color="vmagenta"),

        "vorange"      : PStyle(color="vorange"),
        "orange"       : PStyle(color="orange"),
        "orangewhite"  : PStyle(color="green", bg_color='dgray', underline=True),

        "lpink"        : PStyle(color="lpink"),
        "pink"         : PStyle(color="pink",),
        "vpink"        : PStyle(color="vpink"),
        "plat"         : PStyle(color="plat"),
        "lplum"        : PStyle(color="lplum"),
        "plum"         : PStyle(color="plum"),
        "vplum"        : PStyle(color="vplum"),
        "lpurple"      : PStyle(color="lpurple"),
        "purple"       : PStyle(color="purple"),
        "dpurple"      : PStyle(color="dpurple"),

        "red"          : PStyle(color="red"),
        "vred"         : PStyle(color="vred", bold=True),

        "sand"         : PStyle(color="sand"),
        "silver"       : PStyle(color="dfff", bg_color="dsilver"),

        "white"        : PStyle(color="white"),
        "vwhite"       : PStyle(color="vwhite"),

        "yellow"       : PStyle(color="yellow"),
        "vyellow"      : PStyle(color="vyellow"),


        "conceal": PStyle(conceal=True),
        "conceal_replaced": PStyle(color='plum'),

        "selected_style": PStyle(color='vcyan'),
        "unselected_style": PStyle(),

        "test_color_red_bg_dgray" : PStyle(color="red", bg_color="dgray"),
        "test_color_red_bg_dgray_reverse" : PStyle(color='red', bg_color="dgray", reverse=True),
        "purple_dgray_bg": PStyle(color="purple", bg_color="dgray"),
        "purple_dgray_bg_reverse" : PStyle(color='purple', bg_color="dgray", reverse=True),
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




