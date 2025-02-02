# interactive_menu.py

import time
import sys
import json

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .prints_charming_defaults import (
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_STYLES,
)

from .prints_charming import PrintsCharming
from .table_manager import TableManager
from .frame_builder import FrameBuilder

from .prints_style import PStyle

from .utils import get_key, pole_key_nonblock, AsyncKeyReader


class InteractiveMenu:

    def __init__(
        self,
        *initial_menu_configs,
        pc=None,
        selected_style=None,
        unselected_style=None,
        confirmed_style=None,
        alt_buffer=True,
        menu_start_row=10,
        menu_start_column=None,
        confirm_select_digit_key=False,
        display_instructions=True,
        enable_frames_and_tables=True,
    ) -> None:

        if isinstance(pc, str):
            self.pc = PrintsCharming.get_shared_instance(pc)
            if not self.pc:
                self.pc = PrintsCharming()
                self.pc.warning(f"No shared instance found for key '{pc}'. Using a new instance with default init.")
        else:
            self.pc = pc or PrintsCharming()

        self.reset = self.pc.reset
        self.apply_style = self.pc.apply_style

        self.ctl = self.pc.ctl_map
        self.unicode = self.pc.unicode_map
        self.write = self.pc.write

        # Dictionary to hold menus and their types (vertical or horizontal)
        self.menus = {}
        self.menu_types = {}  # Stores whether each menu is 'hor' or 'vert'
        self.current_menu = None
        self.menu_stack = []  # To track the stack of menus for navigating back

        # Initialize the menus if any configurations are provided
        if initial_menu_configs:
            self._initialize_menus(initial_menu_configs)

        self.selected_style = selected_style
        self.unselected_style = unselected_style or 'default'
        self.confirmed_style = confirmed_style or selected_style

        self.selected_index = 0  # Vertical navigation index (styles)
        self.horizontal_index = 0  # Horizontal navigation index (attributes)

        self.alt_buffer = alt_buffer
        self.menu_start_row = menu_start_row
        self.menu_start_column = menu_start_column

        self.confirm_select_digit_key = confirm_select_digit_key

        self.get_key = get_key
        self.pole_key_nonblock = pole_key_nonblock
        self.async_key_reader = AsyncKeyReader

        self.arrows = {
            'down': self.pc.apply_style(style_name='down_arrow', text="⭣"),
            'up': self.pc.apply_style(style_name='up_arrow', text="⭡"),
            'left': self.pc.apply_style(style_name='left_arrow', text="⇐"),
            'right': self.pc.apply_style(style_name='right_arrow', text="⇒")
        }

        self.vert_nav_directions = f" 'j' or {self.arrows.get('down')} to move down, 'k' or {self.arrows.get('up')} to move up.\n"
        self.hor_nav_directions = f" 'l' or {self.arrows.get('right')} to move right, 'h' or {self.arrows.get('left')} to move left.\n"

        self.enable_expand_submenu = True

        # Track expanded dictionary menus: key = tuple (menu_name, index_of_dict_option)
        self.expanded_submenus = set()

        self.display_instructions = display_instructions

        self.enable_frames_and_tables = enable_frames_and_tables



    def _initialize_menus(self, menu_configs):
        """Helper function to initialize menus from given configurations."""
        for config in menu_configs:
            if len(config) < 3:
                print(f"Invalid menu configuration: {config}")
                continue
            menu_name, menu_type, *options = config
            self.create_menu(menu_name, menu_type, options)


    def create_menu(self, menu_name, menu_type, options):
        """Create a new menu with a given name, type ('hor', 'vert', or 'nested'), and list of options or submenus."""
        if menu_type not in ['hor', 'vert', 'nested']:
            print(f"Invalid menu type '{menu_type}' for menu '{menu_name}'. Must be 'hor', 'vert', or 'nested'.")
            return
        self.menus[menu_name] = options
        self.menu_types[menu_name] = menu_type
        if not self.current_menu:
            self.current_menu = menu_name  # Set the current menu if none is set


    def switch_menu(self, menu_name):
        """Switch to a different menu by name."""
        if menu_name in self.menus:
            self.menu_stack.append(self.current_menu)  # Save current menu to stack for back navigation
            self.current_menu = menu_name
            self.selected_index = 0  # Reset navigation index when switching menus
        else:
            print(f"Menu '{menu_name}' does not exist.")


    def handle_input(self, key):
        if key == '/':
            self.search_menu()
        elif key.isdigit():
            self.quick_select(int(key))

    def search_menu(self):
        """Filters visible menu options based on user input."""
        query = input("Search: ").lower()
        self.filtered_options = [opt for opt in self.menus[self.current_menu] if query in opt.lower()]
        self.selected_index = 0  # Reset selection

    def quick_select(self, num):
        """Allows direct number-based menu selection."""
        if 1 <= num <= len(self.menus[self.current_menu]):
            self.selected_index = num - 1


    def go_back(self):
        """Go back to the previous menu in the stack."""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            self.selected_index = 0
        else:
            print("No previous menu to return to.")



    def display_highlighted_menu(self, row=None, col=None, clear_display=True):
        """Displays the options for the current menu with the selected one highlighted."""
        if self.current_menu is None:
            print("No menu is currently active.")
            return

        self.write('cursor_position', row=self.menu_start_row, col=self.menu_start_column or 1)

        menu_options = self.menus[self.current_menu]  # Access options for the current menu
        menu_type = self.menu_types[self.current_menu]  # Get whether it's 'vert' or 'hor'

        if clear_display:
            # Clear display area first
            # Assuming a max number of lines; adjust as needed or implement a more dynamic clear
            for clear_i in range(0, len(menu_options) + 50):
                self.write('cursor_position', row=self.menu_start_row + clear_i, col=1)
                self.write('clear_line')

            self.write('cursor_position', row=self.menu_start_row, col=1)

        display_text = ""

        if menu_type == 'vert':
            # Display each option on a new line
            for i, option in enumerate(menu_options):
                if isinstance(option, dict):
                    option = list(option.keys())[0]  # If it's a nested menu, show the submenu name
                style = self.selected_style if i == self.selected_index else self.unselected_style
                display_text = f"({i + 1}) {option}"
                self.pc.print(display_text, style=style)

        elif menu_type == 'hor':
            """
            # Display all options on the same line
            display_text = ""
            for i, option in enumerate(menu_options):
                if isinstance(option, dict):
                    option = list(option.keys())[0]  # If it's a nested menu, show the submenu name
                style = self.selected_style if i == self.selected_index else self.unselected_style
                option_text = self.pc.apply_style(style, option)
                display_text += f"{option_text}   "  # Add spacing between options
                

                # Distinguish dictionary entries
                if isinstance(option, dict):
                    dict_label = list(option.keys())[0]
                    # Mark expanded or collapsed
                    arrow_symbol = "▼" if (self.current_menu, i) in self.expanded_submenus else "▶"
                    display_text = f"({i + 1}) {arrow_symbol} {dict_label}"
                else:
                    display_text = f"({i + 1}) {option}"

                style = self.selected_style if i == self.selected_index else self.unselected_style
                self.pc.print(display_text, style=style)
            """

            # For horizontal menus:
            # 1. Identify top-level items (including dictionaries) and print them in one horizontal line.
            # 2. For any expanded dictionary, print its submenu items vertically below.

            top_level_items = []
            expansions = {}  # key: dict_index, value: list of (item, global_index)
            #skip_until = -1  # used to skip printing expansions in the top-level line

            # First pass: separate top-level and expansions
            i = 0
            while i < len(menu_options):
                option = menu_options[i]
                if isinstance(option, dict):
                    # A dictionary option represents a nested menu trigger
                    dict_index = i
                    dict_label = list(option.keys())[0]
                    is_expanded = (self.current_menu, dict_index) in self.expanded_submenus
                    arrow_symbol = "▼" if is_expanded else "▶"
                    # Prepare the displayed text for the dictionary entry
                    text = f"({i + 1}) {arrow_symbol} {dict_label}"
                    top_level_items.append((text, i))  # store text and index

                    if is_expanded:
                        # If expanded, the submenu items follow immediately after
                        submenu_items = option[dict_label]
                        expansion_list = []
                        for j, sub_item in enumerate(submenu_items, start=1):
                            exp_index = dict_index + j
                            if exp_index < len(menu_options):
                                expansion_list.append((sub_item, exp_index))
                        expansions[dict_index] = expansion_list

                        # We'll print these expansions vertically after printing the top-level line.
                        # Do not add them to the top-level line.
                        i += len(submenu_items)
                else:
                    # A regular (non-dict) top-level item
                    text = f"({i + 1}) {option}"
                    top_level_items.append((text, i))
                i += 1

            # Now print the top-level line horizontally
            # Apply styles to each top-level item individually
            horizontal_line_parts = []
            for text, idx in top_level_items:
                is_selected = (idx == self.selected_index)
                style = self.selected_style if is_selected else self.unselected_style
                styled_text = self.pc.apply_style(style, text)
                horizontal_line_parts.append(styled_text)

            # Print the entire horizontal line
            horizontal_line = "   ".join(horizontal_line_parts)
            self.pc.print(horizontal_line)

            # After printing the horizontal line, print expansions for each expanded dictionary
            # vertically beneath the line.
            # For each expanded dictionary entry, print its expansions on subsequent lines
            vertical_line_offset = 1  # Start printing expansions below the horizontal line
            for dict_idx, exp_list in expansions.items():
                # For each submenu item, print on a new line
                for (sub_item, exp_idx) in exp_list:
                    # Check if this expansion item is selected
                    is_selected = (exp_idx == self.selected_index)
                    style = self.selected_style if is_selected else self.unselected_style
                    #self.write('cursor_position', row=self.menu_start_row + vertical_line_offset, col=1)
                    # Indent expansions a bit so they're visually distinguishable
                    display_text = f"     ({exp_idx + 1}) {sub_item}"
                    self.pc.print(display_text, style=style)
                    vertical_line_offset += 1

            #self.pc.print(display_text)


    def toggle_submenu(self, dict_index):
        # dict_index is the index of the dictionary option in the current menu
        current_options = self.menus[self.current_menu]
        dict_item = current_options[dict_index]
        dict_label = list(dict_item.keys())[0]
        submenu_items = dict_item[dict_label]

        # Check if currently expanded
        key = (self.current_menu, dict_index)
        if key in self.expanded_submenus:
            # Collapse: remove inserted submenu items
            # Find how many items belong to this submenu
            # They follow directly after the dictionary item until a "Back" is encountered or end of submenu
            remove_count = len(submenu_items)
            # Remove those items from the current menu options
            # dict_index+1 to dict_index+remove_count
            del current_options[dict_index + 1:dict_index + 1 + remove_count]
            self.expanded_submenus.remove(key)
        else:
            # Expand: insert submenu items directly after the dictionary item
            for idx, sub_item in enumerate(submenu_items, start=1):
                current_options.insert(dict_index + idx, sub_item)
            self.expanded_submenus.add(key)



    def navigate(self, direction, col=None, clear_display=True):
        """Navigate through the current menu options."""
        if self.current_menu is None:
            print("No menu is currently active.")
            return

        menu_options = self.menus[self.current_menu]
        menu_type = self.menu_types[self.current_menu]

        # For vertical menus, navigate by changing the selected_index
        if menu_type == 'vert':
            self.selected_index = (self.selected_index + direction) % len(menu_options)
        # For horizontal menus, navigate horizontally
        elif menu_type == 'hor':
            self.selected_index = (self.selected_index + direction) % len(menu_options)

        # Handle nested menus (if the option is a dictionary representing a submenu)
        if isinstance(menu_options[self.selected_index], dict):
            submenu_name = list(menu_options[self.selected_index].keys())[0]
            self.switch_menu(submenu_name)

        # Clear and redisplay the menu
        for i in range(len(menu_options)):
            self.write('cursor_position', row=self.menu_start_row + i, col=col or 1)

        self.display_highlighted_menu(clear_display=clear_display)


    def run(self):
        if self.alt_buffer:
            self.write('alt_buffer', 'cursor_home', 'hide_cursor')

        if self.current_menu is None:
            print("No menu is currently active.")
            return

        if self.display_instructions:
            # Display instructions
            self.write(f"{self.pc.apply_style(style_name='vgreen', text='Please select an option:')}\n\n")
            self.write(self.vert_nav_directions if self.menu_types[self.current_menu] == 'vert' else self.hor_nav_directions)
            self.pc.print2(f"\n", f" 'q' to quit", end='\n', sep='', style=['default', 'vred'], italic=True, bold=True, style_args_as_one=False)

        self.display_highlighted_menu()

        confirmed_option = None

        message_row = self.menu_start_row + len(self.menus[self.current_menu]) + 10  # Define a row for messages

        if not self.enable_frames_and_tables:

            while True:
                # Clear the input line before capturing the next input
                self.write('cursor_position', row=message_row, col=1)
                self.write('clear_line')  # Clear the current input line

                key = get_key()

                if key == 'q':
                    # Quit this menu
                    if self.alt_buffer:
                        self.write('normal_buffer', 'show_cursor')
                    return None  # Return None to indicate user pressed 'q'

                if not self.enable_expand_submenu:

                    if key in ['k', 'h', self.pc.ctl_map['arrow_up'], self.pc.ctl_map['arrow_left']]:
                        self.navigate(-1)
                        # Clear any existing message
                        self.write('cursor_position', row=message_row, col=1)
                        self.write('clear_line')

                    elif key in ['j', 'l', self.pc.ctl_map['arrow_down'], self.pc.ctl_map['arrow_right']]:
                        self.navigate(1)
                        # Clear any existing message
                        self.write('cursor_position', row=message_row, col=1)
                        self.write('clear_line')

                    elif key == '\r':
                        confirmed_option = self.menus[self.current_menu][self.selected_index]
                        break

                    elif key.isdigit():
                        num = int(key)
                        menu_length = len(self.menus[self.current_menu])
                        if 1 <= num <= menu_length:
                            self.selected_index = num - 1
                            self.display_highlighted_menu()
                            if self.confirm_select_digit_key:
                                confirmed_option = self.menus[self.current_menu][self.selected_index]
                                break
                        else:
                            self.write('cursor_position', row=message_row, col=1)

                            self.pc.print(f"\nInvalid selection: {num}. Please select a valid option.", style='vred')

                else:
                    if key in ['k', 'h', self.pc.ctl_map['arrow_up'], self.pc.ctl_map['arrow_left']]:
                        self.selected_index = (self.selected_index - 1) % len(self.menus[self.current_menu])
                        self.display_highlighted_menu()

                    elif key in ['j', 'l', self.pc.ctl_map['arrow_down'], self.pc.ctl_map['arrow_right']]:
                        self.selected_index = (self.selected_index + 1) % len(self.menus[self.current_menu])
                        self.display_highlighted_menu()

                    elif key == '\r':
                        current_option = self.menus[self.current_menu][self.selected_index]
                        if isinstance(current_option, dict):
                            # Toggle submenu expansion
                            self.toggle_submenu(self.selected_index)
                            # Re-display after expansion/collapse
                            self.display_highlighted_menu()
                            continue  # Don't break; allow user to navigate new expanded/collapsed menu
                        else:
                            # Confirm a non-dict option
                            confirmed_option = current_option
                            break

                    elif key.isdigit():
                        num = int(key)
                        menu_length = len(self.menus[self.current_menu])
                        if 1 <= num <= menu_length:
                            self.selected_index = num - 1
                            self.display_highlighted_menu()
                            if self.confirm_select_digit_key:
                                current_option = self.menus[self.current_menu][self.selected_index]
                                if isinstance(current_option, dict):
                                    self.toggle_submenu(self.selected_index)
                                    self.display_highlighted_menu()
                                    continue
                                else:
                                    confirmed_option = current_option
                                    break
                        else:
                            self.write('cursor_position', row=message_row, col=1)
                            self.pc.print(f"\nInvalid selection: {num}. Please select a valid option.", style='vred')
        else:
            tm = TableManager(pc=self.pc)
            fb = FrameBuilder(pc=self.pc)

            while True:
                self.write('cursor_position', row=message_row, col=1)
                self.write('clear_line')
                key = self.get_key()

                if key == 'q':
                    if self.alt_buffer:
                        self.write('normal_buffer', 'show_cursor')
                    return None

                elif key in ['k', 'h', self.pc.ctl_map['arrow_up'], self.pc.ctl_map['arrow_left']]:
                    self.selected_index = (self.selected_index - 1) % len(self.menus[self.current_menu])
                    self.display_highlighted_menu()

                elif key in ['j', 'l', self.pc.ctl_map['arrow_down'], self.pc.ctl_map['arrow_right']]:
                    self.selected_index = (self.selected_index + 1) % len(self.menus[self.current_menu])
                    self.display_highlighted_menu()

                elif key in ['\r', ' ']:  # Enter or space toggles expansions if dict, confirms if normal option
                    current_option = self.menus[self.current_menu][self.selected_index]
                    if isinstance(current_option, dict):
                        # Toggle submenu expansion
                        self.toggle_submenu(self.selected_index)
                        self.display_highlighted_menu()

                        # Example: Use TableManager to print some info after toggling (adapt as needed)
                        info_table = [
                            ["Status", "Action"],
                            ["Toggled", "Expansion" if (self.current_menu, self.selected_index) in self.expanded_submenus else "Collapse"]
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
                    menu_length = len(self.menus[self.current_menu])
                    if 1 <= num <= menu_length:
                        self.selected_index = num - 1
                        self.display_highlighted_menu()
                        # If confirm_select_digit_key is True, confirm immediately
                        if self.confirm_select_digit_key:
                            current_option = self.menus[self.current_menu][self.selected_index]
                            if isinstance(current_option, dict):
                                self.toggle_submenu(self.selected_index)
                                self.display_highlighted_menu()
                                continue
                            else:
                                confirmed_option = current_option
                                break
                    else:
                        self.write('cursor_position', row=message_row, col=1)
                        self.pc.print(f"\nInvalid selection: {num}. Please select a valid option.", style='vred')


        if self.alt_buffer:
            self.write('normal_buffer', 'show_cursor')

        if confirmed_option and not isinstance(confirmed_option, dict):
            self.pc.print(f'confirmed_option: {confirmed_option}', style={1: self.confirmed_style, (2, 3): self.selected_style})

        return self.selected_index + 1



"""
class InteractiveMenu:
    def __init__(self, options, pc=None, styles=None, key_bindings=None, state=None, config=None):
        self.styles = styles or {
            'selected': PrintsStyle(color='vcyan'),
            'unselected': PrintsStyle(),
            'confirmed': PrintsStyle(color='vgreen'),
            'multi_selected': PrintsStyle(color='vyellow')
        }
        self.pc = pc or PrintsCharming()
        self.control_map = self.pc.CONTROL_MAP  # Use control map from PrintsCharming instance
        self.options = options

        self.key_bindings = key_bindings or {}
        self.state = state or {
            'selected_index': 0,
            'selected_items': set(),  # For multi-selection
            'search_query': "",
        }
        self.config = config or {
            'multi_select': False,
            'editable': False,
            'searchable': False,
            'hierarchical': False,
            'scrollable': False,
            'confirm_required': False,
        }

    def display_menu(self):
        start_index, end_index = self.get_scroll_indices()
        for i, option in enumerate(self.options[start_index:end_index]):
            global_index = i + start_index
            style = self.determine_style(global_index)
            self.pc.print(f"{global_index + 1}. {option}", style=style)

    def get_scroll_indices(self):
        if not self.config['scrollable']:
            return 0, len(self.options)
        max_display = 10  # Example: Display 10 items at a time
        start_index = max(0, self.state['selected_index'] - max_display // 2)
        end_index = min(len(self.options), start_index + max_display)
        return start_index, end_index

    def determine_style(self, global_index):
        if global_index == self.state['selected_index']:
            return self.styles['selected']
        elif global_index in self.state['selected_items']:
            return self.styles['multi_selected']
        else:
            return self.styles['unselected']

    def run(self):
        raise NotImplementedError("Subclasses should implement this method to provide specific behavior.")

"""