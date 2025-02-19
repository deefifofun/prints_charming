import shutil
import signal
import os
import time
import textwrap
from typing import NamedTuple

from prints_charming import PrintsCharming



def init_ui(pc):
    """Handles common UI setup logic."""
    #pc.__class__.write("alt_buffer", "enable_mouse", "enable_sgr_mouse", "hide_cursor")
    pc.__class__.write("alt_buffer", "hide_cursor")


def cleanup_ui(pc):
    """Handles common UI cleanup logic."""
    #pc.__class__.write("disable_mouse", "disable_sgr_mouse", "show_cursor", "normal_buffer")
    pc.__class__.write("show_cursor", "normal_buffer")

########################################
# Global MasterLayout with dynamic scaling
########################################

class MasterLayout:
    """
    Holds the terminal dimensions and a list of top-level layouts.
    Provides a composite render that overlays each sublayout at its
    absolute offset.
    """
    def __init__(self):
        self.update_terminal_size()
        self.sublayouts = []

    def update_terminal_size(self):
        term_size = shutil.get_terminal_size()
        self.width = term_size.columns
        self.height = term_size.lines

    def add_sublayout(self, layout):
        self.sublayouts.append(layout)
        layout.parent = self  # Assign master as parent

    @property
    def inner_width(self):
        # MasterLayout is the top-level container, so use full dimensions.
        return self.width

    @property
    def inner_height(self):
        return self.height

    def render(self):
        # Create a canvas representing the entire terminal.
        canvas = [list(" " * self.width) for _ in range(self.height)]

        # Helper function to overlay a rendered string onto the canvas.
        def overlay(rendered_str, ox, oy):
            lines = rendered_str.split("\n")
            for i, line in enumerate(lines):
                y = oy + i
                if 0 <= y < self.height:
                    for j, char in enumerate(line):
                        x = ox + j
                        if 0 <= x < self.width:
                            canvas[y][x] = char

        # Composite each sublayout onto the master canvas.
        for layout in self.sublayouts:
            # Calculate absolute offsets (based on parent's inner dimensions)
            ox = layout.get_absolute_offset_x()
            oy = layout.get_absolute_offset_y()
            rendered = layout.render()
            overlay(rendered, ox, oy)

        return "\n".join("".join(row) for row in canvas)

########################################
# Responsive Layout with relative values
########################################

