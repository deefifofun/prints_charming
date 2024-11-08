"""
import sys
import termios
import tty
from prints_charming import PrintsCharming, FrameBuilder

pc = PrintsCharming()
fb = FrameBuilder(pc=pc, horiz_char='-', vert_width=1, vert_padding=0, vert_char='|')

expression = ""

button_positions = {}


def init():
    sys.stdout.write("\033[?1000h")  # Enable basic mouse tracking
    sys.stdout.write("\033[?1006h")  # Enable SGR mouse mode
    sys.stdout.write("\033[?25l")  # Hide cursor
    sys.stdout.flush()


def cleanup():
    sys.stdout.write("\033[?1000l")  # Disable basic mouse tracking
    sys.stdout.write("\033[?1006l")  # Disable SGR mouse mode
    sys.stdout.write("\033[?25h")  # Show cursor
    sys.stdout.flush()


def get_mouse_event():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        # Set cbreak mode to allow signals like Ctrl-C
        tty.setcbreak(fd, termios.TCSANOW)
        c = sys.stdin.buffer.read(1)
        if c == b'\x1b':  # Start of an escape sequence
            c += sys.stdin.buffer.read(1)
            if c[-1:] == b'[':
                c += sys.stdin.buffer.read(1)
                if c[-1:] == b'<':
                    # Read until 'M' or 'm' is found
                    while True:
                        ch = sys.stdin.buffer.read(1)
                        c += ch
                        if ch in (b'M', b'm'):
                            break
                    # Now parse the sequence
                    params = c[3:-1].split(b';')
                    if len(params) == 3:
                        b = int(params[0])
                        x = int(params[1])
                        y = int(params[2])
                        event_type = c[-1:]  # b'M' for press, b'm' for release
                        # Return the event code 'b' as well
                        return b, x, y, event_type
    except KeyboardInterrupt:
        raise  # Allow Ctrl-C to interrupt
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None


def build_calculator_ui():
    # Clear screen
    sys.stdout.write("\033[2J")
    sys.stdout.write("\033[H")
    sys.stdout.flush()

    # Build the display area
    fb.print_border_boxed_text(
        text=expression if expression else "0",
        text_style="green",
        text_align="left",
        horiz_border_top_style="cyan",
        horiz_border_bottom_style="cyan",
        text_vert_border_l_style="cyan",
        text_vert_border_r_style="cyan",
    )

    # Build the buttons grid
    buttons = [
        ['7', '8', '9', '/'],
        ['4', '5', '6', '*'],
        ['1', '2', '3', '-'],
        ['C', '0', '=', '+'],
    ]

    global button_positions
    button_positions.clear()

    start_row = 6  # Adjust based on display area height
    button_width = 10  # Adjusted button width
    button_height = 3  # Adjusted button height

    for row_index, row in enumerate(buttons):
        # Set the cursor position at the start of the row
        pc.write('cursor_position', row=start_row + row_index * button_height, col=1)

        # Draw buttons in the row
        fb.print_multi_column_box2(
            columns=row,
            col_widths=[button_width] * 4,
            col_styles=["white"] * 4,
            col_alignments=["center"] * 4,
            horiz_border_top=True,
            horiz_border_bottom=True,
            vert_border_left=True,
            vert_border_right=True,
            col_sep="|",
        )

        # Calculate and store button positions
        for col_index, label in enumerate(row):
            x_start = (col_index * (button_width + 1)) + 1  # +1 for the separator '|'
            x_end = x_start + button_width - 1
            y_start = start_row + row_index * button_height
            y_end = y_start + button_height - 1

            button_positions[label] = {
                'x_range': (x_start, x_end),
                'y_range': (y_start, y_end),
            }

    # For debugging, print button positions
    print("Button Positions:")
    for label, pos in button_positions.items():
        print(f"Button '{label}': x_range={pos['x_range']}, y_range={pos['y_range']}")


def handle_click(x, y):
    x_term = x  # Column (starts from 1)
    y_term = y  # Row (starts from 1)

    print(f"Click at x={x_term}, y={y_term}")

    for label, pos in button_positions.items():
        x_start, x_end = pos['x_range']
        y_start, y_end = pos['y_range']
        print(f"Checking Button '{label}' at x_range={x_start}-{x_end}, y_range={y_start}-{y_end}")
        if x_start <= x_term <= x_end and y_start <= y_term <= y_end:
            print(f"Button '{label}' clicked.")
            process_input(label)
            break
    else:
        print("No button found at this position.")


def process_input(label):
    global expression
    if label in '0123456789.':
        expression += label
    elif label in '+-*/':
        expression += ' ' + label + ' '
    elif label == '=':
        try:
            result = eval(expression)
            expression = str(result)
        except Exception:
            expression = "Error"
    elif label == 'C':
        expression = ""
    build_calculator_ui()


def event_loop():
    while True:
        event = get_mouse_event()
        if event:
            b, x, y, event_type = event
            # Extract the actual button code (lower 3 bits)
            button = b & 0b11
            # Check for scroll events (button code 64 and above)
            if b >= 64:
                # It's a scroll event; ignore or handle as needed
                continue
            if event_type == b'M' and button == 0:
                # Left button press
                handle_click(x, y)
            else:
                # Ignore other events
                continue


def main():
    init()
    build_calculator_ui()
    try:
        event_loop()
    except KeyboardInterrupt:
        pass  # Exit on Ctrl-C
    finally:
        cleanup()


if __name__ == "__main__":
    main()
"""


