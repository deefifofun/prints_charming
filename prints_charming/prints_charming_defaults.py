# prints_charming_defaults.py

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from .prints_style import PStyle
from .utils import (
    compute_bg_color_map,
    get_ansi_256_fg_color_code,
    get_ansi_256_bg_color_code
)



DEFAULT_CONFIG: Dict[str, Union[bool, int, str]] = {
        "color_text"          : True,
        "args_to_strings"     : True,
        "style_names"         : True,
        "style_words_by_index": True,
        "kwargs"              : True,
        "conceal"             : True,
        "tab_width"           : 4,
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
        "indigo": "\033[38;5;54m",
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
        "jupyter": "\033[38;2;48;56;64m",
        "charm": "\033[38;2;24;28;33m",
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


        "header1"      : PStyle(color="blue", bold=True),
        "header2": PStyle(color="cyan", bold=True),
        "header3": PStyle(color='vcyan', bold=True),
        "header_main"  : PStyle(color="vcyan", bold=True),
        "header_text"  : PStyle(color="purple", bg_color="gray", bold=True, italic=True),
        "header_text2" : PStyle(color="gray", bg_color="purple", bold=True),

        # Hyperlinks
        "hyperlink": PStyle(color="blue", underline=True, italic=True),
        "hyperlink-clicked": PStyle(color="blue", underline=True, italic=True, dim=True),

        "link_text": PStyle(color='vgreen'),
        "link_url": PStyle(color='orange'),

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
        "bullet_title": PStyle(color="green", bold=True),

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
        "string": PStyle(color="dfff"),
        "other": PStyle(color="lav"),

        "code"         : PStyle(color="yellow"),

        "python_bracket": PStyle(color="vwhite"),
        "python_builtin": PStyle(color="blue"),
        "python_colon": PStyle(color="vpink", bold=True),
        "python_comma": PStyle(color="white"),
        "python_comment": PStyle(dim=True),
        "python_default_value": PStyle(color="lav", italic=True),
        "python_fstring_variable": PStyle(color="orange"),
        "python_function_name": PStyle(color="cyan"),
        "python_keyword": PStyle(color="lav", italic=True),
        "python_number": PStyle(color="yellow"),
        "python_operator": PStyle(color="vpink"),
        "python_param": PStyle(color="orange"),
        "python_parenthesis": PStyle(color="vwhite"),
        "python_self_param": PStyle(color="red"),
        "python_string": PStyle(color="dgreen"),
        "python_variable": PStyle(color="white"),


        # Markdown specific
        "md_image_title": PStyle(color="vgreen"),
        "md_image_path": PStyle(color="orange"),

        'horiz_border': PStyle(color='purple'),
        'vert_border': PStyle(color='orange'),

        'horiz_border_top': PStyle(color='blue'),
        'vert_border_left': PStyle(color='blue'),
        'vert_border_inner': PStyle(color='blue'),
        'vert_border_right': PStyle(color='blue'),
        'horiz_border_bottom': PStyle(color='blue'),
        'col_sep': PStyle(color='blue'),



        'bottom_segment': PStyle(color='blue'),

        'progress': PStyle(color='cyan', bold=True),

        'button_normal': PStyle(color='white'),
        'button_pressed': PStyle(color='black', bg_color='green', bold=True),


        # Boxes

        # Unselected
        'box_top_unselected': PStyle(color='purple', bold=True, underline=True),
        'box_left_unselected': PStyle(color='purple', bg_color='dgray'),
        'box_content_unselected': PStyle(color='orange', bg_color='dgray'),
        'box_right_unselected': PStyle(color='purple', bg_color='dgray'),
        'box_bottom_unselected': PStyle(color='purple', overline=True),

        # Selected
        'box_top_selected': PStyle(color='purple', bold=True, underline=True),
        'box_left_selected': PStyle(color='purple', bg_color='dgray'),
        'box_content_selected': PStyle(color='orange', bg_color='dgray'),
        'box_right_selected': PStyle(color='purple', bg_color='dgray'),
        'box_bottom_selected': PStyle(color='purple', overline=True),

        # Partial Unselected
        'box_top_unselected_partial': PStyle(color='purple', bold=True, underline=False),
        'box_left_unselected_partial': PStyle(color='purple', bg_color='dgray'),
        'box_content_unselected_partial': PStyle(color='orange', bg_color='dgray'),
        'box_right_unselected_partial': PStyle(color='purple', bg_color='dgray'),
        'box_bottom_unselected_partial': PStyle(color='purple', overline=False),

        # Partial Selected
        'box_top_selected_partial': PStyle(color='purple', bold=True, underline=False),
        'box_left_selected_partial': PStyle(color='purple', bg_color='dgray'),
        'box_content_selected_partial': PStyle(color='orange', bg_color='dgray'),
        'box_right_selected_partial': PStyle(color='purple', bg_color='dgray'),
        'box_bottom_selected_partial': PStyle(color='purple', overline=False),


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

        "jupyter" : PStyle(color="jupyter"),

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



DEFAULT_LEVEL_STYLES = {
    logging.DEBUG: 'debug',
    logging.INFO: 'info',
    logging.WARNING: 'warning',
    logging.ERROR: 'error',
    logging.CRITICAL: 'critical'
}



DEFAULT_UNICODE_MAP = {

        # Arrows
        "arrow_up": "⭡",
        "arrow_down": "⭣",
        "arrow_left": "⇐",
        "arrow_right": "⇒",

        # Boxes and Blocks
        "full_block": "█",
        "seven_eighths_block": "▇",
        "three_quarters_block": "▆",
        "five_eighths_block": "▅",
        "medium_block": "▄",
        "half_block": "▄",

        "light_shade": "░",
        "medium_shade": "▒",
        "dark_shade": "▓",



        "square": "■",
        "hollow_square": "⬜",
        "medium_hollow_square": "□",
        "rounded_hollow_square": "▢",
        "medium_square": "⬛",
        "small_square": "▪",
        "small_hollow_square": "▫",

        "square_corners": "⛶",
        "square_inner_rounded_corners": "⛚",
        "square_shadowed": "❏",
        "squares_tiny": "⚏",
        "square_diagonal_lines": "⛆",

        "square_no_bottom": "⨅",
        "square_no_top": "⨆",

        "box_empty": "☐",
        "box_filled_with_x": "☒",
        "box_filled_with_checkmark": "☑",

        "upper_half_block": "▀",
        "lower_half_block": "▄",

        "lower_three_eighths_block": "▃",

        "blocks_large": "␩",
        "blocks_medium": "␨",
        "blocks_small": "␧",

        "dashes_two": "⚋",

        "upper_one_eighth_block": "▔",
        "lower_one_eighth_block": "▁",

        "box_drawings_light_horizontal": "─",
        "box_drawings_heavy_horizontal": "━",

        "light_left_half_arc": "╸",
        "light_up_arc": "╹",

        "parallelogram": "▰",
        "hollow_rectangle": "▭",

        "quarter_block": "▂",
        "quad_block": "▖",
        "rectangle": "▮",
        "hollow_vert_rectangle": "▯",

        "vertical_line":  "│",
        "light_vertical": "│",
        "heavy_vertical": "┃",

        "upper_light_vertical_line": "⏐",

        "thick_forward_slash": "/",
        "slanted_forward_slash": "／",
        "slanted_back_slash": "＼",
        "thick_back_slash": "\"",

        "left_one_eighth_block": "▏",
        "right_one_eighths_block": "▕",
        "left_quarter_block": "▎",
        "left_three_eighths_block": "▍",
        "left_half_block": "▌",
        "left_five_eighths_block": "▋",
        "left_three_quarters_block": "▊",
        "left_seven_eighths_block": "▉",

        "three_quadrant_block": "▞",
        "quadrant_lower_left": "▖",
        "quadrant_lower_right": "▗",
        "quadrant_upper_left": "▘",
        "quadrant_upper_right": "▝",

        "lower_horizontal_bracket": "⏠",
        "upper_horizontal_bracket": "⏡",

        "upper_left_corner_rounded": "⎛",
        "lower_left_corner_rounded": "⎝",
        "upper_right_corner_rounded": "⎞",
        "lower_right_corner_rounded": "⎠",

        "vertical_right_left_thing": "⎰",
        "vertical_left_right_thing": "⎱",

        "lines_right": "⚞",
        "lines_left": "⚟",


        # Lines and Corners
        "bottom_left_corner": "└",
        "bottom_right_corner": "┘",
        "bottom_t": "┴",
        "cross": "┼",
        "double_bottom_left_corner": "╚",
        "double_bottom_right_corner": "╝",
        "double_horizontal_line": "═",
        "double_top_left_corner": "╔",
        "double_top_right_corner": "╗",
        "double_vertical_line": "║",
        "horizontal_heavy_double_dash": "╍",
        "horizontal_light_double_dash": "╌",
        "horizontal_light_triple_dash": "┄",
        "horizontal_line": "─",
        "left_t": "├",
        "right_t": "┤",
        "top_left_corner": "┌",
        "top_right_corner": "┐",
        "top_t": "┬",
        "vertical_heavy_double_dash": "╏",
        "vertical_light_double_dash": "╎",
        "vertical_light_triple_dash": "┆",


        # Shapes
        "bullet": "•",
        "bullet_operator": "∙",
        "circle": "●",
        "circle_cross_hairs": "⨁",
        "circle_diag_cross_hairs": "⨂",
        "circle_medium": "⚫",
        "circles_chained": "⚯",
        "circles_small": "⛬",
        "circle_filled_with_dot": "☉",
        "circle_shadowed": "❍",
        "circular_vertical": "⩇",
        "diamond": "◆",
        "hollow_circle": "◯",
        "hollow_diamond": "◇",
        "hollow_star": "☆",
        "star": "★",
        "triangle_down": "▼",
        "triangle_left": "◀",
        "triangle_right": "▶",
        "triangle_up": "▲",
        "triangular_bullet": "‣",


        "crown": "♕",
        "crown2": "♔",

        "sixty_nine": "♋",

        "dice_one": "Ķ",
        "dice_two": "ķ",
        "dice_three": "ĸ",
        "dice_four": "Ĺ",
        "dice_five": "ĺ",
        "dice_six": "Ļ",

        "triangles_less_than": "⫷",
        "triangles_greater_than": "⫸",

        "hour_glass_horizontal": "⨝",

        "left_line": "⟝",
        "right_line": "⟞",


        # Animals
        "baboon": "𓃷",
        "barbel": "𓆜",
        "bird_pecking_at_fish": "𓅻",
        "bull": "𓃒",
        "bull_charging": "𓃓",
        "buzzard": "𓅂",
        "calf": "𓃔",
        "cat": "𓃠",
        "catfish": "𓆢",
        "cattle_egret": "𓅥",
        "centipede": "𓆨",
        "charging_ox_head": "𓄀",
        "claw": "𓆆",
        "cobra": "𓆓",
        "cobra_with_feather": "𓆔",
        "cormorant": "𓅧",
        "cow_suckling_calf": "𓃖",
        "crocodile": "𓆊",
        "crocodile_with_curved_tail": "𓆌",
        "dog": "𓃡",
        "donkey": "𓃘",
        "duckling": "𓅷",
        "dung_beetle": "𓆣",
        "egg": "𓆇",
        "elephant": "𓃰",
        "elephant_snout_fish": "𓆞",
        "erect_cobra": "𓆗",
        "erect_cobra_on_basket": "𓆘",
        "falcon": "𓅃",
        "falcon_in_boat": "𓅇",
        "falcon_on_basket": "𓅅",
        "falcon_on_collar_of_beads": "𓅉",
        "falcon_on_standard": "𓅆",
        "falcon_with_sun_on_head": "𓅊",
        "falcon_in_Sokar_barque": "𓅋",
        "fish_scale": "𓆠",
        "flamingo": "𓅟",
        "fly": "𓆦",
        "forepart_of_hartebeest": "𓄄",
        "forepart_of_lion": "𓄂",
        "forepart_of_ram": "𓄆",
        "frog": "𓆏",
        "gazelle": "𓃴",
        "gecko": "𓆈",
        "glossy_ibis": "𓅠",
        "goat_with_collar": "𓃶",
        "goose_picking_up_grain": "𓅼",
        "guinea_fowl": "𓅘",
        "hare": "𓃹",
        "hartebeest_head": "𓄃",
        "head_of_crested_bird": "𓆀",
        "head_of_pintail": "𓅿",
        "head_of_ram": "𓄅",
        "head_of_spoonbill": "𓆁",
        "head_of_vulture": "𓆂",
        "heron": "𓅣",
        "heron_on_perch": "𓅤",
        "hippo": "𓃯",
        "hippo_head": "𓄁",
        "hoopoe": "𓅙",
        "horse": "𓃗",
        "horned_viper": "𓆑",
        "horned_viper_crawling_out_of_enclosure": "𓆒",
        "human_headed_bird_with_bowl_with_smoke": "𓅽",
        "ibex": "𓃵",
        "image_of_crocodile": "𓆍",
        "image_of_falcon": "𓅌",
        "image_of_falcon_on_standard": "𓅍",
        "image_of_falcon_with_two_plumes": "𓅏",
        "jackal": "𓃥",
        "jackal_looking_back": "𓃦",
        "kid": "𓃙",
        "kid_jumping": "𓃚",
        "lapwing": "𓅚",
        "lapwing_with_twisted_wings": "𓅛",
        "leopard_head": "𓄇",
        "lion": "𓃬",
        "locust": "𓆧",
        "long_horned_bull": "𓃽",
        "lying_canine": "𓃢",
        "lying_lion": "𓃭",
        "lying_Set_animal": "𓃫",
        "mature_bovine_lying_down": "𓃜",
        "monkey": "𓃸",
        "mullet": "𓆝",
        "newborn_hartebeest": "𓃛",
        "northern_bald_ibis": "𓅜",
        "oryx": "𓃲",
        "ostrich": "𓅦",
        "owl": "𓅓",
        "panther": "𓃮",
        "Petrocephalus_bane": "𓆟",
        "pintail": "𓅭",
        "pintail_alighting": "𓅯",
        "pintail_flying": "𓅮",
        "plucked_bird": "𓅾",
        "quail_chick": "𓅱",
        "ram": "𓃝",
        "sacred_cow": "𓃕",
        "sacred_Ibis": "𓅞",
        "sacred_Ibis_on_standard": "𓅝",
        "saddle_billed_stork": "𓅡",
        "Set_animal": "𓃩",
        "snake": "𓆙",
        "sparrow": "𓅪",
        "sparrow_low": "𓅫",
        "swallow": "𓅨",
        "swallow_low": "𓅩",
        "tadpole": "𓆐",
        "three_ducklings_in_nest": "𓅸",
        "three_ducklings_in_pool": "𓅹",
        "three_saddle_billed_storks": "𓅢",
        "tilapia": "𓆛",
        "turtle": "𓆉",
        "two_cobras": "𓆕",
        "two_Egyptian_vultures": "𓅀",
        "two_owls": "𓅔",
        "two_plovers": "𓅺",
        "two_quail_chicks": "𓅳",
        "vulture": "𓅐",
        "vulture_and_cobra_each_on_a_basket": "𓅒",
        "white_fronted_goose": "𓅬",
        "widgeon": "𓅰",
        "wing": "𓆃",


        # Currency and Finance
        "alarm_clock": "⏰",
        "atm": "🏧",
        "balance_scale": "⚖️",
        "bank": "🏦",
        "banknotes": "💴",
        "binance_coin": "⚡",
        "bitcoin": "₿",
        "calendar": "📅",
        "chart": "📊",
        "chart_decreasing": "📉",
        "chart_increasing": "📈",
        "coin": "🪙",
        "credit_card": "💳",
        "currency_exchange": "💱",
        "currency_signs": "💲",
        "dollar": "$",
        "dollar_coin": "🪙",
        "dollar_wings": "💸",
        "dogecoin": "Ð",
        "deposit": "🏦⬇️",
        "ethereum": "Ξ",
        "euro": "€",
        "fees": "💸",
        "fire": "🔥",
        "gas": "⛽",
        "gift": "🎁",
        "gem": "💎",
        "gemstone": "💎",
        "gold": "🏅",
        "gold_coin": "🪙",
        "gold_medal": "🥇",
        "handshake": "🤝",
        "hacker": "🕵️‍♂️",
        "incoming_money": "📥💵",
        "infinite": "♾️",
        "investment": "📈💵",
        "key": "🔑",
        "ledger": "📒",
        "legal_scales": "⚖️",
        "litecoin": "Ł",
        "lock_with_key": "🔐",
        "medal": "🥇",
        "money_bag": "💰",
        "money_mouth_face": "🤑",
        "money_stack": "💵",
        "money_with_wings": "💸",
        "network": "🌐",
        "nodes": "🔗",
        "outgoing_money": "📤💵",
        "padlock": "🔐",
        "percent": "％",
        "piggy_bank": "🐖",
        "pound": "£",
        "robot_trade": "🤖💹",
        "rocket": "🚀",
        "ruler": "📏",
        "rupee": "₹",
        "safe": "🛡",
        "scales": "⚖️",
        "shield": "🛡",
        "skull": "💀",
        "smart_contract": "📜🤖",
        "stethoscope": "🩺",
        "stopwatch": "⏱",
        "target": "🎯",
        "tether": "₮",
        "trade": "🔄",
        "trading_floor": "🏦",
        "vault": "🏰",
        "wallet": "👛",
        "withdrawal": "🏦⬆️",
        "yen": "¥",



        # Miscellaneous Icons
        "airplane": "✈️",
        "alien": "👽",
        "alien_robot": "",
        "bar_chart": "📊",
        "barrel": "🛢",
        "bicycle": "🚲",
        "books": "📚",
        "camera": "📷",
        "clipboard": "📋",
        "computer": "💻",
        "cross_mark": "❌",
        "crossed_swords": '⚔',
        "database": "🗄",
        "debug": "🪲",
        "desktop_computer": "🖥",
        "email": "✉️",
        "exception": "⚠️",
        "ghost": "ᗣ",
        "keyboard": "⌨️",
        "lambda": "λ",
        "lightning": "⚡",
        "magnifying_glass": "🔍",
        "music_note": "🎵",
        "outbox_tray": "📤",
        "package": "📦",
        "pacman_left": "ᗤ",
        "pacman_right": "ᗧ",
        "pull_request": "🔃",
        "robot": "🤖",
        "robot_face": "🤖",
        "server": "🖧",
        "soccer_ball": "⚽",
        "terminal": "💻",
        "trophy": "🏆",
        "trash": "🗑",
        "watch": "⌚",




        # Symbols
        "check_box": "☑️",
        "check_mark": "✔",
        "exclamation_mark": "❗",
        "fast_forward_button": "⏩",
        "globe": "🌍",
        "lock": "🔒",
        "pause_button": "⏸",
        "play_button": "▶️",
        "question_mark": "❓",
        "rewind_button": "⏪",
        "stop_button": "⏹",
        "thumbs_down": "👎",
        "thumbs_up": "👍",
        "unlock": "🔓",
        "warning": "⚠️",
        "x": "✖",

        # Weather and Nature
        "cloud": "☁️",
        "rain": "🌧",
        "snowflake": "❄️",
        "sun": "☀️",
        "umbrella": "☂️",
}



DEFAULT_CONTROL_MAP: Dict[str, str] = {

        # Terminal Window Title and Icon
        "set_window_title_and_icon": "\x1b]0;{title}\x07",  # Set terminal window title and icon name (OSC 0)
        "set_icon_name": "\x1b]1;{icon}\x07",      # Set terminal icon name (OSC 1)
        "set_window_title": "\x1b]2;{title}\x07",  # Set only the window title of the terminal window (OSC 2)

        # Insert clickable hyperlink
        "insert_hyperlink": "\x1b]8;;{url}\x07{text}\x1b]8;;\x07",

        # Terminal Current Working Directory
        "set_current_directory": "\x1b]7;file://{hostname}/{path}\x07",  # Set terminal current working directory (OSC 2)

        # Terminal Colors
        "set_palette_color": "\x1b]4;{color_code};rgb:{r}/{g}/{b}\x07",  # Set palette color (OSC 4)

        # Terminal Font
        "set_font": "\x1b]10;{font}\x07",  # Set terminal font (OSC 10)

        # Terminal Background Image
        "set_background_image": "\x1b]11;{image_path}\x07",  # Set terminal background image (OSC 11)

        # Clipboard Operations
        "copy_to_clipboard": "\x1b]52;;{content}\x07",  # Copy content to clipboard (OSC 52)

        # X11 Window Class and Instance
        "set_x11_window_class": "\x1b]3;{instance};{class}\x07",  # Set X11 window class and instance (OSC 3)

        # 256 Color Mode (Foreground)
        "fg_color_256": "\x1b[38;5;{n}m",  # Set 256 color mode foreground (0-255)

        # 256 Color Mode (Background)
        "bg_color_256": "\x1b[48;5;{n}m",  # Set 256 color mode background (0-255)

        # True Color Mode (Foreground)
        "fg_truecolor": "\x1b[38;2;{r};{g};{b}m",  # Set true color mode foreground (RGB)

        # True Color Mode (Background)
        "bg_truecolor": "\x1b[48;2;{r};{g};{b}m",  # Set true color mode background (RGB)

        # Buffer Control
        "alt_buffer": "\x1b[?1049h",
        "normal_buffer": "\x1b[?1049l",
        "alt_buffer_no_save": "\x1b[?47h",  # Switch to alternate buffer without saving the cursor
        "normal_buffer_no_save": "\x1b[?47l",  # Switch back to normal buffer without restoring the cursor

        # Screen Clearing
        "clear_screen": "\x1b[2J",  # Clear the entire screen
        "clear_screen_from_cursor": "\x1b[0J",  # Clear screen from the cursor down
        "clear_screen_to_cursor": "\x1b[1J",  # Clear screen from the cursor up

        # Line Clearing
        "clear_line": "\x1b[2K",  # Clear the entire current line
        "clear_line_from_cursor": "\x1b[0K",  # Clear from the cursor to the end of the line
        "clear_line_to_cursor": "\x1b[1K",  # Clear from the beginning of the line to the cursor

        # Cursor Movement
        "cursor_home": "\x1b[H",  # Move cursor to the home position (top-left corner)
        "cursor_position": "\x1b[{row};{col}H",  # Move cursor to specified row and column
        "cursor_up": "\x1b[{n}A",  # Move cursor up by n rows
        "cursor_down": "\x1b[{n}B",  # Move cursor down by n rows
        "cursor_right": "\x1b[{n}C",  # Move cursor forward (right) by n columns
        "cursor_left": "\x1b[{n}D",  # Move cursor backward (left) by n columns
        "save_cursor_position": "\x1b[s",  # Save the current cursor position
        "restore_cursor_position": "\x1b[u",  # Restore saved cursor position
        "hide_cursor": "\x1b[?25l",  # Hide the cursor
        "show_cursor": "\x1b[?25h",  # Show the cursor


        # Line and Text Manipulation
        "insert_line": "\x1b[L",  # Insert a blank line at the current cursor position
        "delete_line": "\x1b[M",  # Delete the current line
        "scroll_up": "\x1b[S",  # Scroll the page up
        "scroll_down": "\x1b[T",  # Scroll the page down

        # Mouse Control (Enable or disable mouse reporting)
        "enable_mouse": "\x1b[?1000h",  # Enable basic mouse tracking (xterm-style)
        "disable_mouse": "\x1b[?1000l",  # Disable mouse tracking
        'enable_sgr_mouse': "\x1b[?1006h",  # Enable SGR mouse mode
        "disable_sgr_mouse": "\x1b[?1006l", # Disable SGR mouse mode
        "enable_mouse_button_event_tracking": "\x1b[?1002h",  # Enable mouse button event tracking
        "disable_mouse_button_event_tracking": "\x1b[?1002l",  # Disable mouse button event tracking

        # Miscellaneous
        "bell": "\007",  # Bell (beep sound)
        "enable_application_keypad": "\x1b[?1h",  # Enable application keypad mode (for arrow keys, etc.)
        "disable_application_keypad": "\x1b[?1l",  # Disable application keypad mode

        # Key Codes (Special Keys)
        "arrow_up": "\x1b[A",  # Up arrow key
        "arrow_down": "\x1b[B",  # Down arrow key
        "arrow_right": "\x1b[C",  # Right arrow key
        "arrow_left": "\x1b[D",  # Left arrow key

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

        # Tab Keys
        "tab": "\t",                 # Tab key
        "vtab": "\v",                # Vertical Tab key

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


DEFAULT_BYTE_MAP = {
    # Mouse Event Parsing
    "mouse_event_start": b"<",                 # Start of mouse event
    "mouse_event_end_press": b"M",             # End of mouse press event
    "mouse_event_end_release": b"m",           # End of mouse release event
    "mouse_drag_start": b"\x1b[<32;",          # Dragging mouse event start
    "mouse_drag_end": b"\x1b[<35;",            # Dragging mouse event end
    "mouse_scroll_up": b"\x1b[<64;",           # Mouse scroll up
    "mouse_scroll_down": b"\x1b[<65;",         # Mouse scroll down

    # Meta and Escape Keys
    "escape_key": b"\x1b",                     # Escape key
    "meta": b"\x1b",                           # Meta key (Alt or Esc)


    # Bracketed Paste Mode
    "paste_start": b"\x1b[200~",               # Start of pasted text
    "paste_end": b"\x1b[201~",                 # End of pasted text

    # Keyboard Events
    "alt_key_prefix": b"\x1b",                 # Alt key prefix (used for combinations)
    "ctrl_space": b"\x00",                     # Ctrl + Space
    "ctrl_enter": b"\n",                       # Ctrl + Enter (newline)
    "ctrl_tab": b"\t",                         # Ctrl + Tab
    "shift_tab": b"\x1b[Z",                    # Shift + Tab
    "fn_key_prefix": b"\x1bO",                 # Function key prefix (varies by terminal)
    "ctrl_escape": b"\x1b\x1b",                # Ctrl + Esc (double escape)
    "ctrl_backspace": b"\x1b\x7f",             # Ctrl + Backspace
    "backspace": b"\x08",                      # Standard Backspace
    "delete": b"\x1b[3~",                      # Delete key

    # Function Keys (Common Variants)
    "f1": b"\x1bOP",                           # F1 key
    "f2": b"\x1bOQ",                           # F2 key
    "f3": b"\x1bOR",                           # F3 key
    "f4": b"\x1bOS",                           # F4 key
    "f5": b"\x1b[15~",                         # F5 key
    "f6": b"\x1b[17~",                         # F6 key
    "f7": b"\x1b[18~",                         # F7 key
    "f8": b"\x1b[19~",                         # F8 key
    "f9": b"\x1b[20~",                         # F9 key
    "f10": b"\x1b[21~",                        # F10 key
    "f11": b"\x1b[23~",                        # F11 key
    "f12": b"\x1b[24~",                        # F12 key


    # CSI Sequences (Control Sequence Introducer)
    "cursor_up": b"\x1b[A",                    # Cursor up
    "cursor_down": b"\x1b[B",                  # Cursor down
    "cursor_right": b"\x1b[C",                 # Cursor right
    "cursor_left": b"\x1b[D",                  # Cursor left
    "cursor_home": b"\x1b[H",                  # Home key
    "cursor_end": b"\x1b[F",                   # End key
    "cursor_position_report_start": b"\x1b[6n", # Start of cursor position report
    "window_resize_report": b"\x1b[8;",         # Resize report
    "focus_in": b"\x1b[I",                      # Focus in event
    "focus_out": b"\x1b[O",                     # Focus out event
    "application_mode_start": b"\x1b[=",        # Application keypad mode input
    "normal_mode_start": b"\x1b[>",             # Normal keypad mode input

    # Extended Keypad Sequences
    "keypad_0": b"\x1bOp",                     # Keypad 0
    "keypad_1": b"\x1bOq",                     # Keypad 1
    "keypad_2": b"\x1bOr",                     # Keypad 2
    "keypad_3": b"\x1bOs",                     # Keypad 3
    "keypad_4": b"\x1bOt",                     # Keypad 4
    "keypad_5": b"\x1bOu",                     # Keypad 5
    "keypad_6": b"\x1bOv",                     # Keypad 6
    "keypad_7": b"\x1bOw",                     # Keypad 7
    "keypad_8": b"\x1bOx",                     # Keypad 8
    "keypad_9": b"\x1bOy",                     # Keypad 9
    "keypad_period": b"\x1bOn",                # Keypad period
    "keypad_enter": b"\x1bOM",                 # Keypad Enter

    # Terminal Reporting
    "terminal_ready_report": b"\x1b[>0;0;0c",  # Terminal ready (DA report)
    "device_status_report": b"\x1b[5n",        # Device status report (is terminal ready)
    "cursor_save": b"\x1b[s",                  # Save cursor position (parse this as input acknowledgment)
    "cursor_restore": b"\x1b[u",               # Restore cursor position (input acknowledgment)
    "bell_detected": b"\x07",                  # Bell detected in input stream


    # XTerm-Specific Events
    "window_focus_in": b"\x1b[I",              # Window focus in
    "window_focus_out": b"\x1b[O",             # Window focus out
    "title_set": b"\x1b]2;",                   # Title set (partial, often seen during pasting)
    "title_end": b"\x07",                      # End of title set event
    "hyperlink_start": b"\x1b]8;;",            # Hyperlink detection start
    "hyperlink_end": b"\x1b]8;;\a",            # Hyperlink detection end

    # Private Mode Changes
    "mouse_reporting_enabled": b"\x1b[?1000h",  # Mouse reporting enabled acknowledgment
    "mouse_reporting_disabled": b"\x1b[?1000l",  # Mouse reporting disabled acknowledgment
    "sgr_mouse_reporting_enabled": b"\x1b[?1006h",  # SGR mouse reporting enabled acknowledgment
    "sgr_mouse_reporting_disabled": b"\x1b[?1006l",  # SGR mouse reporting disabled acknowledgment

    # Application Keypad Parsing
    "app_keypad_start": b"\x1b=",              # Application keypad start
    "app_keypad_end": b"\x1b>",                # Application keypad end
    "app_cursor_keys_enabled": b"\x1b[?1h",    # Application cursor keys enabled
    "app_cursor_keys_disabled": b"\x1b[?1l",   # Application cursor keys disabled

    # ANSI Special Characters
    "null_char": b"\x00",                      # Null character
    "start_of_header": b"\x01",                # Start of header
    "start_of_text": b"\x02",                  # Start of text
    "end_of_text": b"\x03",                    # End of text
    "end_of_transmission": b"\x04",            # End of transmission
    "cancel": b"\x18",                         # Cancel (Ctrl + X)
    "escape_seq_start": b"\x1b[",              # Start of escape sequence (general)

    # Miscellaneous Input Parsing
    "unknown_event_start": b"\x1b[?",          # Start of unknown private mode toggle
    "invalid_escape_sequence": b"\x1b[999",    # Invalid or incomplete escape sequence
    "newline_detected": b"\n",                 # Newline detected
    "carriage_return_detected": b"\r",         # Carriage return detected
    "control_char_ignored": b"\x1f",           # Common ignored control character in parsing streams
}