class Layout:
    """
    A layout that sizes and positions itself relative to its parent.
    It can have its own border and contains sublayouts and boxes.
    """
    def __init__(self, relative_width, relative_height, relative_offset_x, relative_offset_y, border=True, border_chars=None, allow_overflow_right=False, scroll_offset_x=0):
        # All relative_* values should be between 0 and 1.
        self.relative_width = relative_width
        self.relative_height = relative_height
        self.relative_offset_x = relative_offset_x
        self.relative_offset_y = relative_offset_y
        self.border = border

        # Default border characters if none are provided
        default_border = ("╔", "╗", "╚", "╝", "═", "║")

        # Assign border characters (fallback to defaults)
        self.border_chars = border_chars if border_chars and len(border_chars) == 6 else default_border

        self.allow_overflow_right = allow_overflow_right
        self.scroll_offset_x = scroll_offset_x
        self.sublayouts = []
        self.boxes = []
        self.parent = None  # Will be set when added to a parent
        self.width = None
        self.height = None


    def compute_dimensions(self):
        """Calculate absolute width and height from parent's inner dimensions."""
        if self.parent:
            parent_inner_width = self.parent.inner_width
            parent_inner_height = self.parent.inner_height
        else:
            # Fallback to terminal dimensions if no parent is defined.
            term_size = shutil.get_terminal_size()
            parent_inner_width = term_size.columns
            parent_inner_height = term_size.lines

        self.width = int(parent_inner_width * self.relative_width)
        self.height = int(parent_inner_height * self.relative_height)

    def get_absolute_offset_x(self):
        """Compute absolute horizontal offset from parent's inner width."""
        if self.parent:
            parent_inner_width = self.parent.inner_width
        else:
            parent_inner_width = shutil.get_terminal_size().columns
        return int(parent_inner_width * self.relative_offset_x)

    def get_absolute_offset_y(self):
        """Compute absolute vertical offset from parent's inner height."""
        if self.parent:
            parent_inner_height = self.parent.inner_height
        else:
            parent_inner_height = shutil.get_terminal_size().lines
        return int(parent_inner_height * self.relative_offset_y)

    @property
    def inner_width(self):
        self.compute_dimensions()
        return self.width - 2 if self.border else self.width

    @property
    def inner_height(self):
        self.compute_dimensions()
        return self.height - 2 if self.border else self.height

    def add_sublayout(self, layout):
        layout.parent = self
        self.sublayouts.append(layout)

    def add_box(self, box):
        box.parent = self
        self.boxes.append(box)

    def render(self):

        # 1) Compute own dimensions.
        self.compute_dimensions()

        # 2) Figure out how wide we actually need to draw if allow_overflow_right is True.
        #    We'll measure the bounding "right edge" of each sublayout or box.
        needed_width = self.inner_width  # Start with normal width
        for sub in self.sublayouts:
            sub.compute_dimensions()
            # offset_x is sub's offset within *this* layout's inner area
            sub_right_edge = sub.get_absolute_offset_x() + sub.width
            if sub_right_edge > needed_width:
                needed_width = sub_right_edge

        for box in self.boxes:
            # Use computed offsets and dimensions if the box is relative.
            if hasattr(box, 'relative') and box.relative:
                box_right_edge = box.absolute_offset_x + box.computed_width
            else:
                box_right_edge = box.offset_x + box.width
            if box_right_edge > needed_width:
                needed_width = box_right_edge

        """
        for box in self.boxes:
            # offset_x is box.offset_x within this layout's inner area
            box_right_edge = box.offset_x + box.width
            if box_right_edge > needed_width:
                needed_width = box_right_edge
        """

        # If we allow overflow, we expand the drawing area. If not, we clip to inner_width.
        if self.allow_overflow_right and (needed_width > self.inner_width):
            actual_canvas_width = needed_width
        else:
            actual_canvas_width = self.inner_width

        # 3) Create the internal canvas.
        canvas = [list(" " * actual_canvas_width) for _ in range(self.inner_height)]

        def overlay(rendered_str, ox, oy):
            lines = rendered_str.split("\n")
            for i, line in enumerate(lines):
                y = oy + i
                if 0 <= y < self.inner_height:
                    for j, char in enumerate(line):
                        x = ox + j
                        if 0 <= x < actual_canvas_width:
                            canvas[y][x] = char

        # 4) Render and overlay sublayouts.
        for sub in self.sublayouts:
            ox = sub.get_absolute_offset_x()
            oy = sub.get_absolute_offset_y()
            rendered = sub.render()
            overlay(rendered, ox, oy)

        # 5) Render and overlay boxes.
        """
        for box in self.boxes:
            rendered = box.render(layout_mode=True)
            overlay(rendered, box.offset_x, box.offset_y)
        """
        for box in self.boxes:
            rendered = box.render(layout_mode=True)
            # Use computed offsets for relative boxes; otherwise use fixed offsets.
            if hasattr(box, 'relative') and box.relative:
                overlay(rendered, box.absolute_offset_x, box.absolute_offset_y)
            else:
                overlay(rendered, box.offset_x, box.offset_y)

        # 6) Convert canvas rows to strings.
        inner_content = ["".join(row) for row in canvas]

        # 7) If the layout has a border, wrap it around the content.
        if self.border:
            tl, tr, bl, br, hz, vt = self.border_chars
            top_border = f"{tl}{hz * (actual_canvas_width)}{tr}"
            bottom_border = f"{bl}{hz * (actual_canvas_width)}{br}"
            bordered = [top_border]
            for line in inner_content:
                # If we do not clip horizontally here, the border will match the expanded width
                bordered.append(f"{vt}{line}{vt}")
            bordered.append(bottom_border)
            final_str = "\n".join(bordered)
        else:
            final_str = "\n".join(inner_content)

        # 8) (Optional) If we wanted to *scroll* horizontally, we'd slice each line:
        if self.allow_overflow_right:
            # The maximum visible width inside this layout:
            visible_width = self.inner_width
            # Account for the border if present
            if self.border:
                visible_width += 2  # Because the final_str includes the left/right border

            # Make sure we don't scroll past the left edge
            if self.scroll_offset_x < 0:
                self.scroll_offset_x = 0

            # Make sure we don't scroll past the right edge
            max_scroll = actual_canvas_width - visible_width
            if max_scroll < 0:
                max_scroll = 0
            if self.scroll_offset_x > max_scroll:
                self.scroll_offset_x = max_scroll

            # Now slice each line from scroll_offset_x to scroll_offset_x + visible_width
            lines = final_str.split("\n")
            sliced_lines = []
            for line in lines:
                # Each line might be shorter than needed; so we safely slice
                # using Python's standard substring approach
                segment = line[self.scroll_offset_x: self.scroll_offset_x + visible_width]
                sliced_lines.append(segment)

            final_str = "\n".join(sliced_lines)
        # ============== END SCROLLING LOGIC ==============

        # 9) Return the final rendered string for overlay by the parent.
        return final_str



