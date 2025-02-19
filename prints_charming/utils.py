import os
import sys
import math
import tty
import termios
import select
import asyncio





def get_terminal_width() -> int:
    terminal_size = os.get_terminal_size()
    return terminal_size.columns


def get_terminal_height() -> int:
    terminal_size = os.get_terminal_size()
    return terminal_size.lines


class AsyncKeyReader:
    """
    Sets up an asyncio-based, non-blocking way to capture
    single keystrokes from stdin on a POSIX system in raw mode.
    """

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()

        # Save the original tty settings so we can restore them on exit
        self.fd = sys.stdin.fileno()
        self.original_settings = termios.tcgetattr(self.fd)

        # Put stdin in raw mode so keystrokes are immediately available
        tty.setraw(sys.stdin.fileno())

        # Tell the event loop to call our _on_stdin_ready() whenever stdin has data
        self.loop.add_reader(sys.stdin, self._on_stdin_ready)


    def _on_stdin_ready(self):
        """
        Callback invoked by the event loop when stdin has data.
        It reads the key data as bytes and uses PrintsCharming's
        reverse mapping to interpret escape sequences.
        """
        # Read the first byte in binary mode.
        first_byte = sys.stdin.buffer.read(1)
        if not first_byte:
            return

        # Check if the input begins with the escape character.
        if first_byte == PrintsCharming.shared_byte_map["escape_key"]:
            # Start building the escape sequence.
            # Attempt to read an initial set of 2 additional bytes.
            seq = first_byte + sys.stdin.buffer.read(2)

            # If the sequence does not yet appear complete (i.e. does not end with an alpha or '~'),
            # then read the remaining bytes (this call is blocking, but acceptable in this callback).
            if not (seq[-1:].isalpha() or seq.endswith(b"~")):
                seq += PrintsCharming.read_remaining_escape_sequence()

            # Delegate to PrintsCharming to resolve the sequence.
            token = PrintsCharming.parse_escape_sequence(seq)
            self.queue.put_nowait(token)
        else:
            # For non-escape input, decode the byte to a UTF-8 character.
            try:
                key = first_byte.decode("utf-8", errors="ignore")
            except Exception:
                key = ""
            self.queue.put_nowait(key)


    async def get_key(self):
        """
        Waits until a single character is available in the queue, then returns it.
        This 'blocks' only within the async context (it yields to the event loop).
        """
        return await self.queue.get()

    def get_key_nowait(self):
        """
        Attempts to get a keystroke immediately if available.
        Raises asyncio.QueueEmpty if none is available.
        """
        return self.queue.get_nowait()

    def restore_tty(self):
        """
        Restore original terminal settings.
        Call this upon exiting to leave the terminal in a sane state.
        """
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.original_settings)
        # Also remove the reader so we don't keep reading from stdin
        self.loop.remove_reader(sys.stdin)


class AsyncMouseReader:
    """
    Sets up an asyncio-based, non-blocking mechanism to capture
    mouse events from stdin, leveraging Xterm's basic mouse reporting.
    """

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()

        # Save original tty settings to restore later.
        self.fd = sys.stdin.fileno()
        self.original_settings = termios.tcgetattr(self.fd)

        # Switch stdin to raw mode.
        tty.setraw(self.fd)

        # Enable Xterm mouse tracking (basic mode).
        sys.stdout.write("\033[?1000h")
        sys.stdout.flush()

        # Register our reader callback for stdin.
        self.loop.add_reader(sys.stdin, self._on_stdin_ready)

    def _on_stdin_ready(self):
        """
        Callback invoked by the event loop when stdin has data.
        It checks for the Xterm mouse event escape sequence and decodes it.
        """
        # Read the first byte.
        first_byte = sys.stdin.buffer.read(1)
        if not first_byte:
            return

        # Check if it is an escape sequence.
        if first_byte == b'\x1b':
            # Attempt to read the next two bytes.
            seq = first_byte + sys.stdin.buffer.read(2)
            if seq[1:] == b'[M':
                # Basic mouse event detected; read the following three bytes.
                data = sys.stdin.buffer.read(3)
                if len(data) < 3:
                    return  # Incomplete sequence, so exit early.

                # The three data bytes are encoded by adding 32.
                # Subtract 32 to retrieve the original values.
                button_code = data[0] - 32
                x = data[1] - 32
                y = data[2] - 32

                # Construct an event dictionary.
                event = {
                    'button': button_code,
                    'x': x,
                    'y': y
                }
                self.queue.put_nowait(event)
            else:
                # If it isn't a mouse event, you might choose to handle
                # it differently or simply ignore it.
                pass
        else:
            # Non-escape data can be ignored or processed as needed.
            pass

    async def get_mouse_event(self):
        """
        Asynchronously waits for and returns the next mouse event.
        """
        return await self.queue.get()

    def get_mouse_event_nowait(self):
        """
        Attempts to return a mouse event immediately if available,
        otherwise raises asyncio.QueueEmpty.
        """
        return self.queue.get_nowait()

    def restore_tty(self):
        """
        Restores the original terminal settings and disables mouse reporting.
        Should be called upon exit.
        """
        # Restore original tty settings.
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.original_settings)
        # Disable mouse tracking.
        sys.stdout.write("\033[?1000l")
        sys.stdout.flush()
        # Remove the reader callback.
        self.loop.remove_reader(sys.stdin)


