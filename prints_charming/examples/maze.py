import asyncio
import os
import time
import random
import math
import re
from typing import Optional, Dict, Set, Union
from prints_charming import PStyle, PrintsCharming, FrameBuilder, TableManager, BoundCell, InteractiveMenu


maze_styles = {
    'default': PStyle(),
    'wall_style': PStyle(color='orange'),
    'wall_style_plus': PStyle(color='vgreen'),
    'wall_style_minus': PStyle(color='vred'),
    'wall_style_pipe': PStyle(color='orange'),
    'border_top': PStyle(bg_color='dblue'),
    'border_left': PStyle(bg_color='purple'),
    'border_right': PStyle(bg_color='purple'),
    'path_style': PStyle(bg_color='purple'),
    'solved_path': PStyle(bg_color='vyellow'),
    'orange': PStyle(color='orange'),
    'purple': PStyle(color='purple'),
    'red': PStyle(color='red'),
    'vcyan': PStyle(color='vcyan'),
    'vgreen': PStyle(color='vgreen', bold=True),
    'blue': PStyle(bg_color='blue'),
    'black': PStyle(bg_color='black'),
    'vwhite': PStyle(color='white', bold=True),
    'cyan': PStyle(color='cyan', bold=True),
    'yellow': PStyle(color='yellow', bold=True),
    'start_end_style': PStyle(color='cyan', bold=True),
    "alive_cell": PStyle(color='vred', bold=True),
    'dead_cell': PStyle(color='pink', dim=True),
}



class BasePattern:
    """
    An optional base class you can extend for common logic.
    """
    def __init__(
        self,
        pc_instance: Optional[PrintsCharming] = None,
        fb_instance: Optional[FrameBuilder] = None,
        alt_buffer: bool = True,
        animate: bool = True,
        animate_interval: float = 0.01,
        menu: Optional[InteractiveMenu] = None,
        **kwargs
    ):
        self.pc = pc_instance or PrintsCharming(styles=maze_styles)
        self.fb = fb_instance or FrameBuilder(self.pc, vert_char=' ')
        self.alt_buffer = alt_buffer
        self.animate = animate
        self.animate_interval = animate_interval
        self.menu = menu

    async def init_pattern(self):
        """ Stub method for initialization. """
        if self.alt_buffer:
            self.pc.write('alt_buffer', 'cursor_home', 'hide_cursor')

    async def run_pattern(self):
        """ Stub method for generating or animating the pattern. """
        pass

    def draw_border(self, width, height):

        horiz_border = self.pc.apply_style('border_top', self.fb.horiz_border)
        avail_width = self.fb.get_available_width()
        left_border = self.pc.apply_style('border_left', self.fb.vert_border) + self.fb.vert_padding
        right_border = self.fb.vert_padding + self.pc.apply_style('border_right', self.fb.vert_border)
        # Top border
        print(horiz_border)
        # Side borders
        for _ in range(height - 2):
            line = left_border
            line += self.pc.apply_style('default', self.fb.align_text(' ', avail_width, 'center'))
            line += right_border
            print(line)
        # Bottom border
        print(horiz_border)

    def display_bottom_menu(self):
        """
        Example method to reuse your existing bottom-of-screen menu logic,
        if you want each pattern to show a little menu or let the user quit.
        For brevity, this just returns if user hits 'q'.
        You can integrate your actual InteractiveMenu logic here or call
        self.menu.display_bottom_maze_menu() if that’s suitable.
        """
        if not self.menu:
            return None

        # Reuse your Maze code’s bottom menu logic or a simplified version:
        confirmed_option = None
        message_row = 39  # arbitrary row for messages
        self.pc.write('cursor_position', row=message_row, col=3)
        self.pc.print("Press 'q' to quit or any other key to continue...", style='vgreen')

        while True:
            key = self.menu.get_key()
            if key == 'q':
                if self.alt_buffer:
                    self.pc.write('normal_buffer', 'show_cursor')
                return "Quit"
            else:
                break

        return confirmed_option