class UIElement:
    """
    A base class for UI elements that encapsulates common properties and
    dimension calculations for both relative and absolute sizing.
    """
    def __init__(self, width, height, offset_x=0, offset_y=0, relative=True):
        self.relative = relative
        if self.relative:
            # Interpret these values as fractions of the parent's inner dimensions.
            self.relative_width = width
            self.relative_height = height
            self.relative_offset_x = offset_x
            self.relative_offset_y = offset_y
        else:
            self.width = width
            self.height = height
            self.offset_x = offset_x
            self.offset_y = offset_y

        self.parent = None  # To be set when the element is added to a layout/container.

    @property
    def computed_width(self):
        if self.relative and self.parent:
            # Enforce a minimal width (e.g., 3) to accommodate borders.
            return max(3, int(self.parent.inner_width * self.relative_width))
        return self.width

    @property
    def computed_height(self):
        if self.relative and self.parent:
            return max(3, int(self.parent.inner_height * self.relative_height))
        return self.height

    @property
    def absolute_offset_x(self):
        if self.relative and self.parent:
            return int(self.parent.inner_width * self.relative_offset_x)
        return self.offset_x

    @property
    def absolute_offset_y(self):
        if self.relative and self.parent:
            return int(self.parent.inner_height * self.relative_offset_y)
        return self.offset_y

    def render(self, layout_mode=False):
        """
        A placeholder method. Subclasses should implement their own render logic.
        """
        raise NotImplementedError("Subclasses must implement render()")


########################################
# A simple Box element
########################################

class Box(UIElement):
    """
    A fundamental, non-interactive box element with a border and text content.
    Inherits common functionality from UIElement.
    """
    def __init__(self, width, height, content="", border_chars=None, offset_x=0, offset_y=0, relative=True):
        super().__init__(width, height, offset_x, offset_y, relative)
        self.content = content

        # Default border characters for a box.
        default_border = ("┌", "┐", "└", "┘", "─", "│")
        self.border_chars = border_chars if border_chars is not None else default_border

    def render(self, layout_mode=False):
        w = self.computed_width
        h = self.computed_height

        # Unpack the border characters.
        tl, tr, bl, br, hz, vt = self.border_chars
        top_border = f"{tl}{hz * (w - 2)}{tr}"
        bottom_border = f"{bl}{hz * (w - 2)}{br}"

        # Use textwrap to wrap the content within the available inner width (w-2).
        wrapped_lines = textwrap.wrap(self.content, width=w - 2)

        # Prepare the inner content lines.
        content_lines = []
        """
        lines = self.content.split("\n")
        for i in range(h - 2):
            # Use a corresponding content line if available; otherwise, pad with spaces.
            line = lines[i] if i < len(lines) else ""
            line = line.ljust(w - 2)[:w - 2]
            content_lines.append(f"{vt}{line}{vt}")
        """

        for i in range(h - 2):
            # If there's wrapped text available, use it; otherwise, use an empty string.
            line = wrapped_lines[i] if i < len(wrapped_lines) else ""
            # Left-justify to ensure the line occupies the entire inner width.
            line = line.ljust(w - 2)
            content_lines.append(f"{vt}{line}{vt}")

        # Combine the borders and content.
        return "\n".join([top_border] + content_lines + [bottom_border])