class InputHandler:
    """
    A unified asynchronous input handler that reads both keyboard
    and mouse events from stdin and dispatches them via a single coroutine.
    """
    def __init__(self, enable_keyboard=True, enable_mouse=True):
        self.enable_keyboard = enable_keyboard
        self.enable_mouse = enable_mouse
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()
        self.fd = sys.stdin.fileno()
        # Save original terminal settings.
        self.original_settings = termios.tcgetattr(self.fd)
        # Switch stdin to raw mode.
        tty.setraw(self.fd)
        # Enable basic mouse tracking.
        sys.stdout.write("\033[?1000h")
        sys.stdout.flush()
        # Register a single reader callback for stdin.
        self.loop.add_reader(sys.stdin, self._on_stdin_ready)

    def _on_stdin_ready(self):
        """
        Callback that reads from stdin and distinguishes between
        key and mouse events before enqueuing a tagged event.
        """
        # Read the first byte from stdin.
        first_byte = sys.stdin.buffer.read(1)
        if not first_byte:
            return

        # Check for the escape character indicating a special sequence.
        if first_byte == b'\x1b':
            # Peek at the next two bytes.
            seq = first_byte + sys.stdin.buffer.read(2)
            # Determine if this is a mouse event (Xterm mouse reporting).
            if seq[1:] == b'[M':
                # Read the three additional bytes encoding the mouse event.
                data = sys.stdin.buffer.read(3)
                if len(data) < 3:
                    return  # Incomplete mouse event sequence.
                event = {
                    'type': 'mouse',
                    'button': data[0] - 32,  # Decode per Xterm specification.
                    'x': data[1] - 32,
                    'y': data[2] - 32,
                }
                self.queue.put_nowait(event)
            else:
                # Otherwise, treat as a keyboard escape sequence.
                # (In a real application, you might delegate to a helper
                # to parse more complex sequences.)
                try:
                    key = seq.decode("utf-8", errors="ignore")
                except Exception:
                    key = ''
                event = {'type': 'key', 'key': key}
                self.queue.put_nowait(event)
        else:
            # For non-escape input, decode as a normal key event.
            try:
                key = first_byte.decode("utf-8", errors="ignore")
            except Exception:
                key = ''
            event = {'type': 'key', 'key': key}
            self.queue.put_nowait(event)

    async def process_events(self):
        """
        Continuously process incoming events by dispatching them to
        the appropriate handlers.
        """
        while True:
            event = await self.queue.get()
            if event.get('type') == 'key':
                self.handle_key_event(event['key'])
            elif event.get('type') == 'mouse':
                self.handle_mouse_event(event)
            self.queue.task_done()

    def handle_key_event(self, key):
        """
        Process a keyboard event.
        Override or extend this method to suit application logic.
        """
        # Example: print the key event.
        print(f"Key event received: {key}")

    def handle_mouse_event(self, event):
        """
        Process a mouse event.
        Override or extend this method to suit application logic.
        """
        print(f"Mouse event received: Button {event['button']} at ({event['x']}, {event['y']})")

    def restore_tty(self):
        """
        Restore original terminal settings and disable mouse tracking.
        """
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.original_settings)
        sys.stdout.write("\033[?1000l")
        sys.stdout.flush()
        self.loop.remove_reader(sys.stdin)




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


def pole_key_nonblock():
    """
    Checks if a key is available in stdin (non-blocking).
    Returns the character read if available, or None otherwise.
    """
    # Save original terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        # Switch to raw mode so we can read immediately
        tty.setraw(fd)

        # Use select to see if stdin has data
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            # Data is ready, read 1 character
            ch = sys.stdin.read(1)
            return ch
        else:
            # No data available
            return None
    finally:
        # Restore terminal settings no matter what
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


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









