# prints_charming.regex_patterns.ansi_patterns.py

import re


"""
This module defines regex patterns for matching ANSI escape sequences.

These patterns are integral to the `PrintsCharming` library, enabling advanced
text styling and processing of terminal output. The patterns are designed to
handle a wide range of ANSI sequences, including SGR (Select Graphic Rendition),
CSI (Control Sequence Introducer), OSC (Operating System Command), and more.

Use Cases:
- Removing, escaping, or parsing ANSI codes in terminal output.
- Enhancing the `PrintsCharming` library's ability to style and format console
  text with precision.

For comprehensive usage, see the `PrintsCharming` class in `prints_charming.py`.
"""



ANSI_ALL_PATTERN = re.compile(
    r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\][^\x07]*\x07)'
)
"""
Matches any ANSI escape sequences.

Starts with:
- ESC character (\x1b)

Contains:
- Single-character sequences: any character from '@' to '_', including 
  backslash '\\' and hyphen '-'.
- CSI sequences: '[' followed by optional parameter bytes ([0-?]*), 
  optional intermediate bytes ([ -/]*), and a final byte in the range [@-~].
- OSC sequences: ']' followed by any characters not including BEL (\x07), 
  ending with BEL.

Ends with:
- Single-character sequences: character from '@' to '_'.
- CSI sequences: final byte in the range '@' to '~'.
- OSC sequences: BEL character (\x07).

**Example matches beyond previous levels:**
- '\x1b]0;Title\x07' (Set window title)
- '\x1b[P' (Device Control String)

Use cases:
- Removing all types of ANSI escape sequences from text.
- Parsing and interpreting any ANSI escape code.
"""


ANSI_ALL_NON_OSC_PATTERN = re.compile(
    r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
)
"""
Matches any ANSI escape sequences excluding OSC (Operating System Command) 
sequences.

Starts with:
- ESC character (\x1b).

Contains:
- Single-character sequences: a single character from '@' to '_', including 
  backslash '\\' and hyphen '-'.
- CSI (Control Sequence Introducer) sequences: '[' followed by optional 
  parameter bytes ([0-?]*), optional intermediate bytes ([ -/]*), and a 
  final byte in the range '@' to '~'.

Does not match:
- OSC sequences (which start with ']' and end with BEL (\x07)).

**Example matches beyond previous levels:**
- '\x1b[D' (Move cursor left, single-character).
- '\x1b[1;31m' (Set text attributes, CSI).
- '\x1b[2J' (Clear screen, CSI).

Use cases:
- Parsing or interpreting most ANSI escape sequences except OSC.
- Simplifying text processing when OSC sequences are irrelevant.
"""


ANSI_CSI_PATTERN = re.compile(
    r'\x1b\[[0-?]*[ -/]*[@-~]'
)
"""
Matches ANSI CSI (Control Sequence Introducer) sequences.

Starts with:
- ESC character (\x1b) followed by '['

Contains:
- Optional parameter bytes: digits, semicolons, or '?'.
- Optional intermediate bytes: characters from ' ' (space) to '/'.
- Final byte: any character from '@' to '~'.

Ends with:
- Final byte in the range '@' to '~'.

Does Not Match:
- Single-character ANSI sequences (e.g., \x1b[D).
- OSC sequences (e.g., \x1b]0;Title\x07).

**Example matches beyond previous levels:**
- '\x1b[1;31;40m' (Set text attributes)
- '\x1b[0c' (Device Attributes request)
- '\x1b[2J' (Clear Screen)

Use cases:
- Parsing standard CSI sequences like cursor movement, styling, and screen 
  clearing, including non-alphabetic final bytes.
- Implementing terminal control functions.
"""


ANSI_CORE_PATTERN = re.compile(
    r'\x1b\[[0-9;]*[a-zA-Z]'
)
"""
Matches core ANSI escape sequences commonly used for text styling, cursor 
movement, and screen manipulation.

Starts with:
- ESC character (\x1b) followed by '['

Contains:
- Optional numeric parameters separated by semicolons.

Ends with:
- An alphabetic character (a-z or A-Z).

Does Not Match:
- CSI sequences with non-alphabetic final bytes (e.g., @, [, or ~).
- Single-character ANSI sequences (e.g., \x1b[D).
- OSC sequences (e.g., \x1b]0;Title\x07).

**Example matches beyond previous levels:**
- '\x1b[12;24r' (Set scrolling region)
- '\x1b[5n' (Device status report)

Use cases:
- Handling CSI sequences with alphabetic final bytes.
- Filtering out sequences that use non-standard characters.
"""