# Assumed helper definitions:
class Segment(NamedTuple):
    text: str
    style: any


def build_top_line(box_top: str, length: int, style, partial: bool) -> Segment:
    if partial:
        top_left_char = box_top[0]
        top_right_char = box_top[0]
        text = top_left_char + (" " * (length - 2)) + top_right_char
    else:
        text = box_top * length
    return Segment(text, style)


def build_bottom_line(box_bottom: str, length: int, style, partial: bool) -> Segment:
    if partial:
        bottom_left_char = box_bottom[0]
        bottom_right_char = box_bottom[0]
        text = bottom_left_char + (" " * (length - 2)) + bottom_right_char
    else:
        text = box_bottom * length
    return Segment(text, style)


def build_middle_line(box_left: str, content: str, box_right: str,
                      left_style, center_style, right_style) -> list[Segment]:
    left = Segment(box_left, left_style)
    center = Segment(content, center_style)
    right = Segment(box_right, right_style)
    return [left, center, right]


# The Button class with a render method based on your print_button logic.
class Button(UIElement):
    """
    A clickable button element that renders using styled segments.
    This render method mirrors the logic of your print_button function.
    """
    def __init__(self, width, height, content="",
                 box_top: str = '▁', box_left: str = '▎',
                 box_right: str = '▕', box_bottom: str = '▔',
                 space_char: str = ' ',
                 h_align: str = 'center', size: str = 'small', v_align: str = 'center',
                 partial_box: bool = False,
                 default_style: bool = True, selected: bool = False,
                 top_style=None, mid_left_style=None, mid_content_style=None,
                 mid_right_style=None, bottom_style=None, newline_style='default',
                 offset_x=0, offset_y=0, relative=True, wide_borders=False, on_click=None):
        super().__init__(width, height, offset_x, offset_y, relative)
        self.content = content

        # Button-specific appearance and alignment settings.
        self.box_top = box_top
        self.box_left = box_left
        self.box_right = box_right
        self.box_bottom = box_bottom
        self.space_char = space_char
        self.h_align = h_align      # 'left', 'center', or 'right'
        self.size = size            # 'small' (one-line) or 'large' (three-line)
        self.wide_borders = wide_borders
        self.v_align = v_align      # 'top', 'center', or 'bottom'
        self.partial_box = partial_box

        # Style settings.
        self.default_style = default_style
        self.selected = selected
        self.top_style = top_style
        self.mid_left_style = mid_left_style
        self.mid_content_style = mid_content_style
        self.mid_right_style = mid_right_style
        self.bottom_style = bottom_style
        self.newline_style = newline_style

        self.on_click = on_click

    def render(self, layout_mode=False):
        """
        Renders the button as a styled string using segments.
        This method mirrors your print_button logic but returns the
        assembled string instead of printing it directly.
        """
        # Evaluate content if callable.
        content = self.content() if callable(self.content) else self.content

        # Determine how many lines to render based on size.
        if self.size == 'small':
            lines = [content]
        elif self.size == 'large':
            if self.v_align == 'top':
                lines = [content, '', '']
            elif self.v_align == 'bottom':
                lines = ['', '', content]
            else:  # center
                lines = ['', content, '']
        else:
            raise ValueError("size must be either 'small' or 'large'")

        if self.wide_borders:
            # Use Box default border: (top-left, top-right, bottom-left, bottom-right, horizontal, vertical)
            box_border = ("┌", "┐", "└", "┘", "─", "│")
            tl, tr, bl, br, hz, vt = box_border

            # Determine minimal width required: content plus 2 vertical borders.
            min_width = len(content) + 2
            computed_w = self.computed_width
            width = computed_w if computed_w > min_width else min_width

            # Calculate extra horizontal space for alignment.
            extra_spaces = width - min_width
            if self.h_align == 'left':
                left_spaces = 0
                right_spaces = extra_spaces
            elif self.h_align == 'right':
                left_spaces = extra_spaces
                right_spaces = 0
            else:  # center
                left_spaces = extra_spaces // 2
                right_spaces = extra_spaces - left_spaces

            # Build the top and bottom borders using the Box style.
            top_border = f"{tl}{hz * (width - 2)}{tr}"
            bottom_border = f"{bl}{hz * (width - 2)}{br}"

            # Build the vertical borders with extra spaces.
            mod_left = vt + (self.space_char * left_spaces)
            mod_right = (self.space_char * right_spaces) + vt

            # Calculate available width for the center text.
            center_width = width - (len(mod_left) + len(mod_right))
            # Build each middle line.
            middle_lines = []
            for line in lines:
                # Ensure the text occupies the available space.
                if len(line) < center_width:
                    line = line.ljust(center_width)
                middle_line = f"{mod_left}{line}{mod_right}"
                middle_lines.append(middle_line)
            middle = "\n".join(middle_lines)

            # Combine all parts.
            return "\n".join([top_border, middle, bottom_border])

        else:

            # Compute minimum width required (based on the middle line).
            min_width = len(self.box_left + content + self.box_right)
            # Use the computed width from UIElement (if relative) or the fixed width.
            computed_w = self.computed_width
            width = computed_w if computed_w > min_width else min_width

            # Calculate extra padding for horizontal alignment.
            extra_spaces = width - min_width
            if self.h_align == 'left':
                left_spaces = 0
                right_spaces = extra_spaces
            elif self.h_align == 'right':
                left_spaces = extra_spaces
                right_spaces = 0
            else:  # center
                left_spaces = extra_spaces // 2
                right_spaces = extra_spaces - left_spaces

            mod_left = self.box_left + (self.space_char * left_spaces)
            mod_right = (self.space_char * right_spaces) + self.box_right

            # Calculate the available center width.
            left_len = len(mod_left)
            right_len = len(mod_right)
            center_width = width - (left_len + right_len)

            # Determine styles.
            if self.default_style:
                state = '_selected' if self.selected else '_unselected'
                if self.partial_box:
                    state += '_partial'
                top_style = self.top_style or f'box_top{state}'
                mid_left_style = self.mid_left_style or f'box_left{state}'
                mid_content_style = self.mid_content_style or f'box_content{state}'
                mid_right_style = self.mid_right_style or f'box_right{state}'
                bottom_style = self.bottom_style or f'box_bottom{state}'
            else:
                top_style = self.top_style
                mid_left_style = self.mid_left_style
                mid_content_style = self.mid_content_style
                mid_right_style = self.mid_right_style
                bottom_style = self.bottom_style

            # Build top and bottom segments.
            top_seg = build_top_line(self.box_top, width, top_style, self.partial_box)
            bottom_seg = build_bottom_line(self.box_bottom, width, bottom_style, self.partial_box)

            # Build middle segments.
            middle_segments = []
            for i, line in enumerate(lines):
                # Pad the line if it's shorter than the center width.
                if len(line) < center_width:
                    line = line.ljust(center_width)
                mid_line_segments = build_middle_line(mod_left, line, mod_right,
                                                      mid_left_style, mid_content_style, mid_right_style)
                middle_segments.extend(mid_line_segments)
                # Add a newline segment if not the last middle line.
                if i < len(lines) - 1:
                    middle_segments.append(Segment("\n", self.newline_style))

            newline_seg = Segment("\n", self.newline_style)
            final_segments = [top_seg, newline_seg] + middle_segments + [newline_seg, bottom_seg]

            # Combine the segments into a single string.
            rendered_string = "".join(seg.text for seg in final_segments)
            return rendered_string


    def click(self):
        """Triggers the on_click callback if one is defined."""
        if callable(self.on_click):
            self.on_click()
        else:
            print("Button clicked, but no action is defined.")




