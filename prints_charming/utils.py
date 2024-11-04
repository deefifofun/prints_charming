import os
import sys
import math
import tty
import termios



def get_key():
    """Captures a single key press, including multi-byte sequences for arrow keys."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == '\x1b':  # Escape sequence (for special keys like arrows)
            key += sys.stdin.read(2)  # Read the next 2 characters (e.g., [A for up arrow)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key


# Function to get the foreground ANSI escape sequence, including reset handling
def get_ansi_256_fg_color_code(code: int) -> str:
    if code == 0:
        return "\033[0m"  # Reset/default color
    return f"\033[38;5;{code}m"


# Function to get the background ANSI escape sequence
def get_ansi_256_bg_color_code(code: int) -> str:
    return f"\033[48;5;{code}m"



def compute_bg_color_map(code):
    return code.replace('[38', '[48')  # Change to background color for 256-color codes


def ansi_to_rgb(index: int) -> tuple:
    """Convert an ANSI 256 color index to an RGB tuple."""
    if 0 <= index <= 15:
        # Convert standard color hex to RGB
        hex_color = STANDARD_COLORS.get(index, "#000000")
        return hex_to_rgb(hex_color)
    elif 16 <= index <= 231:
        # Convert color cube to RGB
        return color_cube_to_rgb(index)
    elif 232 <= index <= 255:
        # Convert grayscale to RGB
        return grayscale_to_rgb(index)
    else:
        raise ValueError(f"Invalid ANSI 256 color index: {index}")


def rgb_to_ansi256(r, g, b):
    """Convert an RGB value to the closest ANSI 256 color."""
    # Standard colors first
    closest_index = None
    closest_distance = float('inf')

    # Check standard ANSI colors (0-15)
    for index, hex_color in STANDARD_COLORS.items():
        sr, sg, sb = hex_to_rgb(hex_color)
        distance = math.sqrt((r - sr) ** 2 + (g - sg) ** 2 + (b - sb) ** 2)
        if distance < closest_distance:
            closest_distance = distance
            closest_index = index

    # Check color cube (16-231)
    for index in range(16, 232):
        sr, sg, sb = color_cube_to_rgb(index)
        distance = math.sqrt((r - sr) ** 2 + (g - sg) ** 2 + (b - sb) ** 2)
        if distance < closest_distance:
            closest_distance = distance
            closest_index = index

    # Check grayscale ramp (232-255)
    for index in range(232, 256):
        sr, sg, sb = grayscale_to_rgb(index)
        distance = math.sqrt((r - sr) ** 2 + (g - sg) ** 2 + (b - sb) ** 2)
        if distance < closest_distance:
            closest_distance = distance
            closest_index = index

    return closest_index


def rgb_to_truecolor_fg(r, g, b) -> str:
    """Generate an ANSI escape code for a 24-bit (true color) foreground."""
    return f"\033[38;2;{r};{g};{b}m"


def rgb_to_truecolor_bg(r, g, b) -> str:
    """Generate an ANSI escape code for a 24-bit (true color) background."""
    return f"\033[48;2;{r};{g};{b}m"


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


def ansi_to_css_style(index_fg: int, index_bg: int = None) -> str:
    """Convert ANSI 256 color indexes to a CSS style string for foreground and background."""
    rgb_fg = ansi_to_rgb(index_fg)
    style = f"color: rgb({rgb_fg[0]}, {rgb_fg[1]}, {rgb_fg[2]});"

    if index_bg is not None:
        rgb_bg = ansi_to_rgb(index_bg)
        style += f" background-color: rgb({rgb_bg[0]}, {rgb_bg[1]}, {rgb_bg[2]});"

    return style


def rgb_to_css_style(r_fg, g_fg, b_fg, r_bg=None, g_bg=None, b_bg=None) -> str:
    """Generate CSS style string for both RGB foreground and background."""
    style = f'color: rgb({r_fg}, {g_fg}, {b_fg});'

    if r_bg is not None and g_bg is not None and b_bg is not None:
        style += f' background-color: rgb({r_bg}, {g_bg}, {b_bg});'

    return style


def ansi_to_html(index_fg: int, index_bg: int = None) -> str:
    """Convert ANSI 256 color indexes to an HTML span with both foreground and background colors."""
    rgb_fg = ansi_to_rgb(index_fg)
    style = f"color: rgb({rgb_fg[0]}, {rgb_fg[1]}, {rgb_fg[2]});"

    if index_bg is not None:
        rgb_bg = ansi_to_rgb(index_bg)
        style += f" background-color: rgb({rgb_bg[0]}, {rgb_bg[1]}, {rgb_bg[2]});"

    return f'<span style="{style}">'


def rgb_to_html(r_fg, g_fg, b_fg, r_bg=None, g_bg=None, b_bg=None) -> str:
    """Generate HTML inline style for both RGB foreground and background."""
    style = f'color: rgb({r_fg}, {g_fg}, {b_fg});'

    if r_bg is not None and g_bg is not None and b_bg is not None:
        style += f' background-color: rgb({r_bg}, {g_bg}, {b_bg});'

    return f'<span style="{style}">'


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_color_code(color, format: str = 'ansi', is_bg: bool = False) -> str:
    """
    General-purpose function to return color codes for ANSI, HTML, CSS, hex, etc.
    :param color: ANSI 256 index, RGB tuple, or hex string.
    :param format: Desired output format: 'ansi', 'html', 'css', 'truecolor', 'hex'
    :param is_bg: True for background color, False for foreground.
    :return: The appropriate escape code or HTML string.
    """
    if isinstance(color, str) and color.startswith('#'):
        # It's a hex color, convert to RGB
        r, g, b = hex_to_rgb(color)
    elif isinstance(color, tuple) and len(color) == 3:
        # It's already an RGB tuple
        r, g, b = color
    elif isinstance(color, int):
        # It's an ANSI index, convert to RGB
        r, g, b = ansi_to_rgb(color)
    else:
        raise ValueError("Invalid color format. Must be ANSI index, hex string, or RGB tuple.")

    if format == 'ansi':
        ansi_code = rgb_to_ansi256(r, g, b)
        if is_bg:
            return get_ansi_256_bg_color_code(ansi_code)
        return get_ansi_256_fg_color_code(ansi_code)
    elif format == 'truecolor':
        if is_bg:
            return rgb_to_truecolor_bg(r, g, b)
        return rgb_to_truecolor_fg(r, g, b)
    elif format == 'html' or format == 'css':
        return rgb_to_html(r, g, b, is_bg)
    elif format == 'hex':
        return rgb_to_hex(r, g, b)  # Return hex directly
    else:
        raise ValueError(f"Unsupported format: {format}")


def grayscale_to_rgb(index):
    gray_value = 8 + (index - 232) * 10
    return gray_value, gray_value, gray_value


def color_cube_to_rgb(index):
    index -= 16  # Offset into the color cube
    r = (index // 36) % 6 * 51  # Red component
    g = (index // 6) % 6 * 51   # Green component
    b = index % 6 * 51          # Blue component
    return r, g, b


STANDARD_COLORS = {
    0:  "#000000",  # black
    1:  "#800000",  # red
    2:  "#008000",  # green
    3:  "#808000",  # yellow
    4:  "#000080",  # blue
    5:  "#800080",  # magenta
    6:  "#008080",  # cyan
    7:  "#c0c0c0",  # white (light gray)
    8:  "#808080",  # bright black (gray)
    9:  "#ff0000",  # bright red
    10: "#00ff00",  # bright green
    11: "#ffff00",  # bright yellow
    12: "#0000ff",  # bright blue
    13: "#ff00ff",  # bright magenta
    14: "#00ffff",  # bright cyan
    15: "#ffffff",  # bright white
}


def ansi_to_hex(index: int) -> str:
    if 0 <= index <= 15:
        # Standard colors
        return STANDARD_COLORS.get(index, "#000000")
    elif 16 <= index <= 231:
        # Color cube
        r, g, b = color_cube_to_rgb(index)
        return rgb_to_hex(r, g, b)
    elif 232 <= index <= 255:
        # Grayscale ramp
        r, g, b = grayscale_to_rgb(index)
        return rgb_to_hex(r, g, b)
    else:
        raise ValueError(f"Invalid ANSI 256 color index: {index}")


def adjust_rgb_brightness(r, g, b, factor: float):
    """Adjust the brightness of an RGB color. Factor < 1 makes it darker, > 1 makes it lighter."""
    r = min(max(0, int(r * factor)), 255)
    g = min(max(0, int(g * factor)), 255)
    b = min(max(0, int(b * factor)), 255)
    return r, g, b


def calculate_rgb_contrast_ratio(fg_rgb, bg_rgb):
    """Calculate contrast ratio between foreground and background using the luminance formula."""
    fg_luminance = (0.2126 * fg_rgb[0] + 0.7152 * fg_rgb[1] + 0.0722 * fg_rgb[2]) / 255
    bg_luminance = (0.2126 * bg_rgb[0] + 0.7152 * bg_rgb[1] + 0.0722 * bg_rgb[2]) / 255
    return (fg_luminance + 0.05) / (bg_luminance + 0.05) if bg_luminance > fg_luminance else (bg_luminance + 0.05) / (fg_luminance + 0.05)


def rgb_to_css_style_with_alpha(r_fg, g_fg, b_fg, a_fg=1.0, r_bg=None, g_bg=None, b_bg=None, a_bg=1.0):
    """Generate CSS style string for both RGB(A) foreground and background."""
    style = f'color: rgba({r_fg}, {g_fg}, {b_fg}, {a_fg});'

    if r_bg is not None and g_bg is not None and b_bg is not None:
        style += f' background-color: rgba({r_bg}, {g_bg}, {b_bg}, {a_bg});'

    return style


def hex_with_alpha(hex_color: str, alpha: float = 1.0) -> str:
    """
    Convert a 6-digit hex color to an 8-digit hex color with the given alpha transparency.

    :param hex_color: A 6-digit hex color string (e.g., "#ff5733").
    :param alpha: A float value between 0 and 1 representing the transparency level (0 = transparent, 1 = opaque).
    :return: An 8-digit hex color string with the alpha channel (e.g., "#ff573380").
    """
    # Strip the leading '#' if present
    hex_color = hex_color.lstrip('#')

    # Ensure it's a valid 6-character hex code
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")

    # Convert the alpha value (0-1) to a 2-digit hex value (00-FF)
    alpha_value = int(alpha * 255)
    alpha_hex = f"{alpha_value:02x}"

    # Return the 8-digit hex code
    return f"#{hex_color}{alpha_hex}"


def hex_to_css_style_with_adjustable_alpha(hex_fg: str = None, alpha_fg: float = 1.0, hex_bg: str = None, alpha_bg: float = 1.0) -> str:
    """
    Generate CSS style string for foreground and/or background colors with adjustable alpha, using hex codes.

    :param hex_fg: A 6-digit hex color string for the foreground (optional).
    :param alpha_fg: A float representing the alpha transparency for the foreground (0.0 to 1.0).
    :param hex_bg: A 6-digit hex color string for the background (optional).
    :param alpha_bg: A float representing the alpha transparency for the background (0.0 to 1.0).
    :return: A CSS style string with foreground and background colors, if provided.
    """
    style = ""

    # Handle foreground color with alpha
    if hex_fg:
        fg_with_alpha = hex_with_alpha(hex_fg, alpha_fg)
        style += f'color: {fg_with_alpha}; '

    # Handle background color with alpha
    if hex_bg:
        bg_with_alpha = hex_with_alpha(hex_bg, alpha_bg)
        style += f'background-color: {bg_with_alpha};'

    return style.strip()  # Strip any trailing spaces


def terminal_supports_truecolor() -> bool:
    """Detect if the terminal supports true-color (24-bit RGB)."""
    if os.getenv("COLORTERM") in ("truecolor", "24bit"):
        return True
    return False


def get_terminal_width() -> int:
    terminal_size = os.get_terminal_size()
    return terminal_size.columns