import sys
import termios
import tty
from prints_charming import PrintsCharming, FrameBuilder


class CalculatorUI:
    def __init__(self):
        self.pc = PrintsCharming()
        self.fb = FrameBuilder(pc=self.pc, horiz_char='-', vert_width=1, vert_padding=0, vert_char='|')
        self.expression = ""
        self.button_positions = {}


    def init(self):
        sys.stdout.write("\033[?1000h")  # Enable basic mouse tracking
        sys.stdout.write("\033[?1006h")  # Enable SGR mouse mode
        sys.stdout.write("\033[?25l")    # Hide cursor
        sys.stdout.flush()


    def cleanup(self):
        sys.stdout.write("\033[?1000l")  # Disable basic mouse tracking
        sys.stdout.write("\033[?1006l")  # Disable SGR mouse mode
        sys.stdout.write("\033[?25h")    # Show cursor
        sys.stdout.flush()


    def get_mouse_event(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            # Set cbreak mode to allow signals like Ctrl-C
            tty.setcbreak(fd, termios.TCSANOW)
            c = sys.stdin.buffer.read(1)
            if c == b'\x1b':  # Start of an escape sequence
                c += sys.stdin.buffer.read(1)
                if c[-1:] == b'[':
                    c += sys.stdin.buffer.read(1)
                    if c[-1:] == b'<':
                        # Read until 'M' or 'm' is found
                        while True:
                            ch = sys.stdin.buffer.read(1)
                            c += ch
                            if ch in (b'M', b'm'):
                                break
                        # Now parse the sequence
                        params = c[3:-1].split(b';')
                        if len(params) == 3:
                            b = int(params[0])
                            x = int(params[1])
                            y = int(params[2])
                            event_type = c[-1:]  # b'M' for press, b'm' for release
                            # Return the event code 'b' as well
                            return b, x, y, event_type
        except KeyboardInterrupt:
            raise  # Allow Ctrl-C to interrupt
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None


    def build_calculator_ui(self):
        # Clear screen
        sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")
        sys.stdout.flush()

        # Build the display area
        self.fb.print_border_boxed_text(
            text=self.expression if self.expression else "0",
            text_style="green",
            text_align="left",
            horiz_border_top_style="cyan",
            horiz_border_bottom_style="cyan",
            text_vert_border_l_style="cyan",
            text_vert_border_r_style="cyan",
        )

        # Build the buttons grid
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+'],
        ]

        self.button_positions.clear()

        start_row = 6      # Adjust based on display area height
        button_width = 10  # Adjusted button width
        button_height = 3  # Adjusted button height

        for row_index, row in enumerate(buttons):
            # Set the cursor position at the start of the row
            self.pc.write('cursor_position', row=start_row + row_index * button_height, col=1)

            # Draw buttons in the row
            self.fb.print_multi_column_box2(
                columns=row,
                col_widths=[button_width] * 4,
                col_styles=["white"] * 4,
                col_alignments=["center"] * 4,
                horiz_border_top=True,
                horiz_border_bottom=True,
                vert_border_left=True,
                vert_border_right=True,
                col_sep="|",
            )

            # Calculate and store button positions
            for col_index, label in enumerate(row):
                x_start = (col_index * (button_width + 1)) + 1  # +1 for the separator '|'
                x_end = x_start + button_width - 1
                y_start = start_row + row_index * button_height
                y_end = y_start + button_height - 1

                self.button_positions[label] = {
                    'x_range': (x_start, x_end),
                    'y_range': (y_start, y_end),
                }

        # For debugging, print button positions
        print("Button Positions:")
        for label, pos in self.button_positions.items():
            print(f"Button '{label}': x_range={pos['x_range']}, y_range={pos['y_range']}")


    def handle_click(self, x, y):
        x_term = x  # Column (starts from 1)
        y_term = y  # Row (starts from 1)

        print(f"Click at x={x_term}, y={y_term}")

        for label, pos in self.button_positions.items():
            x_start, x_end = pos['x_range']
            y_start, y_end = pos['y_range']
            print(f"Checking Button '{label}' at x_range={x_start}-{x_end}, y_range={y_start}-{y_end}")
            if x_start <= x_term <= x_end and y_start <= y_term <= y_end:
                print(f"Button '{label}' clicked.")
                self.process_input(label)
                break
        else:
            print("No button found at this position.")


    def process_input(self, label):
        if label in '0123456789.':
            self.expression += label
        elif label in '+-*/':
            self.expression += ' ' + label + ' '
        elif label == '=':
            try:
                result = eval(self.expression)
                self.expression = str(result)
            except Exception:
                self.expression = "Error"
        elif label == 'C':
            self.expression = ""
        self.build_calculator_ui()


    def event_loop(self):
        while True:
            event = self.get_mouse_event()
            if event:
                b, x, y, event_type = event
                # Extract the actual button code (lower 3 bits)
                button = b & 0b11
                # Check for scroll events (button code 64 and above)
                if b >= 64:
                    # It's a scroll event; ignore or handle as needed
                    continue
                if event_type == b'M' and button == 0:
                    # Left button press
                    self.handle_click(x, y)
                else:
                    # Ignore other events
                    continue


    def main(self):
        self.init()
        self.build_calculator_ui()
        try:
            self.event_loop()
        except KeyboardInterrupt:
            pass  # Exit on Ctrl-C
        finally:
            self.cleanup()



if __name__ == "__main__":
    # very basic quick implementation
    calculator_ui = CalculatorUI()
    calculator_ui.main()