class PrintsUI:
    def __init__(self, pc):
        """
        A high-level UI helper class that builds upon PrintsCharming.

        :param pc: An instance of PrintsCharming
        """
        self.pc = pc
        self.master_layout = MasterLayout
        self.layout = Layout
        self.box = Box
        self.button = Button
        self.write = self.pc.write
        self.shared_byte_map = self.pc.__class__.shared_byte_map
        self.button_positions = {}



    def init_ui(self):
        """Handles common UI setup logic."""
        #self.write("alt_buffer", "enable_mouse", "enable_sgr_mouse", "hide_cursor")
        self.pc.__class__.write("alt_buffer", "hide_cursor")


    def cleanup_ui(self):
        """Handles common UI cleanup logic."""
        #self.write("disable_mouse", "disable_sgr_mouse", "show_cursor", "normal_buffer")
        self.pc.__class__.write("show_cursor", "normal_buffer")

    def refresh(self):
        """Clears the terminal and renders the current UI."""
        os.system('clear')
        print(self.master_layout.render())

    def sigwinch_handler(self, signum, frame):
        """
        Handles terminal resize events by updating layout dimensions and refreshing the UI.
        This method can be registered with the SIGWINCH signal.
        """
        self.master_layout.update_terminal_size()
        self.refresh()

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



