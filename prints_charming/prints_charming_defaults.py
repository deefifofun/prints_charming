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
        "header2" : PStyle(color="cyan", bold=True),
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

        "conceal": PStyle(conceal=True)
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

unicode_blocks = {
        "square": "■",
        "large_square": "⬛",
        "large_hollow_square": "⬜",
        "small_square": "▪",
        "small_hollow_square": "▫",
        "rectangle": "▮",
        "parallelogram": "▰",
        "full_block": "█",
        "seven_eighths_block": "▇",
        "three_quarters_block": "▆",
        "five_eighths_block": "▅",
        "half_block": "▄",
        "three_eighths_block": "▃",
        "quarter_block": "▂",
        "one_eighth_block": "▁",
        "left_seven_eighths_block": "▉",
        "left_three_quarters_block": "▊",
        "left_five_eighths_block": "▋",
        "left_half_block": "▌",
        "left_three_eighths_block": "▍",
        "left_quarter_block": "▎",
        "left_one_eighth_block": "▏",
        "light_shade": "░",
        "medium_shade": "▒",
        "dark_shade": "▓",
        "hollow_square": "□",
        "hollow_rectangle": "▭",
        "rounded_square": "▢",
        "hollow_vert_rectangle": "▯",
        "top_left_corner": "┌",
        "top_right_corner": "┐",
        "bottom_left_corner": "└",
        "bottom_right_corner": "┘",
        "horizontal_line": "─",
        "vertical_line": "│",
        "double_top_left_corner": "╔",
        "double_top_right_corner": "╗",
        "double_bottom_left_corner": "╚",
        "double_bottom_right_corner": "╝",
        "double_horizontal_line": "═",
        "double_vertical_line": "║",
        "cross": "┼",
        "top_t": "┬",
        "bottom_t": "┴",
        "left_t": "├",
        "right_t": "┤",
        "circle": "●",  # Black circle
        "hollow_circle": "◯",  # White circle
        "bullet": "•",  # Bullet point
        "triangular_bullet": "‣",  # Triangular bullet
        "diamond": "◆",  # Black diamond
        "hollow_diamond": "◇",  # White diamond
        "triangle_up": "▲",  # Black up-pointing triangle
        "triangle_down": "▼",  # Black down-pointing triangle
        "triangle_left": "◀",  # Black left-pointing triangle
        "triangle_right": "▶",  # Black right-pointing triangle
        "medium_block": "▄",  # Lower half block (larger block for visual effects)
        "upper_half_block": "▀",  # Upper half block
        "quad_block": "▖",  # Quadrant lower left
        "three_quadrant_block": "▞",  # Quadrant upper right and lower left
        "left_block": "▕",  # Left half block (vertical)
        "right_block": "▏",  # Right half block (vertical)
        "vertical_light_double_dash": "╎",  # Light vertical double dash
        "horizontal_light_double_dash": "╌",  # Light horizontal double dash
        "vertical_heavy_double_dash": "╏",  # Heavy vertical double dash
        "horizontal_heavy_double_dash": "╍",  # Heavy horizontal double dash
        "vertical_light_triple_dash": "┆",  # Light vertical triple dash
        "horizontal_light_triple_dash": "┄",  # Light horizontal triple dash
        "check_mark": "✔",  # Check mark
        "multiplication_sign": "✖",  # Multiplication sign (cross)
        "star": "★",  # Black star
        "hollow_star": "☆",  # White star
        "thumbs_up": "👍",
        "thumbs_down": "👎",
        "warning": "⚠️",
        "question_mark": "❓",
        "exclamation_mark": "❗",
        "lock": "🔒",
        "unlock": "🔓",
        "globe": "🌍",
        "check_box": "☑️",
        "play_button": "▶️",
        "pause_button": "⏸",
        "stop_button": "⏹",
        "rewind_button": "⏪",
        "fast_forward_button": "⏩",
        "sun": "☀️",
        "cloud": "☁️",
        "rain": "🌧",
        "snowflake": "❄️",
        "umbrella": "☂️",
        "coffee": "☕",
        "trophy": "🏆",
        "hourglass": "⌛",
        "watch": "⌚",
        "computer": "💻",
        "email": "✉️",
        "camera": "📷",
        "music_note": "🎵",
        "soccer_ball": "⚽",
        "bicycle": "🚲",
        "airplane": "✈️",
        "flag": "🏳️",
        "alien": "👽",
        "robot": "🤖",
        "trash": "🗑",
        "keyboard": "⌨️",  # Keyboard
        "desktop_computer": "🖥",  # Desktop
        "server": "🖧",  # Network icon (symbolizes servers)
        "database": "🗄",  # Filing cabinet, can represent a database
        "magnifying_glass": "🔍",  # Searching (for issues in code or debugging)
        "lightning": "⚡",  # Speed, performance boost
        "books": "📚",  # Documentation or learning materials
        "cross_mark": "❌",  # Failure, failed test
        "package": "📦",  # Package (Python package or module)
        "outbox_tray": "📤",  # Output
        "inbox_tray": "📥",  # Input
        "shield": "🛡",  # Security, protection (firewall)
        "clipboard": "📋",  # Copy-pasting code, task management
        "debug": "🪲",  # Debugging
        "exception": "⚠️",  # Error or exception handling
        "lambda": "λ",  # Lambda function in Python
        "pull_request": "🔃",  # Pull request or version control actions
        "terminal": "💻",  # Command line interface (CLI)
        "bar_chart": "📊",  # Data analytics, machine learning
        "robot_face": "🤖",  # Machine learning, AI
        "barrel": "🛢",  # Docker (containerization)
        "dollar": "$",  # Dollar sign (USD)
        "euro": "€",  # Euro sign (EUR)
        "yen": "¥",  # Yen sign (JPY)
        "pound": "£",  # Pound sign (GBP)
        "rupee": "₹",  # Indian Rupee (INR)
        "bitcoin": "₿",  # Bitcoin symbol
        "ethereum": "Ξ",  # Ethereum symbol
        "litecoin": "Ł",  # Litecoin symbol
        "monero": "ɱ",  # Monero symbol
        "dogecoin": "Ð",  # Dogecoin symbol
        "tether": "₮",  # Tether symbol
        "binance_coin": "⚡",  # Binance Coin symbol (⚡ as a stand-in)
        "currency_exchange": "💱",  # Currency exchange
        "money_bag": "💰",  # Money bag (for wealth)
        "bank": "🏦",  # Bank or financial institution
        "credit_card": "💳",  # Credit card
        "coin": "🪙",  # Coin (represents cryptocurrency or tokens)
        "chart_increasing": "📈",  # Increasing chart (bull market, profit)
        "chart_decreasing": "📉",  # Decreasing chart (bear market, loss)
        "money_with_wings": "💸",  # Money flying away (loss, fees)
        "money_stack": "💵",  # Stack of dollar bills
        "dollar_coin": "🪙",  # Coin (could symbolize any currency)
        "balance_scale": "⚖️",  # Balance scale (fairness, arbitrage)
        "alarm_clock": "⏰",  # Time-sensitive trading
        "rocket": "🚀",  # Rocket (market surge)
        "banknotes": "💴",  # Banknotes (JPY for diversity)
        "currency_signs": "💲",  # Currency signs (generic currency)
        "gold": "🏅",  # Gold (store of value)
        "piggy_bank": "🐖",  # Piggy bank (savings)
        "lock_with_key": "🔐",  # Security (cold storage, wallet protection)
        "ledger": "📒",  # Ledger (bookkeeping, transactions)
        "handshake": "🤝",  # Agreement or trade deal
        "deposit": "🏦⬇️",  # Deposit (bank or account)
        "withdrawal": "🏦⬆️",  # Withdrawal (from bank or account)
        "smart_contract": "📜🤖",  # Smart contract (📜 scroll + 🤖 robot)
        "network": "🌐",  # Network (blockchain or decentralized)
        "key": "🔑",  # Private key, access
        "wallet": "👛",  # Crypto wallet
        "vault": "🏰",  # Vault or secure storage
        "gem": "💎",  # Gem (valuable asset or token)
        "safe": "🛡",  # Safe (protection, cold storage)
        "stopwatch": "⏱",  # Speed (fast transaction)
        "scales": "⚖️",  # Arbitration or DeFi balance
        "incoming_money": "📥💵",  # Incoming payments or deposits
        "outgoing_money": "📤💵",  # Outgoing payments or transfers
        "investment": "📈💵",  # Investment or profits
        "fees": "💸",  # Transaction fees
        "atm": "🏧",  # ATM (fiat withdrawal or deposit)
        "gas": "⛽",  # Gas fees (Ethereum or blockchain transaction fees)
        "stethoscope": "🩺",  # Audit (smart contract auditing)
        "nodes": "🔗",  # Nodes in a decentralized network
        "chart": "📊",  # Financial chart or statistics
        "padlock": "🔐",  # Locked contract or token
        "crossed_swords": "⚔️",  # Competition or trading conflict
        "dollar_wings": "💸",  # Money going out (expenses or trading losses)
        "calendar": "📅",  # Deadline for trading or settlement
        "target": "🎯",  # Price target or investment goal
        "medal": "🥇",  # High-value investment or top position
        "infinite": "♾️",  # Infinite supply (inflationary currency)
        "percent": "％",  # Percentage return or interest
        "trading_floor": "🏦",  # Stock exchange or trading platform
        "ruler": "📏",  # Measuring market performance
        "legal_scales": "⚖️",  # Regulation, legal audits
        "trade": "🔄",  # Trade or transaction
        "gift": "🎁",  # Reward, staking rewards, or bonuses
        "robot_trade": "🤖💹",  # Algorithmic trading (bot trading)
        "hacker": "🕵️‍♂️",  # Hacker (security or vulnerabilities)
        "gold_coin": "🪙",  # Cryptocurrency or tokens
        "gold_medal": "🥇",  # High-value investment
        "money_mouth_face": "🤑",  # Excited about profits or returns
        "skull": "💀",  # Failed investment or crash
        "fire": "🔥",  # Hot market or burning tokens (deflationary supply)
        "gemstone": "💎",  # High-value asset or hard-to-obtain token
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











