import sys
import os
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
        self.pc = PrintsCharming(enable_input_parsing=True, terminal_title="PrintsCharming Calc")
        self.write = self.pc.write
        self.fb = FrameBuilder(pc=self.pc, horiz_char='-', vert_width=1, vert_padding=0, vert_char='|', inner_width=1, inner_padding=0, inner_char='|', horiz_width=45)
        styles_to_edit = {
            'horiz_border': PStyle(color='purple'),
            'vert_border': PStyle(color='orange'),
            'button_pressed': PStyle(color='green', bg_color='jupyter', bold=True, italic=True),
            'button_normal': PStyle(color='white'),
        }
        self.pc.edit_styles(styles_to_edit)
        self.tm = TableManager(pc=self.pc)
        self.expression = ""
        self.display_table_name = "display"
        self.buttons_table_name = "buttons"
        self.button_positions = {}
        self.display_height = 3  # Height of the display area
        self.display_width = 45  # Width of the display area

        self.buttons_layout = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+'],
        ]

        # Store the dimensions of each button cell (as used when drawing them)
        self.button_width = 10

        # Assume a drawn button cell height (including any borders/padding)
        # For instance, if you print:
        #   "\n" + (" " * button_width) + "\n" + label.center(button_width) + "\n" + (" " * button_width) + "\n"
        # and then use a row_height of 3 (omitting the extra newlines), the overall cell might be 5 rows tall.
        self.button_cell_height = 5



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



    def update_button_label(self, label: str, style: str):
        """
        Updates only the label portion of the specified button.
        This assumes that self.button_positions[label] holds the cell's rectangle:
          {'x_range': (x_start, x_end), 'y_range': (y_start, y_end)}
        and that the label is drawn in the middle row of the cell.
        """
        pos = self.button_positions.get(label)
        if pos is None:
            return  # No position recorded for this button

        x_start, x_end = pos['x_range']
        y_start, y_end = pos['y_range']
        # Calculate the cell's height from the stored coordinates.
        cell_height = y_end - y_start + 1
        # Determine the label row: if the button is drawn with a top border/padding,
        # the label is in the middle. For a cell of 5 rows, the label row is y_start + 2.
        label_y = y_start + (cell_height // 2)
        # Use the known button width (should equal x_end - x_start + 1)
        button_width = self.button_width
        # Center the label text within the button width.
        text = label.center(button_width)
        # Move the cursor to the computed label coordinates and write the styled text.
        self.write('cursor_position', row=label_y, col=x_start + 1)
        styled_text = self.pc.apply_style(style, text)
        self.write(styled_text)


    def flash_button_label(self, label: str):
        """
        Flashes the specified button's label with the pressed style, then reverts
        it back to its normal style. This updates only the label text.
        """
        # Update with pressed style.
        self.update_button_label(label, 'button_pressed')
        sys.stdout.flush()
        time.sleep(0.15)  # Adjust delay as desired
        # Revert to normal style.
        self.update_button_label(label, 'button_normal')



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

        self.write(display_table)

        self.button_positions.clear()

        start_row = self.display_height + 1  # Start after the display area
        button_width = 10  # Adjusted button width
        button_border_top = True
        button_border_bottom = True
        button_height = 3 + int(button_border_top) + int(button_border_bottom)
        row_height_to_tallest_col = False
        row_height = (button_height - (int(button_border_top) + int(button_border_bottom))) if not row_height_to_tallest_col else None

        for row_index, row in enumerate(self.buttons_layout):
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

    def update_button_row(self, row_index: int, pressed_buttons: set = None):
        """
        Redraws only a single row of buttons. If pressed_buttons contains one or more labels,
        those buttons are rendered with the 'button_pressed' style.
        """
        if pressed_buttons is None:
            pressed_buttons = set()

        # Settings for button layout
        start_row = self.display_height + 1  # Base starting row for the grid (below display)
        button_width = 10  # Width of each button
        button_border_top = True
        button_border_bottom = True
        # Total height includes extra rows for borders if present.
        button_height = 3 + int(button_border_top) + int(button_border_bottom)
        row_height = button_height - (int(button_border_top) + int(button_border_bottom))

        # Retrieve the specified row from the buttons layout.
        row = self.buttons_layout[row_index]

        # Set cursor position to the top of the affected row.
        self.write('cursor_position', row=start_row + row_index * button_height, col=1)

        padded_buttons = []
        for label in row:
            # If this button is in the pressed_buttons set, apply the pressed style.
            if label in pressed_buttons:
                styled_label = self.pc.apply_style('button_pressed', label.center(button_width))
            else:
                styled_label = label.center(button_width)
            # Create a multi-line block for the button (including top/bottom padding).
            padded_button = (
                f"\n{' ' * button_width}\n"  # Top padding
                f"{styled_label}\n"  # Centered label
                f"{' ' * button_width}\n"  # Bottom padding
            )
            padded_buttons.append(padded_button)

        # Redraw the row using your FrameBuilder's multi-column method.
        self.fb.print_multi_column_box2B(
            columns=padded_buttons,
            col_widths=[button_width] * len(row),
            col_styles=["white"] * len(row),
            horiz_col_alignments=["center"] * len(row),
            vert_col_alignments='center',
            row_height=row_height,
            horiz_border_top=button_border_top,
            horiz_border_bottom=button_border_bottom,
            vert_border_left=True,
            vert_border_right=True,
            col_sep="|",
        )

        # Recompute and update the on-screen positions for each button in this row.
        for col_index, label in enumerate(row):
            x_start = (col_index * (button_width + 1)) + 1  # +1 for the column separator
            x_end = x_start + button_width - 1
            y_start = start_row + row_index * button_height
            y_end = y_start + button_height - 1
            self.button_positions[label] = {
                'x_range': (x_start, x_end),
                'y_range': (y_start, y_end),
            }

    def show_button_pressed(self, label: str):
        """
        Determines the row for the pressed button, updates only that row to show the button
        in a pressed state, waits briefly, then reverts the row back to its normal display.
        """
        # Determine which row the button belongs to by searching your buttons layout.
        row_index = None
        for idx, row in enumerate(self.buttons_layout):
            if label in row:
                row_index = idx
                break
        if row_index is None:
            return  # Button not found

        # Update only the affected row with the pressed button.
        self.update_button_row(row_index, pressed_buttons={label})
        sys.stdout.flush()  # Ensure immediate output
        time.sleep(0.15)  # Short delay for visual feedback
        # Revert the row to its normal appearance.
        self.update_button_row(row_index, pressed_buttons=set())

    def handle_click(self, x: int, y: int):
        """
        Called when a mouse click event is received. Determines which button was
        clicked based on stored button_positions, flashes only its label, then processes
        the input.
        """
        x_term = x  # Terminal column (starting at 1)
        y_term = y  # Terminal row (starting at 1)
        for label, pos in self.button_positions.items():
            x_start, x_end = pos['x_range']
            y_start, y_end = pos['y_range']
            if x_start <= x_term <= x_end and y_start <= y_term <= y_end:
                self.flash_button_label(label)
                self.process_input(label)
                break


    def handle_click2(self, x, y):

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
            self.write(blank_line)
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


def get_script_path():
    """
    Determine whether the script should be executed as a module (-m) or as a script file.
    """
    script_path = os.path.abspath(sys.argv[0])  # Full path of the script
    script_dir = os.path.dirname(script_path)   # Directory of the script
    package_root = None

    # Traverse upwards to find the package root
    current_dir = script_dir
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        if "__init__.py" in os.listdir(current_dir):  # Check for package
            package_root = os.path.dirname(current_dir)
        current_dir = os.path.dirname(current_dir)

    if package_root:
        # Convert to a module path: package.subpackage.script (without .py)
        relative_path = os.path.relpath(script_path, package_root)
        module_path = relative_path.replace(os.sep, ".").rsplit(".", 1)[0]  # Remove .py
        return module_path
    else:
        #return sys.argv[0]  # Use normal script execution
        return os.path.dirname(sys.argv[0])  # ✅ Return one directory higher



if __name__ == "__main__" or __package__ == "prints_charming.examples":
    terminal_mode = 'multi'   # change to 'single' for single terminal mode
    num_instances = 3
    launch_external_script = False
    external_script_path = None  # Full path if running as a script
    external_module = "other.module"  # Python module if running as -m

    if terminal_mode == 'multi':
        instance_count = int(os.getenv("CALCULATOR_INSTANCE", "0"))  # Get instance number (default 0)
        if instance_count == 0:
            # First instance: Launch multiple calculator terminals
            pc = PrintsCharming(terminal_mode="multi")

            for i in range(1, num_instances + 1):
                env_vars = os.environ.copy()
                env_vars["RUNNING_IN_NEW_TERMINAL"] = "1"
                env_vars["CALCULATOR_INSTANCE"] = str(i)  # Assign a unique instance number

                if not launch_external_script:
                    # Determine whether to run as a module or script
                    run_as_module = __package__ == "prints_charming.examples"
                    script_path = get_script_path() if run_as_module else sys.argv[0]
                else:
                    # External script to launch
                    run_as_module = True if external_module else False
                    script_path = external_module or external_script_path


                pc.launch_terminal(
                    name=f"calculator_{i}",
                    script=script_path,
                    title="PrintsCharming Calc",
                    width=45,
                    height=24,
                    env_vars=env_vars,
                    venv_activate_script='activate-colored',
                    run_as_module=run_as_module,
                )
        else:
            # Second instance: runs the calculator UI
            calculator_ui = CalculatorUI()
            calculator_ui.main()
    else:
        calculator_ui = CalculatorUI()
        calculator_ui.main()