########################################
# Functions to refresh and handle resize
########################################

def refresh_layout(master_layout):
    os.system('clear')
    print(master_layout.render())

def sigwinch_handler(signum, frame):
    master_layout.update_terminal_size()
    refresh_layout(master_layout)

# Set up the SIGWINCH handler for terminal resize events.
signal.signal(signal.SIGWINCH, sigwinch_handler)

########################################
# Main demo configuration
########################################


def main():
    init_ui()
    # Create a main layout that occupies 80% of the width and 90% of the height,
    # and is offset by 10% from the left and 5% from the top.
    main_layout = Layout(
        relative_width=0.8,
        relative_height=0.90,
        relative_offset_x=0.10,
        relative_offset_y=0.05,
        border=True,
    )
    master_layout.add_sublayout(main_layout)


    # Add three nested layouts (e.g., header, content, footer) inside the main layout.
    header = Layout(relative_width=0.7, relative_height=0.2,
                    relative_offset_x=0, relative_offset_y=0, border=True)
    header_right = Layout(relative_width=0.30, relative_height=0.2,
                          relative_offset_x=0.70, relative_offset_y=0, border=True)

    content = Layout(relative_width=1.0, relative_height=0.6,
                     relative_offset_x=0, relative_offset_y=0.2, border=True)
    footer = Layout(relative_width=1.0, relative_height=0.2,
                    relative_offset_x=0, relative_offset_y=0.8, border=True)

    main_layout.add_sublayout(header)
    main_layout.add_sublayout(header_right)

    main_layout.add_sublayout(content)
    main_layout.add_sublayout(footer)


    # Place a Box into each of the nested layouts.
    header_box = Box(0.95, 1, content="Header Box", offset_x=0.05, offset_y=0, relative=True)
    header.add_box(header_box)

    header_right_box = Box(1, 1, content="Header Right Box", relative=True)
    header_right.add_box(header_right_box)

    content_box = Box(1, 1, content="Main Content Box", relative=True)
    content.add_box(content_box)

    footer_button = Button(0.25, 1, content="Footer Button1", offset_y=0.25, relative=True)
    footer.add_box(footer_button)

    footer_button2 = Button(0.25, 1, content="Footer Button2", offset_x=0.25, offset_y=0.25, wide_borders=True, relative=True)
    footer.add_box(footer_button2)

    footer_button3 = Button(0.25, 1, content="Footer Button3", offset_x=0.5, size='large', relative=True)
    footer.add_box(footer_button3)

    footer_button4 = Button(0.25, 1, content="Footer Button4", offset_x=0.75, size='large', wide_borders=True, relative=True)
    footer.add_box(footer_button4)

    # Initial render.
    refresh_layout(master_layout)

    # Keep the program running to handle dynamic resizing.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting.")
        cleanup_ui()





if __name__ == "__main__":
    # Create a global MasterLayout instance.
    master_layout = MasterLayout()
    pc = PrintsCharming()
    main()