ANSI_SGR_OR_ERASE = re.compile(
    r'\x1b\[[0-9;]*[mK]'
)
"""
Matches ANSI CSI sequences ending with 'm' or 'K'.

Starts with:
- ESC character (\x1b) followed by '['

Contains:
- Optional numeric parameters separated by semicolons.

Ends with:
- Either 'm' or 'K'.

Example matches beyond previous levels:
- '\x1b[K' (Erase to end of line)
- '\x1b[1;2K' (Erase line with parameters)

Use cases:
- Specifically targeting text formatting and line modification sequences.
- Simplifying parsing when only 'm' or 'K' sequences are relevant.
- Handling both SGR styling and line clearing commands in terminal outputs.
"""


ANSI_SGR_LOOSE_PATTERN = re.compile(
    r'\x1b\[[0-9;]*m'
)
"""
Matches ANSI SGR sequences with optional numeric parameters.

Starts with:
- ESC character (\x1b) followed by '['

Contains:
- Optional numeric parameters separated by semicolons.

Ends with:
- 'm' character.

Example matches beyond previous levels:
- '\x1b[m' (Shorthand Reset all attributes or no params)

Use cases:
- Parsing or removing text styling codes.
- Applying text attributes in terminal applications.
"""


ANSI_SGR_STRICT_PATTERN = re.compile(
    r'\x1b\[([0-9]+)(;[0-9]+)*m'
)
"""
Matches ANSI SGR sequences with at least one numeric parameter.

Starts with:
- ESC character (\x1b) followed by '['

Contains:
- One or more numeric parameters separated by semicolons.

Ends with:
- 'm' character.

Example matches beyond previous levels:
- '\x1b[31m' (red text)
- '\x1b[1;4m' (bold and underlined text).
- '\x1b[38;5;231m' (256-color foreground).
- '\x1b[38;2;24;28;33m' (TrueColor foreground).

Use cases:
- Parsing or stripping SGR codes for color or style in text output.
- Useful in strict parsing scenarios where at least one parameter is 
  required. 
"""


ANSI_SINGLE_CHAR_PATTERN = re.compile(
    r'\x1b[@-Z\\-_]'
)
"""
Matches ANSI single-character escape sequences that do not use parameters
or CSI sequences.

Starts with:
- ESC character (\x1b)

Contains:
- A single character from '@' to '_', including backslash '\\' and hyphen '-'.

Ends with:
- The single character after ESC.

**Example matches beyond previous levels:**
- '\x1b=' (Set alternate keypad mode)
- '\x1b>' (Set numeric keypad mode)
- '\x1b[D' (cursor left).
- '\x1b[M' (scroll up).

Use cases:
- Processing simple, single-character control sequences.
- Specifically for simple ANSI escape sequences used for terminal control, 
  like keyboard inputs or mode toggles.
"""


ANSI_HYPERLINK_PATTERN = re.compile(
    r'\x1b]8;;([^\x07]*)\x07(.*?)\x1b]8;;\x07'
)
"""
Matches ANSI hyperlinks.

Examples:
- '\x1b]8;;https://github.com/deefifofun/prints_charming\x07Click Here\x1b]8;;\x07'
"""



# Grouping ANSI patterns
ansi_escape_patterns = {
    "all": ANSI_ALL_PATTERN,  # Sequences, including OSC.
    "all_non_osc": ANSI_ALL_NON_OSC_PATTERN,  # Sequences excluding OSC.
    "csi": ANSI_CSI_PATTERN,  # CSI sequences (cursor movement, styling).
    "core": ANSI_CORE_PATTERN,  # Sequences with alphabetic final bytes.
    "sgr_mk": ANSI_SGR_OR_ERASE,  # SGR sequences ending in 'm' or 'K'.
    "sgr_loose": ANSI_SGR_LOOSE_PATTERN,  # SGR sequences, with optional params.
    "sgr_strict": ANSI_SGR_STRICT_PATTERN,  # SGR sequences requiring numeric params.
    "single_char": ANSI_SINGLE_CHAR_PATTERN,  # Single-character sequences (no params).
    "hyperlinks": ANSI_HYPERLINK_PATTERN,  # OSC 8 hyperlinks with URL and display text.
}


