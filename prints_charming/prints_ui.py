import sys
import termios
import tty
import time



class PrintsUI:
    def __init__(self, pc):
        """
        A high-level UI helper class that builds upon PrintsCharming.

        :param pc: An instance of PrintsCharming
        """
        self.pc = pc
        self.write = self.pc.write
        self.shared_byte_map = self.pc.__class__.shared_byte_map
        self.button_positions = {}



    def init_ui(self):
        """Handles common UI setup logic."""
        self.write("alt_buffer", "enable_mouse", "enable_sgr_mouse", "hide_cursor")


    def cleanup_ui(self):
        """Handles common UI cleanup logic."""
        self.write("disable_mouse", "disable_sgr_mouse", "show_cursor", "normal_buffer")


    def register_buttons(self, button_grid, start_row, button_width=10, button_height=3):
        """Registers button positions dynamically for mouse click tracking."""
        self.button_positions.clear()
        for row_index, row in enumerate(button_grid):
            for col_index, label in enumerate(row):
                x_start = (col_index * (button_width + 1)) + 1  # +1 for separator
                x_end = x_start + button_width - 1
                y_start = start_row + row_index * button_height
                y_end = y_start + button_height - 1

                self.button_positions[label] = {
                    'x_range': (x_start, x_end),
                    'y_range': (y_start, y_end),
                }


    def handle_click(self, x, y, callback):
        """Generic click handler that maps clicks to buttons."""
        x_term = x  # Column (starts from 1)
        y_term = y  # Row (starts from 1)

        for label, pos in self.button_positions.items():
            x_start, x_end = pos['x_range']
            y_start, y_end = pos['y_range']
            if x_start <= x_term <= x_end and y_start <= y_term <= y_end:
                callback(label)  # Execute function tied to this button
                break


    def event_loop(self, keystroke_handler, click_handler):
        """Unified event loop for handling keystrokes and mouse clicks."""
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
                    if event_type_byte == self.shared_byte_map['mouse_event_end_press'] and button == 0:
                        click_handler(x, y)
                elif event_type == 'keystroke' and event_data:
                    keystroke_handler(event_data)
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)





