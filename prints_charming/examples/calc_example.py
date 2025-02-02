import sys
import time
import asyncio
import termios
import tty
from prints_charming import (
    PStyle,
    PrintsCharming,
    FrameBuilder,
    TableManager,
    BoundCell,
)




class CalculatorUI:
    def __init__(self):
        self.pc = PrintsCharming(enable_input_parsing=True)
        self.write = self.pc.write
        self.fb = FrameBuilder(pc=self.pc, horiz_char='-', vert_width=1, vert_padding=0, vert_char='|', inner_width=1, inner_padding=0, inner_char='|', horiz_width=45)
        styles_to_edit = {
            'horiz_border': PStyle(color='purple'),
            'vert_border': PStyle(color='orange')
        }
        self.pc.edit_styles(styles_to_edit)
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


    def handle_keystroke(self, key):
        if key in '0123456789.':
            self.process_input(key)
        elif key in '+-*/':
            self.process_input(key)
        elif key == '=' or key == '\n':
            self.process_input('=')
        elif key.lower() == 'c':
            self.process_input('C')
        elif key == '\x7f':  # Backspace
            self.expression = self.expression[:-1]
            self.update_display()
        elif key in ('UP_ARROW', 'DOWN_ARROW', 'LEFT_ARROW', 'RIGHT_ARROW'):
            # Handle arrow keys if needed
            pass
        elif key == 'ESCAPE':
            pass
        else:
            pass



    def build_calculator_ui(self):

        # Clear screen
        self.write("clear_screen", "cursor_home")

        # Build the display area using TableManager with BoundCell
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
        print(display_table)

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
        button_border_top = True
        button_border_bottom = True
        button_height = 3 + int(button_border_top) + int(button_border_bottom)
        row_height_to_tallest_col = False
        row_height = (button_height - (int(button_border_top) + int(button_border_bottom))) if not row_height_to_tallest_col else None

        for row_index, row in enumerate(buttons):
            # Set cursor position at the start of the row
            self.write('cursor_position', row=start_row + row_index * button_height, col=1)

            # Modify each button to be multi-line to fill full height
            padded_buttons = [
                f"\n{' ' * button_width}\n{label.center(button_width)}\n{' ' * button_width}\n"
                for label in row
            ]

            # Draw buttons in the row with extra padding
            self.fb.print_multi_column_box2B(
                columns=padded_buttons,
                col_widths=[button_width] * 4,
                col_styles=["white"] * 4,
                horiz_col_alignments=["center"] * 4,
                vert_col_alignments='center',
                row_height=row_height,
                horiz_border_top=button_border_top,
                horiz_border_bottom=button_border_bottom,
                vert_border_left=True,
                vert_border_right=True,
                col_sep="|",
            )

            # Calculate and store button positions
            for col_index, label in enumerate(row):
                x_start = (col_index * (button_width + 1)) + 1  # +1 for the separator '|'
                x_end = x_start + button_width - 1
                y_start = start_row + row_index * button_height
                y_end = y_start + button_height - 1  # Updated to match new height

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


    def update_display(self):
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
        self.update_display()



    def event_loop(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd, termios.TCSANOW)
            while True:
                event_type, event_data = self.pc.__class__.parse_input()
                if event_type == 'mouse' and event_data:
                    b_code, x, y, event_type_byte = event_data
                    button = b_code & 0b11
                    if b_code >= 64:
                        continue  # Ignore scroll events
                    if event_type_byte == self.pc.shared_byte_map['mouse_event_end_press'] and button == 0:
                        self.handle_click(x, y)
                elif event_type == 'keystroke' and event_data:
                    self.handle_keystroke(event_data)
                else:
                    # No input; sleep briefly to prevent high CPU usage
                    time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


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