class MultiRuleCellularAutomata(BasePattern):
    """
    A multi-rule, interactive, and exportable CA with:
      - Aging cells
      - 4 different "Life-like" rules you can switch on the fly
      - Edit mode for painting cells
      - Fractal-wave synergy toggle
      - Procedural dungeon export
    """

    def __init__(
        self,
        pc_instance=None,
        fb_instance=None,
        alt_buffer=True,
        animate=True,
        animate_interval=0.05,
        menu=None,
        width=None,
        height=None,
        **kwargs
    ):
        super().__init__(pc_instance, fb_instance, alt_buffer, animate, animate_interval, menu, **kwargs)

        full_height = self.fb.terminal_height - 2
        self.ca_height = max(1, full_height - 1)
        interior_width = self.fb.get_available_width()
        self.ca_width = interior_width

        if width is not None:
            self.ca_width = min(width, interior_width)
        if height is not None:
            self.ca_height = min(height, full_height - 1)

        # Grid with "ages" (0 = dead, 1..10 = alive)
        self.grid = [[0]*self.ca_width for _ in range(self.ca_height)]

        # Current rule sets
        # We'll store them as (birth_set, survive_set)
        # E.g. for Classic: birth={3}, survive={2,3}
        # We'll also keep HighLife, Seeds, Custom
        self.rules_map: Dict[str, (Set[int], Set[int])] = {
            "Classic": ({3}, {2, 3}),     # B3/S23
            "HighLife": ({3, 6}, {2, 3}), # B36/S23
            "Seeds": ({2}, set()),        # B2/S (no survival)
            "Custom": ({3}, {2, 3}),      # starts as B3/S23 but user can mutate
        }
        self.current_rule = "Classic"

        # For toggling fractal/wave synergy
        self.fractal_wave_on = False

        # For editing mode
        self.edit_mode = False
        self.cursor_x = self.ca_width // 2
        self.cursor_y = self.ca_height // 2

        # For controlling the simulation
        self.paused = False

    async def init_pattern(self):
        if self.alt_buffer:
            self.pc.write("alt_buffer", "cursor_home", "hide_cursor")
        self.draw_border(self.fb.horiz_width, self.pc.terminal_height - 1)

        # Random initial seed
        self.randomize_grid()

        self.setup_bottom_menu()

    def randomize_grid(self, density=0.2):
        """
        20% chance a cell is alive by default.
        """
        for y in range(self.ca_height):
            for x in range(self.ca_width):
                self.grid[y][x] = 1 if (random.random() < density) else 0

    def setup_bottom_menu(self):
        """
        Menu Items:
          1) Pause/Resume
          2) Step
          3) Faster
          4) Slower
          5) Change Rule
          6) Toggle Edit
          7) Export Dungeon
          8) Toggle FractalWave
          9) Quit
        """
        if not self.menu:
            return
        self.menu.menus = {
            "multi_ca_menu": [
                "Pause/Resume",
                "Step",
                "Faster",
                "Slower",
                "Change Rule",
                "Toggle Edit",
                "Export Dungeon",
                "FractalWave Off",
                "Back",
                "Quit"
            ]
        }
        self.menu.current_menu = "multi_ca_menu"
        self.menu.selected_index = 0

    def display_bottom_maze_menu(self):
        if not self.menu:
            return
        self.menu.menu_start_row = self.pc.terminal_height - 2
        self.menu.menu_start_column = 4
        self.menu.display_highlighted_menu(clear_display=False)

    async def run_pattern(self):
        key_reader = self.menu.async_key_reader()
        try:
            while True:
                # 1) Render
                self.render_grid()

                # If in edit mode, highlight the cursor
                if self.edit_mode:
                    self.render_edit_cursor()

                # 2) Bottom menu
                self.display_bottom_maze_menu()

                # 3) Sleep
                await asyncio.sleep(self.animate_interval)

                # 4) If not paused, do an update
                if not self.paused:
                    self.update_grid()
                    if self.fractal_wave_on:
                        self.infuse_fractal_wave()

                # 5) Non-blocking key read
                try:
                    ch = key_reader.get_key_nowait()
                    if ch == 'q':
                        if self.alt_buffer:
                            self.pc.write("normal_buffer", "show_cursor")
                        return "Quit"
                    result = self.handle_bottom_menu_input(ch)
                    if result == "Quit":
                        if self.alt_buffer:
                            self.pc.write("normal_buffer", "show_cursor")
                        return "Quit"
                    elif result == "Back":
                        if self.alt_buffer:
                            self.pc.write("normal_buffer", "show_cursor")
                        return "Back"
                except asyncio.QueueEmpty:
                    pass

        finally:
            key_reader.restore_tty()

    def render_grid(self):
        start_row = 2
        start_col = self.fb.vert_width + len(self.fb.vert_padding) + 1

        for y in range(self.ca_height):
            self.pc.write("cursor_position", row=start_row + y, col=start_col)
            line_parts = []
            for x in range(self.ca_width):
                age = self.grid[y][x]
                if age == 0:
                    line_parts.append(self.pc.apply_style('dead_cell', '.'))
                elif age == 1:
                    line_parts.append(self.pc.apply_style('alive_cell', 'o'))
                elif age == 2:
                    line_parts.append(self.pc.apply_style('red', 'O'))
                else:
                    line_parts.append(self.pc.apply_style('vcyan', '@'))
            print(''.join(line_parts))

    def render_edit_cursor(self):
        """
        Visually highlight the cell under the cursor (like an inverted color).
        We'll just place an 'X' or something.
        """
        # Make sure the cursor is in bounds
        cx = max(0, min(self.ca_width - 1, self.cursor_x))
        cy = max(0, min(self.ca_height - 1, self.cursor_y))

        start_row = 2 + cy
        start_col = self.fb.vert_width + len(self.fb.vert_padding) + 1 + cx

        self.pc.write("cursor_position", row=start_row, col=start_col)
        self.pc.write("reverse_video")
        age = self.grid[cy][cx]
        char = '.'
        if age == 1:
            char = 'o'
        elif age == 2:
            char = 'O'
        elif age >= 3:
            char = '@'
        else:
            char = '.'
        print(char, end="", flush=True)
        self.pc.write("reset_attributes")

    def update_grid(self):
        """
        Use self.current_rule to get the birth/survive sets. Then apply aging.
        """
        birth, survive = self.rules_map[self.current_rule]

        new_grid = [[0]*self.ca_width for _ in range(self.ca_height)]
        for y in range(self.ca_height):
            for x in range(self.ca_width):
                age = self.grid[y][x]
                n = self.count_neighbors(x, y)
                if age > 0:
                    # cell is alive
                    if n in survive:
                        new_grid[y][x] = min(age + 1, 10)
                    else:
                        new_grid[y][x] = 0
                else:
                    # cell is dead
                    if n in birth:
                        new_grid[y][x] = 1
        self.grid = new_grid

    def count_neighbors(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = x + dx
                ny = y + dy
                if 0 <= nx < self.ca_width and 0 <= ny < self.ca_height:
                    if self.grid[ny][nx] > 0:
                        count += 1
        return count

    def infuse_fractal_wave(self):
        """
        Silly synergy: each generation, we randomly pick some cells near
        the "middle row" and birth them if they are dead, or kill them
        if they're old, etc. Could also combine fractal or wave logic.
        This is just a placeholder for truly weird synergy.
        """
        mid = self.ca_height // 2
        for x in range(self.ca_width):
            if random.random() < 0.02:  # 2% chance
                y = mid + int(3 * math.sin(x/4 + random.random()*2))
                if 0 <= y < self.ca_height:
                    # Flip that cell
                    if self.grid[y][x] == 0:
                        self.grid[y][x] = 1
                    else:
                        self.grid[y][x] = 0

    def handle_bottom_menu_input(self, ch):
        """
        We'll handle arrow keys for editing mode, plus the menu's Enter key.
        If user is in edit mode, pressing 'p' toggles a cell.
        We'll also handle the main commands from the menu.
        """
        if not self.menu:
            return None

        # If in edit mode, arrow keys move the cursor
        if self.edit_mode:
            if ch in ['arrow_up', 'k']:
                self.cursor_y = max(0, self.cursor_y - 1)
            elif ch in ['arrow_down', 'j']:
                self.cursor_y = min(self.ca_height - 1, self.cursor_y + 1)
            elif ch in ['arrow_left', 'h']:
                self.cursor_x = max(0, self.cursor_x - 1)
            elif ch in ['arrow_right', 'l']:
                self.cursor_x = min(self.ca_width - 1, self.cursor_x + 1)
            elif ch == 'p':
                # Toggle the cell at cursor
                cy, cx = self.cursor_y, self.cursor_x
                if self.grid[cy][cx] > 0:
                    self.grid[cy][cx] = 0
                else:
                    self.grid[cy][cx] = 1
            # We also want to check if the user pressed Enter for menu
            if ch == '\r':
                choice = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
                return self.execute_menu_choice(choice)
            return None

        # Otherwise, normal arrow-based menu navigation
        if ch in ['k', 'arrow_up', 'arrow_left']:
            self.menu.navigate(-1, clear_display=False)
        elif ch in ['j', 'arrow_down', 'arrow_right']:
            self.menu.navigate(1, clear_display=False)
        elif ch == '\r':
            # Confirm
            choice = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
            return self.execute_menu_choice(choice)

        return None

    def execute_menu_choice(self, choice):
        if choice == "Pause/Resume":
            self.paused = not self.paused
        elif choice == "Step":
            # Single-step if paused
            if self.paused:
                self.update_grid()
                if self.fractal_wave_on:
                    self.infuse_fractal_wave()
        elif choice == "Faster":
            self.animate_interval = max(0.01, self.animate_interval - 0.02)
        elif choice == "Slower":
            self.animate_interval = min(1.0, self.animate_interval + 0.02)
        elif choice == "Change Rule":
            self.change_rule_via_submenu()
        elif choice == "Toggle Edit":
            self.edit_mode = not self.edit_mode
        elif choice == "Export Dungeon":
            self.export_dungeon()
        elif choice.startswith("FractalWave"):
            # Toggle fractal wave
            if self.fractal_wave_on:
                self.fractal_wave_on = False
                # update menu text
                idx = self.menu.menus[self.menu.current_menu].index(choice)
                self.menu.menus[self.menu.current_menu][idx] = "FractalWave Off"
            else:
                self.fractal_wave_on = True
                idx = self.menu.menus[self.menu.current_menu].index(choice)
                self.menu.menus[self.menu.current_menu][idx] = "FractalWave On"
        elif choice == "Back":
            # Return a special signal so run_pattern() can exit and go back to main menu
            return "Back"
        elif choice == "Quit":
            return "Quit"
        return None


    def change_rule_via_submenu(self):
        """
        We'll show a small interactive submenu to let the user pick:
         1) Classic
         2) HighLife
         3) Seeds
         4) Custom (and possibly tweak B/S sets?)
        For brevity, let's do a mini interactive approach inside the console.
        """
        # If you want to do a fancy InteractiveMenu approach, you can.
        # We'll do a quick prompt approach for demonstration.
        self.pc.print("Available Rules:", style='vcyan')
        rules = list(self.rules_map.keys())  # ["Classic", "HighLife", "Seeds", "Custom"]
        for i, rname in enumerate(rules, start=1):
            self.pc.print(f"{i}. {rname}", style='default')
        self.pc.print("Enter a number to pick your rule (or press Enter to cancel).", style='vwhite')

        user_input = self.menu.get_key()  # This blocks for one char
        if user_input.isdigit():
            choice_idx = int(user_input)
            if 1 <= choice_idx <= len(rules):
                self.current_rule = rules[choice_idx - 1]
                self.pc.print(f"Switched to rule: {self.current_rule}", style='vcyan')
                return
        self.pc.print("Rule change canceled or invalid input.", style='vred')

    def export_dungeon(self, file_path="dungeon_export.txt"):
        """
        Interprets alive cells as '.' (floor) and dead cells as '#' (wall).
        Prints to console as a basic ASCII “dungeon.”
        In practice, you might write this to a file or feed into a game engine.
        """

        try:
            with open(file_path, "a") as file:
                file.write("\n--- DUNGEON EXPORT ---\n")
                for y in range(self.ca_height):
                    row_str = []
                    for x in range(self.ca_width):
                        if self.grid[y][x] > 0:
                            row_str.append('.')
                        else:
                            row_str.append('#')
                    file.write(''.join(row_str) + "\n")
                file.write("--- End of Dungeon Export ---\n")
            self.pc.print(f"Dungeon successfully appended to {file_path}", style='vgreen')
        except Exception as e:
            self.pc.print(f"Failed to export dungeon: {e}", style='vred')



"""
class Maze:
    def __init__(
        self,
        pc_instance: Optional[PrintsCharming] = None,
        fb_instance: Optional[FrameBuilder] = None,
        grid_width: Optional[int] = None,
        grid_height: Optional[int] = None,
        alt_buffer: bool = True,
        animate: bool = True,
        animate_interval: float = 0.001,
        menu: Optional[InteractiveMenu] = None,
        **kwargs
    ) -> None:

        self.pc = pc_instance or PrintsCharming(
            styles=maze_styles if maze_styles else None,
            **kwargs.get("pc_params", {})
        )
        self.fb = fb_instance or FrameBuilder(self.pc, vert_char=' ')
        self.grid_width = grid_width
        self.grid_height = grid_height

        if not grid_width or not grid_height:
            self.get_grid_dimensions()

        self.alt_buffer = alt_buffer
        self.animate = animate
        self.animate_interval = animate_interval

        # Initialize the maze grid with walls on all sides
        self.maze = [
            [{'N': True, 'S': True, 'E': True, 'W': True} for _ in range(self.grid_width)]
            for _ in range(self.grid_height)
        ]
        self.visited = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        self.maze_start_column = None
        self.maze_start_row = None
        self.maze_end_row = None

        self.menu = menu




    def get_grid_dimensions(self):
        # Calculate available width and height inside borders
        available_width = self.fb.get_available_width()
        available_height = self.fb.terminal_height - 2

        # Estimate cell dimensions dynamically
        # Measure the width of a cell in characters
        # Build a sample cell line to measure its length
        sample_top_cell_contents = ['+', '---', '+']
        sample_top_cell_styles = ['wall_style_plus', 'wall_style_minus', 'wall_style_plus']
        sample_top_cell = self.pc.apply_styles(sample_top_cell_contents, sample_top_cell_styles, '')

        sample_middle_cell_contents = ['|', '   ', '|']
        sample_middle_cell_styles = ['wall_style_pipe', 'path_style']
        sample_middle_cell = self.pc.apply_styles(sample_middle_cell_contents, sample_middle_cell_styles, '')

        # Calculate the visible length of the sample cell lines
        # cell_width = len(fb.strip_ansi_escape_sequences(sample_top_cell)) - 1  # Subtract 1 to account for overlap
        cell_width = len(''.join(sample_top_cell_contents)) - 1  # Subtract 1 to account for overlap
        cell_height = 2  # Each cell is 2 lines high

        # Calculate maximum number of cells that can fit in the available space
        max_maze_width = max(available_width // cell_width, 1)
        max_maze_height = max((available_height - 2) // cell_height, 1)

        # Adjust the maze size
        #self.grid_width = max_maze_width + 1
        self.grid_width = max_maze_width
        self.grid_height = max_maze_height



    async def init_maze(self):
        if self.alt_buffer:
            self.pc.write('alt_buffer', 'cursor_home', 'hide_cursor')

        # Draw border once at the start of the game
        self.draw_border(self.fb.horiz_width, self.pc.terminal_height - 1)


    def reset_maze(self):
        # Reset visited cells and maze structure
        self.visited = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.maze = [
            [{'N': True, 'S': True, 'E': True, 'W': True} for _ in range(self.grid_width)]
            for _ in range(self.grid_height)
        ]


    def draw_border(self, width, height):

        
        # Build styled borders
        #(horiz_border_top,
         #vert_border_left,
         #vert_border_inner,
         #vert_border_right,
         #horiz_border_bottom) = self.fb.build_styled_border_box(horiz_style='blue', vert_style='purple')
        

        horiz_border = self.pc.apply_style('border_top', self.fb.horiz_border)
        avail_width = self.fb.get_available_width()
        left_border = self.pc.apply_style('border_left', self.fb.vert_border) + self.fb.vert_padding
        right_border = self.fb.vert_padding + self.pc.apply_style('border_right', self.fb.vert_border)
        # Top border
        print(horiz_border)
        # Side borders
        for _ in range(height - 2):
            line = left_border
            line += self.pc.apply_style('default', self.fb.align_text(' ', avail_width, 'center'))
            #line += self.pc.apply_style('default', self.fb.align_text(' '))
            line += right_border
            print(line)
        # Bottom border
        print(horiz_border)



    def display_bottom_maze_menu(self):

        self.menu.menu_start_column = self.maze_start_column
        self.menu.menu_start_row = self.maze_end_row + 1
        self.menu.display_highlighted_menu(clear_display=False)

        confirmed_option = None

        message_row = self.menu.menu_start_row + len(self.menu.menus[self.menu.current_menu]) + 10  # Define a row for messages

        if not self.menu.enable_frames_and_tables:

            while True:
                # Clear the input line before capturing the next input
                self.pc.write('cursor_position', row=message_row, col=self.menu.menu_start_column)
                self.pc.write('clear_line')  # Clear the current input line

                key = self.menu.get_key()

                if key == 'q':
                    # Quit this menu
                    if self.alt_buffer:
                        self.pc.write('normal_buffer', '\n', 'show_cursor')
                    return "Quit"  # Explicitly return "Quit"



                if not self.menu.enable_expand_submenu:

                    if key in ['k', 'h', self.pc.ctl_map['arrow_up'], self.pc.ctl_map['arrow_left']]:
                        self.menu.navigate(-1, clear_display=False)
                        # Clear any existing message
                        self.pc.write('cursor_position', row=message_row, col=self.menu.menu_start_column)
                        self.pc.write('clear_line')

                    elif key in ['j', 'l', self.pc.ctl_map['arrow_down'], self.pc.ctl_map['arrow_right']]:
                        self.menu.navigate(1, clear_display=False)
                        # Clear any existing message
                        self.pc.write('cursor_position', row=message_row, col=self.menu.menu_start_column)
                        self.pc.write('clear_line')

                    elif key == '\r':
                        confirmed_option = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
                        if confirmed_option == "Quit":
                            if self.alt_buffer:
                                self.pc.write('normal_buffer', '\n', 'show_cursor')
                            return "Quit"
                        elif confirmed_option == "Create Maze":
                            return "Create Maze"

                        break


                    elif key.isdigit():
                        num = int(key)
                        menu_length = len(self.menu.menus[self.menu.current_menu])
                        if 1 <= num <= menu_length:
                            self.menu.selected_index = num - 1
                            self.menu.display_highlighted_menu(clear_display=False)
                            if self.menu.confirm_select_digit_key:
                                confirmed_option = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
                                break
                        else:
                            self.pc.write('cursor_position', row=message_row, col=self.menu.menu_start_column)

                            self.pc.print(f"\nInvalid selection: {num}. Please select a valid option.", style='vred')

                else:
                    if key in ['k', 'h', self.pc.ctl_map['arrow_up'], self.pc.ctl_map['arrow_left']]:
                        self.menu.selected_index = (self.menu.selected_index - 1) % len(self.menu.menus[self.menu.current_menu])
                        self.menu.display_highlighted_menu(clear_display=False)

                    elif key in ['j', 'l', self.pc.ctl_map['arrow_down'], self.pc.ctl_map['arrow_right']]:
                        self.menu.selected_index = (self.menu.selected_index + 1) % len(self.menu.menus[self.menu.current_menu])
                        self.menu.display_highlighted_menu(clear_display=False)


                    elif key == '\r':
                        current_option = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
                        if isinstance(current_option, dict):
                            # Toggle submenu expansion
                            self.menu.toggle_submenu(self.menu.selected_index)
                            # Re-display after expansion/collapse
                            self.menu.display_highlighted_menu(clear_display=False)
                            continue  # Don't break; allow user to navigate new expanded/collapsed menu
                        else:
                            # Confirm a non-dict option
                            confirmed_option = current_option

                            if confirmed_option == "Quit":
                                if self.alt_buffer:
                                    self.pc.write('normal_buffer', 'show_cursor')
                                return "Quit"
                            elif confirmed_option == "Create Maze":
                                return "Create Maze"

                            break

                    elif key.isdigit():
                        num = int(key)
                        menu_length = len(self.menu.menus[self.menu.current_menu])
                        if 1 <= num <= menu_length:
                            self.menu.selected_index = num - 1
                            self.menu.display_highlighted_menu(clear_display=False)
                            if self.menu.confirm_select_digit_key:
                                current_option = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
                                if isinstance(current_option, dict):
                                    self.menu.toggle_submenu(self.menu.selected_index)
                                    self.menu.display_highlighted_menu(clear_display=False)
                                    continue
                                else:
                                    confirmed_option = current_option
                                    break
                        else:
                            self.pc.write('cursor_position', row=message_row, col=self.menu.menu_start_column)
                            self.pc.print(f"\nInvalid selection: {num}. Please select a valid option.", style='vred')
        else:
            tm = TableManager(pc=self.pc)
            fb = self.fb

            while True:
                self.pc.write('cursor_position', row=message_row, col=self.menu.menu_start_column)
                self.pc.write('clear_line')
                key = self.menu.get_key()

                if key == 'q':
                    if self.menu.alt_buffer:
                        self.pc.write('normal_buffer', 'show_cursor')
                    return None

                elif key in ['k', 'h', self.pc.ctl_map['arrow_up'], self.pc.ctl_map['arrow_left']]:
                    self.menu.selected_index = (self.menu.selected_index - 1) % len(self.menu.menus[self.menu.current_menu])
                    self.menu.display_highlighted_menu(clear_display=False)

                elif key in ['j', 'l', self.pc.ctl_map['arrow_down'], self.pc.ctl_map['arrow_right']]:
                    self.menu.selected_index = (self.menu.selected_index + 1) % len(self.menu.menus[self.menu.current_menu])
                    self.menu.display_highlighted_menu(clear_display=False)

                elif key in ['\r', ' ']:  # Enter or space toggles expansions if dict, confirms if normal option
                    current_option = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
                    if isinstance(current_option, dict):
                        # Toggle submenu expansion
                        self.menu.toggle_submenu(self.menu.selected_index)
                        self.menu.display_highlighted_menu(clear_display=False)

                        # Example: Use TableManager to print some info after toggling (adapt as needed)
                        info_table = [
                            ["Status", "Action"],
                            ["Toggled", "Expansion" if (self.menu.current_menu, self.menu.selected_index) in self.menu.expanded_submenus else "Collapse"]
                        ]
                        table_str = tm.generate_table(info_table, table_name="toggle_info", show_table_name=True, border_style="vblue", target_text_box=True)
                        self.pc.print(table_str)

                        # Example: Use FrameBuilder to print a framed message
                        fb.print_border_boxed_text2(
                            texts=[["Expansion toggled"]],
                            style='default',
                            horiz_style='vblue',
                            vert_style='vblue',
                            border_top=True, border_bottom=True, border_left=True, border_right=True,
                            border_inner=False
                        )
                        continue
                    else:
                        # Confirm a non-dict option if Enter pressed
                        if key == '\r':
                            confirmed_option = current_option
                            break
                        # If space pressed on a non-dict, do nothing special (just continue navigation)
                        continue

                elif key.isdigit():
                    num = int(key)
                    menu_length = len(self.menu.menus[self.menu.current_menu])
                    if 1 <= num <= menu_length:
                        self.menu.selected_index = num - 1
                        self.menu.display_highlighted_menu(clear_display=False)
                        # If confirm_select_digit_key is True, confirm immediately
                        if self.menu.confirm_select_digit_key:
                            current_option = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
                            if isinstance(current_option, dict):
                                self.menu.toggle_submenu(self.menu.selected_index)
                                self.menu.display_highlighted_menu(clear_display=False)
                                continue
                            else:
                                confirmed_option = current_option
                                break
                    else:
                        self.pc.write('cursor_position', row=message_row, col=self.menu.menu_start_column)
                        self.pc.print(f"\nInvalid selection: {num}. Please select a valid option.", style='vred')

        if self.alt_buffer:
            self.pc.write('normal_buffer', 'show_cursor')

        if confirmed_option and not isinstance(confirmed_option, dict):
            self.pc.print(f'confirmed_option: {confirmed_option}', style={1: self.menu.confirmed_style, (2, 3): self.menu.selected_style})

        return self.menu.selected_index + 1



    async def generate_maze(self, x=0, y=0):
        self.visited[y][x] = True
        if self.animate:
            await self.display_partial_maze(x, y)

        directions = ['N', 'S', 'E', 'W']
        random.shuffle(directions)
        for direction in directions:
            nx, ny = x, y
            if direction == 'N':
                ny -= 1
            elif direction == 'S':
                ny += 1
            elif direction == 'E':
                nx += 1
            elif direction == 'W':
                nx -= 1
            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height and not self.visited[ny][nx]:
                # Remove walls between current cell and next cell
                self.maze[y][x][direction] = False
                opposite = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
                self.maze[ny][nx][opposite[direction]] = False
                result = await self.generate_maze(nx, ny)
                if result == "Quit":
                    return "Quit"  # Propagate "Quit" back

        # Only display the menu after the entire maze is generated
        if self.menu and all(all(row) for row in self.visited):
            result = self.display_bottom_maze_menu()
            if result == "Quit":
                return "Quit"
            elif result == "Create Maze":
                self.reset_maze()
                return await self.generate_maze()



    async def display_partial_maze(self, cx, cy):
        maze_lines = []
        for y in range(self.grid_height):
            # Top line of the current row
            top_line_chars = []
            for x in range(self.grid_width):
                cell = self.maze[y][x]
                top_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
                if cell['N']:
                    top_line_chars.append(self.pc.apply_style('wall_style_minus', '---'))
                else:
                    top_line_chars.append(self.pc.apply_style('path_style', '   '))
            top_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
            maze_lines.append(''.join(top_line_chars))

            # Middle line of the current row
            middle_line_chars = []
            for x in range(self.grid_width):
                cell = self.maze[y][x]
                if cell['W']:
                    middle_line_chars.append(self.pc.apply_style('wall_style_pipe', '|'))
                else:
                    middle_line_chars.append(self.pc.apply_style('path_style', ' '))
                if (x, y) == (cx, cy):
                    middle_line_chars.append(self.pc.apply_style('start_end_style', ' @ '))  # Current cell
                elif (x, y) == (0, 0):
                    middle_line_chars.append(self.pc.apply_style('start_end_style', ' S '))
                elif (x, y) == (self.grid_width - 1, self.grid_height - 1):
                    middle_line_chars.append(self.pc.apply_style('start_end_style', ' E '))
                else:
                    middle_line_chars.append(self.pc.apply_style('path_style', '   '))
            if self.maze[y][self.grid_width - 1]['E']:
                middle_line_chars.append(self.pc.apply_style('wall_style_pipe', '|'))
            else:
                middle_line_chars.append(self.pc.apply_style('path_style', ' '))
            maze_lines.append(''.join(middle_line_chars))

        # Bottom line of the last row
        bottom_line_chars = []
        for x in range(self.grid_width):
            bottom_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
            if self.maze[self.grid_height - 1][x]['S']:
                bottom_line_chars.append(self.pc.apply_style('wall_style_minus', '---'))
            else:
                bottom_line_chars.append(self.pc.apply_style('path_style', '   '))
        bottom_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
        maze_lines.append(''.join(bottom_line_chars))

        maze_start_row = 2  # Adjust this value based on your top border height
        self.maze_start_row = maze_start_row
        maze_start_column = self.fb.vert_width + len(self.fb.vert_padding) + 1  # Adjust this value based on your left border width
        self.maze_start_column = maze_start_column

        self.pc.write("cursor_position", row=maze_start_row, col=maze_start_column)

        # Print the maze lines
        for i, line in enumerate(maze_lines):
            row = maze_start_row + i
            # Adjust cursor position for each line
            self.pc.write("cursor_position", row=row, col=maze_start_column)
            print(line)
            self.maze_end_row = row
        await asyncio.sleep(self.animate_interval)  # Delay for animation effect


    def display_maze(self, pc, fb):
        maze_lines = []

        for y in range(self.grid_height):
            # Top line of the current row
            top_line_chars = []
            for x in range(self.grid_width):
                cell = self.maze[y][x]
                # Corner
                top_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
                # Wall or passage
                if cell['N']:
                    top_line_chars.append(self.pc.apply_style('wall_style_minus', '---'))
                else:
                    top_line_chars.append(self.pc.apply_style('path_style', '   '))
            # Last corner
            top_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
            maze_lines.append(''.join(top_line_chars))

            # Middle line of the current row
            middle_line_chars = []
            for x in range(self.grid_width):
                cell = self.maze[y][x]
                # Wall or passage
                if cell['W']:
                    middle_line_chars.append(pc.apply_style('wall_style_pipe', '|'))
                else:
                    middle_line_chars.append(pc.apply_style('path_style', ' '))
                # Cell content
                if (x, y) == (0, 0):
                    # Start position
                    middle_line_chars.append(pc.apply_style('start_end_style', ' S '))
                elif (x, y) == (self.grid_width - 1, self.grid_height - 1):
                    # End position
                    middle_line_chars.append(pc.apply_style('start_end_style', ' E '))
                else:
                    middle_line_chars.append(pc.apply_style('path_style', '   '))
            # Last wall on the right
            if self.maze[y][self.grid_width - 1]['E']:
                middle_line_chars.append(pc.apply_style('wall_style_pipe', '|'))
            else:
                middle_line_chars.append(pc.apply_style('path_style', ' '))
            maze_lines.append(''.join(middle_line_chars))

        # Bottom line of the last row
        bottom_line_chars = []
        for x in range(self.grid_width):
            bottom_line_chars.append(pc.apply_style('wall_style_plus', '+'))
            if self.maze[self.grid_height - 1][x]['S']:
                bottom_line_chars.append(pc.apply_style('wall_style_minus', '---'))
            else:
                bottom_line_chars.append(pc.apply_style('path_style', '   '))
        bottom_line_chars.append(pc.apply_style('wall_style_plus', '+'))
        maze_lines.append(''.join(bottom_line_chars))

        # Determine the starting position for the maze within the already-drawn borders
        maze_start_line = 2  # Adjust based on your top border height
        maze_start_column = self.fb.vert_width + len(self.fb.vert_padding) + 1

        # Print each line of the maze at the correct position
        for i, line in enumerate(maze_lines):
            self.pc.write("cursor_position", row=maze_start_line + i, col=maze_start_column)
            print(line)



    async def solve_maze(self):
        start = (0, 0)  # Top-left corner
        end = (self.grid_height - 1, self.grid_width - 1)  # Bottom-right corner
        directions = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}
        queue = [(start, [start])]  # (current_position, path_traversed)
        visited = set()

        while queue:
            (y, x), path = queue.pop(0)

            if (y, x) in visited:
                continue
            visited.add((y, x))

            # If we've reached the end, highlight and return the path
            if (y, x) == end:
                await self.display_solution_path(path)
                return path

            # Explore neighbors based on the maze structure
            for direction, (dy, dx) in directions.items():
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.grid_height and 0 <= nx < self.grid_width:
                    if not self.maze[y][x][direction]:  # No wall in this direction
                        queue.append(((ny, nx), path + [(ny, nx)]))

        return None  # No solution found


    async def display_solution_path(self, path):
        # Use a special style for the solution path
        solution_style = self.pc.apply_style('solved_path', '   ')
        for (y, x) in path:
            # Animate the path cell by cell
            self.visited[y][x] = True  # Mark as visited for visual clarity
            await self.display_partial_maze(x, y)
            print(f"\033[{2 + y};{2 + x * 4}H{solution_style}", end='')  # Adjust positioning
            await asyncio.sleep(0.05)
"""

###############################################################################
# MAZE CLASS
###############################################################################
class Maze(BasePattern):
    def __init__(
        self,
        pc_instance: Optional[PrintsCharming] = None,
        fb_instance: Optional[FrameBuilder] = None,
        grid_width: Optional[int] = None,
        grid_height: Optional[int] = None,
        alt_buffer: bool = True,
        animate: bool = True,
        animate_interval: float = 0.001,
        menu: Optional[InteractiveMenu] = None,
        **kwargs
    ) -> None:
        super().__init__(pc_instance, fb_instance, alt_buffer, animate, animate_interval, menu, **kwargs)

        self.grid_width = grid_width
        self.grid_height = grid_height

        if not grid_width or not grid_height:
            self.get_grid_dimensions()

        # Initialize the maze grid with walls on all sides
        self.maze = [
            [{'N': True, 'S': True, 'E': True, 'W': True} for _ in range(self.grid_width)]
            for _ in range(self.grid_height)
        ]
        self.visited = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        self.maze_start_column = None
        self.maze_start_row = None
        self.maze_end_row = None




    def setup_bottom_menu(self, menu_name=''):
        """
        Creates a simple interactive menu stored in self.menu.
        Items: Pause/Resume, Step, Faster, Slower, Quit
        We'll position it near the bottom, above the bottom border line.
        """
        if not self.menu:
            return

        self.menu.menus = {
            "ca_menu": [
                "Pause/Resume",
                "Step",
                "Faster",
                "Slower",
                "Back",
                "Quit"
            ]
        }
        self.menu.current_menu = "ca_menu"
        self.menu.selected_index = 0

    def display_bottom_maze_menu(self):
        if not self.menu:
            return None

        self.menu.menu_start_column = self.maze_start_column
        self.menu.menu_start_row = self.maze_end_row + 1
        self.menu.display_highlighted_menu(clear_display=False)

        confirmed_option = None
        message_row = self.menu.menu_start_row + len(self.menu.menus[self.menu.current_menu]) + 10

        while True:
            self.pc.write('cursor_position', row=message_row, col=self.menu.menu_start_column)
            self.pc.write('clear_line')
            key = self.menu.get_key()

            if key == 'q':
                if self.alt_buffer:
                    self.pc.write('normal_buffer', 'show_cursor')
                return "Quit"

            elif key in ['k', 'h', self.pc.ctl_map['arrow_up'], self.pc.ctl_map['arrow_left']]:
                self.menu.navigate(-1, clear_display=False)

            elif key in ['j', 'l', self.pc.ctl_map['arrow_down'], self.pc.ctl_map['arrow_right']]:
                self.menu.navigate(1, clear_display=False)

            elif key == '\r':
                confirmed_option = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
                if confirmed_option == "Quit":
                    if self.alt_buffer:
                        self.pc.write('normal_buffer', 'show_cursor')
                    return "Quit"
                elif confirmed_option == "Create Maze":
                    return "Create Maze"
                break

            elif key.isdigit():
                num = int(key)
                menu_length = len(self.menu.menus[self.menu.current_menu])
                if 1 <= num <= menu_length:
                    self.menu.selected_index = num - 1
                    self.menu.display_highlighted_menu(clear_display=False)
                    confirmed_option = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
                    break
                else:
                    self.pc.write('cursor_position', row=message_row, col=self.menu.menu_start_column)
                    self.pc.print(f"Invalid selection: {num}. Please select a valid option.", style='vred')

        return confirmed_option

    def get_grid_dimensions(self):
        # Calculate available width and height inside borders
        available_width = self.fb.get_available_width()
        available_height = self.fb.terminal_height - 2

        sample_top_cell_contents = ['+', '---', '+']
        cell_width = len(''.join(sample_top_cell_contents)) - 1
        cell_height = 2  # Each cell is 2 lines high

        max_maze_width = max(available_width // cell_width, 1)
        max_maze_height = max((available_height - 2) // cell_height, 1)

        self.grid_width = max_maze_width
        self.grid_height = max_maze_height


    async def init_pattern(self):
        if self.alt_buffer:
            self.pc.write('alt_buffer', 'cursor_home', 'hide_cursor')
        # Draw border
        self.draw_border(self.fb.horiz_width, self.pc.terminal_height - 1)

        # Show the initial menu right away so user can see it
        # (Alternatively you could wait until user triggers something.)
        #self.display_bottom_maze_menu()


    def reset_maze(self):
        # Reset visited cells and maze structure
        self.visited = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.maze = [
            [{'N': True, 'S': True, 'E': True, 'W': True} for _ in range(self.grid_width)]
            for _ in range(self.grid_height)
        ]

    async def run_pattern(self):
        """
        Generate the maze and (optionally) show a 'bottom menu' afterwards.
        """
        # Generate Maze
        result = await self.generate_maze()
        if result == "Quit":
            return "Quit"

        # If not animate, display the final Maze once
        if not self.animate:
            self.display_maze(self.pc, self.fb)

        # Possibly show a menu or do something else
        menu_result = self.display_bottom_menu()
        if menu_result == "Quit":
            return "Quit"

    async def generate_maze(self, x=0, y=0):
        self.visited[y][x] = True
        if self.animate:
            await self.display_partial_maze(x, y)

        directions = ['N', 'S', 'E', 'W']
        random.shuffle(directions)
        for direction in directions:
            nx, ny = x, y
            if direction == 'N':
                ny -= 1
            elif direction == 'S':
                ny += 1
            elif direction == 'E':
                nx += 1
            elif direction == 'W':
                nx -= 1

            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height and not self.visited[ny][nx]:
                self.maze[y][x][direction] = False
                opposite = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
                self.maze[ny][nx][opposite[direction]] = False
                result = await self.generate_maze(nx, ny)
                if result == "Quit":
                    return "Quit"

    async def display_partial_maze(self, cx, cy):
        maze_lines = []
        for y in range(self.grid_height):
            # Top line of the current row
            top_line_chars = []
            for x in range(self.grid_width):
                cell = self.maze[y][x]
                top_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
                if cell['N']:
                    top_line_chars.append(self.pc.apply_style('wall_style_minus', '---'))
                else:
                    top_line_chars.append(self.pc.apply_style('path_style', '   '))
            top_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
            maze_lines.append(''.join(top_line_chars))

            # Middle line of the current row
            middle_line_chars = []
            for x in range(self.grid_width):
                cell = self.maze[y][x]
                if cell['W']:
                    middle_line_chars.append(self.pc.apply_style('wall_style_pipe', '|'))
                else:
                    middle_line_chars.append(self.pc.apply_style('path_style', ' '))
                if (x, y) == (cx, cy):
                    middle_line_chars.append(self.pc.apply_style('start_end_style', ' @ '))
                elif (x, y) == (0, 0):
                    middle_line_chars.append(self.pc.apply_style('start_end_style', ' S '))
                elif (x, y) == (self.grid_width - 1, self.grid_height - 1):
                    middle_line_chars.append(self.pc.apply_style('start_end_style', ' E '))
                else:
                    middle_line_chars.append(self.pc.apply_style('path_style', '   '))
            if self.maze[y][self.grid_width - 1]['E']:
                middle_line_chars.append(self.pc.apply_style('wall_style_pipe', '|'))
            else:
                middle_line_chars.append(self.pc.apply_style('path_style', ' '))
            maze_lines.append(''.join(middle_line_chars))

        # Bottom line
        bottom_line_chars = []
        for x in range(self.grid_width):
            bottom_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
            if self.maze[self.grid_height - 1][x]['S']:
                bottom_line_chars.append(self.pc.apply_style('wall_style_minus', '---'))
            else:
                bottom_line_chars.append(self.pc.apply_style('path_style', '   '))
        bottom_line_chars.append(self.pc.apply_style('wall_style_plus', '+'))
        maze_lines.append(''.join(bottom_line_chars))

        maze_start_row = 2
        self.maze_start_row = maze_start_row
        maze_start_column = self.fb.vert_width + len(self.fb.vert_padding) + 1
        self.maze_start_column = maze_start_column

        self.pc.write("cursor_position", row=maze_start_row, col=maze_start_column)

        for i, line in enumerate(maze_lines):
            row = maze_start_row + i
            self.pc.write("cursor_position", row=row, col=maze_start_column)
            print(line)
            self.maze_end_row = row

        await asyncio.sleep(self.animate_interval)

    def display_maze(self, pc, fb):
        # If the user wants a final static display for non-animated usage
        maze_lines = []
        for y in range(self.grid_height):
            # Top line
            top_line_chars = []
            for x in range(self.grid_width):
                cell = self.maze[y][x]
                top_line_chars.append(pc.apply_style('wall_style_plus', '+'))
                if cell['N']:
                    top_line_chars.append(pc.apply_style('wall_style_minus', '---'))
                else:
                    top_line_chars.append(pc.apply_style('path_style', '   '))
            top_line_chars.append(pc.apply_style('wall_style_plus', '+'))
            maze_lines.append(''.join(top_line_chars))

            # Middle line
            middle_line_chars = []
            for x in range(self.grid_width):
                cell = self.maze[y][x]
                if cell['W']:
                    middle_line_chars.append(pc.apply_style('wall_style_pipe', '|'))
                else:
                    middle_line_chars.append(pc.apply_style('path_style', ' '))
                if (x, y) == (0, 0):
                    middle_line_chars.append(pc.apply_style('start_end_style', ' S '))
                elif (x, y) == (self.grid_width - 1, self.grid_height - 1):
                    middle_line_chars.append(pc.apply_style('start_end_style', ' E '))
                else:
                    middle_line_chars.append(pc.apply_style('path_style', '   '))
            if self.maze[y][self.grid_width - 1]['E']:
                middle_line_chars.append(pc.apply_style('wall_style_pipe', '|'))
            else:
                middle_line_chars.append(pc.apply_style('path_style', ' '))
            maze_lines.append(''.join(middle_line_chars))

        # Bottom line
        bottom_line_chars = []
        for x in range(self.grid_width):
            bottom_line_chars.append(pc.apply_style('wall_style_plus', '+'))
            if self.maze[self.grid_height - 1][x]['S']:
                bottom_line_chars.append(pc.apply_style('wall_style_minus', '---'))
            else:
                bottom_line_chars.append(pc.apply_style('path_style', '   '))
        bottom_line_chars.append(pc.apply_style('wall_style_plus', '+'))
        maze_lines.append(''.join(bottom_line_chars))

        maze_start_line = 2
        maze_start_column = self.fb.vert_width + len(self.fb.vert_padding) + 1

        for i, line in enumerate(maze_lines):
            pc.write("cursor_position", row=maze_start_line + i, col=maze_start_column)
            print(line)



###############################################################################
# CELLULAR AUTOMATA (Conway’s Game of Life)
###############################################################################
class CellularAutomata(BasePattern):
    """
    More interesting variant of Conway’s Game of Life:
     - Multi-state living cells: "young," "mid," and "old"
       so we can color them differently.
     - Bottom menu with interactive controls (Pause, Step, Speed, Quit).
     - Keeps cells within the ASCII border from top to bottom.
    """
    def __init__(
        self,
        pc_instance: Optional[PrintsCharming] = None,
        fb_instance: Optional[FrameBuilder] = None,
        alt_buffer: bool = True,
        animate: bool = True,
        animate_interval: float = 0.05,
        menu: Optional[InteractiveMenu] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        **kwargs
    ):
        super().__init__(pc_instance, fb_instance, alt_buffer, animate, animate_interval, menu, **kwargs)

        # Reserve 2 lines for top/bottom border in height
        # The total terminal height includes the top border and bottom border lines,
        # so the interior available for the CA will be (terminal_height - 2).
        full_height = self.fb.terminal_height - 2
        # We'll also keep the final line for the bottom menu, so subtract 1 more:
        self.ca_height = max(1, full_height - 1)

        # For the width, we remove some columns for the left & right border
        # plus any padding from FrameBuilder
        interior_width = self.fb.get_available_width()
        self.ca_width = interior_width

        self.width = width or self.fb.get_available_width()
        self.height = height or self.fb.terminal_height - 1
        # 2D grid for cells (True=alive, False=dead)
        #self.grid = [[False] * self.width for _ in range(self.height)]

        # Store "ages":
        #   0 = dead
        #   1 = young
        #   2 = mid
        #   3 = old
        self.grid = [[0] * self.ca_width for _ in range(self.ca_height)]

        # For controlling the simulation
        self.paused = False

    async def init_pattern(self):
        if self.alt_buffer:
            self.pc.write('alt_buffer', 'cursor_home', 'hide_cursor')
        self.draw_border(self.fb.horiz_width, self.pc.terminal_height - 1)
        self.randomize_grid()

        # Show the initial menu right away so user can see it
        # (Alternatively you could wait until user triggers something.)
        self.setup_bottom_menu()


    def randomize_grid(self):
        """
        20% chance a cell is alive. We store ages:
         - 1 => young
        """
        for y in range(self.ca_height):
            for x in range(self.ca_width):
                self.grid[y][x] = 1 if (random.random() < 0.2) else 0


    async def run_pattern(self):
        """
        The main loop (with asynchronous, non-blocking key reading).
        """
        # Acquire the async key reader from your InteractiveMenu or however you structure it
        key_reader = self.menu.async_key_reader()
        try:
            while True:
                # 1) Render the grid
                self.render_grid()

                # 2) Show (draw) the bottom menu so the user can see their current selection
                self.display_bottom_maze_menu()

                # 3) Sleep for the animation interval
                await asyncio.sleep(self.animate_interval)

                # 4) If not paused, update the grid
                if not self.paused:
                    self.update_grid()

                # 5) Check if any key is available (non-blocking)
                #    If no key, the except block catches QueueEmpty, and we just move on.
                try:
                    ch = key_reader.get_key_nowait()
                    # Check for global 'q' press or pass it to the menu
                    if ch == 'q':
                        # If 'q' is a quick quit key, do your cleanup
                        if self.alt_buffer:
                            self.pc.write("normal_buffer", "show_cursor")
                        return "Quit"

                    # If any other key, feed it into the bottom menu logic
                    result = self.handle_bottom_menu_input(ch)
                    if result == "Quit":
                        if self.alt_buffer:
                            self.pc.write("normal_buffer", "show_cursor")
                        return "Quit"

                    elif result == "Back":  # <--- CATCH THE NEW SIGNAL
                        if self.alt_buffer:
                            self.pc.write("normal_buffer", "show_cursor")
                        return "Back"

                except asyncio.QueueEmpty:
                    # No key pressed this iteration, so we do nothing
                    pass

        finally:
            # Always restore terminal in case something breaks out
            key_reader.restore_tty()


    def render_grid(self):
        # Position the grid in the same place you do the Maze, for consistency
        start_row = 2
        start_col = self.fb.vert_width + len(self.fb.vert_padding) + 1

        for y in range(self.ca_height):
            self.pc.write("cursor_position", row=start_row + y, col=start_col)
            line_parts = []
            for x in range(self.ca_width):
                age = self.grid[y][x]
                if age == 0:
                    # Dead
                    line_parts.append(self.pc.apply_style('dead_cell', '.'))
                elif age == 1:
                    # Young
                    line_parts.append(self.pc.apply_style('alive_cell', 'o'))
                elif age == 2:
                    # Mid
                    # We'll pick a different color or style
                    line_parts.append(self.pc.apply_style('red', 'O'))
                else:
                    # age >= 3 => old
                    line_parts.append(self.pc.apply_style('vcyan', '@'))
            print(''.join(line_parts))


    def update_grid(self):
        """
        Typical Conway's rules, but we store "ages" if alive.
        1) Count neighbors that are age>=1 (alive in any stage).
        2) Survive if 2 or 3 neighbors
        3) Birth if exactly 3 neighbors
        4) Age living cells by +1 each turn (capped at 10 for demonstration)
        """
        #new_grid = [[False]*self.width for _ in range(self.height)]
        new_grid = [[0]*self.ca_width for _ in range(self.ca_height)]
        for y in range(self.ca_height):
            for x in range(self.ca_width):
                age = self.grid[y][x]
                neighbors = self.count_neighbors(x, y)

                if age > 0:
                    # Cell is alive
                    if neighbors in [2, 3]:
                        # Survives, age + 1
                        new_age = min(age + 1, 10)
                        new_grid[y][x] = new_age
                    else:
                        # Dies
                        new_grid[y][x] = 0
                else:
                    # Cell is dead
                    if neighbors == 3:
                        # Birth: new cell, age=1
                        new_grid[y][x] = 1
        self.grid = new_grid


    def count_neighbors(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = x + dx
                ny = y + dy
                if 0 <= nx < self.ca_width and 0 <= ny < self.ca_height:
                    if self.grid[ny][nx] > 0:  # any age > 0 is alive
                        count += 1
        return count


    ###########################################################################
    # BOTTOM MENU LOGIC
    ###########################################################################

    def setup_bottom_menu(self):
        """
        Creates a simple interactive menu stored in self.menu.
        Items: Pause/Resume, Step, Faster, Slower, Quit
        We'll position it near the bottom, above the bottom border line.
        """
        if not self.menu:
            return

        self.menu.menus = {
            "ca_menu": [
                "Pause/Resume",
                "Step",
                "Faster",
                "Slower",
                "Back",
                "Quit"
            ]
        }
        self.menu.current_menu = "ca_menu"
        self.menu.selected_index = 0


    def display_bottom_maze_menu(self):
        """
        Very similar to Maze's bottom menu logic.
        We'll place it on the second-to-last row (just above the bottom border).
        """
        if not self.menu:
            return

        # The bottom border is at row = self.pc.terminal_height - 1
        # So we place the menu at row = self.pc.terminal_height - 2
        self.menu.menu_start_row = self.pc.terminal_height - 2
        self.menu.menu_start_column = 4  # small left offset
        self.menu.display_highlighted_menu(clear_display=False)


    def handle_bottom_menu_input(self, ch):
        """
        Evaluate the single character 'ch' from the async key reader.
        If user selects 'Quit', return "Quit", otherwise return None.
        """
        if not self.menu:
            return None

        # Navigation
        #if ch in ['k', self.pc.ctl_map['arrow_up'], self.pc.ctl_map['arrow_left']]:
        if ch in ['k', 'arrow_up', 'arrow_left']:
            self.menu.navigate(-1, clear_display=False)
        #elif ch in ['j', self.pc.ctl_map['arrow_down'], self.pc.ctl_map['arrow_right']]:
        elif ch in ['j', 'arrow_down', 'arrow_right']:
            self.menu.navigate(1, clear_display=False)
        elif ch == '\r':
            # Confirm selection
            choice = self.menu.menus[self.menu.current_menu][self.menu.selected_index]
            return self.execute_menu_choice(choice)

        return None


    def execute_menu_choice(self, choice):
        """
        Processes the chosen menu option.
        """
        if choice == "Pause/Resume":
            self.paused = not self.paused
        elif choice == "Step":
            # Single-step: if paused, do one update
            if self.paused:
                self.update_grid()
        elif choice == "Faster":
            # Decrease animate_interval (faster updates)
            self.animate_interval = max(0.01, self.animate_interval - 0.02)
        elif choice == "Slower":
            # Increase animate_interval (slower updates)
            self.animate_interval = min(1.0, self.animate_interval + 0.02)
        elif choice == "Back":
            # Return a special signal so run_pattern() can exit and go back to main menu
            return "Back"
        elif choice == "Quit":
            return "Quit"
        return None


###############################################################################
# FRACTAL TREE
###############################################################################
class FractalTree(BasePattern):
    def __init__(
        self,
        pc_instance: Optional[PrintsCharming] = None,
        fb_instance: Optional[FrameBuilder] = None,
        alt_buffer: bool = True,
        animate: bool = True,
        animate_interval: float = 0.05,
        menu: Optional[InteractiveMenu] = None,
        max_depth: int = 6,
        **kwargs
    ):
        super().__init__(pc_instance, fb_instance, alt_buffer, animate, animate_interval, menu, **kwargs)
        self.max_depth = max_depth
        self.lines = []

    async def run_pattern(self):
        # We can animate the fractal tree by drawing each recursion step by step
        # or just draw once. Here, let's do it iteratively, from depth=1..max_depth
        for depth in range(1, self.max_depth + 1):
            self.pc.write("cursor_position", row=2, col=2)
            self.pc.write("clear_screen_down")
            self.lines = []
            self.generate_tree(x=0, y=0, angle=-math.pi/2, depth=depth, length=8)
            # Now we have a list of line segments; let's “draw” them in ASCII
            self.draw_tree()

            await asyncio.sleep(self.animate_interval)

            # Check for user input to quit
            key = self.menu.async_key_reader()
            if key == 'q':
                if self.alt_buffer:
                    self.pc.write('normal_buffer', 'show_cursor')
                return "Quit"

        # Wait a bit after finishing
        await asyncio.sleep(1.5)

    def generate_tree(self, x, y, angle, depth, length):
        """
        Recursively produce line segments (x1,y1) -> (x2,y2) in self.lines
        We'll store them so we can “rasterize” them in ASCII later.
        """
        if depth == 0:
            return
        x2 = x + length * math.cos(angle)
        y2 = y + length * math.sin(angle)
        self.lines.append(((x, y), (x2, y2)))
        # branch left
        self.generate_tree(x2, y2, angle - math.pi/4, depth - 1, length*0.7)
        # branch right
        self.generate_tree(x2, y2, angle + math.pi/4, depth - 1, length*0.7)

    def draw_tree(self):
        """
        Convert the floating coordinates to a character grid, then print.
        We’ll offset them so it fits nicely in the terminal.
        """
        # Convert all x,y to screen coords
        coords = []
        minx = miny = 999999999
        maxx = maxy = -999999999

        for (x1, y1), (x2, y2) in self.lines:
            minx = min(minx, x1, x2)
            maxx = max(maxx, x1, x2)
            miny = min(miny, y1, y2)
            maxy = max(maxy, y1, y2)
            coords.append(((x1, y1), (x2, y2)))

        # We’ll pad edges
        w = int(maxx - minx + 20)
        h = int(maxy - miny + 20)

        # Create a grid of spaces
        grid = []
        for _ in range(h):
            grid.append([" "] * w)

        # A simple line-draw approach: we’ll mark endpoints and any midpoints
        for (x1, y1), (x2, y2) in coords:
            # shift to positive indices
            sx1 = x1 - minx + 10
            sy1 = y1 - miny + 10
            sx2 = x2 - minx + 10
            sy2 = y2 - miny + 10

            # We'll just step along the line in small increments
            steps = int( max(abs(sx2 - sx1), abs(sy2 - sy1)) * 2 )  # oversample
            for i in range(steps+1):
                t = i / steps
                px = int(sx1 + t*(sx2 - sx1))
                py = int(sy1 + t*(sy2 - sy1))
                if 0 <= py < h and 0 <= px < w:
                    grid[int(py)][int(px)] = "█"  # trunk or branch

        # Print out
        start_row = 2
        start_col = 2
        for row_idx, rowdata in enumerate(grid):
            self.pc.write("cursor_position", row=start_row + row_idx, col=start_col)
            line_str = "".join(rowdata)
            # color the tree
            print(self.pc.apply_style('vgreen', line_str))


###############################################################################
# WAVE PATTERN
###############################################################################
class WavePattern(BasePattern):
    def __init__(
        self,
        pc_instance: Optional[PrintsCharming] = None,
        fb_instance: Optional[FrameBuilder] = None,
        alt_buffer: bool = True,
        animate: bool = True,
        animate_interval: float = 0.05,
        menu: Optional[InteractiveMenu] = None,
        width: int = 60,
        height: int = 20,
        **kwargs
    ):
        super().__init__(pc_instance, fb_instance, alt_buffer, animate, animate_interval, menu, **kwargs)
        self.width = width
        self.height = height
        self.t = 0.0  # time or phase for the wave

    async def run_pattern(self):
        while True:
            self.draw_wave()
            await asyncio.sleep(self.animate_interval)
            self.t += 0.2

            # check quit
            key = self.menu.poll_key_nonblock()
            if key == 'q':
                if self.alt_buffer:
                    self.pc.write('normal_buffer', 'show_cursor')
                return "Quit"

    def draw_wave(self):
        start_row = 2
        start_col = 2
        # Clear the region
        self.pc.write("cursor_position", row=start_row, col=start_col)
        self.pc.write("clear_screen_down")

        for y in range(self.height):
            self.pc.write("cursor_position", row=start_row + y, col=start_col)
            line_parts = []
            for x in range(self.width):
                # simple sine wave
                wave_y = (self.height/2) + (math.sin( (x/5.0) + self.t ) * (self.height/4))
                if abs(y - wave_y) < 0.5:
                    line_parts.append(self.pc.apply_style('vcyan', '█'))
                else:
                    line_parts.append(self.pc.apply_style('default', ' '))
            print("".join(line_parts))



###############################################################################
# MENU LAUNCHER
###############################################################################
"""
def get_menu(menus, pc):
    horiz_menu = InteractiveMenu(
        *menus,
        pc=pc,
        selected_style='vcyan',
        unselected_style='default',
        confirmed_style='vgreen',
        alt_buffer=False,
        display_instructions=False,
        enable_frames_and_tables=False,
    )

    return horiz_menu
"""


"""
def run_menu(menus, pc):

    horiz_menu = InteractiveMenu(
        *menus,
        pc=pc,
        selected_style='vcyan',
        unselected_style='default',
        confirmed_style='vgreen',
        enable_frames_and_tables=False,
        alt_buffer=True
    )

    choice = horiz_menu.run()

    # If user pressed 'q' at aggregator, choice is None
    if choice is None:
        # User pressed q in aggregator, exit
        return

    # choice corresponds to the chosen line (1-based)
    if choice == 1:
        new_menu = get_menu(menus, pc)
        return new_menu

    elif choice == 2:
        # Quit
        return
    # After scenario returns, we loop again to aggregator
    # Exiting main ends the program.
"""

"""
async def main():

    pc = PrintsCharming(styles=maze_styles)
    fb = FrameBuilder(pc=pc, horiz_char=' ', vert_width=2, vert_padding=1, vert_char=' ')

    launch_maze_menus = [
        ("maze_menu", "hor", "Create Maze", "Quit")
    ]

    menu = run_menu(launch_maze_menus, pc)

    if not menu:
        return

    # Generate and display the maze
    maze = Maze(pc, fb, animate=True, menu=menu)

    await maze.init_maze()


    result = await maze.generate_maze()
    if result == "Quit":
        pc.print("Exiting program...", style="vred")
        return  # Exit the program cleanly


    if not maze.animate:
        maze.display_maze(pc, fb)

    if PrintsCharming.is_alt_buffer:
        PrintsCharming.write("normal_buffer", "show_cursor")  # Restore terminal



    # Solve the maze and display the solution
    #solution_path = await maze.solve_maze()
"""

def get_menu(menus, pc):
    horiz_menu = InteractiveMenu(
        *menus,
        pc=pc,
        selected_style='vcyan',
        unselected_style='default',
        confirmed_style='vgreen',
        alt_buffer=False,
        display_instructions=False,
        enable_frames_and_tables=False,
    )
    return horiz_menu

def run_menu(menus, pc):
    vert_menu = InteractiveMenu(
        *menus,
        pc=pc,
        selected_style='vcyan',
        unselected_style='default',
        confirmed_style='vgreen',
        enable_frames_and_tables=False,
        alt_buffer=True
    )
    choice = vert_menu.run()
    return choice






###############################################################################
# MAIN
###############################################################################
async def main():
    #pc = PrintsCharming(styles=maze_styles)
    pc = PrintsCharming()
    pc.add_styles(maze_styles)
    fb = FrameBuilder(pc=pc, horiz_char=' ', vert_width=2, vert_padding=1, vert_char=' ')

    """
    # We’ll define a “main menu” with multiple pattern options
    first_menu_items = [
        ("main_menu", "vert",
         "Maze",
         "Cellular Automata",
         "Fractal Tree",
         "Wave Pattern",
         "Quit")
    ]
    choice = run_menu(first_menu_items, pc)

    if choice is None:
        return

    # main_menu is the 1-based index of the selected item:
    if choice == 1:
        # Maze
        pattern = Maze(pc_instance=pc, fb_instance=fb, animate=True, menu=InteractiveMenu(pc=pc))

    elif choice == 2:

        bottom_menu_items = [
            ("ca_menu", "hor",
             "Pause/Resume",
             "Step",
             "Faster",
             "Slower",
             "Back",
             "Quit")
        ]

        # Cellular Automata
        pattern = CellularAutomata(
            pc_instance=pc,
            fb_instance=fb,
            animate=True,
            menu=InteractiveMenu(
                *bottom_menu_items,
                pc=pc,
                selected_style='vcyan',
                unselected_style='default',
                confirmed_style='vgreen',
                alt_buffer=False,
                display_instructions=False,
                enable_frames_and_tables=False,
            )
        )

    elif choice == 3:
        # Fractal Tree
        pattern = FractalTree(pc_instance=pc, fb_instance=fb, animate=True, menu=InteractiveMenu(pc=pc))
    elif choice == 4:
        # Wave Pattern
        pattern = WavePattern(pc_instance=pc, fb_instance=fb, animate=True, menu=InteractiveMenu(pc=pc))
    elif choice == 5:
        pc.print("Exiting program...", style="vred")
        return
    else:
        pc.print("Invalid Option. Exiting...", style="vred")
        return

    # Initialize the chosen pattern (draw border, etc.)
    await pattern.init_pattern()
    # Run/animate/generate the chosen pattern
    result = await pattern.run_pattern()
    if result == "Quit":
        pc.print("User requested quit. Exiting program...", style="red")
    """

    while True:
        # Show the top-level menu again and wait for a choice
        first_menu_items = [
            ("main_menu", "vert",
             "Maze",
             "Cellular Automata",
             "Fractal Tree",
             "Wave Pattern",
             "MultiRule CA",
             "Quit")
        ]

        choice = run_menu(first_menu_items, pc)
        if choice is None:
            return

        if choice == 1:
            # Maze
            pattern = Maze(
                pc_instance=pc,
                fb_instance=fb,
                animate=True,
                menu=InteractiveMenu(
                    pc=pc
                )
            )

        elif choice == 2:
            bottom_menu_items = [
                ("ca_menu", "hor",
                 "Pause/Resume",
                 "Step",
                 "Faster",
                 "Slower",
                 "Back",
                 "Quit")
            ]

            pattern = CellularAutomata(
                pc_instance=pc,
                fb_instance=fb,
                animate=True,
                menu=InteractiveMenu(
                    *bottom_menu_items,
                    pc=pc,
                    selected_style='vcyan',
                    unselected_style='default',
                    confirmed_style='vgreen',
                    alt_buffer=False,
                    display_instructions=False,
                    enable_frames_and_tables=False,
                )
            )

        elif choice == 3:
            pattern = FractalTree(pc_instance=pc, fb_instance=fb, animate=True, menu=InteractiveMenu(pc=pc))

        elif choice == 4:
            pattern = WavePattern(pc_instance=pc, fb_instance=fb, animate=True, menu=InteractiveMenu(pc=pc))

        elif choice == 5:

            bottom_menu_items = [
                ("multi_ca_menu", "hor",
                 "Pause/Resume",
                 "Step",
                 "Faster",
                 "Slower",
                 "Change Rule",
                 "Toggle Edit",
                 "Export Dungeon",
                 "FractalWave Off",
                 "Back",
                 "Quit")
            ]

            pattern = MultiRuleCellularAutomata(
                pc_instance=pc,
                fb_instance=fb,
                animate=True,
                menu=InteractiveMenu(
                    *bottom_menu_items,
                    pc=pc,
                    selected_style='vcyan',
                    unselected_style='default',
                    confirmed_style='vgreen',
                    alt_buffer=False,
                    display_instructions=False,
                    enable_frames_and_tables=False,
                )
            )

        elif choice == 6:
            pc.print("Exiting program...", style="vred")
            return

        else:
            pc.print("Invalid Option. Exiting...", style="vred")
            return

        # Now we have a chosen “pattern”
        # 1) Initialize
        await pattern.init_pattern()
        # 2) Run/animate
        result = await pattern.run_pattern()

        # If user selected "Quit" in the bottom menu, end the entire program
        if result == "Quit":
            pc.print("User requested quit. Exiting program...", style="red")
            return

        # If user selected "Back", we do NOT return. We let the loop continue,
        # so it re-displays the main menu and the user can pick again.
        if result == "Back":
            # re-loop -> show the main menu again
            continue



    # Restore terminal
    if PrintsCharming.is_alt_buffer:
        PrintsCharming.write("normal_buffer", "show_cursor")




if __name__ == "__main__":
    asyncio.run(main())



"""
class Maze:
    def __init__(self, width, height, pc, fb, tm, animate=False):
        self.width = width
        self.height = height
        # Initialize the maze grid with walls on all sides
        self.maze = [
            [{'N': True, 'S': True, 'E': True, 'W': True} for _ in range(width)]
            for _ in range(height)
        ]
        self.visited = [[False for _ in range(width)] for _ in range(height)]
        self.pc = pc
        self.fb = fb
        self.tm = tm
        self.animate = animate
        self.table_name = "maze_table"
        self.bound_cells = {}
        self.init_display()

    def init_display(self):
        # Initialize BoundCells for each maze cell
        table_data = []
        for y in range(self.height * 2 + 1):
            row_cells = []
            for x in range(self.width * 2 + 1):
                bound_cell = BoundCell(lambda x=x, y=y: self.get_cell_display(x, y))
                self.bound_cells[(x, y)] = bound_cell
                row_cells.append(bound_cell)
            table_data.append(row_cells)

        # Add the table to the TableManager
        display_table = self.tm.add_bound_table(
            table_data=table_data,
            table_name=self.table_name,
            show_table_name=False,
            border_char="",
            border_style="default",
            col_sep="",
            header_style="",
            cell_style="",
            use_styles=True,
            target_text_box=True,
            ephemeral=False,
            append_newline=False,
        )
        # Print the initial maze (empty with walls)
        print(display_table)

    def get_cell_display(self, x, y):
        # Determine if this position corresponds to a wall or a path
        if y % 2 == 0:
            if x % 2 == 0:
                return self.pc.apply_style('wall_style', '+')
            else:
                # Horizontal walls
                cell_x = x // 2
                cell_y = y // 2
                if cell_y == 0:
                    if self.maze[cell_y][cell_x]['N']:
                        return self.pc.apply_style('wall_style', '---')
                    else:
                        return '   '
                else:
                    if self.maze[cell_y - 1][cell_x]['S']:
                        return self.pc.apply_style('wall_style', '---')
                    else:
                        return '   '
        else:
            if x % 2 == 0:
                # Vertical walls
                cell_x = x // 2
                cell_y = y // 2
                if cell_x == 0:
                    if self.maze[cell_y][cell_x]['W']:
                        return self.pc.apply_style('wall_style', '|')
                    else:
                        return ' '
                else:
                    if self.maze[cell_y][cell_x - 1]['E']:
                        return self.pc.apply_style('wall_style', '|')
                    else:
                        return ' '
            else:
                # Cell content
                cell_x = x // 2
                cell_y = y // 2
                if (cell_x, cell_y) == (0, 0):
                    return self.pc.apply_style('start_end_style', ' S ')
                elif (cell_x, cell_y) == (self.width - 1, self.height - 1):
                    return self.pc.apply_style('start_end_style', ' E ')
                elif self.visited[cell_y][cell_x]:
                    return self.pc.apply_style('path_style', '   ')
                else:
                    return '   '

    async def generate_maze(self, x=0, y=0):
        self.visited[y][x] = True
        if self.animate:
            await self.update_display()
        directions = ['N', 'S', 'E', 'W']
        random.shuffle(directions)
        for direction in directions:
            nx, ny = x, y
            if direction == 'N':
                ny -= 1
            elif direction == 'S':
                ny += 1
            elif direction == 'E':
                nx += 1
            elif direction == 'W':
                nx -= 1
            if 0 <= nx < self.width and 0 <= ny < self.height and not self.visited[ny][nx]:
                # Remove walls between current cell and next cell
                self.maze[y][x][direction] = False
                opposite = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
                self.maze[ny][nx][opposite[direction]] = False
                await self.generate_maze(nx, ny)
                if self.animate:
                    await self.update_display()

    async def update_display(self):
        # Update all cells
        for y in range(self.height * 2 + 1):
            for x in range(self.width * 2 + 1):
                self.bound_cells[(x, y)].get_value()
        self.tm.refresh_bound_table(self.table_name)
        await asyncio.sleep(0.05)

    def display_maze(self):
        # Final display update
        for y in range(self.height * 2 + 1):
            for x in range(self.width * 2 + 1):
                self.bound_cells[(x, y)].get_value()
        self.tm.refresh_bound_table(self.table_name)


# Main function to generate and display the maze
async def main():
    pc = PrintsCharming(styles=maze_styles)
    fb = FrameBuilder(pc=pc, horiz_char=' ', vert_width=3, vert_padding=1, vert_char=' ')
    tm = TableManager(pc=pc)

    # Build styled borders to calculate available width and height
    horiz_border_top, vert_border_left, vert_border_inner, vert_border_right, horiz_border_bottom = fb.build_styled_border_box(
        border_top_style='purple',
        border_bottom_style='purple',
        border_left_style='purple',
        border_right_style='purple'
    )

    # Calculate available width and height inside borders
    available_width = fb.get_available_width()
    available_height = fb.terminal_height - 2

    # Estimate cell dimensions dynamically
    # Measure the width of a cell in characters
    # Build a sample cell line to measure its length
    sample_top_cell = pc.apply_style('wall_style', '+') + \
                      pc.apply_style('wall_style', '---') + \
                      pc.apply_style('wall_style', '+')
    sample_middle_cell = pc.apply_style('wall_style', '|') + \
                         pc.apply_style('path_style', '   ') + \
                         pc.apply_style('wall_style', '|')

    # Calculate the visible length of the sample cell lines
    cell_width = len(fb.strip_ansi_escape_sequences(sample_top_cell)) - 1  # Subtract 1 to account for overlap
    cell_height = 2  # Each cell is 2 lines high

    # Calculate maximum number of cells that can fit in the available space
    max_maze_width = max(available_width // cell_width, 1)
    max_maze_height = max((available_height - 2) // cell_height, 1)

    # Adjust the maze size
    width = max_maze_width
    height = max_maze_height


    # Generate and display the maze
    maze = Maze(width, height, pc, fb, tm, animate=True)
    await maze.generate_maze()
    maze.display_maze()

if __name__ == "__main__":
    asyncio.run(main())
"""

