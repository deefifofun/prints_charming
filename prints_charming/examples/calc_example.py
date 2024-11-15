import os
import sys
import time
import termios
import tty
from prints_charming import(
    PrintsCharming,
    FrameBuilder,
    TableManager,
    BoundCell,
)

class CalculatorUI:
    def __init__(self):
        self.pc = PrintsCharming()
        self.write = self.pc.write
        self.fb = FrameBuilder(pc=self.pc, horiz_char='-', vert_width=1, vert_padding=0, vert_char='|', horiz_width=45)
        self.tm = TableManager(pc=self.pc)
        self.expression = ""
        self.display_table_name = "display"
        self.buttons_table_name = "buttons"
        self.button_positions = {}
        self.display_height = 3  # Height of the display area
        self.display_width = 40  # Width of the display area

    def init(self):
        self.write("alt_buffer", "enable_mouse", "enable_sgr_mouse", "hide_cursor")

    def cleanup(self):
        self.write("disable_mouse", "disable_sgr_mouse", "show_cursor", "normal_buffer")

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
        self.write("clear_screen", "cursor_home")

        # Build the display area using TableManager with BoundCell
        # Define a fixed width and height for the display
        display_data = [[BoundCell(lambda: self.get_display_text())]]
        display_table = self.tm.add_bound_table(
            table_data=display_data,
            table_name=self.display_table_name,
            show_table_name=False,
            border_char="-",
            border_style="cyan",
            col_sep="",
            header_style="green",
            cell_style="green",
            use_styles=True,
            target_text_box=True,
            ephemeral=False,
            append_newline=False,
        )

        # Print the display table
        print(display_table, end='')

        # Build the buttons grid using FrameBuilder
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+'],
        ]

        self.button_positions.clear()

        start_row = self.display_height + 1  # Start after the display area
        button_width = 10  # Adjusted button width
        button_height = 3  # Adjusted button height

        for row_index, row in enumerate(buttons):
            # Set the cursor position at the start of the row
            self.write('cursor_position', row=start_row + row_index * button_height, col=1)

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

    def get_display_text(self):
        # Ensure the display text fits within the display area
        max_length = self.display_width - 4  # Subtract borders and padding
        text = self.expression if self.expression else "0"
        return text[-max_length:]  # Get the last part that fits

    def handle_click(self, x, y):
        x_term = x  # Column (starts from 1)
        y_term = y  # Row (starts from 1)

        for label, pos in self.button_positions.items():
            x_start, x_end = pos['x_range']
            y_start, y_end = pos['y_range']
            if x_start <= x_term <= x_end and y_start <= y_term <= y_end:
                self.process_input(label)
                break

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

        # Move cursor back to the display area
        self.write('cursor_position', row=1, col=1)
        # Clear the display area by overwriting with spaces
        blank_line = ' ' * self.display_width
        for i in range(self.display_height):
            print(blank_line)
        # Move cursor back to the top of the display
        self.write('cursor_position', row=1, col=1)

        # Refresh only the display table
        self.tm.refresh_bound_table(self.display_table_name)

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
    calculator_ui = CalculatorUI()
    calculator_ui.main()

"""
class CalculatorUI:
    def __init__(self):
        self.pc = PrintsCharming()
        self.write = self.pc.write
        self.fb = FrameBuilder(pc=self.pc, horiz_char='-', vert_width=1, vert_padding=0, vert_char='|')
        self.expression = ""
        self.button_positions = {}


    def init(self):
        self.write("enable_mouse", "enable_sgr_mouse", "hide_cursor")


    def cleanup(self):
        self.write("disable_mouse", "disable_sgr_mouse", "show_cursor")


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
        self.write("clear_screen", "cursor_home")

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
            self.write('cursor_position', row=start_row + row_index * button_height, col=1)

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
"""



